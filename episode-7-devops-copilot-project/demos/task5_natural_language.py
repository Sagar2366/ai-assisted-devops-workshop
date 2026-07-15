#!/usr/bin/env python3
"""
Task 5: Natural Language → DevOps Commands
AI-Assisted DevOps Workshop | Episode 7 | Sagar Utekar

Convert plain English requests into executable kubectl/docker commands.
"show me crashing pods" → kubectl get pods --field-selector=status.phase=Failed

The key principle: natural language is the UX layer, safety is still
the execution layer. Even friendly-sounding requests get classified.

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
# System Prompts
# ═══════════════════════════════════════════════════════════════════════

NL_TRANSLATION_PROMPT = """You are a DevOps command translator. Convert natural language
requests into exact shell commands for Kubernetes, Docker, or Helm.

Rules:
1. Output ONLY valid JSON — no markdown, no backticks, no explanation outside JSON
2. Use the most specific flags available (--field-selector, -o jsonpath, etc.)
3. Default to the 'default' namespace unless the user specifies one
4. Prefer safe read-only commands when the intent is ambiguous
5. If the request is truly unclear, set command to "UNCLEAR" and explain in the explanation field

Available tools: kubectl, docker, helm, curl, jq

Response format:
{
    "command": "the exact command to run",
    "explanation": "brief explanation of what this does",
    "risk_level": "SAFE|RESTRICTED|BLOCKED"
}

Examples:
- "show crashing pods" → {"command": "kubectl get pods --field-selector=status.phase=Failed -A", "explanation": "Lists all failed pods across namespaces", "risk_level": "SAFE"}
- "restart the web service" → {"command": "kubectl rollout restart deployment/web", "explanation": "Rolling restart of web deployment", "risk_level": "RESTRICTED"}
- "delete staging namespace" → {"command": "kubectl delete namespace staging", "explanation": "Deletes namespace and all resources", "risk_level": "BLOCKED"}
"""

CLASSIFICATION_PROMPT = """Classify this DevOps command into one risk tier:
SAFE - Read-only (kubectl get, docker ps, helm status, cat, ls)
RESTRICTED - Modifies state, recoverable (kubectl scale, docker stop, helm upgrade)
BLOCKED - Destructive/irreversible (kubectl delete namespace, rm -rf, docker system prune --all)
Respond with JSON only: {"risk_level": "SAFE|RESTRICTED|BLOCKED", "reason": "brief explanation"}"""

MODEL = "claude-sonnet-4-20250514"

COLORS = {
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "CYAN": "\033[96m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "RESET": "\033[0m",
}


# ═══════════════════════════════════════════════════════════════════════
# Natural Language Translator
# ═══════════════════════════════════════════════════════════════════════

def translate_natural_language(client, request):
    """Convert a natural language request to a DevOps command.

    Args:
        client: Anthropic client instance
        request: Natural language description (e.g., "show crashing pods")

    Returns:
        dict with 'command', 'explanation', 'risk_level'
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=250,
        system=NL_TRANSLATION_PROMPT,
        messages=[
            {"role": "user", "content": f"Translate: {request}"}
        ]
    )

    text = response.content[0].text.strip()

    try:
        # Handle potential markdown wrapping
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except (json.JSONDecodeError, ValueError):
        return {
            "command": "UNCLEAR",
            "explanation": "Could not parse AI response",
            "risk_level": "BLOCKED"
        }


