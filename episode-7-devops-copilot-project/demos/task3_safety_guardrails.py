#!/usr/bin/env python3
"""
Task 3: Safety Guardrails — Three-Tier Protection System
AI-Assisted DevOps Workshop | Episode 7 | Sagar Utekar

Implement the safety engine: SAFE commands auto-run, RESTRICTED require
confirmation, BLOCKED are denied. This is what makes an AI copilot
safe for production use.

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import json
import os
import sys
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed.")
    print("Run: pip install anthropic")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════
# Safety Guardrail Engine
# ═══════════════════════════════════════════════════════════════════════

CLASSIFICATION_SYSTEM_PROMPT = """You are a DevOps command safety classifier. Classify each command into one tier:

SAFE - Read-only commands (kubectl get, docker ps, helm status, cat, ls)
RESTRICTED - State-changing but recoverable (kubectl scale, docker stop, helm upgrade)
BLOCKED - Destructive or irreversible (kubectl delete namespace, rm -rf /, docker system prune --all)

Respond with JSON only:
{"risk_level": "SAFE|RESTRICTED|BLOCKED", "reason": "brief explanation"}
"""

COLORS = {
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "RESET": "\033[0m",
}


class SafetyGuardrail:
    """Three-tier safety system for DevOps command execution."""

    def __init__(self, client):
        self.client = client
        self.execution_log = []

    def classify(self, command):
        """Classify a command using Claude AI."""
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=150,
            system=CLASSIFICATION_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Classify: {command}"}
            ]
        )
        text = response.content[0].text
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except (json.JSONDecodeError, ValueError):
            return {"risk_level": "BLOCKED", "reason": "Failed to classify — blocking for safety"}

    def execute(self, command, force=False, force_reason=None):
        """Execute a command through the safety guardrail system."""
        print(f"\n{'─' * 65}")
        print(f"  Command: {command}")
        print(f"{'─' * 65}")

        # Classify the command
        classification = self.classify(command)
        risk_level = classification.get("risk_level", "BLOCKED")
        reason = classification.get("reason", "No reason provided")

        print(f"  Risk Level: {self._colorize(risk_level)}")
        print(f"  Reason:     {reason}")

        # Apply guardrail policy
        if risk_level == "SAFE":
            return self._handle_safe(command, reason)
        elif risk_level == "RESTRICTED":
            if force:
                return self._handle_force_override(command, reason, force_reason)
            return self._handle_restricted(command, reason)
        elif risk_level == "BLOCKED":
            if force:
                return self._handle_force_override(command, reason, force_reason)
            return self._handle_blocked(command, reason)
        else:
            return self._handle_blocked(command, "Unknown classification")

    def _handle_safe(self, command, reason):
        """SAFE: Auto-execute without confirmation."""
        print(f"\n  {COLORS['GREEN']}[AUTO-RUN]{COLORS['RESET']} Executing safe command...")
        print(f"  {COLORS['DIM']}$ {command}{COLORS['RESET']}")
        # Simulate execution
        print(f"  {COLORS['GREEN']}>>> Command executed successfully (simulated){COLORS['RESET']}")
        self._log(command, "SAFE", "executed", reason)
        return {"status": "executed", "risk_level": "SAFE"}

    def _handle_restricted(self, command, reason):
        """RESTRICTED: Require human confirmation."""
        print(f"\n  {COLORS['YELLOW']}[CONFIRMATION REQUIRED]{COLORS['RESET']}")
        print(f"  This command modifies system state.")
        print(f"  Command: {command}")

        # In demo mode, simulate the confirmation prompt
        print(f"\n  {COLORS['YELLOW']}Proceed? (y/n): {COLORS['RESET']}", end="")
        try:
            response = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            response = "n"

        if response == "y":
            print(f"  {COLORS['GREEN']}>>> Confirmed. Executing... (simulated){COLORS['RESET']}")
            self._log(command, "RESTRICTED", "confirmed_and_executed", reason)
            return {"status": "executed", "risk_level": "RESTRICTED"}
        else:
            print(f"  {COLORS['YELLOW']}>>> Execution cancelled by user.{COLORS['RESET']}")
            self._log(command, "RESTRICTED", "denied_by_user", reason)
            return {"status": "denied", "risk_level": "RESTRICTED"}

    def _handle_blocked(self, command, reason):
        """BLOCKED: Refuse to execute."""
        print(f"\n  {COLORS['RED']}{'=' * 55}{COLORS['RESET']}")
        print(f"  {COLORS['RED']}{COLORS['BOLD']}  BLOCKED — COMMAND DENIED{COLORS['RESET']}")
        print(f"  {COLORS['RED']}{'=' * 55}{COLORS['RESET']}")
        print(f"  {COLORS['RED']}This command is too dangerous for automated execution.")
        print(f"  Reason: {reason}{COLORS['RESET']}")
        print(f"\n  {COLORS['DIM']}To override: use --force with a documented reason{COLORS['RESET']}")
        self._log(command, "BLOCKED", "denied", reason)
        return {"status": "blocked", "risk_level": "BLOCKED"}

    def _handle_force_override(self, command, reason, force_reason):
        """Emergency override with --force flag."""
        print(f"\n  {COLORS['RED']}[FORCE OVERRIDE ACTIVATED]{COLORS['RESET']}")
        print(f"  Override reason: {force_reason}")
        print(f"  {COLORS['YELLOW']}>>> Executing with override... (simulated){COLORS['RESET']}")
        self._log(command, "OVERRIDE", "force_executed", f"{reason} | Override: {force_reason}")
        return {"status": "force_executed", "risk_level": "OVERRIDE"}

    def _log(self, command, risk_level, action, reason):
        """Log the execution decision."""
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "risk_level": risk_level,
            "action": action,
            "reason": reason,
        })

    def _colorize(self, level):
        """Return colored risk level text."""
        color_map = {"SAFE": "GREEN", "RESTRICTED": "YELLOW", "BLOCKED": "RED"}
        color = COLORS.get(color_map.get(level, ""), COLORS["RESET"])
        return f"{color}{COLORS['BOLD']}[{level}]{COLORS['RESET']}"


def main():
    """Run the safety guardrail demonstration."""
    print("\n" + "=" * 65)
    print("  TASK 3: Three-Tier Safety Guardrails")
    print("=" * 65)
    print("  Goal: Build the execution engine with safety gates")
    print("  SAFE → auto-run | RESTRICTED → confirm | BLOCKED → deny")
    print("=" * 65)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n  ERROR: ANTHROPIC_API_KEY not set.")
        print("  Run: export ANTHROPIC_API_KEY='your-key-here'\n")
        sys.exit(1)

    client = anthropic.Anthropic()
    guardrail = SafetyGuardrail(client)

    # ─────────────────────────────────────────────────────────────────
    # Test Tier 1: SAFE command
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 1: SAFE Command (should auto-run)")
    print("-" * 65)
    guardrail.execute("kubectl get pods -n default")

    # ─────────────────────────────────────────────────────────────────
    # Test Tier 2: RESTRICTED command
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 2: RESTRICTED Command (requires confirmation)")
    print("-" * 65)
    guardrail.execute("kubectl scale deployment/api-server --replicas=5")

    # ─────────────────────────────────────────────────────────────────
    # Test Tier 3: BLOCKED command
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 3: BLOCKED Command (should be denied)")
    print("-" * 65)
    guardrail.execute("kubectl delete namespace production")

    # ─────────────────────────────────────────────────────────────────
    # Test Emergency Override
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 4: Emergency Override (--force)")
    print("-" * 65)
    guardrail.execute(
        "docker system prune --all -f",
        force=True,
        force_reason="Disk at 98% capacity — emergency cleanup approved by SRE lead"
    )

    # ─────────────────────────────────────────────────────────────────
    # Execution Summary
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Execution Log:")
    print("-" * 65)
    for entry in guardrail.execution_log:
        print(f"  [{entry['risk_level']:10}] {entry['action']:25} | {entry['command'][:40]}")

    # ─────────────────────────────────────────────────────────────────
    # Key Learning
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  Key Learning:")
    print("=" * 65)
    print("  - Three tiers create defense-in-depth for AI copilots")
    print("  - SAFE auto-runs keep the workflow fast for read-only ops")
    print("  - RESTRICTED confirmation prevents accidental state changes")
    print("  - BLOCKED denial stops catastrophic commands entirely")
    print("  - Emergency override (--force) exists but requires a reason")
    print("=" * 65)
    print("\n  Next: Task 4 — Audit Logging")
    print("  We'll record every decision for compliance and debugging.\n")


if __name__ == "__main__":
    main()
