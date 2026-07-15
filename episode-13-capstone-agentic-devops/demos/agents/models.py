"""
Shared Data Models — Agentic DevOps Platform
Dataclasses and type definitions used across all specialist agents.
AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class Severity(str, Enum):
    """Severity levels for findings and recommendations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AgentStatus(str, Enum):
    """Execution status of an agent response."""

    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class ActionItem:
    """A concrete action recommended by an agent."""

    description: str
    command: Optional[str] = None
    severity: Severity = Severity.MEDIUM
    automated: bool = False
    requires_approval: bool = True


@dataclass
class AgentResponse:
    """Standardized response from any specialist agent."""

    agent_name: str
    content: str
    confidence: float
    actions: list[str] = field(default_factory=list)
    action_items: list[ActionItem] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: AgentStatus = AgentStatus.SUCCESS
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def is_successful(self) -> bool:
        """Check if the response indicates success."""
        return self.status in (AgentStatus.SUCCESS, AgentStatus.PARTIAL)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON transport."""
        return {
            "agent_name": self.agent_name,
            "content": self.content,
            "confidence": self.confidence,
            "actions": self.actions,
            "action_items": [
                {
                    "description": a.description,
                    "command": a.command,
                    "severity": a.severity.value,
                    "automated": a.automated,
                    "requires_approval": a.requires_approval,
                }
                for a in self.action_items
            ],
            "metadata": self.metadata,
            "status": self.status.value,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
            "request_id": self.request_id,
        }


@dataclass
class WorkflowStep:
    """A single step in a multi-agent workflow."""

    step_id: str
    agent_name: str
    instruction: str
    depends_on: list[str] = field(default_factory=list)
    condition: Optional[str] = None
    timeout_seconds: int = 60


@dataclass
class WorkflowRequest:
    """Request to execute a multi-agent workflow."""

    workflow_name: str
    steps: list[WorkflowStep]
    context: dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class WorkflowResponse:
    """Aggregated response from a multi-agent workflow execution."""

    workflow_name: str
    results: dict[str, AgentResponse] = field(default_factory=dict)
    merged_summary: str = ""
    total_duration_seconds: float = 0.0
    status: AgentStatus = AgentStatus.SUCCESS
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def all_actions(self) -> list[str]:
        """Collect all actions from all agent responses."""
        actions: list[str] = []
        for response in self.results.values():
            actions.extend(response.actions)
        return actions
