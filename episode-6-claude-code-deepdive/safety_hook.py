"""
Episode 6: Claude Code Deep Dive for DevOps
AI-Assisted DevOps Workshop

Pre-tool hook: Block dangerous commands before Claude Code runs them.

Author: Sagar Utekar

Prerequisites:
    - Python 3.10+
    - Claude Code installed (npm install -g @anthropic-ai/claude-code)
    - hooks_config.json copied to .claude/settings.json with correct paths

Usage:
    This script is invoked automatically by Claude Code via the PreToolUse hook.
    It receives the tool input as a CLI argument, checks for blocked/warning
    patterns, and exits non-zero to block dangerous commands.
"""
import sys
import json

BLOCKED_PATTERNS = [
    "kubectl delete",
    "kubectl exec",
    "terraform destroy",
    "rm -rf",
    "docker system prune",
    "helm uninstall",
]

WARNING_PATTERNS = [
    "kubectl apply",
    "terraform apply",
    "kubectl scale",
    "kubectl rollout",
]


def check_command(tool_input: str):
    try:
        data = json.loads(tool_input)
        command = data.get("command", "")
    except (json.JSONDecodeError, AttributeError):
        command = tool_input

    for pattern in BLOCKED_PATTERNS:
        if pattern in command:
            print(f"BLOCKED: Command contains '{pattern}' — not allowed by safety policy", file=sys.stderr)
            sys.exit(1)  # Non-zero exit = block the tool

    for pattern in WARNING_PATTERNS:
        if pattern in command:
            print(f"WARNING: Command contains '{pattern}' — proceeding with caution", file=sys.stderr)


if __name__ == "__main__":
    check_command(sys.argv[1] if len(sys.argv) > 1 else "")
