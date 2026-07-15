#!/usr/bin/env python3
"""
AI-Assisted DevOps Workshop | Episode 8 - Claude Code Deep Dive | Sagar Utekar

Demo 1: Generating CLAUDE.md from Repository Analysis

This script analyzes a repository structure and generates a CLAUDE.md file
that provides Claude Code with project context, architecture details,
safety rules, and common commands.

CLAUDE.md is the primary way to give Claude Code persistent context about
your project - it reads this file automatically when entering a directory.
"""

import os
import json
from pathlib import Path


def print_header():
    print("=" * 65)
    print("  CLAUDE CODE DEEP DIVE - CLAUDE.md Generator")
    print("  AI-Assisted DevOps Workshop | Episode 8")
    print("=" * 65)
    print()


def scan_repository(repo_path):
    """Scan repository for common files and directories to determine project type."""
    print("-" * 65)
    print("  Phase 1: Scanning Repository Structure")
    print("-" * 65)
    print()

    findings = {
        "languages": [],
        "frameworks": [],
        "deployment_targets": [],
        "ci_cd": [],
        "has_tests": False,
        "has_docs": False,
        "package_manager": None,
        "project_name": os.path.basename(os.path.abspath(repo_path)),
    }

    # Check for language indicators
    indicators = {
        "package.json": ("JavaScript/TypeScript", "Node.js"),
        "requirements.txt": ("Python", None),
        "pyproject.toml": ("Python", None),
        "go.mod": ("Go", None),
        "Cargo.toml": ("Rust", None),
        "pom.xml": ("Java", "Maven"),
        "build.gradle": ("Java/Kotlin", "Gradle"),
        "Gemfile": ("Ruby", "Rails"),
    }

    for filename, (language, framework) in indicators.items():
        filepath = os.path.join(repo_path, filename)
        if os.path.exists(filepath):
            print(f"  [FOUND] {filename}")
            if language and language not in findings["languages"]:
                findings["languages"].append(language)
            if framework and framework not in findings["frameworks"]:
                findings["frameworks"].append(framework)
            if filename == "package.json":
                findings["package_manager"] = "npm/yarn"
                # Try to detect frameworks from package.json
                try:
                    with open(filepath, "r") as f:
                        pkg = json.load(f)
                        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                        if "react" in deps:
                            findings["frameworks"].append("React")
                        if "next" in deps:
                            findings["frameworks"].append("Next.js")
                        if "express" in deps:
                            findings["frameworks"].append("Express")
                        if "fastify" in deps:
                            findings["frameworks"].append("Fastify")
                except (json.JSONDecodeError, IOError):
                    pass
            elif filename == "requirements.txt":
                findings["package_manager"] = "pip"
                try:
                    with open(filepath, "r") as f:
                        content = f.read().lower()
                        if "django" in content:
                            findings["frameworks"].append("Django")
                        if "flask" in content:
                            findings["frameworks"].append("Flask")
                        if "fastapi" in content:
                            findings["frameworks"].append("FastAPI")
                except IOError:
                    pass

    # Check for deployment/infra indicators
    deployment_checks = {
        "Dockerfile": "Docker/Containers",
        "docker-compose.yml": "Docker Compose",
        "docker-compose.yaml": "Docker Compose",
    }

    for filename, target in deployment_checks.items():
        if os.path.exists(os.path.join(repo_path, filename)):
            print(f"  [FOUND] {filename}")
            findings["deployment_targets"].append(target)

    # Check for directories
    dir_checks = {
        "k8s": "Kubernetes",
        "kubernetes": "Kubernetes",
        "helm": "Kubernetes (Helm)",
        "terraform": "Terraform/Cloud",
        "pulumi": "Pulumi/Cloud",
        "cdk": "AWS CDK",
        ".github": "GitHub Actions",
        ".gitlab-ci.yml": "GitLab CI",
        "Jenkinsfile": "Jenkins",
    }

    for dirname, target in dir_checks.items():
        path = os.path.join(repo_path, dirname)
        if os.path.exists(path):
            print(f"  [FOUND] {dirname}/")
            if "CI" in target or "Actions" in target or "Jenkins" in target:
                findings["ci_cd"].append(target)
            else:
                findings["deployment_targets"].append(target)

    # Check for tests
    test_dirs = ["tests", "test", "__tests__", "spec", "e2e"]
    for td in test_dirs:
        if os.path.exists(os.path.join(repo_path, td)):
            findings["has_tests"] = True
            print(f"  [FOUND] {td}/ (test directory)")
            break

    # Check for docs
    doc_dirs = ["docs", "documentation", "wiki"]
    for dd in doc_dirs:
        if os.path.exists(os.path.join(repo_path, dd)):
            findings["has_docs"] = True
            print(f"  [FOUND] {dd}/ (documentation)")
            break

    if not findings["languages"]:
        print("  [INFO] No specific language indicators found")
        findings["languages"].append("Unknown")

    print()
    return findings


