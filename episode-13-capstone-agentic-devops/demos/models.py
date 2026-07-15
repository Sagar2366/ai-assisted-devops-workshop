"""
Data Models — Agentic DevOps Platform

Pydantic models defining the request/response schema for agent interactions,
workflow orchestration, health checks, and audit logging.

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class SafetyClassification(str, Enum):
    """Classification levels for safety guardrails.

    SAFE: Operation poses no risk and can execute immediately.
    RESTRICTED: Operation requires elevated permissions or explicit approval.
    BLOCKED: Operation is categorically denied regardless of permissions.
    """

    SAFE = "SAFE"
    RESTRICTED = "RESTRICTED"
    BLOCKED = "BLOCKED"


class Urgency(str, Enum):
    """Request urgency levels affecting routing and prioritization.

    LOW: Informational queries, can be queued.
    MEDIUM: Standard operational requests.
    HIGH: Time-sensitive operations needing prompt attention.
    CRITICAL: Incident-level urgency, bypasses normal queuing.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentCapability(BaseModel):
    """Describes what a specific agent can do.

    Used for intelligent routing — the orchestrator matches incoming
    requests against agent capabilities to select the best handler.

    Attributes:
        name: Unique identifier for this capability.
        description: Human-readable description of what this capability covers.
        keywords: Terms that trigger routing to this capability.
        examples: Example requests that would match this capability.
    """

    name: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for this capability",
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Human-readable description of the capability",
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Terms that trigger routing to this capability",
    )
    examples: List[str] = Field(
        default_factory=list,
        description="Example requests matching this capability",
    )


class AgentRequest(BaseModel):
    """Incoming request to the agent platform.

    Represents a user's intent that needs to be routed to the appropriate
    agent for processing.

    Attributes:
        message: The user's natural language request.
        context: Optional contextual data (e.g., current namespace, cluster).
        preferred_agent: Optional hint for which agent to route to.
        urgency: How time-sensitive this request is.
        user_id: Identifier of the requesting user for audit purposes.
        trace_id: Distributed tracing identifier; auto-generated if not provided.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The user's natural language request",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional contextual data for the request",
    )
    preferred_agent: Optional[str] = Field(
        default=None,
        description="Optional hint for agent routing",
    )
    urgency: Urgency = Field(
        default=Urgency.MEDIUM,
        description="Request urgency level",
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Identifier of the requesting user",
    )
    trace_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Distributed tracing identifier",
    )


class AgentResponse(BaseModel):
    """Response from an agent after processing a request.

    Contains the agent's output along with metadata about the execution
    including confidence, actions taken, and safety classification.

    Attributes:
        agent_name: Which agent handled this request.
        response: The agent's natural language response.
        confidence: How confident the agent is in its response (0.0-1.0).
        actions_taken: List of actions the agent performed or recommends.
        safety_classification: Safety level assigned to this interaction.
        trace_id: Distributed tracing identifier linking request to response.
        duration_ms: How long the agent took to process in milliseconds.
        metadata: Optional additional metadata from the agent.
    """

    agent_name: str = Field(
        ...,
        description="Which agent handled this request",
    )
    response: str = Field(
        ...,
        description="The agent's natural language response",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Agent confidence in the response (0.0-1.0)",
    )
    actions_taken: List[str] = Field(
        default_factory=list,
        description="List of actions performed or recommended",
    )
    safety_classification: SafetyClassification = Field(
        default=SafetyClassification.SAFE,
        description="Safety classification of this interaction",
    )
    trace_id: str = Field(
        ...,
        description="Distributed tracing identifier",
    )
    duration_ms: float = Field(
        ...,
        ge=0.0,
        description="Processing duration in milliseconds",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional additional metadata from the agent",
    )


class WorkflowRequest(BaseModel):
    """Request to execute a multi-step workflow.

    Workflows consist of multiple agent actions that can be
    executed sequentially or in parallel.

    Attributes:
        description: Human-readable description of the workflow goal.
        steps: Optional explicit steps; if not provided, the orchestrator plans them.
        parallel: Whether independent steps can execute concurrently.
        timeout_seconds: Maximum time for the entire workflow.
        user_id: Identifier of the requesting user.
        trace_id: Distributed tracing identifier.
    """

    description: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Human-readable workflow description",
    )
    steps: Optional[List[str]] = Field(
        default=None,
        description="Explicit steps; orchestrator plans if omitted",
    )
    parallel: bool = Field(
        default=False,
        description="Whether independent steps can run concurrently",
    )
    timeout_seconds: int = Field(
        default=600,
        gt=0,
        description="Maximum time for the entire workflow",
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Identifier of the requesting user",
    )
    trace_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Distributed tracing identifier",
    )


class WorkflowStatus(str, Enum):
    """Status of a workflow execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowResponse(BaseModel):
    """Response from a completed workflow execution.

    Attributes:
        workflow_id: Unique identifier for this workflow execution.
        status: Current status of the workflow.
        results: List of individual agent responses from each step.
        total_duration_ms: Total workflow execution time in milliseconds.
        steps_completed: Number of steps that completed successfully.
        steps_total: Total number of steps in the workflow.
        error: Error message if the workflow failed.
    """

    workflow_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this workflow execution",
    )
    status: WorkflowStatus = Field(
        ...,
        description="Current status of the workflow",
    )
    results: List[AgentResponse] = Field(
        default_factory=list,
        description="Individual agent responses from each step",
    )
    total_duration_ms: float = Field(
        ...,
        ge=0.0,
        description="Total workflow execution time in milliseconds",
    )
    steps_completed: int = Field(
        default=0,
        ge=0,
        description="Number of steps completed successfully",
    )
    steps_total: int = Field(
        default=0,
        ge=0,
        description="Total number of steps in the workflow",
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if the workflow failed",
    )


