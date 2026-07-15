#!/usr/bin/env python3
"""
AI Kubernetes Manifest Generator - Episode 12, Task 3
=====================================================
Uses Claude to generate production-ready Kubernetes manifests including
Deployment, Service, HPA, and Ingress resources.

Author: Sagar Utekar | CNCF Ambassador | Kubestronaut
"""

import os
import sys
import json
import re
import anthropic

print("=" * 65)
print("  AI KUBERNETES MANIFEST GENERATOR")
print("  Episode 12: AI-Powered Deployment Automation")
print("=" * 65)


# =============================================================================
# Configuration
# =============================================================================

SAMPLE_APPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample-apps")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
MODEL = "claude-sonnet-4-20250514"


# =============================================================================
# Application Analyzer (from Task 1)
# =============================================================================

def read_app_files(app_dir):
    """Read dependency and source files from an application directory."""
    files = {}
    target_files = [
        "requirements.txt", "package.json", "go.mod",
        "app.py", "main.py", "app.js", "index.js", "main.go",
    ]
    for filename in target_files:
        filepath = os.path.join(app_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                files[filename] = f.read()
    return files


def analyze_application(app_dir):
    """Analyze application and return deployment profile."""
    client = anthropic.Anthropic()
    files = read_app_files(app_dir)
    if not files:
        return None

    file_contents = ""
    for name, content in files.items():
        file_contents += f"\n--- {name} ---\n{content}\n"

    prompt = f"""Analyze the following application files and produce a deployment profile as JSON.

{file_contents}

Return a JSON object with these fields:
- "runtime": the language (python, node, go)
- "runtime_version": recommended version string
- "framework": the web framework used
- "port": integer port the app listens on
- "dependencies": list of key dependency names
- "env_vars": list of environment variable names needed
- "health_endpoint": health check path or "/health"
- "build_command": command to install dependencies
- "start_command": command to start the application in production
- "needs_database": boolean
- "database_type": type if applicable or null

Return ONLY the JSON object, no markdown fences, no explanation."""

    message = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text
    json_match = re.search(r"\{[\s\S]*\}", response_text)
    if json_match:
        return json.loads(json_match.group())
    return None


# =============================================================================
# Kubernetes Manifest Generation
# =============================================================================

def build_k8s_prompt(profile, app_name, namespace="production"):
    """Create a prompt for generating Kubernetes manifests."""
    return f"""Generate production-ready Kubernetes manifests for this application.

Application Name: {app_name}
Namespace: {namespace}
Container Image: {app_name}:latest
Application Profile:
{json.dumps(profile, indent=2)}

Generate the following resources as a single YAML document (separated by ---):

1. **Namespace** resource for '{namespace}'
2. **Deployment** with:
   - 2 replicas
   - Resource requests: cpu=100m, memory=128Mi
   - Resource limits: cpu=500m, memory=512Mi
   - Liveness probe on the health_endpoint with initialDelaySeconds=10
   - Readiness probe on the health_endpoint with initialDelaySeconds=5
   - Pod anti-affinity (preferred) for spreading across nodes
   - Labels: app={app_name}, version="1.0.0", managed-by=ai-deployment
   - Environment variables from the profile
   - For sensitive env vars, reference a Secret named {app_name}-secrets
3. **Service** (ClusterIP) mapping port 80 to the container port
4. **HorizontalPodAutoscaler** (autoscaling/v2):
   - Min replicas: 2
   - Max replicas: 10
   - Target CPU utilization: 70%
5. **Ingress** (networking.k8s.io/v1):
   - Host: {app_name}.example.com
   - TLS with secret {app_name}-tls
   - Annotations for nginx ingress controller and cert-manager

Return ONLY the YAML content. No markdown fences, no explanation text."""


def generate_k8s_manifests(profile, app_name, namespace="production"):
    """Use Claude to generate Kubernetes manifests."""
    client = anthropic.Anthropic()
    prompt = build_k8s_prompt(profile, app_name, namespace)

    message = client.messages.create(
        model=MODEL,
        max_tokens=5000,
        messages=[{"role": "user", "content": prompt}],
    )

    manifests = message.content[0].text

    # Strip markdown code fences if present
    if manifests.strip().startswith("```"):
        lines = manifests.strip().split("\n")
        if lines[-1].strip() == "```":
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        manifests = "\n".join(lines)

    return manifests


def save_manifests(content, output_path):
    """Save the generated manifests to disk."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(content)
    return output_path


# =============================================================================
# Main Execution
# =============================================================================

if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n  ERROR: ANTHROPIC_API_KEY environment variable not set.")
        print("  Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Experiment 1: Python App K8s Manifests
    print(f"\n{'-' * 65}")
    print("  EXPERIMENT 1: K8s Manifests for Python Flask App")
    print(f"{'-' * 65}")

    python_app_dir = os.path.join(SAMPLE_APPS_DIR, "python-app")
    print(f"\n  [1/3] Analyzing python-app...")
    python_profile = analyze_application(python_app_dir)

    if python_profile:
        print(f"  [2/3] Generating Kubernetes manifests...")
        python_manifests = generate_k8s_manifests(
            python_profile, "python-flask-app", "production"
        )

        output_path = os.path.join(OUTPUT_DIR, "python-app", "k8s", "manifests.yaml")
        save_manifests(python_manifests, output_path)
        print(f"  [3/3] Saved to: {output_path}")

        print(f"\n  Generated Manifests:")
        print(f"  {'.' * 50}")
        for line in python_manifests.split("\n")[:40]:
            print(f"  | {line}")
        if python_manifests.count("\n") > 40:
            print(f"  | ... ({python_manifests.count(chr(10)) - 40} more lines)")
        print(f"  {'.' * 50}")

    # Experiment 2: Node App K8s Manifests
    print(f"\n{'-' * 65}")
    print("  EXPERIMENT 2: K8s Manifests for Node.js Express App")
    print(f"{'-' * 65}")

    node_app_dir = os.path.join(SAMPLE_APPS_DIR, "node-app")
    print(f"\n  [1/3] Analyzing node-app...")
    node_profile = analyze_application(node_app_dir)

    if node_profile:
        print(f"  [2/3] Generating Kubernetes manifests...")
        node_manifests = generate_k8s_manifests(
            node_profile, "node-express-app", "production"
        )

        output_path = os.path.join(OUTPUT_DIR, "node-app", "k8s", "manifests.yaml")
        save_manifests(node_manifests, output_path)
        print(f"  [3/3] Saved to: {output_path}")

        print(f"\n  Generated Manifests:")
        print(f"  {'.' * 50}")
        for line in node_manifests.split("\n")[:40]:
            print(f"  | {line}")
        if node_manifests.count("\n") > 40:
            print(f"  | ... ({node_manifests.count(chr(10)) - 40} more lines)")
        print(f"  {'.' * 50}")

    # Summary
    print(f"\n{'=' * 65}")
    print("  KUBERNETES MANIFEST GENERATION COMPLETE")
    print(f"{'=' * 65}")
    print(f"\n  Generated Resources (per app):")
    print(f"  ├── Namespace")
    print(f"  ├── Deployment (2 replicas, resource limits, probes)")
    print(f"  ├── Service (ClusterIP, port 80 -> app port)")
    print(f"  ├── HorizontalPodAutoscaler (2-10 replicas, 70% CPU)")
    print(f"  └── Ingress (TLS, nginx controller)")

    print(f"\n  Key Learning:")
    print(f"  AI-generated K8s manifests encode production best practices:")
    print(f"  resource limits, health probes, autoscaling, and anti-affinity.")
    print(f"  Each manifest is tailored to the application's specific needs.")

    print(f"\n  Next: task4_compose_generator.py")
    print(f"{'=' * 65}")