def generate_claude_md(findings):
    """Generate CLAUDE.md content based on repository analysis."""
    print("-" * 65)
    print("  Phase 2: Generating CLAUDE.md Content")
    print("-" * 65)
    print()

    project_name = findings["project_name"]
    languages = ", ".join(findings["languages"])
    frameworks = ", ".join(findings["frameworks"]) if findings["frameworks"] else "N/A"
    deployments = ", ".join(findings["deployment_targets"]) if findings["deployment_targets"] else "N/A"

    sections = []

    # Project Overview
    sections.append(f"""# {project_name}

## Project Overview

This is a {languages} project{f' using {frameworks}' if findings["frameworks"] else ''}.
Deployment targets: {deployments}.
""")

    # Architecture
    arch_lines = ["## Architecture\n"]
    arch_lines.append(f"- **Languages**: {languages}")
    if findings["frameworks"]:
        arch_lines.append(f"- **Frameworks**: {frameworks}")
    if findings["deployment_targets"]:
        arch_lines.append(f"- **Infrastructure**: {deployments}")
    if findings["ci_cd"]:
        arch_lines.append(f"- **CI/CD**: {', '.join(findings['ci_cd'])}")
    if findings["package_manager"]:
        arch_lines.append(f"- **Package Manager**: {findings['package_manager']}")
    sections.append("\n".join(arch_lines))

    # Environments
    sections.append("""## Environments

| Environment | Purpose | Branch |
|-------------|---------|--------|
| development | Local dev & testing | feature/* |
| staging | Pre-production validation | develop |
| production | Live traffic | main |
""")

    # Safety Rules
    safety_rules = ["## Safety Rules\n"]
    safety_rules.append("**CRITICAL - Always follow these rules:**\n")
    safety_rules.append("1. NEVER run destructive commands against production")
    safety_rules.append("2. NEVER commit secrets, tokens, or credentials")
    safety_rules.append("3. ALWAYS run tests before committing changes")
    if "Kubernetes" in deployments or "Kubernetes (Helm)" in deployments:
        safety_rules.append("4. NEVER run `kubectl delete` without `--dry-run` first")
        safety_rules.append("5. ALWAYS verify the current kubectl context before operations")
    if "Terraform/Cloud" in deployments:
        safety_rules.append("4. ALWAYS run `terraform plan` before `terraform apply`")
        safety_rules.append("5. NEVER use `terraform destroy` without explicit approval")
    if "Docker/Containers" in deployments:
        safety_rules.append("- NEVER use `docker system prune -af` in production")
    sections.append("\n".join(safety_rules))

    # Common Commands
    commands = ["## Common Commands\n"]
    commands.append("```bash")
    if findings["package_manager"] == "npm/yarn":
        commands.append("# Install dependencies")
        commands.append("npm install")
        commands.append("")
        commands.append("# Run development server")
        commands.append("npm run dev")
        commands.append("")
        commands.append("# Run tests")
        commands.append("npm test")
        commands.append("")
        commands.append("# Build for production")
        commands.append("npm run build")
    elif findings["package_manager"] == "pip":
        commands.append("# Install dependencies")
        commands.append("pip install -r requirements.txt")
        commands.append("")
        commands.append("# Run application")
        commands.append("python -m app")
        commands.append("")
        commands.append("# Run tests")
        commands.append("pytest")
        commands.append("")
        commands.append("# Lint code")
        commands.append("ruff check .")
    else:
        commands.append("# Build the project")
        commands.append("make build")
        commands.append("")
        commands.append("# Run tests")
        commands.append("make test")
        commands.append("")
        commands.append("# Deploy")
        commands.append("make deploy")

    if "Docker/Containers" in deployments:
        commands.append("")
        commands.append("# Docker build")
        commands.append(f"docker build -t {project_name}:latest .")
        commands.append("")
        commands.append("# Docker run")
        commands.append(f"docker run -p 8080:8080 {project_name}:latest")

    if "Kubernetes" in deployments or "Kubernetes (Helm)" in deployments:
        commands.append("")
        commands.append("# Deploy to Kubernetes")
        commands.append("kubectl apply -f k8s/")
        commands.append("")
        commands.append("# Check deployment status")
        commands.append("kubectl rollout status deployment/<app-name>")

    if "Terraform/Cloud" in deployments:
        commands.append("")
        commands.append("# Terraform workflow")
        commands.append("cd terraform/")
        commands.append("terraform init")
        commands.append("terraform plan -out=tfplan")
        commands.append("terraform apply tfplan")

    commands.append("```")
    sections.append("\n".join(commands))

    # Code Style
    sections.append("""## Code Style

- Follow existing patterns in the codebase
- Write descriptive commit messages (conventional commits preferred)
- Add tests for new functionality
- Update documentation when changing public APIs
""")

    content = "\n\n".join(sections)

    print("  Generated sections:")
    print("    - Project Overview")
    print("    - Architecture")
    print("    - Environments")
    print("    - Safety Rules")
    print("    - Common Commands")
    print("    - Code Style")
    print()

    return content


