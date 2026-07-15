#!/usr/bin/env python3
"""
AI Full Deployment Pipeline - Episode 12, Task 5
=================================================
Orchestrates the complete AI deployment automation pipeline: analyze
application source code, then generate all deployment artifacts in one pass.

Author: Sagar Utekar | CNCF Ambassador | Kubestronaut
"""

import os
import sys
import json
import re
import time
import anthropic

print("=" * 65)
print("  AI FULL DEPLOYMENT PIPELINE")
print("  Episode 12: AI-Powered Deployment Automation")
print("=" * 65)


# =============================================================================
# Configuration
# =============================================================================

SAMPLE_APPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample-apps")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
MODEL = "claude-sonnet-4-20250514"


# =============================================================================
# Pipeline Components
# =============================================================================

class DeploymentPipeline:
    """Orchestrates the full AI deployment automation pipeline."""

    def __init__(self, app_dir, app_name, namespace="production", domain="example.com"):
        self.app_dir = app_dir
        self.app_name = app_name
        self.namespace = namespace
        self.domain = domain
        self.client = anthropic.Anthropic()
        self.profile = None
        self.output_base = os.path.join(OUTPUT_DIR, app_name)
        self.artifacts = {}

    def run(self):
        """Execute the full deployment pipeline."""
        print(f"\n{'=' * 65}")
        print(f"  PIPELINE: {self.app_name}")
        print(f"  Source:    {self.app_dir}")
        print(f"  Output:    {self.output_base}/")
        print(f"{'=' * 65}")

        start_time = time.time()

        # Phase 1: Analyze
        print(f"\n  [1/5] Analyzing application...")
        self.profile = self._analyze()
        if not self.profile:
            print("  FAILED: Could not analyze application")
            return False

        print(f"         Runtime:   {self.profile.get('runtime')} {self.profile.get('runtime_version')}")
        print(f"         Framework: {self.profile.get('framework')}")
        print(f"         Port:      {self.profile.get('port')}")
        print(f"         Database:  {self.profile.get('database_type', 'none')}")

        # Save profile
        self._save("profile.json", json.dumps(self.profile, indent=2))

        # Phase 2: Dockerfile
        print(f"\n  [2/5] Generating Dockerfile...")
        dockerfile = self._generate_dockerfile()
        self._save("Dockerfile", dockerfile)
        self.artifacts["Dockerfile"] = len(dockerfile.split("\n"))

        # Phase 3: .dockerignore
        print(f"\n  [3/5] Generating .dockerignore...")
        dockerignore = self._generate_dockerignore()
        self._save(".dockerignore", dockerignore)
        self.artifacts[".dockerignore"] = len(dockerignore.split("\n"))

        # Phase 4: K8s manifests
        print(f"\n  [4/5] Generating Kubernetes manifests...")
        manifests = self._generate_k8s()
        self._save("k8s/manifests.yaml", manifests)
        self.artifacts["k8s/manifests.yaml"] = len(manifests.split("\n"))

        # Phase 5: Compose
        print(f"\n  [5/5] Generating docker-compose.yaml...")
        compose = self._generate_compose()
        self._save("docker-compose.yaml", compose)
        self.artifacts["docker-compose.yaml"] = len(compose.split("\n"))

        elapsed = time.time() - start_time
        self._print_summary(elapsed)
        return True

    def _read_app_files(self):
        """Read relevant application files."""
        files = {}
        target_files = [
            "requirements.txt", "package.json", "go.mod",
            "app.py", "main.py", "server.py",
            "app.js", "index.js", "server.js",
            "main.go", "Procfile",
        ]
        for filename in target_files:
            filepath = os.path.join(self.app_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    files[filename] = f.read()
        return files

    def _analyze(self):
        """Phase 1: Analyze the application."""
        files = self._read_app_files()
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

        message = self.client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if json_match:
            return json.loads(json_match.group())
        return None

    def _generate_dockerfile(self):
        """Phase 2: Generate multi-stage Dockerfile."""
        prompt = f"""Generate a production-ready, multi-stage Dockerfile for this application.

Application Name: {self.app_name}
Application Profile:
{json.dumps(self.profile, indent=2)}

Requirements:
1. Multi-stage build (builder + runtime)
2. Specific version tags (no 'latest')
3. Non-root user in runtime stage
4. HEALTHCHECK instruction
5. Minimize layers, leverage cache
6. LABEL instructions (maintainer, description, version)
7. Proper EXPOSE and CMD

Return ONLY the Dockerfile content. No markdown fences."""

        message = self.client.messages.create(
            model=MODEL,
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )

        content = message.content[0].text
        if content.strip().startswith("```"):
            lines = content.strip().split("\n")
            if lines[-1].strip() == "```":
                lines = lines[1:-1]
            else:
                lines = lines[1:]
            content = "\n".join(lines)
        return content

    def _generate_dockerignore(self):
        """Phase 3: Generate .dockerignore."""
        runtime = self.profile.get("runtime", "python")

        if runtime == "python":
            return """# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
.eggs/
venv/
.venv/
env/

# IDE
.vscode/
.idea/
*.swp

# Git
.git/
.gitignore

# Docker
Dockerfile
docker-compose*.yaml
.dockerignore

# Docs
*.md
LICENSE

# Tests
tests/
.pytest_cache/
.coverage
htmlcov/
"""
        elif runtime == "node":
            return """# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build
dist/
build/

# IDE
.vscode/
.idea/
*.swp

# Git
.git/
.gitignore

# Docker
Dockerfile
docker-compose*.yaml
.dockerignore

# Docs
*.md
LICENSE

# Tests
coverage/
.nyc_output/

# Environment
.env
.env.local
"""
        else:
            return """# General
.git/
.gitignore
*.md
LICENSE
Dockerfile
docker-compose*.yaml
.dockerignore
.vscode/
.idea/
"""

    def _generate_k8s(self):
        """Phase 4: Generate Kubernetes manifests."""
        prompt = f"""Generate production-ready Kubernetes manifests for this application.

Application Name: {self.app_name}
Namespace: {self.namespace}
Container Image: {self.app_name}:latest
Domain: {self.app_name}.{self.domain}
Application Profile:
{json.dumps(self.profile, indent=2)}

Generate these resources separated by ---:
1. Namespace
2. Deployment (2 replicas, resource limits, liveness/readiness probes, anti-affinity)
3. Service (ClusterIP, port 80 -> app port)
4. HorizontalPodAutoscaler (2-10 replicas, 70% CPU)
5. Ingress (TLS, nginx controller, cert-manager)

Labels: app={self.app_name}, version="1.0.0", managed-by=ai-deployment

Return ONLY the YAML. No markdown fences."""

        message = self.client.messages.create(
            model=MODEL,
            max_tokens=5000,
            messages=[{"role": "user", "content": prompt}],
        )

        content = message.content[0].text
        if content.strip().startswith("```"):
            lines = content.strip().split("\n")
            if lines[-1].strip() == "```":
                lines = lines[1:-1]
            else:
                lines = lines[1:]
            content = "\n".join(lines)
        return content

    def _generate_compose(self):
        """Phase 5: Generate docker-compose.yaml."""
        prompt = f"""Generate a docker-compose.yaml for local development.

Application Name: {self.app_name}
Application Profile:
{json.dumps(self.profile, indent=2)}

Requirements:
1. Version "3.8"
2. App service: build context, port mapping, volume mounts for live reload, env vars, healthcheck
3. Database service if needed (based on database_type), with healthcheck and named volume
4. Custom bridge network
5. depends_on with condition: service_healthy
6. Comments explaining sections

Return ONLY the YAML. No markdown fences."""

        message = self.client.messages.create(
            model=MODEL,
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )

        content = message.content[0].text
        if content.strip().startswith("```"):
            lines = content.strip().split("\n")
            if lines[-1].strip() == "```":
                lines = lines[1:-1]
            else:
                lines = lines[1:]
            content = "\n".join(lines)
        return content

    def _save(self, filename, content):
        """Save an artifact to the output directory."""
        path = os.path.join(self.output_base, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        print(f"         Saved: {path}")

    def _print_summary(self, elapsed):
        """Print pipeline summary."""
        print(f"\n{'=' * 65}")
        print(f"  PIPELINE COMPLETE: {self.app_name}")
        print(f"{'=' * 65}")
        print(f"\n  Time elapsed: {elapsed:.1f}s")
        print(f"\n  Generated artifacts:")
        for artifact, lines in self.artifacts.items():
            print(f"    {artifact:30s} ({lines} lines)")
        print(f"\n  Output directory: {self.output_base}/")
        print(f"  ├── profile.json")
        print(f"  ├── Dockerfile")
        print(f"  ├── .dockerignore")
        print(f"  ├── docker-compose.yaml")
        print(f"  └── k8s/")
        print(f"      └── manifests.yaml")


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

    # Pipeline 1: Python Flask App
    print(f"\n{'-' * 65}")
    print("  EXPERIMENT 1: Full Pipeline for Python Flask App")
    print(f"{'-' * 65}")

    pipeline1 = DeploymentPipeline(
        app_dir=os.path.join(SAMPLE_APPS_DIR, "python-app"),
        app_name="python-flask-app",
        namespace="production",
        domain="mycompany.com",
    )
    pipeline1.run()

    # Pipeline 2: Node Express App
    print(f"\n{'-' * 65}")
    print("  EXPERIMENT 2: Full Pipeline for Node.js Express App")
    print(f"{'-' * 65}")

    pipeline2 = DeploymentPipeline(
        app_dir=os.path.join(SAMPLE_APPS_DIR, "node-app"),
        app_name="node-express-app",
        namespace="production",
        domain="mycompany.com",
    )
    pipeline2.run()

    # Final Summary
    print(f"\n{'=' * 65}")
    print("  ALL PIPELINES COMPLETE")
    print(f"{'=' * 65}")
    print(f"\n  Applications processed: 2")
    print(f"  Total artifacts generated: {len(pipeline1.artifacts) + len(pipeline2.artifacts)}")
    print(f"\n  Output structure:")
    print(f"  output/")
    print(f"  ├── python-flask-app/")
    print(f"  │   ├── profile.json")
    print(f"  │   ├── Dockerfile")
    print(f"  │   ├── .dockerignore")
    print(f"  │   ├── docker-compose.yaml")
    print(f"  │   └── k8s/manifests.yaml")
    print(f"  └── node-express-app/")
    print(f"      ├── profile.json")
    print(f"      ├── Dockerfile")
    print(f"      ├── .dockerignore")
    print(f"      ├── docker-compose.yaml")
    print(f"      └── k8s/manifests.yaml")

    print(f"\n  Key Learning:")
    print(f"  A single AI-powered pipeline produces a complete, consistent set")
    print(f"  of deployment artifacts from source code analysis. Every artifact")
    print(f"  derives from the same deployment profile, ensuring alignment")
    print(f"  between development, CI/CD, and production environments.")

    print(f"\n  Next steps:")
    print(f"  1. cd output/<app-name> && docker compose up")
    print(f"  2. cd output/<app-name> && docker build -t <app> .")
    print(f"  3. cd output/<app-name> && kubectl apply -f k8s/")
    print(f"{'=' * 65}")
