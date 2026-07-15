#!/usr/bin/env python3
"""
Multi-Agent Orchestrator — Agentic DevOps Platform

Decomposes complex multi-domain requests into sub-tasks, routes each to the
appropriate specialist agent, executes with dependency-aware parallelism,
and synthesizes a unified response.

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional

import anthropic

from .models import AgentResponse, AgentStatus, Severity, ActionItem


# ---------------------------------------------------------------------------
# Decomposition prompt
# ---------------------------------------------------------------------------

DECOMPOSITION_SYSTEM_PROMPT = """You are a DevOps task planner. Break the user's complex request into discrete sub-tasks that can each be handled by a specialist agent.

Available agents:
- k8s: Kubernetes operations (pods, deployments, scaling, logs, troubleshooting)
- cicd: CI/CD pipelines (deploy, PR review, build analysis, releases)
- security: Security scanning (manifests, Dockerfiles, compliance, RBAC)
- iac: Infrastructure as Code (Terraform, HCL, cloud resources, modules)

For each sub-task, specify:
- task: What needs to be done (clear, actionable instruction)
- agent: Which agent handles it (k8s, cicd, security, or iac)
- depends_on: List of task indices this depends on (0-indexed, empty if independent)

Rules:
- Keep tasks focused on a single domain
- Identify true dependencies (not all tasks are sequential)
- Independent tasks should have empty depends_on (they can run in parallel)

Respond with JSON only:
{"tasks": [{"task": "...", "agent": "...", "depends_on": []}]}"""

SYNTHESIS_SYSTEM_PROMPT = """You are a DevOps orchestrator synthesizing results from multiple specialist agents into a unified response.

Guidelines:
1. Start with an overall status (success/partial/failed)
2. Summarize key findings from each agent concisely
3. Highlight conflicts or concerns between agent outputs
4. Provide a prioritized list of next steps
5. Note any tasks that failed and their impact

