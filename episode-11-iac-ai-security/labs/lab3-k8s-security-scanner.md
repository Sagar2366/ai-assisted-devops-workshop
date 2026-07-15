# Lab 3: Kubernetes Security Scanner

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut | Docker Captain

> **Mission:** Build an AI-powered scanner that analyzes Kubernetes manifests for security misconfigurations including privileged containers, missing security contexts, RBAC over-permissions, and absent network policies.

---

## Concepts

### The Kubernetes Attack Surface

Kubernetes manifests define the security posture of your workloads. A single misconfiguration can turn a container into an attack vector:

```
Pod Security Issues          →  Container escape → Node compromise
RBAC Over-permissions        →  Lateral movement → Cluster takeover
Missing Network Policies     →  Unrestricted pod-to-pod communication
No Resource Limits           →  DoS via resource exhaustion
```

### Security Layers in Kubernetes

Think of Kubernetes security like concentric castle walls:

| Layer | What It Protects | Common Misconfigurations |
|-------|-----------------|--------------------------|
| Pod Security | Container runtime | Privileged mode, root user, hostPID |
| RBAC | API access | ClusterAdmin to all service accounts |
| Network Policies | Pod communication | No policies = flat network |
| Resource Limits | Cluster stability | No limits = noisy neighbor DoS |
| Secrets Management | Sensitive data | Secrets in env vars, no encryption |

---

## Step 1: Examine the Insecure Deployment

```bash
cat demos/sample-manifests/insecure-deployment.yaml
```

This manifest intentionally violates multiple security best practices:
- Runs as root (UID 0)
- Privileged security context
- No resource limits
- Mounts the Docker socket
- Uses `latest` image tag
- No readiness/liveness probes

## Step 2: Run the Scanner

```bash
cd demos
python3 task3_k8s_security_scanner.py
```

The scanner parses the YAML and sends it to Claude with a comprehensive security checklist.

## Step 3: Understanding the Security Checks

The scanner evaluates manifests against these categories:

### Pod Security Standards (PSS)

```python
PSS_CHECKS = """
Check against Kubernetes Pod Security Standards:

RESTRICTED (most secure):
- Must run as non-root (runAsNonRoot: true)
- Must drop ALL capabilities
- Must set readOnlyRootFilesystem: true
- Must not allow privilege escalation
- Seccomp profile must be RuntimeDefault or Localhost

BASELINE (minimum):
- Must not use privileged: true
- Must not use hostNetwork, hostPID, hostIPC
- Must not mount hostPath volumes
- Must not use dangerous capabilities (NET_RAW, SYS_ADMIN)
"""
```

### RBAC Analysis

```python
RBAC_CHECKS = """
For any RBAC resources (Role, ClusterRole, RoleBinding, ClusterRoleBinding):
- Flag wildcard (*) verbs or resources
- Flag ClusterRoleBindings to default service accounts
- Flag access to secrets, configmaps with sensitive data
- Flag impersonation permissions
- Check for privilege escalation paths (bind, escalate verbs)
"""
```

### Network Policy Coverage

```python
NETWORK_CHECKS = """
- Does the namespace have a default-deny NetworkPolicy?
- Are ingress rules scoped to specific pods/namespaces?
- Are egress rules restricting outbound traffic?
- Is there DNS egress allowed (port 53)?
"""
```

## Step 4: Interpreting Results

The scanner output maps findings to real attack scenarios:

```
Finding: privileged: true
Attack: Container escape via /dev access → mount host filesystem
        → read kubelet credentials → compromise all pods on node
Reference: CIS Kubernetes 5.2.1 - Minimize privileged containers
```

```
Finding: No resource limits defined
Attack: Cryptocurrency miner deploys → consumes all node CPU/memory
        → other pods evicted → service disruption
Reference: CIS Kubernetes 5.4.1 - Ensure resource limits are set
```

## Step 5: Multi-Document Scanning

Real deployments have multiple resources. The scanner handles multi-document YAML:

```python
# The scanner processes all documents in a YAML file:
# - Deployments, StatefulSets, DaemonSets (pod security)
# - Services (type LoadBalancer exposure)
# - Roles/ClusterRoles (RBAC permissions)
# - NetworkPolicies (or lack thereof)
# - ServiceAccounts (automountServiceAccountToken)
```

## Step 6: Severity Scoring

The AI assigns severity based on exploitability and impact:

| Severity | Criteria | Example |
|----------|----------|---------|
| CRITICAL | Immediate cluster compromise possible | privileged + hostPID + hostNetwork |
| HIGH | Container escape or data exposure likely | privileged OR root + hostPath |
| MEDIUM | Defense-in-depth violation | No readOnlyRootFilesystem |
| LOW | Best practice deviation | Missing labels, no probes |

---

## What Success Looks Like

After running `task3_k8s_security_scanner.py`:

```
═══════════════════════════════════════════════════════════════════
   TASK 3: Kubernetes Manifest Security Scanner
═══════════════════════════════════════════════════════════════════

Scanning: demos/sample-manifests/insecure-deployment.yaml
─────────────────────────────────────────────────────────────────

[CRITICAL] Container runs in privileged mode (CIS 5.2.1)
[CRITICAL] Docker socket mounted as volume (Container escape risk)
[HIGH] Container runs as root user (CIS 5.2.6)
[HIGH] No resource limits defined (CIS 5.4.1)
[MEDIUM] Using 'latest' image tag (Supply chain risk)
[MEDIUM] allowPrivilegeEscalation not set to false (CIS 5.2.5)
[MEDIUM] No readOnlyRootFilesystem (CIS 5.2.4)
[LOW] No readiness/liveness probes defined
[LOW] No pod disruption budget

Pod Security Standard: FAILS Baseline and Restricted levels

Key Learning: Kubernetes security requires defense-in-depth —
no single control is sufficient; layers of restrictions prevent
container escape from becoming cluster compromise.

Next: Lab 4 — Scan Dockerfiles for security vulnerabilities
```

---

## Key Takeaway

Kubernetes security is not a single checkbox but a layered defense strategy. AI scanning understands the *relationships* between security controls — a privileged container with hostPath access is far more dangerous than either alone. By mapping findings to real attack paths, the scanner helps developers understand not just *what* to fix, but *why* it matters.

---

**Next:** [Lab 4 — Dockerfile Scanner](lab4-dockerfile-scanner.md) — Audit Dockerfiles for vulnerabilities, secrets, and best practice violations.
