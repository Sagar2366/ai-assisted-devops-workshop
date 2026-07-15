"""
Safety Guardrails — Agentic DevOps Platform

Implements a multi-tier safety classification system that evaluates every
incoming request before agent execution. Operations are classified as SAFE,
RESTRICTED (requires elevated permissions), or BLOCKED (categorically denied).

The system uses pattern matching with regex and keyword analysis to prevent
dangerous operations from executing without proper authorization.

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple


class SafetyClassification(str, Enum):
    """Classification levels for safety guardrails.

    SAFE: Operation poses no risk to infrastructure or data integrity.
        These are read-only queries, status checks, and informational requests.
        Examples: "show pod status", "list deployments", "describe service".

    RESTRICTED: Operation could modify infrastructure state and requires
        elevated permissions or explicit confirmation before execution.
        Admins may proceed; other roles need approval.
        Examples: "scale deployment to 5 replicas", "restart the auth service".

    BLOCKED: Operation is categorically denied regardless of user role or
        permissions. These are destructive operations that could cause
        catastrophic data loss or security vulnerabilities.
        Examples: "delete the production namespace", "drop the user database".
    """

    SAFE = "SAFE"
    RESTRICTED = "RESTRICTED"
    BLOCKED = "BLOCKED"


# ---------------------------------------------------------------------------
# Pattern definitions
# ---------------------------------------------------------------------------

BLOCKED_PATTERNS: List[re.Pattern[str]] = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"delete\s+namespace",
        r"kubectl\s+delete\s+namespace",
        r"kubectl\s+delete\s+ns\b",
        r"drop\s+(database|table|schema)",
        r"disable\s+(auth|authentication|authorization|security)",
        r"rm\s+-rf\s+/",
        r"rm\s+-rf\s+\*",
        r"kubectl\s+delete\s+.*--all\b",
        r"terraform\s+destroy(?!\s+.*-plan|-target)",
        r"truncate\s+table",
        r"format\s+(disk|drive|volume)",
        r"chmod\s+777\s+/",
        r"iptables\s+-F",
        r"systemctl\s+stop\s+firewall",
        r"kill\s+-9\s+1\b",
        r":(){ :\|:& };:",  # Fork bomb
        r"mkfs\.",
        r"dd\s+if=.*of=/dev/",
        r">\s*/etc/(passwd|shadow|sudoers)",
    ]
]

RESTRICTED_PATTERNS: List[re.Pattern[str]] = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bscale\b",
        r"\brestart\b",
        r"\bdeploy\b",
        r"\bmodify\b",
        r"\bapply\b",
        r"\brollback\b",
        r"\bupdate\b",
        r"\bupgrade\b",
        r"\bpatch\b",
        r"\bdelete\b(?!\s+namespace)",
        r"\bremove\b",
        r"\bcreate\b",
        r"\binstall\b",
        r"\buninstall\b",
        r"\bhelm\s+(install|upgrade|rollback|uninstall)",
        r"\bkubectl\s+(apply|patch|edit|replace|set)",
        r"\bterraform\s+(apply|plan|import)",
        r"\bdocker\s+(stop|rm|rmi|prune)",
        r"\bsystemctl\s+(restart|stop|start|enable|disable)",
        r"\bcordon\b",
        r"\bdrain\b",
        r"\btaint\b",
    ]
]

# Keywords that indicate read-only/safe operations
SAFE_KEYWORDS: List[str] = [
    "get",
    "list",
    "describe",
    "show",
    "status",
    "logs",
    "view",
    "check",
    "inspect",
    "explain",
    "help",
    "info",
    "top",
    "events",
    "history",
    "diff",
    "plan",
    "validate",
    "lint",
    "audit",
    "monitor",
    "watch",
]


def classify_request(message: str) -> SafetyClassification:
    """Classify a request message into a safety tier.

    Applies pattern matching in priority order: BLOCKED first, then
    RESTRICTED, defaulting to SAFE if no patterns match.

    Args:
        message: The raw user request string to classify.

    Returns:
        SafetyClassification indicating the risk tier of the request.

    Examples:
        >>> classify_request("show me the pods in production")
        <SafetyClassification.SAFE: 'SAFE'>
        >>> classify_request("scale the deployment to 10 replicas")
        <SafetyClassification.RESTRICTED: 'RESTRICTED'>
        >>> classify_request("delete namespace production")
        <SafetyClassification.BLOCKED: 'BLOCKED'>
    """
    # Check blocked patterns first — highest severity
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(message):
            return SafetyClassification.BLOCKED

    # Check restricted patterns
    for pattern in RESTRICTED_PATTERNS:
        if pattern.search(message):
            return SafetyClassification.RESTRICTED

    return SafetyClassification.SAFE


@dataclass
class SafetyGuard:
    """Comprehensive safety evaluation engine.

    Combines regex pattern matching with keyword analysis to provide
    nuanced safety classifications. Supports role-based access control
    to determine whether a user may proceed with restricted operations.

    Attributes:
        blocked_patterns: Compiled regex patterns for blocked operations.
        restricted_patterns: Compiled regex patterns for restricted operations.
        safe_keywords: Keywords indicating safe/read-only operations.
        custom_blocked: Additional blocked patterns added at runtime.
        custom_restricted: Additional restricted patterns added at runtime.

    Example:
        >>> guard = SafetyGuard()
        >>> classification, reason = guard.check("delete namespace production")
        >>> print(classification)
        BLOCKED
        >>> print(reason)
        'Matches blocked pattern: delete namespace'
    """

    blocked_patterns: List[re.Pattern[str]] = field(
        default_factory=lambda: list(BLOCKED_PATTERNS)
    )
    restricted_patterns: List[re.Pattern[str]] = field(
        default_factory=lambda: list(RESTRICTED_PATTERNS)
    )
    safe_keywords: List[str] = field(default_factory=lambda: list(SAFE_KEYWORDS))
    custom_blocked: List[re.Pattern[str]] = field(default_factory=list)
    custom_restricted: List[re.Pattern[str]] = field(default_factory=list)

    def check(self, message: str) -> Tuple[SafetyClassification, str]:
        """Evaluate a message and return its safety classification with reason.

        Performs a thorough analysis of the message against all pattern
        databases and returns both the classification and a human-readable
        explanation of why that classification was assigned.

        Args:
            message: The user request to evaluate.

        Returns:
            A tuple of (SafetyClassification, reason_string) where the reason
            explains which pattern or rule triggered the classification.
        """
        if not message or not message.strip():
            return SafetyClassification.SAFE, "Empty message is safe"

        normalized = message.strip()

        # Check custom blocked patterns first
        for pattern in self.custom_blocked:
            if pattern.search(normalized):
                return (
                    SafetyClassification.BLOCKED,
                    f"Matches custom blocked pattern: {pattern.pattern}",
                )

        # Check built-in blocked patterns
        for pattern in self.blocked_patterns:
            if pattern.search(normalized):
                return (
                    SafetyClassification.BLOCKED,
                    f"Matches blocked pattern: {pattern.pattern}",
                )

        # Check custom restricted patterns
        for pattern in self.custom_restricted:
            if pattern.search(normalized):
                return (
                    SafetyClassification.RESTRICTED,
                    f"Matches custom restricted pattern: {pattern.pattern}",
                )

        # Check built-in restricted patterns
        for pattern in self.restricted_patterns:
            if pattern.search(normalized):
                return (
                    SafetyClassification.RESTRICTED,
                    f"Matches restricted pattern: {pattern.pattern}",
                )

        # Check for safe keywords as a positive signal
        lower_message = normalized.lower()
        for keyword in self.safe_keywords:
            if keyword in lower_message.split():
                return (
                    SafetyClassification.SAFE,
                    f"Contains safe keyword: {keyword}",
                )

        # Default: SAFE for unrecognized operations
        return SafetyClassification.SAFE, "No restricted or blocked patterns detected"

    def is_allowed(self, message: str, user_role: str = "viewer") -> bool:
        """Determine if a user with the given role may execute this message.

        Role hierarchy:
            - admin: Can execute SAFE and RESTRICTED operations.
            - operator: Can execute SAFE and RESTRICTED operations.
            - viewer: Can only execute SAFE operations.

        BLOCKED operations are never allowed regardless of role.

        Args:
            message: The user request to evaluate.
            user_role: The user's role (admin, operator, viewer).

        Returns:
            True if the user is permitted to execute this operation.
        """
        classification, _ = self.check(message)

        if classification == SafetyClassification.BLOCKED:
            return False

        if classification == SafetyClassification.RESTRICTED:
            return user_role.lower() in ("admin", "operator")

        return True

    def get_required_approval(self, classification: SafetyClassification) -> str:
        """Determine what approval is needed for a given classification level.

        Args:
            classification: The safety classification to check.

        Returns:
            Human-readable string describing the required approval process.
        """
        approval_map = {
            SafetyClassification.SAFE: "none",
            SafetyClassification.RESTRICTED: (
                "Requires approval from an admin or operator role. "
                "Submit an approval request via the /approve endpoint "
                "or use --force with admin credentials."
            ),
            SafetyClassification.BLOCKED: (
                "This operation is categorically blocked and cannot be "
                "approved through the platform. If this operation is truly "
                "necessary, it must be performed manually with full audit "
                "trail outside the agentic platform."
            ),
        }
        return approval_map.get(classification, "unknown classification level")

    def add_blocked_pattern(self, pattern: str) -> None:
        """Add a custom blocked pattern at runtime.

        Args:
            pattern: Regex pattern string to add to the blocked list.

        Raises:
            re.error: If the pattern is not valid regex.
        """
        compiled = re.compile(pattern, re.IGNORECASE)
        self.custom_blocked.append(compiled)

    def add_restricted_pattern(self, pattern: str) -> None:
        """Add a custom restricted pattern at runtime.

        Args:
            pattern: Regex pattern string to add to the restricted list.

        Raises:
            re.error: If the pattern is not valid regex.
        """
        compiled = re.compile(pattern, re.IGNORECASE)
        self.custom_restricted.append(compiled)
