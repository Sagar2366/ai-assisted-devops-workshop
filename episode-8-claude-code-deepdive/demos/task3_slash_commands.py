#!/usr/bin/env python3
"""
AI-Assisted DevOps Workshop | Episode 8 - Claude Code Deep Dive | Sagar Utekar

Demo 3: Creating Custom Slash Commands

This script creates custom slash commands for Claude Code that automate
common DevOps workflows: incident response, deployment, rollback, and
health checks. Each command uses $ARGUMENTS for parameterization.

Slash commands are markdown files in .claude/commands/ that provide
reusable prompt templates invoked via /project:<command-name>.
"""

import os
from pathlib import Path


def print_header():
    print("=" * 65)
    print("  CLAUDE CODE DEEP DIVE - Custom Slash Commands")
    print("  AI-Assisted DevOps Workshop | Episode 8")
    print("=" * 65)
    print()


def create_commands_directory(base_path):
    """Create the .claude/commands/ directory."""
    print("-" * 65)
    print("  Phase 1: Creating Commands Directory")
    print("-" * 65)
    print()

    commands_dir = os.path.join(base_path, ".claude", "commands")
    os.makedirs(commands_dir, exist_ok=True)

    print(f"  [CREATED] {commands_dir}/")
    print()
    print("  Slash commands are stored as .md files in .claude/commands/")
    print("  They are invoked as: /project:<filename-without-extension>")
    print("  The special token $ARGUMENTS captures user input after the command")
    print()

    return commands_dir


def create_incident_command(commands_dir):
    """Create the incident response slash command."""
    print("-" * 65)
    print("  Phase 2: Creating /project:incident Command")
    print("-" * 65)
    print()

    content = """# Incident Response Runbook

You are an SRE incident commander. A production incident has been reported.

## Incident Details
**Service/Issue**: $ARGUMENTS

## Response Steps

Execute these steps in order, reporting findings at each stage:

### 1. Initial Assessment
- Check the service health endpoints
- Review recent deployments (last 2 hours)
- Check for related alerts in monitoring

```bash
# Check pod status for the affected service
kubectl get pods -n production -l app=$ARGUMENTS --sort-by='.status.startTime'

# Check recent events
kubectl get events -n production --sort-by='.lastTimestamp' | head -20

# Check deployment history
kubectl rollout history deployment/$ARGUMENTS -n production
```

### 2. Impact Assessment
- Determine blast radius (which users/services affected)
- Check error rates and latency metrics
- Identify if this is a partial or full outage

### 3. Mitigation Options
Based on findings, recommend ONE of:
- **Rollback**: If caused by recent deployment
- **Scale**: If caused by traffic spike
- **Restart**: If caused by resource exhaustion
- **Escalate**: If root cause is unclear

### 4. Communication
Draft a status update with:
- What is happening
- Who is affected
- What we are doing about it
- Expected resolution time

## Rules
- Do NOT run destructive commands
- Do NOT modify production state without explicit approval
- ALWAYS use --dry-run for any modification commands
- Report findings clearly and concisely
"""

    filepath = os.path.join(commands_dir, "incident.md")
    with open(filepath, "w") as f:
        f.write(content)

    print(f"  [WRITTEN] {filepath}")
    print()
    print("  Usage: /project:incident payment-service")
    print("  Usage: /project:incident high-latency-in-api-gateway")
    print()

    return filepath


def create_deploy_command(commands_dir):
    """Create the deployment checklist slash command."""
    print("-" * 65)
    print("  Phase 3: Creating /project:deploy Command")
    print("-" * 65)
    print()

    content = """# Deployment Checklist

You are a deployment automation assistant. Execute a safe deployment for the specified service.

## Deployment Target
**Service**: $ARGUMENTS

## Pre-Deployment Checks

Run ALL checks before proceeding. Stop if any check fails.

### 1. Code Readiness
```bash
# Verify we're on the correct branch
git branch --show-current

# Check for uncommitted changes
git status

# Verify all tests pass
npm test 2>&1 | tail -20
```

### 2. Environment Validation
```bash
# Verify kubectl context (must NOT be production for initial checks)
kubectl config current-context

# Check current deployment status
kubectl get deployment $ARGUMENTS -n staging -o wide

# Verify image exists in registry
docker manifest inspect registry.example.com/$ARGUMENTS:$(git rev-parse --short HEAD) 2>&1
```

### 3. Deployment Execution (Staging First)
```bash
# Deploy to staging
kubectl set image deployment/$ARGUMENTS \
  $ARGUMENTS=registry.example.com/$ARGUMENTS:$(git rev-parse --short HEAD) \
  -n staging

# Wait for rollout
kubectl rollout status deployment/$ARGUMENTS -n staging --timeout=300s

# Run smoke tests against staging
curl -sf https://staging.example.com/health | jq .
```

### 4. Production Deployment
**IMPORTANT**: Only proceed after staging validation passes.

```bash
# Show the production deployment plan (dry-run)
kubectl set image deployment/$ARGUMENTS \
  $ARGUMENTS=registry.example.com/$ARGUMENTS:$(git rev-parse --short HEAD) \
  -n production --dry-run=client -o yaml
```

Present the dry-run output and WAIT for explicit user approval before applying.

### 5. Post-Deployment Verification
```bash
# Monitor rollout
kubectl rollout status deployment/$ARGUMENTS -n production --timeout=600s

# Check pod health
kubectl get pods -n production -l app=$ARGUMENTS

# Verify health endpoint
curl -sf https://api.example.com/health | jq .
```

## Rules
- NEVER skip staging deployment
- ALWAYS use --dry-run before production changes
- ALWAYS wait for explicit approval before production deployment
- If any step fails, STOP and report the failure
"""

    filepath = os.path.join(commands_dir, "deploy.md")
    with open(filepath, "w") as f:
        f.write(content)

    print(f"  [WRITTEN] {filepath}")
    print()
    print("  Usage: /project:deploy user-service")
    print("  Usage: /project:deploy api-gateway")
    print()

    return filepath


