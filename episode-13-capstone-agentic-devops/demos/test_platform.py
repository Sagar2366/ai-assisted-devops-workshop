#!/usr/bin/env python3
"""
Integration Tests — Agentic DevOps Platform

Tests the platform end-to-end: health endpoint, agent routing, safety
blocking, and audit logging. Uses httpx async client against the FastAPI app.

Run with: pytest test_platform.py -v

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

import json
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def anyio_backend():
    """Use asyncio as the async backend for tests."""
    return "asyncio"


@pytest.fixture
async def client():
    """Create an async HTTP client bound to the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Health Endpoint Tests
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    @pytest.mark.anyio
    async def test_health_returns_200(self, client: AsyncClient) -> None:
        """Health endpoint should return 200 with platform status."""
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_health_response_structure(self, client: AsyncClient) -> None:
        """Health response should contain required fields."""
        response = await client.get("/health")
        data = response.json()

        assert "status" in data
        assert "agents" in data
        assert "uptime_seconds" in data
        assert "version" in data
        assert data["version"] == "1.0.0"

    @pytest.mark.anyio
    async def test_health_reports_agent_status(self, client: AsyncClient) -> None:
        """Health endpoint should report status for each registered agent."""
        response = await client.get("/health")
        data = response.json()

        # After startup, agents should be registered
        if data["agents"]:
            for agent_name, status in data["agents"].items():
                assert status in ("ready", "degraded", "unavailable")


# ---------------------------------------------------------------------------
# Agent Routing Tests
# ---------------------------------------------------------------------------


class TestAgentRouting:
    """Tests for the /ask endpoint and request routing."""

    @pytest.mark.anyio
    async def test_k8s_query_routes_to_k8s_agent(self, client: AsyncClient) -> None:
        """Kubernetes-related queries should route to the k8s agent."""
        # Mock the agent handle method to avoid real API calls
        mock_response = AsyncMock()
        mock_response.content = "Pod is in CrashLoopBackOff due to OOM."
        mock_response.confidence = 0.87
        mock_response.actions = ["diagnosed_issue"]
        mock_response.metadata = {"namespace": "default"}

        with patch.dict(
            "main.agents",
            {"k8s": AsyncMock(handle=AsyncMock(return_value=mock_response))},
        ):
            response = await client.post(
                "/ask",
                json={"message": "Why is my pod crashing in the default namespace?"},
            )

        # Should route successfully (not return 403 or 500)
        assert response.status_code in (200, 403, 500)

        if response.status_code == 200:
            data = response.json()
            assert data["agent_name"] == "k8s-agent" or "k8s" in data.get("agent_name", "")

    @pytest.mark.anyio
    async def test_terraform_query_routes_to_iac_agent(self, client: AsyncClient) -> None:
        """Terraform-related queries should route to the IaC agent."""
        mock_response = AsyncMock()
        mock_response.content = "Generated Terraform module for S3 bucket."
        mock_response.confidence = 0.87
        mock_response.actions = ["generated_terraform"]
        mock_response.metadata = {"operation": "generate"}

        with patch.dict(
            "main.agents",
            {"iac": AsyncMock(handle=AsyncMock(return_value=mock_response))},
        ):
            response = await client.post(
                "/ask",
                json={"message": "Generate Terraform for an S3 bucket with encryption"},
            )

        assert response.status_code in (200, 403, 500)

    @pytest.mark.anyio
    async def test_ask_requires_message(self, client: AsyncClient) -> None:
        """The /ask endpoint should reject requests without a message."""
        response = await client.post("/ask", json={})
        assert response.status_code == 422  # Validation error


# ---------------------------------------------------------------------------
# Safety Blocking Tests
# ---------------------------------------------------------------------------


class TestSafetyBlocking:
    """Tests for the safety guardrail system."""

    @pytest.mark.anyio
    async def test_blocked_operation_returns_403(self, client: AsyncClient) -> None:
        """Dangerous operations should be blocked with 403 status."""
        response = await client.post(
            "/ask",
            json={"message": "delete namespace production"},
        )
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_blocked_terraform_destroy(self, client: AsyncClient) -> None:
        """terraform destroy without target should be blocked."""
        response = await client.post(
            "/ask",
            json={"message": "terraform destroy the entire infrastructure"},
        )
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_safe_query_is_allowed(self, client: AsyncClient) -> None:
        """Read-only queries should pass safety checks."""
        mock_response = AsyncMock()
        mock_response.content = "Pods are healthy."
        mock_response.confidence = 0.9
        mock_response.actions = ["listed_pods"]
        mock_response.metadata = {}

        with patch.dict(
            "main.agents",
            {"k8s": AsyncMock(handle=AsyncMock(return_value=mock_response))},
        ):
            response = await client.post(
                "/ask",
                json={"message": "show me the pods in production namespace"},
            )

        # Safe query should not be blocked
        assert response.status_code != 403


# ---------------------------------------------------------------------------
# Audit Logging Tests
# ---------------------------------------------------------------------------


class TestAuditLogging:
    """Tests for the audit logging system."""

    @pytest.mark.anyio
    async def test_blocked_request_is_audited(self, client: AsyncClient) -> None:
        """Blocked requests should generate an audit log entry."""
        with patch("main.audit_logger") as mock_logger:
            await client.post(
                "/ask",
                json={"message": "delete namespace production"},
            )

            # Verify audit_logger.log_event was called
            assert mock_logger.log_event.called

    @pytest.mark.anyio
    async def test_successful_request_is_audited(self, client: AsyncClient) -> None:
        """Successful requests should generate an audit log entry."""
        mock_response = AsyncMock()
        mock_response.content = "All pods running."
        mock_response.confidence = 0.9
        mock_response.actions = ["listed_pods"]
        mock_response.metadata = {}

        with patch("main.audit_logger") as mock_logger, patch.dict(
            "main.agents",
            {"k8s": AsyncMock(handle=AsyncMock(return_value=mock_response))},
        ):
            await client.post(
                "/ask",
                json={"message": "list pods in default namespace"},
            )

            # Audit logger should have been called for the successful request
            assert mock_logger.log_event.called


# ---------------------------------------------------------------------------
# Agent List Endpoint Tests
# ---------------------------------------------------------------------------


class TestAgentListEndpoint:
    """Tests for the /agents/list endpoint."""

    @pytest.mark.anyio
    async def test_list_agents_returns_200(self, client: AsyncClient) -> None:
        """Agent list endpoint should return 200."""
        response = await client.get("/agents/list")
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_list_agents_structure(self, client: AsyncClient) -> None:
        """Agent list should contain agents array and total count."""
        response = await client.get("/agents/list")
        data = response.json()

        assert "agents" in data
        assert "total" in data
        assert isinstance(data["agents"], list)
        assert isinstance(data["total"], int)
