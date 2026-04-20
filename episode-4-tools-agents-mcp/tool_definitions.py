"""
Episode 4: Building Tools, Agents & MCP Servers
File: tool_definitions.py — Claude API Tool Schema Definitions (JSON)

Author: Sagar Utekar
Prerequisites: Episodes 1-3 completed; Claude API key working

Tool definitions that tell the Claude API what tools the agent can call,
including parameter schemas and descriptions. These are passed to
client.messages.create(tools=TOOL_DEFINITIONS).
"""
import json

TOOL_DEFINITIONS = [
    {
        "name": "kubectl",
        "description": "Execute a read-only kubectl command. Supports: get, describe, logs, top, explain, api-resources. Does NOT support: delete, exec, apply, patch.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The kubectl command without 'kubectl' prefix. Example: 'get pods -n production -o wide'"},
                "namespace": {"type": "string", "description": "Override namespace (optional)"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "get_pod_logs",
        "description": "Fetch logs from a Kubernetes pod. Use for debugging crashes, errors, and application issues.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod": {"type": "string", "description": "Pod name"},
                "namespace": {"type": "string", "description": "Namespace", "default": "default"},
                "lines": {"type": "integer", "description": "Number of recent log lines", "default": 50},
                "previous": {"type": "boolean", "description": "Get logs from previous (crashed) container", "default": False}
            },
            "required": ["pod"]
        }
    },
    {
        "name": "get_cluster_health",
        "description": "Get comprehensive cluster health: node status, unhealthy pods, warning events, resource usage. Use as first step in any investigation.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "query_prometheus",
        "description": "Execute a PromQL query against Prometheus. Use for metrics like error rates, latency, resource utilization.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "PromQL query. Example: 'rate(http_requests_total{status=~\"5..\"}[5m])'"},
                "prometheus_url": {"type": "string", "description": "Prometheus URL", "default": "http://localhost:9090"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "scale_deployment",
        "description": "Scale a deployment's replica count. Max 10 replicas (safety limit).",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Deployment name"},
                "replicas": {"type": "integer", "description": "Target replica count (max 10)"},
                "namespace": {"type": "string", "description": "Namespace", "default": "default"}
            },
            "required": ["name", "replicas"]
        }
    },
    {
        "name": "rollback_deployment",
        "description": "Rollback a deployment to its previous version. Use when a recent deployment caused issues.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Deployment name"},
                "namespace": {"type": "string", "description": "Namespace", "default": "default"}
            },
            "required": ["name"]
        }
    }
]


if __name__ == "__main__":
    print("Claude API Tool Definitions")
    print("=" * 50)
    for tool in TOOL_DEFINITIONS:
        print(f"\n  Tool: {tool['name']}")
        print(f"  Description: {tool['description'][:80]}...")
        print(f"  Required params: {tool['input_schema'].get('required', [])}")
    print(f"\nTotal tools: {len(TOOL_DEFINITIONS)}")
    print("\nFull JSON:")
    print(json.dumps(TOOL_DEFINITIONS, indent=2))
