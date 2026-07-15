"""
Audit Logging — Agentic DevOps Platform

Thread-safe audit logging system that records every agent interaction to
a JSONL file. Supports querying, statistics, and integrates with FastAPI
as middleware for automatic request/response auditing.

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

import json
import threading
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from .models import AuditEntry, SafetyClassification


def generate_trace_id() -> str:
    """Generate a unique trace identifier for distributed tracing.

    Uses UUID4 to ensure globally unique identifiers that can be
    correlated across multiple services and log systems.

    Returns:
        A string UUID suitable for use as a trace/correlation ID.

    Example:
        >>> trace_id = generate_trace_id()
        >>> len(trace_id) == 36  # UUID4 format: 8-4-4-4-12
        True
    """
    return str(uuid4())


class AuditLogger:
    """Thread-safe audit logger that writes entries to a JSONL file.

    Each line in the audit file is a self-contained JSON object representing
    one agent interaction. The logger supports concurrent writes via a
    threading lock and provides query capabilities for audit review.

    Attributes:
        log_file: Path to the JSONL audit log file.
        _lock: Threading lock for concurrent write safety.

    Example:
        >>> logger = AuditLogger("platform_audit.jsonl")
        >>> entry = AuditEntry(
        ...     trace_id=generate_trace_id(),
        ...     agent_name="k8s-agent",
        ...     action="list_pods",
        ...     input_summary="Show pods in production",
        ...     output_summary="Found 12 pods running",
        ... )
        >>> logger.log(entry)
    """

    def __init__(self, log_file: str = "audit.jsonl") -> None:
        """Initialize the audit logger.

        Creates the log file and parent directories if they don't exist.

        Args:
            log_file: Path to the JSONL audit log file. Relative paths
                are resolved from the current working directory.
        """
        self.log_file = Path(log_file)
        self._lock = threading.Lock()

        # Ensure parent directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not self.log_file.exists():
            self.log_file.touch()

    def log(self, entry: AuditEntry) -> None:
        """Write an audit entry to the log file.

        Thread-safe: uses a lock to prevent interleaved writes from
        concurrent requests.

        Args:
            entry: The AuditEntry to persist. The entry's timestamp is
                serialized to ISO 8601 format.
        """
        record = entry.model_dump()
        # Serialize datetime to ISO format string
        if isinstance(record.get("timestamp"), datetime):
            record["timestamp"] = record["timestamp"].isoformat()

        line = json.dumps(record, default=str) + "\n"

        with self._lock:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(line)

    def query(
        self,
        agent_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        safety_classification: Optional[SafetyClassification] = None,
        user_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
        """Query audit entries with optional filters.

        Reads the audit log and returns entries matching all specified
        criteria. Filters are ANDed together.

        Args:
            agent_name: Filter by agent name (exact match).
            start_time: Only include entries at or after this time.
            end_time: Only include entries at or before this time.
            safety_classification: Filter by safety classification level.
            user_id: Filter by user identifier.
            limit: Maximum number of entries to return (most recent first).

        Returns:
            List of matching AuditEntry objects, ordered most recent first,
            up to the specified limit.
        """
        entries: List[AuditEntry] = []

        if not self.log_file.exists():
            return entries

        with self._lock:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Parse timestamp
            ts_raw = record.get("timestamp")
            if ts_raw and isinstance(ts_raw, str):
                try:
                    record["timestamp"] = datetime.fromisoformat(ts_raw)
                except ValueError:
                    continue

            # Apply filters
            if agent_name and record.get("agent_name") != agent_name:
                continue

            if start_time and record.get("timestamp"):
                if record["timestamp"] < start_time:
                    continue

            if end_time and record.get("timestamp"):
                if record["timestamp"] > end_time:
                    continue

            if safety_classification:
                if record.get("safety_classification") != safety_classification.value:
                    continue

            if user_id and record.get("user_id") != user_id:
                continue

            try:
                entries.append(AuditEntry(**record))
            except (ValueError, TypeError):
                continue

            if len(entries) >= limit:
                break

        return entries

    def get_stats(self) -> Dict[str, Any]:
        """Compute aggregate statistics from the audit log.

        Provides counts by agent, safety classification, and average
        duration metrics for operational visibility.

        Returns:
            Dictionary containing:
                - total_entries: Total number of audit records.
                - by_agent: Dict mapping agent names to request counts.
                - by_classification: Dict mapping classification levels to counts.
                - avg_duration_ms: Average processing time across all entries.
                - success_rate: Fraction of successful operations (0.0-1.0).
                - unique_users: Number of distinct user IDs seen.
        """
        stats: Dict[str, Any] = {
            "total_entries": 0,
            "by_agent": defaultdict(int),
            "by_classification": defaultdict(int),
            "avg_duration_ms": 0.0,
            "success_rate": 0.0,
            "unique_users": set(),
        }

        total_duration = 0.0
        success_count = 0

        if not self.log_file.exists():
            stats["by_agent"] = dict(stats["by_agent"])
            stats["by_classification"] = dict(stats["by_classification"])
            stats["unique_users"] = 0
            return stats

        with self._lock:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            stats["total_entries"] += 1
            stats["by_agent"][record.get("agent_name", "unknown")] += 1
            stats["by_classification"][
                record.get("safety_classification", "SAFE")
            ] += 1
            total_duration += record.get("duration_ms", 0.0)

            if record.get("success", True):
                success_count += 1

            if record.get("user_id"):
                stats["unique_users"].add(record["user_id"])

        # Compute averages
        if stats["total_entries"] > 0:
            stats["avg_duration_ms"] = total_duration / stats["total_entries"]
            stats["success_rate"] = success_count / stats["total_entries"]

        # Convert sets and defaultdicts for JSON serialization
        stats["unique_users"] = len(stats["unique_users"])
        stats["by_agent"] = dict(stats["by_agent"])
        stats["by_classification"] = dict(stats["by_classification"])

        return stats

    def clear(self) -> None:
        """Clear all audit log entries.

        WARNING: This is destructive and should only be used in
        testing or development. In production, use log rotation instead.
        """
        with self._lock:
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.truncate(0)


class AuditMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that automatically audits every HTTP request.

    Wraps each incoming request to record timing, status, and routing
    information in the audit log. Works transparently without requiring
    changes to route handlers.

    Attributes:
        audit_logger: The AuditLogger instance to write entries to.

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> logger = AuditLogger("api_audit.jsonl")
        >>> app.add_middleware(AuditMiddleware, audit_logger=logger)
    """

    def __init__(self, app: Any, audit_logger: AuditLogger) -> None:
        """Initialize the audit middleware.

        Args:
            app: The FastAPI/Starlette application instance.
            audit_logger: AuditLogger instance for persisting entries.
        """
        super().__init__(app)
        self.audit_logger = audit_logger

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process a request and record an audit entry.

        Measures request duration, captures route information, and
        logs the result regardless of whether the request succeeds
        or fails.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware/handler in the chain.

        Returns:
            The HTTP response from the downstream handler.
        """
        start_time = time.perf_counter()
        trace_id = request.headers.get("X-Trace-ID", generate_trace_id())

        # Attempt to extract useful request context
        method = request.method
        path = request.url.path
        user_id = request.headers.get("X-User-ID", None)

        # Process the request
        response: Optional[Response] = None
        success = True
        try:
            response = await call_next(request)
            if response.status_code >= 400:
                success = False
        except Exception:
            success = False
            raise
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000.0

            # Determine safety classification from response header if set
            classification = SafetyClassification.SAFE
            if response and response.headers.get("X-Safety-Classification"):
                try:
                    classification = SafetyClassification(
                        response.headers["X-Safety-Classification"]
                    )
                except ValueError:
                    pass

            entry = AuditEntry(
                trace_id=trace_id,
                timestamp=datetime.utcnow(),
                agent_name="api-gateway",
                action=f"{method} {path}",
                input_summary=f"{method} {path}",
                output_summary=f"Status: {response.status_code if response else 'error'}",
                safety_classification=classification,
                duration_ms=duration_ms,
                user_id=user_id,
                success=success,
            )
            self.audit_logger.log(entry)

        # Add trace ID to response headers for correlation
        if response:
            response.headers["X-Trace-ID"] = trace_id

        return response
