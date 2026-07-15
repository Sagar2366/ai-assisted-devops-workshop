# Lab 2: Pre/Post Hooks for Safety and Audit

> **Mission:** Configure Claude Code hooks that prevent dangerous infrastructure operations and maintain a complete audit trail of all AI-assisted actions.

## Concept: What Are Hooks?

Hooks are **automated gatekeepers** that run before or after Claude Code takes an action. They intercept tool calls (Bash commands, file edits, MCP operations) and can block, modify, or log them.

**Analogy:** Think of hooks like admission controllers in Kubernetes. Just as a ValidatingWebhook rejects pods that violate policies, a pre-hook rejects commands that violate your safety rules. And just as audit logs track every API call to your cluster, post-hooks record every action Claude Code takes.

## Hook Types

| Hook Type | When It Runs | Use Case |
|-----------|-------------|----------|
| `PreToolUse` | Before any tool executes | Block dangerous commands, require confirmation |
| `PostToolUse` | After a tool completes | Log actions, send notifications, validate output |
| `Notification` | On status changes | Alert on errors, track session activity |
| `Stop` | When Claude stops | Generate summaries, cleanup temporary resources |

## Step 1: Understanding Hook Configuration

Hooks are configured in `settings.json` (user or project level):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/your/hook-script.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/your/audit-script.sh"
          }
        ]
      }
    ]
  }
}
```

## Step 2: Create a Safety Pre-Hook

This hook blocks dangerous commands before they execute:

```bash
#!/bin/bash
# File: .claude/hooks/pre-command-safety.sh
# Blocks dangerous infrastructure commands

set -euo pipefail

# The hook receives tool input via stdin as JSON
INPUT=$(cat)

# Extract the command being executed
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only check Bash commands
if [ "$TOOL_NAME" != "Bash" ]; then
    exit 0
fi

# Define blocked patterns for production safety
BLOCKED_PATTERNS=(
    "kubectl delete namespace"
    "kubectl delete -n prod"
    "kubectl delete --all"
    "terraform destroy"
    "terraform apply.*-auto-approve.*prod"
    "rm -rf /"
    "rm -rf /*"
    "helm uninstall.*prod"
    "aws.*--no-dry-run.*delete"
    "DROP DATABASE"
    "DROP TABLE"
)

# Check command against blocked patterns
for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        # Output JSON to block the action
        echo '{"decision": "block", "reason": "BLOCKED: Command matches dangerous pattern: '"$pattern"'. This action requires manual execution with explicit approval."}'
        exit 0
    fi
done

# Define commands requiring extra caution (warning but allow)
CAUTION_PATTERNS=(
    "kubectl apply.*prod"
    "terraform apply"
    "helm upgrade.*prod"
    "aws.*modify"
)

for pattern in "${CAUTION_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        echo '{"decision": "allow", "message": "CAUTION: This command affects production. Proceeding with care."}'
        exit 0
    fi
done

# Allow all other commands
exit 0
```

Make it executable:

```bash
chmod +x .claude/hooks/pre-command-safety.sh
```

## Step 3: Create an Audit Post-Hook

This hook logs every action Claude Code takes:

```bash
#!/bin/bash
# File: .claude/hooks/post-action-audit.sh
# Logs all Claude Code actions for audit trail

set -euo pipefail

# Read the tool result from stdin
INPUT=$(cat)

# Extract relevant fields
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')
TOOL_INPUT=$(echo "$INPUT" | jq -c '.tool_input // {}')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')

# Create audit log directory
AUDIT_DIR="${HOME}/.claude/audit-logs"
mkdir -p "$AUDIT_DIR"

# Log file per day
LOG_FILE="${AUDIT_DIR}/$(date +%Y-%m-%d).jsonl"

# Create structured audit entry
AUDIT_ENTRY=$(jq -n \
    --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg tool "$TOOL_NAME" \
    --arg session "$SESSION_ID" \
    --arg user "$(whoami)" \
    --arg directory "$(pwd)" \
    --argjson input "$TOOL_INPUT" \
    '{
        timestamp: $timestamp,
        tool: $tool,
        session: $session,
        user: $user,
        directory: $directory,
        input: $input
    }')

# Append to audit log
echo "$AUDIT_ENTRY" >> "$LOG_FILE"

# Exit successfully (post-hooks should not block)
exit 0
```

## Step 4: Configure Hooks in Settings

Add hooks to your project settings:

```bash
mkdir -p .claude

