# Episode 6: Tools, Agents & MCP Servers

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

---

## What You'll Learn

This episode teaches you to give AI the ability to **TAKE ACTION** — not just answer questions. You will learn to define tools that Claude can call, build the core agent loop (think -> act -> observe -> repeat), and connect everything through MCP (Model Context Protocol) servers. By the end, you will have built a Kubernetes MCP server that lets any AI client query pods, read logs, and manage deployments autonomously.

The progression is deliberate: first you learn how to describe tools to the model, then how to execute those calls, then how to loop until a problem is solved, and finally how to package everything as a reusable MCP server.

---

## 6 Tasks

| Task | Name | What You Learn |
|------|------|----------------|
| 1 | Function Calling | Define tool schemas so Claude knows what actions it can take |
| 2 | Tool Execution | Execute tool calls and return results to the model |
| 3 | Agent Loop | Build the core loop: think -> act -> observe -> repeat |
| 4 | MCP Introduction | Understand Model Context Protocol and why DevOps teams need it |
| 5 | K8s MCP Server | Build a Kubernetes MCP server with pods, logs, and describe |
| 6 | Multi-Tool Agent | Combine everything into an autonomous incident-solving agent |

---

## Prerequisites

- Python 3.10+
- Anthropic API key (`ANTHROPIC_API_KEY` environment variable)
- `pip install anthropic mcp`
- kubectl configured (or we will mock it — no live cluster required)
- Docker installed
- Helm installed (optional, for lab 6)

---

## How to Follow Along

1. Work through labs in order — each builds on the previous
2. Start with `lab0-setup.md` to verify your environment
3. Type out the code (do not copy-paste) — muscle memory matters
4. Each lab has a "What Success Looks Like" section so you know you got it right
5. Experiment: change the tools, add new ones, break things and fix them

---

## File Structure

```
episode-6-tools-agents-mcp/
├── README.md
├── labs/
│   ├── lab0-setup.md
│   ├── lab1-function-calling.md
│   ├── lab2-tool-execution.md
│   ├── lab3-agent-loop.md
│   ├── lab4-mcp-intro.md
│   ├── lab5-k8s-mcp-server.md
│   └── lab6-multi-tool-agent.md
└── demos/
    ├── task1_function_calling.py
    ├── task2_tool_execution.py
    ├── task3_agent_loop.py
    ├── task4_mcp_basics.py
    ├── task5_k8s_mcp_server.py
    └── task6_multi_tool_agent.py
```

---

## Key Concepts

| Concept | What It Is | DevOps Analogy |
|---------|-----------|----------------|
| **Tools** | Structured functions the model can request to call | Runbook procedures an SRE can execute |
| **Agents** | A loop where the model keeps calling tools until done | An SRE working an incident until resolution |
| **MCP** | A standard protocol connecting AI to tools/data sources | USB for AI integrations — one connector for everything |

---

## Episode Structure

| Time | Section | Activity |
|------|---------|----------|
| 0:00 - 0:15 | Setup & Context | Environment check, API keys |
| 0:15 - 0:45 | Function Calling | Define tools Claude can invoke |
| 0:45 - 1:15 | Tool Execution | Execute calls, feed results back |
| 1:15 - 1:45 | Agent Loop | Build think-act-observe cycle |
| 1:45 - 2:15 | MCP Introduction | Protocol concepts + DevOps value |
| 2:15 - 2:45 | K8s MCP Server | Build a real MCP server |
| 2:45 - 3:15 | Multi-Tool Agent | Orchestrate kubectl+docker+helm |
| 3:15 - 3:30 | Wrap-up | Review, next steps |

---

## Links

- [Lab 0: Setup](labs/lab0-setup.md)
- [Lab 1: Function Calling](labs/lab1-function-calling.md)
- [Lab 2: Tool Execution](labs/lab2-tool-execution.md)
- [Lab 3: Agent Loop](labs/lab3-agent-loop.md)
- [Lab 4: MCP Introduction](labs/lab4-mcp-intro.md)
- [Lab 5: K8s MCP Server](labs/lab5-k8s-mcp-server.md)
- [Lab 6: Multi-Tool Agent](labs/lab6-multi-tool-agent.md)

---

**Built by [Sagar Utekar](https://github.com/Sagar2366)** | CNCF Ambassador | Kubestronaut
