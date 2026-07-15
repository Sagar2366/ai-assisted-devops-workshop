# Lab 2: FastAPI Gateway

> **Mission:** Build the REST API gateway that accepts natural language DevOps requests and returns structured responses.

---

## Why FastAPI?

- **Async-first** — agents call kubectl, Prometheus, and cloud APIs concurrently without blocking
- **Auto-docs** — Swagger UI generated from code; no separate documentation to maintain
- **Pydantic validation** — malformed payloads rejected before reaching expensive LLM calls
- **WebSocket support** — stream long-running incident triage results back in real time

---

## Concept: API Gateway Pattern

> **Analogy:** Think of the gateway as an airport control tower. Planes (requests) arrive from CLI tools, Slack bots, and dashboards. The tower validates flight plans, assigns runways, and communicates status — but never flies the planes. Your gateway validates, routes, and formats, but never decides what action to take.

---

## Step 1: Define Request/Response Models with Pydantic

Create `app/models.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class Priority(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class DevOpsRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=2000,
        examples=["Why is pod checkout-7b4f crashlooping in production?"])
    context: Optional[str] = Field(None, description="Namespace, cluster, or time window")
    priority: Priority = Priority.medium

class DevOpsResponse(BaseModel):
    request_id: str
    status: str
    answer: str
    actions_taken: List[str] = []
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WorkflowRequest(BaseModel):
    objective: str = Field(..., min_length=10)
    steps: Optional[List[str]] = None
    dry_run: bool = True

class ActionStep(BaseModel):
    step_number: int
    description: str
    agent: str
    status: str = "pending"

class WorkflowResponse(BaseModel):
    workflow_id: str
    objective: str
    steps: List[ActionStep]
    status: str

class HealthStatus(BaseModel):
    status: str
    version: str
    agents: dict
    uptime_seconds: float
```

---

## Step 2: Create the /ask Endpoint

Create `app/main.py`:

```python
import uuid, time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.models import *
import asyncio

app = FastAPI(title="Agentic DevOps Gateway", version="0.1.0")
START_TIME = time.time()

@app.post("/ask", response_model=DevOpsResponse)
async def ask_agent(request: DevOpsRequest):
    """Accept a natural language DevOps request and route to the appropriate agent."""
    return DevOpsResponse(
        request_id=str(uuid.uuid4()),
        status="completed",
        answer=f"Received: {request.query}. Agent routing not yet connected.",
        actions_taken=["validated_request", "assigned_request_id"],
        confidence=0.0
    )
```

---

## Step 3: Create the /workflow Endpoint for Multi-Step Tasks

```python
@app.post("/workflow", response_model=WorkflowResponse)
async def execute_workflow(request: WorkflowRequest):
    """Execute a multi-step workflow like canary deploys or incident triage."""
    workflow_id = str(uuid.uuid4())
    if request.steps:
        steps = [ActionStep(step_number=i, description=s, agent="pending")
                 for i, s in enumerate(request.steps, 1)]
    else:
        steps = [ActionStep(step_number=1, description="Plan execution", agent="planner")]
    return WorkflowResponse(
        workflow_id=workflow_id, objective=request.objective,
        steps=steps, status="planned" if request.dry_run else "executing"
    )
```

---

## Step 4: Create the /health Endpoint with Agent Status

```python
AGENTS_REGISTRY = {
    "kubernetes": {"status": "ready", "capabilities": ["pod_status", "logs", "scaling"]},
    "prometheus": {"status": "ready", "capabilities": ["query", "alerts"]},
    "incident": {"status": "ready", "capabilities": ["triage", "escalate"]},
    "deployment": {"status": "ready", "capabilities": ["canary", "rollback"]},
}

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Liveness probe + agent availability for operational dashboards."""
    return HealthStatus(
        status="healthy", version="0.1.0",
        agents=AGENTS_REGISTRY, uptime_seconds=round(time.time() - START_TIME, 2)
    )
```

---

## Step 5: Add WebSocket /ws for Streaming Responses

```python
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Stream agent progress in real time during long-running operations."""
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            request = DevOpsRequest.model_validate_json(data)
            await ws.send_json({"type": "ack", "message": f"Processing: {request.query}"})
            for stage in ["parsing", "routing", "executing", "formatting"]:
                await asyncio.sleep(0.5)
                await ws.send_json({"type": "progress", "stage": stage})
            await ws.send_json({"type": "result", "status": "completed",
                                "answer": f"Processed: {request.query}"})
    except WebSocketDisconnect:
        pass
```

---

## Step 6: Add OpenAPI Documentation

Enrich the auto-generated docs with tags and descriptions:

```python
tags_metadata = [
    {"name": "queries", "description": "Natural language DevOps queries"},
    {"name": "workflows", "description": "Multi-step orchestrated workflows"},
    {"name": "system", "description": "Health and status"},
]

app = FastAPI(
    title="Agentic DevOps Gateway",
    description="REST gateway routing natural language requests to AI agents.",
    version="0.1.0",
    openapi_tags=tags_metadata,
    docs_url="/docs", redoc_url="/redoc",
)
```

---

## Run It

```bash
pip install fastapi uvicorn pydantic
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Test:

```bash
curl http://localhost:8000/health | jq

curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Why is pod checkout-7b4f crashlooping?", "priority": "high"}'

curl -X POST http://localhost:8000/workflow \
  -H "Content-Type: application/json" \
  -d '{"objective": "Canary deploy checkout-service v2.4.1", "dry_run": true}'

echo '{"query": "Show pod status in staging"}' | websocat ws://localhost:8000/ws
```

---

## What Success Looks Like

1. Swagger UI at `/docs` shows all endpoints with full request/response schemas
2. `/health` returns the agent registry with kubernetes, prometheus, incident, and deployment agents
3. `/ask` with a query under 5 characters returns a 422 Pydantic validation error
4. `/workflow` with `dry_run: true` returns planned steps without executing
5. WebSocket at `/ws` streams progress stages back in real time

---

## Key Takeaway

> The gateway is the single entry point — it validates, routes, and formats, but never makes decisions. Every request passes through Pydantic validation before reaching agent logic. Every response is structured so downstream consumers can parse it reliably. You can swap agents, change routing, or add capabilities without breaking the API contract.

---

Next: [Lab 3: Agent Router](lab3-agent-router.md)
