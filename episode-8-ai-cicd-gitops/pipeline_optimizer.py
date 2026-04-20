"""
Episode 8: AI-Powered CI/CD & GitOps
AI Pipeline Optimizer -- Analyzes GitHub Actions workflows and suggests optimizations.

Author: Sagar Utekar
Prerequisites:
    - Claude API key set as ANTHROPIC_API_KEY environment variable
    - Python anthropic package installed (pip install anthropic)
    - GitHub Actions workflow files in .github/workflows/
"""
import anthropic
import os
import glob

client = anthropic.Anthropic()

def read_workflows() -> dict:
    """Read all GitHub Actions workflow files."""
    workflows = {}
    for f in glob.glob(".github/workflows/*.yml") + glob.glob(".github/workflows/*.yaml"):
        with open(f) as fh:
            workflows[f] = fh.read()
    return workflows


def analyze_workflows(workflows: dict) -> str:
    """Analyze all workflows for optimization opportunities."""

    workflow_text = ""
    for path, content in workflows.items():
        workflow_text += f"\n### {path}\n```yaml\n{content}\n```\n"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="""You are a CI/CD optimization expert. Analyze GitHub Actions workflows and provide specific, actionable improvements.

Focus on:
1. **Speed** — Parallel jobs, caching, skipping unnecessary steps
2. **Cost** — Runner selection, job consolidation, timeout limits
3. **Security** — Pinned action versions, secret handling, permissions
4. **Reliability** — Retry logic, timeout handling, failure notifications
5. **Intelligence** — Where AI can be added (code review, test generation, deploy decisions)

For each optimization:
- Estimated impact (time saved, cost reduced, risk mitigated)
- Exact YAML change needed
- Before vs After comparison""",
        messages=[{
            "role": "user",
            "content": f"Analyze these CI/CD workflows:\n{workflow_text}"
        }]
    )

    return response.content[0].text


def generate_smart_pipeline() -> str:
    """Generate an AI-enhanced CI/CD pipeline from scratch."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": """Generate a production-ready GitHub Actions workflow that includes AI at every stage:

1. **On PR Open:**
   - AI code review (using Claude API)
   - Automated test generation for changed code
   - Security scan with AI analysis

2. **On Push to Main:**
   - Build with intelligent caching (cache keys based on actual dependency changes)
   - Run tests with AI-powered failure analysis
   - If tests fail -> AI suggests fix, creates PR

3. **Deploy Stage:**
   - AI analyzes the diff and determines deployment risk (low/medium/high)
   - Low risk -> auto-deploy canary -> watch metrics -> promote
   - Medium risk -> deploy canary -> require human approval
   - High risk -> block deploy -> request senior review

4. **Post-Deploy:**
   - AI monitors error rates for 30 minutes
   - Auto-rollback if error rate exceeds threshold
   - Generate deployment summary with AI

Output as a complete, valid GitHub Actions YAML file."""
        }]
    )

    return response.content[0].text


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        print("Generating AI-enhanced pipeline...")
        print(generate_smart_pipeline())
    else:
        workflows = read_workflows()
        if workflows:
            print(f"Analyzing {len(workflows)} workflows...")
            print(analyze_workflows(workflows))
        else:
            print("No workflows found in .github/workflows/")
            print("Generating a sample AI-enhanced pipeline instead...\n")
            print(generate_smart_pipeline())
