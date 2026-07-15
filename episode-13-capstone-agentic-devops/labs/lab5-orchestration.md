# Lab 5: Multi-Agent Orchestration

> **Mission:** Orchestrate multiple agents for complex multi-domain requests that span Kubernetes, Security, CI/CD, and Infrastructure.

---

## Why Orchestration Matters

Real-world DevOps problems rarely live in a single domain. "Deploy the new version, verify it passes security scanning, and confirm the pods are healthy" spans CI/CD, Security, and Kubernetes. Without orchestration, the user would need to manually call three agents in sequence and correlate results themselves.

> **Analogy:** Think of a symphony orchestra. Each musician (specialist agent) is world-class at their instrument. But without a conductor (orchestrator), they would each play at their own tempo, in their own key, with no coordination. The conductor does not play any instrument — their job is decomposition (interpreting the score), coordination (keeping everyone in sync), and synthesis (producing a unified performance from 80 independent musicians).

---

## Orchestrator Responsibilities

The orchestrator handles three phases:

1. **Decompose** — Break a complex request into sub-tasks, each assignable to a specialist
2. **Route** — Assign each sub-task to the appropriate agent (parallel when independent, sequential when dependent)
3. **Synthesize** — Merge results from multiple agents into a unified response

```
User: "Deploy checkout-service v2.1, scan it for CVEs, and verify pods are healthy"
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                              │
│                                                              │
│  Decompose:                                                  │
│    Task 1: "Deploy checkout-service v2.1"    → CI/CD Agent   │
│    Task 2: "Scan for CVEs"                   → Security Agent│
│    Task 3: "Verify pods are healthy"         → K8s Agent     │
│                                                              │
│  Dependencies: Task 2 depends on Task 1                      │
│                Task 3 depends on Task 1                      │
│                Task 2 and Task 3 are independent (parallel)  │
│                                                              │
│  Execution:                                                  │
│    Phase 1: CI/CD Agent deploys                              │
│    Phase 2: Security + K8s run in parallel                   │
│                                                              │
│  Synthesize: Merge all results into unified report           │
└──────────────────────────────────────────────────────────────┘
```

---

## Step 1: Decompose Complex Requests with Claude

The orchestrator uses Claude to break down a complex request into discrete sub-tasks with dependency information.

```python
#!/usr/bin/env python3
"""Request decomposition using LLM."""

import json
from typing import Any

import anthropic


DECOMPOSITION_PROMPT = """You are a DevOps task planner. Break the user's request into discrete sub-tasks.

Available agents:
- k8s-agent: Kubernetes operations (pods, deployments, scaling, logs)
- cicd-agent: CI/CD pipelines (deploy, PR review, build analysis)
- security-agent: Security scanning (manifests, Dockerfiles, compliance)
- iac-agent: Infrastructure as Code (Terraform, HCL, modules)

For each sub-task, specify:
- task: What needs to be done
- agent: Which agent handles it
- depends_on: List of task indices this depends on (0-indexed)

Respond with JSON only:
{"tasks": [{"task": "...", "agent": "...", "depends_on": []}]}
"""


async def decompose_request(message: str) -> list[dict[str, Any]]:
    """Break a complex request into agent-assignable sub-tasks."""
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=DECOMPOSITION_PROMPT,
        messages=[{"role": "user", "content": message}]
    )

    result = json.loads(response.content[0].text)
    return result["tasks"]
```

---

## Step 2: Build the Dependency Graph

Sub-tasks form a directed acyclic graph (DAG). Tasks without dependencies can run in parallel; tasks with dependencies must wait.

```python
from collections import defaultdict, deque


def build_execution_plan(tasks: list[dict]) -> list[list[int]]:
    """Build parallel execution phases from task dependencies.

    Returns a list of phases. Tasks within a phase can run concurrently.
    Phases execute sequentially.

    Example:
        tasks = [
            {"task": "deploy", "agent": "cicd", "depends_on": []},
            {"task": "scan", "agent": "security", "depends_on": [0]},
            {"task": "verify", "agent": "k8s", "depends_on": [0]},
        ]
        # Returns: [[0], [1, 2]]
        # Phase 1: deploy (alone)
        # Phase 2: scan + verify (parallel, both depend only on deploy)
    """
    n = len(tasks)
    in_degree = [0] * n
    dependents = defaultdict(list)

    for i, task in enumerate(tasks):
        for dep in task.get("depends_on", []):
            dependents[dep].append(i)
            in_degree[i] += 1

    phases = []
    queue = deque([i for i in range(n) if in_degree[i] == 0])

    while queue:
        # All tasks in current queue can run in parallel
        phase = list(queue)
        phases.append(phase)
        next_queue = deque()

        for task_idx in phase:
            for dependent in dependents[task_idx]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    next_queue.append(dependent)

        queue = next_queue

    return phases
```

---

## Step 3: Execute Phases with Parallel Agent Calls

Each phase runs its tasks concurrently using `asyncio.gather`. Results from earlier phases are available as context for later phases.