Be concise, actionable, and highlight the most important information first."""


class Orchestrator:
    """Multi-agent orchestrator for complex DevOps workflows.

    Handles the full lifecycle of multi-domain requests:
    1. Decompose: Use Claude to break request into agent-assignable sub-tasks
    2. Plan: Build a dependency DAG and identify parallel execution phases
    3. Execute: Run phases sequentially, tasks within a phase in parallel
    4. Synthesize: Merge results into a unified response

    Attributes:
        name: Agent identifier.
        domain: Operational domain (orchestration).
        capabilities: Keywords that trigger multi-agent handling.
        agents: Dictionary of registered specialist agents.
        timeout: Maximum seconds for the entire workflow.
    """

    def __init__(self, agents: Dict[str, Any], timeout: int = 300) -> None:
        self.name: str = "orchestrator"
        self.domain: str = "orchestration"
        self.capabilities: List[str] = [
            "workflow", "multi", "coordinate", "orchestrate", "pipeline",
            "end-to-end", "full",
        ]
        self.agents = agents
        self.timeout = timeout
        self._client: Optional[anthropic.Anthropic] = None

    @property
    def client(self) -> anthropic.Anthropic:
        """Lazy-initialize the Anthropic client."""
        if self._client is None:
            self._client = anthropic.Anthropic()
        return self._client

    async def handle(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Orchestrate a complex multi-agent workflow.

        Args:
            message: The user's complex multi-domain request.
            context: Optional shared context for all agents.

        Returns:
            AgentResponse containing the synthesized results from all agents.
        """
        start_time = time.time()

        try:
            # Phase 1: Decompose into sub-tasks
            tasks = await self._decompose(message)

            if not tasks:
                return AgentResponse(
                    agent_name=self.name,
                    content="Unable to decompose the request into actionable tasks.",
                    confidence=0.3,
                    actions=["decomposition_failed"],
                    status=AgentStatus.ERROR,
                )

            # Phase 2: Build execution plan (parallel phases)
            execution_plan = self._build_execution_plan(tasks)

            # Phase 3: Execute phases
            results = await self._execute_phases(tasks, execution_plan, context)

            # Phase 4: Synthesize unified response
            summary = await self._synthesize(message, tasks, results)

            duration = time.time() - start_time

            # Collect all actions from sub-tasks
            all_actions = ["decomposed_request", "built_execution_plan"]
            all_action_items: List[ActionItem] = []
            for result in results.values():
                if isinstance(result, dict) and "actions" in result:
                    all_actions.extend(result["actions"])

            all_actions.append("synthesized_results")

            return AgentResponse(
                agent_name=self.name,
                content=summary,
                confidence=0.85,
                actions=all_actions,
                action_items=all_action_items,
                metadata={
                    "tasks_total": len(tasks),
                    "tasks_completed": sum(
                        1 for r in results.values()
                        if isinstance(r, dict) and r.get("status") != "failed"
                    ),
                    "execution_phases": len(execution_plan),
                    "duration_seconds": round(duration, 2),
                },
                status=AgentStatus.SUCCESS,
            )

        except Exception as exc:
            duration = time.time() - start_time
            return AgentResponse(
                agent_name=self.name,
                content=f"Orchestration failed: {str(exc)}",
                confidence=0.2,
                actions=["orchestration_error"],
                metadata={"error": str(exc), "duration_seconds": round(duration, 2)},
                status=AgentStatus.ERROR,
            )

    async def _decompose(self, message: str) -> List[Dict[str, Any]]:
        """Break a complex request into agent-assignable sub-tasks using Claude.

        Args:
            message: The user's complex request.

        Returns:
            List of task dictionaries with task, agent, and depends_on fields.
        """
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=DECOMPOSITION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": message}],
        )

        response_text = response.content[0].text

        # Extract JSON from response (handle potential markdown fences)
        json_match = json.loads(response_text)
        if isinstance(json_match, dict) and "tasks" in json_match:
            return json_match["tasks"]

        return []

    def _build_execution_plan(self, tasks: List[Dict[str, Any]]) -> List[List[int]]:
        """Build parallel execution phases from task dependencies.

        Uses topological sorting to identify which tasks can run concurrently.
        Tasks within a phase have no inter-dependencies and execute in parallel.
        Phases execute sequentially.

        Args:
            tasks: List of task dictionaries with depends_on fields.

        Returns:
            List of phases, each containing task indices that can run in parallel.
        """
        n = len(tasks)
        in_degree = [0] * n
        dependents: Dict[int, List[int]] = defaultdict(list)

        for i, task in enumerate(tasks):
            for dep in task.get("depends_on", []):
                if isinstance(dep, int) and 0 <= dep < n:
                    dependents[dep].append(i)
                    in_degree[i] += 1

        phases: List[List[int]] = []
        queue = deque(i for i in range(n) if in_degree[i] == 0)

        while queue:
            phase = list(queue)
            phases.append(phase)
            next_queue: deque = deque()

            for task_idx in phase:
                for dependent in dependents[task_idx]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_queue.append(dependent)

            queue = next_queue

        return phases

    async def _execute_phases(
        self,
        tasks: List[Dict[str, Any]],
        execution_plan: List[List[int]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[int, Dict[str, Any]]:
        """Execute task phases with parallel agent calls.

        Tasks within a phase run concurrently via asyncio.gather.
        Results from earlier phases are available as context for later phases.

        Args:
            tasks: All decomposed tasks.
            execution_plan: Phases of task indices.
            context: Shared context for all agents.

        Returns:
            Dictionary mapping task index to result dictionary.
        """
        results: Dict[int, Dict[str, Any]] = {}

        for phase_idx, phase_tasks in enumerate(execution_plan):
            # Build context from prior results
            prior_context = dict(context or {})
            for i, result in results.items():
                if isinstance(result, dict) and "content" in result:
                    prior_context[f"task_{i}_result"] = result["content"][:500]

            # Execute all tasks in this phase concurrently
            coros = []
            for task_idx in phase_tasks:
                task = tasks[task_idx]
                coros.append(
                    self._execute_single_task(task, prior_context)
                )

            phase_results = await asyncio.gather(*coros, return_exceptions=True)

            for task_idx, result in zip(phase_tasks, phase_results):
                if isinstance(result, Exception):
                    results[task_idx] = {
                        "content": f"Task failed: {str(result)}",
                        "status": "failed",
                        "actions": [],
                        "error": str(result),
                    }
                else:
                    results[task_idx] = result

        return results

    async def _execute_single_task(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single task via the appropriate specialist agent.

        Args:
            task: Task dictionary with 'task' instruction and 'agent' name.
            context: Context including results from prior phases.

        Returns:
            Result dictionary from the agent.
        """
        agent_name = task.get("agent", "")
        agent = self.agents.get(agent_name)

        if agent is None:
            return {
                "content": f"Agent '{agent_name}' not available",
                "status": "failed",
                "actions": [],
            }

        try:
            result = await asyncio.wait_for(
                agent.handle(task["task"], context=context),
                timeout=self.timeout,
            )

            # Convert AgentResponse to dict
            if hasattr(result, "to_dict"):
                return result.to_dict()
            elif hasattr(result, "content"):
                return {
                    "agent_name": result.agent_name,
                    "content": result.content,
                    "confidence": result.confidence,
                    "actions": result.actions,
                    "status": result.status.value if hasattr(result.status, "value") else "success",
                }
            return {"content": str(result), "status": "success", "actions": []}

        except asyncio.TimeoutError:
            return {
                "content": f"Task timed out after {self.timeout}s",
                "status": "timeout",
                "actions": [],
            }

    async def _synthesize(
        self,
        original_request: str,
        tasks: List[Dict[str, Any]],
        results: Dict[int, Dict[str, Any]],
    ) -> str:
        """Merge multiple agent results into a unified summary.

        Uses Claude to correlate findings, identify conflicts, and produce
        a coherent response from all specialist agent outputs.

        Args:
            original_request: The user's original request.
            tasks: Decomposed task list.
            results: Results from each task execution.

        Returns:
            Synthesized summary string.
        """
        results_text = "\n\n".join(
            f"Task {i+1}: {tasks[i]['task']} (Agent: {tasks[i]['agent']})\n"
            f"Status: {results[i].get('status', 'unknown')}\n"
            f"Result: {results[i].get('content', 'No output')[:800]}"
            for i in sorted(results.keys())
            if i < len(tasks)
        )

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=SYNTHESIS_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": (
                    f"Original request: {original_request}\n\n"
                    f"Agent results:\n{results_text}\n\n"
                    "Provide a unified summary with overall status and next steps."
                ),
            }],
        )

        return response.content[0].text
