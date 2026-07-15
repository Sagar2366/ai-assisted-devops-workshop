# =============================================================================
# Agentic DevOps Platform — Production Dockerfile
# Multi-stage build with security hardening
# AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder — install dependencies in a full Python image
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install dependencies first (layer caching optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: Runtime — minimal image with only what we need
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

LABEL maintainer="Sagar Utekar"
LABEL description="Agentic DevOps Platform - Multi-agent AI system for DevOps operations"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/ai-assisted-devops-workshop"

# Security: create non-root user
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -d /app -s /sbin/nologin appuser

# Copy installed dependencies from builder stage
COPY --from=builder /install /usr/local

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appgroup . .

# Create directory for audit logs with correct permissions
RUN mkdir -p /app/logs && chown appuser:appgroup /app/logs

# Switch to non-root user
USER appuser

# Expose the API port
EXPOSE 8000

# Health check using the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run with uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
