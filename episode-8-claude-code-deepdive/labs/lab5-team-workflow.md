# Lab 5: Team Workflow Patterns

> **Mission:** Set up Claude Code for team collaboration on infrastructure repositories — sharing consistent configurations, enforcing safety policies, and integrating AI-assisted code review into your DevOps workflow.

## Concept: Shared AI Configuration

When one engineer configures Claude Code perfectly, that knowledge benefits only them. When you encode it into version-controlled project files, the entire team operates at the same level of safety and productivity.

**Analogy:** Think of shared Claude Code configuration like a team's `.editorconfig` or `.eslintrc` — but for AI behavior. Just as those files ensure every engineer's editor formats code the same way, shared Claude Code settings ensure every engineer's AI assistant follows the same operational rules, respects the same safety boundaries, and speaks the same domain language.

## Project Settings vs User Settings

| Setting Level | Location | Scope | Version Controlled |
|---------------|----------|-------|-------------------|
| **Project** | `.claude/settings.json` | Everyone on the repo | Yes (shared via git) |
| **User** | `~/.claude/settings.json` | Only you, all projects | No (personal) |

### What Goes Where

**Project settings** (shared with team):
- Permission allowlists for safe operations
- Permission denylists for dangerous operations
- Hook configurations for safety and audit
- MCP server configurations

**User settings** (personal preferences):
- Personal API keys and tokens
- Custom MCP servers for personal tools
- Theme and display preferences
- Personal permission overrides

---

## Step 1: Shared CLAUDE.md Patterns

### Pattern 1: Team Conventions Header

Every team CLAUDE.md should start with identity and boundaries:

```markdown
# Project: Payment Platform Infrastructure

## Team
- Owning team: Platform SRE
- On-call rotation: PagerDuty "platform-sre-primary"
- Slack channel: #platform-sre
- Escalation: @sre-leads

## Golden Rules (NEVER violate)
- NEVER apply changes to production without a plan file
- NEVER delete stateful resources (PVCs, databases) without backup verification
- NEVER commit secrets — use External Secrets Operator
- NEVER bypass the CI pipeline for production deployments
- ALWAYS use --dry-run=client before kubectl apply in prod
```

### Pattern 2: Environment-Aware Instructions

```markdown
## Environment Detection
When working in this repository, detect the target environment from:
1. Current kubectl context: `kubectl config current-context`
2. Terraform workspace: `terraform workspace show`
3. Branch name: `git branch --show-current`

## Environment-Specific Rules
### If targeting PRODUCTION:
- Require explicit confirmation before any write operation
- Always generate a rollback plan before changes
- Tag all operations with incident ticket if during an incident

### If targeting STAGING:
- Apply changes freely but validate with smoke tests
- Clean up test resources after verification

### If targeting DEV:
- Full autonomy for experimentation
- No approval needed for any operation
```

### Pattern 3: Architecture as Context

```markdown
## Service Map
| Service | Language | DB | Queue | Owner |
|---------|----------|-----|-------|-------|
| api-gateway | Go 1.22 | - | - | platform |
| user-service | Python 3.12 | PostgreSQL | RabbitMQ | identity |
| payment-engine | Java 21 | PostgreSQL | Kafka | payments |
| notification | Node 20 | MongoDB | SQS | engagement |

## Dependency Graph
api-gateway -> user-service -> PostgreSQL (RDS)
api-gateway -> payment-engine -> Kafka -> notification
```

---

## Step 2: Project Settings Configuration

Create `.claude/settings.json` for the team:

```json
{
  "permissions": {
    "allow": [
      "Bash(kubectl get *)",
      "Bash(kubectl describe *)",
      "Bash(kubectl logs *)",
      "Bash(terraform plan *)",
      "Bash(terraform fmt *)",
      "Bash(terraform validate *)",
      "Bash(helm list *)",
      "Bash(helm status *)",
      "Bash(git *)",
      "Bash(docker ps *)",
      "Bash(docker images *)",
      "Bash(cat *)",
      "Bash(ls *)",
      "Bash(grep *)",
      "Bash(find *)"
    ],
    "deny": [
      "Bash(kubectl delete namespace *)",
      "Bash(kubectl delete pv *)",
      "Bash(terraform destroy *)",
      "Bash(rm -rf /)",
      "Bash(rm -rf /*)",
      "Bash(docker system prune --all *)"
    ]
  }
}
```

