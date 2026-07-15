# Lab 6: Production Ready

> **Mission:** Add authentication, rate limiting, observability, and error handling to make the platform production-grade.

---

## The Gap Between Demo and Production

A platform that works in a demo is not a platform you can run at 3 AM. Production readiness means: unauthenticated requests are rejected, abusive clients are throttled, every request is traceable through logs and metrics, and failures degrade gracefully instead of cascading.

> **Analogy:** Think of the difference between a prototype race car and a production vehicle. Both go fast. But the production vehicle has seatbelts, airbags, ABS, crumple zones, and a dashboard that tells you when something is wrong. Your platform needs the same: protection (auth), throttling (rate limits), visibility (observability), and resilience (error handling).

---

## Step 1: API Key Authentication Middleware

Every request must carry a valid API key. Without this, anyone who discovers your endpoint can trigger agent actions on your infrastructure.

```python
#!/usr/bin/env python3
"""API key authentication middleware."""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import hashlib
import os
from typing import Set


# In production, load from a secrets manager (Vault, AWS SSM, etc.)
VALID_API_KEYS: Set[str] = {
    hashlib.sha256(key.encode()).hexdigest()
    for key in os.getenv("API_KEYS", "dev-key-001,dev-key-002").split(",")
}

# Endpoints that don't require authentication
PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware that validates API key on every request.

    Keys are compared by SHA-256 hash to avoid timing attacks
    from string comparison.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # Extract API key from header
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Missing X-API-Key header"}
            )

        # Compare hashed key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if key_hash not in VALID_API_KEYS:
            return JSONResponse(
                status_code=403,
                content={"error": "Invalid API key"}
            )

        # Attach user identity to request state
        request.state.api_key_hash = key_hash[:8]
        return await call_next(request)
```

---

## Step 2: Rate Limiting

Prevent any single client from overwhelming the platform. Use a sliding window counter per API key.

```python
#!/usr/bin/env python3
"""Token bucket rate limiter."""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


@dataclass
class TokenBucket:
    """Token bucket for rate limiting a single client."""
    capacity: int = 60          # Max requests per window
    refill_rate: float = 1.0    # Tokens added per second
    tokens: float = 60.0
    last_refill: float = field(default_factory=time.time)

    def consume(self) -> bool:
        """Attempt to consume a token. Returns True if allowed."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

    @property
    def retry_after(self) -> int:
        """Seconds until next token is available."""
        if self.tokens >= 1.0:
            return 0
        return int((1.0 - self.tokens) / self.refill_rate) + 1


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-client rate limiting using token bucket algorithm."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.buckets: dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(capacity=requests_per_minute,
                              tokens=float(requests_per_minute))
        )

    async def dispatch(self, request: Request, call_next):
        # Identify client by API key hash or IP
        client_id = getattr(request.state, "api_key_hash", None)
        if not client_id:
            client_id = request.client.host if request.client else "unknown"

        bucket = self.buckets[client_id]

        if not bucket.consume():
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"},
                headers={"Retry-After": str(bucket.retry_after)}
            )

        return await call_next(request)
```

---

## Step 3: Structured Logging

JSON-structured logs enable querying in Loki, CloudWatch, or Datadog. Every log line includes the trace ID so you can correlate an entire request lifecycle.

```python
#!/usr/bin/env python3
"""Structured logging configuration."""

import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for machine parsing."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include trace_id if available
        if hasattr(record, "trace_id"):
            log_entry["trace_id"] = record.trace_id

        # Include extra fields
        if hasattr(record, "agent"):
            log_entry["agent"] = record.agent
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms

        # Include exception info
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured JSON logging for the platform."""
    logger = logging.getLogger("devops_platform")
    logger.setLevel(getattr(logging, level.upper()))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger
```

---

## Step 4: Prometheus Metrics

Expose standard RED (Rate, Errors, Duration) metrics for every agent interaction.

