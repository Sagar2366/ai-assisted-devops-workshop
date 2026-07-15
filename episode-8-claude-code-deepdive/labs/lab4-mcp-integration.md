# Lab 4: Connecting MCP Servers to Claude Code

> **Mission:** Configure Model Context Protocol (MCP) servers that give Claude Code real-time access to your infrastructure — Kubernetes clusters, cloud APIs, observability platforms, and more.

## Concept: MCP in Claude Code

MCP servers extend Claude Code's capabilities beyond file reading and shell commands. They provide **structured, typed access** to external systems with proper authentication and rate limiting.

**Analogy:** If Claude Code without MCP is like an SRE with only SSH access, Claude Code with MCP is like an SRE with a full observability dashboard, cloud console, and ticketing system — all accessible from one terminal.

## How MCP Works in Claude Code

```
Claude Code CLI
    │
    ├── Built-in Tools (Bash, Read, Write, Edit)
    │
    └── MCP Servers (configured in settings)
        ├── Kubernetes MCP → Live cluster access
        ├── AWS MCP → Cloud resource queries
        ├── Prometheus MCP → Metrics and alerts
        └── GitHub MCP → Issues, PRs, Actions
```

## Step 1: MCP Configuration Location

MCP servers are configured in your settings files:

```bash
# Project-level (shared with team)
.claude/settings.json

# User-level (personal servers)
~/.claude/settings.json
```

## Step 2: Configure the GitHub MCP Server

GitHub MCP gives Claude Code access to issues, pull requests, and Actions:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

Test it:
```bash
claude

> List the open pull requests in this repository
> Show me the last 5 failed GitHub Actions runs
> What issues are labeled "bug" and assigned to the SRE team?
```

## Step 3: Configure a Kubernetes MCP Server

For real-time cluster access through structured queries:

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "npx",
      "args": ["-y", "@manusa/kubernetes-mcp-server"],
      "env": {
        "KUBECONFIG": "${HOME}/.kube/config"
      }
    }
  }
}
```

This provides Claude Code with typed Kubernetes operations:
- List and describe resources across namespaces
- Watch for changes in real-time
- Query pod logs with structured filters
- Check resource utilization

## Step 4: Configure a Filesystem MCP Server (for Restricted Paths)

For controlled access to specific infrastructure paths:

```json
{
  "mcpServers": {
    "infra-docs": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/runbooks",
        "/path/to/architecture-docs"
      ]
    }
  }
}
```

## Step 5: Configure Prometheus/Grafana MCP

For observability access:

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "node",
      "args": ["/path/to/prometheus-mcp-server/index.js"],
      "env": {
        "PROMETHEUS_URL": "http://prometheus.monitoring.svc:9090",
        "GRAFANA_URL": "http://grafana.monitoring.svc:3000",
        "GRAFANA_API_KEY": "${GRAFANA_API_KEY}"
      }
    }
  }
}
```

## Step 6: Full Project MCP Configuration

Combine multiple MCP servers in your project settings:

```bash
cat > .claude/settings.json << 'EOF'
{
  "permissions": {
    "allow": [
      "Bash(kubectl get *)",
      "Bash(terraform plan *)",
      "Bash(git *)",
      "mcp__github__*",
      "mcp__kubernetes__get_*",
      "mcp__kubernetes__list_*"
    ],
    "deny": [
      "Bash(kubectl delete *)",
      "mcp__kubernetes__delete_*"
    ]
  },
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "./docs",
        "./runbooks"
      ]
    }
  }
}
EOF
```

## Step 7: MCP Permissions — Allow and Deny

Control which MCP operations Claude Code can perform:

```json
{
  "permissions": {
    "allow": [
      "mcp__github__list_pull_requests",
      "mcp__github__get_issue",
      "mcp__github__list_commits",
      "mcp__kubernetes__get_*",
      "mcp__kubernetes__list_*",
      "mcp__prometheus__query"
    ],
    "deny": [
      "mcp__github__create_issue",
      "mcp__github__merge_pull_request",
      "mcp__kubernetes__delete_*",
      "mcp__kubernetes__patch_*"
    ]
  }
}
```

The pattern is: `mcp__{server-name}__{tool-name}`

## Step 8: Building a Custom MCP Server for Your Infrastructure

For organization-specific needs, you can build custom MCP servers:

```python
#!/usr/bin/env python3
"""
Custom MCP server for internal infrastructure.
Provides structured access to deployment pipelines,
feature flags, and service catalog.
"""

# This is a conceptual example — see Episode 5 for full MCP server development

# Your custom server could expose:
# - get_service_status(service_name) → health, version, last deploy
# - list_feature_flags(environment) → active flags and their states
# - get_deployment_history(service, days) → recent deploys with outcomes
# - query_on_call(team) → current on-call engineer and contact
```

Configure your custom server:

```json
{
  "mcpServers": {
    "internal-platform": {
      "command": "python3",
      "args": ["/path/to/your/platform-mcp-server.py"],
      "env": {
        "PLATFORM_API_URL": "https://internal-platform.company.com",
        "PLATFORM_TOKEN": "${PLATFORM_TOKEN}"
      }
    }
  }
}
```

## Step 9: Test MCP Integration

```bash
# Start Claude Code with MCP servers configured
claude

# Test GitHub MCP
> What PRs are waiting for review from the SRE team?

# Test Kubernetes MCP (if configured)
> Show me all pods with restart count > 3 across all namespaces

# Test combined queries
> Check if the latest PR deployment is healthy in staging

# Verify MCP servers are loaded
> What MCP tools do you have access to?
```

## Step 10: MCP Server Health Monitoring

Add a slash command to verify MCP connectivity:

```bash
cat > .claude/commands/mcp-status.md << 'EOF'
# MCP Server Status Check

Verify all configured MCP servers are responsive.

## Steps
1. List all available MCP tools and their servers
2. For each server, attempt a simple read operation:
   - GitHub: list repos
   - Kubernetes: get namespaces
   - Filesystem: list root directory
3. Report status of each server: CONNECTED / ERROR / TIMEOUT

## Output Format
| Server | Status | Latency | Last Tool Count |
|--------|--------|---------|-----------------|
EOF
```

## What Success Looks Like

After completing this lab, you should have:

- [x] At least one MCP server configured and responding
- [x] Permissions controlling which MCP operations are allowed
- [x] Claude Code answering questions using live infrastructure data
- [x] MCP tools appearing in Claude Code's available tool list
- [x] Understanding of how to add custom MCP servers

## Key Takeaway

MCP transforms Claude Code from a tool that knows about your infrastructure (through CLAUDE.md) into one that can observe your infrastructure in real time. The combination of contextual knowledge (CLAUDE.md) + safety guardrails (hooks) + live data (MCP) creates an AI assistant that is genuinely useful for production operations — not just development.

## Next

Proceed to [Lab 5: Team Workflow Patterns](lab5-team-workflow.md) to learn how to share these configurations across your team effectively.
