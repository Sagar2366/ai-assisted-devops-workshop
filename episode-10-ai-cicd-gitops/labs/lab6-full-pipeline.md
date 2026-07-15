# Lab 6: Full AI-Powered CI/CD Pipeline

> **Mission:** Wire all components into an end-to-end AI-powered pipeline — from commit to production, with AI gates at every stage.

---

## The Concept

### Why a Full Pipeline?

Individual AI tools are useful. But the real power comes from orchestrating them into a single flow: every commit gets reviewed, every pipeline gets optimized, every deployment gets risk-scored. No manual steps, no gaps where bugs slip through.

> **Analogy:** Like an airport security system. Individual checkpoints (metal detector, bag scanner, passport check) are useful alone — but wired together into a single flow, they create a system where nothing dangerous gets through. Each gate catches what the others miss.

---

### Pipeline Architecture

```
                    +-----------------+
                    |   Developer     |
                    |   git push      |
                    +--------+--------+
                             |
                             v
                    +--------+--------+
                    |  AI Code Review |  <-- Stage 1: Review diff
                    |  (Claude API)   |
                    +--------+--------+
                             |
                      Pass / Fail
                             |
                             v
                    +--------+--------+
                    | Pipeline        |  <-- Stage 2: Run tests
                    | (GitHub Actions)|
                    +--------+--------+
                             |
                             v
                    +--------+--------+
                    | AI Risk Gate    |  <-- Stage 3: Score deployment
                    | (PreSync Hook)  |
                    +--------+--------+
                             |
                      Low / High Risk
                             |
                    +--------+--------+
                    |    ArgoCD       |  <-- Stage 4: Deploy
                    |    Sync         |
                    +--------+--------+
                             |
                             v
                    +--------+--------+
                    | AI Release      |  <-- Stage 5: Generate notes
                    | Notes Generator |
                    +--------+--------+
                             |
                             v
                    +--------+--------+
                    |  Changelog &    |
                    |  Notification   |
                    +-----------------+
```

---

### Stage Responsibilities

| Stage | Tool | Blocks On | Output |
|-------|------|-----------|--------|
| 1. Code Review | Claude API | Critical findings | Review comment on PR |
| 2. CI Tests | GitHub Actions | Test failures | Build artifacts |
| 3. Risk Gate | Risk scorer + Claude | Score > threshold | Approve/Block/Review |
| 4. Deploy | ArgoCD | Risk gate failure | Running pods |
| 5. Release Notes | Commit analyzer | Never blocks | Changelog, Slack post |

---

## What You'll Build

A Python orchestrator that simulates the full pipeline end-to-end: takes a code change, runs it through all AI gates, and produces a final deploy/no-deploy decision with full audit trail.

---

## Step 1: Pipeline Orchestrator

```python
import anthropic

client = anthropic.Anthropic()

class AIPipeline:
    def __init__(self):
        self.stages = []
        self.blocked = False
        self.audit_trail = []

    def run_stage(self, name, func, *args):
        """Run a pipeline stage with logging."""
        print(f"\n{'='*60}")
        print(f"STAGE: {name}")
        print(f"{'='*60}")

        result = func(*args)
        self.stages.append({"name": name, "result": result})
        self.audit_trail.append(f"[{name}] {result.get('status', 'unknown')}")

        if result.get("status") == "BLOCKED":
            self.blocked = True
            print(f"PIPELINE BLOCKED at stage: {name}")

        return result
```

---

## Step 2: Integrate All Stages

```python
def stage_code_review(diff):
    """Stage 1: AI reviews the code change."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system="Review this diff. Return JSON: {\"status\": \"PASS\"|\"FAIL\", \"critical_issues\": count, \"findings\": [...]}",
        messages=[{"role": "user", "content": f"```diff\n{diff}\n```"}]
    )
    return {"status": "PASS", "details": message.content[0].text}


def stage_risk_gate(manifest):
    """Stage 3: Score deployment risk."""
    score = calculate_risk_score(manifest)
    if score >= 7:
        return {"status": "BLOCKED", "score": score}
    return {"status": "PASS", "score": score}


def stage_release_notes(commits):
    """Stage 5: Generate release notes."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system="Generate concise release notes from these commits.",
        messages=[{"role": "user", "content": commits}]
    )
    return {"status": "PASS", "notes": message.content[0].text}
```

---

## Step 3: Run the Full Pipeline

```python
pipeline = AIPipeline()

# Stage 1: Code Review
pipeline.run_stage("Code Review", stage_code_review, diff)

if not pipeline.blocked:
    # Stage 2: Tests (simulated)
    pipeline.run_stage("CI Tests", lambda: {"status": "PASS", "tests": "142 passed"})

if not pipeline.blocked:
    # Stage 3: Risk Gate
    pipeline.run_stage("Risk Gate", stage_risk_gate, deployment_manifest)

if not pipeline.blocked:
    # Stage 4: Deploy (simulated)
    pipeline.run_stage("Deploy", lambda: {"status": "PASS", "target": "production"})

    # Stage 5: Release Notes
    pipeline.run_stage("Release Notes", stage_release_notes, commit_log)

# Final Report
print("\n" + "="*60)
print("PIPELINE RESULT:", "BLOCKED" if pipeline.blocked else "DEPLOYED")
print("Audit Trail:")
for entry in pipeline.audit_trail:
    print(f"  {entry}")
```

---

## Run It

```bash
python3 demos/task6_full_pipeline.py
```

---

## What Success Looks Like

### Scenario A: Safe Deployment
```
STAGE: Code Review ............ PASS (0 critical issues)
STAGE: CI Tests ............... PASS (142 tests passed)
STAGE: Risk Gate .............. PASS (score: 3/10)
STAGE: Deploy ................. PASS (production)
STAGE: Release Notes .......... PASS (changelog generated)

PIPELINE RESULT: DEPLOYED
```

### Scenario B: Risky Change Blocked
```
STAGE: Code Review ............ PASS (0 critical issues)
STAGE: CI Tests ............... PASS (142 tests passed)
STAGE: Risk Gate .............. BLOCKED (score: 9/10)
  - Major version bump in production
  - Replica scale-down during peak hours
  - Resource limits removed

PIPELINE RESULT: BLOCKED
Action Required: Human review before deployment
```

---

## Key Takeaway

The full pipeline is more than the sum of its parts. Each AI gate catches different classes of risk: code review catches bugs, the risk gate catches deployment dangers, and release notes ensure nothing ships without documentation. The audit trail provides full traceability — every decision, every AI assessment, every gate result — exactly what you need when the post-mortem asks "how did this get to production?"

---

Back to: [README](../README.md)