def write_claude_md(content, output_path):
    """Write the generated CLAUDE.md to disk."""
    print("-" * 65)
    print("  Phase 3: Writing CLAUDE.md")
    print("-" * 65)
    print()

    with open(output_path, "w") as f:
        f.write(content)

    print(f"  [WRITTEN] {output_path}")
    print(f"  [SIZE] {len(content)} bytes")
    print()


def main():
    print_header()

    # Use current directory or a sample structure
    repo_path = os.getcwd()

    print(f"  Analyzing repository: {repo_path}")
    print()

    # Create a sample repo structure for demonstration
    demo_path = Path("/tmp/sample-devops-project")
    demo_path.mkdir(exist_ok=True)

    # Create sample files to simulate a real project
    sample_files = {
        "package.json": json.dumps({
            "name": "devops-api",
            "version": "1.0.0",
            "dependencies": {"express": "^4.18.0", "pg": "^8.11.0"},
            "devDependencies": {"jest": "^29.0.0"},
            "scripts": {"start": "node src/index.js", "test": "jest", "dev": "nodemon src/index.js"}
        }, indent=2),
        "Dockerfile": "FROM node:20-alpine\nWORKDIR /app\nCOPY . .\nRUN npm install\nEXPOSE 8080\nCMD [\"node\", \"src/index.js\"]",
    }

    for filename, content in sample_files.items():
        filepath = demo_path / filename
        filepath.write_text(content)

    # Create directories
    (demo_path / "k8s").mkdir(exist_ok=True)
    (demo_path / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (demo_path / "terraform").mkdir(exist_ok=True)
    (demo_path / "tests").mkdir(exist_ok=True)
    (demo_path / "docs").mkdir(exist_ok=True)

    print(f"  [DEMO] Created sample project at: {demo_path}")
    print()

    # Scan the sample repository
    findings = scan_repository(str(demo_path))

    # Display findings summary
    print("-" * 65)
    print("  Analysis Summary")
    print("-" * 65)
    print()
    print(f"  Project: {findings['project_name']}")
    print(f"  Languages: {', '.join(findings['languages'])}")
    print(f"  Frameworks: {', '.join(findings['frameworks']) if findings['frameworks'] else 'None detected'}")
    print(f"  Deployment: {', '.join(findings['deployment_targets']) if findings['deployment_targets'] else 'None detected'}")
    print(f"  CI/CD: {', '.join(findings['ci_cd']) if findings['ci_cd'] else 'None detected'}")
    print(f"  Has Tests: {'Yes' if findings['has_tests'] else 'No'}")
    print(f"  Has Docs: {'Yes' if findings['has_docs'] else 'No'}")
    print()

    # Generate CLAUDE.md
    content = generate_claude_md(findings)

    # Write to disk
    output_path = str(demo_path / "CLAUDE.md")
    write_claude_md(content, output_path)

    # Display the generated file
    print("-" * 65)
    print("  Generated CLAUDE.md Preview")
    print("-" * 65)
    print()
    for line in content.split("\n")[:40]:
        print(f"  {line}")
    print("  ...")
    print()

    print("=" * 65)
    print()
    print("  Key Learning:")
    print("  CLAUDE.md gives Claude Code persistent project context.")
    print("  It auto-loads when Claude enters a directory, providing:")
    print("  - Project architecture and conventions")
    print("  - Safety guardrails that prevent dangerous operations")
    print("  - Common commands so Claude knows your workflow")
    print("  - Code style preferences for consistent output")
    print()
    print("  Next: task2_hooks_setup.py - Setting up safety hooks")
    print()
    print("=" * 65)


if __name__ == "__main__":
    main()
