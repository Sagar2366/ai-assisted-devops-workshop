#!/usr/bin/env python3
"""
AI-Assisted DevOps Workshop | Episode 8 - Claude Code Deep Dive | Sagar Utekar

Demo 2: Setting Up Claude Code Safety Hooks

This script configures Claude Code hooks for safety enforcement:
- PreToolUse hooks: Block dangerous commands before execution
- PostToolUse hooks: Audit logging after actions complete

Hooks are the mechanism for enforcing organizational policies
and maintaining audit trails in Claude Code workflows.
"""

import os
import json
import stat
from pathlib import Path


def print_header():
    print("=" * 65)
    print("  CLAUDE CODE DEEP DIVE - Safety Hooks Configuration")
    print("  AI-Assisted DevOps Workshop | Episode 8")
    print("=" * 65)
    print()


def create_directory_structure(base_path):
    """Create the .claude directory structure for hooks."""
    print("-" * 65)
    print("  Phase 1: Creating Directory Structure")
    print("-" * 65)
    print()

    claude_dir = os.path.join(base_path, ".claude")
    hooks_dir = os.path.join(claude_dir, "hooks")

    os.makedirs(hooks_dir, exist_ok=True)

    print(f"  [CREATED] {claude_dir}/")
    print(f"  [CREATED] {hooks_dir}/")
    print()

    return claude_dir, hooks_dir


def create_pre_command_validator(hooks_dir):
    """Create the pre-command validator hook script."""
    print("-" * 65)
    print("  Phase 2: Creating PreToolUse Hook - Command Validator")
    print("-" * 65)
    print()

    script_path = os.path.join(hooks_dir, "pre-command-validator.sh")

    script_content = '''#!/bin/bash
# Claude Code PreToolUse Hook - Command Validator
# Blocks dangerous commands before they execute
#
# This hook receives JSON on stdin with the tool name and input.
# Exit 0 = allow, Exit 2 = block (with reason on stdout)

set -euo pipefail

# Read the hook input from stdin
INPUT=$(cat)

# Extract the tool name and command
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only check Bash/shell tool invocations
if [[ "$TOOL_NAME" != "Bash" && "$TOOL_NAME" != "bash" ]]; then
    exit 0
fi

# Define blocked patterns for production safety
BLOCKED_PATTERNS=(
    "rm -rf /"
    "rm -rf /*"
    "kubectl delete namespace prod"
    "kubectl delete ns prod"
    "terraform destroy"
    "docker system prune -af"
    "DROP DATABASE"
    "DROP TABLE"
    "truncate table"
    ":(){ :|:& };:"
    "chmod -R 777 /"
    "mkfs"
    "dd if=/dev/zero"
    "shutdown"
    "reboot"
    "init 0"
    "halt"
)

# Check for blocked patterns
for PATTERN in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qi "$PATTERN"; then
        echo "BLOCKED: Command matches dangerous pattern: '$PATTERN'"
        echo "Reason: This command could cause data loss or service disruption."
        echo "If this is intentional, run it manually outside Claude Code."
        exit 2
    fi
done

# Warn about production context commands
PROD_PATTERNS=(
    "kubectl.*--context.*prod"
    "kubectl.*-n.*production"
    "aws.*--profile.*prod"
    "gcloud.*--project.*prod"
)

for PATTERN in "${PROD_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$PATTERN"; then
        echo "BLOCKED: Command targets production environment."
        echo "Production commands require manual execution with explicit approval."
        exit 2
    fi
done

# Allow the command
exit 0
'''

    with open(script_path, "w") as f:
        f.write(script_content)

    # Make executable
    os.chmod(script_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    print(f"  [WRITTEN] {script_path}")
    print()
    print("  Blocked patterns include:")
    print("    - Destructive filesystem operations (rm -rf /)")
    print("    - Production Kubernetes deletions")
    print("    - Terraform destroy without approval")
    print("    - Database DROP/TRUNCATE commands")
    print("    - System-level dangerous commands")
    print("    - Production-targeted cloud CLI commands")
    print()

    return script_path


def create_post_action_logger(hooks_dir):
    """Create the post-action audit logger hook script."""
    print("-" * 65)
    print("  Phase 3: Creating PostToolUse Hook - Audit Logger")
    print("-" * 65)
    print()

    script_path = os.path.join(hooks_dir, "post-action-logger.sh")

    script_content = '''#!/bin/bash
# Claude Code PostToolUse Hook - Audit Logger
# Logs all tool actions for compliance and debugging
#
# This hook receives JSON on stdin with the tool name, input, and output.
# It always exits 0 (logging should never block operations).

set -euo pipefail

# Configuration
LOG_DIR="${HOME}/.claude/audit-logs"
LOG_FILE="${LOG_DIR}/claude-actions-$(date +%Y-%m-%d).log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Read the hook input from stdin
INPUT=$(cat)

# Extract fields
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')
TOOL_INPUT=$(echo "$INPUT" | jq -c '.tool_input // {}')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"

# Create structured log entry
LOG_ENTRY=$(jq -n \
    --arg ts "$TIMESTAMP" \
    --arg session "$SESSION_ID" \
    --arg tool "$TOOL_NAME" \
    --argjson input "$TOOL_INPUT" \
    '{
        timestamp: $ts,
        session_id: $session,
        tool_name: $tool,
        tool_input: $input,
        status: "completed"
    }')

# Append to daily log file
echo "$LOG_ENTRY" >> "$LOG_FILE"

# Log high-risk actions to a separate file for easy review
HIGH_RISK_TOOLS=("Bash" "Write" "Edit")
for RISK_TOOL in "${HIGH_RISK_TOOLS[@]}"; do
    if [[ "$TOOL_NAME" == "$RISK_TOOL" ]]; then
        echo "$LOG_ENTRY" >> "${LOG_DIR}/high-risk-$(date +%Y-%m-%d).log"
        break
    fi
done

# Always allow (exit 0) - logging should never block
exit 0
'''

    with open(script_path, "w") as f:
        f.write(script_content)

    # Make executable
    os.chmod(script_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    print(f"  [WRITTEN] {script_path}")
    print()
    print("  Logging features:")
    print("    - Structured JSON log entries")
    print("    - Daily log rotation by filename")
    print("    - Separate high-risk action log")
    print("    - Session ID tracking for correlation")
    print("    - UTC timestamps for consistency")
    print()

    return script_path


def create_settings_json(claude_dir, hooks_dir):
    """Create the settings.json with hooks configuration."""
    print("-" * 65)
    print("  Phase 4: Writing settings.json with Hooks Configuration")
    print("-" * 65)
    print()

    settings_path = os.path.join(claude_dir, "settings.json")

    pre_validator = os.path.join(hooks_dir, "pre-command-validator.sh")
    post_logger = os.path.join(hooks_dir, "post-action-logger.sh")

    settings = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": pre_validator,
                            "timeout": 5000,
                            "description": "Validates commands against safety policies before execution"
                        }
                    ]
                },
                {
                    "matcher": "Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": pre_validator,
                            "timeout": 5000,
                            "description": "Checks file write operations for safety"
                        }
                    ]
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": post_logger,
                            "timeout": 3000,
                            "description": "Logs all tool actions for audit compliance"
                        }
                    ]
                }
            ]
        }
    }

    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

    print(f"  [WRITTEN] {settings_path}")
    print()
    print("  Hook Configuration Summary:")
    print()
    print("  PreToolUse Hooks (run BEFORE tool execution):")
    print("    - Bash matcher: Validates shell commands against blocklist")
    print("    - Write matcher: Checks file operations for safety")
    print("    - Timeout: 5 seconds (blocks if hook hangs)")
    print()
    print("  PostToolUse Hooks (run AFTER tool execution):")
    print("    - * (wildcard) matcher: Logs ALL tool actions")
    print("    - Timeout: 3 seconds")
    print("    - Non-blocking: logging failures don't affect operations")
    print()

    return settings_path, settings


