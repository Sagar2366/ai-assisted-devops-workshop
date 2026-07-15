#!/usr/bin/env python3
"""
Task 1: CLI Interface — Building the DevOps Copilot Shell
AI-Assisted DevOps Workshop | Episode 7 | Sagar Utekar

Build an interactive CLI that will become our copilot's interface.
No AI yet — just the shell that accepts commands and manages state.

Prerequisites:
  pip install rich  (optional, for colored output)
"""

import sys
import os
from datetime import datetime

# Try to use rich for colored output, fall back to plain text
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# ═══════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════
COPILOT_NAME = "DevOps Copilot"
VERSION = "0.1.0"
PROMPT_SYMBOL = "devops> "


def print_banner():
    """Display the welcome banner."""
    banner_text = f"""
{'=' * 65}
  {COPILOT_NAME} v{VERSION}
  AI-Assisted DevOps Workshop | Episode 7
{'=' * 65}
  Type 'help' for available commands
  Type 'quit' or 'exit' to leave
{'=' * 65}
"""
    if HAS_RICH:
        console.print(Panel(
            f"[bold cyan]{COPILOT_NAME}[/] v{VERSION}\n"
            "AI-Assisted DevOps Workshop | Episode 7\n\n"
            "[dim]Type 'help' for commands | 'quit' to exit[/]",
            title="Welcome",
            border_style="cyan"
        ))
    else:
        print(banner_text)


def print_help():
    """Display available commands."""
    print("\n" + "-" * 65)
    print("  Available Commands:")
    print("-" * 65)
    commands = {
        "help": "Show this help message",
        "history": "Show command history",
        "clear": "Clear the screen",
        "status": "Show copilot status",
        "quit/exit": "Exit the copilot",
    }
    for cmd, desc in commands.items():
        print(f"  {cmd:<15} {desc}")
    print("-" * 65)
    print("  Any other input will be echoed back (AI processing in Task 2+)")
    print("-" * 65 + "\n")


def print_status(history):
    """Display copilot status information."""
    print("\n" + "-" * 65)
    print("  Copilot Status:")
    print("-" * 65)
    print(f"  Name:          {COPILOT_NAME}")
    print(f"  Version:       {VERSION}")
    print(f"  Commands Run:  {len(history)}")
    print(f"  User:          {os.getenv('USER', 'unknown')}")
    print(f"  Session Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  AI Backend:    Not connected (coming in Task 2)")
    print("-" * 65 + "\n")


def print_history(history):
    """Display command history."""
    print("\n" + "-" * 65)
    print("  Command History:")
    print("-" * 65)
    if not history:
        print("  (no commands yet)")
    else:
        for i, cmd in enumerate(history[-10:], 1):
            print(f"  {i:3}. {cmd}")
    print("-" * 65 + "\n")


def process_command(user_input, history):
    """Process a user command. Returns False to exit, True to continue."""
    stripped = user_input.strip()

    if not stripped:
        return True

    # Add to history
    history.append(stripped)

    # Handle built-in commands
    if stripped.lower() in ("quit", "exit"):
        print("\n" + "=" * 65)
        print(f"  Goodbye! Session ended with {len(history)} commands.")
        print("=" * 65 + "\n")
        return False

    elif stripped.lower() == "help":
        print_help()

    elif stripped.lower() == "history":
        print_history(history)

    elif stripped.lower() == "clear":
        os.system("clear" if os.name != "nt" else "cls")
        print_banner()

    elif stripped.lower() == "status":
        print_status(history)

    else:
        # Echo the command back — AI classification comes in Task 2
        if HAS_RICH:
            console.print(f"  [dim]Received:[/] [yellow]{stripped}[/]")
            console.print(f"  [dim]Status:[/]   No AI connected yet — see Task 2")
        else:
            print(f"  Received: {stripped}")
            print(f"  Status:   No AI connected yet — see Task 2")

    return True


def main():
    """Main interactive loop."""
    print("\n" + "=" * 65)
    print("  TASK 1: Building the DevOps Copilot CLI Interface")
    print("=" * 65)
    print("  Goal: Create an interactive shell for our copilot")
    print("  Note: No AI yet — that comes in Task 2!")
    print("=" * 65 + "\n")

    print_banner()

    history = []

    # Main interaction loop
    while True:
        try:
            if HAS_RICH:
                user_input = console.input(f"[bold green]{PROMPT_SYMBOL}[/]")
            else:
                user_input = input(PROMPT_SYMBOL)

            if not process_command(user_input, history):
                break

        except KeyboardInterrupt:
            print("\n\n  (Use 'quit' or 'exit' to leave cleanly)")
            continue

        except EOFError:
            print("\n")
            break

    # ─────────────────────────────────────────────────────────────────
    # Key Learning
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  Key Learning:")
    print("=" * 65)
    print("  - Interactive CLI with input loop is the copilot's foundation")
    print("  - Command history enables context for future AI interactions")
    print("  - Graceful exit handling (quit/exit/Ctrl+C) is essential")
    print("  - Rich library provides colored output with plain-text fallback")
    print("=" * 65)
    print("\n  Next: Task 2 — AI Command Classification")
    print("  We'll connect Claude to classify commands by risk level.\n")


if __name__ == "__main__":
    main()
