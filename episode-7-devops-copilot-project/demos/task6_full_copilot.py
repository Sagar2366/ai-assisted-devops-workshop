#!/usr/bin/env python3
"""
Task 6: Full DevOps Copilot — All Features Combined
AI-Assisted DevOps Workshop | Episode 7 | Sagar Utekar

The complete DevOps copilot with: natural language interface,
command classification, three-tier safety guardrails, and
full audit logging. Production-ready.

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic rich
"""

import json
import os
import sys
import uuid
import time
from datetime import datetime
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# ═══════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════

VERSION = "1.0.0"
MODEL = "claude-sonnet-4-20250514"
LOG_DIR = Path("/tmp/devops-copilot-audit")

COLORS = {
    "GREEN": "\033[92m", "YELLOW": "\033[93m", "RED": "\033[91m",
    "CYAN": "\033[96m", "BOLD": "\033[1m", "DIM": "\033[2m", "RESET": "\033[0m",
}

# ═══════════════════════════════════════════════════════════════════════
# System Prompts
# ═══════════════════════════════════════════════════════════════════════

CLASSIFY_PROMPT = """Classify this DevOps command into one risk tier:
SAFE - Read-only (kubectl get, docker ps, helm status)
RESTRICTED - Modifies state, recoverable (scale, restart, stop)
BLOCKED - Destructive/irreversible (delete namespace, rm -rf, prune --all)
Respond with JSON only: {"risk_level": "SAFE|RESTRICTED|BLOCKED", "reason": "brief"}"""

TRANSLATE_PROMPT = """Convert natural language to a DevOps command.
Respond with JSON: {"command": "exact command", "explanation": "what it does", "risk_level": "SAFE|RESTRICTED|BLOCKED"}"""


# ═══════════════════════════════════════════════════════════════════════
# Audit Logger (from Task 4)
# ═══════════════════════════════════════════════════════════════════════

class AuditLogger:
    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.log_dir = LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "audit.log"
        self.entries = []

    def log(self, command, classification, action, reasoning=""):
        try:
            user = os.getlogin()
        except OSError:
            user = os.getenv("USER", "unknown")
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": self.session_id,
            "user": user,
            "command": command,
            "classification": classification,
            "action_taken": action,
            "ai_reasoning": reasoning,
        }
        self.entries.append(entry)
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def get_stats(self):
        stats = {"total": len(self.entries), "SAFE": 0, "RESTRICTED": 0, "BLOCKED": 0}
        for e in self.entries:
            cls = e["classification"]
            if cls in stats:
                stats[cls] += 1
        return stats


# ═══════════════════════════════════════════════════════════════════════
# DevOps Copilot (combines all tasks)
# ═══════════════════════════════════════════════════════════════════════

