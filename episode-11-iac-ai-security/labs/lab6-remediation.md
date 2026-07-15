# Lab 6: AI-Powered Security Remediation

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut | Docker Captain

> **Mission:** Use AI to automatically generate secure, fixed versions of insecure infrastructure manifests — preserving original functionality while hardening security posture, with clear explanations of every change made.

---

## Concepts

### The Remediation Challenge

Finding security issues is only half the battle. The real challenge is fixing them without breaking functionality:

```
Traditional Fix Process:
  Security team finds issue → Files ticket → Developer context-switches →
  Researches fix → Implements → Breaks something → Reverts → Tries again

AI-Assisted Fix Process:
  AI finds issue → Generates fix preserving intent → Explains rationale →
  Developer reviews and applies
```

### Why AI Remediation is Different

| Manual Remediation | AI Remediation |
|-------------------|----------------|
| Developer must research each fix | Fix generated with context |
| Generic examples from docs | Tailored to your specific manifest |
| May introduce new issues | Holistic — fixes don't conflict |
| No explanation of *why* | Every change explained with rationale |
| Hours per finding | Seconds per manifest |

### The Remediation Pipeline

```
Insecure Manifest
       │
       ▼
┌──────────────────┐
│ Identify Issues  │  ← What's wrong (from Labs 2-5)
├──────────────────┤
│ Preserve Intent  │  ← What was the developer trying to do?
├──────────────────┤
│ Generate Fix     │  ← Secure version maintaining functionality
├──────────────────┤
│ Explain Changes  │  ← Diff with rationale for each change
└──────────────────┘
       │
       ▼
Secure Manifest + Change Report
```

---

## Step 1: Run the Remediation Engine

```bash
cd demos
python3 task6_remediation.py
```

The remediation engine processes all three insecure sample files and generates fixed versions.

## Step 2: Understanding the Remediation Prompt

The key to effective remediation is instructing the AI to balance security with functionality:

```python
remediation_prompt = """You are a security remediation engine. Given an insecure
infrastructure manifest:

1. IDENTIFY all security issues (reference CIS controls where applicable)
2. PRESERVE the original intent and functionality
3. GENERATE a secure version with these principles:
   - Least privilege (minimum permissions needed)
   - Defense in depth (multiple security layers)
   - Secure defaults (opt-in to risk, not opt-out)
4. EXPLAIN each change with:
   - What was changed
   - Why it was insecure
   - What attack it prevents
   - Any functional considerations

IMPORTANT: The fix must still work. Do not remove functionality —
harden it. If a capability is needed, find the most restrictive way
to grant it."""
```

## Step 3: Kubernetes Remediation Example

**Before (insecure):**
```yaml
spec:
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      privileged: true
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock
```

**After (remediated):**
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:1.2.3@sha256:abc123...  # Pinned
    securityContext:
      privileged: false
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    resources:
      limits:
        memory: "256Mi"
        cpu: "500m"
      requests:
        memory: "128Mi"
        cpu: "250m"
```

**Change Report:**
```
1. Removed privileged: true → Prevents container escape to host
2. Added runAsNonRoot: true → Blocks root execution even if image uses root
3. Pinned image tag + digest → Prevents supply chain substitution
4. Removed Docker socket mount → Eliminates node compromise path
5. Added resource limits → Prevents resource exhaustion attacks
6. Set readOnlyRootFilesystem → Prevents write-based persistence
7. Dropped ALL capabilities → Minimum privilege for container runtime
```

## Step 4: Terraform Remediation

The engine also fixes Terraform configurations:

**Before:**
```hcl
resource "aws_s3_bucket" "data" {
  bucket = "my-public-data"
  acl    = "public-read"
}
```

**After:**
```hcl
resource "aws_s3_bucket" "data" {
  bucket = "my-public-data"
  # Removed public-read ACL — use bucket policy for controlled access
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}
```

## Step 5: Dockerfile Remediation

**Before:**
```dockerfile
FROM python:latest
COPY . /app
RUN pip install -r /app/requirements.txt
ENV DATABASE_PASSWORD=mysecretpassword
CMD ["python", "/app/main.py"]
```

**After:**
```dockerfile
FROM python:3.12-slim@sha256:abc123... AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim@sha256:abc123...
RUN addgroup --system app && adduser --system --ingroup app appuser
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --chown=appuser:app . .
USER appuser
HEALTHCHECK --interval=30s --timeout=3s CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"]
CMD ["python", "main.py"]
# NOTE: DATABASE_PASSWORD should be injected via runtime secrets (Docker secrets, K8s secrets, or vault)
```

## Step 6: Batch Remediation

For real-world use, process entire directories:

```python
# Process all manifests in a directory
import os
for filename in os.listdir("manifests/"):
    if filename.endswith(('.yaml', '.yml', '.tf', 'Dockerfile')):
        remediate_file(os.path.join("manifests/", filename))
```

---

## What Success Looks Like

After running `task6_remediation.py`:

```
═══════════════════════════════════════════════════════════════════
   TASK 6: AI-Powered Security Remediation Engine
═══════════════════════════════════════════════════════════════════

Remediating: insecure-deployment.yaml
─────────────────────────────────────────────────────────────────
Issues Found: 8
Fixes Applied: 8
[Generated secure Kubernetes manifest with change explanations]

Remediating: insecure-terraform.tf
─────────────────────────────────────────────────────────────────
Issues Found: 6
Fixes Applied: 6
[Generated secure Terraform with change explanations]

Remediating: insecure-dockerfile
─────────────────────────────────────────────────────────────────
Issues Found: 7
Fixes Applied: 7
[Generated secure Dockerfile with change explanations]

Summary: 21 issues remediated across 3 files
All fixes preserve original functionality while hardening security.

Key Learning: AI remediation generates complete, working fixes —
not just suggestions. By understanding intent, it hardens security
without breaking the deployment.

Next: Review all fixes and apply to your own infrastructure!
```

---

## Key Takeaway

AI-powered remediation closes the loop on security scanning. Instead of handing developers a list of problems to research and fix individually, the AI generates complete, working, secure versions of their manifests with explanations for every change. This reduces mean-time-to-remediate from days to minutes while educating developers on *why* each security control matters.

---

**Congratulations!** You have completed Episode 11. You now have the skills to:
- Generate secure IaC from natural language
- Review existing infrastructure for security issues
- Scan Kubernetes manifests against security standards
- Audit Dockerfiles for vulnerabilities
- Validate compliance against CIS benchmarks
- Auto-remediate findings with AI-generated fixes
