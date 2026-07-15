# Lab 1: Writing CLAUDE.md Files for DevOps Repositories

> **Mission:** Create CLAUDE.md files that encode your team's operational knowledge, architecture decisions, and safety constraints — transforming Claude Code from a generic assistant into a DevOps expert for your specific infrastructure.

## Concept: What Is CLAUDE.md?

CLAUDE.md is a **machine-readable runbook** that sits in your repository. Every time Claude Code starts in a directory, it automatically reads this file and follows its instructions.

**Analogy:** Imagine onboarding a new SRE to your team. You would give them:
- Architecture diagrams (what exists)
- Runbooks (how to operate it)
- War stories (what NOT to do)
- Team conventions (how we do things here)

CLAUDE.md is all of this in one file, written for an AI teammate that never forgets.

## How CLAUDE.md Inheritance Works

```
/repo/CLAUDE.md                    ← Always loaded (project root)
/repo/terraform/CLAUDE.md          ← Added when working in terraform/
/repo/kubernetes/CLAUDE.md         ← Added when working in kubernetes/
/repo/scripts/CLAUDE.md            ← Added when working in scripts/
```

Claude Code merges these contextually — the root file provides base knowledge, and subdirectory files add specialized context.

## Step 1: Root CLAUDE.md — Project Overview

Create the root `CLAUDE.md` in your infrastructure repository:

```markdown
# Project: Acme Infrastructure

## Architecture
- **Cloud Provider:** AWS (us-east-1 primary, eu-west-1 DR)
- **Orchestration:** EKS 1.29 with Karpenter autoscaling
- **IaC:** Terraform 1.7+ with remote state in S3
- **CI/CD:** GitHub Actions → ArgoCD → EKS
- **Observability:** Prometheus + Grafana + Loki

## Environments
| Environment | Cluster         | Namespace Pattern    |
|-------------|-----------------|----------------------|
| dev         | eks-dev-use1    | {service}-dev        |
| staging     | eks-stg-use1    | {service}-staging    |
| production  | eks-prod-use1   | {service}-prod       |
| dr          | eks-dr-euw1     | {service}-dr         |

## Critical Rules
- NEVER run `terraform apply` without a plan file
- NEVER delete resources in production namespace directly
- NEVER commit secrets — use AWS Secrets Manager + External Secrets Operator
- ALWAYS use `--dry-run=client` before any kubectl apply in prod
- ALWAYS check ArgoCD sync status before manual interventions

## Conventions
- Terraform modules follow: modules/{provider}/{resource-type}/
- Kubernetes manifests follow: k8s/{environment}/{service}/
- All PRs require at least one SRE approval for infra changes
- Commit messages follow Conventional Commits (feat:, fix:, ops:)

## Common Tasks
- **Deploy to staging:** Push to `staging` branch, ArgoCD auto-syncs
- **Deploy to production:** Create release tag `v*.*.*`, ArgoCD syncs after approval
- **Rollback:** `argocd app rollback <app-name> <revision>`
- **Scale service:** Edit HPA in k8s/{env}/{service}/hpa.yaml
```

## Step 2: Subdirectory CLAUDE.md — Terraform Context

Create `terraform/CLAUDE.md`:

```markdown
# Terraform Context

## State Management
- Backend: S3 bucket `acme-terraform-state-{env}`
- Lock: DynamoDB table `terraform-locks-{env}`
- Workspaces: NOT used — separate state files per environment

## Module Structure
```
modules/
├── aws/
│   ├── eks/          # EKS cluster configuration
│   ├── rds/          # RDS instances (PostgreSQL)
│   ├── elasticache/  # Redis clusters
│   └── networking/   # VPC, subnets, security groups
└── common/
    ├── tags/         # Standard tagging module
    └── naming/       # Resource naming conventions
```

## Safety Rules
- Always run `terraform plan -out=plan.tfplan` before apply
- Never use `terraform taint` in production — use `moved` blocks
- Check blast radius: `terraform plan | grep "Plan:"`
- If destroying resources, ALWAYS confirm the workspace/environment first

## Naming Convention
- Resources: `{project}-{environment}-{service}-{resource}`
- Example: `acme-prod-api-rds`

## When Reviewing Terraform Changes
1. Check for state drift: compare plan output with expected
2. Verify no secrets in variables (use data sources for secrets)
3. Ensure tags include: Environment, Team, Service, ManagedBy
4. Confirm lifecycle rules for stateful resources (prevent_destroy)
```

