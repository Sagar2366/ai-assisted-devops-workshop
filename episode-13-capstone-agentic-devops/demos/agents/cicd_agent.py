#!/usr/bin/env python3
"""
CI/CD Specialist Agent — Agentic DevOps Platform

Handles pull request reviews, pipeline optimization, deployment analysis,
and build failure diagnosis. Uses Claude for code review and pipeline YAML
analysis combined with simulated CI system interaction.

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import anthropic

from .models import AgentResponse, AgentStatus, Severity, ActionItem


# ---------------------------------------------------------------------------
# Simulated CI/CD data
# ---------------------------------------------------------------------------

SIMULATED_PIPELINE = """
name: CI Pipeline
stages:
  - build:
      duration: 4m 32s
      status: success
  - test:
      duration: 12m 18s
      status: success
      coverage: 67%
  - security-scan:
      duration: 3m 45s
      status: success
      findings: 2 medium, 0 critical
  - deploy-staging:
      duration: 2m 10s
      status: success
  - integration-tests:
      duration: 8m 55s
      status: failed
      error: "TimeoutError: /api/checkout endpoint response exceeded 5000ms"
"""

SIMULATED_PR_DIFF = """
diff --git a/src/checkout/handler.py b/src/checkout/handler.py
index 3a4b5c6..7d8e9f0 100644
--- a/src/checkout/handler.py
+++ b/src/checkout/handler.py
@@ -45,6 +45,15 @@ class CheckoutHandler:
     async def process_order(self, order: Order) -> Receipt:
-        result = await self.payment_client.charge(order.total)
+        # Retry logic for payment processing
+        for attempt in range(3):
+            try:
+                result = await self.payment_client.charge(order.total)
+                break
+            except PaymentTimeoutError:
+                if attempt == 2:
+                    raise
+                await asyncio.sleep(2 ** attempt)
+
         inventory = await self.inventory_client.reserve(order.items)
+        await self.notification_client.send_confirmation(order.customer_email)
         return Receipt(order_id=order.id, status="confirmed")
