#!/usr/bin/env python3
"""
Task 4: Dockerfile Security Auditor

Uses Claude AI to audit Dockerfiles for security vulnerabilities including
running as root, embedded secrets, unversioned base images, unnecessary
packages, and inefficient layer ordering.

Episode 11 - AI-Assisted DevOps Workshop
Author: Sagar Utekar | CNCF Ambassador | Kubestronaut
"""

import os
import anthropic


def print_header():
    print("=" * 65)
    print("   TASK 4: Dockerfile Security Auditor")
    print("=" * 65)
    print()


DOCKERFILE_SECURITY_PROMPT = """You are a container security expert specializing in
Dockerfile analysis. You have deep knowledge of:

- Docker build best practices and layer optimization
- Container runtime security principles
- Supply chain security (base images, registries, signatures)
- Common CVEs in popular base images
- CIS Docker Benchmark v1.6
- Secrets management in container builds
- Multi-stage build patterns for minimal attack surface

When auditing Dockerfiles, evaluate these categories:

1. BASE IMAGE SECURITY:
   - Is the image pinned by tag AND digest (sha256)?
   - Is it from a trusted/official registry?
   - Is it a minimal image (alpine, distroless, scratch)?
   - Are there known CVEs in the base image version?

2. SECRETS AND CREDENTIALS:
   - ENV instructions with passwords, tokens, API keys
   - ARG with sensitive default values
   - COPY of files likely containing secrets (.env, credentials, keys)
   - Secrets in RUN commands (curl with auth headers)
   - Secrets persisted across layers

3. USER AND PERMISSIONS:
   - Does the container run as non-root? (USER instruction)
   - Are file permissions correctly set?
   - Is SUID/SGID risk minimized?

4. ATTACK SURFACE:
   - Are unnecessary packages installed?
   - Are build tools present in the final image?
   - Is multi-stage build used to minimize image?
   - Are unnecessary ports exposed?
   - Is apt/apk cache cleaned?

5. SUPPLY CHAIN:
   - Are package versions pinned?
   - Is there curl|bash pattern (remote code execution)?
   - Are packages from trusted repositories?

6. RUNTIME SECURITY:
   - Is HEALTHCHECK defined?
   - Is the filesystem read-only compatible?
   - Are volumes used for mutable data?

7. LAYER OPTIMIZATION:
   - Is layer ordering cache-friendly?
   - Are multi-line RUN commands consolidated?
   - Is .dockerignore referenced/needed?

Format findings as:
[SEVERITY] Title
Line: <line number or instruction>
Risk: <specific attack vector or vulnerability>
Fix: <corrected Dockerfile instruction>

Provide an overall Image Security Score (1-10, where 10 is most secure).
"""


def load_dockerfile(filepath: str) -> str:
    """Load a Dockerfile for analysis."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)
    with open(full_path, "r") as f:
        return f.read()


def scan_dockerfile(dockerfile_content: str, context: str = "") -> str:
    """Scan a Dockerfile for security vulnerabilities."""
    client = anthropic.Anthropic()

    scan_prompt = f"""Perform a comprehensive security audit of this Dockerfile.

Analyze every instruction for security implications. Consider:
- What attack surface does each instruction create?
- Are there secrets that will persist in image layers?
- Can an attacker leverage this image for privilege escalation?
- Is the build process vulnerable to supply chain attacks?

{f"Context: {context}" if context else ""}

For each finding, provide:
- Severity (CRITICAL, HIGH, MEDIUM, LOW)
- The specific line/instruction that is problematic
- The attack vector or vulnerability it creates
- A corrected version of the instruction

After all findings, provide:
- Image Security Score (1-10)
- The top 3 most impactful fixes
- A recommended secure version of the complete Dockerfile

Dockerfile to audit:
```dockerfile
{dockerfile_content}
```"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=DOCKERFILE_SECURITY_PROMPT,
        messages=[
            {"role": "user", "content": scan_prompt}
        ]
    )

    return message.content[0].text


def run_experiments():
    """Run Dockerfile security scanning experiments."""

    # Experiment 1: Scan the insecure Dockerfile
    print("Experiment 1: Full Security Audit of Insecure Dockerfile")
    print("-" * 65)

    try:
        dockerfile_content = load_dockerfile(
            "sample-manifests/insecure-dockerfile"
        )
        print(f"Loaded Dockerfile ({len(dockerfile_content)} bytes)")
        print("Sending to AI for security audit...")
        print()

        result = scan_dockerfile(dockerfile_content)
        print(result)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Ensure sample-manifests/insecure-dockerfile exists")
    except anthropic.APIError as e:
        print(f"API Error: {e}")

    print()
    print()

    # Experiment 2: Multi-stage build with leaked build secrets
    print("Experiment 2: Multi-Stage Build with Leaked Secrets")
    print("-" * 65)

    multistage_dockerfile = """FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./

# Private NPM registry auth
ARG NPM_TOKEN=npm_defaulttoken123
RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc
RUN npm ci
RUN rm .npmrc

COPY . .
RUN npm run build

FROM node:18-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

EXPOSE 3000
CMD ["node", "dist/server.js"]
"""

    try:
        print("Scanning multi-stage Dockerfile for subtle security issues...")
        print()
        result = scan_dockerfile(
            multistage_dockerfile,
            context="Node.js API service using private NPM packages"
        )
        print(result)
    except anthropic.APIError as e:
        print(f"API Error: {e}")

    print()
    print()

    # Experiment 3: Python ML application
    print("Experiment 3: Data Science Dockerfile Analysis")
    print("-" * 65)

    ml_dockerfile = """FROM nvidia/cuda:12.0-devel-ubuntu22.04

RUN apt-get update && apt-get install -y \\
    python3.11 python3-pip git wget curl \\
    libgl1-mesa-glx libglib2.0-0

RUN pip install --upgrade pip
RUN pip install torch torchvision numpy pandas scikit-learn \\
    jupyter notebook flask gunicorn transformers datasets

COPY . /workspace
WORKDIR /workspace

# Download pre-trained model weights
RUN wget https://huggingface.co/models/weights.bin -O /workspace/models/weights.bin

# Jupyter config with no auth
RUN jupyter notebook --generate-config && \\
    echo "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py && \\
    echo "c.NotebookApp.password = ''" >> /root/.jupyter/jupyter_notebook_config.py

EXPOSE 8888 5000

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root"]
"""

    try:
        print("Scanning ML/Data Science Dockerfile for security issues...")
        print()
        result = scan_dockerfile(
            ml_dockerfile,
            context="Internal ML platform for model training and inference"
        )
        print(result)
    except anthropic.APIError as e:
        print(f"API Error: {e}")


def main():
    print_header()

    print("This demo audits Dockerfiles for security vulnerabilities including")
    print("embedded secrets, running as root, supply chain risks, and attack")
    print("surface expansion through unnecessary packages.")
    print()

    run_experiments()

    print()
    print("=" * 65)
    print()
    print("Key Learning: Dockerfiles define the entire container attack surface.")
    print("AI scanning catches not just syntax issues but semantic problems like")
    print("secrets that persist across layers, supply chain risks from unverified")
    print("downloads, and authentication bypasses in service configurations.")
    print()
    print("Next: Run task5_compliance_checker.py to validate against CIS")
    print("      Kubernetes Benchmark controls.")


if __name__ == "__main__":
    main()