```python
#!/usr/bin/env python3
"""Prometheus metrics for observability."""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response


# Request metrics
REQUEST_COUNT = Counter(
    "devops_platform_requests_total",
    "Total requests by endpoint and status",
    ["endpoint", "method", "status_code"]
)

REQUEST_DURATION = Histogram(
    "devops_platform_request_duration_seconds",
    "Request duration in seconds",
    ["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
)

# Agent metrics
AGENT_CALLS = Counter(
    "devops_platform_agent_calls_total",
    "Total calls per agent",
    ["agent_name", "status"]
)

AGENT_DURATION = Histogram(
    "devops_platform_agent_duration_seconds",
    "Agent processing time in seconds",
    ["agent_name"]
)

AGENT_CONFIDENCE = Histogram(
    "devops_platform_agent_confidence",
    "Distribution of agent confidence scores",
    ["agent_name"],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# System metrics
ACTIVE_REQUESTS = Gauge(
    "devops_platform_active_requests",
    "Number of currently processing requests"
)

SAFETY_BLOCKS = Counter(
    "devops_platform_safety_blocks_total",
    "Requests blocked by safety layer",
    ["classification"]
)


async def metrics_endpoint():
    """Expose Prometheus metrics at /metrics."""
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4"
    )
```

---

## Step 5: Health Endpoints with Dependency Checks

A production health endpoint checks not just "is the process alive" but "can it serve traffic" — are agents initialized, is the LLM reachable, is the audit log writable.

```python
#!/usr/bin/env python3
"""Health check endpoints."""

import time
from fastapi import APIRouter

health_router = APIRouter()
START_TIME = time.time()


@health_router.get("/health")
async def health_check():
    """Liveness probe: is the process running?"""
    return {"status": "healthy", "uptime_seconds": round(time.time() - START_TIME, 2)}


@health_router.get("/ready")
async def readiness_check():
    """Readiness probe: can the platform serve traffic?

    Checks:
    - All agents are initialized
    - LLM backend is reachable
    - Audit log is writable
    """
    checks = {
        "agents_loaded": True,    # Replace with actual agent registry check
        "llm_reachable": True,    # Replace with LLM health ping
        "audit_writable": True,   # Replace with file/DB write test
    }

    all_healthy = all(checks.values())
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }
```

---

## Step 6: Global Error Handling

Unhandled exceptions should never leak stack traces to clients. Catch everything, log the details internally, and return a safe error response.

```python
#!/usr/bin/env python3
"""Global exception handlers."""

import traceback
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("devops_platform")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled exceptions and return a safe error response."""
    trace_id = getattr(request.state, "trace_id", "unknown")

    # Log full details internally
    logger.error(
        "Unhandled exception",
        extra={
            "trace_id": trace_id,
            "path": request.url.path,
            "exception": str(exc),
            "traceback": traceback.format_exc()
        }
    )

    # Return safe response to client
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "trace_id": trace_id,
            "message": "An unexpected error occurred. Check logs with this trace_id."
        }
    )
```

---

## Putting It All Together

Wire all middleware into your FastAPI app:

```python
from fastapi import FastAPI

app = FastAPI(title="Agentic DevOps Platform", version="1.0.0")

# Add middleware (order matters: outermost first)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
app.add_middleware(APIKeyMiddleware)

# Add exception handlers
app.add_exception_handler(Exception, global_exception_handler)

# Add metrics endpoint
app.add_route("/metrics", metrics_endpoint)

# Add health routes
app.include_router(health_router)
```

---

## What Success Looks Like

After completing this lab:

1. Requests without `X-API-Key` header receive 401 Unauthorized
2. Requests with an invalid key receive 403 Forbidden
3. A client sending more than 60 requests/minute receives 429 with a `Retry-After` header
4. Every request produces a JSON log line with trace_id, agent, and duration
5. `/metrics` returns Prometheus-format metrics showing request rate, error rate, and duration histograms
6. `/health` returns liveness status; `/ready` returns dependency-checked readiness
7. Unhandled exceptions return a generic 500 with trace_id (no stack traces leaked)

Verify with:

```bash
# No auth → 401
curl -s http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}' | jq .error

# Valid auth → 200
curl -s http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-001" \
  -d '{"message": "Why is my pod crashing?"}' | jq .agent_name

# Rate limit → 429
for i in $(seq 1 65); do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/health
done | sort | uniq -c

# Metrics
curl -s http://localhost:8000/metrics | grep devops_platform
```

---

## Key Takeaway

Production readiness is not a feature you add at the end — it is a set of cross-cutting concerns that must be wired into the platform from the start. Authentication prevents unauthorized access, rate limiting prevents resource exhaustion, structured logging enables debugging at scale, metrics enable alerting before users notice problems, and graceful error handling prevents information leakage. Every production system needs all five, and middleware patterns let you add them without touching business logic.

---

This completes the lab series. You now have a fully production-ready agentic DevOps platform.
