"""
Episode 10: AI-Powered Deployment Automation
Tool: AI Deployment Artifact Triple Generator

One app analysis -> Dockerfile + K8s manifests + docker-compose.yml
All consistent, all generated from the same application analysis.

Author: Sagar Utekar
Prerequisites:
    - Anthropic API key (set ANTHROPIC_API_KEY env var)
    - pip install anthropic
    - analyzer.py (from this episode) in the same directory or on PYTHONPATH
    - An application directory to analyze (or use the built-in sample app from analyzer.py)
"""
import anthropic
import os
import json

client = anthropic.Anthropic()


def generate_dockerfile(app_analysis: dict, app_dir: str) -> str:
    """Generate an optimized, multi-stage Dockerfile."""

    # Read requirements.txt if it exists
    requirements = ""
    req_path = os.path.join(app_dir, "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path) as f:
            requirements = f.read()

    # Read the main app file
    app_code = ""
    for fname in ["app.py", "main.py", "server.py"]:
        fpath = os.path.join(app_dir, fname)
        if os.path.exists(fpath):
            with open(fpath) as f:
                app_code = f.read()
            break

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system="""You generate production-ready Dockerfiles. Follow these rules:

## Multi-stage build (mandatory):
- Stage 1: builder — install dependencies
- Stage 2: runtime — copy only what is needed

## Security (mandatory):
- Use specific version tags, never :latest
- Run as non-root user (create appuser with UID 1000)
- No secrets in the image
- Minimize layers
- Use COPY, not ADD (unless extracting archives)

## Performance:
- Copy requirements.txt FIRST, then app code (layer caching)
- Use .dockerignore patterns in comments
- Use slim or alpine base images

## Health check:
- Add HEALTHCHECK instruction matching the app's health endpoint

Output ONLY the Dockerfile content. No explanations outside the file.""",
        messages=[{
            "role": "user",
            "content": f"""Generate a Dockerfile for this app:

Framework: {app_analysis.get('framework', 'Flask')}
Port: {app_analysis.get('port', 5000)}
Dependencies: {requirements}
App code: {app_code[:2000]}"""
        }]
    )

    result = response.content[0].text

    # Strip markdown code fences if present
    if result.startswith("```"):
        lines = result.split("\n")
        result = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    return result


def generate_k8s_manifests(app_analysis: dict) -> str:
    """Generate Kubernetes Deployment + Service + Ingress."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": """You generate production-ready Kubernetes manifests. Generate ALL of these in a single YAML file separated by ---:

## 1. Deployment:
- 2 replicas minimum
- Rolling update strategy (maxSurge: 1, maxUnavailable: 0)
- Resource requests AND limits
- Liveness probe (checks /health or app-appropriate endpoint)
- Readiness probe (same or different path)
- Security context: runAsNonRoot, readOnlyRootFilesystem, drop ALL capabilities
- Pod anti-affinity (prefer spreading across nodes)
- Environment variables from ConfigMap and Secret references (not hardcoded)

## 2. Service:
- ClusterIP type (default)
- Correct port mapping

## 3. Ingress:
- nginx ingress class
- TLS placeholder
- Path-based routing

## 4. ConfigMap:
- Non-sensitive configuration values

## 5. HorizontalPodAutoscaler:
- CPU target 70%
- Min 2, Max 10

Output ONLY the YAML. No explanations outside the manifests.
Use the app name as the base for all resource names.""",
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{
            "role": "user",
            "content": f"""Generate K8s manifests for:
App name: {app_analysis.get('app_name', 'sample-api')}
Framework: {app_analysis.get('framework', 'Flask')}
Port: {app_analysis.get('port', 5000)}
Has database: {app_analysis.get('has_database', False)}
Dependencies: {json.dumps(app_analysis.get('dependencies', []))}"""
        }]
    )

    result = response.content[0].text
    if result.startswith("```"):
        lines = result.split("\n")
        result = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    return result


def generate_docker_compose(app_analysis: dict) -> str:
    """Generate docker-compose.yml for local development."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system="""You generate docker-compose.yml files for local development.

## Rules:
- Use version '3.8' or later compose spec
- Include the app service + all dependencies (Redis, Postgres, etc.)
- Mount source code as a volume for hot reload
- Use .env file for configuration (include .env.example in comments)
- Add health checks for all services
- Use named volumes for persistent data
- Include a docker-compose.override.yml suggestion for dev-specific settings
- Expose ports only on localhost (127.0.0.1:port:port)

Output ONLY the docker-compose.yml content. No explanations outside the file.""",
        messages=[{
            "role": "user",
            "content": f"""Generate docker-compose.yml for local development:
App name: {app_analysis.get('app_name', 'sample-api')}
Framework: {app_analysis.get('framework', 'Flask')}
Port: {app_analysis.get('port', 5000)}
Has database: {app_analysis.get('has_database', False)}
Dependencies: {json.dumps(app_analysis.get('dependencies', []))}"""
        }]
    )

    result = response.content[0].text
    if result.startswith("```"):
        lines = result.split("\n")
        result = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    return result


def generate_all(app_dir: str, output_dir: str = "generated"):
    """Generate all deployment artifacts for an app."""

    # First, analyze the app
    from analyzer import analyze_app
    print("Step 1: Analyzing application...")
    analysis = analyze_app(app_dir)

    if "error" in analysis:
        print(f"Error: {analysis['error']}")
        return

    print(f"  Framework: {analysis.get('framework', 'unknown')}")
    print(f"  Port: {analysis.get('port', 'unknown')}")
    print(f"  Recommended target: {analysis.get('recommended_target', 'unknown')}")

    os.makedirs(output_dir, exist_ok=True)

    # Generate Dockerfile
    print("\nStep 2: Generating Dockerfile...")
    dockerfile = generate_dockerfile(analysis, app_dir)
    dockerfile_path = os.path.join(output_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile)
    print(f"  Created: {dockerfile_path}")

    # Generate K8s manifests
    print("\nStep 3: Generating Kubernetes manifests...")
    k8s_manifests = generate_k8s_manifests(analysis)
    k8s_path = os.path.join(output_dir, "k8s-manifests.yaml")
    with open(k8s_path, "w") as f:
        f.write(k8s_manifests)
    print(f"  Created: {k8s_path}")

    # Generate docker-compose
    print("\nStep 4: Generating docker-compose.yml...")
    compose = generate_docker_compose(analysis)
    compose_path = os.path.join(output_dir, "docker-compose.yml")
    with open(compose_path, "w") as f:
        f.write(compose)
    print(f"  Created: {compose_path}")

    # Print summary
    print(f"""
{'='*60}
DEPLOYMENT ARTIFACTS GENERATED
{'='*60}
App: {analysis.get('app_name', 'sample-api')}
Framework: {analysis.get('framework', 'unknown')}
Output directory: {output_dir}/

Files created:
  1. Dockerfile          — Multi-stage build, non-root, health check
  2. k8s-manifests.yaml  — Deployment + Service + Ingress + HPA
  3. docker-compose.yml  — Local dev with all dependencies

Next steps:
  docker build -t {analysis.get('app_name', 'sample-api')}:latest -f {dockerfile_path} {app_dir}
  docker compose -f {compose_path} up
  kubectl apply -f {k8s_path}
{'='*60}
""")

    return {
        "analysis": analysis,
        "dockerfile": dockerfile,
        "k8s_manifests": k8s_manifests,
        "docker_compose": compose
    }


if __name__ == "__main__":
    import sys
    app_dir = sys.argv[1] if len(sys.argv) > 1 else "sample_app"
    generate_all(app_dir)
