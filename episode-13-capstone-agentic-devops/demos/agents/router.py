#!/usr/bin/env python3
"""
Agent Router — Agentic DevOps Platform

Routes incoming requests to the appropriate specialist agent using a hybrid
approach: fast keyword matching for common queries, LLM-based classification
as a fallback for ambiguous requests.

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any, Dict, Optional

import anthropic


# ---------------------------------------------------------------------------
# Agent capability registry for keyword-based routing
# ---------------------------------------------------------------------------

AGENT_KEYWORDS: Dict[str, list[str]] = {
    "k8s": [
        "pod", "deploy", "deployment", "kubectl", "namespace", "crashloop",
        "crashloopbackoff", "oom", "oomkilled", "node", "service", "ingress",
        "helm", "k8s", "kubernetes", "container", "replica", "statefulset",
        "daemonset", "pvc", "configmap", "scale", "restart", "logs", "rollout",
    ],
    "cicd": [
        "pipeline", "ci/cd", "cicd", "github actions", "jenkins", "deploy",
        "build", "pr", "pull request", "merge", "branch", "artifact",
        "release", "canary", "rollback", "workflow", "gitlab",
    ],
    "security": [
        "security", "scan", "vulnerability", "cve", "rbac", "compliance",
        "audit", "dockerfile", "trivy", "network policy", "privilege",
        "secret", "encryption", "tls", "certificate", "policy",
    ],
    "iac": [
        "terraform", "hcl", "module", "infrastructure", "provider",
        "resource", "state", "plan", "apply", "drift", "pulumi",
        "cloudformation", "iac", "tf", "s3", "vpc", "ec2",
    ],
}

AGENT_PATTERNS: Dict[str, list[str]] = {
    "k8s": [
        r"why is .+ (crashing|failing|pending|restarting|crashloop)",
        r"scale .+ to \d+",
        r"(get|show) .+ (logs|pods|status)",
        r"restart .+ (deployment|pod|service)",
    ],
    "cicd": [
        r"(review|check) .+ (pr|pull request)",
        r"(deploy|release) .+ (to|in) .+",
        r"(optimize|fix) .+ pipeline",
        r"why .+ build (fail|broke)",
    ],
    "security": [
        r"scan .+ (for|against) .+",
        r"audit .+ (dockerfile|manifest|rbac)",
        r"check .+ (compliance|vulnerabilities|cves)",
    ],
    "iac": [
        r"(generate|create|write) .+ terraform",
        r"review .+ (terraform|hcl|infrastructure)",
        r"(plan|apply|destroy) .+",
    ],
}

CONFIDENCE_THRESHOLD = 0.6


class AgentRouter:
    """Hybrid router combining keyword matching with LLM classification.

    Uses a two-phase approach:
    1. Fast keyword + regex pattern matching (handles ~80% of requests in <1ms)
    2. LLM fallback for ambiguous queries (uses Claude for classification)

    Attributes:
        agents: Dictionary of registered agent instances.
        client: Anthropic client for LLM-based routing.
    """

    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self._client: Optional[anthropic.Anthropic] = None

    @property
    def client(self) -> anthropic.Anthropic:
        """Lazy-initialize the Anthropic client."""
        if self._client is None:
            self._client = anthropic.Anthropic()
        return self._client

    def register_agents(self, agents: Dict[str, Any]) -> None:
        """Register available agents for routing."""
        self.agents = agents

    def route(self, message: str) -> Dict[str, Any]:
        """Route a message to the best specialist agent.

        Args:
            message: The user's natural language request.

        Returns:
            Dictionary with 'agent' name, 'confidence' score, and 'method' used.
        """
        # Phase 1: Try keyword matching
        keyword_result = self._keyword_route(message)

        if (
            keyword_result["agent"] is not None
            and keyword_result["confidence"] >= CONFIDENCE_THRESHOLD
        ):
            return keyword_result

        # Phase 2: LLM fallback for ambiguous queries
        try:
            llm_result = self._llm_route(message)
            return llm_result
        except Exception:
            # If LLM fails, use best keyword match or default
            if keyword_result["agent"] is not None:
                return keyword_result
            return {"agent": "k8s", "confidence": 0.3, "method": "default_fallback"}

    def _keyword_route(self, message: str) -> Dict[str, Any]:
        """Route based on keyword frequency and regex pattern matching.

        Args:
            message: The user's request text.

        Returns:
            Routing result with agent, confidence, and scoring details.
        """
        message_lower = message.lower()
        scores: Counter = Counter()

        # Score keyword matches
        for agent_name, keywords in AGENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    scores[agent_name] += 1

        # Score pattern matches (weighted 3x)
        for agent_name, patterns in AGENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    scores[agent_name] += 3

        if not scores:
            return {"agent": None, "confidence": 0.0, "method": "keyword"}

        top_agent, top_score = scores.most_common(1)[0]
        total_score = sum(scores.values())
        confidence = round(top_score / total_score, 2) if total_score > 0 else 0.0

        return {
            "agent": top_agent,
            "confidence": confidence,
            "method": "keyword",
            "scores": dict(scores),
        }

    def _llm_route(self, message: str) -> Dict[str, Any]:
        """Use Claude to classify intent when keyword matching is ambiguous.

        Args:
            message: The user's request text.

        Returns:
            Routing result from LLM classification.
        """
        agent_descriptions = (
            "- k8s: Kubernetes operations (pods, deployments, scaling, logs, troubleshooting)\n"
            "- cicd: CI/CD pipelines (deploy, PR review, build analysis, releases)\n"
            "- security: Security scanning (manifests, Dockerfiles, compliance, RBAC)\n"
            "- iac: Infrastructure as Code (Terraform, HCL, modules, cloud resources)\n"
        )

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            system=(
                "You are an intent classifier for a DevOps platform.\n"
                "Classify the user's request to ONE of these agents:\n\n"
                f"{agent_descriptions}\n"
                'Respond with JSON only: {"agent": "<name>", "confidence": <0.0-1.0>}'
            ),
            messages=[{"role": "user", "content": message}],
        )

        result = json.loads(response.content[0].text)
        result["method"] = "llm"
        return result
