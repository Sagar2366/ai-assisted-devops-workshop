# Lab 4: Specialist Agents

> **Mission:** Build specialist agents for Kubernetes, CI/CD, Security, and Infrastructure-as-Code domains.

---

## Why Specialists Beat Generalists

A single "do-everything" agent drowns in context. It loads Kubernetes docs, Terraform syntax, security benchmarks, and CI/CD pipeline YAML into the same prompt, forcing the LLM to guess which knowledge is relevant. Specialists solve this by scoping each agent to a single domain with domain-specific tools, prompts, and validation.

> **Analogy:** Think of a Formula 1 pit crew. You do not have one mechanic who changes all four tires, refuels the car, adjusts the wing, and cleans the visor. You have a front-right tire specialist, a rear-left tire specialist, a fuel specialist — each with exactly the tools they need, executing their task in under two seconds. Specialist agents work the same way: narrow scope, deep expertise, fast execution.

---

## The BaseAgent Interface

Every specialist implements a common contract. This enables the router to treat all agents uniformly while each agent handles domain-specific logic internally.

```python
#!/usr/bin/env python3
"""Base agent interface for all specialist agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AgentResult:
    """Standardized result from any specialist agent."""
    agent_name: str
    content: str
    confidence: float
    actions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "success"


class BaseAgent(ABC):
    """Abstract base class for all specialist agents.

    Every agent must implement:
    - handle(): Process a request and return a result
    - can_handle(): Determine if this agent can handle a given query

    Attributes:
        name: Unique identifier for this agent.
        domain: The domain this agent specializes in.
        capabilities: List of actions this agent can perform.
    """

    def __init__(self, name: str, domain: str, capabilities: list[str]):
        self.name = name
        self.domain = domain
        self.capabilities = capabilities

    @abstractmethod
    async def handle(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Process an incoming request and return a structured result."""
        ...

    def can_handle(self, message: str) -> float:
        """Return a confidence score (0.0-1.0) for handling this message."""
        message_lower = message.lower()
        matches = sum(1 for kw in self.capabilities if kw in message_lower)
        return min(matches / max(len(self.capabilities) * 0.3, 1), 1.0)
```

---

## K8sAgent: Kubernetes Specialist

The Kubernetes agent handles pod troubleshooting, deployment scaling, log retrieval, and restart operations. It combines Claude for reasoning with subprocess calls to `kubectl` for real cluster interaction.

```python
#!/usr/bin/env python3
"""Kubernetes specialist agent."""

import asyncio
import subprocess
from typing import Optional

import anthropic

from .base import BaseAgent, AgentResult


class K8sAgent(BaseAgent):
    """Specialist agent for Kubernetes cluster operations.

    Capabilities:
    - troubleshoot: Diagnose pod failures (CrashLoopBackOff, OOMKilled, ImagePullBackOff)
    - scale: Adjust replica counts for deployments
    - restart: Perform rolling restarts of deployments
    - logs: Retrieve and analyze pod logs
    """

    def __init__(self):
        super().__init__(
            name="k8s-agent",
            domain="kubernetes",
            capabilities=["pod", "deploy", "kubectl", "namespace", "crashloop",
                         "oom", "node", "service", "scale", "restart", "logs",
                         "k8s", "kubernetes", "container", "replica"]
        )
        self.client = anthropic.Anthropic()

    async def handle(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Route to the appropriate K8s operation based on intent."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["scale", "replica"]):
            return await self._scale(message, context)
        elif any(word in message_lower for word in ["restart", "rollout"]):
            return await self._restart(message, context)
        elif any(word in message_lower for word in ["log", "logs"]):
            return await self._get_logs(message, context)
        else:
            return await self._troubleshoot(message, context)

    async def _troubleshoot(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Diagnose pod or deployment issues using kubectl + Claude analysis."""
        namespace = (context or {}).get("namespace", "default")

        # Gather cluster state
        pod_status = await self._run_kubectl(
            f"get pods -n {namespace} --no-headers"
        )

        # Use Claude to analyze
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system="You are a Kubernetes troubleshooting expert. Analyze the cluster state and provide actionable diagnosis.",
            messages=[{
                "role": "user",
                "content": f"User issue: {message}\n\nPod status:\n{pod_status}\n\nProvide diagnosis and remediation steps."
            }]
        )

        return AgentResult(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.85,
            actions=["gathered_pod_status", "analyzed_with_llm"],
            metadata={"namespace": namespace}
        )

    async def _scale(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Scale a deployment to the requested replica count."""
        # Implementation: parse deployment name and replica count, execute kubectl scale
        return AgentResult(
            agent_name=self.name,
            content="Scaling operation planned. Use --execute flag to apply.",
            confidence=0.9,
            actions=["parsed_scale_request", "validated_deployment_exists"],
            metadata={"dry_run": True}
        )

    async def _restart(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Perform a rolling restart of a deployment."""
        return AgentResult(
            agent_name=self.name,
            content="Rolling restart planned. This will restart pods one at a time.",
            confidence=0.9,
            actions=["parsed_restart_request"],
            metadata={"dry_run": True}
        )

    async def _get_logs(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Retrieve and analyze pod logs."""
        namespace = (context or {}).get("namespace", "default")
        pod_name = (context or {}).get("pod", "")

        if pod_name:
            logs = await self._run_kubectl(f"logs {pod_name} -n {namespace} --tail=50")
        else:
            logs = "No specific pod specified. Use context to provide pod name."

        return AgentResult(
            agent_name=self.name,
            content=f"Log analysis:\n{logs}",
            confidence=0.8,
            actions=["retrieved_logs"],
            metadata={"namespace": namespace, "pod": pod_name}
        )

    async def _run_kubectl(self, command: str) -> str:
        """Execute a kubectl command and return output."""
        try:
            process = await asyncio.create_subprocess_exec(
                "kubectl", *command.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                return stdout.decode().strip()
            return f"Error: {stderr.decode().strip()}"
        except FileNotFoundError:
            return "kubectl not found. Ensure kubectl is installed and configured."
```

