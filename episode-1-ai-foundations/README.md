# Episode 1: AI Foundations for SRE & DevOps

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

<!-- [Watch on YouTube](https://youtube.com/...) -->

---

## What You'll Learn

By the end of this episode, you'll have ONE mental model — the Payload Shift — that makes every AI tool, agent, and buzzword slot into place, plus your first working API call to Claude with SRE context.

| Concept | One-Line Summary |
|---------|-----------------|
| The Payload Shift | Alerts moved from human dashboards to AI agents. Same infra, new destination. |
| Five Eras of AI | Rule-based → ML → Deep Learning → LLMs/GenAI → AI Agents. Each removed a constraint. |
| How LLMs Work | Training data = Docker layers. Weights = image. Inference = running the container. |
| Context Engineering | 5 things compete for the context window — the #1 skill for building agents |
| Agents = Brain + Hands + Loop | LLM (brain) + Tools (hands) + Reasoning Loop (autonomy) |
| MCP & A2A | Universal adapter for tools (MCP) and agent-to-agent communication (A2A) |
| When Agents Fail | High variability = good fit. Deterministic workflows = use a bash script. |

---

## The Payload Shift — The One Framework You Need

This is the single most important concept in the entire series. Everything builds on this.

```
BEFORE:  Alert → Dashboard → YOU read → YOU fix → YOU report
AFTER:   Alert → AI Agent → Agent reads → Agent fixes → Agent reports
```

Your alerts, logs, and metrics are the payload. They used to go to human dashboards. Now they go to AI agents. Same data, new destination.

### Real-World Scenarios

| Scenario | Today (Human) | With Agents |
|---|---|---|
| **3 AM OOM alert** | You wake up, read dashboard, run kubectl, find the bad deploy, roll back. 45 min. | Agent receives alert, checks logs + recent deploys, rolls back, reports to Slack. 60 sec. |
| **PR merged to main** | CI runs tests. You manually review for security, performance. You deploy and watch. | Agent reviews diff, generates tests, deploys canary, watches metrics, promotes or rolls back. |
| **Cloud cost creep** | You run a monthly audit, find idle resources, write Terraform, create PR. Half a day. | Agent scans weekly, finds waste, generates Terraform with cost estimates, creates PR. You approve. |
| **Cascading failure** | Memory leak → OOM → 12 services down. You spend 45 min finding the root cause. | Agent catches the first OOM, traces the leaking service, rolls back before the cascade. |

---

## Five Eras of AI — Each Removed a Constraint

![Evolution to Agentic Systems](images/evolution-timeline-08.png)
> *Source: AWS — "Building Agentic Systems" Workshop, 2026*

| Era | Constraint Removed | DevOps Example |
|-----|-------------------|----------------|
| Rule-Based AI (1950s-1980s) | Doing everything manually | Static threshold alerting: "If CPU > 80%, page the engineer" |
| Machine Learning (1980s-2010s) | Manual threshold tuning | Anomaly detection — predict disk full in 6 hours based on growth patterns |
| Deep Learning & NLP (2017-2022) | The language barrier | Log classification, intent detection — "Show me pods that keep crashing" works |
| LLMs & Generative AI (2022-2024) | Writing everything from scratch | Generate Terraform, Dockerfiles, K8s manifests, runbooks in seconds |
| AI Agents (Today) | Human execution speed | Detect → diagnose → fix → verify → report — autonomously |

### LLMs + GenAI vs AI Agents

![Request-Response vs Agent Loop](images/request-vs-agent-14.png)
> *Source: AWS — "Building Agentic Systems" Workshop, 2026*

| LLMs + GenAI (Era 4) | AI Agents (Era 5) |
|---|---|
| "Here's a Terraform file" | Writes, plans, applies, and verifies the Terraform |
| "The pod is OOMKilled" | Detects OOM, checks resource limits, patches deployment, confirms fix |
| Answers questions | Completes tasks autonomously |
| Stateless — one prompt, one response | Stateful — multi-step reasoning with memory |
| No tools | Has tools — can run kubectl, call APIs, read logs |

**LLMs are Stack Overflow. AI agents are your senior SRE on-call.**

---

## Context Engineering

The context window is NOT just where you put your prompt — five different things compete for space inside it. Managing this is the #1 skill for building agents.

![Context Engineering and Memory](images/context-engineering-12.png)
> *Source: AWS — "Building Agentic Systems" Workshop, 2026*

| Component | What It Is |
|-----------|-----------|
| System Prompt | Agent persona and foundational instructions |
| Past Context | Conversation history — current + relevant past sessions |
| Tool Definitions | What tools can the agent use? MCP servers, functions, APIs |
| Retrieved Memory | Knowledge from external systems via RAG, runbooks, docs |
| Tool Outputs | Results from tools the agent already called this session |

---

## MCP & A2A

| | MCP (Model Context Protocol) | A2A (Agent-to-Agent) |
|---|---|---|
| **Connects** | Agents ↔ Tools & Data | Agents ↔ Other Agents |
| **Analogy** | USB-C port | HTTP between microservices |
| **When needed** | Single agent using tools | Multi-agent systems |

---

## When Agents Fail

| Agents are good for... | Agents are NOT good for... |
|---|---|
| **High variability** — diverse alert types, many possible root causes | **Deterministic workflows** — output must be exactly reproducible every time |
| **Cognitive load reduction** — analyzing 10,000 log lines, correlating 50 metrics | **Fully structured input** — if input is already perfect, a rules engine is faster |
| **Cross-system orchestration** — spanning APIs, databases, knowledge domains | **Zero tolerance for error** — medical dosing, financial settlements, safety-critical |
| **Human capacity bottlenecks** — 200 alerts per day, 3 on-call engineers | **Simple static automation** — if a bash script solves it, skip the agent |

The sweet spot: problems with repeatable **patterns** but variable **details**.

---

## Try It Yourself

### Prerequisites

```bash
export ANTHROPIC_API_KEY="your-key-here"   # Get from console.anthropic.com
pip install anthropic
```

### Demo: Your First SRE-Aware API Call

```bash
python3 demos/first_api_call.py
```

Send a real Kubernetes alert to Claude with an SRE system prompt. Notice how the system prompt — `"You are a senior SRE with 10 years of Kubernetes experience"` — changes everything about the response.

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-6-latest",
    max_tokens=1024,
    system="You are a senior SRE with 10 years of Kubernetes experience. Be concise and actionable.",
    messages=[
        {
            "role": "user",
            "content": """Analyze this alert and give me a 3-step remediation plan:

ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)"""
        }
    ]
)

