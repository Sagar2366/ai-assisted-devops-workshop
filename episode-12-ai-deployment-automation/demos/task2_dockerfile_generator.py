#!/usr/bin/env python3
"""
AI Dockerfile Generator - Episode 12, Task 2
=============================================
Uses Claude to generate optimized multi-stage Dockerfiles based on
application deployment profiles.

Author: Sagar Utekar | CNCF Ambassador | Kubestronaut
"""

import os
import sys
import json
import re
import anthropic

print("=" * 65)
print("  AI DOCKERFILE GENERATOR")
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
        "app.py", "main.py", "server.py",
        "app.js", "index.js", "server.js",
        "main.go", "Procfile",
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
# Dockerfile Generation Prompt
# =============================================================================

def build_dockerfile_prompt(profile, app_name):
    """Create a prompt asking Claude to generate an optimized Dockerfile."""
    return f"""Generate a production-ready, multi-stage Dockerfile for this application.

Application Name: {app_name}
Application Profile:
{json.dumps(profile, indent=2)}

Requirements:
1. Use a multi-stage build with named stages (builder + runtime)
2. Use specific version tags for base images (never use 'latest')
3. Run as a non-root user in the runtime stage
4. Include a HEALTHCHECK instruction using the health_endpoint
5. Minimize layers and leverage Docker build cache
6. Include LABEL instructions (maintainer, description, version)
7. Set appropriate EXPOSE and CMD/ENTRYPOINT
8. For Python: use slim base, install with --no-cache-dir
9. For Node: use alpine base, use npm ci --production
10. Copy only necessary files (not source in build stage)

Return ONLY the Dockerfile content. No markdown fences, no explanation text."""


# =============================================================================
# Dockerfile Generator
# =============================================================================

def generate_dockerfile(profile, app_name):
    """Use Claude to generate a multi-stage Dockerfile."""
    client = anthropic.Anthropic()
    prompt = build_dockerfile_prompt(profile, app_name)

    message = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    dockerfile_content = message.content[0].text

    # Strip markdown code fences if present
    if dockerfile_content.strip().startswith("```"):
        lines = dockerfile_content.strip().split("\n")
        # Remove first line (```dockerfile) and last line (```)
        if lines[-1].strip() == "```":
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        dockerfile_content = "\n".join(lines)

    return dockerfile_content


def save_dockerfile(content, output_path):
    """Save the generated Dockerfile to disk."""
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

    # Experiment 1: Python App Dockerfile
    print(f"\n{'-' * 65}")
    print("  EXPERIMENT 1: Generate Dockerfile for Python Flask App")
    print(f"{'-' * 65}")

    python_app_dir = os.path.join(SAMPLE_APPS_DIR, "python-app")
    print(f"\n  [1/3] Analyzing python-app...")
    python_profile = analyze_application(python_app_dir)

    if python_profile:
        print(f"  [2/3] Generating multi-stage Dockerfile...")
        python_dockerfile = generate_dockerfile(python_profile, "python-flask-app")

        output_path = os.path.join(OUTPUT_DIR, "python-app", "Dockerfile")
        save_dockerfile(python_dockerfile, output_path)
        print(f"  [3/3] Saved to: {output_path}")

        print(f"\n  Generated Dockerfile:")
        print(f"  {'.' * 50}")
        for line in python_dockerfile.split("\n"):
            print(f"  | {line}")
        print(f"  {'.' * 50}")

    # Experiment 2: Node App Dockerfile
    print(f"\n{'-' * 65}")
    print("  EXPERIMENT 2: Generate Dockerfile for Node.js Express App")
    print(f"{'-' * 65}")

    node_app_dir = os.path.join(SAMPLE_APPS_DIR, "node-app")
    print(f"\n  [1/3] Analyzing node-app...")
    node_profile = analyze_application(node_app_dir)

    if node_profile:
        print(f"  [2/3] Generating multi-stage Dockerfile...")
        node_dockerfile = generate_dockerfile(node_profile, "node-express-app")

        output_path = os.path.join(OUTPUT_DIR, "node-app", "Dockerfile")
        save_dockerfile(node_dockerfile, output_path)
        print(f"  [3/3] Saved to: {output_path}")

        print(f"\n  Generated Dockerfile:")
        print(f"  {'.' * 50}")
        for line in node_dockerfile.split("\n"):
            print(f"  | {line}")
        print(f"  {'.' * 50}")

    # Summary
    print(f"\n{'=' * 65}")
    print("  DOCKERFILE GENERATION COMPLETE")
    print(f"{'=' * 65}")
    print(f"\n  Generated Dockerfiles:")
    print(f"  ├── output/python-app/Dockerfile  (multi-stage, slim base)")
    print(f"  └── output/node-app/Dockerfile    (multi-stage, alpine base)")

    print(f"\n  Key Learning:")
    print(f"  AI-generated Dockerfiles follow production best practices by")
    print(f"  default: multi-stage builds, non-root users, health checks,")
    print(f"  and minimal images — tailored to each application's profile.")

    print(f"\n  Next: task3_k8s_generator.py")
    print(f"{'=' * 65}")
