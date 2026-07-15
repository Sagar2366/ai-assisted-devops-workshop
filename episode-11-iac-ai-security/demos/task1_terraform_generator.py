#!/usr/bin/env python3
"""
Task 1: Natural Language to Secure Terraform Generator

Uses Claude AI to transform natural language infrastructure descriptions
into secure, production-ready Terraform configurations with security
best practices baked in from generation time.

Episode 11 - AI-Assisted DevOps Workshop
Author: Sagar Utekar | CNCF Ambassador | Kubestronaut
"""

import anthropic


def print_header():
    print("=" * 65)
    print("   TASK 1: Natural Language -> Secure Terraform Generator")
    print("=" * 65)
    print()


SYSTEM_PROMPT = """You are a senior cloud infrastructure engineer specializing in
secure Terraform configurations. When generating Terraform code, you MUST follow
these security requirements:

1. ALWAYS enable encryption at rest (KMS/SSE) and in transit (TLS)
2. NEVER use 0.0.0.0/0 for ingress unless explicitly for public ALB/NLB
3. ALWAYS add resource tagging (Environment, Team, ManagedBy, SecurityLevel)
4. Use least-privilege IAM policies — never use Action: "*" or Resource: "*"
5. Enable logging and monitoring by default (CloudTrail, VPC Flow Logs, Access Logs)
6. Pin provider and module versions with exact constraints
7. Use private subnets for compute resources (EC2, ECS, EKS nodes)
8. Enable deletion protection for stateful resources (RDS, S3, DynamoDB)
9. Use security groups with specific port/CIDR rules, never allow-all
10. Configure backup and disaster recovery (Multi-AZ, cross-region replication)
11. Enforce IMDSv2 for EC2 instances
12. Use secrets manager or parameter store for sensitive values — never hardcode

Output ONLY valid Terraform HCL code with comments explaining security decisions.
Include a terraform {} block with required_providers and version constraints."""


def generate_terraform(description: str) -> str:
    """Generate secure Terraform from a natural language description."""
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""Generate secure, production-ready Terraform for the following:

{description}

Include:
- All necessary resources with security controls
- Comments explaining each security decision
- Variables for configurable values
- Outputs for important resource attributes
"""
            }
        ]
    )

    return message.content[0].text


def run_experiments():
    """Run terraform generation experiments with different infrastructure requests."""

    experiments = [
        {
            "name": "EKS Cluster Generation",
            "description": """Create an EKS cluster with:
- Managed node groups (2-5 nodes, t3.large)
- Private API endpoint
- Cluster autoscaler support
- Pod security standards enforcement
- Integration with AWS Secrets Manager"""
        },
        {
            "name": "S3 Bucket for Application Logs",
            "description": """Create an S3 bucket for storing application logs with:
- 90-day lifecycle transition to Glacier
- Cross-region replication to DR region
- Access only from specific VPC endpoint
- Compliance with data retention requirements"""
        },
        {
            "name": "VPC with Public and Private Subnets",
            "description": """Create a production VPC with:
- 3 availability zones
- Public subnets for load balancers only
- Private subnets for application tier
- Isolated subnets for databases
- NAT gateways for outbound internet access
- VPC flow logs enabled"""
        }
    ]

    for i, experiment in enumerate(experiments, 1):
        print(f"Experiment {i}: {experiment['name']}")
        print("-" * 65)
        print(f"Request: {experiment['description'][:80]}...")
        print()

        try:
            result = generate_terraform(experiment["description"])
            print("Generated Terraform:")
            print()
            print(result)
        except anthropic.APIError as e:
            print(f"API Error: {e}")
            print("Ensure ANTHROPIC_API_KEY is set correctly.")

        print()
        print()


def main():
    print_header()

    print("This demo generates secure Terraform configurations from natural")
    print("language descriptions. Security best practices are enforced by the")
    print("system prompt acting as an encoded security policy.")
    print()

    run_experiments()

    print("=" * 65)
    print()
    print("Key Learning: AI-generated Terraform can enforce security policies")
    print("at creation time, eliminating the fix-after-deploy cycle. The system")
    print("prompt encodes your organization's security requirements as natural")
    print("language constraints that the AI follows during generation.")
    print()
    print("Next: Run task2_terraform_reviewer.py to review existing Terraform")
    print("      for security and cost issues.")


if __name__ == "__main__":
    main()