def display_configuration(settings):
    """Display the complete configuration for review."""
    print("-" * 65)
    print("  Complete Configuration")
    print("-" * 65)
    print()
    print("  settings.json:")
    print()

    formatted = json.dumps(settings, indent=2)
    for line in formatted.split("\n"):
        print(f"    {line}")
    print()


def display_file_tree(base_path):
    """Show the created file structure."""
    print("-" * 65)
    print("  Created File Structure")
    print("-" * 65)
    print()
    print(f"  {base_path}/")
    print("  +-- .claude/")
    print("  |   +-- settings.json          (hooks configuration)")
    print("  |   +-- hooks/")
    print("  |       +-- pre-command-validator.sh  (PreToolUse)")
    print("  |       +-- post-action-logger.sh     (PostToolUse)")
    print()


def main():
    print_header()

    # Create in a demo directory
    base_path = "/tmp/claude-hooks-demo"
    os.makedirs(base_path, exist_ok=True)

    print(f"  Setting up hooks in: {base_path}")
    print()

    # Phase 1: Create directory structure
    claude_dir, hooks_dir = create_directory_structure(base_path)

    # Phase 2: Create pre-command validator
    create_pre_command_validator(hooks_dir)

    # Phase 3: Create post-action logger
    create_post_action_logger(hooks_dir)

    # Phase 4: Create settings.json
    settings_path, settings = create_settings_json(claude_dir, hooks_dir)

    # Display complete configuration
    display_configuration(settings)

    # Display file tree
    display_file_tree(base_path)

    # Hook lifecycle explanation
    print("-" * 65)
    print("  Hook Lifecycle")
    print("-" * 65)
    print()
    print("  1. User asks Claude Code to run a command")
    print("  2. PreToolUse hook fires BEFORE execution:")
    print("     - Hook receives tool name + input as JSON on stdin")
    print("     - Exit 0 = allow, Exit 2 = block with reason")
    print("     - If blocked, Claude sees the rejection reason")
    print("  3. Tool executes (if allowed)")
    print("  4. PostToolUse hook fires AFTER execution:")
    print("     - Hook receives tool name + input + output")
    print("     - Logs the action for audit trail")
    print("     - Always exits 0 (non-blocking)")
    print()

    print("=" * 65)
    print()
    print("  Key Learning:")
    print("  Hooks enforce safety policies at the tool execution layer.")
    print("  Unlike CLAUDE.md (advisory), hooks are ENFORCED - Claude Code")
    print("  cannot bypass a hook that returns exit code 2.")
    print()
    print("  Use PreToolUse to: block dangerous commands, enforce policies")
    print("  Use PostToolUse to: audit logging, notifications, metrics")
    print()
    print("  Next: task3_slash_commands.py - Custom slash commands")
    print()
    print("=" * 65)


if __name__ == "__main__":
    main()
