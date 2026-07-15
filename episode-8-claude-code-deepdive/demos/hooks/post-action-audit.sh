#!/bin/bash
# =================================================================
# Post-Tool-Use Audit Hook for Claude Code
# =================================================================
# This hook runs AFTER every tool execution in Claude Code.
# It creates a structured audit trail of all actions taken,
# enabling compliance reporting, incident forensics, and
# team usage analytics.
#
# Installation:
#   1. Place in .claude/hooks/post-action-audit.sh
#   2. chmod +x .claude/hooks/post-action-audit.sh
#   3. Configure in .claude/settings.json under hooks.PostToolUse
#
# Output: Appends JSONL to ~/.claude/audit-logs/YYYY-MM-DD.jsonl
# =================================================================

set -euo pipefail

# -----------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------
AUDIT_DIR="${CLAUDE_AUDIT_DIR:-${HOME}/.claude/audit-logs}"
AUDIT_RETENTION_DAYS="${CLAUDE_AUDIT_RETENTION:-90}"
MAX_INPUT_LENGTH=5000  # Truncate very long inputs

# -----------------------------------------------------------------
# Create audit directory if it does not exist
# -----------------------------------------------------------------
mkdir -p "$AUDIT_DIR"

# -----------------------------------------------------------------
# Read the tool execution result from stdin
# -----------------------------------------------------------------
INPUT=$(cat)

# -----------------------------------------------------------------
# Extract fields from the hook payload
# -----------------------------------------------------------------
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')
TOOL_INPUT=$(echo "$INPUT" | jq -c '.tool_input // {}' | head -c "$MAX_INPUT_LENGTH")
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')

# -----------------------------------------------------------------
# Gather environment context
# -----------------------------------------------------------------
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")
USERNAME=$(whoami)
HOSTNAME_SHORT=$(hostname -s 2>/dev/null || echo "unknown")
WORKING_DIR=$(pwd 2>/dev/null || echo "unknown")
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "none")
GIT_REPO=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "none")

# -----------------------------------------------------------------
# Determine risk level based on command content
# -----------------------------------------------------------------
RISK_LEVEL="low"

if [ "$TOOL_NAME" = "Bash" ]; then
    COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')
    
    # High risk: production-affecting commands
    if echo "$COMMAND" | grep -qiE "(prod|production|terraform apply|helm upgrade)"; then
        RISK_LEVEL="high"
    # Medium risk: infrastructure queries
    elif echo "$COMMAND" | grep -qiE "(kubectl|terraform|helm|aws|gcloud|az)"; then
        RISK_LEVEL="medium"
    fi
elif [ "$TOOL_NAME" = "Write" ] || [ "$TOOL_NAME" = "Edit" ]; then
    # Medium risk: file modifications
    RISK_LEVEL="medium"
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')
    
    # High risk: modifying infrastructure files
    if echo "$FILE_PATH" | grep -qiE "(terraform|kubernetes|helm|deploy|prod)"; then
        RISK_LEVEL="high"
    fi
fi

# -----------------------------------------------------------------
# Build the structured audit log entry
# -----------------------------------------------------------------
LOG_FILE="${AUDIT_DIR}/$(date +%Y-%m-%d).jsonl"

AUDIT_ENTRY=$(jq -n \
    --arg timestamp "$TIMESTAMP" \
    --arg session_id "$SESSION_ID" \
    --arg tool_name "$TOOL_NAME" \
    --arg user "$USERNAME" \
    --arg hostname "$HOSTNAME_SHORT" \
    --arg working_dir "$WORKING_DIR" \
    --arg git_repo "$GIT_REPO" \
    --arg git_branch "$GIT_BRANCH" \
    --arg risk_level "$RISK_LEVEL" \
    --argjson tool_input "$TOOL_INPUT" \
    '{
        timestamp: $timestamp,
        session_id: $session_id,
        tool_name: $tool_name,
        tool_input: $tool_input,
        context: {
            user: $user,
            hostname: $hostname,
            working_dir: $working_dir,
            git_repo: $git_repo,
            git_branch: $git_branch
        },
        risk_level: $risk_level
    }')

# -----------------------------------------------------------------
# Write to audit log (atomic append)
# -----------------------------------------------------------------
echo "$AUDIT_ENTRY" >> "$LOG_FILE"

# -----------------------------------------------------------------
# Rotate old audit logs (cleanup logs older than retention period)
# Run cleanup only 1% of the time to avoid performance impact
# -----------------------------------------------------------------
if [ $((RANDOM % 100)) -eq 0 ]; then
    find "$AUDIT_DIR" -name "*.jsonl" -mtime +"$AUDIT_RETENTION_DAYS" -delete 2>/dev/null || true
fi

# -----------------------------------------------------------------
# Optional: Send high-risk actions to external systems
# -----------------------------------------------------------------
if [ "$RISK_LEVEL" = "high" ]; then
    # Send to Slack webhook if configured
    if [ -n "${CLAUDE_SLACK_WEBHOOK:-}" ]; then
        SLACK_MSG=$(jq -n \
            --arg text ":warning: High-risk action by $USERNAME: [$TOOL_NAME] in $GIT_REPO ($GIT_BRANCH)" \
            '{text: $text}')
        curl -s -X POST "$CLAUDE_SLACK_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "$SLACK_MSG" > /dev/null 2>&1 || true
    fi
    
    # Write to syslog if available
    if command -v logger &>/dev/null; then
        logger -t "claude-code-audit" -p "user.warning" \
            "HIGH-RISK: user=$USERNAME tool=$TOOL_NAME repo=$GIT_REPO branch=$GIT_BRANCH" 2>/dev/null || true
    fi
fi

# -----------------------------------------------------------------
# Post-hooks must always exit 0 (never block after execution)
# -----------------------------------------------------------------
exit 0