class DevOpsCopilot:
    """Full DevOps Copilot with NL interface, classification, guardrails, and logging."""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.logger = AuditLogger()
        self.start_time = time.time()
        self.commands_executed = 0
        self.commands_blocked = 0

    def print_banner(self):
        banner = f"""
{'=' * 65}
  DevOps Copilot v{VERSION} | Session: {self.logger.session_id}
{'=' * 65}
  Commands:
    /help   - Show help       /audit  - View audit log
    /stats  - Show stats      /exit   - Exit copilot

  Input modes:
    Direct command:  kubectl get pods
    Natural language: show me crashing pods
{'=' * 65}
"""
        if HAS_RICH:
            console.print(Panel(
                f"[bold cyan]DevOps Copilot[/] v{VERSION} | Session: {self.logger.session_id}\n\n"
                "[dim]/help /audit /stats /exit[/]\n"
                "Direct commands or natural language supported",
                title="Ready", border_style="cyan"
            ))
        else:
            print(banner)

    def is_direct_command(self, text):
        """Detect if input is a direct command vs natural language."""
        prefixes = ["kubectl", "docker", "helm", "k9s", "terraform",
                    "ansible", "git", "curl", "cat", "ls", "grep", "rm"]
        return any(text.strip().startswith(p) for p in prefixes)

    def classify_command(self, command):
        """Classify a command's risk level via Claude."""
        response = self.client.messages.create(
            model=MODEL, max_tokens=150,
            system=CLASSIFY_PROMPT,
            messages=[{"role": "user", "content": f"Classify: {command}"}]
        )
        text = response.content[0].text
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except (json.JSONDecodeError, ValueError):
            return {"risk_level": "BLOCKED", "reason": "Classification failed"}

    def translate_to_command(self, natural_language):
        """Translate natural language to a DevOps command."""
        response = self.client.messages.create(
            model=MODEL, max_tokens=250,
            system=TRANSLATE_PROMPT,
            messages=[{"role": "user", "content": natural_language}]
        )
        text = response.content[0].text
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except (json.JSONDecodeError, ValueError):
            return {"command": "", "explanation": "Could not translate", "risk_level": "BLOCKED"}

    def apply_guardrail(self, command, classification):
        """Apply the three-tier safety guardrail."""
        risk = classification.get("risk_level", "BLOCKED")
        reason = classification.get("reason", "")

        if risk == "SAFE":
            print(f"  {COLORS['GREEN']}[AUTO-RUN]{COLORS['RESET']} {command}")
            print(f"  {COLORS['GREEN']}>>> Executed successfully (simulated){COLORS['RESET']}")
            self.logger.log(command, "SAFE", "executed", reason)
            self.commands_executed += 1
            return True

        elif risk == "RESTRICTED":
            print(f"  {COLORS['YELLOW']}[CONFIRM]{COLORS['RESET']} {command}")
            print(f"  Reason: {reason}")
            resp = input(f"  {COLORS['YELLOW']}Execute? (y/n): {COLORS['RESET']}").strip().lower()
            if resp == "y":
                print(f"  {COLORS['GREEN']}>>> Confirmed and executed (simulated){COLORS['RESET']}")
                self.logger.log(command, "RESTRICTED", "confirmed", reason)
                self.commands_executed += 1
                return True
            else:
                print(f"  {COLORS['YELLOW']}>>> Cancelled by user{COLORS['RESET']}")
                self.logger.log(command, "RESTRICTED", "cancelled", reason)
                return False

        else:  # BLOCKED
            print(f"  {COLORS['RED']}[BLOCKED] {command}{COLORS['RESET']}")
            print(f"  {COLORS['RED']}Reason: {reason}{COLORS['RESET']}")
            print(f"  {COLORS['RED']}This command has been denied.{COLORS['RESET']}")
            self.logger.log(command, "BLOCKED", "denied", reason)
            self.commands_blocked += 1
            return False

    def handle_input(self, user_input):
        """Process user input through the full pipeline."""
        stripped = user_input.strip()

        # Handle special commands
        if stripped.startswith("/"):
            return self._handle_special(stripped)

        print(f"\n{'─' * 65}")

        # Determine if direct command or natural language
        if self.is_direct_command(stripped):
            print(f"  {COLORS['DIM']}Mode: Direct command{COLORS['RESET']}")
            command = stripped
        else:
            print(f"  {COLORS['DIM']}Mode: Natural language translation{COLORS['RESET']}")
            result = self.translate_to_command(stripped)
            command = result.get("command", "")
            explanation = result.get("explanation", "")
            print(f"  {COLORS['CYAN']}Translated:{COLORS['RESET']} {command}")
            print(f"  {COLORS['DIM']}{explanation}{COLORS['RESET']}")
            if not command:
                print(f"  {COLORS['RED']}Could not translate request.{COLORS['RESET']}")
                return True

        # Classify the command
        classification = self.classify_command(command)
        risk = classification.get("risk_level", "UNKNOWN")
        color_map = {"SAFE": "GREEN", "RESTRICTED": "YELLOW", "BLOCKED": "RED"}
        color = COLORS.get(color_map.get(risk, ""), COLORS["RESET"])
        print(f"  Risk: {color}{COLORS['BOLD']}[{risk}]{COLORS['RESET']}")

        # Apply guardrail
        self.apply_guardrail(command, classification)
        print(f"{'─' * 65}")
        return True

    def _handle_special(self, command):
        """Handle special /commands."""
        cmd = command.lower()

        if cmd == "/help":
            print("\n" + "-" * 65)
            print("  /help   Show this help")
            print("  /audit  Show recent audit entries")
            print("  /stats  Show session statistics")
            print("  /exit   Exit the copilot")
            print("-" * 65)

        elif cmd == "/audit":
            print("\n" + "-" * 65)
            print("  Recent Audit Log:")
            print("-" * 65)
            for e in self.logger.entries[-5:]:
                ts = e["timestamp"][:19]
                print(f"  {ts} | {e['classification']:<11} | {e['action_taken']:<10} | {e['command'][:30]}")
            if not self.logger.entries:
                print("  (no entries yet)")
            print("-" * 65)

        elif cmd == "/stats":
            stats = self.logger.get_stats()
            duration = int(time.time() - self.start_time)
            print("\n" + "-" * 65)
            print(f"  Session: {self.logger.session_id} | Duration: {duration}s")
            print(f"  Commands executed: {self.commands_executed}")
            print(f"  Commands blocked:  {self.commands_blocked}")
            print(f"  Total processed:   {stats['total']}")
            print(f"  SAFE: {stats['SAFE']} | RESTRICTED: {stats['RESTRICTED']} | BLOCKED: {stats['BLOCKED']}")
            print("-" * 65)

        elif cmd == "/exit":
            return False

        else:
            print(f"  Unknown command: {command}. Type /help for options.")

        return True

    def run(self):
        """Main interaction loop."""
        self.print_banner()

        while True:
            try:
                user_input = input(f"\n{COLORS['CYAN']}copilot>{COLORS['RESET']} ")
                if not user_input.strip():
                    continue
                if not self.handle_input(user_input):
                    break
            except KeyboardInterrupt:
                print("\n  (Use /exit to quit)")
                continue
            except EOFError:
                break

        # Exit summary
        duration = int(time.time() - self.start_time)
        print(f"\n{'=' * 65}")
        print(f"  Session Summary")
        print(f"{'=' * 65}")
        print(f"  Duration:         {duration} seconds")
        print(f"  Commands run:     {self.commands_executed}")
        print(f"  Commands blocked: {self.commands_blocked}")
        print(f"  Total processed:  {len(self.logger.entries)}")
        print(f"  Audit log:        {self.logger.log_file}")
        print(f"{'=' * 65}")


def main():
    """Entry point for the full DevOps Copilot."""
    print("\n" + "=" * 65)
    print("  TASK 6: Full DevOps Copilot — All Features Combined")
    print("=" * 65)
    print("  Features: NL Interface + Classification + Guardrails + Audit")
    print("  Model: claude-sonnet-4-20250514")
    print("=" * 65)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n  ERROR: ANTHROPIC_API_KEY not set.")
        print("  Run: export ANTHROPIC_API_KEY='your-key-here'\n")
        sys.exit(1)

    copilot = DevOpsCopilot()
    copilot.run()

    # ─────────────────────────────────────────────────────────────────
    # Key Learning
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  Key Learning:")
    print("=" * 65)
    print("  - A production copilot combines multiple AI capabilities")
    print("  - Pipeline: Input -> Translate -> Classify -> Guardrail -> Log")
    print("  - Every action is audited for compliance and trust")
    print("  - Natural language + direct commands serve different users")
    print("  - Session management tracks cumulative safety metrics")
    print("=" * 65)
    print("\n  Congratulations! You've built a complete DevOps AI Copilot.")
    print("  This is the foundation for production-grade AI-assisted ops.\n")


if __name__ == "__main__":
    main()
