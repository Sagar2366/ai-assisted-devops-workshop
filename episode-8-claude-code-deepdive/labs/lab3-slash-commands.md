# Lab 3: Custom Slash Commands for SRE

> **Mission:** Create reusable slash commands that encode your team's operational procedures — turning multi-step SRE workflows into single-command invocations.

## Concept: What Are Slash Commands?

Slash commands are **predefined prompts** stored as markdown files in your `.claude/commands/` directory. When you type `/command-name` in Claude Code, it loads the prompt template and executes it.

**Analogy:** Think of slash commands like Kubernetes operators. An operator encodes the operational knowledge of running a specific application. Similarly, a slash command encodes the operational knowledge of performing a specific SRE task — health checks, incident response, rollbacks — so that any team member can execute complex procedures consistently.

## How Slash Commands Work

```
.claude/commands/                    ← Project-level (shared via git)
    health-check.md
    incident-response.md
    rollback.md

~/.claude/commands/                  ← User-level (personal commands)
    my-debug-workflow.md
    standup-summary.md
```

When you type `/health-check` in Claude Code, it reads `.claude/commands/health-check.md` and uses its content as a structured prompt.

## Step 1: Create the Commands Directory

```bash
mkdir -p .claude/commands
```

## Step 2: Health Check Command

```bash
cat > .claude/commands/health-check.md << 'EOF'
# Health Check: $ARGUMENTS

Perform a comprehensive health check of the specified service or environment.

## Steps to Execute

1. **Cluster Status**
   - Run `kubectl get nodes` and flag any NotReady nodes
   - Run `kubectl top nodes` and flag nodes above 80% CPU or memory

2. **Pod Health**
   - Run `kubectl get pods -n $ARGUMENTS` (or all namespaces if not specified)
   - Flag any pods not in Running/Completed state
   - Check for recent restarts: `kubectl get pods --sort-by='.status.containerStatuses[0].restartCount'`

3. **Service Endpoints**
   - Verify services have healthy endpoints: `kubectl get endpoints -n $ARGUMENTS`
   - Flag any services with 0 endpoints

4. **Recent Events**
   - Check for warning events: `kubectl get events --field-selector type=Warning --sort-by=.lastTimestamp`
   - Summarize any patterns in warnings

5. **Resource Quotas**
   - Check resource quota usage: `kubectl describe resourcequota -n $ARGUMENTS`
   - Flag any quotas above 80% utilization

## Output Format

Present results as a table with status indicators:
- HEALTHY: All checks passing
- WARNING: Non-critical issues detected
- CRITICAL: Immediate attention required

End with recommended actions for any non-healthy items.
EOF
```

Usage: `/health-check production` or `/health-check monitoring`

## Step 3: Incident Response Command

```bash
cat > .claude/commands/incident-response.md << 'EOF'
# Incident Response: $ARGUMENTS

You are assisting with an active incident. The reported issue is: $ARGUMENTS

## Immediate Actions (First 5 Minutes)

1. **Assess Impact**
   - Check affected services: `kubectl get pods --field-selector status.phase!=Running -A`
   - Check ingress health: `kubectl get ingress -A`
   - Verify recent deployments: `kubectl rollout history deployment -A | tail -20`

2. **Gather Context**
   - Last 5 minutes of events: `kubectl get events -A --sort-by=.lastTimestamp | tail -30`
   - Check ArgoCD sync status: `argocd app list` (if available)
   - Recent git commits: `git log --oneline -10`

3. **Identify Root Cause**
   - Correlate timeline: When did the issue start?
   - What changed: deployments, config changes, infrastructure?
   - Check external dependencies: DNS, cloud provider status

## Communication Template

Generate an incident communication update:
```
**Incident**: [Title from $ARGUMENTS]
**Status**: Investigating / Identified / Monitoring / Resolved
**Impact**: [Affected users/services]
**Timeline**: [When it started]
**Current Actions**: [What we are doing]
**Next Update**: [Time]
```

## Rollback Decision Tree

If a recent deployment is the cause:
1. Identify the deployment: `kubectl rollout history deployment/<name> -n <ns>`
2. Rollback: `kubectl rollout undo deployment/<name> -n <ns>`
3. Verify: `kubectl rollout status deployment/<name> -n <ns>`

## IMPORTANT
- Do NOT make production changes without confirming with me first
- Prefer --dry-run flags on all mutating commands
- Log all findings for the post-incident review
EOF
```

Usage: `/incident-response API latency spike in checkout service`

## Step 4: Rollback Command

```bash
cat > .claude/commands/rollback.md << 'EOF'
# Rollback: $ARGUMENTS

Perform a safe rollback of the specified service. Service/details: $ARGUMENTS

## Pre-Rollback Checks

1. **Identify Current State**
   - Current revision: `kubectl rollout history deployment/$ARGUMENTS`
   - Current image: `kubectl get deployment $ARGUMENTS -o jsonpath='{.spec.template.spec.containers[0].image}'`
   - Confirm which revision to roll back to

2. **Verify Rollback Target**
   - Show previous revision details
   - Confirm the target revision was previously stable

## Execute Rollback

3. **Perform Rollback (with confirmation)**
   - Show the command: `kubectl rollout undo deployment/$ARGUMENTS --to-revision=<N>`
   - Wait for my explicit approval before executing
   - After approval: execute and monitor

4. **Verify Rollback**
   - Watch rollout: `kubectl rollout status deployment/$ARGUMENTS`
   - Check pod health: `kubectl get pods -l app=$ARGUMENTS`
   - Verify endpoints: `kubectl get endpoints $ARGUMENTS`

5. **Post-Rollback**
   - Confirm service is healthy
   - Note the bad revision for investigation
   - Suggest creating a git revert for the problematic commit

## Safety Rules
- NEVER rollback without showing me the plan first
- ALWAYS verify the target revision was previously healthy
- ALWAYS monitor the rollback until all pods are ready
EOF
```

