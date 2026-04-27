# Episode 1: AI Foundations for SRE & DevOps

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

---

## What You'll Learn

Every concept is taught through live coding — I write the code from scratch on camera, you follow along.

- Make your first LLM API call (what ChatGPT does behind the scenes)
- System prompts — one line turns a generic chatbot into a senior SRE
- Persona swap — same K8s OOM alert, 3 different expert analyses
- Where LLMs break — hallucination, no live cluster access, no execution
- Basic tool use — the model decides to call a function on its own
- Multi-turn conversations — how memory actually works at the API level
- Context window management — what happens when conversations overflow
- Summarization — compress old messages, keep the critical facts

---

## 9 Tasks

| Task | Name | What You Learn |
|------|------|----------------|
| 1 | First API Call | Send a K8s question, get an AI response — this is what ChatGPT does |
| 2 | System Prompts | Add one line, transform generic output into expert SRE triage |
| 3 | Persona Swap | Same OOM alert analyzed by SRE, Network Engineer, Security Engineer |
| 4 | Limitations | Ask about fake kubectl flags — watch the AI hallucinate with confidence |
| 4b | Tool Use | Define a pod health checker — the model decides when to call it |
| 5 | Conversation History | Multi-turn K8s troubleshooting — the AI remembers context |
| 6 | Context Window | When conversations get too long, slide the window |
| 7 | Summarization | Compress 10 turns into 2 sentences — keep names, tools, constraints |
| 8 | Personalization | Extract an engineer's profile, tailor every response to their stack |

All tasks use real SRE scenarios — K8s OOM alerts, pod crash troubleshooting, incident triage. No "hello world."

---

## 5 AI Providers

Every task works with any of these providers. I demo with Anthropic Claude on camera. The repo includes code for all five after the video goes live.

| Provider | Cost | Install | Get Your Key |
|----------|------|---------|-------------|
| **Google Gemini** | **Free** | `pip install google-generativeai` | [aistudio.google.com](https://aistudio.google.com) |
| Anthropic Claude | Paid | `pip install anthropic` | [console.anthropic.com](https://console.anthropic.com) |
| OpenAI GPT | Paid | `pip install openai` | [platform.openai.com](https://platform.openai.com) |
| AWS Bedrock | Paid | `pip install boto3` | `aws configure` (IAM) |
| MAF (Semantic Kernel) | Paid | `pip install semantic-kernel` | Uses OpenAI key |

---

## Prerequisites

- Python 3.10+
- At least one API key (Google Gemini is free — no credit card needed)

---

## How to Follow Along

1. **Watch the video** — I write every line from scratch, explaining as I go
2. **Follow the [labs](labs/)** — step-by-step guides for each task with concepts, code patterns, and expected output
3. **After the video** — clone this repo for the complete code across all 5 providers

```bash
git clone https://github.com/Sagar2366/ai-assisted-devops-workshop.git
cd ai-assisted-devops-workshop/episode-1-ai-foundations
```

---

## Cost

This entire episode costs **$0.00** with Google Gemini's free tier. With paid providers: ~$0.25 total for all 9 tasks.

---

## What Comes Next

| Episode | Topic | What You Build |
|---------|-------|----------------|
| **Ep 2** | Local & Remote LLMs | Ollama on your machine — no API key, no cloud dependency |
| **Ep 3** | Prompt Engineering | Zero-shot, few-shot, chain-of-thought for DevOps |
| **Ep 4** | Tools, Agents & MCP | Function calling, MCP servers — AI that takes action |
| **Ep 5** | DevOps Copilot | RAG, embeddings — AI that searches YOUR runbooks |

> This is part of a 14-episode series: **AI-Assisted DevOps Workshop** — from zero to a full agentic SRE platform.

---

## Links

- [Labs](labs/) — step-by-step guides for each task
  - [Lab 0: Setup](labs/lab0-setup.md)
  - [Lab 1: First API Call](labs/lab1-first-api-call.md)
  - [Lab 2: System Prompts](labs/lab2-system-prompts.md)
  - [Lab 3: Persona Swap](labs/lab3-persona-swap.md)
  - [Lab 4: Limitations](labs/lab4-limitations.md)
  - [Lab 4b: Basic Tool Use](labs/lab4b-basic-tool.md)
  - [Lab 5: Conversation History](labs/lab5-conversation-history.md)
  - [Lab 6: Context Window](labs/lab6-context-window.md)
  - [Lab 7: Summarization](labs/lab7-summarization.md)
  - [Lab 8: Personalization](labs/lab8-personalization.md)
- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) by Anthropic
<!-- - [Watch on YouTube](https://youtube.com/...) -->

---

**Built by [Sagar Utekar](https://github.com/Sagar2366)** | CNCF Ambassador | Kubestronaut
