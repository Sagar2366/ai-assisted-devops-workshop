# AI-Assisted DevOps Workshop

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut | AI SRE Practitioner

A hands-on, 14-episode YouTube series where you build AI agents that automate real DevOps workflows. No gatekeeping. No paywalls. Everything open source.

Total API cost for ALL demos: **~$3-5**. Ollama demos are free.

---

## Quick Start

```bash
git clone https://github.com/Sagar2366/ai-assisted-devops-workshop.git
cd ai-assisted-devops-workshop
pip install -r requirements.txt
chmod +x demos/setup.sh
./demos/setup.sh
```

If setup completes with 3 pod types visible (Running, ImagePullBackOff, CrashLoopBackOff), you are ready for Episode 1.

---

## Episodes

### Foundations (Ep 0-7) — Understand

| # | Topic | What You Build |
|---|-------|---------------|
| 0 | [Course Overview](episode-0-course-overview/) | -- |
| 1 | [AI Foundations for SRE & DevOps](episode-1-ai-foundations/) | First LLM API call with SRE context across 5 providers |
| 2 | [Local LLMs with Ollama](episode-2-local-llms/) | Ollama deep dive + local-to-cloud swap pattern |
| 3 | [Claude API Deep Dive](episode-3-claude-api-deepdive/) | Model tiers, thinking mode, prompt caching, 200K context |
| 4 | [AWS Bedrock for Enterprise SRE](episode-4-aws-bedrock-enterprise/) | IAM auth, multi-provider gateway, enterprise patterns |
| 5 | [Prompt Engineering for DevOps](episode-5-prompt-engineering/) | Prompt testing framework + 4 production templates |
| 6 | [Tools, Agents & MCP Servers](episode-6-tools-agents-mcp/) | K8s MCP server + core agent loop |
| 7 | [Build a DevOps Copilot](episode-7-devops-copilot-project/) | CLI copilot with safety guardrails + audit logging |

### AI DevOps (Ep 8-12) — Build & Ship

| # | Topic | What You Build |
|---|-------|---------------|
| 8 | [Claude Code Deep Dive](episode-8-claude-code-deepdive/) | CLAUDE.md template + safety/audit hooks |
| 9 | [AI Shell Scripting](episode-9-ai-shell-scripting/) | Script generator, fixer, and converter |
| 10 | [AI-Powered CI/CD & GitOps](episode-10-ai-cicd-gitops/) | AI code reviewer + pipeline optimizer + ArgoCD risk gate |
| 11 | [IaC + AI & Security Scanning](episode-11-iac-ai-security/) | Terraform generator + K8s security scanner |
| 12 | [Deployment Automation](episode-12-ai-deployment-automation/) | Dockerfile + K8s + Compose generator from app analysis |

### Capstone (Ep 13)

| # | Topic | What You Build |
|---|-------|---------------|
| 13 | [Agentic DevOps Platform](episode-13-capstone-agentic-devops/) | Multi-agent platform with FastAPI gateway |

---

## Prerequisites

- Basic Linux/terminal, Docker & Kubernetes fundamentals
- No AI/ML experience needed — we start from zero
- Python 3.10+

```bash
# Core tools
brew install ollama kubectl helm kind docker

# AI tools
npm install -g @anthropic-ai/claude-code
pip install anthropic openai boto3

# Workshop tools
pip install fastapi uvicorn pydantic "mcp[cli]"
```

**Accounts (free tiers work):** [Anthropic API](https://console.anthropic.com) | GitHub | AWS (optional)

---

## What Makes This Different

- **Agents that FIX things** — scale, rollback, restart with safety limits, not just diagnosis
- **3 LLM backends** — Ollama (free/local) + Claude API (cloud) + Bedrock (enterprise)
- **Safety guardrails** — SAFE/RESTRICTED/BLOCKED commands + audit logging on every action
- **12 named frameworks** — mental models that outlast any tool (Payload Shift, Three Rings, Agent Mesh, etc.)
- **Cost transparency** — every demo shows API cost, every episode shows ROI vs commercial tools
- **Interview prep** — real questions woven into every episode + dedicated career episode

---

## License

MIT — use it, fork it, teach it.