Usage: `/rollback payment-service -n production`

## Step 5: Cost Analysis Command

```bash
cat > .claude/commands/cost-check.md << 'EOF'
# Cost Analysis: $ARGUMENTS

Analyze resource costs and optimization opportunities for: $ARGUMENTS

## Resource Utilization

1. **Compute Analysis**
   - Current requests vs actual usage: `kubectl top pods -n $ARGUMENTS`
   - Identify over-provisioned pods (usage < 30% of requests)
   - Identify under-provisioned pods (usage > 80% of requests)

2. **Storage Analysis**
   - PVC utilization: `kubectl get pvc -n $ARGUMENTS`
   - Identify unbound or unused PVCs

3. **Right-Sizing Recommendations**
   - For each over-provisioned resource, suggest new requests/limits
   - Calculate estimated savings (assume on-demand pricing)
   - Present as a table: Service | Current | Recommended | Monthly Savings

## Output Format

Present a cost optimization report with:
- Total current estimated cost
- Potential savings by category
- Priority-ordered recommendations (highest savings first)
- Risk assessment for each recommendation
EOF
```

## Step 6: Terraform Plan Review Command

```bash
cat > .claude/commands/plan-review.md << 'EOF'
# Terraform Plan Review: $ARGUMENTS

Review the Terraform plan output for safety and correctness.

## Steps

1. **Generate Plan**
   - Run: `terraform plan -out=review.tfplan $ARGUMENTS`
   - Run: `terraform show -json review.tfplan`

2. **Analyze Changes**
   - Count: resources to add, change, destroy
   - Flag any DESTROY operations (these need extra scrutiny)
   - Flag any changes to stateful resources (RDS, EBS, S3)

3. **Safety Review**
   - Check for unintended cascading deletes
   - Verify no changes to shared infrastructure (VPC, subnets)
   - Confirm no security group rule removals
   - Check for any `force_new` replacements on stateful resources

4. **Summary Format**
   ```
   ## Plan Summary
   - Add: X resources
   - Change: Y resources  
   - Destroy: Z resources

   ## Risk Assessment: LOW/MEDIUM/HIGH/CRITICAL

   ## Flagged Items
   - [item]: [reason for concern]

   ## Recommendation
   - SAFE TO APPLY / NEEDS REVIEW / DO NOT APPLY
   ```

5. **Cleanup**
   - Remove the plan file: `rm review.tfplan`
EOF
```

## Step 7: On-Call Handoff Command

```bash
cat > .claude/commands/oncall-handoff.md << 'EOF'
# On-Call Handoff Summary

Generate an on-call shift handoff document.

## Gather Information

1. **Active Issues**
   - Check for any ongoing incidents or alerts
   - List any services in degraded state
   - Note any pending maintenance windows

2. **Recent Changes (Last 24h)**
   - Recent deployments: `git log --since="24 hours ago" --oneline`
   - ArgoCD sync history (if available)
   - Any infrastructure changes applied

3. **Upcoming Events**
   - Scheduled maintenance windows
   - Planned deployments
   - Known risk periods (traffic spikes, etc.)

4. **Known Issues / Workarounds**
   - Issues that are known but not yet fixed
   - Temporary workarounds in place
   - Escalation contacts for specific systems

## Output Format

```markdown
# On-Call Handoff: [Date]

## Current Status: GREEN/YELLOW/RED

## Active Issues
- [Issue]: [Status] - [Workaround if any]

## Recent Changes
- [Change]: [Impact] - [Rollback plan if needed]

## Watch Items
- [Item]: [Why] - [What to do if it triggers]

## Escalation Contacts
- [System]: [Person] - [Contact method]
```
EOF
```

## Step 8: Test Your Commands

```bash
# Launch Claude Code
claude

# Test health check
> /health-check staging

# Test incident response
> /incident-response High error rate on authentication service

# Test plan review
> /plan-review -var-file=environments/staging.tfvars

# List available commands
> What slash commands are available?
```

## What Success Looks Like

After completing this lab, you should have:

- [x] `.claude/commands/` directory with 5+ operational commands
- [x] Commands that use `$ARGUMENTS` for parameterization
- [x] Multi-step procedures encoded as structured prompts
- [x] Safety reminders embedded in destructive commands
- [x] Communication templates for incident response
- [x] Commands tested and working in Claude Code sessions

## Key Takeaway

Slash commands democratize operational expertise. A junior engineer running `/incident-response` gets the same structured, safe procedure that a senior SRE would follow. This is not about replacing human judgment — it is about ensuring that judgment is applied consistently, with all the right checks and context, every single time.

## Next

Proceed to [Lab 4: MCP Integration](lab4-mcp-integration.md) to connect Claude Code to live infrastructure through Model Context Protocol servers.