print(message.content[0].text)
```

**No API key?** Two free alternatives:

**Ollama (local, free):**
```bash
ollama run llama3.2:3b "You are a senior SRE. A pod named api-server has restarted 15 times. Last log: 'out of memory'. Memory limit 256Mi, usage 255Mi. Give a 3-step fix."
```

**Kiro by AWS (free tier):** Open Kiro, paste the same alert, and ask for a remediation plan.

**Checkpoint:** You should see a structured remediation plan mentioning memory limits and OOM. If you get a 401 error → your API key isn't set. If `ModuleNotFoundError` → run `pip install anthropic`.

---

## AI Landscape for DevOps (2025-2026)

### AI Assistants (question → answer)

| Name | By |
|------|-----|
| ChatGPT | OpenAI |
| Claude | Anthropic |
| Gemini | Google |
| Copilot | Microsoft |
| Meta AI | Meta |
| Perplexity | Perplexity AI |
| Le Chat | Mistral |

### AI Agents (goal → autonomous execution)

| Name | By | Specialty |
|------|-----|-----------|
| Kiro | AWS | Dev workflows, AWS, coding |
| GitHub Copilot Agent | GitHub/Microsoft | Coding, PRs, repo tasks |
| Cursor | Cursor | Agentic code editing |
| Devin | Cognition | Autonomous software engineering |
| Claude Code | Anthropic | Terminal coding agent |
| Gemini Code Assist | Google | Coding, GCP tasks |
| Docker Gordon | Docker | Container workflows |
| Replit Agent | Replit | Build & deploy apps |

### Kubernetes / Cloud Native AI Agents

| Name | By | Specialty |
|------|-----|-----------|
| kagent | Solo.io / CNCF Sandbox | Kubernetes-native agents via CRDs |
| K8sGPT | CNCF Sandbox | Cluster scanning & issue explanation |
| Robusta AI | Robusta | Incident investigation, alerting |
| Botkube | Botkube | ChatOps for K8s (Slack/Teams) |

---

## Cost

This entire episode costs **~$0.02** (one Claude Sonnet API call). Ollama and Kiro demos are free.

---

## Files

| File | What It Does |
|------|-------------|
| [`demos/first_api_call.py`](demos/first_api_call.py) | Your first SRE-aware Claude API call |

---

## What's Next

**Episode 2: Local & Remote LLMs** — Set up Ollama for free local inference, Claude API for cloud, and AWS Bedrock for enterprise. Three backends, one agent framework.

<!-- [Watch Episode 2 →](../episode-2-llms-local-remote/) -->
