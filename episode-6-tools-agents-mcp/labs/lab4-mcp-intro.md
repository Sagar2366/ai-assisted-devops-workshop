# Lab 4: MCP Introduction — What Is MCP and Why It Matters for DevOps

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

> **Mission:** Understand the Model Context Protocol (MCP), its architecture, and why it is a game-changer for DevOps tool integration.

---

## Concept: The Problem MCP Solves

Without MCP, every AI tool integration is custom:

```
Agent A  ---custom code--->  kubectl
Agent A  ---custom code--->  Docker
Agent A  ---custom code--->  Prometheus
Agent B  ---different code-> kubectl  (duplicated effort!)
Agent B  ---different code-> Docker   (duplicated effort!)
```

With MCP, tools are exposed through a standard protocol:

```
Agent A  ---MCP--->  K8s MCP Server     ----> kubectl
Agent B  ---MCP--->  K8s MCP Server     ----> kubectl
Agent C  ---MCP--->  K8s MCP Server     ----> kubectl

Agent A  ---MCP--->  Docker MCP Server  ----> docker
Agent B  ---MCP--->  Docker MCP Server  ----> docker
```

**DevOps analogy:** MCP is like Kubernetes itself — a standard interface. Just as K8s lets you deploy any container without knowing the underlying infrastructure, MCP lets any AI client use any tool server without custom integration code.

---

## MCP Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌──────────────┐
│   AI Client     │  MCP    │   MCP Server    │  API    │   Backend    │
│  (Agent/IDE)    │◄───────►│  (Your Code)    │◄───────►│  (kubectl,   │
│                 │         │                 │         │   docker)    │
└─────────────────┘         └─────────────────┘         └──────────────┘

The protocol defines:
  - How clients discover available tools
  - How clients call tools with parameters
  - How servers return results
  - How errors are communicated
```

### Key Components

| Component | Role | DevOps Example |
|-----------|------|----------------|
| **MCP Client** | Discovers and calls tools | Claude Code, an agent script |
| **MCP Server** | Exposes tools over the protocol | Your K8s tool server |
| **Tools** | Individual actions the server provides | `list_pods`, `get_logs` |
| **Resources** | Read-only data the server exposes | Cluster config, dashboards |

---

## Why MCP Matters for DevOps

### 1. Reusability
Build a K8s MCP server once — every AI tool can use it. Claude Code, custom agents, VS Code extensions, ChatGPT plugins — all through the same server.

### 2. Standardization
No more one-off integrations. The protocol handles discovery, invocation, and error handling.

### 3. Security Boundary
The MCP server is the gateway. You control what actions are exposed, add auth, rate limiting, and audit logging in one place.

### 4. Composability
Mix and match MCP servers:
- K8s MCP Server + Prometheus MCP Server + PagerDuty MCP Server = Full incident response agent

---

## MCP Server Skeleton (Python)

```python
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# Create the server
server = Server("devops-tools")


@server.list_tools()
async def list_tools():
    """Declare what tools this server provides."""
    return [
        Tool(
            name="get_pod_status",
            description="Get Kubernetes pod status",
            inputSchema={
                "type": "object",
                "properties": {
                    "pod_name": {"type": "string", "description": "Pod name"},
                    "namespace": {"type": "string", "description": "Namespace"}
                },
                "required": ["pod_name"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool invocations."""
    if name == "get_pod_status":
        # Your implementation here
        result = f"Pod {arguments['pod_name']} is Running"
        return [TextContent(type="text", text=result)]
    raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the server over stdio."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## How MCP Differs From Direct Tool Use

| Aspect | Direct Tool Use (Labs 1-3) | MCP Server |
|--------|---------------------------|------------|
| **Integration** | Tools defined in your script | Tools exposed as a service |
| **Reusability** | One script, one set of tools | Any client can connect |
| **Discovery** | Hardcoded tool list | Dynamic via `list_tools()` |
| **Transport** | In-process | stdio, HTTP/SSE, or WebSocket |
| **Ideal for** | Quick prototypes, single agents | Production, shared tooling |

---

## MCP in the DevOps Ecosystem

```
┌─────────────────────────────────────────────────┐
│              Your DevOps MCP Servers             │
├─────────────────┬───────────────┬───────────────┤
│  K8s Server     │ Docker Server │ Helm Server   │
│  - list_pods    │ - list_images │ - list_charts │
│  - get_logs     │ - inspect     │ - install     │
│  - describe     │ - pull/push   │ - upgrade     │
│  - scale        │ - build       │ - rollback    │
└────────┬────────┴───────┬───────┴───────┬───────┘
         │                │               │
         └────────────────┼───────────────┘
                          │ MCP Protocol
         ┌────────────────┼───────────────┐
         │                │               │
    Claude Code     Custom Agent     VS Code
```

---

## What Success Looks Like

- You understand the client-server architecture of MCP
- You can explain why standardization matters for DevOps tooling
- You recognize the skeleton structure of an MCP server
- You see how MCP enables composable, reusable tool servers

---

## Key Takeaway

MCP is the "USB standard" for AI tools. Instead of building custom integrations between every agent and every tool, you build one MCP server per tool domain and any compliant client can use it. For DevOps teams managing dozens of tools, this is the difference between N*M integrations and N+M.

**Next:** [Lab 5: K8s MCP Server](lab5-k8s-mcp-server.md)
