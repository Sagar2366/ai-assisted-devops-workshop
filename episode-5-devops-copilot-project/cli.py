"""
Episode 5: Build a DevOps Copilot
AI-Assisted DevOps Workshop

DevOps Copilot CLI -- Interactive mode.
Run investigations from your terminal.

Author: Sagar Utekar

Prerequisites:
    - Python 3.10+
    - anthropic Python SDK (pip install anthropic)
    - ANTHROPIC_API_KEY environment variable set
    - kubectl configured and pointing to your cluster
    - copilot.py and k8s_tools.py in the same directory
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from copilot import run_copilot

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           DevOps Copilot v1.0                                ║
║           Built by Sagar Utekar                              ║
║           CNCF Ambassador | Kubestronaut                     ║
║                                                              ║
║  Commands:                                                   ║
║    diagnose    - Full cluster diagnosis                      ║
║    health      - Quick health check                          ║
║    investigate <topic> - Investigate a specific issue         ║
║    ask <question> - Ask anything about the cluster           ║
║    quit        - Exit                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

QUICK_COMMANDS = {
    "diagnose": "Investigate the entire cluster. Find all unhealthy pods, diagnose each issue, determine root causes, and fix what you can. Provide a prioritized report.",
    "health": "Do a quick health check of the cluster. Report status of nodes, pods, and any warnings. Keep it brief — just the facts.",
}


def main():
    print(BANNER)

    while True:
        try:
            user_input = input("\ncopilot> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # Check for quick commands
        parts = user_input.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd in QUICK_COMMANDS:
            run_copilot(QUICK_COMMANDS[cmd])
        elif cmd == "investigate":
            if len(parts) > 1:
                run_copilot(f"Investigate this specific issue: {parts[1]}")
            else:
                print("Usage: investigate <topic>")
        elif cmd == "ask":
            if len(parts) > 1:
                run_copilot(parts[1])
            else:
                print("Usage: ask <question>")
        else:
            # Treat entire input as a task
            run_copilot(user_input)


if __name__ == "__main__":
    main()
