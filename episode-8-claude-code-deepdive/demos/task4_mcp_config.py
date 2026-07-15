#!/usr/bin/env python3
"""
AI-Assisted DevOps Workshop | Episode 8 - Claude Code Deep Dive | Sagar Utekar

Demo 4: Configuring MCP Servers for Claude Code

This script configures Model Context Protocol (MCP) servers that extend
Claude Code's capabilities with external tool integrations:
- kubernetes-mcp: Direct Kubernetes cluster operations
- github-mcp: Pull request and issue management
- prometheus-mcp: Metrics queries and alerting

MCP servers give Claude Code access to external systems through a
standardized protocol, turning it into a true DevOps copilot.
"""

import os
import json
from pathlib import Path


def print_header():
    print("=" * 65)
    print("  CLAUDE CODE DEEP DIVE - MCP Server Configuration")
    print("  AI-Assisted DevOps Workshop | Episode 8")
    print("=" * 65)
    print()


def explain_mcp():
    """Explain what MCP is and why it matters."""
    print("-" * 65)
    print("  What is MCP (Model Context Protocol)?")
    print("-" * 65)
    print()
    print("  MCP is an open protocol that connects AI assistants to")
    print("  external data sources and tools through a standardized")
    print("  interface. Think of it as a USB-C port for AI tools.")
    print()
    print("  Without MCP: Claude Code can only use built-in tools")
    print("  With MCP:    Claude Code gains access to any system")
    print("               that implements an MCP server")
    print()
    print("  Architecture:")
    print("  +------------------+     +------------------+")
    print("  |   Claude Code    |<--->|   MCP Server     |")
    print("  |  (MCP Client)    |     | (e.g., K8s, GH)  |")
    print("  +------------------+     +------------------+")
    print("          |                        |")
    print("     JSON-RPC over               External")
    print("     stdio/SSE                   Systems")
    print()


def read_existing_settings(settings_path):
    """Read existing settings or return empty dict."""
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def configure_kubernetes_mcp():
    """Configure the Kubernetes MCP server."""
    print("-" * 65)
    print("  MCP Server 1: Kubernetes Operations")
    print("-" * 65)
    print()

    config = {
        "command": "npx",
        "args": [
            "-y",
            "@kubernetes/mcp-server"
        ],
        "env": {
            "KUBECONFIG": "${HOME}/.kube/config",
            "K8S_DEFAULT_NAMESPACE": "default"
        },
        "description": "Kubernetes cluster operations via MCP"
    }

    print("  Server: @kubernetes/mcp-server")
    print("  Transport: stdio (launched as subprocess)")
    print()
    print("  Capabilities added to Claude Code:")
    print("    - List/describe pods, deployments, services")
    print("    - Read pod logs with filtering")
    print("    - Check rollout status")
    print("    - Get resource YAML definitions")
    print("    - Watch events in namespaces")
    print("    - Port-forward for debugging")
    print()
    print("  Example interactions enabled:")
    print('    "Show me all failing pods in production"')
    print('    "Get the logs from the payment-service pod that crashed"')
    print('    "Describe the ingress configuration for api-gateway"')
    print()

    return config


def configure_github_mcp():
    """Configure the GitHub MCP server."""
    print("-" * 65)
    print("  MCP Server 2: GitHub PR & Issue Management")
    print("-" * 65)
    print()

    config = {
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-github"
        ],
        "env": {
            "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
        },
        "description": "GitHub operations - PRs, issues, code search"
    }

    print("  Server: @modelcontextprotocol/server-github")
    print("  Transport: stdio (launched as subprocess)")
    print()
    print("  Capabilities added to Claude Code:")
    print("    - Create and review pull requests")
    print("    - Search code across repositories")
    print("    - Manage issues and labels")
    print("    - Read file contents from any branch")
    print("    - List and trigger workflow runs")
    print("    - Review PR diffs and comments")
    print()
    print("  Example interactions enabled:")
    print('    "Create a PR with these changes and add reviewers"')
    print('    "Find all open issues labeled bug in our infra repo"')
    print('    "What CI checks are failing on PR #142?"')
    print()

    return config


def configure_prometheus_mcp():
    """Configure the Prometheus MCP server."""
    print("-" * 65)
    print("  MCP Server 3: Prometheus Metrics & Alerting")
    print("-" * 65)
    print()

    config = {
        "command": "npx",
        "args": [
            "-y",
            "@prometheus/mcp-server"
        ],
        "env": {
            "PROMETHEUS_URL": "http://prometheus.monitoring.svc:9090",
            "PROMETHEUS_AUTH_TOKEN": "${PROM_TOKEN}"
        },
        "description": "Prometheus metrics queries and alert management"
    }

    print("  Server: @prometheus/mcp-server")
    print("  Transport: stdio (launched as subprocess)")
    print()
    print("  Capabilities added to Claude Code:")
    print("    - Execute PromQL queries")
    print("    - Check firing alerts")
    print("    - Query metric metadata")
    print("    - Get target health status")
    print("    - Retrieve recording rules")
    print("    - Time-range metric analysis")
    print()
    print("  Example interactions enabled:")
    print('    "What is the p99 latency for the API in the last hour?"')
    print('    "Show me the error rate trend for payment-service"')
    print('    "Are there any alerts firing right now?"')
    print()

    return config


