#!/usr/bin/env python3
"""
Security Specialist Agent — Agentic DevOps Platform

Handles Kubernetes manifest scanning, Dockerfile auditing, RBAC analysis,
and compliance checking. Uses Claude for security analysis combined with
pattern-based detection for known vulnerabilities.

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import anthropic

from .models import AgentResponse, AgentStatus, Severity, ActionItem


# ---------------------------------------------------------------------------
# Simulated security scan data
# ---------------------------------------------------------------------------

SIMULATED_MANIFEST = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
spec:
  template:
    spec:
      containers:
      - name: payment
        image: payment-svc:latest
        ports:
        - containerPort: 8080
        env:
        - name: DB_PASSWORD
          value: "supersecret123"
        securityContext:
          privileged: true
          runAsRoot: true
"""

SIMULATED_DOCKERFILE = """FROM ubuntu:latest
RUN apt-get update && apt-get install -y curl wget python3
COPY . /app
RUN chmod 777 /app
EXPOSE 8080 22
ENV API_KEY=sk-prod-abc123xyz
CMD ["python3", "/app/main.py"]
"""


class SecurityAgent:
    """Specialist agent for security scanning and compliance auditing.

    Capabilities:
    - scan: Analyze Kubernetes manifests for security misconfigurations
    - audit: Review Dockerfiles against CIS benchmarks
    - rbac: Evaluate RBAC policies for least-privilege violations
    - compliance: Check configurations against security frameworks

    Attributes:
        name: Agent identifier used for routing and audit.
        domain: The operational domain this agent covers.
        capabilities: Keywords that trigger routing to this agent.
    """

    def __init__(self) -> None:
        self.name: str = "security-agent"
        self.domain: str = "security"
        self.capabilities: List[str] = [
            "security", "scan", "vulnerability", "cve", "rbac",
            "compliance", "audit", "dockerfile", "trivy", "network policy",
            "privilege", "secret", "encryption", "tls", "certificate",
            "policy", "hardening",
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
        """Process an incoming security request.

        Routes to manifest scanning, Dockerfile auditing, or general
        compliance checking based on intent analysis.

        Args:
            message: The user's natural language request.
            context: Optional context including manifests, Dockerfiles, etc.

        Returns:
            AgentResponse with findings, severity ratings, and remediation steps.
        """
        message_lower = message.lower()

        if any(word in message_lower for word in ["scan", "manifest", "yaml", "k8s"]):
            return await self._scan_manifest(message, context)
        elif any(word in message_lower for word in ["audit", "dockerfile", "docker", "image"]):
            return await self._audit_dockerfile(message, context)
        elif any(word in message_lower for word in ["rbac", "role", "permission", "access"]):
            return await self._check_rbac(message, context)
        else:
            return await self._check_compliance(message, context)

    async def _scan_manifest(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Scan Kubernetes manifests for security misconfigurations.

        Checks for: privileged containers, missing security contexts,
        secrets in environment variables, use of :latest tag, missing
        resource limits, and host network/PID access.
        """
        manifest = (context or {}).get("manifest", SIMULATED_MANIFEST)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a Kubernetes security expert performing a manifest scan. "
                "Analyze the YAML for these categories of issues:\n"
                "1. CRITICAL: Privileged containers, host namespace access, secrets in plaintext\n"
                "2. HIGH: Running as root, no security context, :latest tag\n"
                "3. MEDIUM: Missing resource limits, no readiness probes, no network policy\n"
                "4. LOW: Missing labels, no pod disruption budget\n\n"
                "For each finding, provide: severity, description, affected line/field, "
                "and exact remediation YAML. Output as a structured report."
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Security scan request: {message}\n\n"
                    f"Manifest to scan:\n```yaml\n{manifest}\n```\n\n"
                    "Provide a prioritized security report."
                ),
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.90,
            actions=["parsed_manifest", "checked_security_context", "checked_secrets", "generated_report"],
            action_items=[
                ActionItem(
                    description="Remove privileged: true from security context",
                    severity=Severity.CRITICAL,
                    automated=False,
                    requires_approval=True,
                ),
                ActionItem(
                    description="Move DB_PASSWORD to a Kubernetes Secret resource",
                    severity=Severity.CRITICAL,
                    automated=False,
                    requires_approval=True,
                ),
                ActionItem(
                    description="Pin image tag to specific version instead of :latest",
                    severity=Severity.HIGH,
                    automated=False,
                    requires_approval=False,
                ),
            ],
            metadata={"scan_type": "kubernetes_manifest", "findings_count": 4},
        )

    async def _audit_dockerfile(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Audit a Dockerfile against CIS Docker Benchmark best practices.

        Checks for: running as root, using :latest base, hardcoded secrets,
        unnecessary port exposure, missing health checks, and oversized images.
        """
        dockerfile = (context or {}).get("dockerfile", SIMULATED_DOCKERFILE)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a container security expert auditing against CIS Docker Benchmark. "
                "Check for:\n"
                "1. CRITICAL: Hardcoded secrets/API keys, running as root\n"
                "2. HIGH: Using :latest tag, exposing SSH port, chmod 777\n"
                "3. MEDIUM: No HEALTHCHECK, no USER instruction, large base image\n"
                "4. LOW: Missing .dockerignore mention, no multi-stage build\n\n"
                "For each finding, cite the CIS benchmark reference and provide "
                "the corrected Dockerfile snippet."
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Dockerfile audit request: {message}\n\n"
                    f"Dockerfile:\n```dockerfile\n{dockerfile}\n```\n\n"
                    "Provide a CIS-referenced security audit."
                ),
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.88,
            actions=["parsed_dockerfile", "checked_cis_benchmark", "identified_secrets", "generated_audit"],
            action_items=[
                ActionItem(
                    description="Remove hardcoded API_KEY from ENV, use build secrets",
                    severity=Severity.CRITICAL,
                    automated=False,
                    requires_approval=True,
                ),
                ActionItem(
                    description="Add USER instruction to run as non-root",
                    command='Add: RUN useradd -r appuser && USER appuser',
                    severity=Severity.HIGH,
                    automated=False,
                    requires_approval=False,
                ),
                ActionItem(
                    description="Remove SSH port exposure (port 22)",
                    severity=Severity.HIGH,
                    automated=False,
                    requires_approval=False,
                ),
            ],
            metadata={"scan_type": "dockerfile_audit", "findings_count": 6},
        )

    async def _check_rbac(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Evaluate RBAC configuration for least-privilege violations.

        Analyzes ClusterRoles, RoleBindings, and ServiceAccount permissions
        to identify overly broad access grants.
        """
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a Kubernetes RBAC security expert. Analyze the request and "
                "provide recommendations for: 1) Overly permissive ClusterRoles, "
                "2) Unnecessary cluster-admin bindings, 3) ServiceAccounts with excessive "
                "permissions, 4) Missing namespace scoping. Suggest least-privilege alternatives."
            ),
            messages=[{
                "role": "user",
                "content": f"RBAC review request: {message}",
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.84,
            actions=["analyzed_rbac_config", "checked_privilege_levels", "generated_recommendations"],
            metadata={"scan_type": "rbac_audit"},
        )

    async def _check_compliance(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """General security compliance analysis.

        Provides recommendations covering pod security standards, network
        policies, secrets management, and encryption at rest/in transit.
        """
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a DevSecOps compliance expert. Analyze the request and provide "
                "security recommendations covering: Pod Security Standards (restricted), "
                "Network Policies (deny-all default), Secrets management (external secrets "
                "operator), Encryption (at rest and in transit), and Supply chain security "
                "(image signing, SBOM). Prioritize by risk and effort."
            ),
            messages=[{
                "role": "user",
                "content": message,
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.82,
            actions=["analyzed_security_posture", "checked_compliance_frameworks"],
            metadata={"scan_type": "compliance_check"},
        )
