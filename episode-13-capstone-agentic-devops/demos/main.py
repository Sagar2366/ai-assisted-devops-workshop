#!/usr/bin/env python3
"""
Agentic DevOps Platform — Main Application

FastAPI application serving as the gateway for the multi-agent DevOps platform.
Routes natural language requests to specialist AI agents for Kubernetes,
CI/CD, Security, and Infrastructure-as-Code operations.

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agents import K8sAgent, CICDAgent, SecurityAgent, IaCAgent, Orchestrator
from agents.router import AgentRouter
from config import get_settings
from models import AgentRequest, AgentResponse, HealthResponse
from safety import SafetyClassification, SafetyGuard

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

settings = get_settings()
safety_guard = SafetyGuard()
router = AgentRouter()

# Initialize specialist agents
agents: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agents on startup, cleanup on shutdown."""
    # Startup: register all specialist agents
    agents["k8s"] = K8sAgent()
    agents["cicd"] = CICDAgent()
    agents["security"] = SecurityAgent()
    agents["iac"] = IaCAgent()
    agents["orchestrator"] = Orchestrator(agents)

    router.register_agents(agents)
    yield


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Agentic DevOps Platform",
    description="Multi-agent platform routing natural language DevOps requests to specialist AI agents.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/ask", response_model=AgentResponse)
async def ask(request: AgentRequest) -> AgentResponse:
    """Accept a natural language DevOps request and route to the best agent.

    The request flows through:
    1. Safety classification (block dangerous operations)
    2. Intent routing (select specialist agent)
    3. Agent execution (process and respond)
    4. Audit logging (record the interaction)
    """
    trace_id = request.trace_id or str(uuid.uuid4())
    start = time.time()

    # Step 1: Safety check
    classification, reason = safety_guard.check(request.message)
    if classification == SafetyClassification.BLOCKED:
        raise HTTPException(
            status_code=403,
            detail=f"This operation is blocked by safety policy. Reason: {reason}",
        )

    # Step 2: Route to the appropriate agent
    route_result = router.route(request.message)
    agent_name = route_result["agent"]
    confidence = route_result["confidence"]

    # Step 3: Execute via selected agent
    agent = agents.get(agent_name)
    if not agent:
        raise HTTPException(
            status_code=500,
            detail=f"Agent '{agent_name}' not available.",
        )

    try:
        result = await agent.handle(
            message=request.message,
            context=request.context,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(exc)}")

    duration_ms = (time.time() - start) * 1000

    return AgentResponse(
        agent_name=agent_name,
        response=result.content,
        confidence=result.confidence,
        actions_taken=result.actions,
        safety_classification=classification.value,
        trace_id=trace_id,
        duration_ms=duration_ms,
        metadata=result.metadata,
    )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Platform health check with agent status.

    Used as a Kubernetes liveness/readiness probe.
    """
    agent_status = {
        name: "ready" for name, agent in agents.items() if agent is not None
    }

    return HealthResponse(
        status="healthy" if agents else "degraded",
        agents=agent_status,
        uptime_seconds=round(time.time() - START_TIME, 2),
        version="1.0.0",
        llm_provider=settings.llm.provider.value,
        llm_reachable=True,
    )


@app.get("/agents/list")
async def list_agents() -> Dict[str, Any]:
    """List all available agents and their capabilities."""
    agent_list = []
    for name, agent in agents.items():
        if name == "orchestrator":
            continue
        agent_list.append({
            "name": agent.name,
            "domain": agent.domain,
            "capabilities": agent.capabilities[:10],
        })

    return {"agents": agent_list, "total": len(agent_list)}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled exceptions — never leak stack traces."""
    trace_id = str(uuid.uuid4())
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "trace_id": trace_id,
        },
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=True,
        log_level="info",
    )