### Permission Pattern Design

The key insight is to **allow read operations broadly** and **deny destructive operations specifically**:

```
Allow Pattern:
  Bash(kubectl get *)       <- Wildcard covers all read variations
  Bash(terraform plan *)    <- Planning is always safe

Deny Pattern:
  Bash(kubectl delete namespace *)  <- Specific destructive action
  Bash(terraform destroy *)         <- Specific destructive action
```

Commands not matching either list will prompt for confirmation — this is the correct default for state-changing operations that are not inherently dangerous.

---

## Step 3: Code Review Workflows

### Using Claude Code for Infrastructure PR Review

Create `.claude/commands/review-infra.md`:

```markdown
You are reviewing an infrastructure change. Analyze the current git diff and evaluate:

## Safety Analysis
1. **Blast Radius:** What is affected? How many services/users impacted?
2. **Reversibility:** Can this be rolled back? How quickly?
3. **Dependencies:** Does this change break any downstream services?

## Terraform-Specific Checks (if applicable)
- Are there resources being destroyed? List them.
- Are there changes to stateful resources (RDS, ElastiCache, EBS)?
- Is the `prevent_destroy` lifecycle rule set for critical resources?
- Are all variables documented with descriptions?
- Is the blast radius documented in the PR description?

## Kubernetes-Specific Checks (if applicable)
- Do all pods have resource requests AND limits?
- Are PodDisruptionBudgets configured for production services?
- Are health checks (readiness + liveness) properly configured?
- Are image tags pinned to digests (not mutable tags like `latest`)?

## Security Checks
- Are there any hardcoded secrets, tokens, or credentials?
- Are RBAC permissions following least-privilege principle?
- Are NetworkPolicies maintained for affected namespaces?

## Output Format
Rate this change:
- Risk: LOW / MEDIUM / HIGH / CRITICAL
- Confidence: How confident are you in this assessment?
- Recommendation: APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION
- Action items: Specific things to fix or verify before merging
```

### Automated Review on PR Creation

Add to your CI workflow (`.github/workflows/ai-review.yml`):

```yaml
name: AI Infrastructure Review
on:
  pull_request:
    paths:
      - 'terraform/**'
      - 'kubernetes/**'
      - 'helm/**'

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: AI Review
        run: |
          claude --print "Review this PR's infrastructure changes for safety. \
            Focus on blast radius, reversibility, and security. \
            Output as a structured review comment."
```

---

## Step 4: Onboarding New Team Members

### The "Day One" CLAUDE.md Pattern

Create a section specifically for new engineers:

```markdown
## For New Team Members

### Getting Started
1. Clone this repo and run `./scripts/setup-dev.sh`
2. Install Claude Code: `npm install -g @anthropic-ai/claude-code`
3. Set your API key: `export ANTHROPIC_API_KEY="your-key"`
4. Run `claude` in this directory — it will load all project context automatically

### Common First Tasks
- `/healthcheck` — Run a full cluster health assessment
- `/incident <description>` — Start an incident response workflow
- Ask: "What services does the api-gateway depend on?"
- Ask: "How do I deploy to staging?"
- Ask: "What was the last incident and what caused it?"

### What Claude Code Already Knows About This Repo
- All architecture decisions (from this CLAUDE.md)
- All safety rules (from settings.json permissions)
- All operational procedures (from slash commands)
- Current service versions and dependencies
```

---

## Step 5: Multi-Environment Permission Strategy

### Environment-Specific Settings Files

```
.claude/
├── settings.json              <- Base (read-only permissions)
├── settings.local.json        <- Personal overrides (gitignored)
└── commands/
    ├── incident.md
    ├── deploy.md
    └── rollback.md
```

Add to `.gitignore`:

```
.claude/settings.local.json
```

