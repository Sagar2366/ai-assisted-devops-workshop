"""
Episode 8: AI-Powered CI/CD & GitOps
CI Fix Agent -- Analyzes build failures and suggests/applies fixes.

Author: Sagar Utekar
Prerequisites:
    - Claude API key set as ANTHROPIC_API_KEY environment variable
    - Python anthropic package installed (pip install anthropic)
    - gh CLI installed and authenticated (for fetching build logs)
"""
import anthropic
import subprocess
import json

client = anthropic.Anthropic()

def get_build_log(log_file: str = None) -> str:
    """Get the failing build log."""
    if log_file:
        with open(log_file) as f:
            return f.read()
    # Or get from last CI run
    result = subprocess.run(
        "gh run list --limit 1 --status failure --json databaseId -q '.[0].databaseId'",
        shell=True, capture_output=True, text=True
    )
    if result.stdout.strip():
        run_id = result.stdout.strip()
        log_result = subprocess.run(
            f"gh run view {run_id} --log-failed",
            shell=True, capture_output=True, text=True
        )
        return log_result.stdout
    return "No failing builds found."


def analyze_and_fix(build_log: str):
    """Analyze build failure and generate fix."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="""You are a CI/CD expert. Analyze build failures and provide EXACT fixes.

Output format:
## Root Cause
[One sentence]

## Fix
[Exact code changes needed -- show full file paths and diffs]

## Commands to Verify
```bash
[Commands to run to verify the fix works]
```

## Prevention
[How to prevent this failure in the future]""",
        messages=[{
            "role": "user",
            "content": f"This CI build failed. Analyze and fix:\n\n```\n{build_log[:20000]}\n```"
        }]
    )

    return response.content[0].text


def auto_fix_pipeline():
    """Full auto-fix pipeline."""
    print("Fetching build logs...")
    log = get_build_log()

    if "No failing builds" in log:
        print("No failing builds found!")
        return

    print("Analyzing failure...")
    fix = analyze_and_fix(log)
    print(fix)

    # Ask for confirmation before applying
    print("\n" + "="*50)
    response = input("Apply this fix? (y/n): ")
    if response.lower() == 'y':
        print("Use Claude Code to apply: paste the fix above")
    else:
        print("Fix saved for manual review.")


if __name__ == "__main__":
    auto_fix_pipeline()
