#!/usr/bin/env python3
"""
AI Docker Compose Generator - Episode 12, Task 4
=================================================
Uses Claude to generate docker-compose.yaml files for local development,
including dependent services like databases and caches.

Author: Sagar Utekar | CNCF Ambassador | Kubestronaut
"""

import os
import sys
import json
import re
import anthropic

print("=" * 65)
print("  AI DOCKER COMPOSE GENERATOR")
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
# Docker Compose Generation
# =============================================================================

def build_compose_prompt(profile, app_name):
    """Create a prompt for generating docker-compose.yaml."""
    return f"""Generate a docker-compose.yaml for local development of this application.

Application Name: {app_name}
Application Profile:
{json.dumps(profile, indent=2)}

Requirements:
1. Use docker compose format version "3.8"
2. Main application service:
   - Build from current directory (context: .)
   - Map the app port to the same host port
   - Volume mount ./ to /app for live code reloading
   - Exclude dependency directories from the mount (node_modules, __pycache__)
   - Set all environment variables from the profile
   - Add depends_on with condition: service_healthy for dependent services
   - Include a healthcheck using the health_endpoint
   - Set restart: unless-stopped
3. Dependent services (based on database_type):
   - If redis: add redis:7-alpine service with healthcheck
   - If mongodb: add mongo:7 service with healthcheck
   - If postgres: add postgres:16-alpine with POSTGRES_PASSWORD and healthcheck
   - If mysql: add mysql:8 with MYSQL_ROOT_PASSWORD and healthcheck
4. Networking:
   - Define a custom bridge network named "app-network"
   - Connect all services to it
5. Volumes:
   - Use named volumes for database persistence
6. Include helpful comments explaining each section

Return ONLY the docker-compose.yaml content. No markdown fences, no explanation text."""


def generate_compose(profile, app_name):
    """Use Claude to generate a docker-compose.yaml."""
    client = anthropic.Anthropic()
    prompt = build_compose_prompt(profile, app_name)

    message = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    compose_content = message.content[0].text

    # Strip markdown code fences if present
    if compose_content.strip().startswith("```"):
        lines = compose_content.strip().split("\n")
        if lines[-1].strip() == "```":
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        compose_content = "\n".join(lines)

    return compose_content


def save_compose(content, output_path):
    """Save the generated compose file to disk."""
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

    # Experiment 1: Python App Compose
    print(f"\n{'-' * 65}")
    print("  EXPERIMENT 1: Docker Compose for Python Flask App")
    print(f"{'-' * 65}")

    python_app_dir = os.path.join(SAMPLE_APPS_DIR, "python-app")
    print(f"\n  [1/3] Analyzing python-app...")
    python_profile = analyze_application(python_app_dir)

    if python_profile:
        print(f"  [2/3] Generating docker-compose.yaml...")
        python_compose = generate_compose(python_profile, "python-flask-app")

        output_path = os.path.join(OUTPUT_DIR, "python-app", "docker-compose.yaml")
        save_compose(python_compose, output_path)
        print(f"  [3/3] Saved to: {output_path}")

        print(f"\n  Generated docker-compose.yaml:")
        print(f"  {'.' * 50}")
        for line in python_compose.split("\n"):
            print(f"  | {line}")
        print(f"  {'.' * 50}")

    # Experiment 2: Node App Compose
    print(f"\n{'-' * 65}")
    print("  EXPERIMENT 2: Docker Compose for Node.js Express App")
    print(f"{'-' * 65}")

    node_app_dir = os.path.join(SAMPLE_APPS_DIR, "node-app")
    print(f"\n  [1/3] Analyzing node-app...")
    node_profile = analyze_application(node_app_dir)

    if node_profile:
        print(f"  [2/3] Generating docker-compose.yaml...")
        node_compose = generate_compose(node_profile, "node-express-app")

        output_path = os.path.join(OUTPUT_DIR, "node-app", "docker-compose.yaml")
        save_compose(node_compose, output_path)
        print(f"  [3/3] Saved to: {output_path}")

        print(f"\n  Generated docker-compose.yaml:")
        print(f"  {'.' * 50}")
        for line in node_compose.split("\n"):
            print(f"  | {line}")
        print(f"  {'.' * 50}")

    # Summary
    print(f"\n{'=' * 65}")
    print("  DOCKER COMPOSE GENERATION COMPLETE")
    print(f"{'=' * 65}")
    print(f"\n  Generated Compose Files:")
    print(f"  ├── output/python-app/docker-compose.yaml  (app + redis)")
    print(f"  └── output/node-app/docker-compose.yaml    (app + mongodb)")

    print(f"\n  Services per file:")
    print(f"  ├── Application service (build, volumes, healthcheck)")
    print(f"  ├── Database/Cache service (persistent volume)")
    print(f"  └── Custom bridge network for isolation")

    print(f"\n  Key Learning:")
    print(f"  AI-generated compose files bridge development and production.")
    print(f"  Derived from the same deployment profile as K8s manifests,")
    print(f"  they provide a consistent local environment that catches")
    print(f"  integration issues before code reaches the cluster.")

    print(f"\n  Next: task5_full_deployment.py")
    print(f"{'=' * 65}")