cat > .claude/settings.json << 'EOF'
{
  "permissions": {
    "allow": [
      "Bash(kubectl get *)",
      "Bash(terraform plan *)",
      "Bash(terraform fmt *)",
      "Bash(terraform validate *)",
      "Bash(helm list *)",
      "Bash(git *)"
    ],
    "deny": [
      "Bash(kubectl delete namespace *)",
      "Bash(terraform destroy *)",
      "Bash(rm -rf /)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/pre-command-safety.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/post-action-audit.sh"
          }
        ]
      }
    ]
  }
}
EOF
```

## Step 5: Create a Notification Hook for Slack

```bash
#!/bin/bash
# File: .claude/hooks/notify-slack.sh
# Sends notifications for important actions

set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Only notify for infrastructure-impacting commands
NOTIFY_PATTERNS=(
    "terraform apply"
    "kubectl apply.*prod"
    "helm upgrade"
    "aws.*create"
    "aws.*delete"
)

SHOULD_NOTIFY=false
for pattern in "${NOTIFY_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        SHOULD_NOTIFY=true
        break
    fi
done

if [ "$SHOULD_NOTIFY" = true ]; then
    # Send to Slack webhook (set SLACK_WEBHOOK_URL in environment)
    if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
        PAYLOAD=$(jq -n \
            --arg text ":robot_face: Claude Code executed: \`$COMMAND\` by $(whoami) in $(basename $(pwd))" \
            '{text: $text}')
        
        curl -s -X POST "$SLACK_WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d "$PAYLOAD" > /dev/null 2>&1 || true
    fi
fi

exit 0
```

## Step 6: Test Your Hooks

```bash
# Start Claude Code
claude

# Test blocked command
> Run kubectl delete namespace production
# Expected: Hook blocks with safety message

# Test allowed command
> Run kubectl get pods -n staging
# Expected: Command executes normally

# Test audit logging
> Run terraform plan -out=plan.tfplan
# Then check the audit log:
# cat ~/.claude/audit-logs/$(date +%Y-%m-%d).jsonl | jq .

# Verify audit entries exist
> Run cat ~/.claude/audit-logs/$(date +%Y-%m-%d).jsonl | jq .
```

## Step 7: Advanced Hook — Environment Verification

```bash
#!/bin/bash
# File: .claude/hooks/verify-environment.sh
# Ensures commands target the correct environment

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Check if kubectl context matches expected environment
if echo "$COMMAND" | grep -qE "kubectl.*(apply|delete|scale|patch)"; then
    CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "unknown")
    
    # Block production commands if context looks like production
    if echo "$CURRENT_CONTEXT" | grep -qi "prod"; then
        if ! echo "$COMMAND" | grep -q "\-\-dry-run"; then
            echo '{"decision": "block", "reason": "BLOCKED: Current kubectl context is production ('"$CURRENT_CONTEXT"'). Add --dry-run=client to test first, or switch to a non-prod context."}'
            exit 0
        fi
    fi
fi

exit 0
```

## What Success Looks Like

After completing this lab, you should have:

- [x] A pre-hook that blocks dangerous infrastructure commands
- [x] A post-hook that logs all actions to a structured audit trail
- [x] Hooks configured in `.claude/settings.json`
- [x] Tested that blocked commands are rejected with clear messages
- [x] Tested that allowed commands proceed normally
- [x] Audit logs accumulating in `~/.claude/audit-logs/`

## Viewing Your Audit Trail

```bash
# View today's actions
cat ~/.claude/audit-logs/$(date +%Y-%m-%d).jsonl | jq .

# Count actions by tool type
cat ~/.claude/audit-logs/$(date +%Y-%m-%d).jsonl | jq -r '.tool' | sort | uniq -c | sort -rn

# Find all production-related actions
cat ~/.claude/audit-logs/*.jsonl | jq 'select(.input.command // "" | test("prod"))'
```

## Key Takeaway

Hooks transform Claude Code from "trust but verify" to "verify then trust." In DevOps, where a single command can take down production, this automated safety net is not optional — it is essential. The combination of pre-hooks (prevention) and post-hooks (audit) gives you both real-time protection and historical accountability.

## Next

Proceed to [Lab 3: Custom Slash Commands for SRE](lab3-slash-commands.md) to build reusable commands for common operational tasks.
