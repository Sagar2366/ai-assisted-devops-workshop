#!/usr/bin/env python3
"""
Task 6: AI-Powered Security Remediation Engine

Uses Claude AI to automatically generate secure, fixed versions of insecure
infrastructure manifests — preserving original functionality while hardening
security posture, with clear explanations of every change made.

Episode 11 - AI-Assisted DevOps Workshop
Author: Sagar Utekar | CNCF Ambassador | Kubestronaut
"""

import os
import anthropic


def print_header():
    print("=" * 65)
    print("   TASK 6: AI-Powered Security Remediation Engine")
    print("=" * 65)
    print()


REMEDIATION_SYSTEM_PROMPT = """You are a security remediation engine that generates
secure, working versions of insecure infrastructure manifests. Your core principles:

1. PRESERVE INTENT: The remediated version must still accomplish what the original
   was trying to do. Do not remove functionality — harden it.

2. LEAST PRIVILEGE: Grant the minimum permissions needed for the workload to function.

3. DEFENSE IN DEPTH: Apply multiple security layers so no single control failure
   leads to compromise.

4. SECURE DEFAULTS: Default to the most secure option; require explicit opt-in to risk.

5. EXPLAIN EVERYTHING: For each change, explain:
   - What was changed
   - Why the original was insecure
   - What attack it prevents
   - Any functional considerations or trade-offs

When remediating:
- Kubernetes: Apply Pod Security Standards (Restricted level), add resource limits,
  fix RBAC to least-privilege, pin images by digest
- Terraform: Enable encryption, restrict network access, add logging, pin versions,
  remove hardcoded secrets
- Dockerfiles: Use multi-stage builds, run as non-root, pin base images, remove secrets,
  minimize attack surface

Output format:
1. ISSUES IDENTIFIED (numbered list with severity)
2. REMEDIATED MANIFEST (complete, working, copy-paste ready)
3. CHANGE LOG (what changed and why, line by line)
"""


def load_file(filepath: str) -> str:
    """Load an infrastructure file for remediation."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)
    with open(full_path, "r") as f:
        return f.read()


def remediate(content: str, file_type: str, filename: str) -> str:
    """Generate a secure, remediated version of an insecure manifest."""
    client = anthropic.Anthropic()

    type_guidance = {
        "kubernetes": """For Kubernetes manifests:
- Set runAsNonRoot: true with a specific UID (e.g., 1000)
- Drop ALL capabilities, add only specific ones needed
- Set readOnlyRootFilesystem: true (use emptyDir for write paths)
- Remove hostPath, hostNetwork, hostPID, hostIPC
- Add resource limits AND requests
- Pin image tags and add image pull policy
- Scope RBAC to specific resources and verbs needed
- Add NetworkPolicy for ingress/egress control
- Mount secrets as volumes, not env vars
- Add seccomp RuntimeDefault profile
- Remove Docker socket mounts""",

        "terraform": """For Terraform configurations:
- Remove hardcoded credentials (use variables/secrets manager)
- Enable encryption at rest for all data stores
- Add public access blocks to S3 buckets
- Restrict security groups to specific ports/CIDRs
- Enable logging (VPC flow logs, S3 access logs, CloudTrail)
- Add deletion protection for stateful resources
- Enable Multi-AZ for databases
- Add backup retention policies
- Pin provider versions
- Enforce IMDSv2 for EC2 instances
- Use IAM roles instead of access keys
- Apply least-privilege IAM policies""",

        "dockerfile": """For Dockerfiles:
- Pin base image by tag AND digest
- Use minimal base image (alpine, distroless, slim)
- Implement multi-stage build
- Remove ALL hardcoded secrets/credentials
- Add USER instruction (create non-root user)
- Remove unnecessary packages and build tools
- Add HEALTHCHECK instruction
- Optimize layer ordering for cache efficiency
- Clean package manager caches
- Add .dockerignore guidance
- Remove dangerous tools (nmap, netcat, etc.)
- Add security-related labels"""
    }

    remediation_prompt = f"""Remediate this insecure {file_type} file: {filename}

REQUIREMENTS:
{type_guidance.get(file_type, "")}

PROCESS:
1. First, list ALL security issues found (with severity)
2. Then, output the COMPLETE remediated file (ready to use as-is)
3. Finally, provide a detailed change log explaining each modification

The remediated version MUST:
- Be syntactically valid and deployable
- Preserve the original functionality/intent
- Follow all security best practices for this file type
- Include comments explaining security decisions

Original insecure file:
```
{content}
```"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=REMEDIATION_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": remediation_prompt}
        ]
    )

    return message.content[0].text


def run_experiments():
    """Run remediation experiments on all insecure sample files."""

    files_to_remediate = [
        {
            "path": "sample-manifests/insecure-deployment.yaml",
            "type": "kubernetes",
            "name": "Kubernetes Deployment + RBAC"
        },
        {
            "path": "sample-manifests/insecure-terraform.tf",
            "type": "terraform",
            "name": "Terraform AWS Infrastructure"
        },
        {
            "path": "sample-manifests/insecure-dockerfile",
            "type": "dockerfile",
            "name": "Python Application Dockerfile"
        }
    ]

    total_issues = 0

    for i, file_info in enumerate(files_to_remediate, 1):
        print(f"Experiment {i}: Remediating {file_info['name']}")
        print("-" * 65)

        try:
            content = load_file(file_info["path"])
            print(f"Loaded: {file_info['path']} ({len(content)} bytes)")
            print(f"Type: {file_info['type']}")
            print("Generating secure remediated version...")
            print()

            result = remediate(
                content,
                file_info["type"],
                file_info["path"]
            )
            print(result)

            # Count issues (approximate from output)
            issue_count = result.lower().count("[critical]") + \
                         result.lower().count("[high]") + \
                         result.lower().count("[medium]") + \
                         result.lower().count("[low]")
            if issue_count == 0:
                # Try counting numbered items in issues section
                import re
                issue_count = len(re.findall(r'^\d+\.', result, re.MULTILINE))
            total_issues += max(issue_count, 1)

        except FileNotFoundError as e:
            print(f"Error: {e}")
        except anthropic.APIError as e:
            print(f"API Error: {e}")

        print()
        print()

    return total_issues


def main():
    print_header()

    print("This demo automatically generates secure, fixed versions of insecure")
    print("infrastructure manifests. The AI preserves original functionality")
    print("while hardening security, and explains every change made.")
    print()

    total_issues = run_experiments()

    print("=" * 65)
    print()
    print(f"Summary: ~{total_issues} issues remediated across 3 files")
    print("All fixes preserve original functionality while hardening security.")
    print()
    print("Key Learning: AI remediation generates complete, working fixes —")
    print("not just suggestions. By understanding intent, it hardens security")
    print("without breaking the deployment. Each change includes rationale")
    print("that educates developers on WHY security controls matter.")
    print()
    print("Congratulations! You have completed all 6 tasks in Episode 11.")
    print("You now have AI-powered tools for the full IaC security lifecycle:")
    print("  Generate -> Review -> Scan -> Audit -> Comply -> Remediate")


if __name__ == "__main__":
    main()