def create_rollback_command(commands_dir):
    """Create the rollback procedure slash command."""
    print("-" * 65)
    print("  Phase 4: Creating /project:rollback Command")
    print("-" * 65)
    print()

    content = """# Rollback Procedure

You are executing an emergency rollback. Speed is critical but safety cannot be compromised.

## Rollback Target
**Service**: $ARGUMENTS

## Rollback Steps

### 1. Current State Assessment
```bash
# Get current deployment info
kubectl get deployment $ARGUMENTS -n production -o jsonpath='{.spec.template.spec.containers[0].image}'

# Check rollout history
kubectl rollout history deployment/$ARGUMENTS -n production

# Get current replica status
kubectl get pods -n production -l app=$ARGUMENTS -o wide
```

### 2. Identify Rollback Target
```bash
# Show last 5 revisions with change cause
kubectl rollout history deployment/$ARGUMENTS -n production --revision=0 | tail -10
```

Present the revision history and ask which revision to rollback to.
Default: previous revision (rollback by 1).

### 3. Execute Rollback
```bash
# Perform the rollback (dry-run first)
kubectl rollout undo deployment/$ARGUMENTS -n production --dry-run=client

# Execute actual rollback after confirmation
kubectl rollout undo deployment/$ARGUMENTS -n production

# Monitor rollback progress
kubectl rollout status deployment/$ARGUMENTS -n production --timeout=300s
```

### 4. Verify Rollback Success
```bash
# Confirm new (old) image is running
kubectl get deployment $ARGUMENTS -n production -o jsonpath='{.spec.template.spec.containers[0].image}'

# Check all pods are healthy
kubectl get pods -n production -l app=$ARGUMENTS

# Verify health endpoint
curl -sf https://api.example.com/$ARGUMENTS/health | jq .

# Check error rates (last 5 minutes)
echo "Monitor error rates in your observability platform"
```

### 5. Post-Rollback Actions
- Document what was rolled back and why
- Create an incident ticket if not already exists
- Notify the team in #deployments channel
- Schedule a post-mortem if service was degraded > 5 minutes

## Rules
- Rollback FIRST, investigate LATER
- ALWAYS do dry-run before actual rollback
- If rollback fails, escalate immediately
- Document the timeline of events
"""

    filepath = os.path.join(commands_dir, "rollback.md")
    with open(filepath, "w") as f:
        f.write(content)

    print(f"  [WRITTEN] {filepath}")
    print()
    print("  Usage: /project:rollback payment-service")
    print("  Usage: /project:rollback auth-service")
    print()

    return filepath