"""


class CICDAgent:
    """Specialist agent for CI/CD pipeline operations.

    Capabilities:
    - review: Analyze pull requests for correctness, performance, and security
    - optimize: Suggest pipeline speed and reliability improvements
    - diagnose: Investigate build and test failures
    - deploy: Plan and validate deployment strategies

    Attributes:
        name: Agent identifier used for routing and audit.
        domain: The operational domain this agent covers.
        capabilities: Keywords that trigger routing to this agent.
    """

    def __init__(self) -> None:
        self.name: str = "cicd-agent"
        self.domain: str = "ci-cd"
        self.capabilities: List[str] = [
            "pipeline", "ci/cd", "cicd", "github actions", "jenkins",
            "deploy", "build", "pr", "pull request", "merge", "branch",
            "artifact", "release", "canary", "rollback", "workflow",
            "gitlab", "test", "coverage",
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
        """Process an incoming CI/CD request.

        Routes to the appropriate sub-handler based on intent analysis:
        PR review, pipeline optimization, failure diagnosis, or deployment.

        Args:
            message: The user's natural language request.
            context: Optional context including PR URL, pipeline ID, etc.

        Returns:
            AgentResponse with analysis, recommendations, and actions.
        """
        message_lower = message.lower()

        if any(word in message_lower for word in ["review", "pr", "pull request", "diff"]):
            return await self._review_pr(message, context)
        elif any(word in message_lower for word in ["optimize", "slow", "speed", "faster"]):
            return await self._optimize_pipeline(message, context)
        elif any(word in message_lower for word in ["fail", "broken", "error", "red"]):
            return await self._diagnose_failure(message, context)
        else:
            return await self._plan_deployment(message, context)

    async def _review_pr(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Review a pull request for code quality, security, and best practices.

        Analyzes the PR diff using Claude to identify potential bugs,
        security issues, performance concerns, and suggest improvements.
        """
        pr_diff = (context or {}).get("diff", SIMULATED_PR_DIFF)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a senior software engineer performing a code review. "
                "Analyze the diff for: 1) Correctness bugs, 2) Error handling gaps, "
                "3) Performance concerns, 4) Security issues, 5) Testing gaps. "
                "Provide specific, actionable feedback with line references."
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Review request: {message}\n\n"
                    f"PR Diff:\n{pr_diff}\n\n"
                    "Provide a structured code review."
                ),
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.88,
            actions=["retrieved_pr_diff", "analyzed_code_changes", "generated_review"],
            action_items=[
                ActionItem(
                    description="Add unit tests for retry logic",
                    severity=Severity.MEDIUM,
                    automated=False,
                    requires_approval=False,
                ),
                ActionItem(
                    description="Add timeout configuration to notification client",
                    severity=Severity.LOW,
                    automated=False,
                    requires_approval=False,
                ),
            ],
            metadata={"operation": "pr_review", "files_changed": 1},
        )

    async def _optimize_pipeline(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Analyze CI/CD pipeline for optimization opportunities.

        Reviews pipeline configuration and execution history to identify
        bottlenecks, parallelization opportunities, and caching strategies.
        """
        pipeline_data = (context or {}).get("pipeline", SIMULATED_PIPELINE)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a CI/CD optimization expert. Analyze the pipeline and suggest "
                "improvements for: 1) Parallelization of independent stages, "
                "2) Caching strategies for dependencies, 3) Test optimization (selective "
                "testing, test splitting), 4) Image layer caching, 5) Resource right-sizing. "
                "Quantify expected time savings where possible."
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Optimization request: {message}\n\n"
                    f"Current pipeline:\n{pipeline_data}\n\n"
                    "Suggest optimizations with estimated impact."
                ),
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.85,
            actions=["analyzed_pipeline_stages", "identified_bottlenecks", "generated_optimizations"],
            action_items=[
                ActionItem(
                    description="Parallelize test and security-scan stages",
                    severity=Severity.MEDIUM,
                    automated=True,
                    requires_approval=True,
                ),
                ActionItem(
                    description="Add dependency caching to build stage",
                    severity=Severity.LOW,
                    automated=True,
                    requires_approval=True,
                ),
            ],
            metadata={"operation": "optimize", "current_duration": "31m 40s"},
        )

    async def _diagnose_failure(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Diagnose CI/CD pipeline failures.

        Analyzes build logs, test results, and pipeline configuration to
        identify the root cause of failures and suggest fixes.
        """
        pipeline_data = (context or {}).get("pipeline", SIMULATED_PIPELINE)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=(
                "You are a CI/CD debugging expert. Analyze the failed pipeline and: "
                "1) Identify the failing stage and root cause, "
                "2) Determine if this is a flaky test, code issue, or infra problem, "
                "3) Provide specific fix with commands/code changes."
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Failure investigation: {message}\n\n"
                    f"Pipeline data:\n{pipeline_data}\n\n"
                    "Diagnose the failure and provide remediation."
                ),
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.86,
            actions=["retrieved_pipeline_logs", "identified_failing_stage", "diagnosed_root_cause"],
            action_items=[
                ActionItem(
                    description="Increase timeout for checkout endpoint integration test",
                    command="Update test config: CHECKOUT_TIMEOUT=10000",
                    severity=Severity.HIGH,
                    automated=False,
                    requires_approval=False,
                ),
            ],
            metadata={"operation": "diagnose", "failing_stage": "integration-tests"},
        )

    async def _plan_deployment(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Plan a deployment strategy (canary, blue-green, rolling).

        Analyzes the deployment requirements and recommends the safest
        strategy based on service criticality and change scope.
        """
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a deployment strategy expert. Based on the request, recommend: "
                "1) Deployment strategy (canary/blue-green/rolling), "
                "2) Rollout percentage and timing, "
                "3) Health check criteria for promotion, "
                "4) Rollback triggers and procedure. "
                "Consider service dependencies and blast radius."
            ),
            messages=[{
                "role": "user",
                "content": f"Deployment planning: {message}",
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.84,
            actions=["analyzed_deployment_scope", "selected_strategy", "generated_plan"],
            action_items=[
                ActionItem(
                    description="Execute canary deployment at 10% traffic",
                    severity=Severity.HIGH,
                    automated=False,
                    requires_approval=True,
                ),
            ],
            metadata={"operation": "deploy_plan"},
        )
