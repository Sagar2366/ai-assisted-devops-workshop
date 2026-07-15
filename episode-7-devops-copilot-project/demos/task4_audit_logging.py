#!/usr/bin/env python3
"""
Task 4: Audit Logging — JSON Audit Trail for Every Action
AI-Assisted DevOps Workshop | Episode 7 | Sagar Utekar

Record every copilot action (command, classification, decision, timestamp)
to a structured JSON log. This is what makes an AI copilot auditable
and safe for production environments with compliance requirements.

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed.")
    print("Run: pip install anthropic")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════

MODEL = "claude-sonnet-4-20250514"
AUDIT_DIR = Path("/tmp/devops-copilot-audit")

CLASSIFICATION_SYSTEM_PROMPT = """Classify this DevOps command into one risk tier:
SAFE - Read-only (kubectl get, docker ps, helm status, cat, ls)
RESTRICTED - Modifies state, recoverable (kubectl scale, docker stop, helm upgrade)
BLOCKED - Destructive/irreversible (kubectl delete namespace, rm -rf, docker system prune --all)
Respond with JSON only: {"risk_level": "SAFE|RESTRICTED|BLOCKED", "reason": "brief explanation"}"""

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
# Audit Logger
# ═══════════════════════════════════════════════════════════════════════

class AuditLogger:
    """JSON Lines audit logger for all copilot actions.

    Format: one JSON object per line (.jsonl) — easy to grep, parse, and
    ship to centralized logging systems (ELK, Splunk, Datadog).
    """

    def __init__(self, log_dir=AUDIT_DIR):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = f"sess_{uuid.uuid4().hex[:8]}"
        self.user = os.environ.get("USER", "unknown")
        self.entries = []
        self._log_file = self._get_log_file()

    def _get_log_file(self):
        """Generate daily log file path."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.log_dir / f"copilot-audit-{date_str}.jsonl"

    def log(self, command, risk_level, action_taken, ai_reasoning, output_preview=None):
        """Record an audit entry.

        Args:
            command: The command that was processed
            risk_level: SAFE, RESTRICTED, or BLOCKED
            action_taken: executed, confirmed, denied, cancelled, blocked
            ai_reasoning: Why the AI classified it this way
            output_preview: First N chars of command output (optional)
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "user": self.user,
            "command": command,
            "risk_level": risk_level,
            "action_taken": action_taken,
            "ai_reasoning": ai_reasoning,
            "output_preview": output_preview[:200] if output_preview else None,
        }

        self.entries.append(entry)

        # Write to file (append mode — safe for concurrent writes)
        with open(self._log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def get_recent(self, n=10):
        """Get the N most recent entries from this session."""
        return self.entries[-n:]

    def get_stats(self):
        """Get summary statistics for this session."""
        stats = {
            "total": len(self.entries),
            "SAFE": 0,
            "RESTRICTED": 0,
            "BLOCKED": 0,
            "executed": 0,
            "denied": 0,
            "cancelled": 0,
        }
        for entry in self.entries:
            level = entry["risk_level"]
            action = entry["action_taken"]
            if level in stats:
                stats[level] += 1
            if action in stats:
                stats[action] += 1
        return stats

    def display_log(self):
        """Print formatted audit log to terminal."""
        print("\n" + "-" * 65)
        print("  Audit Log Entries:")
        print("-" * 65)
        print(f"  {'Timestamp':<22} {'Risk':<12} {'Action':<12} {'Command':<20}")
        print(f"  {'─' * 20} {'─' * 10} {'─' * 10} {'─' * 18}")

        for entry in self.entries:
            ts = entry["timestamp"][11:19]  # HH:MM:SS
            risk = entry["risk_level"]
            action = entry["action_taken"]
            cmd = entry["command"][:20]

            # Color by risk level
            if risk == "SAFE":
                color = COLORS["GREEN"]
            elif risk == "RESTRICTED":
                color = COLORS["YELLOW"]
            else:
                color = COLORS["RED"]

            print(f"  {ts:<22} {color}{risk:<12}{COLORS['RESET']} {action:<12} {cmd}")

        print("-" * 65)


# ═══════════════════════════════════════════════════════════════════════
# Command Classifier (reused from Task 2)
# ═══════════════════════════════════════════════════════════════════════

def classify_command(client, command):
    """Classify a command's risk level."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=150,
        system=CLASSIFICATION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Classify: {command}"}]
    )
    text = response.content[0].text
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except (json.JSONDecodeError, ValueError):
        return {"risk_level": "BLOCKED", "reason": "Classification failed — blocking for safety"}


# ═══════════════════════════════════════════════════════════════════════
# Simulated Guardrail + Audit Integration
# ═══════════════════════════════════════════════════════════════════════

