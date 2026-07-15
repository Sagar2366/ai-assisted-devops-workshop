# Lab 1: Natural Language to Terraform Generator

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut | Docker Captain

> **Mission:** Use AI to transform natural language infrastructure descriptions into secure, production-ready Terraform configurations — with security best practices baked in from the start.

---

## Concepts

### Shift-Left Security Through Generation

Think of traditional IaC security as a spell-checker that runs *after* you write your essay. Our approach is more like having a security expert co-authoring the essay with you from the very first word.

| Traditional Approach | AI-First Approach |
|---------------------|-------------------|
| Write Terraform → Scan → Fix | Describe intent → Generate secure TF |
| Security is a gate | Security is built-in |
| Developers vs. Security team | AI bridges the gap |
| Fix after the fact | Correct by construction |

### The Generation Pipeline

```
Natural Language Description
        │
        ▼
┌─────────────────────┐
│  Prompt Engineering  │  ← Security requirements injected
│  + Context Window    │  ← Best practices as system prompt
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Claude Generates   │  ← Terraform with security controls
│   Terraform HCL      │  ← Comments explaining decisions
└─────────┬───────────┘
          │
          ▼
  Secure Terraform Output
```

---

## Step 1: Understanding the System Prompt Strategy

The key to generating secure Terraform is a well-crafted system prompt that encodes security requirements. Open `demos/task1_terraform_generator.py` and examine the system prompt:

```python
SYSTEM_PROMPT = """You are a senior cloud infrastructure engineer specializing in
secure Terraform configurations. When generating Terraform code:

1. ALWAYS enable encryption at rest and in transit
2. NEVER use 0.0.0.0/0 for ingress unless explicitly requested for public ALB
3. ALWAYS add resource tagging for governance
4. Use least-privilege IAM policies
5. Enable logging and monitoring by default
6. Pin provider and module versions
7. Use private subnets for compute resources
..."""
```

**Why this matters:** Without these constraints, AI will generate *functional* Terraform that may not be *secure*. The system prompt acts as your organization's security policy encoded in natural language.

## Step 2: Run the Generator

```bash
cd demos
python3 task1_terraform_generator.py
```

The script demonstrates generating Terraform for several scenarios:
- An EKS cluster with managed node groups
- An S3 bucket for application logs
- A VPC with public and private subnets

## Step 3: Examine the Output

For the EKS cluster request, observe how the AI:

1. **Enables envelope encryption** for secrets at rest
2. **Creates private endpoint access** instead of public
3. **Configures security groups** with minimal ingress rules
4. **Adds IAM roles** following least-privilege
5. **Enables control plane logging** for audit trails

```hcl
# Example: AI-generated EKS with security controls
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.29"  # Pinned version

  encryption_config {
    provider {
      key_arn = aws_kms_key.eks.arn  # Envelope encryption
    }
    resources = ["secrets"]
  }

  vpc_config {
    endpoint_private_access = true   # Private API endpoint
    endpoint_public_access  = false  # No public access
    subnet_ids              = var.private_subnet_ids
  }

  enabled_cluster_log_types = [
    "api", "audit", "authenticator",
    "controllerManager", "scheduler"
  ]
}
```

## Step 4: Customize the Generator

Try modifying the infrastructure descriptions to see how security controls adapt:

```python
# Experiment: Request a publicly accessible resource
description = "Create an S3 bucket for hosting a static website"

# Observe: AI should add:
# - CloudFront distribution (not direct S3 access)
# - Bucket policy restricting to CloudFront OAI
# - SSL/TLS certificate
# - Access logging enabled
```

## Step 5: Add Organization-Specific Policies

Extend the system prompt with your organization's requirements:

```python
ORG_POLICIES = """
Additional organizational requirements:
- All resources must be tagged with: Environment, Team, CostCenter, DataClassification
- S3 buckets must have lifecycle policies
- EC2 instances must use IMDSv2
- All databases must have automated backups with 30-day retention
- Resources must be deployed in us-east-1 or eu-west-1 only
"""
```

## Step 6: Structured Output for Pipeline Integration

The generator can output structured JSON alongside HCL for CI/CD integration:

```python
# Request structured output
structured_prompt = """
Generate the Terraform AND a JSON metadata block containing:
{
  "resources_created": [...],
  "security_controls": [...],
  "compliance_tags": [...],
  "estimated_monthly_cost": "..."
}
"""
```

---

## What Success Looks Like

After running `task1_terraform_generator.py`, you should see:

```
═══════════════════════════════════════════════════════════════════
   TASK 1: Natural Language → Secure Terraform Generator
═══════════════════════════════════════════════════════════════════

Experiment 1: EKS Cluster Generation
─────────────────────────────────────────────────────────────────
[Generated Terraform with encryption, private endpoints, logging]

Experiment 2: S3 Bucket Generation
─────────────────────────────────────────────────────────────────
[Generated Terraform with versioning, encryption, access logging]

Experiment 3: VPC Generation
─────────────────────────────────────────────────────────────────
[Generated Terraform with NAT gateways, flow logs, NACLs]

Key Learning: AI-generated Terraform can enforce security policies
at creation time, eliminating the fix-after-deploy cycle.

Next: Lab 2 — Review existing Terraform for security issues
```

---

## Key Takeaway

By encoding security policies into AI prompts, we shift security left to the *generation* phase. The AI doesn't just write functional infrastructure — it writes infrastructure that is secure by default. This eliminates entire categories of misconfigurations before they ever reach a `terraform plan`.

---

**Next:** [Lab 2 — Terraform Reviewer](lab2-terraform-reviewer.md) — Use AI to review existing Terraform for security and cost issues.