def create_healthcheck_command(commands_dir):
    """Create the system health check slash command."""
    print("-" * 65)
    print("  Phase 5: Creating /project:healthcheck Command")
    print("-" * 65)
    print()

    content = """# System Health Check

You are performing a comprehensive health check of the system.

## Target
**Scope**: $ARGUMENTS

## Health Check Procedure

### 1. Cluster-Level Health
```bash
# Node status
kubectl get nodes -o wide

# Cluster resource usage
kubectl top nodes

# Check for any nodes in NotReady state
kubectl get nodes | grep -v " Ready"

# Check system pods
kubectl get pods -n kube-system --field-selector=status.phase!=Running
```

### 2. Application Health
```bash
# Check all deployments in the target namespace
kubectl get deployments -n $ARGUMENTS -o wide

# Check for pods not in Running state
kubectl get pods -n $ARGUMENTS --field-selector=status.phase!=Running

# Check pod resource usage
kubectl top pods -n $ARGUMENTS --sort-by=memory | head -20

# Check for restart loops (pods with high restart count)
kubectl get pods -n $ARGUMENTS -o jsonpath='{range .items[*]}{.metadata.name}{"\\t"}{.status.containerStatuses[0].restartCount}{"\\n"}{end}' | sort -t$'\\t' -k2 -rn | head -10
```

### 3. Service Connectivity
```bash
# Check all services and endpoints
kubectl get svc -n $ARGUMENTS
kubectl get endpoints -n $ARGUMENTS

# Verify ingress configuration
kubectl get ingress -n $ARGUMENTS -o wide
```

### 4. Storage Health
```bash
# Check PVC status
kubectl get pvc -n $ARGUMENTS

# Check for any pending PVCs
kubectl get pvc -n $ARGUMENTS --field-selector=status.phase!=Bound
```

### 5. Recent Events (Last 30 minutes)
```bash
# Check for warnings and errors
kubectl get events -n $ARGUMENTS --sort-by='.lastTimestamp' --field-selector=type=Warning | tail -20
```

## Health Report Format

Summarize findings in this format:

| Component | Status | Details |
|-----------|--------|---------|
| Nodes | OK/WARN/CRIT | ... |
| Pods | OK/WARN/CRIT | ... |
| Services | OK/WARN/CRIT | ... |
| Storage | OK/WARN/CRIT | ... |
| Events | OK/WARN/CRIT | ... |

**Overall Status**: [HEALTHY / DEGRADED / CRITICAL]

If any component is WARN or CRIT, provide specific remediation steps.

## Rules
- This is a READ-ONLY operation - do NOT modify any resources
- Report ALL findings, even minor warnings
- Flag any resource approaching limits (>80% utilization)
- Note any pods with restart count > 5
"""

    filepath = os.path.join(commands_dir, "healthcheck.md")
    with open(filepath, "w") as f:
        f.write(content)

    print(f"  [WRITTEN] {filepath}")
    print()
    print("  Usage: /project:healthcheck production")
    print("  Usage: /project:healthcheck staging")
    print()

    return filepath


def display_summary(commands_dir):
    """Display summary of all created commands."""
    print("-" * 65)
    print("  Commands Summary")
    print("-" * 65)
    print()
    print("  Created slash commands:")
    print()
    print("  +----------------------------------------------------------+")
    print("  | Command              | Purpose                           |")
    print("  +----------------------------------------------------------+")
    print("  | /project:incident    | Incident response runbook         |")
    print("  | /project:deploy      | Safe deployment checklist         |")
    print("  | /project:rollback    | Emergency rollback procedure      |")
    print("  | /project:healthcheck | System health assessment          |")
    print("  +----------------------------------------------------------+")
    print()
    print("  File structure:")
    print()
    print("  .claude/")
    print("  +-- commands/")
    print("      +-- incident.md       ($ARGUMENTS = service/issue)")
    print("      +-- deploy.md         ($ARGUMENTS = service name)")
    print("      +-- rollback.md       ($ARGUMENTS = service name)")
    print("      +-- healthcheck.md    ($ARGUMENTS = namespace/scope)")
    print()
    print("  How $ARGUMENTS works:")
    print("  When you type: /project:incident payment-service timeout")
    print("  $ARGUMENTS becomes: 'payment-service timeout'")
    print("  Claude uses this to fill in the context of the command template")
    print()


def main():
    print_header()

    # Create in a demo directory
    base_path = "/tmp/claude-commands-demo"
    os.makedirs(base_path, exist_ok=True)

    print(f"  Setting up slash commands in: {base_path}")
    print()

    # Phase 1: Create directory
    commands_dir = create_commands_directory(base_path)

    # Phase 2-5: Create commands
    create_incident_command(commands_dir)
    create_deploy_command(commands_dir)
    create_rollback_command(commands_dir)
    create_healthcheck_command(commands_dir)

    # Summary
    display_summary(commands_dir)

    print("=" * 65)
    print()
    print("  Key Learning:")
    print("  Slash commands turn complex runbooks into reusable prompts.")
    print("  They encode your team's operational procedures so that")
    print("  Claude Code follows your established workflows consistently.")
    print()
    print("  Benefits for DevOps teams:")
    print("  - Standardized incident response across team members")
    print("  - Deployment safety built into the workflow")
    print("  - On-call engineers get guided procedures via /project:*")
    print("  - $ARGUMENTS makes commands flexible and reusable")
    print()
    print("  Next: task4_mcp_config.py - Configuring MCP servers")
    print()
    print("=" * 65)


if __name__ == "__main__":
    main()