def classify_command(client, command):
    """Classify a command's risk level (from Task 2)."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=150,
        system=CLASSIFICATION_PROMPT,
        messages=[{"role": "user", "content": f"Classify: {command}"}]
    )
    text = response.content[0].text
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except (json.JSONDecodeError, ValueError):
        return {"risk_level": "BLOCKED", "reason": "Classification failed"}


def is_natural_language(user_input):
    """Detect if input is natural language (vs a direct command).

    Heuristic: if it starts with a known command prefix, it's a command.
    """
    command_prefixes = [
        "kubectl", "docker", "helm", "terraform", "ansible",
        "cat", "grep", "find", "ls", "ps", "top", "curl",
        "git", "make", "npm", "pip", "rm", "mv", "cp"
    ]
    first_word = user_input.strip().split()[0].lower() if user_input.strip() else ""
    return first_word not in command_prefixes


def display_translation(request, result, classification=None):
    """Display a natural language translation with formatting."""
    command = result.get("command", "UNCLEAR")
    explanation = result.get("explanation", "")
    risk = result.get("risk_level", "BLOCKED")

    # Risk level color
    color_map = {"SAFE": "GREEN", "RESTRICTED": "YELLOW", "BLOCKED": "RED"}
    color = COLORS.get(color_map.get(risk, ""), COLORS["RESET"])

    print(f"\n  {COLORS['DIM']}Input:{COLORS['RESET']}   \"{request}\"")
    print(f"  {COLORS['CYAN']}Command:{COLORS['RESET']} {command}")
    print(f"  {COLORS['DIM']}Reason:{COLORS['RESET']}  {explanation}")
    print(f"  {COLORS['DIM']}Risk:{COLORS['RESET']}    {color}{COLORS['BOLD']}[{risk}]{COLORS['RESET']}")

    # Show what the guardrail would do
    if risk == "SAFE":
        print(f"  {COLORS['GREEN']}Action:  Would auto-execute{COLORS['RESET']}")
    elif risk == "RESTRICTED":
        print(f"  {COLORS['YELLOW']}Action:  Would ask for confirmation{COLORS['RESET']}")
    else:
        print(f"  {COLORS['RED']}Action:  Would be BLOCKED{COLORS['RESET']}")


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

def main():
    """Run the natural language translation demonstration."""
    print("\n" + "=" * 65)
    print("  TASK 5: Natural Language → DevOps Commands")
    print("=" * 65)
    print("  Goal: Convert plain English to kubectl/docker commands")
    print("  Key:  NL is convenience; safety pipeline still enforces rules")
    print("=" * 65)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n  ERROR: ANTHROPIC_API_KEY not set.")
        print("  Run: export ANTHROPIC_API_KEY='your-key-here'\n")
        sys.exit(1)

    client = anthropic.Anthropic()
    print("\n  Anthropic client initialized.")

    # ─────────────────────────────────────────────────────────────────
    # Experiment 1: Safe read-only translations
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 1: Safe (read-only) natural language requests")
    print("-" * 65)

    safe_requests = [
        "show me pods that are crashing",
        "how much memory are the nodes using?",
        "list all services in production namespace",
        "what docker containers are running?",
    ]

    for request in safe_requests:
        result = translate_natural_language(client, request)
        display_translation(request, result)

    # ─────────────────────────────────────────────────────────────────
    # Experiment 2: Restricted (state-changing) translations
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 2: Restricted (state-changing) requests")
    print("-" * 65)

    restricted_requests = [
        "restart the auth service",
        "scale the web frontend to 10 replicas",
        "stop the redis container",
    ]

    for request in restricted_requests:
        result = translate_natural_language(client, request)
        display_translation(request, result)

    # ─────────────────────────────────────────────────────────────────
    # Experiment 3: Dangerous requests (should be blocked)
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 3: Dangerous requests (should produce BLOCKED commands)")
    print("-" * 65)

    dangerous_requests = [
        "delete the production namespace",
        "remove all docker images and containers",
        "wipe the etcd data directory",
    ]

    for request in dangerous_requests:
        result = translate_natural_language(client, request)
        display_translation(request, result)

    # ─────────────────────────────────────────────────────────────────
    # Experiment 4: Ambiguous requests
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 4: Ambiguous requests (AI should choose safest)")
    print("-" * 65)

    ambiguous_requests = [
        "clean up the cluster",
        "fix the broken pod",
        "check on things",
    ]

    for request in ambiguous_requests:
        result = translate_natural_language(client, request)
        display_translation(request, result)

    # ─────────────────────────────────────────────────────────────────
    # Experiment 5: Input detection (NL vs direct command)
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 5: Detecting natural language vs direct commands")
    print("-" * 65)

    test_inputs = [
        "kubectl get pods",
        "show me crashing pods",
        "docker ps",
        "what containers are running?",
        "helm status my-release",
        "is my app healthy?",
    ]

    for inp in test_inputs:
        is_nl = is_natural_language(inp)
        mode = "Natural Language" if is_nl else "Direct Command"
        color = COLORS["CYAN"] if is_nl else COLORS["GREEN"]
        print(f"  {color}[{mode:<17}]{COLORS['RESET']} {inp}")

    # ─────────────────────────────────────────────────────────────────
    # Key Learning
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  Key Learning:")
    print("=" * 65)
    print("  - Natural language removes the need to memorize kubectl flags")
    print("  - The AI generates commands; the safety pipeline still decides")
    print("  - Ambiguous requests should default to the safest interpretation")
    print("  - Always show the generated command BEFORE executing it")
    print("  - NL detection lets users mix plain English and direct commands")
    print("=" * 65)
    print("\n  Next: Task 6 — Full Copilot")
    print("  We'll wire everything together into a complete tool.\n")


if __name__ == "__main__":
    main()
