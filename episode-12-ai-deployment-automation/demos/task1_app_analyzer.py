#!/usr/bin/env python3
"""
AI Application Analyzer - Episode 12, Task 1
=============================================
Uses Claude to analyze application source code and dependency files,
producing a structured deployment profile that drives artifact generation.

Author: Sagar Utekar | CNCF Ambassador | Kubestronaut
"""

import os
import sys
import json
import re
import anthropic

print("=" * 65)
print("  AI APPLICATION ANALYZER")
print("  Episode 12: AI-Powered Deployment Automation")
print("=" * 65)


# =============================================================================
# Configuration
# =============================================================================

SAMPLE_APPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample-apps")
MODEL = "claude-sonnet-4-20250514"


# =============================================================================
# Application File Reader
# =============================================================================

def read_app_files(app_dir):
    """Read dependency and source files from an application directory."""
    files = {}
    target_files = [
        "requirements.txt", "package.json", "go.mod", "Gemfile",
        "app.py", "main.py", "server.py",
        "app.js", "index.js", "server.js",
        "main.go",
        "Procfile", ".env.example", "Makefile",
    ]

    for filename in target_files:
        filepath = os.path.join(app_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                files[filename] = f.read()

    return files


# =============================================================================
# Analysis Prompt Builder
# =============================================================================

def build_analysis_prompt(files):
    """Construct the prompt that asks Claude to analyze the application."""
    file_contents = ""
    for name, content in files.items():
        file_contents += f"\n--- {name} ---\n{content}\n"

    return f"""Analyze the following application files and produce a deployment profile as JSON.

{file_contents}

Return a JSON object with exactly these fields:
- "runtime": the language (python, node, go, ruby)
- "runtime_version": recommended version string (e.g., "3.11", "20", "1.21")
- "framework": the web framework used (e.g., flask, express, gin)
- "port": integer port the app listens on
- "dependencies": list of key dependency names
- "env_vars": list of environment variable names needed
- "health_endpoint": health check path if available, or "/health"
- "build_command": command to install dependencies
- "start_command": command to start the application in production
- "needs_database": boolean indicating if a database is required
- "database_type": type if applicable (postgres, redis, mongodb, mysql) or null

Return ONLY the JSON object, no markdown fences, no explanation."""


# =============================================================================
# Claude Analysis
# =============================================================================

def analyze_application(app_dir, app_name=None):
    """Use Claude to analyze an application and return a deployment profile."""
    if app_name is None:
        app_name = os.path.basename(app_dir)

    print(f"\n{'-' * 65}")
    print(f"  Analyzing: {app_name}")
    print(f"  Directory: {app_dir}")
    print(f"{'-' * 65}")

    # Read files
    files = read_app_files(app_dir)
    if not files:
        print(f"  ERROR: No recognizable application files found in {app_dir}")
        return None

    print(f"  Found files: {', '.join(files.keys())}")

    # Build prompt and call Claude
    client = anthropic.Anthropic()
    prompt = build_analysis_prompt(files)

    print(f"  Sending to Claude ({MODEL})...")

    message = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text

    # Extract JSON from response
    json_match = re.search(r"\{[\s\S]*\}", response_text)
    if json_match:
        profile = json.loads(json_match.group())
        return profile

    print("  ERROR: Could not extract JSON profile from response")
    print(f"  Raw response: {response_text[:200]}")
    return None


def display_profile(profile, app_name):
    """Display the deployment profile in a readable format."""
    print(f"\n  Deployment Profile for '{app_name}':")
    print(f"  {'.' * 50}")
    print(f"  Runtime:        {profile.get('runtime')} {profile.get('runtime_version')}")
    print(f"  Framework:      {profile.get('framework')}")
    print(f"  Port:           {profile.get('port')}")
    print(f"  Health Check:   {profile.get('health_endpoint')}")
    print(f"  Build Command:  {profile.get('build_command')}")
    print(f"  Start Command:  {profile.get('start_command')}")
    print(f"  Database:       {profile.get('database_type') if profile.get('needs_database') else 'None'}")
    print(f"  Dependencies:   {', '.join(profile.get('dependencies', []))}")
    print(f"  Env Variables:  {', '.join(profile.get('env_vars', []))}")


# =============================================================================
# Main Execution
# =============================================================================

if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n  ERROR: ANTHROPIC_API_KEY environment variable not set.")
        print("  Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    # Experiment 1: Analyze Python App
    print(f"\n{'=' * 65}")
    print("  EXPERIMENT 1: Python Flask Application")
    print(f"{'=' * 65}")

    python_app_dir = os.path.join(SAMPLE_APPS_DIR, "python-app")
    python_profile = analyze_application(python_app_dir, "python-flask-app")

    if python_profile:
        display_profile(python_profile, "python-flask-app")
        print(f"\n  Full JSON:")
        print(f"  {json.dumps(python_profile, indent=2)}")

    # Experiment 2: Analyze Node App
    print(f"\n{'=' * 65}")
    print("  EXPERIMENT 2: Node.js Express Application")
    print(f"{'=' * 65}")

    node_app_dir = os.path.join(SAMPLE_APPS_DIR, "node-app")
    node_profile = analyze_application(node_app_dir, "node-express-app")

    if node_profile:
        display_profile(node_profile, "node-express-app")
        print(f"\n  Full JSON:")
        print(f"  {json.dumps(node_profile, indent=2)}")

    # Summary
    print(f"\n{'=' * 65}")
    print("  ANALYSIS COMPLETE")
    print(f"{'=' * 65}")
    print(f"\n  Applications analyzed: 2")
    print(f"  Profiles generated:   {sum(1 for p in [python_profile, node_profile] if p)}")

    print(f"\n  Key Learning:")
    print(f"  AI application analysis transforms unstructured source code into")
    print(f"  structured deployment profiles. These profiles become the single")
    print(f"  source of truth for generating all deployment artifacts.")

    print(f"\n  Next: task2_dockerfile_generator.py")
    print(f"{'=' * 65}")
