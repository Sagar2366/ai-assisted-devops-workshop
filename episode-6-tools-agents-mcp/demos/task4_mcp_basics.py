#!/usr/bin/env python3
"""
AI-Assisted DevOps Workshop | Episode 6 | Sagar Utekar
=======================================================
Task 4: MCP Basics - Building Your First MCP Server

Learn how to expose Kubernetes tools via the Model Context Protocol
(MCP), the open standard for connecting AI models to external tools.

In this task, you will:
- Create an MCP server using the mcp package
- Register 3 tools: list_namespaces, get_pods, describe_pod
- Implement each tool with subprocess kubectl calls (with mock fallback)
- Run the server over stdio with mcp.server.stdio

Prerequisites:
- pip install mcp
- kubectl configured (optional - mock fallback provided)

The key insight: MCP is a STANDARD PROTOCOL. Build your server once,
and any MCP-compatible client (Claude Desktop, Claude Code, etc.)
can use your tools without custom integration.
"""

import asyncio
import json
import subprocess
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# =================================================================
# CREATE THE MCP SERVER
# =================================================================

server = Server("k8s-mcp-basics")


# =================================================================
# MOCK FALLBACK DATA
# =================================================================
# Used when kubectl is not available or not configured.
# In production, the subprocess calls hit a real cluster.

MOCK_NAMESPACES = ["default", "production", "staging", "monitoring", "kube-system"]

MOCK_PODS = {
    "default": [
        {"name": "nginx-demo-7d4b8c6f5-x2k9m", "status": "Running", "ready": "1/1", "restarts": 0, "age": "7d"},
    ],
    "production": [
        {"name": "api-gateway-6d8f7c5b4-x9k2m", "status": "Running", "ready": "2/2", "restarts": 0, "age": "14d"},
        {"name": "payment-service-5c4d3e2f1-a8b9c", "status": "Running", "ready": "1/1", "restarts": 0, "age": "3d"},
        {"name": "order-service-7e6f5d4c3-k2l3m", "status": "CrashLoopBackOff", "ready": "0/1", "restarts": 23, "age": "1d"},
        {"name": "redis-cache-0", "status": "Running", "ready": "1/1", "restarts": 0, "age": "30d"},
    ],
    "staging": [
        {"name": "api-gateway-staging-abc123", "status": "Running", "ready": "1/1", "restarts": 0, "age": "2d"},
        {"name": "order-service-staging-def456", "status": "Running", "ready": "1/1", "restarts": 2, "age": "2d"},
    ],
    "monitoring": [
        {"name": "prometheus-server-0", "status": "Running", "ready": "1/1", "restarts": 0, "age": "30d"},
        {"name": "grafana-7f8e9d0c1-q2w3e", "status": "Running", "ready": "1/1", "restarts": 0, "age": "30d"},
    ],
    "kube-system": [
        {"name": "coredns-5d78c9869d-abc12", "status": "Running", "ready": "1/1", "restarts": 0, "age": "60d"},
        {"name": "kube-proxy-d4e5f", "status": "Running", "ready": "1/1", "restarts": 0, "age": "60d"},
    ],
}

MOCK_DESCRIBE = {
    "order-service-7e6f5d4c3-k2l3m": {
        "name": "order-service-7e6f5d4c3-k2l3m",
        "namespace": "production",
        "node": "worker-node-03",
        "status": "CrashLoopBackOff",
        "ip": "10.244.3.12",
        "image": "registry.internal/order-service:v3.2.1",
        "resources": {
            "limits": {"cpu": "500m", "memory": "256Mi"},
            "requests": {"cpu": "100m", "memory": "128Mi"}
        },
        "last_state": {
            "terminated": {
                "reason": "Error",
                "exit_code": 1,
                "message": "Connection refused: postgres://db.internal:5432"
            }
        },
        "events": [
            {"type": "Warning", "reason": "BackOff", "age": "2m", "message": "Back-off restarting failed container"},
            {"type": "Warning", "reason": "Failed", "age": "3m", "message": "Error: container exited with code 1"},
            {"type": "Normal", "reason": "Pulled", "age": "5m", "message": "Container image pulled successfully"},
        ]
    }
}


# =================================================================
# HELPER: Run kubectl with mock fallback
# =================================================================

def run_kubectl(args: list[str], mock_result: str) -> str:
    """
    Try to run a kubectl command via subprocess.
    If kubectl is not available or fails, return mock data instead.
    """
    try:
        result = subprocess.run(
            ["kubectl"] + args,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout
        # kubectl command failed - use mock fallback
        return mock_result
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # kubectl not installed or timed out - use mock fallback
        return mock_result


# =================================================================
# TOOL REGISTRATION
# =================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Declare the tools this MCP server exposes to clients."""
    return [
        Tool(
            name="list_namespaces",
            description=(
                "List all Kubernetes namespaces in the cluster. "
                "Use this to discover what namespaces exist before "
                "querying for pods. Similar to 'kubectl get namespaces'."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_pods",
            description=(
                "List all pods in a specific Kubernetes namespace with "
                "their status, readiness, and restart count. Similar to "
                "'kubectl get pods -n <namespace>'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes namespace to query (e.g., 'default', 'production')"
                    }
                },
                "required": ["namespace"]
            }
        ),
        Tool(
            name="describe_pod",
            description=(
                "Get detailed information about a specific pod including "
                "its configuration, resource limits, container states, "
                "and recent events. Similar to 'kubectl describe pod'."
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
                        "description": "Full name of the pod to describe"
                    }
                },
                "required": ["namespace", "pod_name"]
            }
        )
    ]


