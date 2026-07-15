# Lab 5: Build a Kubernetes MCP Server

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

> **Mission:** Build a fully functional Kubernetes MCP server that exposes list_pods, get_logs, and describe_resource as tools any MCP client can use.

---

## Concept: From Prototype to Protocol

In Labs 1-3, you defined tools inline in a script. Now you will package them as an **MCP server** — a standalone process that any AI client can discover and use. This is how production DevOps AI tooling works.

**DevOps analogy:** Labs 1-3 were like writing a one-off script. This lab is like packaging that script into a proper CLI tool with `--help`, flags, and man pages — making it reusable by anyone.

---

## Step-by-Step: Build the K8s MCP Server

### Step 1: Project Structure

```
k8s-mcp-server/
├── server.py       # Main MCP server
└── k8s_tools.py    # Kubernetes tool implementations
```

### Step 2: Kubernetes Tool Implementations

```python
# k8s_tools.py
"""Kubernetes tool implementations for the MCP server."""

import json
import subprocess
from typing import Optional


def list_pods(namespace: str = "default") -> str:
    """List all pods in a namespace."""
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return json.dumps({"error": result.stderr.strip()})

        data = json.loads(result.stdout)
        pods = []
        for item in data.get("items", []):
            status = item["status"]["phase"]
            name = item["metadata"]["name"]
            containers = item["status"].get("containerStatuses", [])
            restarts = sum(c.get("restartCount", 0) for c in containers)
            ready = sum(1 for c in containers if c.get("ready", False))
            total = len(containers)
            pods.append({
                "name": name,
                "status": status,
                "ready": f"{ready}/{total}",
                "restarts": restarts
            })
        return json.dumps({"namespace": namespace, "pods": pods})
    except FileNotFoundError:
        return _mock_list_pods(namespace)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_logs(pod_name: str, namespace: str = "default",
             tail_lines: int = 50, container: Optional[str] = None) -> str:
    """Get logs from a pod."""
    try:
        cmd = ["kubectl", "logs", pod_name, "-n", namespace,
               f"--tail={tail_lines}"]
        if container:
            cmd.extend(["-c", container])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return json.dumps({"error": result.stderr.strip()})
        return json.dumps({
            "pod": pod_name, "namespace": namespace,
            "lines": result.stdout.strip().split("\n")
        })
    except FileNotFoundError:
        return _mock_get_logs(pod_name, namespace, tail_lines)
    except Exception as e:
        return json.dumps({"error": str(e)})


def describe_resource(resource_type: str, resource_name: str,
                      namespace: str = "default") -> str:
    """Describe a Kubernetes resource."""
    try:
        result = subprocess.run(
            ["kubectl", "describe", resource_type, resource_name, "-n", namespace],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return json.dumps({"error": result.stderr.strip()})
        return json.dumps({
            "resource": f"{resource_type}/{resource_name}",
            "namespace": namespace,
            "description": result.stdout
        })
    except FileNotFoundError:
        return _mock_describe(resource_type, resource_name, namespace)
    except Exception as e:
        return json.dumps({"error": str(e)})


# Mock implementations for environments without kubectl
def _mock_list_pods(namespace: str) -> str:
    return json.dumps({
        "namespace": namespace,
        "pods": [
            {"name": "web-frontend-7d4b8c", "status": "Running", "ready": "1/1", "restarts": 0},
            {"name": "api-gateway-5f6a2d", "status": "Running", "ready": "2/2", "restarts": 0},
            {"name": "payment-svc-3e8b1a", "status": "CrashLoopBackOff", "ready": "0/1", "restarts": 12},
            {"name": "redis-cache-9c2d4f", "status": "Running", "ready": "1/1", "restarts": 0},
        ]
    })


def _mock_get_logs(pod_name: str, namespace: str, tail_lines: int) -> str:
    return json.dumps({
        "pod": pod_name, "namespace": namespace,
        "lines": [
            "2024-01-15T10:00:01Z INFO  Starting service...",
            "2024-01-15T10:00:02Z INFO  Connecting to database...",
            "2024-01-15T10:00:03Z ERROR Connection refused: postgres:5432",
            "2024-01-15T10:00:04Z FATAL Cannot start without database connection",
            "2024-01-15T10:00:04Z INFO  Shutting down...",
        ][:tail_lines]
    })


def _mock_describe(resource_type: str, resource_name: str, namespace: str) -> str:
    return json.dumps({
        "resource": f"{resource_type}/{resource_name}",
        "namespace": namespace,
        "description": f"""Name: {resource_name}
Namespace: {namespace}
Labels: app={resource_name}
Status: CrashLoopBackOff
Containers:
  main:
    Image: {resource_name}:v1.2.3
    Limits: memory=256Mi, cpu=500m
    Requests: memory=128Mi, cpu=250m
    Last State: Terminated (Exit Code 1)
    Reason: Error
Events:
  Warning  BackOff  1m  kubelet  Back-off restarting failed container
  Normal   Pulled   2m  kubelet  Container image pulled successfully
  Warning  Failed   2m  kubelet  Error: connection refused to postgres:5432"""
    })
```

