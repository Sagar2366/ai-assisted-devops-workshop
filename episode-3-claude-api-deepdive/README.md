# Episode 3: Claude API Deep Dive — Cloud AI for Production SRE

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut | Docker Captain

---

## Where We Are in the Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   CLOUD RING (Claude API)  ← YOU ARE HERE                       │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                         │   │
│   │   TOOL RING (MCP Servers)                               │   │
│   │                                                         │   │
│   │   ┌─────────────────────────────────────────────────┐   │   │
│   │   │                                                 │   │   │
│   │   │   LOCAL (Claude Code CLI)                       │   │   │
│   │   │                                                 │   │   │
│   │   └─────────────────────────────────────────────────┘   │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This episode** focuses on the outermost ring — calling the Claude API directly from your SRE tooling, automation pipelines, and incident response systems.

---

## Course Structure

| # | Section | Description | Lab |
|---|---------|-------------|-----|
| 1 | Setup & Authentication | SDK install, API key management, environment config | [lab-01](labs/lab-01-setup.md) |
| 2 | Model Tiers | Haiku vs Sonnet vs Opus — choosing the right model for SRE workloads | [lab-02](labs/lab-02-model-tiers.md) |
| 3 | Thinking Mode | Extended thinking for complex root-cause analysis | [lab-03](labs/lab-03-thinking-mode.md) |
| 4 | Prompt Caching | Reducing latency and cost for repeated system context | [lab-04](labs/lab-04-prompt-caching.md) |
| 5 | Large Context Windows | Feeding full runbooks, log dumps, and config trees | [lab-05](labs/lab-05-large-context.md) |
| 6 | Streaming | Real-time output for incident dashboards and alert triage | [lab-06](labs/lab-06-streaming.md) |

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Python | 3.10+ |
| Anthropic SDK | `pip install anthropic` |
| API Key | Obtain from [console.anthropic.com](https://console.anthropic.com) |
| Environment Variable | `export ANTHROPIC_API_KEY="sk-ant-..."` |

```bash
# Quick setup
pip install anthropic
export ANTHROPIC_API_KEY="your-key-here"
python -c "import anthropic; print(anthropic.__version__)"
```

---

## File Structure

```
episode-3-claude-api-deepdive/
├── README.md
├── labs/
│   ├── lab-01-setup.md
│   ├── lab-02-model-tiers.md
│   ├── lab-03-thinking-mode.md
│   ├── lab-04-prompt-caching.md
│   ├── lab-05-large-context.md
│   └── lab-06-streaming.md
└── demos/
    ├── incident-triage.py
    ├── log-analyzer.py
    ├── runbook-executor.py
    ├── alert-enrichment.py
    └── streaming-dashboard.py
```

---

## Labs

| Lab | Title | SRE Use Case |
|-----|-------|--------------|
| [lab-01](labs/lab-01-setup.md) | Setup & Authentication | Secure key management in production environments |
| [lab-02](labs/lab-02-model-tiers.md) | Model Tiers | Selecting cost-effective models for alert classification vs deep analysis |
| [lab-03](labs/lab-03-thinking-mode.md) | Thinking Mode | Complex root-cause analysis with extended reasoning chains |
| [lab-04](labs/lab-04-prompt-caching.md) | Prompt Caching | Caching system context for repeated on-call queries |
| [lab-05](labs/lab-05-large-context.md) | Large Context Windows | Processing full incident timelines and multi-service configs |
| [lab-06](labs/lab-06-streaming.md) | Streaming | Real-time triage output during active incidents |

---

## Cost Considerations for SRE Workloads

When integrating the Claude API into production SRE systems, model selection directly impacts both cost and effectiveness:

| Model | Best For | Cost Profile |
|-------|----------|--------------|
| **Haiku** | High-volume, low-latency tasks (alert classification, log filtering, status parsing) | Cheapest — ideal for pipelines processing thousands of events |
| **Sonnet** | Balanced workloads (incident summarization, runbook generation, change analysis) | Best balance of capability and cost for most SRE automation |
| **Opus** | Complex reasoning (root-cause analysis across distributed systems, architecture reviews) | Highest cost — reserve for tasks requiring deep multi-step reasoning |

**Recommendation:** Start with Sonnet for development, use Haiku for high-throughput production paths, and reserve Opus for complex investigative workflows where accuracy justifies the cost.

---

## What Comes Next

| Episode | Title | Focus |
|---------|-------|-------|
| 4 | MCP Servers | Building tool servers that give Claude access to your infrastructure |
| 5 | Claude Code CLI | Interactive SRE workflows from the terminal |
| 6 | Multi-Agent Orchestration | Coordinating multiple Claude agents for incident response |
| 7 | Production Deployment | Hardening, observability, and scaling AI-assisted operations |

---

## Quick Start

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Analyze this alert and suggest triage steps: CPU at 98% on prod-web-03"
        }
    ]
)

print(message.content[0].text)
```

---

*Part of the AI-Assisted DevOps Workshop series. Progress through each episode to build production-grade AI integrations for Site Reliability Engineering.*
