#!/usr/bin/env python3
"""
Episode 6 - Task 5: Complete K8s MCP Server
=============================================

Build a full-featured Kubernetes MCP server with list pods, get logs,
and describe pod tools. This is a production-ready MCP server pattern.

In this task, you will:
- Build a complete MCP server with 3 real-world tools
- Implement proper error handling
- Return realistic kubectl-style output
- See how to run the server for use with Claude

Prerequisites:
- pip install mcp
- Understanding of async Python (asyncio)

The key insight: MCP servers can be as simple or complex as you need.
This one wraps kubectl commands, but you could wrap ANY API or CLI.
"""

import asyncio
import json
from datetime import datetime
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# ============================================================
# CREATE THE MCP SERVER
# ============================================================

server = Server("k8s-tools")

# ============================================================
# MOCK KUBERNETES DATA
# ============================================================
# In production, these would call subprocess.run(["kubectl", ...])
# or use the kubernetes Python client library.

MOCK_PODS = {
    "production": [
        {
            "name": "api-gateway-6d8f7c5b4-x9k2m",
            "namespace": "production",
            "status": "Running",
            "ready": "2/2",
            "restarts": 0,
            "age": "7d",
            "ip": "10.244.1.45",
            "node": "worker-node-01"
        },
        {
            "name": "api-gateway-6d8f7c5b4-y3n7p",
            "namespace": "production",
            "status": "Running",
            "ready": "2/2",
            "restarts": 1,
            "age": "7d",
            "ip": "10.244.2.32",
            "node": "worker-node-02"
        },
        {
            "name": "payment-service-5c4d3e2f1-a8b9c",
            "namespace": "production",
            "status": "Running",
            "ready": "1/1",
            "restarts": 0,
            "age": "3d",
            "ip": "10.244.1.67",
            "node": "worker-node-01"
        },
        {
            "name": "order-service-7e6f5d4c3-k2l3m",
            "namespace": "production",
            "status": "CrashLoopBackOff",
            "ready": "0/1",
            "restarts": 23,
            "age": "1d",
            "ip": "10.244.3.12",
            "node": "worker-node-03"
        },
        {
            "name": "redis-cache-0",
            "namespace": "production",
            "status": "Running",
            "ready": "1/1",
            "restarts": 0,
            "age": "30d",
            "ip": "10.244.2.10",
            "node": "worker-node-02"
        }
    ],
    "monitoring": [
        {
            "name": "prometheus-server-0",
            "namespace": "monitoring",
            "status": "Running",
            "ready": "1/1",
            "restarts": 0,
            "age": "14d",
            "ip": "10.244.1.100",
            "node": "worker-node-01"
        },
        {
            "name": "grafana-7f8e9d0c1-q2w3e",
            "namespace": "monitoring",
            "status": "Running",
            "ready": "1/1",
            "restarts": 0,
            "age": "14d",
            "ip": "10.244.2.101",
            "node": "worker-node-02"
        }
    ]
}

MOCK_LOGS = {
    "api-gateway": """2024-01-15T10:30:01Z [INFO] Incoming request: GET /api/v1/products - client=192.168.1.100
2024-01-15T10:30:01Z [INFO] Upstream response: 200 OK (latency=45ms)
2024-01-15T10:30:02Z [INFO] Incoming request: POST /api/v1/orders - client=192.168.1.105
2024-01-15T10:30:02Z [INFO] Rate limit check: OK (remaining=450/500)
2024-01-15T10:30:03Z [WARN] Upstream timeout: order-service (threshold=5000ms, actual=5200ms)
2024-01-15T10:30:04Z [INFO] Circuit breaker: order-service state=HALF_OPEN
2024-01-15T10:30:05Z [INFO] Health check: all upstreams OK except order-service""",
    "order-service": """2024-01-15T10:29:55Z [INFO] Starting order-service v3.2.1
2024-01-15T10:29:56Z [INFO] Connecting to database: postgres://db.internal:5432/orders
2024-01-15T10:29:57Z [ERROR] Failed to connect to database: connection refused
2024-01-15T10:29:58Z [ERROR] Retrying database connection (attempt 2/5)...
2024-01-15T10:29:59Z [ERROR] Failed to connect to database: connection refused
2024-01-15T10:30:00Z [FATAL] All database connection attempts failed. Exiting.
2024-01-15T10:30:00Z [INFO] Process exited with code 1""",
    "payment-service": """2024-01-15T10:30:01Z [INFO] Processing payment #PAY-98765 amount=$149.99
2024-01-15T10:30:01Z [INFO] Stripe API call: charge created successfully
2024-01-15T10:30:02Z [INFO] Payment confirmed for order #ORD-12345
2024-01-15T10:30:03Z [INFO] Health check: OK (response_time=12ms)
2024-01-15T10:30:04Z [INFO] Processing payment #PAY-98766 amount=$29.99
2024-01-15T10:30:04Z [INFO] Stripe API call: charge created successfully"""
}


