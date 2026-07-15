#!/usr/bin/env python3
"""
Infrastructure-as-Code Specialist Agent — Agentic DevOps Platform

Handles Terraform module generation, HCL code review, drift detection
analysis, and infrastructure cost optimization. Uses Claude for code
generation and review with deep knowledge of cloud provider best practices.

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import anthropic

from .models import AgentResponse, AgentStatus, Severity, ActionItem


# ---------------------------------------------------------------------------
# Simulated Terraform data
# ---------------------------------------------------------------------------

SIMULATED_TERRAFORM = """
resource "aws_s3_bucket" "data" {
  bucket = "company-data-prod"
  acl    = "public-read"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "web-server"
  }
}

resource "aws_security_group" "web" {
  name = "web-sg"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
"""

SIMULATED_PLAN_OUTPUT = """
Terraform will perform the following actions:

  # aws_instance.web will be updated in-place
  ~ resource "aws_instance" "web" {
      ~ instance_type = "t2.micro" -> "t3.medium"
        tags          = {
            "Name" = "web-server"
        }
    }

  # aws_s3_bucket.logs will be created
  + resource "aws_s3_bucket" "logs" {
      + bucket = "company-logs-prod"
      + acl    = "private"
    }

Plan: 1 to add, 1 to change, 0 to destroy.
"""


class IaCAgent:
    """Specialist agent for Infrastructure-as-Code operations.

    Capabilities:
    - generate: Create Terraform modules from natural language descriptions
    - review: Analyze HCL for security, cost, and best practices
    - plan: Interpret terraform plan output and assess risk
    - optimize: Suggest cost and performance improvements

    Attributes:
        name: Agent identifier used for routing and audit.
        domain: The operational domain this agent covers.
        capabilities: Keywords that trigger routing to this agent.
    """

    def __init__(self) -> None:
        self.name: str = "iac-agent"
        self.domain: str = "infrastructure-as-code"
        self.capabilities: List[str] = [
            "terraform", "hcl", "module", "infrastructure", "provider",
            "resource", "state", "plan", "apply", "drift", "pulumi",
            "cloudformation", "iac", "tf", "s3", "vpc", "ec2",
            "aws", "azure", "gcp",
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
        """Process an incoming IaC request.

        Routes to generation, review, plan analysis, or optimization
        based on intent keywords in the message.

        Args:
            message: The user's natural language request.
            context: Optional context including HCL code, plan output, etc.

        Returns:
            AgentResponse with generated code, findings, or recommendations.
        """
        message_lower = message.lower()

        if any(word in message_lower for word in ["generate", "create", "write", "build"]):
            return await self._generate(message, context)
        elif any(word in message_lower for word in ["review", "check", "audit", "scan"]):
            return await self._review(message, context)
        elif any(word in message_lower for word in ["plan", "diff", "change", "drift"]):
            return await self._analyze_plan(message, context)
        else:
            return await self._optimize(message, context)

    async def _generate(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Generate Terraform code from a natural language description.

        Produces production-ready HCL with proper variable usage, outputs,
        tagging, encryption, and least-privilege IAM policies.
        """
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=(
                "You are a Terraform expert. Generate production-ready HCL code "
                "following these standards:\n"
                "1. Use variables.tf for all configurable values with descriptions and defaults\n"
                "2. Use outputs.tf for useful resource attributes\n"
                "3. Proper resource naming with project/environment prefixes\n"
                "4. Tags: Name, Environment, Project, ManagedBy=terraform\n"
                "5. Encryption at rest for all storage resources\n"
                "6. Least-privilege IAM policies\n"
                "7. Include comments explaining design decisions\n"
                "8. Use data sources for AMI lookups instead of hardcoded IDs\n\n"
                "Output the complete module with main.tf, variables.tf, and outputs.tf."
            ),
            messages=[{
                "role": "user",
                "content": f"Generate Terraform for: {message}",
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.87,
            actions=["parsed_requirements", "generated_terraform_module", "included_variables_outputs"],
            action_items=[
                ActionItem(
                    description="Review generated Terraform before applying",
                    command="terraform plan -out=tfplan",
                    severity=Severity.MEDIUM,
                    automated=False,
                    requires_approval=True,
                ),
            ],
            metadata={"operation": "generate", "output_files": ["main.tf", "variables.tf", "outputs.tf"]},
        )

    async def _review(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Review Terraform/HCL code for security and best practices.

        Checks for: public S3 buckets, overly permissive security groups,
        missing encryption, hardcoded values, missing tags, and state
        management issues.
        """
        hcl_code = (context or {}).get("code", SIMULATED_TERRAFORM)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a Terraform security and best-practices reviewer. "
                "Analyze the HCL code and report findings in these categories:\n"
                "1. CRITICAL: Public data exposure, no encryption, wildcard permissions\n"
                "2. HIGH: Missing security groups, overly permissive access, hardcoded secrets\n"
                "3. MEDIUM: Missing tags, no lifecycle rules, hardcoded values\n"
                "4. LOW: Naming conventions, missing descriptions, formatting\n\n"
                "For each finding, provide: severity, resource affected, current value, "
                "recommended fix with corrected HCL snippet."
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Review request: {message}\n\n"
                    f"Terraform code:\n```hcl\n{hcl_code}\n```\n\n"
                    "Provide a prioritized review."
                ),
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.89,
            actions=["parsed_hcl", "checked_security", "checked_best_practices", "generated_review"],
            action_items=[
                ActionItem(
                    description="Remove public-read ACL from S3 bucket",
                    severity=Severity.CRITICAL,
                    automated=False,
                    requires_approval=True,
                ),
                ActionItem(
                    description="Restrict security group ingress to specific CIDR/ports",
                    severity=Severity.CRITICAL,
                    automated=False,
                    requires_approval=True,
                ),
                ActionItem(
                    description="Add encryption configuration to S3 bucket",
                    severity=Severity.HIGH,
                    automated=False,
                    requires_approval=False,
                ),
            ],
            metadata={"operation": "review", "findings_count": 5},
        )

    async def _analyze_plan(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Analyze a terraform plan output for risk assessment.

        Interprets planned changes to identify potentially dangerous
        operations (destroys, in-place updates) and assesses blast radius.
        """
        plan_output = (context or {}).get("plan", SIMULATED_PLAN_OUTPUT)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=(
                "You are a Terraform plan reviewer. Analyze the plan output and provide:\n"
                "1. Summary of changes (creates, updates, destroys)\n"
                "2. Risk assessment (low/medium/high) based on resource types affected\n"
                "3. Potential issues: data loss, downtime, permission changes\n"
                "4. Recommendation: safe to apply, needs review, or block\n"
                "Be concise and highlight the most important concerns."
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Plan analysis request: {message}\n\n"
                    f"Terraform plan output:\n```\n{plan_output}\n```\n\n"
                    "Assess risk and provide recommendation."
                ),
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.86,
            actions=["parsed_plan_output", "assessed_risk", "checked_destructive_changes"],
            action_items=[
                ActionItem(
                    description="Verify instance type change won't cause downtime",
                    severity=Severity.MEDIUM,
                    automated=False,
                    requires_approval=True,
                ),
            ],
            metadata={
                "operation": "plan_analysis",
                "adds": 1,
                "changes": 1,
                "destroys": 0,
            },
        )

    async def _optimize(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Suggest infrastructure cost and performance optimizations.

        Analyzes resource configurations and recommends right-sizing,
        reserved capacity, spot instances, and architectural improvements.
        """
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a cloud infrastructure optimization expert. Provide recommendations "
                "for: 1) Compute right-sizing (instance types, auto-scaling), "
                "2) Storage optimization (lifecycle policies, tiers), "
                "3) Network cost reduction (NAT gateway consolidation, VPC endpoints), "
                "4) Reserved/Spot/Savings Plans opportunities, "
                "5) Architecture improvements (serverless where appropriate). "
                "Quantify estimated monthly savings where possible."
            ),
            messages=[{
                "role": "user",
                "content": f"Optimization request: {message}",
            }],
        )

        return AgentResponse(
            agent_name=self.name,
            content=response.content[0].text,
            confidence=0.82,
            actions=["analyzed_infrastructure", "identified_savings", "generated_recommendations"],
            metadata={"operation": "optimize"},
        )
