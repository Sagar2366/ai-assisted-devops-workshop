# Episode 13: Agentic DevOps Platform (Capstone)

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

---

## What You'll Build

A production-ready **multi-agent DevOps platform** — the culmination of everything from Episodes 1-12. You'll build a FastAPI gateway that accepts natural language DevOps requests, routes them to specialist AI agents (Kubernetes, CI/CD, Security, Infrastructure-as-Code), orchestrates multi-agent collaboration for complex tasks, and enforces safety guardrails on every action.

This is what an AI-native SRE platform looks like. Not a chatbot — a platform.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENTIC DEVOPS PLATFORM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   FastAPI Gateway                          │  │
│  │  POST /ask    POST /workflow    GET /health               │  │
│  │  POST /agent/{name}    GET /audit    WebSocket /ws        │  │
│  └────────────────────────┬──────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────▼──────────────────────────────────┐  │
│  │                   Safety Layer                             │  │
│  │  ┌─────────┐  ┌──────────────┐  ┌─────────────────────┐  │  │
│  │  │  SAFE   │  │  RESTRICTED  │  │      BLOCKED        │  │  │
│  │  │  read   │  │  scale/restart│  │  delete namespace   │  │  │
│  │  │  list   │  │  deploy      │  │  drop database      │  │  │
│  │  │  describe│  │  modify config│  │  disable auth       │  │  │
│  │  └─────────┘  └──────────────┘  └─────────────────────┘  │  │
│  └────────────────────────┬──────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────▼──────────────────────────────────┐  │
│  │                   Agent Router                             │  │
│  │  Analyzes intent → selects specialist → delegates         │  │
│  └──┬──────────┬──────────┬──────────┬───────────────────────┘  │
│     │          │          │          │                          │
│  ┌──▼───┐  ┌──▼───┐  ┌──▼───┐  ┌──▼───┐                      │
│  │ K8s  │  │ CI/CD│  │ Sec  │  │ IaC  │   Specialist Agents   │
│  │Agent │  │Agent │  │Agent │  │Agent │                        │
│  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘                      │
│     │          │          │          │                          │
│  ┌──▼──────────▼──────────▼──────────▼───────────────────────┐  │
│  │              Multi-Agent Orchestrator                      │  │
│  │  Complex workflows → parallel agents → merge results      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Audit Logger                             │  │
│  │  Every request → action → result logged with trace ID     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                     LLM Backends                                │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────────┐   │
│  │  Ollama  │  │  Claude API  │  │  AWS Bedrock           │   │
│  │  (local) │  │  (cloud)     │  │  (enterprise)          │   │
│  └──────────┘  └──────────────┘  └────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ask` | Natural language DevOps request → routed to best agent |
| POST | `/workflow` | Multi-step workflow → orchestrated across agents |
| POST | `/agent/{name}` | Direct call to a specific specialist agent |
| GET | `/health` | Platform health check with agent status |
| GET | `/audit` | Query audit log (filtered by time, agent, action) |
| GET | `/agents` | List available agents and their capabilities |
| WS | `/ws` | WebSocket for streaming agent responses |

---

## Specialist Agents

| Agent | Domain | Capabilities |
|-------|--------|--------------|
| **K8s Agent** | Kubernetes | Troubleshoot pods, scale deployments, restart services, analyze logs |
| **CI/CD Agent** | Pipelines | Review PRs, optimize pipelines, diagnose build failures, suggest improvements |
| **Security Agent** | Security | Scan manifests, audit RBAC, check CVEs, review network policies |
| **IaC Agent** | Terraform/IaC | Generate modules, review plans, detect drift, optimize costs |

---

## 7 Labs

| Lab | Name | What You Build |
|-----|------|----------------|
| 0 | Setup | Install dependencies, configure LLM backends, verify platform starts |
| 1 | Architecture | Design multi-agent system: router, specialists, orchestrator patterns |
| 2 | FastAPI Gateway | Build the REST API with request validation and streaming |
| 3 | Agent Router | Intent classification and intelligent routing to specialists |
| 4 | Specialist Agents | Build four domain experts with tool-use and memory |
| 5 | Orchestration | Multi-agent collaboration for complex cross-domain workflows |
| 6 | Production Ready | Auth, rate limiting, observability, circuit breakers, graceful degradation |

---

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Ollama running locally (for local LLM backend)
- At least one API key: Anthropic (`ANTHROPIC_API_KEY`) or AWS Bedrock configured
- Completed Episodes 1-12 (concepts build progressively)

---

## Quick Start

```bash
# Clone and navigate
cd ai-assisted-devops-workshop/episode-13-capstone-agentic-devops/demos

