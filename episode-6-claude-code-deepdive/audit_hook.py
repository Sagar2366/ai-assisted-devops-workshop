"""
Episode 6: Claude Code Deep Dive for DevOps
AI-Assisted DevOps Workshop

Post-tool hook: Log every action Claude Code takes.

Author: Sagar Utekar

Prerequisites:
    - Python 3.10+
    - Claude Code installed (npm install -g @anthropic-ai/claude-code)
    - hooks_config.json copied to .claude/settings.json with correct paths

Usage:
    This script is invoked automatically by Claude Code via the PostToolUse hook.
    It receives the tool name and tool input as CLI arguments and appends a
    JSON log entry to /tmp/claude-code-audit.log.
"""
import sys
import json
from datetime import datetime

LOG_FILE = "/tmp/claude-code-audit.log"


def log_action(tool_name: str, tool_input: str):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "input": tool_input[:500]
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    log_action(
        sys.argv[1] if len(sys.argv) > 1 else "unknown",
        sys.argv[2] if len(sys.argv) > 2 else ""
    )