```python
import asyncio
import time
from typing import Optional


async def execute_orchestrated(
    message: str,
    agents: dict,
    timeout: int = 300
) -> dict:
    """Execute a multi-agent orchestrated workflow.

    Args:
        message: The complex user request.
        agents: Dictionary mapping agent names to agent instances.
        timeout: Maximum time for the entire workflow in seconds.

    Returns:
        Unified result with individual agent responses and merged summary.
    """
    start = time.time()

    # Phase 1: Decompose
    tasks = await decompose_request(message)
    execution_plan = build_execution_plan(tasks)

    # Phase 2: Execute each phase
    results = {}

    for phase_idx, phase_tasks in enumerate(execution_plan):
        # Gather context from previous phases
        prior_context = {
            tasks[i]["agent"]: results[i]
            for i in results
        }

        # Run all tasks in this phase concurrently
        coros = []
        for task_idx in phase_tasks:
            task = tasks[task_idx]
            agent = agents.get(task["agent"])
            if agent:
                coros.append(
                    _execute_single_task(agent, task, prior_context, timeout)
                )

        phase_results = await asyncio.gather(*coros, return_exceptions=True)

        for task_idx, result in zip(phase_tasks, phase_results):
            if isinstance(result, Exception):
                results[task_idx] = {"error": str(result), "status": "failed"}
            else:
                results[task_idx] = result

    # Phase 3: Synthesize
    duration = time.time() - start
    summary = await _synthesize_results(message, tasks, results)

    return {
        "original_request": message,
        "tasks": tasks,
        "execution_plan": execution_plan,
        "results": results,
        "summary": summary,
        "duration_seconds": round(duration, 2),
        "status": "completed"
    }


async def _execute_single_task(
    agent,
    task: dict,
    context: dict,
    timeout: int
) -> dict:
    """Execute a single task with timeout protection."""
    try:
        result = await asyncio.wait_for(
            agent.handle(task["task"], context=context),
            timeout=timeout
        )
        return result.to_dict() if hasattr(result, "to_dict") else vars(result)
    except asyncio.TimeoutError:
        return {"error": "Task timed out", "status": "timeout"}
```

---

## Step 4: Synthesize Results into a Unified Response

After all agents complete, the orchestrator merges their outputs into a coherent summary.

```python
async def _synthesize_results(
    original_request: str,
    tasks: list[dict],
    results: dict
) -> str:
    """Merge multiple agent results into a unified summary."""
    client = anthropic.Anthropic()

    results_text = "\n\n".join(
        f"Task: {tasks[i]['task']} (Agent: {tasks[i]['agent']})\n"
        f"Result: {results[i].get('content', results[i].get('error', 'No output'))}"
        for i in sorted(results.keys())
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=(
            "You are a DevOps orchestrator. Synthesize the results from multiple "
            "specialist agents into a clear, unified summary. Highlight key findings, "
            "flag any conflicts between agents, and provide an overall status."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Original request: {original_request}\n\n"
                f"Agent results:\n{results_text}\n\n"
                "Provide a unified summary with overall status and next steps."
            )
        }]
    )

    return response.content[0].text
```

---

## Step 5: Handle Failures Gracefully

In production, individual agents may fail. The orchestrator must decide whether to abort the workflow, skip the failed task, or retry.

```python
class FailureStrategy:
    """Strategies for handling agent failures in orchestrated workflows."""

    @staticmethod
    def abort_on_failure(results: dict, task_idx: int) -> bool:
        """Abort entire workflow if any task fails."""
        return results.get(task_idx, {}).get("status") == "failed"

    @staticmethod
    def skip_and_continue(results: dict, task_idx: int) -> bool:
        """Skip failed tasks and continue with remaining work."""
        return False  # Never abort

    @staticmethod
    def retry_then_skip(results: dict, task_idx: int, max_retries: int = 2) -> bool:
        """Retry failed tasks up to max_retries, then skip."""
        retry_count = results.get(task_idx, {}).get("retry_count", 0)
        return retry_count >= max_retries
```

---

## What Success Looks Like

After completing this lab:

1. A complex request like "Deploy v2.1, scan for vulnerabilities, and verify pod health" is automatically decomposed into three sub-tasks
2. The dependency graph correctly identifies that scanning and verification depend on deployment
3. Independent tasks (scan + verify) execute in parallel, reducing total latency
4. Individual agent failures are handled gracefully without crashing the workflow
5. A unified summary is generated that correlates findings from all agents

Test it:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Deploy checkout-service v2.1 to staging, scan it for CVEs, and confirm all pods are healthy"
  }'
```

Expected: Three agent results with a synthesized summary showing deployment status, security scan results, and pod health verification.

---

## Key Takeaway

Orchestration is what transforms a collection of independent agents into a coherent platform. Without it, you have a bag of tools. With it, you have a system that can handle complex, multi-domain requests with the same ease as a single-domain query. The key patterns are: decompose into a DAG, execute phases in parallel where possible, fail gracefully, and synthesize a unified response. This mirrors how an Incident Commander coordinates multiple teams during a production incident — delegate, parallelize, and unify.

---

Next: [Lab 6: Production Ready](lab6-production-ready.md)