### settings.local.json for Senior SREs

Senior engineers who need broader permissions can add a local override:

```json
{
  "permissions": {
    "allow": [
      "Bash(kubectl apply *)",
      "Bash(terraform apply *)",
      "Bash(helm upgrade *)"
    ]
  }
}
```

This gives senior engineers broader access without lowering the safety floor for the rest of the team.

---

## Step 6: Shared Hook Templates

### Team Safety Hook (committed to repo)

```bash
#!/bin/bash
# .claude/hooks/team-safety.sh
# Shared safety checks for the entire team

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Prevent operations during maintenance windows
MAINTENANCE_FILE="/tmp/maintenance-mode.flag"
if [ -f "$MAINTENANCE_FILE" ]; then
    if echo "$COMMAND" | grep -qiE "kubectl.*(apply|delete|scale|patch)"; then
        echo '{"decision": "block", "reason": "MAINTENANCE MODE ACTIVE: Infrastructure changes are frozen. Check #ops-announcements for details."}'
        exit 0
    fi
fi

# Prevent operations outside business hours unless during an incident
HOUR=$(date +%H)
INCIDENT_FILE="/tmp/active-incident.flag"
if [ "$HOUR" -lt 6 ] || [ "$HOUR" -gt 22 ]; then
    if [ ! -f "$INCIDENT_FILE" ]; then
        if echo "$COMMAND" | grep -qiE "terraform apply|helm upgrade|kubectl apply"; then
            echo '{"decision": "block", "reason": "OUTSIDE BUSINESS HOURS: Production changes restricted to 06:00-22:00 unless an incident is active. Create /tmp/active-incident.flag to override."}'
            exit 0
        fi
    fi
fi

exit 0
```

---

## Step 7: Version Control Best Practices

### Commit Strategy for Claude Code Config

```bash
# Initial setup
git add .claude/settings.json .claude/commands/ CLAUDE.md
git commit -m "feat: add Claude Code team configuration

- Shared safety permissions (allow reads, deny destructive)
- Incident response slash command
- Deployment workflow slash command
- Project CLAUDE.md with architecture and conventions"

# After an incident teaches a new lesson
git add CLAUDE.md
git commit -m "ops: update CLAUDE.md with lesson from INC-2847

- Added rule: always verify PDB before scaling down
- Added warning about Redis connection pool exhaustion
- Updated service dependency map"
```

### PR Template for Config Changes

```markdown
## Claude Code Configuration Change

### What changed
- [ ] CLAUDE.md (project knowledge)
- [ ] settings.json (permissions/hooks)
- [ ] Slash commands (operational workflows)
- [ ] Hook scripts (safety/audit)

### Why
[Describe the operational scenario that motivated this change]

### Impact
- Who is affected: [All team members / SRE only / Specific team]
- Safety implication: [More permissive / More restrictive / Neutral]
- Tested by: [How you verified this works correctly]
```

---

## What Success Looks Like

After completing this lab, you should have:

- [x] A shared `.claude/settings.json` with team-appropriate permissions
- [x] A CLAUDE.md that encodes your team's operational knowledge
- [x] Environment-specific rules that prevent accidental production changes
- [x] Code review slash commands for infrastructure PRs
- [x] An onboarding section that helps new team members immediately
- [x] A `.gitignore` entry for personal settings overrides
- [x] Understanding of project vs user settings separation

When a new engineer joins your team, they clone the repo, run `claude`, and immediately have access to the same AI-assisted operational knowledge that took your senior engineers years to accumulate.

---

## Key Takeaway

The highest-leverage Claude Code investment is not in individual productivity — it is in team consistency. When your safety rules, operational knowledge, and workflow automation are encoded in version-controlled project files, every engineer on the team operates with the same guardrails and the same institutional knowledge. The AI becomes a force multiplier not just for individuals, but for the entire team's operational maturity. New hires are immediately productive, on-call engineers have consistent procedures, and hard-won operational lessons are never forgotten.

---

**Previous: [Lab 4: MCP Integration](lab4-mcp-integration.md)** | **Back to [README](../README.md)**
