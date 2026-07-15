#!/usr/bin/env python3
"""
Task 2: AI-Powered Terraform Security and Cost Reviewer

Uses Claude AI to review existing Terraform configurations for security
vulnerabilities, cost optimization opportunities, and operational best
practices. Produces prioritized findings with CIS references and fixes.

Episode 11 - AI-Assisted DevOps Workshop
Author: Sagar Utekar | CNCF Ambassador | Kubestronaut
"""

import os
import anthropic


def print_header():
    print("=" * 65)
    print("   TASK 2: AI-Powered Terraform Security & Cost Reviewer")
    print("=" * 65)
    print()


REVIEW_SYSTEM_PROMPT = """You are a senior cloud security architect performing a
comprehensive Terraform code review. You have deep expertise in:

- AWS security best practices and the CIS AWS Foundations Benchmark v3.0
- Cost optimization and FinOps principles
- Operational excellence and reliability patterns
- Compliance frameworks (SOC2, PCI-DSS, HIPAA, GDPR)

When reviewing Terraform code, you identify issues with:
- Specific severity levels (CRITICAL, HIGH, MEDIUM, LOW)
- CIS Benchmark references where applicable
- Clear description of the vulnerability and its impact
- Concrete Terraform code to remediate the issue
- Attack scenarios that explain real-world risk

Format each finding as:
[SEVERITY] Title (CIS Reference if applicable)
Description: What is wrong
Impact: What could happen if exploited
Remediation: Terraform code to fix it
"""


def load_terraform_file(filepath: str) -> str:
    """Load a Terraform file for review."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)
    with open(full_path, "r") as f:
        return f.read()


def review_terraform(terraform_code: str, context: str = "") -> str:
    """Review Terraform code for security, cost, and operational issues."""
    client = anthropic.Anthropic()

    review_prompt = f"""Perform a comprehensive security and cost review of this
Terraform configuration. Identify ALL issues across these categories:

1. SECURITY ISSUES (reference CIS AWS Foundations Benchmark):
   - Data exposure risks (public access, missing encryption)
   - Network security (overly permissive security groups, missing NACLs)
   - IAM/access control (over-privileged policies, hardcoded credentials)
   - Secrets management (plaintext passwords, missing KMS encryption)
   - Logging and monitoring gaps

2. COST OPTIMIZATION:
   - Over-provisioned resources
   - Missing auto-scaling configurations
   - Resources that should use reserved/spot pricing
   - Redundant or unused resources

3. OPERATIONAL RISKS:
   - Missing monitoring/alerting
   - No backup/disaster recovery configuration
   - Single points of failure
   - Missing deletion protection on stateful resources

For each finding provide:
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- CIS Reference: If applicable (e.g., CIS AWS 2.1.1)
- Description: Clear explanation of the issue
- Impact: Specific attack scenario or business risk
- Remediation: Exact Terraform code to fix it

After all findings, provide a summary with counts by severity.

{f"Additional context: {context}" if context else ""}

Terraform code to review:
```hcl
{terraform_code}
```"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=REVIEW_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": review_prompt}
        ]
    )

    return message.content[0].text


def run_experiments():
    """Run Terraform review experiments."""

    # Experiment 1: Review the insecure Terraform sample
    print("Experiment 1: Full Security Review of Insecure Terraform")
    print("-" * 65)

    try:
        terraform_code = load_terraform_file(
            "sample-manifests/insecure-terraform.tf"
        )
        print(f"Loaded Terraform file ({len(terraform_code)} bytes)")
        print("Sending to AI for comprehensive security review...")
        print()

        result = review_terraform(terraform_code)
        print(result)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Ensure sample-manifests/insecure-terraform.tf exists")
    except anthropic.APIError as e:
        print(f"API Error: {e}")

    print()
    print()

    # Experiment 2: Focused cost review
    print("Experiment 2: Cost Optimization Focus")
    print("-" * 65)

    cost_terraform = """
resource "aws_instance" "web" {
  count         = 10
  ami           = "ami-12345678"
  instance_type = "m5.2xlarge"

  root_block_device {
    volume_size = 500
    volume_type = "io1"
    iops        = 10000
  }
}

resource "aws_nat_gateway" "nat" {
  count         = 6
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
}

resource "aws_rds_cluster" "main" {
  engine         = "aurora-mysql"
  instance_class = "db.r5.4xlarge"
  cluster_members = [
    aws_rds_cluster_instance.main[0].id,
    aws_rds_cluster_instance.main[1].id,
    aws_rds_cluster_instance.main[2].id,
  ]
}
"""

    try:
        print("Reviewing over-provisioned infrastructure for cost savings...")
        print()
        result = review_terraform(
            cost_terraform,
            context="This is a development environment used by a team of 5 developers"
        )
        print(result)
    except anthropic.APIError as e:
        print(f"API Error: {e}")

    print()
    print()

    # Experiment 3: IAM-focused review
    print("Experiment 3: IAM Security Deep Dive")
    print("-" * 65)

    iam_terraform = """
resource "aws_iam_role" "lambda_role" {
  name = "lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
        AWS     = "*"
      }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:*",
          "dynamodb:*",
          "logs:*",
          "ec2:*",
          "iam:*"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user" "ci_user" {
  name = "ci-deploy-user"
}

resource "aws_iam_access_key" "ci_key" {
  user = aws_iam_user.ci_user.name
}

output "ci_secret_key" {
  value = aws_iam_access_key.ci_key.secret
}
"""

    try:
        print("Reviewing IAM configuration for privilege escalation risks...")
        print()
        result = review_terraform(
            iam_terraform,
            context="Lambda function processes payment webhooks"
        )
        print(result)
    except anthropic.APIError as e:
        print(f"API Error: {e}")


def main():
    print_header()

    print("This demo reviews Terraform configurations for security vulnerabilities,")
    print("cost optimization opportunities, and operational risks. The AI provides")
    print("CIS Benchmark references and specific Terraform fixes for each finding.")
    print()

    run_experiments()

    print()
    print("=" * 65)
    print()
    print("Key Learning: AI reviews catch contextual issues that static rules")
    print("miss, like correlating resource relationships, understanding data")
    print("sensitivity from naming, and identifying privilege escalation paths")
    print("across multiple IAM resources.")
    print()
    print("Next: Run task3_k8s_security_scanner.py to scan Kubernetes manifests")
    print("      for security misconfigurations.")


if __name__ == "__main__":
    main()