# =================================================================
# TOOL EXECUTION
# =================================================================

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool invocations from MCP clients."""
    try:
        if name == "list_namespaces":
            return handle_list_namespaces()
        elif name == "get_pods":
            return handle_get_pods(arguments)
        elif name == "describe_pod":
            return handle_describe_pod(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'. Available: list_namespaces, get_pods, describe_pod"
            )]
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


def handle_list_namespaces() -> list[TextContent]:
    """List namespaces using kubectl (with mock fallback)."""
    # Build mock output in kubectl style
    mock_output = "NAME            STATUS   AGE\n"
    for ns in MOCK_NAMESPACES:
        mock_output += f"{ns:<16}Active   30d\n"
    mock_output += f"\n{len(MOCK_NAMESPACES)} namespace(s) in cluster"

    # Try real kubectl, fall back to mock
    output = run_kubectl(
        ["get", "namespaces", "--no-headers",
         "-o", "custom-columns=NAME:.metadata.name,STATUS:.status.phase,AGE:.metadata.creationTimestamp"],
        mock_output
    )

    return [TextContent(type="text", text=output)]


def handle_get_pods(arguments: dict) -> list[TextContent]:
    """List pods in a namespace using kubectl (with mock fallback)."""
    namespace = arguments.get("namespace", "default")

    # Build mock output in kubectl-style format
    pods = MOCK_PODS.get(namespace, [])
    if not pods:
        mock_output = f"No resources found in {namespace} namespace."
    else:
        header = f"{'NAME':<45} {'READY':<8} {'STATUS':<20} {'RESTARTS':<10} {'AGE'}"
        lines = [header]
        for pod in pods:
            lines.append(
                f"{pod['name']:<45} {pod['ready']:<8} {pod['status']:<20} {pod['restarts']:<10} {pod['age']}"
            )
        lines.append(f"\n{len(pods)} pod(s) in namespace '{namespace}'")
        mock_output = "\n".join(lines)

    # Try real kubectl, fall back to mock
    output = run_kubectl(["get", "pods", "-n", namespace], mock_output)

    return [TextContent(type="text", text=output)]


def handle_describe_pod(arguments: dict) -> list[TextContent]:
    """Describe a pod using kubectl (with mock fallback)."""
    namespace = arguments.get("namespace", "default")
    pod_name = arguments.get("pod_name", "")

    # Check if we have detailed mock data for this pod
    desc = MOCK_DESCRIBE.get(pod_name)
    if desc:
        containers = desc["resources"]
        events = desc["events"]
        mock_output = f"""Name:         {desc['name']}
Namespace:    {desc['namespace']}
Node:         {desc['node']}
Status:       {desc['status']}
IP:           {desc['ip']}

Containers:
  app:
    Image:      {desc['image']}
    State:      Waiting (CrashLoopBackOff)
    Limits:     cpu={containers['limits']['cpu']}, memory={containers['limits']['memory']}
    Requests:   cpu={containers['requests']['cpu']}, memory={containers['requests']['memory']}
    Last State: Terminated
      Reason:    {desc['last_state']['terminated']['reason']}
      Exit Code: {desc['last_state']['terminated']['exit_code']}
      Message:   {desc['last_state']['terminated']['message']}

