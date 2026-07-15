# Lab 4: ArgoCD AI Risk Gate

> **Mission:** Add AI risk assessment before ArgoCD syncs deployments to production — block high-risk changes automatically and require human approval.

---

## The Concept

### Why Risk-Gate Deployments?

ArgoCD syncs happen fast. A single manifest change can scale your replicas from 3 to 300, switch to an untested image, or accidentally deploy to the wrong namespace. AI risk scoring catches these dangerous patterns BEFORE the sync happens — not after your pager goes off.

> **Analogy:** Like a pharmacist checking a prescription before dispensing. The doctor (developer) wrote it, but the pharmacist (AI risk gate) checks for dangerous drug interactions, incorrect dosages, and wrong-patient errors before the medicine (deployment) reaches the patient (production).

---

### Risk Scoring Dimensions

| Dimension | Low Risk (0-2) | Medium Risk (3-5) | High Risk (6-10) |
|-----------|---------------|-------------------|------------------|
| Replicas | No change | Scale up 2x | Scale down or 10x+ up |
| Images | Tag update (patch) | Minor version bump | Major version or unknown registry |
| Resources | Increase limits | Decrease limits slightly | Remove limits entirely |
| Namespace | Same namespace | Staging namespace | Production or kube-system |
| RBAC | No change | Add view permissions | ClusterRole or admin |

---

## What You'll Build

A risk scoring engine that:
1. Analyzes ArgoCD application manifests (before vs. after)
2. Scores changes across multiple dimensions
3. Uses Claude for nuanced analysis of complex changes
4. Blocks syncs that exceed a risk threshold

---

## Step 1: Static Risk Scoring

```python
def score_manifest_changes(old_manifest, new_manifest):
    """Score changes between two K8s manifests."""
    risk_score = 0
    findings = []

    # Replica changes
    old_replicas = old_manifest.get("spec", {}).get("replicas", 1)
    new_replicas = new_manifest.get("spec", {}).get("replicas", 1)

    if new_replicas < old_replicas:
        risk_score += 5
        findings.append(f"SCALE DOWN: {old_replicas} -> {new_replicas} replicas")
    elif new_replicas > old_replicas * 3:
        risk_score += 4
        findings.append(f"LARGE SCALE UP: {old_replicas} -> {new_replicas} replicas")

    # Image changes
    old_image = get_container_image(old_manifest)
    new_image = get_container_image(new_manifest)

    if old_image != new_image:
        if get_registry(old_image) != get_registry(new_image):
            risk_score += 6
            findings.append(f"REGISTRY CHANGE: {old_image} -> {new_image}")
        elif get_major_version(old_image) != get_major_version(new_image):
            risk_score += 4
            findings.append(f"MAJOR VERSION BUMP: {old_image} -> {new_image}")
        else:
            risk_score += 1
            findings.append(f"Image update: {old_image} -> {new_image}")

    # Resource limit changes
    old_limits = get_resource_limits(old_manifest)
    new_limits = get_resource_limits(new_manifest)

    if old_limits and not new_limits:
        risk_score += 7
        findings.append("RESOURCE LIMITS REMOVED — unbounded resource usage")

    # Namespace
    new_ns = new_manifest.get("metadata", {}).get("namespace", "default")
    if new_ns in ("production", "prod", "kube-system"):
        risk_score += 3
        findings.append(f"Deploying to sensitive namespace: {new_ns}")

    return risk_score, findings
```

---

## Step 2: AI-Powered Nuanced Analysis

```python
import anthropic

client = anthropic.Anthropic()

def ai_risk_assessment(manifest_diff, static_score, findings):
    """Use Claude for nuanced risk analysis beyond static checks."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system="""You are an SRE risk assessor for Kubernetes deployments.
Given a manifest change, static risk score, and findings:
1. Assess whether the static score is appropriate (could be over/under)
2. Identify risks the static analysis missed
3. Recommend: APPROVE, REQUIRE_REVIEW, or BLOCK
4. If blocking, explain what must change before deployment is safe.

Consider blast radius, rollback difficulty, and time-of-day risk.""",
        messages=[
            {"role": "user", "content": f"""Manifest diff:
{manifest_diff}

Static risk score: {static_score}/10
Static findings:
{chr(10).join(f'- {f}' for f in findings)}

Provide your risk assessment."""}
        ]
    )
    return message.content[0].text
```

---

## Step 3: ArgoCD PreSync Hook Integration

```yaml
# argocd-risk-gate-hook.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ai-risk-gate
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      containers:
        - name: risk-gate
          image: python:3.11-slim
          command: ["python3", "/scripts/risk_gate.py"]
          env:
            - name: ANTHROPIC_API_KEY
              valueFrom:
                secretKeyRef:
                  name: ai-credentials
                  key: anthropic-api-key
            - name: RISK_THRESHOLD
              value: "7"
      restartPolicy: Never
  backoffLimit: 0  # Fail immediately — don't retry risky deploys
```

---

## Step 4: Decision Logic

```python
def gate_decision(risk_score, ai_assessment):
    """Make the final gate decision."""
    THRESHOLD = 7

    if risk_score >= THRESHOLD:
        print(f"BLOCKED: Risk score {risk_score}/10 exceeds threshold {THRESHOLD}")
        print(f"AI Assessment: {ai_assessment}")
        exit(1)  # Non-zero exit = ArgoCD PreSync hook fails = sync blocked
    elif risk_score >= 4:
        print(f"CAUTION: Risk score {risk_score}/10 — requiring review")
        # Post to Slack, create approval ticket, etc.
        exit(0)  # Allow but notify
    else:
        print(f"APPROVED: Risk score {risk_score}/10 — safe to deploy")
        exit(0)
```

---

## Run It

```bash
python3 demos/task4_argocd_risk_gate.py
```

---

## What Success Looks Like

Given a manifest that:
- Changes the image from `myapp:1.2.3` to `myapp:2.0.0` (major version bump)
- Reduces replicas from 5 to 2 (scale down)
- Targets the `production` namespace

The risk gate:
1. Calculates a static score of 12/10 (multiple high-risk factors)
2. AI confirms: "BLOCK — major version bump combined with replica reduction in production creates high rollback risk. Deploy to staging first."
3. The PreSync hook exits non-zero, blocking the ArgoCD sync
4. Team is notified via Slack with the full assessment

---

## Key Takeaway

Static risk scoring catches the obvious dangers (scale-downs, removed limits). AI adds nuanced judgment: "This replica reduction might be fine after the load test showed we're over-provisioned" vs. "This replica reduction during Black Friday is insane." The combination of deterministic rules + AI reasoning creates a risk gate that's both reliable and intelligent.

---

Next: [Lab 5: Commit Analyzer](lab5-commit-analyzer.md)