# ============================================================
# TOOL REGISTRATION
# ============================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of available tools."""
    return [
        Tool(
            name="list_pods",
            description=(
                "List all pods in a Kubernetes namespace with their current "
                "status, readiness, restart count, and age. Similar to "
                "'kubectl get pods -n <namespace>'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes namespace to query (e.g., 'production', 'monitoring', 'default')"
                    },
                    "status_filter": {
                        "type": "string",
                        "description": "Optional: filter by pod status (e.g., 'Running', 'CrashLoopBackOff', 'Pending')",
                        "enum": ["Running", "CrashLoopBackOff", "Pending", "Failed", "Succeeded"]
                    }
                },
                "required": ["namespace"]
            }
        ),
        Tool(
            name="get_pod_logs",
            description=(
                "Get recent log output from a specific pod. Useful for "
                "debugging errors, investigating crashes, or checking "
                "application behavior. Similar to 'kubectl logs <pod> -n <namespace>'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes namespace where the pod is running"
                    },
                    "pod_name": {
                        "type": "string",
                        "description": "Full pod name (e.g., 'api-gateway-6d8f7c5b4-x9k2m')"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of log lines to retrieve (default: 50, max: 1000)"
                    },
                    "container": {
                        "type": "string",
                        "description": "Container name if pod has multiple containers"
                    }
                },
                "required": ["namespace", "pod_name"]
            }
        ),
        Tool(
            name="describe_pod",
            description=(
                "Get detailed information about a pod including its "
                "configuration, conditions, events, resource usage, "
                "and container details. Similar to 'kubectl describe pod <pod> -n <namespace>'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes namespace"
                    },
                    "pod_name": {
                        "type": "string",
                        "description": "Full pod name to describe"
                    }
                },
                "required": ["namespace", "pod_name"]
            }
        )
    ]


# ============================================================
# TOOL EXECUTION
# ============================================================

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool and return results."""

    try:
        if name == "list_pods":
            return await handle_list_pods(arguments)
        elif name == "get_pod_logs":
            return await handle_get_pod_logs(arguments)
        elif name == "describe_pod":
            return await handle_describe_pod(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'. Available tools: list_pods, get_pod_logs, describe_pod"
            )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def handle_list_pods(arguments: dict) -> list[TextContent]:
    """Handle the list_pods tool call."""
    namespace = arguments.get("namespace", "default")
    status_filter = arguments.get("status_filter")

    pods = MOCK_PODS.get(namespace, [])
    if not pods:
        return [TextContent(
            type="text",
            text=f"No pods found in namespace '{namespace}'. Available namespaces: {list(MOCK_PODS.keys())}"
        )]

    # Apply filter if specified
    if status_filter:
        pods = [p for p in pods if p["status"] == status_filter]

    # Format like kubectl output
    header = f"{'NAME':<45} {'READY':<8} {'STATUS':<20} {'RESTARTS':<10} {'AGE':<6}"
    lines = [header, "-" * len(header)]
    for pod in pods:
        lines.append(
            f"{pod['name']:<45} {pod['ready']:<8} {pod['status']:<20} {pod['restarts']:<10} {pod['age']:<6}"
        )
    lines.append(f"\n{len(pods)} pod(s) in namespace '{namespace}'")

    return [TextContent(type="text", text="\n".join(lines))]


async def handle_get_pod_logs(arguments: dict) -> list[TextContent]:
    """Handle the get_pod_logs tool call."""
    namespace = arguments.get("namespace", "default")
    pod_name = arguments.get("pod_name", "")
    lines = min(arguments.get("lines", 50), 1000)

    # Match pod name to our mock data
    log_key = None
    for key in MOCK_LOGS:
        if key in pod_name:
            log_key = key
            break

    if not log_key:
        return [TextContent(
            type="text",
            text=f"Error from server (NotFound): pods \"{pod_name}\" not found in namespace \"{namespace}\""
        )]

    logs = MOCK_LOGS[log_key]
    log_lines = logs.strip().split("\n")[-lines:]

    output = f"=== Logs from {pod_name} (namespace: {namespace}, last {len(log_lines)} lines) ===\n"
    output += "\n".join(log_lines)

    return [TextContent(type="text", text=output)]


async def handle_describe_pod(arguments: dict) -> list[TextContent]:
    """Handle the describe_pod tool call."""
    namespace = arguments.get("namespace", "default")
    pod_name = arguments.get("pod_name", "")

    # Find the pod in our mock data
    pods = MOCK_PODS.get(namespace, [])
    pod = next((p for p in pods if p["name"] == pod_name), None)

    if not pod:
        return [TextContent(
            type="text",
            text=f"Error from server (NotFound): pods \"{pod_name}\" not found in namespace \"{namespace}\""
        )]

    # Format like kubectl describe output
    is_crashing = pod["status"] == "CrashLoopBackOff"

    description = f"""Name:         {pod['name']}
Namespace:    {pod['namespace']}
Node:         {pod['node']}/10.0.1.{pod['node'][-2:]}
Status:       {pod['status']}
IP:           {pod['ip']}
Controlled By: Deployment/{pod['name'].rsplit('-', 2)[0]}

