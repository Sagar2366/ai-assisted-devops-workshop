"""
Episode 9: Infrastructure as Code + AI & Security Scanning
Tool: AI Terraform Generator

Describe what you want in English -> Get production-ready Terraform.
Includes generation, review, and cost estimation functions.

Author: Sagar Utekar
Prerequisites:
    - Anthropic API key (set ANTHROPIC_API_KEY env var)
    - pip install anthropic
    - Terraform CLI installed (optional, for applying generated code)
"""
import anthropic
import os
import json

client = anthropic.Anthropic()

TERRAFORM_SYSTEM = """You are a Terraform expert. Generate production-ready Terraform code.

## Standards:
- Always use variables for configurable values
- Include sensible defaults
- Add descriptions to all variables and outputs
- Use modules for reusable components
- Include tags for cost allocation (Project, Environment, ManagedBy)
- Follow HashiCorp naming conventions
- Include backend configuration for remote state
- NEVER hardcode secrets — use variables or data sources

## Security by Default:
- Encryption at rest and in transit
- Least privilege IAM
- Private subnets for workloads
- Security groups with minimal rules
- No public access unless explicitly requested
- Enable logging and monitoring

## Output Format:
Generate multiple files:
1. main.tf — Primary resources
2. variables.tf — All variables with types, descriptions, defaults
3. outputs.tf — Useful outputs
4. versions.tf — Provider versions and backend config

Wrap each file in a code block with the filename as comment:
```hcl
# filename: main.tf
...
```"""


def generate_terraform(description: str, output_dir: str = None) -> dict:
    """Generate Terraform from natural language description."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        system=[{
            "type": "text",
            "text": TERRAFORM_SYSTEM,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{
            "role": "user",
            "content": f"Generate Terraform for:\n\n{description}"
        }]
    )

    result_text = response.content[0].text

    # Parse files from response
    files = {}
    current_file = None
    current_content = []

    for line in result_text.split('\n'):
        if line.startswith('```hcl') or line.startswith('```terraform'):
            continue
        elif line.startswith('# filename:'):
            if current_file and current_content:
                files[current_file] = '\n'.join(current_content)
            current_file = line.replace('# filename:', '').strip()
            current_content = []
        elif line.strip() == '```' and current_file:
            if current_content:
                files[current_file] = '\n'.join(current_content)
            current_file = None
            current_content = []
        elif current_file:
            current_content.append(line)

    if current_file and current_content:
        files[current_file] = '\n'.join(current_content)

    # Save files if output directory specified
    if output_dir and files:
        os.makedirs(output_dir, exist_ok=True)
        for filename, content in files.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"  Created: {filepath}")

    return {"files": files, "raw_response": result_text}


def review_terraform(tf_dir: str) -> str:
    """AI review of existing Terraform code."""

    tf_files = {}
    for f in os.listdir(tf_dir):
        if f.endswith('.tf') or f.endswith('.tfvars'):
            with open(os.path.join(tf_dir, f)) as fh:
                tf_files[f] = fh.read()

    tf_content = ""
    for name, content in tf_files.items():
        tf_content += f"\n### {name}\n```hcl\n{content}\n```\n"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="""You review Terraform code for production readiness.

Check for:
1. SECURITY — Public access, encryption, IAM permissions, secrets handling
2. COST — Over-provisioned resources, missing spot instances, reserved capacity
3. RELIABILITY — Multi-AZ, backups, health checks, auto-scaling
4. STATE SAFETY — Will this destroy/recreate resources unexpectedly?
5. BEST PRACTICES — Module usage, naming, tagging, documentation

Output:
## Risk Assessment: LOW / MEDIUM / HIGH / CRITICAL

### Issues Found
For each issue: [CRITICAL/WARNING/INFO] description + fix""",
        messages=[{
            "role": "user",
            "content": f"Review this Terraform:\n{tf_content}"
        }]
    )

    return response.content[0].text


def estimate_cost(tf_dir: str) -> str:
    """AI cost estimation for Terraform resources."""

    tf_content = ""
    for f in os.listdir(tf_dir):
        if f.endswith('.tf'):
            with open(os.path.join(tf_dir, f)) as fh:
                tf_content += fh.read() + "\n"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system="You estimate AWS monthly costs for Terraform resources. Be specific with pricing. Use current AWS pricing.",
        messages=[{
            "role": "user",
            "content": f"Estimate monthly cost for these resources:\n```hcl\n{tf_content}\n```"
        }]
    )

    return response.content[0].text


if __name__ == "__main__":
    # Demo: Generate EKS infrastructure
    print("Generating Terraform for EKS cluster...")
    result = generate_terraform(
        """Create an EKS cluster with:
        - VPC with 3 AZs, public and private subnets
        - EKS cluster version 1.29
        - 2 managed node groups:
          - general: t3.large, 2-5 nodes, on-demand
          - compute: c5.xlarge, 1-10 nodes, spot instances
        - Cluster autoscaler IAM role (IRSA)
        - ALB Ingress Controller IAM role (IRSA)
        - KMS encryption for secrets
        - CloudWatch logging enabled
        - Region: ap-south-1 (Mumbai)""",
        output_dir="generated/eks-cluster"
    )

    print(f"\nGenerated {len(result['files'])} files!")

    # Review the generated code
    if os.path.exists("generated/eks-cluster"):
        print("\nReviewing generated Terraform...")
        review = review_terraform("generated/eks-cluster")
        print(review)
