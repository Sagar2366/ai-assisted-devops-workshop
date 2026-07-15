# Lab 5: CIS Compliance Checker

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut | Docker Captain

> **Mission:** Build an AI-powered compliance checker that validates Kubernetes manifests against CIS Kubernetes Benchmark controls, producing audit-ready reports with pass/fail status, evidence, and remediation guidance.

---

## Concepts

### What is the CIS Kubernetes Benchmark?

The Center for Internet Security (CIS) Kubernetes Benchmark is the industry-standard security configuration guide. Think of it as a building code inspection for your Kubernetes cluster:

| Building Code | CIS Benchmark |
|--------------|---------------|
| Fire exits required | Pod security standards enforced |
| Load-bearing walls certified | RBAC properly configured |
| Electrical grounding tested | Network policies in place |
| Inspection certificate | Compliance report |

### CIS Benchmark Structure

```
CIS Kubernetes Benchmark v1.8
├── 1. Control Plane Components
│   ├── 1.1 API Server
│   ├── 1.2 Controller Manager
│   └── 1.3 Scheduler
├── 2. etcd
├── 3. Control Plane Configuration
├── 4. Worker Nodes
│   ├── 4.1 Kubelet
│   └── 4.2 kube-proxy
└── 5. Policies
    ├── 5.1 RBAC and Service Accounts
    ├── 5.2 Pod Security Standards
    ├── 5.3 Network Policies
    ├── 5.4 Secrets Management
    └── 5.7 General Policies
```

### Manifest-Level CIS Controls

While many CIS controls require cluster-level access, several can be validated from manifests alone:

| CIS Control | What We Check | From Manifest? |
|-------------|--------------|----------------|
| 5.1.1 | RBAC least privilege | Yes (Roles) |
| 5.1.5 | Default service accounts | Yes (SA config) |
| 5.2.1 | Privileged containers | Yes (securityContext) |
| 5.2.2 | Host namespaces | Yes (hostPID, hostNetwork) |
| 5.2.6 | Root containers | Yes (runAsNonRoot) |
| 5.3.2 | Default deny NetworkPolicy | Yes (NetworkPolicy) |
| 5.4.1 | Secrets as files not env | Yes (env vs volume) |

---

## Step 1: Run the Compliance Checker

```bash
cd demos
python3 task5_compliance_checker.py
```

The checker evaluates the insecure deployment against specific CIS controls.

## Step 2: Understanding the CIS Mapping

Each check maps to a specific CIS control with rationale:

```python
CIS_CONTROLS = {
    "5.2.1": {
        "title": "Ensure that the cluster has at least one active policy control mechanism in place",
        "check": "Verify privileged: true is not set",
        "scored": True,
        "level": 1
    },
    "5.2.2": {
        "title": "Minimize the admission of privileged containers",
        "check": "Verify hostPID, hostIPC, hostNetwork are false",
        "scored": True,
        "level": 1
    },
    "5.2.6": {
        "title": "Minimize the admission of root containers",
        "check": "Verify runAsNonRoot: true or runAsUser > 0",
        "scored": True,
        "level": 2
    }
}
```

## Step 3: Audit Report Format

The compliance checker produces audit-ready output:

```
┌─────────────────────────────────────────────────────────────┐
│              CIS Kubernetes Benchmark v1.8                    │
│              Compliance Assessment Report                     │
├─────────────────────────────────────────────────────────────┤
│ Assessment Date: 2026-07-15                                  │
│ Target: insecure-deployment.yaml                             │
│ Controls Assessed: 12                                        │
│ Pass: 2 | Fail: 8 | N/A: 2                                  │
│ Compliance Score: 20%                                        │
└─────────────────────────────────────────────────────────────┘
```

## Step 4: Evidence Collection

For audit purposes, the checker provides evidence for each finding:

```
Control: CIS 5.2.1 - Minimize privileged containers
Status: FAIL
Evidence:
  Resource: Deployment/insecure-app
  Container: main
  Path: spec.template.spec.containers[0].securityContext.privileged
  Value: true
  Expected: false or not set
Remediation:
  Remove 'privileged: true' from container securityContext.
  If elevated permissions are needed, use specific capabilities instead.
```

## Step 5: Compliance Scoring

The checker calculates a weighted compliance score:

```python
# Scoring methodology:
# - Level 1 controls (basic security): Weight 1.0
# - Level 2 controls (defense in depth): Weight 0.7
# - Scored controls count toward pass/fail
# - Not-scored controls are informational

# Score = (sum of passed weighted controls) / (sum of all weighted controls) * 100
```

## Step 6: Delta Reporting

Compare compliance between versions to track improvement:

```python
# The AI can compare two manifests and report:
# - Newly introduced violations
# - Resolved violations
# - Compliance score trend
# - Remaining remediation effort estimate
```

---

## What Success Looks Like

After running `task5_compliance_checker.py`:

```
═══════════════════════════════════════════════════════════════════
   TASK 5: CIS Kubernetes Benchmark Compliance Checker
═══════════════════════════════════════════════════════════════════

Target: demos/sample-manifests/insecure-deployment.yaml
Benchmark: CIS Kubernetes v1.8
─────────────────────────────────────────────────────────────────

[FAIL] CIS 5.2.1 — Privileged containers must be minimized
       Evidence: privileged: true in container 'main'

[FAIL] CIS 5.2.2 — Host namespaces must not be shared
       Evidence: hostPID: true, hostNetwork: true

[FAIL] CIS 5.2.6 — Root containers must be minimized
       Evidence: No runAsNonRoot constraint, no runAsUser set

[FAIL] CIS 5.4.1 — Resource limits must be defined
       Evidence: No resources.limits in container spec

[PASS] CIS 5.1.5 — Default service account not used
       Evidence: serviceAccountName: app-sa (custom SA)

─────────────────────────────────────────────────────────────────
Compliance Score: 20% (2/10 controls passing)
Level 1 Controls: 1/6 PASS | Level 2 Controls: 1/4 PASS

Key Learning: CIS benchmarks provide a standardized, auditable
framework for Kubernetes security. AI maps manifest configurations
to specific controls, producing evidence-based compliance reports.

Next: Lab 6 — Auto-remediate findings with AI-generated fixes
```

---

## Key Takeaway

Compliance checking is not just about passing an audit — it is about establishing a measurable security baseline. AI-powered CIS checking bridges the gap between security frameworks (written for auditors) and Kubernetes manifests (written by developers), automatically mapping configurations to control requirements and producing evidence that satisfies both technical teams and compliance officers.

---

**Next:** [Lab 6 — Remediation](lab6-remediation.md) — Use AI to generate secure, fixed versions of insecure manifests.