class HealthResponse(BaseModel):
    """Health check response for the platform.

    Provides a snapshot of the platform's operational status including
    the state of each registered agent.

    Attributes:
        status: Overall platform health status.
        agents: Map of agent names to their individual health status.
        uptime_seconds: How long the platform has been running.
        version: Platform version string.
        llm_provider: Active LLM provider name.
        llm_reachable: Whether the LLM backend is currently reachable.
    """

    status: str = Field(
        ...,
        description="Overall platform health: 'healthy', 'degraded', or 'unhealthy'",
    )
    agents: Dict[str, str] = Field(
        default_factory=dict,
        description="Agent name to status mapping",
    )
    uptime_seconds: float = Field(
        ...,
        ge=0.0,
        description="Platform uptime in seconds",
    )
    version: str = Field(
        ...,
        description="Platform version string",
    )
    llm_provider: str = Field(
        default="ollama",
        description="Active LLM provider name",
    )
    llm_reachable: bool = Field(
        default=False,
        description="Whether the LLM backend is reachable",
    )


class AuditEntry(BaseModel):
    """Single audit log entry recording an agent interaction.

    Every request processed by the platform generates an audit entry
    for compliance, debugging, and observability purposes.

    Attributes:
        trace_id: Distributed tracing identifier linking related entries.
        timestamp: When this event occurred (ISO 8601 format).
        agent_name: Which agent handled the interaction.
        action: High-level description of what was done.
        input_summary: Truncated summary of the request input.
        output_summary: Truncated summary of the agent output.
        safety_classification: Safety level assigned to this interaction.
        duration_ms: Processing time in milliseconds.
        user_id: Identifier of the requesting user.
        success: Whether the operation completed successfully.
    """

    trace_id: str = Field(
        ...,
        description="Distributed tracing identifier",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this event occurred",
    )
    agent_name: str = Field(
        ...,
        description="Which agent handled the interaction",
    )
    action: str = Field(
        ...,
        description="High-level action description",
    )
    input_summary: str = Field(
        default="",
        max_length=500,
        description="Truncated summary of the request input",
    )
    output_summary: str = Field(
        default="",
        max_length=500,
        description="Truncated summary of the agent output",
    )
    safety_classification: SafetyClassification = Field(
        default=SafetyClassification.SAFE,
        description="Safety classification for this interaction",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Processing time in milliseconds",
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Identifier of the requesting user",
    )
    success: bool = Field(
        default=True,
        description="Whether the operation completed successfully",
    )