---

## SecurityAgent: Security Specialist

The Security agent scans Kubernetes manifests, audits Dockerfiles against best practices, and checks RBAC configurations for compliance violations.

```python
#!/usr/bin/env python3
"""Security specialist agent."""

from typing import Optional
import anthropic

from .base import BaseAgent, AgentResult


class SecurityAgent(BaseAgent):
    """Specialist agent for security scanning and compliance.

    Capabilities:
    - scan: Analyze Kubernetes manifests for security misconfigurations
    - audit: Review Dockerfiles against CIS benchmarks
    - compliance: Check RBAC and network policies
    """

    def __init__(self):
        super().__init__(
            name="security-agent",
            domain="security",
            capabilities=["security", "scan", "audit", "vulnerability", "cve",
                         "rbac", "compliance", "dockerfile", "trivy", "network policy",
                         "privilege", "secret", "encryption"]
        )
        self.client = anthropic.Anthropic()

    async def handle(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Route to the appropriate security operation."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["scan", "manifest", "yaml"]):
            return await self._scan_manifest(message, context)
        elif any(word in message_lower for word in ["audit", "dockerfile", "docker"]):
            return await self._audit_dockerfile(message, context)
        else:
            return await self._check_compliance(message, context)

    async def _scan_manifest(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Scan Kubernetes manifests for security issues."""
        manifest = (context or {}).get("manifest", "")

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a Kubernetes security expert. Analyze manifests for: "
                "privileged containers, missing security contexts, host networking, "
                "missing resource limits, secrets in env vars, missing network policies. "
                "Output findings as a prioritized list with severity and remediation."
            ),
            messages=[{
                "role": "user",
                "content": f"Scan request: {message}\n\nManifest:\n{manifest}"
            }]
        )

        return AgentResult(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.88,
            actions=["scanned_manifest", "identified_security_issues"],
            metadata={"scan_type": "kubernetes_manifest"}
        )

    async def _audit_dockerfile(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Audit a Dockerfile against security best practices."""
        dockerfile = (context or {}).get("dockerfile", "")

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a container security expert. Audit Dockerfiles for: "
                "running as root, using latest tag, exposing unnecessary ports, "
                "copying secrets, missing health checks, large attack surface. "
                "Reference CIS Docker Benchmark where applicable."
            ),
            messages=[{
                "role": "user",
                "content": f"Audit request: {message}\n\nDockerfile:\n{dockerfile}"
            }]
        )

        return AgentResult(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.85,
            actions=["audited_dockerfile", "checked_cis_benchmark"],
            metadata={"scan_type": "dockerfile_audit"}
        )

    async def _check_compliance(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Check general security compliance."""
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a DevSecOps compliance expert. Analyze the request "
                "and provide security recommendations covering RBAC, network "
                "policies, pod security standards, and secrets management."
            ),
            messages=[{
                "role": "user",
                "content": message
            }]
        )

        return AgentResult(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.82,
            actions=["analyzed_compliance_posture"],
            metadata={"scan_type": "compliance_check"}
        )
```