Events:
  TYPE      REASON     AGE    MESSAGE"""
        for event in events:
            mock_output += f"\n  {event['type']:<9} {event['reason']:<10} {event['age']:<6} {event['message']}"
    else:
        # Check if the pod exists in our pod list
        pods = MOCK_PODS.get(namespace, [])
        pod = next((p for p in pods if p["name"] == pod_name), None)
        if pod:
            mock_output = (
                f"Name:      {pod['name']}\n"
                f"Namespace: {namespace}\n"
                f"Status:    {pod['status']}\n"
                f"Ready:     {pod['ready']}\n"
                f"Restarts:  {pod['restarts']}\n"
                f"Age:       {pod['age']}"
            )
        else:
            mock_output = f"Error from server (NotFound): pods \"{pod_name}\" not found in namespace \"{namespace}\""

    # Try real kubectl, fall back to mock
    output = run_kubectl(["describe", "pod", pod_name, "-n", namespace], mock_output)

    return [TextContent(type="text", text=output)]


# =================================================================
# DEMONSTRATION MODE
# =================================================================

async def demonstrate():
    """Show what the MCP server does by calling handlers directly."""
    print()
    print("=" * 65)
    print("  EPISODE 6 - TASK 4: MCP BASICS")
    print("  AI-Assisted DevOps Workshop | Sagar Utekar")
    print("=" * 65)
    print()
    print("  This MCP server exposes 3 Kubernetes tools:")
    print("    1. list_namespaces  - Discover available namespaces")
    print("    2. get_pods         - List pods in a namespace")
    print("    3. describe_pod     - Get detailed pod information")
    print()

    # Show registered tools
    print("=" * 65)
    print("REGISTERED TOOLS (what clients see via list_tools)")
    print("=" * 65)
    registered_tools = await list_tools()
    for tool in registered_tools:
        print(f"\n  Tool: {tool.name}")
        print(f"  Description: {tool.description[:70]}...")
        required = tool.inputSchema.get("required", [])
        print(f"  Required params: {required if required else '(none)'}")
    print()

    # -----------------------------------------------------------------
    # Experiment 1: List Namespaces
    # -----------------------------------------------------------------
    print("=" * 65)
    print("EXPERIMENT 1: list_namespaces")
    print("=" * 65)
    print("-" * 65)
    result = await call_tool("list_namespaces", {})
    for content in result:
        print(content.text)
    print()

    # -----------------------------------------------------------------
    # Experiment 2: Get Pods in Production
    # -----------------------------------------------------------------
    print("=" * 65)
    print("EXPERIMENT 2: get_pods (namespace='production')")
    print("=" * 65)
    print("-" * 65)
    result = await call_tool("get_pods", {"namespace": "production"})
    for content in result:
        print(content.text)
    print()

    # -----------------------------------------------------------------
    # Experiment 3: Describe a Crashing Pod
    # -----------------------------------------------------------------
    print("=" * 65)
    print("EXPERIMENT 3: describe_pod (crashing pod)")
    print("=" * 65)
    print("-" * 65)
    result = await call_tool("describe_pod", {
        "namespace": "production",
        "pod_name": "order-service-7e6f5d4c3-k2l3m"
    })
    for content in result:
        print(content.text)
    print()

    # -----------------------------------------------------------------
    # Experiment 4: Error Handling
    # -----------------------------------------------------------------
    print("=" * 65)
    print("EXPERIMENT 4: Error handling (pod not found)")
    print("=" * 65)
    print("-" * 65)
    result = await call_tool("describe_pod", {
        "namespace": "production",
        "pod_name": "nonexistent-pod-xyz"
    })
    for content in result:
        print(content.text)
    print()

    # How to run as a real MCP server
    print("=" * 65)
    print("RUNNING AS A REAL MCP SERVER")
    print("=" * 65)
    print("""
    1. Start in server mode:
       python3 task4_mcp_basics.py --serve

    2. Configure in Claude Code (~/.claude/settings.json):
       {
           "mcpServers": {
               "k8s-basics": {
                   "command": "python3",
                   "args": ["/path/to/task4_mcp_basics.py", "--serve"]
               }
           }
       }

    3. Claude Code will automatically:
       - Launch this script as a subprocess
       - Call list_tools() to discover available tools
       - Invoke tools when Claude needs K8s information
    """)

    # Key Learning
    print("=" * 65)
    print("KEY LEARNING")
    print("=" * 65)
    print("""
    1. MCP server structure:
       - server = Server("name")        # Create the server
       - @server.list_tools()           # Declare available tools
       - @server.call_tool()            # Handle tool invocations
       - mcp.server.stdio.stdio_server  # Run over stdio transport

    2. Each tool uses subprocess to call kubectl:
       - subprocess.run(["kubectl", ...]) for real clusters
       - Mock fallback when kubectl is unavailable
       - Timeout handling for resilience

    3. Tool results are TextContent objects:
       - Always return text (even for errors)
       - Format output for AI readability
       - Include helpful context (namespace, counts)

    4. MCP handles all the plumbing:
       - Tool discovery (list_tools)
       - Invocation routing (call_tool by name)
       - Transport (stdio for local, SSE for remote)
       - Error propagation

    5. Build ONCE, use from ANY MCP client:
       - Claude Desktop, Claude Code, VS Code
       - No custom API integration needed per client
    """)

    print("=" * 65)
    print("Next: task5_k8s_mcp_server.py")
    print("  -> Build a complete, production-ready K8s MCP server")
    print("=" * 65)


# =================================================================
# MAIN - Run as MCP server (stdio) or in demo mode
# =================================================================

async def run_server():
    """Run the MCP server over stdio for use with Claude Desktop/Code."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import sys

    if "--serve" in sys.argv:
        # Run as a real MCP server over stdio
        # Usage: python3 task4_mcp_basics.py --serve
        asyncio.run(run_server())
    else:
        # Run in demo mode (shows what the server does)
        asyncio.run(demonstrate())