## Step 3: Subdirectory CLAUDE.md — Kubernetes Context

Create `kubernetes/CLAUDE.md`:

```markdown
# Kubernetes Context

## Cluster Access
- Use `kubectx` to switch contexts: dev, staging, prod
- NEVER run commands against prod without explicit confirmation
- Default namespace is NOT used — always specify `-n <namespace>`

## Manifest Standards
- All resources must have resource requests AND limits
- PodDisruptionBudgets required for production services
- NetworkPolicies required for all namespaces
- All images must reference SHA digests, not mutable tags

## Debugging Playbook
When investigating pod issues:
1. `kubectl get events -n <ns> --sort-by=.lastTimestamp`
2. `kubectl describe pod <pod> -n <ns>`
3. `kubectl logs <pod> -n <ns> --previous` (for crash loops)
4. Check HPA status: `kubectl get hpa -n <ns>`
5. Check node pressure: `kubectl top nodes`

## Forbidden Actions
- `kubectl delete namespace` — NEVER (destroys everything)
- `kubectl exec` in production — ONLY during active incidents with approval
- `kubectl edit` — NEVER in production (use GitOps via ArgoCD)
- `kubectl scale --replicas=0` — ONLY in dev/staging
```

## Step 4: CLAUDE.md for Scripts Directory

Create `scripts/CLAUDE.md`:

```markdown
# Scripts Context

## Script Categories
- `deploy/` — Deployment automation (called by CI/CD)
- `maintenance/` — Scheduled maintenance tasks
- `incident/` — Incident response automation
- `migration/` — Data and infrastructure migrations

## Requirements for All Scripts
- Must have `set -euo pipefail` at the top
- Must log to stdout (captured by CI/CD)
- Must accept `--dry-run` flag for testing
- Must exit with meaningful codes (0=success, 1=error, 2=warning)
- Must not hardcode environment-specific values

## Testing Scripts
- Test in dev environment first: `ENV=dev ./script.sh --dry-run`
- Integration tests in `tests/` mirror script structure
- Use `shellcheck` for static analysis before committing
```

## Step 5: Test Your CLAUDE.md Configuration

Launch Claude Code and verify it picks up your context:

```bash
# From repo root
claude

> What cloud provider does this project use?
# Should answer "AWS" based on CLAUDE.md

> What should I check before running terraform apply?
# Should mention plan file, blast radius, state drift

# Navigate to kubernetes directory context
> If I need to debug a crashing pod, what steps should I follow?
# Should list the debugging playbook from kubernetes/CLAUDE.md
```

## Step 6: Advanced CLAUDE.md Patterns

### Pattern: Conditional Instructions

```markdown
## When Working on Incident Response
- Prioritize speed over code elegance
- Skip tests for hotfixes (mark with TODO for follow-up)
- Always create a post-incident ticket

## When Working on New Features
- Write tests first (TDD approach)
- Update architecture docs in docs/
- Add monitoring/alerting for new services
```

### Pattern: Tool-Specific Instructions

```markdown
## When Using kubectl
- Always specify namespace with -n flag
- Prefer `get -o yaml` over `describe` for programmatic use
- Use `--dry-run=client -o yaml` to generate manifests

## When Using Terraform
- Run `terraform fmt` before committing
- Use `terraform validate` before plan
- Check for module updates: `terraform init -upgrade`
```

### Pattern: Response Format Instructions

```markdown
## Output Preferences
- When showing infrastructure changes, format as a table
- When explaining errors, include the fix command
- When creating Terraform, include variable descriptions
- When writing Kubernetes manifests, include comments explaining non-obvious fields
```

## What Success Looks Like

After completing this lab, you should have:

- [x] A root CLAUDE.md encoding your architecture and critical rules
- [x] Subdirectory CLAUDE.md files for terraform, kubernetes, scripts
- [x] Claude Code correctly answering questions using your project context
- [x] Conditional instructions for different work modes
- [x] Your team's operational knowledge captured in version-controlled files

## Key Takeaway

CLAUDE.md is the single most impactful configuration for Claude Code. A well-written CLAUDE.md turns generic AI assistance into domain-specific expertise. Treat it like living documentation — update it after every incident, every architecture decision, every lesson learned. Unlike traditional docs that rot, CLAUDE.md is actively used every time Claude Code runs.

## Next

Proceed to [Lab 2: Pre/Post Hooks for Safety and Audit](lab2-hooks.md) to add runtime guardrails that enforce your CLAUDE.md rules automatically.