def write_settings(base_path, k8s_config, github_config, prometheus_config):
    """Write the complete settings.json with MCP configuration."""
    print("-" * 65)
    print("  Phase 4: Writing MCP Configuration")
    print("-" * 65)
    print()

    claude_dir = os.path.join(base_path, ".claude")
    os.makedirs(claude_dir, exist_ok=True)

    settings_path = os.path.join(claude_dir, "settings.json")

    # Read existing settings
    settings = read_existing_settings(settings_path)

    # Add MCP servers configuration
    settings["mcpServers"] = {
        "kubernetes": k8s_config,
        "github": github_config,
        "prometheus": prometheus_config
    }

    # Write settings
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

    print(f"  [WRITTEN] {settings_path}")
    print()

    return settings_path, settings


def display_configuration(settings):
    """Display the complete MCP configuration."""
    print("-" * 65)
    print("  Complete MCP Configuration")
    print("-" * 65)
    print()
    print("  .claude/settings.json:")
    print()

    formatted = json.dumps(settings, indent=2)
    for line in formatted.split("\n"):
        print(f"    {line}")
    print()


def display_usage_patterns():
    """Show how MCP servers enhance Claude Code workflows."""
    print("-" * 65)
    print("  DevOps Workflow Enhancement with MCP")
    print("-" * 65)
    print()
    print("  Scenario: On-call engineer investigating a latency spike")
    print()
    print("  Without MCP (manual workflow):")
    print("    1. Open Grafana, find the right dashboard")
    print("    2. Switch to terminal, run kubectl commands")
    print("    3. Open GitHub, check recent deployments")
    print("    4. Correlate findings manually")
    print()
    print("  With MCP (Claude Code workflow):")
    print('    > "Investigate the latency spike in payment-service"')
    print()
    print("    Claude Code automatically:")
    print("    1. [prometheus-mcp] Queries p99 latency, finds spike at 14:32")
    print("    2. [kubernetes-mcp] Checks pod status, finds OOMKilled pods")
    print("    3. [github-mcp] Finds deployment at 14:30 that changed memory limits")
    print("    4. Correlates: deployment reduced memory -> OOM -> latency spike")
    print("    5. Recommends: rollback or increase memory limits")
    print()
    print("  Time saved: ~15 minutes of context switching per investigation")
    print()


def display_security_notes():
    """Display security considerations for MCP configuration."""
    print("-" * 65)
    print("  Security Considerations")
    print("-" * 65)
    print()
    print("  1. Token Management:")
    print("     - Use environment variable references (${GITHUB_TOKEN})")
    print("     - NEVER hardcode tokens in settings.json")
    print("     - Rotate tokens on a regular schedule")
    print()
    print("  2. Least Privilege:")
    print("     - GitHub token: repo read + PR write (not admin)")
    print("     - K8s: Use a ServiceAccount with RBAC (not cluster-admin)")
    print("     - Prometheus: Read-only access is sufficient")
    print()
    print("  3. Network Security:")
    print("     - MCP servers run locally as subprocesses")
    print("     - External connections use your existing auth")
    print("     - No data leaves your machine except to configured endpoints")
    print()


def main():
    print_header()

    # Create in a demo directory
    base_path = "/tmp/claude-mcp-demo"
    os.makedirs(base_path, exist_ok=True)

    print(f"  Configuring MCP servers in: {base_path}")
    print()

    # Explain MCP
    explain_mcp()

    # Configure each MCP server
    k8s_config = configure_kubernetes_mcp()
    github_config = configure_github_mcp()
    prometheus_config = configure_prometheus_mcp()

    # Write configuration
    settings_path, settings = write_settings(
        base_path, k8s_config, github_config, prometheus_config
    )

    # Display complete config
    display_configuration(settings)

    # Show usage patterns
    display_usage_patterns()

    # Security notes
    display_security_notes()

    # File structure
    print("-" * 65)
    print("  Created File Structure")
    print("-" * 65)
    print()
    print(f"  {base_path}/")
    print("  +-- .claude/")
    print("      +-- settings.json    (MCP server configuration)")
    print()
    print("  MCP servers configured:")
    print("    - kubernetes: Cluster operations and debugging")
    print("    - github: PR/issue workflow automation")
    print("    - prometheus: Metrics queries and alert checks")
    print()

    print("=" * 65)
    print()
    print("  Key Learning:")
    print("  MCP servers transform Claude Code from a code assistant")
    print("  into a full DevOps copilot that can interact with your")
    print("  infrastructure, repositories, and observability stack.")
    print()
    print("  The protocol is standardized - any tool that implements")
    print("  an MCP server becomes immediately available to Claude Code")
    print("  without custom integration work.")
    print()
    print("  Next: Combine all four features (CLAUDE.md + Hooks +")
    print("  Slash Commands + MCP) for a complete Claude Code setup!")
    print()
    print("=" * 65)


if __name__ == "__main__":
    main()
