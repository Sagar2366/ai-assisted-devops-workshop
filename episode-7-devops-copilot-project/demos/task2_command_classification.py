#!/usr/bin/env python3
"""
Task 2: Command Classification — AI Risk Assessment
AI-Assisted DevOps Workshop | Episode 7 | Sagar Utekar

Use Claude to classify DevOps commands into SAFE, RESTRICTED, or BLOCKED
based on their potential impact on production systems.

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import json
import os
import sys

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed.")
    print("Run: pip install anthropic")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════
# Classification System Prompt
# ═══════════════════════════════════════════════════════════════════════

CLASSIFICATION_SYSTEM_PROMPT = """You are a DevOps command safety classifier. Your job is to assess
the risk level of commands that an engineer wants to run.

Classify each command into exactly one of three tiers:

## SAFE
Commands that only READ data and cannot modify system state.
Examples: kubectl get, docker ps, cat, ls, helm status, kubectl describe

## RESTRICTED
Commands that MODIFY state but can be recovered from or are scoped.
Examples: kubectl scale, docker stop, kubectl rollout restart,
helm upgrade, kubectl apply (non-destructive)

## BLOCKED
Commands that DESTROY data, affect production globally, or are irreversible.
Examples: kubectl delete namespace, rm -rf, docker system prune --all,
kubectl delete pv, helm uninstall (production)

Respond ONLY with valid JSON in this exact format:
{
  "risk_level": "SAFE|RESTRICTED|BLOCKED",
  "category": "brief category name",
  "reason": "one-sentence explanation of why this classification applies",
  "command": "the original command"
}
"""

# ═══════════════════════════════════════════════════════════════════════
# Test Commands
# ═══════════════════════════════════════════════════════════════════════

TEST_COMMANDS = [
    "kubectl get pods -n production",
    "kubectl delete namespace prod",
    "rm -rf /tmp/old-logs",
    "docker ps --format 'table {{.Names}}\\t{{.Status}}'",
    "docker system prune --all -f",
    "kubectl scale deployment/api --replicas=3",
    "kubectl rollout restart deployment/web-frontend",
    "helm status my-release",
]

# Color codes for terminal output
COLORS = {
    "SAFE": "\033[92m",       # Green
    "RESTRICTED": "\033[93m", # Yellow
    "BLOCKED": "\033[91m",    # Red
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
}


def classify_command(client, command):
    """Send a command to Claude for risk classification."""
    print(f"\n  Classifying: {COLORS['DIM']}{command}{COLORS['RESET']}")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        system=CLASSIFICATION_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Classify this command: {command}"}
        ]
    )

    # Extract the text response
    response_text = response.content[0].text

    # Parse the JSON response
    try:
        result = json.loads(response_text)
        return result
    except json.JSONDecodeError:
        # Try to extract JSON from the response if it has extra text
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(response_text[start:end])
        return {
            "risk_level": "UNKNOWN",
            "category": "parse_error",
            "reason": "Could not parse AI response",
            "command": command,
        }


def display_result(result):
    """Display a classification result with color coding."""
    level = result.get("risk_level", "UNKNOWN")
    color = COLORS.get(level, COLORS["RESET"])

    print(f"  Result:  {color}{COLORS['BOLD']}[{level}]{COLORS['RESET']}")
    print(f"  Category: {result.get('category', 'N/A')}")
    print(f"  Reason:   {result.get('reason', 'N/A')}")


def main():
    """Run the command classification demo."""
    print("\n" + "=" * 65)
    print("  TASK 2: AI Command Classification")
    print("=" * 65)
    print("  Goal: Use Claude to classify DevOps commands by risk level")
    print("  Model: claude-sonnet-4-20250514")
    print("=" * 65)

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n  ERROR: ANTHROPIC_API_KEY environment variable not set.")
        print("  Run: export ANTHROPIC_API_KEY='your-key-here'\n")
        sys.exit(1)

    # Initialize the Anthropic client
    client = anthropic.Anthropic()
    print("\n  Anthropic client initialized successfully.")

    # ─────────────────────────────────────────────────────────────────
    # Classify test commands
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Classifying DevOps commands through Claude...")
    print("-" * 65)

    results = {"SAFE": 0, "RESTRICTED": 0, "BLOCKED": 0}

    for command in TEST_COMMANDS:
        result = classify_command(client, command)
        display_result(result)
        level = result.get("risk_level", "UNKNOWN")
        if level in results:
            results[level] += 1

    # ─────────────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Classification Summary:")
    print("-" * 65)
    print(f"  {COLORS['SAFE']}SAFE:       {results['SAFE']} commands{COLORS['RESET']}")
    print(f"  {COLORS['RESTRICTED']}RESTRICTED: {results['RESTRICTED']} commands{COLORS['RESET']}")
    print(f"  {COLORS['BLOCKED']}BLOCKED:    {results['BLOCKED']} commands{COLORS['RESET']}")
    print(f"  Total:      {sum(results.values())} commands classified")
    print("-" * 65)

    # ─────────────────────────────────────────────────────────────────
    # Key Learning
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  Key Learning:")
    print("=" * 65)
    print("  - Claude classifies commands using a structured system prompt")
    print("  - JSON response format enables programmatic decision-making")
    print("  - Three tiers (SAFE/RESTRICTED/BLOCKED) map to action policies")
    print("  - The AI understands DevOps context and blast radius")
    print("=" * 65)
    print("\n  Next: Task 3 — Safety Guardrails")
    print("  We'll build the execution engine that acts on these classifications.\n")


if __name__ == "__main__":
    main()
