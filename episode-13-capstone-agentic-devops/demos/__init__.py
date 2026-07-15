"""
Agentic DevOps Platform — Demo Package

Core modules for the AI-Assisted DevOps Workshop Episode 13 capstone project.
Provides configuration, data models, safety guardrails, and audit logging.

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from .config import PlatformSettings, get_settings
from .models import (
    AgentCapability,
    AgentRequest,
    AgentResponse,
    AuditEntry,
    HealthResponse,
    SafetyClassification,
    WorkflowRequest,
    WorkflowResponse,
)
from .safety import SafetyGuard, classify_request

__all__ = [
    "AgentCapability",
    "AgentRequest",
    "AgentResponse",
    "AuditEntry",
    "HealthResponse",
    "PlatformSettings",
    "SafetyClassification",
    "SafetyGuard",
    "WorkflowRequest",
    "WorkflowResponse",
    "classify_request",
    "get_settings",
]
