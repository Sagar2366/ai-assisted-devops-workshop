#!/usr/bin/env python3
"""
Kubernetes Specialist Agent — Agentic DevOps Platform

Handles pod troubleshooting, deployment scaling, log retrieval, and rolling
restarts. Uses Claude for root-cause analysis combined with simulated kubectl
calls for cluster interaction.

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

import anthropic

from .models import AgentResponse, AgentStatus, Severity, ActionItem


# ---------------------------------------------------------------------------
# Simulated kubectl outputs (for workshop/demo safety)
# ---------------------------------------------------------------------------

SIMULATED_PODS = """NAME                          READY   STATUS             RESTARTS   AGE
payment-svc-7b8f6d9c4-xk2lp  1/1     Running            0          2d
payment-svc-7b8f6d9c4-mn9qr  0/1     CrashLoopBackOff   5          15m
auth-svc-5c4d8e7f2-jt4wp     1/1     Running            0          5d
frontend-6a9b3c1d8-zr7vn     1/1     Running            0          1d
"""

SIMULATED_EVENTS = """LAST SEEN   TYPE      REASON              OBJECT                            MESSAGE
2m          Warning   BackOff             pod/payment-svc-7b8f6d9c4-mn9qr   Back-off restarting failed container
5m          Warning   OOMKilled           pod/payment-svc-7b8f6d9c4-mn9qr   Container killed due to OOM
10m         Normal    Pulling             pod/payment-svc-7b8f6d9c4-mn9qr   Pulling image "payment-svc:v2.1.0"
"""

SIMULATED_LOGS = """2024-01-15T10:32:01Z ERROR [payment-svc] OutOfMemoryError: Java heap space
2024-01-15T10:32:01Z ERROR [payment-svc]   at com.example.payment.TransactionService.process(TransactionService.java:142)
2024-01-15T10:32:01Z ERROR [payment-svc]   at com.example.payment.PaymentHandler.handle(PaymentHandler.java:89)
2024-01-15T10:31:55Z INFO  [payment-svc] Processing batch of 5000 transactions
2024-01-15T10:31:50Z INFO  [payment-svc] Connected to database successfully
"""


async def _run_kubectl(command: str) -> str:
    """Execute a kubectl command (simulated for workshop safety).

    In production, this would execute real kubectl commands via
    asyncio.create_subprocess_exec. For the workshop, we return
    simulated output so participants can run demos without a live cluster.

    Args:
        command: The kubectl command arguments (e.g., "get pods -n production").

    Returns:
        Simulated kubectl output as a string.
    """
    if "get pods" in command or "get pod" in command:
        return SIMULATED_PODS
    elif "get events" in command or "events" in command:
        return SIMULATED_EVENTS
    elif "logs" in command:
        return SIMULATED_LOGS
    elif "scale" in command:
        return "deployment.apps/payment-svc scaled"
    elif "rollout restart" in command:
        return "deployment.apps/payment-svc restarted"
    elif "rollout status" in command:
        return "deployment \"payment-svc\" successfully rolled out"
    elif "describe" in command:
        return (
            "Name: payment-svc-7b8f6d9c4-mn9qr\n"
            "Status: CrashLoopBackOff\n"
            "Restart Count: 5\n"
            "Last State: Terminated (OOMKilled)\n"
            "Limits: memory=256Mi, cpu=500m\n"
            "Requests: memory=128Mi, cpu=100m"
        )
    return f"kubectl {command} executed successfully"


class K8sAgent:
    """Specialist agent for Kubernetes cluster operations.

    Capabilities:
    - troubleshoot: Diagnose pod failures (CrashLoopBackOff, OOMKilled, ImagePullBackOff)
    - scale: Adjust replica counts for deployments
    - restart: Perform rolling restarts of deployments
    - logs: Retrieve and analyze pod logs for error patterns

    Attributes:
        name: Agent identifier used for routing and audit.
        domain: The operational domain this agent covers.
        capabilities: Keywords that trigger routing to this agent.
    """

    def __init__(self) -> None:
        self.name: str = "k8s-agent"
        self.domain: str = "kubernetes"
        self.capabilities: List[str] = [
            "pod", "deploy", "deployment", "kubectl", "namespace",
            "crashloop", "oom", "node", "service", "scale", "restart",
            "logs", "k8s", "kubernetes", "container", "replica",
            "ingress", "helm", "rollout",
        ]
        self._client: Optional[anthropic.Anthropic] = None

    @property
    def client(self) -> anthropic.Anthropic:
        """Lazy-initialize the Anthropic client."""
        if self._client is None:
            self._client = anthropic.Anthropic()
        return self._client

    async def handle(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process an incoming Kubernetes request.

        Routes internally based on intent keywords to the appropriate
        sub-handler: troubleshoot, scale, restart, or logs.

        Args:
            message: The user's natural language request.
            context: Optional context including namespace, pod name, etc.

        Returns:
            AgentResponse with diagnosis, recommended actions, and metadata.
        """
        message_lower = message.lower()

        if any(word in message_lower for word in ["scale", "replica"]):
            return await self._scale(message, context)
        elif any(word in message_lower for word in ["restart", "rollout"]):
            return await self._restart(message, context)
        elif any(word in message_lower for word in ["log", "logs"]):
            return await self._get_logs(message, context)
        else:
            return await self._troubleshoot(message, context)

    async def _troubleshoot(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Diagnose pod or deployment issues using kubectl data + Claude analysis.

        Gathers pod status, events, and logs from the cluster, then uses
        Claude to perform root-cause analysis and recommend remediation.
        """
        namespace = (context or {}).get("namespace", "default")

        # Gather cluster state
        pod_status = await _run_kubectl(f"get pods -n {namespace}")
        events = await _run_kubectl(f"get events -n {namespace}")
        logs = await _run_kubectl(f"logs -n {namespace} --tail=20")

        # Use Claude for root-cause analysis
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=(
                "You are a Kubernetes troubleshooting expert. Analyze the cluster "
                "state data and provide: 1) Root cause diagnosis, 2) Impact assessment, "
                "3) Remediation steps with exact kubectl commands. Be concise and actionable."
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"User issue: {message}\n\n"
                    f"Pod status:\n{pod_status}\n\n"
                    f"Events:\n{events}\n\n"
                    f"Recent logs:\n{logs}\n\n"
                    "Provide diagnosis and step-by-step remediation."
                ),
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.87,
            actions=["gathered_pod_status", "retrieved_events", "analyzed_logs", "diagnosed_issue"],
            action_items=[
                ActionItem(
                    description="Increase memory limits for affected pod",
                    command="kubectl set resources deployment/payment-svc --limits=memory=512Mi",
                    severity=Severity.HIGH,
                    automated=False,
                    requires_approval=True,
                ),
            ],
            metadata={"namespace": namespace, "data_sources": ["pods", "events", "logs"]},
        )

    async def _scale(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Scale a deployment to the requested replica count.

        Validates the deployment exists, checks current state, and
        produces the scaling command. Requires approval before execution.
        """
        namespace = (context or {}).get("namespace", "default")

        # Simulate scale operation
        result = await _run_kubectl(f"scale deployment/payment-svc --replicas=5 -n {namespace}")

        return AgentResponse(
            agent_name=self.name,
            content=(
                f"Scaling operation prepared.\n\n"
                f"Command: kubectl scale deployment/payment-svc --replicas=5 -n {namespace}\n"
                f"Simulated result: {result}\n\n"
                f"This is a RESTRICTED operation. In production, this requires approval "
                f"before execution."
            ),
            confidence=0.92,
            actions=["parsed_scale_request", "validated_deployment", "prepared_command"],
            action_items=[
                ActionItem(
                    description="Scale deployment to requested replicas",
                    command=f"kubectl scale deployment/payment-svc --replicas=5 -n {namespace}",
                    severity=Severity.MEDIUM,
                    automated=False,
                    requires_approval=True,
                ),
            ],
            metadata={"namespace": namespace, "operation": "scale", "dry_run": True},
        )

    async def _restart(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Perform a rolling restart of a deployment.

        Issues a rollout restart to gracefully cycle all pods without
        downtime, respecting the deployment's rolling update strategy.
        """
        namespace = (context or {}).get("namespace", "default")

        result = await _run_kubectl(f"rollout restart deployment/payment-svc -n {namespace}")

        return AgentResponse(
            agent_name=self.name,
            content=(
                f"Rolling restart prepared.\n\n"
                f"Command: kubectl rollout restart deployment/payment-svc -n {namespace}\n"
                f"This will restart pods one at a time following the rolling update strategy.\n"
                f"Simulated result: {result}"
            ),
            confidence=0.90,
            actions=["parsed_restart_request", "prepared_rollout_restart"],
            action_items=[
                ActionItem(
                    description="Rolling restart of deployment",
                    command=f"kubectl rollout restart deployment/payment-svc -n {namespace}",
                    severity=Severity.MEDIUM,
                    automated=False,
                    requires_approval=True,
                ),
            ],
            metadata={"namespace": namespace, "operation": "restart", "dry_run": True},
        )

    async def _get_logs(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Retrieve and analyze pod logs for error patterns.

        Fetches recent logs and uses Claude to identify error patterns,
        correlate with known issues, and suggest fixes.
        """
        namespace = (context or {}).get("namespace", "default")
        pod_name = (context or {}).get("pod", "payment-svc-7b8f6d9c4-mn9qr")

        logs = await _run_kubectl(f"logs {pod_name} -n {namespace} --tail=50")

        # Analyze logs with Claude
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=(
                "You are a log analysis expert. Identify error patterns, correlate "
                "timestamps, and provide actionable insights. Focus on root cause."
            ),
            messages=[{
                "role": "user",
                "content": f"Analyze these pod logs:\n\n{logs}",
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.83,
            actions=["retrieved_logs", "analyzed_error_patterns"],
            metadata={"namespace": namespace, "pod": pod_name, "log_lines": len(logs.splitlines())},
        )