Containers:
  app:
    Image:         myregistry/{pod['name'].rsplit('-', 2)[0]}:v3.2.1
    Port:          8080/TCP
    State:         {'Waiting (CrashLoopBackOff)' if is_crashing else 'Running'}
    Ready:         {pod['ready'] == '1/1'}
    Restart Count: {pod['restarts']}
    Limits:
      cpu:     500m
      memory:  512Mi
    Requests:
      cpu:     100m
      memory:  256Mi

Conditions:
  Type              Status
  Initialized       True
  Ready             {'False' if is_crashing else 'True'}
  ContainersReady   {'False' if is_crashing else 'True'}
  PodScheduled      True

Events:
  Type     Reason     Age    Message
  ----     ------     ----   -------"""

    if is_crashing:
        description += f"""
  Warning  BackOff    1m     Back-off restarting failed container
  Warning  Failed     2m     Error: container exited with code 1
  Normal   Pulled     3m     Container image pulled successfully
  Normal   Created    3m     Created container app
  Normal   Started    3m     Started container app"""
    else:
        description += f"""
  Normal   Scheduled  {pod['age']}    Successfully assigned to {pod['node']}
  Normal   Pulled     {pod['age']}    Container image already present
  Normal   Created    {pod['age']}    Created container app
  Normal   Started    {pod['age']}    Started container app"""

    return [TextContent(type="text", text=description)]


# ============================================================
# DEMONSTRATION MODE
# ============================================================

async def demonstrate():
    """Demonstrate the server by calling handlers directly."""
    print("=" * 65)
    print("  EPISODE 6 - TASK 5: COMPLETE K8s MCP SERVER")
    print("  A Production-Ready MCP Server Pattern")
    print("=" * 65)
    print()

    # Show available tools
    print("=" * 65)
    print("REGISTERED TOOLS")
    print("=" * 65)
    tools = await list_tools()
    for tool in tools:
        print(f"\n  {tool.name}:")
        print(f"    {tool.description[:70]}...")
    print()

    # Experiment 1: List pods
    print("=" * 65)
    print("EXPERIMENT 1: List Pods in Production")
    print("=" * 65)
    print("-" * 65)
    result = await call_tool("list_pods", {"namespace": "production"})
    for content in result:
        print(content.text)
    print()

    # Experiment 2: Get logs from a crashing pod
    print("=" * 65)
    print("EXPERIMENT 2: Get Logs from Crashing Pod")
    print("=" * 65)
    print("-" * 65)
    result = await call_tool("get_pod_logs", {
        "namespace": "production",
        "pod_name": "order-service-7e6f5d4c3-k2l3m",
        "lines": 10
    })
    for content in result:
        print(content.text)
    print()

    # Experiment 3: Describe a pod
    print("=" * 65)
    print("EXPERIMENT 3: Describe a Problem Pod")
    print("=" * 65)
    print("-" * 65)
    result = await call_tool("describe_pod", {
        "namespace": "production",
        "pod_name": "order-service-7e6f5d4c3-k2l3m"
    })
    for content in result:
        print(content.text)
    print()

    # Experiment 4: Error handling
    print("=" * 65)
    print("EXPERIMENT 4: Error Handling (Pod Not Found)")
    print("=" * 65)
    print("-" * 65)
    result = await call_tool("get_pod_logs", {
        "namespace": "production",
        "pod_name": "nonexistent-pod-abc123"
    })
    for content in result:
        print(content.text)
    print()

    # Key Learning
    print("=" * 65)
    print("KEY LEARNING")
    print("=" * 65)
    print("""
    1. A complete MCP server has:
       - Tool registration (@server.list_tools)
       - Tool execution (@server.call_tool)
       - Proper error handling (try/except, not-found cases)
       - Realistic output formatting

    2. Tools should return data formatted for AI consumption:
       - Structured enough to parse
       - Human-readable enough to understand
       - Include context (namespace, timestamps, etc.)

    3. Error handling is critical:
       - Invalid namespaces -> helpful error message
       - Pod not found -> kubectl-style error
       - Exceptions -> caught and returned as text

    4. To run as a real MCP server (uncomment the main block below):
       python3 task5_k8s_mcp_server.py

    5. Configure in Claude Code's settings:
       {
           "mcpServers": {
               "k8s-tools": {
                   "command": "python3",
                   "args": ["/path/to/task5_k8s_mcp_server.py"]
               }
           }
       }
    """)

    print("=" * 65)
    print("Next: task6_multi_tool_agent.py")
    print("  -> Build an agent that orchestrates multiple tools")
    print("=" * 65)


# ============================================================
# MAIN - Run as demo or as MCP server
# ============================================================

async def run_server():
    """Run as a real MCP server over stdio."""
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(
            read, write,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import sys

    if "--serve" in sys.argv:
        # Run as actual MCP server (for use with Claude Code/Desktop)
        asyncio.run(run_server())
    else:
        # Run in demo mode (shows what the server does)
        asyncio.run(demonstrate())
