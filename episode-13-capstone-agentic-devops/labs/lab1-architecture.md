# Lab 1: Multi-Agent Architecture

> **Mission:** Understand and design the multi-agent system with router, specialists, and orchestrator.

---

## The Problem: Why Single Agents Fail at Scale

Consider a production incident at 3 AM. Your monitoring detects a spike in p99 latency, a Kubernetes pod is crash-looping, and your CI/CD pipeline just deployed a canary with a memory leak. A single AI agent trying to handle all of this simultaneously faces context overload.

> **Analogy:** Think of a hospital emergency room. You do not have one doctor who performs surgery, reads X-rays, dispenses medication, and manages triage simultaneously. Instead, you have specialists (surgeon, radiologist, pharmacist) coordinated by a triage nurse who routes patients to the right expert. A multi-agent system works identically: a router triages incoming requests, specialists handle domain-specific work, and an orchestrator coordinates the overall response.

Single agents fail at scale because of:

1. **Context window saturation** - Handling Kubernetes, Terraform, CI/CD, and observability simultaneously exhausts context with irrelevant information.
2. **Tool sprawl** - Loading every possible tool into one agent creates ambiguity about which tool to use.
3. **Lack of parallelism** - A single agent processes sequentially when incident tasks should run concurrently.

---

## Architecture Patterns: Router, Specialists, Orchestrator

**The Router** is the entry point. It classifies incoming requests and determines which specialist agents should handle them. It performs no work itself.

**The Specialists** each own a single domain:

| Agent | Domain | Tools |
|-------|--------|-------|
| KubernetesAgent | Cluster operations | kubectl, helm |
| ObservabilityAgent | Metrics and logs | promql, loki |
| DeploymentAgent | CI/CD pipelines | argocd, gh actions |
| InfraAgent | Infrastructure state | terraform, pulumi |

**The Orchestrator** coordinates multi-agent workflows, aggregates results, and resolves conflicts between specialist recommendations.

> **Analogy:** The orchestrator is like an Incident Commander in the ICS (Incident Command System). It does not fight the fire directly but coordinates the teams who do, ensuring everyone works toward the same resolution without conflicts.

---

## Agent Communication: Request/Response vs Event-Driven

### Request/Response (Synchronous)

The router sends a request to a specialist and waits for the response. Simple but creates bottlenecks.

```python
from dataclasses import dataclass
import uuid

@dataclass
class AgentMessage:
    sender: str
    recipient: str
    intent: str
    payload: dict
    correlation_id: str = str(uuid.uuid4())

response = await kubernetes_agent.handle(AgentMessage(
    sender="router", recipient="kubernetes-agent",
    intent="diagnose_pod_crash",
    payload={"namespace": "production", "pod_pattern": "api-server-*"}
))
```

### Event-Driven (Asynchronous)

Agents publish events to a shared bus. Other agents subscribe to events they care about. Enables parallelism and loose coupling.

```python
@dataclass
class AgentEvent:
    source: str
    event_type: str
    data: dict
    event_id: str = str(uuid.uuid4())

await event_bus.publish(AgentEvent(
    source="observability-agent",
    event_type="anomaly_detected",
    data={"metric": "http_request_duration_seconds", "severity": "critical"}
))
```

We use **request/response for direct queries** and **event-driven for incident correlation**.

---

## Design the Agent Interface

Every specialist agent implements a common interface with three phases: **analyze**, **plan**, and **execute**. This separation ensures agents never jump straight to action without understanding the problem.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentResult:
    agent_name: str
    status: AgentStatus
    analysis: dict = field(default_factory=dict)
    plan: list = field(default_factory=list)
    actions_taken: list = field(default_factory=list)
    confidence: float = 0.0

class BaseAgent(ABC):
    """Base class for all specialist agents."""

    def __init__(self, name: str, domain: str, capabilities: list[str]):
        self.name = name
        self.domain = domain
        self.capabilities = capabilities
        self.status = AgentStatus.IDLE

    @abstractmethod
    async def analyze(self, context: dict) -> dict:
        """Gather information. Read-only - no system modifications."""
        ...

    @abstractmethod
    async def plan(self, analysis: dict) -> list[dict]:
        """Propose actions. Each step includes action, reason, risk, reversible."""
        ...

    @abstractmethod
    async def execute(self, plan: list[dict], dry_run: bool = True) -> AgentResult:
        """Execute the plan. Default dry_run=True for safety."""
        ...

    async def run(self, context: dict, dry_run: bool = True) -> AgentResult:
        """Full lifecycle: analyze -> plan -> execute."""
        self.status = AgentStatus.ANALYZING
        analysis = await self.analyze(context)
        self.status = AgentStatus.PLANNING
        plan = await self.plan(analysis)
        self.status = AgentStatus.EXECUTING
        result = await self.execute(plan, dry_run=dry_run)
        self.status = AgentStatus.COMPLETED
        return result

    def can_handle(self, intent: str) -> bool:
        return intent in self.capabilities
```

---

## Agent Registry and Discovery

The registry allows the router to discover available agents and match requests to the right specialist, decoupling the router from specific implementations.

```python
from typing import Optional


class AgentRegistry:
    """Registry for discovering and routing to specialist agents."""

    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}
        self._capability_index: dict[str, list[str]] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent
        for capability in agent.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = []
            self._capability_index[capability].append(agent.name)

    def find_by_capability(self, capability: str) -> list[BaseAgent]:
        agent_names = self._capability_index.get(capability, [])
        return [self._agents[name] for name in agent_names]

    def find_best_agent(self, intent: str) -> Optional[BaseAgent]:
        """Find the most specialized agent for a given intent."""
        candidates = self.find_by_capability(intent)
        if not candidates:
            return None
        return min(candidates, key=lambda a: len(a.capabilities))

    def list_agents(self) -> list[dict]:
        return [
            {"name": a.name, "domain": a.domain, "status": a.status.value}
            for a in self._agents.values()
        ]


# Usage
registry = AgentRegistry()
# registry.register(KubernetesAgent())
# registry.register(ObservabilityAgent())
```

---

## Request Flow Through the System

```
User: "Why is checkout returning 503s?"
       │
       ▼
┌─────────────┐
│   Router    │  Classifies: [diagnose_http_error, check_service_health]
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Registry   │  Finds: ObservabilityAgent, KubernetesAgent
└──────┬──────┘
       ├───────────────────┐
       ▼                   ▼
┌────────────────┐  ┌────────────────┐
│ Observability  │  │  Kubernetes    │
│ analyze/plan/  │  │  analyze/plan/ │
│ execute        │  │  execute       │
└───────┬────────┘  └───────┬────────┘
        └─────────┬─────────┘
                  ▼
          ┌──────────────┐
          │ Orchestrator │  Correlates: 503s from 0/3 ready pods (OOMKilled)
          └──────────────┘
```

---

## What Success Looks Like

After completing this lab, you have:

- A clear mental model of how requests flow from user input, through the router, to specialists in parallel, and back through the orchestrator.
- Understanding of why analyze/plan/execute prevents premature action on production systems.
- A working `BaseAgent` abstract class and `AgentRegistry` ready to extend in subsequent labs.

---

## Key Takeaway

> Multi-agent systems decompose complex problems the same way microservices decompose monoliths. Each agent has a bounded context, a clear interface, and independent scalability. The router is your API gateway, specialists are your services, and the orchestrator is your saga coordinator.

---

Next: [Lab 2: FastAPI Gateway](lab2-fastapi-gateway.md)
