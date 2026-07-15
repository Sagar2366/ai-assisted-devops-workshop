# Lab 4: Dockerfile Security Scanner

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut | Docker Captain

> **Mission:** Build an AI-powered Dockerfile auditor that detects security vulnerabilities including running as root, embedded secrets, unversioned base images, unnecessary packages, and inefficient layer ordering.

---

## Concepts

### Why Dockerfiles Are Security-Critical

A Dockerfile is the DNA of your container. Every instruction shapes the attack surface:

```
FROM ubuntu:latest        ← Unpinned base = supply chain risk
RUN apt-get install -y *  ← Attack surface expansion
COPY . /app              ← May include secrets, .git, etc.
USER root                ← Container runs with maximum privileges
```

### The Container Security Pyramid

Think of container security like building a house — the foundation (base image) determines everything above:

| Level | Control | Risk if Missing |
|-------|---------|-----------------|
| Base Image | Pinned, minimal, scanned | Supply chain attacks, known CVEs |
| Build Process | Multi-stage, no secrets | Credential leakage, bloated images |
| Runtime User | Non-root, read-only FS | Privilege escalation, persistence |
| Layer Hygiene | Minimal packages, clean | Expanded attack surface |

### Common CVE Patterns in Dockerfiles

| Pattern | Risk | CVE Example |
|---------|------|-------------|
| `FROM node:latest` | Unpatched vulnerabilities | CVE-2024-22019 (Node.js) |
| `RUN curl \| bash` | Remote code execution | Supply chain injection |
| `ENV API_KEY=secret` | Credential exposure | Visible in image layers |
| `COPY . /app` | Secret leakage | .env, .git/config in image |

---

## Step 1: Examine the Insecure Dockerfile

```bash
cat demos/sample-manifests/insecure-dockerfile
```

This Dockerfile contains intentional security issues:
- Uses `latest` tag for base image
- Runs as root
- Contains hardcoded secrets/credentials
- Installs unnecessary packages
- Has no health check
- Poor layer ordering (cache busting)
- No `.dockerignore` awareness

## Step 2: Run the Scanner

```bash
cd demos
python3 task4_dockerfile_scanner.py
```

## Step 3: Understanding the Analysis Categories

### Supply Chain Security

```python
SUPPLY_CHAIN_CHECKS = """
- Is the base image pinned by digest (sha256)?
- Is the base image from a trusted registry?
- Are multi-stage builds used to minimize final image?
- Are package versions pinned in apt-get/apk/pip?
- Is there a COPY --from pattern from verified builder stages?
"""
```

### Secrets Detection

```python
SECRETS_CHECKS = """
- ENV instructions containing passwords, tokens, API keys
- COPY of files that commonly contain secrets (.env, credentials)
- ARG with default values for sensitive data
- RUN commands that fetch secrets (curl to vault without cleanup)
- Any base64-encoded strings that decode to credentials
"""
```

### Runtime Security

```python
RUNTIME_CHECKS = """
- Does the container run as non-root? (USER instruction)
- Is HEALTHCHECK defined?
- Are unnecessary capabilities likely required?
- Is the filesystem read-only compatible?
- Are ports exposed appropriately (not 0.0.0.0)?
"""
```

## Step 4: Layer Analysis

The AI understands Docker's layer caching and can identify:

```dockerfile
# BAD: Cache-busting order
COPY . /app                  # Any file change invalidates cache
RUN pip install -r requirements.txt  # Reinstalls everything

# GOOD: Cache-optimized order  
COPY requirements.txt /app/  # Only changes when deps change
RUN pip install -r requirements.txt
COPY . /app                  # App changes don't rebuild deps
```

## Step 5: Multi-Stage Build Analysis

The scanner evaluates whether multi-stage builds are used correctly:

```dockerfile
# AI detects: Build tools leaked into production image
FROM golang:1.22 AS builder
RUN go build -o /app

FROM ubuntu:22.04  # Should be distroless/scratch
COPY --from=builder /app /app
# Missing: RUN apt-get purge build-essential
```

## Step 6: Remediation Suggestions

For each finding, the AI provides a specific fix:

```
Finding: Running as root (no USER instruction)
Severity: HIGH
Fix:
  # Add before CMD/ENTRYPOINT:
  RUN addgroup --system appgroup && \
      adduser --system --ingroup appgroup appuser
  USER appuser:appgroup
```

---

## What Success Looks Like

After running `task4_dockerfile_scanner.py`:

```
═══════════════════════════════════════════════════════════════════
   TASK 4: Dockerfile Security Auditor
═══════════════════════════════════════════════════════════════════

Scanning: demos/sample-manifests/insecure-dockerfile
─────────────────────────────────────────────────────────────────

[CRITICAL] Hardcoded secrets in ENV instructions (credential exposure)
[CRITICAL] Base image uses 'latest' tag (supply chain risk)
[HIGH] Container runs as root (no USER instruction)
[HIGH] COPY includes potential secret files (.env pattern)
[MEDIUM] No HEALTHCHECK instruction defined
[MEDIUM] Unnecessary packages installed (build tools in runtime)
[MEDIUM] Package manager cache not cleaned (bloated image)
[LOW] Suboptimal layer ordering (poor cache utilization)
[LOW] No .dockerignore file referenced

Image Security Score: 2/10 (Critical Issues Present)

Key Learning: Dockerfiles define the entire container attack surface.
AI scanning catches not just syntax issues but semantic problems like
secrets that persist across layers and supply chain risks.

Next: Lab 5 — Check against CIS Kubernetes benchmarks
```

---

## Key Takeaway

Dockerfile security extends beyond "don't run as root." AI-powered scanning understands the semantic meaning of instructions — it can identify that a `COPY` might include secrets, that layer ordering affects both security and performance, and that the choice of base image cascades into hundreds of potential CVEs. Catching these issues before `docker build` prevents vulnerabilities from ever reaching production.

---

**Next:** [Lab 5 — Compliance Checker](lab5-compliance-checker.md) — Validate infrastructure against CIS Kubernetes Benchmark controls.
