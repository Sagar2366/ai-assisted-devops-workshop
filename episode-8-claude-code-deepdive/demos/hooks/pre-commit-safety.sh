#!/bin/bash
# =================================================================
# Pre-Tool-Use Safety Hook for Claude Code
# =================================================================
# This hook runs BEFORE any Bash command executes in Claude Code.
# It inspects the command and blocks dangerous operations that
# could damage production infrastructure.
#
# Installation:
#   1. Place in .claude/hooks/pre-commit-safety.sh
#   2. chmod +x .claude/hooks/pre-commit-safety.sh
#   3. Configure in .claude/settings.json under hooks.PreToolUse
#
# Input: JSON on stdin with tool_name and tool_input
# Output: JSON with "decision" field (block/allow) or exit 0 to allow
# =================================================================

set -euo pipefail

# -----------------------------------------------------------------
# Read input from Claude Code hook system
# -----------------------------------------------------------------
INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only process Bash tool invocations
if [ "$TOOL_NAME" != "Bash" ] || [ -z "$COMMAND" ]; then
    exit 0
fi

# -----------------------------------------------------------------
# Category 1: ABSOLUTELY BLOCKED — Never allow these
# These commands can cause catastrophic, unrecoverable damage
# -----------------------------------------------------------------
CRITICAL_BLOCKS=(
    "rm -rf /"
    "rm -rf /*"
    "rm -rf ~"
    "mkfs\."
    "dd if=.* of=/dev/"
    ":(){:|:&};:"
    "chmod -R 777 /"
    "curl.*\| ?bash"
    "wget.*\| ?bash"
    "curl.*\| ?sh"
    "wget.*\| ?sh"
)

for pattern in "${CRITICAL_BLOCKS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        cat << BLOCK_JSON
{"decision": "block", "reason": "CRITICAL SAFETY BLOCK: Command matches catastrophically dangerous pattern. This command could destroy the system and is never allowed. Pattern matched: $pattern"}
BLOCK_JSON
        exit 0
    fi
done

# -----------------------------------------------------------------
# Category 2: PRODUCTION BLOCKED — Never allow against production
# These commands are fine in dev but dangerous in production
# -----------------------------------------------------------------
PROD_BLOCKS=(
    "kubectl delete namespace.*prod"
    "kubectl delete --all.*-n.*prod"
    "kubectl delete -n.*prod.*--all"
    "terraform destroy.*prod"
    "terraform apply.*-auto-approve.*prod"
    "helm uninstall.*prod"
    "helm delete.*prod"
    "aws.*delete.*--no-dry-run.*prod"
    "DROP DATABASE.*prod"
    "DROP TABLE.*prod"
    "TRUNCATE.*prod"
)

for pattern in "${PROD_BLOCKS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        cat << BLOCK_JSON
{"decision": "block", "reason": "PRODUCTION SAFETY BLOCK: This command targets production resources and is blocked. Pattern: $pattern. If this is intentional, execute manually outside Claude Code with proper change management approval."}
BLOCK_JSON
        exit 0
    fi
done

# -----------------------------------------------------------------
# Category 3: CONTEXT VERIFICATION — Block if wrong context
# Check that kubectl commands target the expected cluster
# -----------------------------------------------------------------
if echo "$COMMAND" | grep -qE "kubectl.*(apply|delete|scale|patch|edit|replace)"; then
    # Check if we can determine the current context
    if command -v kubectl &>/dev/null; then
        CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "unknown")
        
        # If context contains "prod" and command is mutating, require dry-run
        if echo "$CURRENT_CONTEXT" | grep -qi "prod"; then
            if ! echo "$COMMAND" | grep -q "\-\-dry-run"; then
                cat << BLOCK_JSON
{"decision": "block", "reason": "CONTEXT SAFETY: Your current kubectl context is '$CURRENT_CONTEXT' (production). Mutating commands require --dry-run=client flag first. Switch to a non-production context or add --dry-run=client to verify the command."}
BLOCK_JSON
                exit 0
            fi
        fi
    fi
fi

# -----------------------------------------------------------------
# Category 4: TERRAFORM STATE PROTECTION
# Prevent direct state manipulation without explicit intent
# -----------------------------------------------------------------
TERRAFORM_DANGEROUS=(
    "terraform state rm"
    "terraform state mv"
    "terraform force-unlock"
    "terraform import.*-auto-approve"
    "terraform taint"
)

for pattern in "${TERRAFORM_DANGEROUS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        cat << BLOCK_JSON
{"decision": "block", "reason": "TERRAFORM SAFETY: Direct state manipulation ('$pattern') is blocked. These operations can corrupt state and should be performed manually with proper planning and backup."}
BLOCK_JSON
        exit 0
    fi
done

# -----------------------------------------------------------------
# Category 5: CAUTION — Allow but warn
# These commands need extra attention
# -----------------------------------------------------------------
CAUTION_PATTERNS=(
    "kubectl apply.*prod"
    "terraform apply"
    "helm upgrade.*prod"
    "aws.*create"
    "aws.*modify"
    "aws.*update"
)

for pattern in "${CAUTION_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        cat << CAUTION_JSON
{"decision": "allow", "message": "CAUTION: This command modifies infrastructure. Pattern: $pattern. Proceeding — ensure you have verified the plan/diff."}
CAUTION_JSON
        exit 0
    fi
done

# -----------------------------------------------------------------
# Default: Allow the command
# -----------------------------------------------------------------
exit 0
