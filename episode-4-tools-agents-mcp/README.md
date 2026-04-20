# Episode 4: Building Tools, Agents & MCP Servers

- Build 6 Kubernetes tools with safety guardrails
- The core agent loop pattern (observe → think → act → evaluate)
- Tool definitions for Claude API (JSON schema)
- MCP server that exposes K8s tools to any AI client

```
         ┌─────────┐
         │   LLM   │ ← BRAIN (reasons, plans, decides)
         └────┬────┘
              │
         ┌────▼────┐
         │  TOOLS  │ ← HANDS (kubectl, APIs, logs)
         └────┬────┘
              │
         ┌────▼────┐
         │  LOOP   │ ← AUTONOMY (observe → think → act → evaluate)
         └────┬────┘
              │
         ┌────▼────┐
         │   MCP   │ ← UNIVERSAL JOINT (standard protocol for all tools)
         └─────────┘
```

## Setup

```bash
export ANTHROPIC_API_KEY="your-key-here"
pip install anthropic "mcp[cli]"
kind create cluster --name workshop
```

## Files

| File | Description |
|------|-------------|
| `k8s_tools.py` | 6 tool functions: kubectl, pod logs, cluster health, Prometheus query, scale, rollback |
| `tool_definitions.py` | Claude API tool schemas for all 6 tools |
| `agent_loop.py` | Core agent loop |
| `mcp_server.py` | MCP server for Kubernetes (FastMCP) |
