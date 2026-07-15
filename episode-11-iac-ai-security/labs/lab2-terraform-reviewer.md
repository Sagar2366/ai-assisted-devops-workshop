# Lab 2: AI-Powered Terraform Reviewer

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut | Docker Captain

> **Mission:** Build an AI reviewer that analyzes existing Terraform configurations for security vulnerabilities, cost optimization opportunities, and operational best practices — providing actionable findings with severity ratings and fix suggestions.

---

## Concepts

### Beyond Pattern Matching

Traditional Terraform scanners (tfsec, checkov) use predefined rules. They catch known patterns but miss contextual issues:

| Traditional Scanner | AI Reviewer |
|--------------------|-------------|
| "S3 bucket lacks encryption" | "This S3 bucket stores PII (based on naming) but lacks encryption AND access logging" |
| Fixed severity ratings | Context-aware severity (public-facing vs. internal) |
| Rule ID references | Explanation of *why* it matters with attack scenarios |
| Generic fix suggestions | Fixes that match your existing code style |

### The Review Pipeline

Think of this like a senior engineer doing a pull request review, but one who has memorized every AWS security best practice, CIS benchmark, and cost optimization guide:

```
Terraform Code
      │
      ▼
┌──────────────────┐
│  Security Review │ → Misconfigurations, exposed secrets, IAM issues
├──────────────────┤
│   Cost Review    │ → Over-provisioning, missing reservations, waste
├──────────────────┤
│   Ops Review     │ → Missing monitoring, no DR, single points of failure
└──────────────────┘
      │
      ▼
Prioritized Findings with Fixes
```

---

## Step 1: Review the Insecure Terraform Sample

First, examine the intentionally insecure Terraform file:

```bash
cat demos/sample-manifests/insecure-terraform.tf
```

This file contains multiple security issues:
- Public S3 bucket with no encryption
- Security group with 0.0.0.0/0 ingress on all ports
- Unencrypted RDS instance with public access
- IAM policy with `*` permissions

## Step 2: Run the Reviewer

```bash
cd demos
python3 task2_terraform_reviewer.py
```

The reviewer will analyze the insecure Terraform and produce findings organized by:
- **CRITICAL** — Immediate exploitation risk
- **HIGH** — Significant security exposure
- **MEDIUM** — Best practice violations
- **LOW** — Optimization opportunities

## Step 3: Understand the Review Prompt Structure

The effectiveness of the reviewer depends on how we structure the analysis request:

```python
review_prompt = f"""Review this Terraform configuration for:

1. SECURITY ISSUES (reference CIS AWS Foundations Benchmark where applicable):
   - Data exposure risks (public access, missing encryption)
   - Network security (overly permissive rules, missing NACLs)
   - IAM/access control (over-privileged policies, missing MFA)
   - Secrets management (hardcoded credentials, missing KMS)

2. COST OPTIMIZATION:
   - Over-provisioned resources
   - Missing auto-scaling configurations
   - Unused or redundant resources

3. OPERATIONAL RISKS:
   - Missing monitoring/alerting
   - No backup/DR configuration
   - Single points of failure

For each finding, provide:
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- Category: Security / Cost / Operations
- Description: What the issue is
- Impact: What could go wrong
- CIS Reference: If applicable (e.g., CIS AWS 2.1.1)
- Fix: Terraform code to remediate

Terraform to review:
{terraform_code}"""
```

## Step 4: Analyze a Specific Finding

Let's trace through how the AI identifies the open security group issue:

**Input:**
```hcl
resource "aws_security_group" "allow_all" {
  name = "allow-all-traffic"
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

**AI Analysis:**
```
Severity: CRITICAL
Category: Security
CIS Reference: CIS AWS 4.1, 4.2
Description: Security group allows all inbound traffic from any source
Impact: Any internet-connected attacker can reach all ports on associated
        resources. This is equivalent to having no firewall.
Attack Scenario: Port scanning reveals open services → exploitation of
                 unpatched services → lateral movement within VPC
Fix: [Restricted security group with specific port/CIDR rules]
```

## Step 5: Multi-Resource Context Analysis

The AI reviewer excels at finding issues that span multiple resources:

```python
# The AI can detect:
# 1. An RDS instance in a public subnet (cross-referencing subnet and RDS configs)
# 2. An S3 bucket policy that contradicts bucket ACLs
# 3. A Lambda with VPC config but no NAT gateway for internet access
# 4. An ECS task definition referencing a public ECR image
```

## Step 6: Integrate with CI/CD

Structure the output for automated pipeline consumption:

```python
# Request JSON output for CI/CD integration
json_prompt = """
Output findings as JSON array:
[{
  "id": "FINDING-001",
  "severity": "CRITICAL",
  "category": "security",
  "resource": "aws_security_group.allow_all",
  "cis_reference": "CIS AWS 4.1",
  "title": "Unrestricted ingress on all ports",
  "description": "...",
  "remediation": "...",
  "terraform_fix": "..."
}]
"""
```

This enables:
- Failing CI pipelines on CRITICAL/HIGH findings
- Tracking security posture over time
- Automated PR comments with findings

---

## What Success Looks Like

After running `task2_terraform_reviewer.py`:

```
═══════════════════════════════════════════════════════════════════
   TASK 2: AI-Powered Terraform Security & Cost Reviewer
═══════════════════════════════════════════════════════════════════

Reviewing: demos/sample-manifests/insecure-terraform.tf
─────────────────────────────────────────────────────────────────

[CRITICAL] Public S3 bucket without encryption (CIS AWS 2.1.1, 2.1.2)
[CRITICAL] Security group allows 0.0.0.0/0 on all ports (CIS AWS 4.1)
[HIGH] RDS instance publicly accessible without encryption (CIS AWS 2.3.1)
[HIGH] IAM policy with wildcard permissions (CIS AWS 1.16)
[MEDIUM] Missing access logging on S3 bucket (CIS AWS 2.1.3)
[MEDIUM] No deletion protection on RDS instance
[LOW] Resources missing required tags

Summary: 2 CRITICAL | 2 HIGH | 2 MEDIUM | 1 LOW

Key Learning: AI reviews catch contextual issues that static rules miss,
like correlating resource relationships and understanding data sensitivity.

Next: Lab 3 — Scan Kubernetes manifests for security issues
```

---

## Key Takeaway

AI-powered Terraform review goes beyond checking individual resources against static rules. It understands relationships between resources, infers data sensitivity from naming conventions, and provides contextual remediation that matches your existing code patterns. This makes security review accessible to every developer, not just security specialists.

---

**Next:** [Lab 3 — K8s Security Scanner](lab3-k8s-security-scanner.md) — Scan Kubernetes manifests for RBAC, SecurityContext, and network policy issues.
