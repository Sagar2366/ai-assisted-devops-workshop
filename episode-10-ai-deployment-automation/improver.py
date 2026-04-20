"""
Episode 10: AI-Powered Deployment Automation
Tool: AI Manifest Improvement Scanner

Reads existing K8s manifests and suggests production-readiness improvements.
Scores on 5 dimensions: Reliability, Security, Observability, Resource Management, Rollout Safety.

Author: Sagar Utekar
Prerequisites:
    - Anthropic API key (set ANTHROPIC_API_KEY env var)
    - pip install anthropic
    - K8s manifest files to scan (or use the built-in minimal manifest demo)
"""
import anthropic
import os
import json

client = anthropic.Anthropic()

IMPROVER_SYSTEM = """You are a Kubernetes deployment expert reviewing manifests for production readiness.

## Check these categories and score each 1-5:

### 1. Reliability (health checks, replicas, PDB, anti-affinity)
### 2. Security (non-root, read-only fs, capabilities, network policy)
### 3. Observability (labels, annotations, resource names)
### 4. Resource Management (requests, limits, HPA, VPA)
### 5. Rollout Safety (strategy, PDB, preStop hook, terminationGracePeriod)

## For EACH issue found:
- Category
- Severity: CRITICAL / WARNING / INFO
- What is missing or wrong
- The EXACT YAML to add or change (not just a description -- show the actual fix)

## Output format:
### Scorecard
| Category | Score | Issues |
|----------|-------|--------|
(table)

### Overall: X/25 — PRODUCTION READY / NEEDS WORK / NOT READY

### Improvements
(numbered list with YAML snippets)"""


def improve_manifests(manifest_path: str) -> str:
    """Review K8s manifests and suggest improvements."""

    if os.path.isfile(manifest_path):
        with open(manifest_path) as f:
            content = f.read()
        manifests_text = f"### {manifest_path}\n```yaml\n{content}\n```"
    else:
        manifests_text = ""
        for fname in os.listdir(manifest_path):
            if fname.endswith((".yaml", ".yml")):
                fpath = os.path.join(manifest_path, fname)
                with open(fpath) as f:
                    content = f.read()
                manifests_text += f"\n### {fname}\n```yaml\n{content}\n```\n"

    if not manifests_text:
        return "No YAML files found."

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": IMPROVER_SYSTEM,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{
            "role": "user",
            "content": f"Review these Kubernetes manifests and suggest improvements:\n\n{manifests_text}"
        }]
    )

    return response.content[0].text


# A deliberately minimal manifest for the demo
MINIMAL_MANIFEST = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
      - name: api
        image: mycompany/api-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          value: "postgresql://admin:password123@db:5432/myapp"
"""

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(f"Scanning: {path}\n")
        result = improve_manifests(path)
    else:
        # Demo with the minimal manifest
        print("Scanning minimal manifest for improvements...\n")

        # Write the minimal manifest to a temp file
        temp_path = "/tmp/minimal-deployment.yaml"
        with open(temp_path, "w") as f:
            f.write(MINIMAL_MANIFEST)

        result = improve_manifests(temp_path)

    print(result)