### Step 3: The MCP Server

```python
# server.py
"""Kubernetes MCP Server — exposes K8s tools over the Model Context Protocol."""

import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

from k8s_tools import list_pods, get_logs, describe_resource

# Create the MCP server
server = Server("k8s-mcp-server")


@server.list_tools()
async def handle_list_tools():
    """Advertise available Kubernetes tools."""
    return [
        Tool(
            name="list_pods",
            description="List all pods in a Kubernetes namespace with their status, readiness, and restart count",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes namespace (default: 'default')"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_logs",
            description="Retrieve recent log lines from a Kubernetes pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "pod_name": {
                        "type": "string",
                        "description": "Name of the pod"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes namespace (default: 'default')"
                    },
                    "tail_lines": {
                        "type": "integer",
                        "description": "Number of recent log lines to retrieve (default: 50)"
                    },
                    "container": {
                        "type": "string",
                        "description": "Container name (for multi-container pods)"
                    }
                },
                "required": ["pod_name"]
            }
        ),
        Tool(
            name="describe_resource",
            description="Get detailed description of a Kubernetes resource including events, conditions, and configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "description": "Type of resource (pod, deployment, service, etc.)",
                        "enum": ["pod", "deployment", "service", "ingress", "configmap", "secret"]
                    },
                    "resource_name": {
                        "type": "string",
                        "description": "Name of the resource"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes namespace (default: 'default')"
                    }
                },
                "required": ["resource_type", "resource_name"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Execute a Kubernetes tool and return results."""
    if name == "list_pods":
        result = list_pods(arguments.get("namespace", "default"))
    elif name == "get_logs":
        result = get_logs(
            pod_name=arguments["pod_name"],
            namespace=arguments.get("namespace", "default"),
            tail_lines=arguments.get("tail_lines", 50),
            container=arguments.get("container")
        )
    elif name == "describe_resource":
        result = describe_resource(
            resource_type=arguments["resource_type"],
            resource_name=arguments["resource_name"],
            namespace=arguments.get("namespace", "default")
        )
    else:
        raise ValueError(f"Unknown tool: {name}")

    return [TextContent(type="text", text=result)]


async def main():
    """Run the MCP server over stdio transport."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Testing with MCP Inspector

The MCP Inspector is a browser-based development tool for testing MCP servers interactively.

### Install and Launch

```bash
# Run the inspector against your server
npx @modelcontextprotocol/inspector python3 server.py
```

This opens a browser UI where you can:
1. **See all registered tools** — verify your schemas are correct
2. **Call tools interactively** — fill in parameters and execute
3. **Inspect JSON-RPC messages** — see the raw protocol traffic
4. **Test error handling** — try invalid inputs and missing resources

### Manual Testing via stdio

You can also pipe JSON-RPC messages directly to your server:

```bash
# List available tools
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python3 server.py

# Call a tool
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_pods","arguments":{"namespace":"default"}},"id":2}' | python3 server.py
```

### Integration with Claude Code

Configure your server so Claude Code discovers and uses your tools:

```json
// Add to ~/.claude/settings.json or project .claude/settings.json
{
  "mcpServers": {
    "k8s": {
      "command": "python3",
      "args": ["/path/to/server.py"]
    }
  }
}
```

Once configured, Claude Code will:
- Start your server as a subprocess on launch
- Call `list_tools()` to discover available tools
- Invoke tools when Claude needs Kubernetes data during conversations

---

## What Success Looks Like

- The server starts without errors
- `list_tools()` returns all three tool definitions with correct schemas
- `call_tool("list_pods", {"namespace": "default"})` returns formatted pod output
- `call_tool("get_logs", {"pod_name": "...", "namespace": "default"})` returns log lines
- `call_tool("describe_resource", {"resource_type": "pod", ...})` returns full description
- Invalid inputs and missing resources return helpful error messages (not crashes)
- MCP Inspector shows all tools and allows interactive testing
- Claude Code can discover and invoke your tools in conversation

---

## Key Takeaway

An MCP server is a thin protocol wrapper around your existing tooling. The real logic (kubectl calls, parsing, error handling) stays in your tool implementations. MCP just gives it a standard interface that any AI client can discover and use. Build once, connect everywhere.

**Next:** [Lab 6: Multi-Tool Agent](lab6-multi-tool-agent.md)