def process_command_with_audit(client, logger, command):
    """Full pipeline: classify → guardrail → audit."""
    print(f"\n  Command: {COLORS['BOLD']}{command}{COLORS['RESET']}")

    # Classify
    classification = classify_command(client, command)
    risk_level = classification.get("risk_level", "BLOCKED")
    reason = classification.get("reason", "No reason provided")

    # Display classification
    color_map = {"SAFE": "GREEN", "RESTRICTED": "YELLOW", "BLOCKED": "RED"}
    color = COLORS.get(color_map.get(risk_level, ""), COLORS["RESET"])
    print(f"  Risk:    {color}[{risk_level}]{COLORS['RESET']}")
    print(f"  Reason:  {reason}")

    # Apply guardrail policy and determine action
    if risk_level == "SAFE":
        action = "executed"
        print(f"  Action:  {COLORS['GREEN']}Auto-executed (simulated){COLORS['RESET']}")
        output = "NAME        READY   STATUS    RESTARTS   AGE\nweb-abc12   1/1     Running   0          2h"
    elif risk_level == "RESTRICTED":
        action = "confirmed"
        print(f"  Action:  {COLORS['YELLOW']}Confirmed by user (simulated){COLORS['RESET']}")
        output = "deployment.apps/web scaled"
    else:
        action = "denied"
        print(f"  Action:  {COLORS['RED']}DENIED — command blocked{COLORS['RESET']}")
        output = None

    # Log to audit trail
    entry = logger.log(
        command=command,
        risk_level=risk_level,
        action_taken=action,
        ai_reasoning=reason,
        output_preview=output
    )

    print(f"  Logged:  {COLORS['DIM']}entry written to {logger._log_file.name}{COLORS['RESET']}")
    return entry


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

def main():
    """Run the audit logging demonstration."""
    print("\n" + "=" * 65)
    print("  TASK 4: Audit Logging — JSON Trail for Every Action")
    print("=" * 65)
    print("  Goal: Record every copilot action with timestamp + context")
    print("  Format: JSON Lines (.jsonl) — one entry per line")
    print("=" * 65)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n  ERROR: ANTHROPIC_API_KEY not set.")
        print("  Run: export ANTHROPIC_API_KEY='your-key-here'\n")
        sys.exit(1)

    client = anthropic.Anthropic()
    logger = AuditLogger()

    print(f"\n  Session ID: {logger.session_id}")
    print(f"  Log file:   {logger._log_file}")
    print(f"  User:       {logger.user}")

    # ─────────────────────────────────────────────────────────────────
    # Experiment 1: Process several commands through the pipeline
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 1: Processing commands with audit logging")
    print("-" * 65)

    test_commands = [
        "kubectl get pods -n production",
        "kubectl scale deployment/api --replicas=5",
        "kubectl delete namespace production",
        "docker ps --format 'table {{.Names}}\\t{{.Status}}'",
        "helm status my-release",
        "rm -rf /var/lib/etcd",
    ]

    for command in test_commands:
        process_command_with_audit(client, logger, command)

    # ─────────────────────────────────────────────────────────────────
    # Experiment 2: Display the audit log
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 2: Reviewing the audit trail")
    print("-" * 65)

    logger.display_log()

    # ─────────────────────────────────────────────────────────────────
    # Experiment 3: Session statistics
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 3: Session statistics")
    print("-" * 65)

    stats = logger.get_stats()
    print(f"\n  Total commands processed: {stats['total']}")
    print(f"  {COLORS['GREEN']}SAFE:       {stats['SAFE']}{COLORS['RESET']}")
    print(f"  {COLORS['YELLOW']}RESTRICTED: {stats['RESTRICTED']}{COLORS['RESET']}")
    print(f"  {COLORS['RED']}BLOCKED:    {stats['BLOCKED']}{COLORS['RESET']}")
    print(f"\n  Executed: {stats['executed']}  |  Denied: {stats['denied']}  |  Cancelled: {stats['cancelled']}")

    # ─────────────────────────────────────────────────────────────────
    # Experiment 4: Raw JSON output
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Experiment 4: Raw JSON log file content")
    print("-" * 65)

    print(f"\n  File: {logger._log_file}")
    print(f"  Size: {logger._log_file.stat().st_size} bytes")
    print(f"\n  Sample entry (pretty-printed):")
    print(f"  {json.dumps(logger.entries[0], indent=4)}")

    # ─────────────────────────────────────────────────────────────────
    # Key Learning
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  Key Learning:")
    print("=" * 65)
    print("  - Every AI copilot action MUST be logged for accountability")
    print("  - JSON Lines format is grep-friendly and ships to any log system")
    print("  - Audit logs answer 'what did the AI do?' during incidents")
    print("  - Session IDs group actions for timeline reconstruction")
    print("  - Include AI reasoning — not just what happened, but WHY")
    print("=" * 65)
    print("\n  Next: Task 5 — Natural Language Interface")
    print("  We'll add plain English → kubectl/docker translation.\n")


if __name__ == "__main__":
    main()
