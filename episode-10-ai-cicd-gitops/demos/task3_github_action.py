#!/usr/bin/env python3
"""
Task 3: GitHub Action Generator
================================
Generates a complete GitHub Action workflow file for AI-powered PR review.
Outputs a production-ready YAML that can be dropped into .github/workflows/.

Usage:
    export ANTHROPIC_API_KEY="your-key"
    python3 task3_github_action.py
"""

import anthropic


def main():
    print("=" * 65)
    print("  TASK 3: GITHUB ACTION GENERATOR")
    print("  Generate a complete AI-powered PR review GitHub Action")
    print("=" * 65)

    # ─── System Prompt ───────────────────────────────────────────────
    SYSTEM_PROMPT = """You are a GitHub Actions expert. Generate production-ready workflow YAML files.
Follow these best practices:
- Pin action versions to full SHA or major version
- Use minimal permissions (principle of least privilege)
- Include error handling and timeout settings
- Add concurrency controls to avoid duplicate runs
- Use environment variables for configuration
Return ONLY valid YAML — no markdown fences, no explanation."""

    # ─── Generate the Workflow ───────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Generating AI-powered PR review workflow...")
    print("-" * 65)

    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": """Generate a GitHub Actions workflow file for AI-powered code review that:

1. Name: "AI Code Review"
2. Triggers on pull_request events (opened, synchronize, reopened)
3. Permissions: contents read, pull-requests write
4. Concurrency: cancel in-progress runs for same PR
5. Job "ai-review" on ubuntu-latest with 10-minute timeout
6. Steps:
   a. Checkout with fetch-depth: 0
   b. Setup Python 3.11
   c. Install anthropic SDK
   d. Get PR diff using gh CLI (save to pr_diff.txt)
   e. Run Python script that:
      - Reads pr_diff.txt
      - Sends to Claude with a code review system prompt
      - Writes results to review_output.md
   f. Post review as PR comment using gh CLI
   g. Fail the check if critical issues are found (exit code based on review)
7. Use secrets.ANTHROPIC_API_KEY and secrets.GITHUB_TOKEN
8. Include proper error handling with continue-on-error where appropriate

Return the complete YAML."""}
        ]
    )

    workflow_yaml = message.content[0].text

    print("\n" + "=" * 65)
    print("  GENERATED WORKFLOW")
    print("=" * 65)
    print(workflow_yaml)

    # ─── Also generate the companion review script ───────────────────
    print("\n" + "-" * 65)
    print("  Generating companion review script...")
    print("-" * 65)

    message2 = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system="You are a Python developer. Generate clean, production-ready scripts. Return ONLY the Python code — no markdown.",
        messages=[
            {"role": "user", "content": """Generate a Python script (review.py) that:
1. Reads pr_diff.txt
2. Sends the diff to Claude with a system prompt for code review
3. The review should look for: security issues, bugs, performance problems
4. Writes the review to review_output.md in Markdown format
5. Exits with code 1 if any CRITICAL issues found, 0 otherwise
6. Handles errors gracefully (API failures, empty diffs)
7. Truncates diffs over 50000 chars with a note

Use anthropic SDK. Use claude-sonnet-4-20250514 model."""}
        ]
    )

    review_script = message2.content[0].text

    print("\n" + "=" * 65)
    print("  GENERATED REVIEW SCRIPT (review.py)")
    print("=" * 65)
    print(review_script)

    # ─── Summary ─────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Key Learning:")
    print("  A complete AI code review system needs two parts: the workflow")
    print("  YAML (triggers, permissions, steps) and the review script (API")
    print("  call, prompt engineering, output formatting). Together they give")
    print("  every PR an instant AI review — no human action required.")
    print("-" * 65)
    print("  Next: python3 task4_argocd_risk_gate.py")
    print("-" * 65)


if __name__ == "__main__":
    main()