# Install dependencies
pip install -r requirements.txt

# Set your LLM backend
export ANTHROPIC_API_KEY="your-key-here"

# Run the platform
uvicorn main:app --reload --port 8000

# Test it
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "Why is my payment-service pod CrashLoopBackOff?"}'
```

---

## Run with Docker

```bash
cd demos
docker-compose up -d

# Platform: http://localhost:8000
# Docs:     http://localhost:8000/docs
# Metrics:  http://localhost:9090 (Prometheus)
# Traces:   http://localhost:16686 (Jaeger)
```

---

## How to Follow Along

1. **Watch the video** — I build the entire platform from scratch, explaining every design decision
2. **Follow the [labs](labs/)** — step-by-step guides from setup to production-ready
3. **After the video** — clone this repo for the complete platform code

```bash
git clone https://github.com/Sagar2366/ai-assisted-devops-workshop.git
cd ai-assisted-devops-workshop/episode-13-capstone-agentic-devops
```

---

## Episode Map — How Everything Connects

| Episode | Concept | Used In This Capstone |
|---------|---------|----------------------|
| 1 | AI Foundations | LLM calls from every agent |
| 2 | Local LLMs | Ollama backend for air-gapped environments |
| 3 | Prompt Engineering | System prompts for each specialist agent |
| 4 | Chains & Pipelines | Multi-step agent reasoning |
| 5 | RAG | Knowledge retrieval for runbook context |
| 6 | Tool Use | Agents calling kubectl, terraform, trivy |
| 7 | Agents | Each specialist is a ReAct agent |
| 8 | Multi-Agent | Orchestrator coordinates specialists |
| 9 | Safety | SAFE/RESTRICTED/BLOCKED guardrails |
| 10 | Evaluation | Agent response quality metrics |
| 11 | MLOps | Model versioning and A/B testing |
| 12 | Production AI | Rate limiting, caching, observability |

---

## What Comes Next

This is the capstone — you've built a complete AI-native DevOps platform. From here:

| Path | Description |
|------|-------------|
| **Extend** | Add new specialist agents (database, networking, cost optimization) |
| **Deploy** | Run on Kubernetes with Helm charts and GitOps |
| **Enterprise** | Add SSO, multi-tenancy, and approval workflows |
| **Open Source** | Package as a CLI tool or Slack bot for your team |

> This is the final episode of the **AI-Assisted DevOps Workshop** — a 14-episode series from zero to a full agentic SRE platform.

---

## Links

- [Labs](labs/) — step-by-step guides
  - [Lab 0: Setup](labs/lab0-setup.md)
  - [Lab 1: Architecture](labs/lab1-architecture.md)
  - [Lab 2: FastAPI Gateway](labs/lab2-fastapi-gateway.md)
  - [Lab 3: Agent Router](labs/lab3-agent-router.md)
  - [Lab 4: Specialist Agents](labs/lab4-specialist-agents.md)
  - [Lab 5: Orchestration](labs/lab5-orchestration.md)
  - [Lab 6: Production Ready](labs/lab6-production-ready.md)
- [Demos](demos/) — complete platform source code
- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) by Anthropic
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Built by [Sagar Utekar](https://github.com/Sagar2366)** | CNCF Ambassador | Kubestronaut