---

## IaCAgent: Infrastructure-as-Code Specialist

The IaC agent generates Terraform modules, reviews HCL for best practices, and suggests improvements for cost optimization and security hardening.

```python
#!/usr/bin/env python3
"""Infrastructure-as-Code specialist agent."""

from typing import Optional
import anthropic

from .base import BaseAgent, AgentResult


class IaCAgent(BaseAgent):
    """Specialist agent for Infrastructure-as-Code operations.

    Capabilities:
    - generate: Create Terraform modules from natural language descriptions
    - review: Analyze HCL for best practices, security, and cost optimization
    - suggest: Recommend improvements to existing infrastructure code
    """

    def __init__(self):
        super().__init__(
            name="iac-agent",
            domain="infrastructure-as-code",
            capabilities=["terraform", "hcl", "module", "infrastructure",
                         "provider", "resource", "state", "plan", "apply",
                         "iac", "pulumi", "cloudformation", "drift"]
        )
        self.client = anthropic.Anthropic()

    async def handle(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Route to the appropriate IaC operation."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["generate", "create", "write"]):
            return await self._generate(message, context)
        elif any(word in message_lower for word in ["review", "check", "audit"]):
            return await self._review(message, context)
        else:
            return await self._suggest_improvements(message, context)

    async def _generate(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Generate Terraform code from a natural language description."""
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=(
                "You are a Terraform expert. Generate production-ready HCL code "
                "following best practices: use variables, outputs, proper naming, "
                "tagging, encryption at rest, least-privilege IAM. Include comments "
                "explaining design decisions."
            ),
            messages=[{
                "role": "user",
                "content": f"Generate Terraform for: {message}"
            }]
        )

        return AgentResult(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.87,
            actions=["generated_terraform_code"],
            metadata={"operation": "generate"}
        )

    async def _review(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Review Terraform/HCL code for best practices."""
        hcl_code = (context or {}).get("code", "")

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a Terraform reviewer. Analyze HCL for: "
                "security misconfigurations, missing encryption, overly permissive IAM, "
                "missing tags, hardcoded values, state management issues, "
                "cost optimization opportunities. Provide severity and fix for each finding."
            ),
            messages=[{
                "role": "user",
                "content": f"Review request: {message}\n\nHCL code:\n{hcl_code}"
            }]
        )

        return AgentResult(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.85,
            actions=["reviewed_hcl_code", "identified_issues"],
            metadata={"operation": "review"}
        )

    async def _suggest_improvements(self, message: str, context: Optional[dict] = None) -> AgentResult:
        """Suggest improvements to existing infrastructure code."""
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are an infrastructure optimization expert. Suggest improvements "
                "for cost reduction, security hardening, reliability, and maintainability. "
                "Prioritize suggestions by impact and effort."
            ),
            messages=[{
                "role": "user",
                "content": message
            }]
        )

        return AgentResult(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.80,
            actions=["analyzed_infrastructure", "generated_suggestions"],
            metadata={"operation": "suggest"}
        )
```

---

## What Success Looks Like

After completing this lab:

1. Each specialist agent implements `BaseAgent` with a `handle()` method and `can_handle()` scoring
2. The K8s agent correctly routes between troubleshoot, scale, restart, and logs operations
3. The Security agent can scan manifests, audit Dockerfiles, and check compliance
4. The IaC agent generates Terraform, reviews HCL, and suggests improvements
5. All agents return structured `AgentResult` objects with confidence scores and action lists
6. Every agent uses Claude for reasoning while keeping domain-specific logic in Python

Test it locally:

```python
import asyncio
from agents.k8s_agent import K8sAgent

async def main():
    agent = K8sAgent()
    result = await agent.handle("Why is my payment-service pod CrashLoopBackOff?")
    print(f"Agent: {result.agent_name}")
    print(f"Confidence: {result.confidence}")
    print(f"Response: {result.content[:200]}")

asyncio.run(main())
```

---

## Key Takeaway

Specialist agents are effective because they constrain scope. A K8s agent does not need to know Terraform syntax, and a Security agent does not need to know how to scale deployments. Each agent carries a focused system prompt, a narrow tool set, and domain-specific validation. This mirrors how high-performing SRE teams organize: specialists who go deep in one domain, coordinated by an orchestrator who sees the big picture.

---

Next: [Lab 5: Orchestration](lab5-orchestration.md)
