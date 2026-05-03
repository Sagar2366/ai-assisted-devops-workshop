# Episode 2: Local LLMs with Ollama — Run AI on Your Laptop

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut | Docker Captain

---

## What You'll Learn

Run AI models **on your laptop** — no API keys, no internet, no data leaving your machine. Every task uses real SRE scenarios: K8s crash logs, OOM alerts, Prometheus rules.

```
┌──────────────────────────────────────────────┐
│  ENTERPRISE RING (Bedrock / Azure OpenAI)    │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  CLOUD RING (Claude API / OpenAI)    │    │
│  │                                      │    │
│  │  ┌──────────────────────────────┐    │    │
│  │  │  LOCAL RING (Ollama)  ← YOU  │    │    │
│  │  │  Free, private, air-gapped   │    │    │
│  │  │  Start here. Move out only   │    │    │
│  │  │  when you NEED to.           │    │    │
│  │  └──────────────────────────────┘    │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

This is the innermost ring of the Three Rings framework. **Cost: $0.00.**

---

## Course Structure

### Section 0: Prerequisites & Setup

| # | Topic | Lab |
|---|-------|-----|
| 0.1 | Prerequisites | [Lab 0](labs/lab0-setup.md) |
| 0.2 | Installing Ollama | [Lab 0](labs/lab0-setup.md) |
| 0.3 | Pulling Models & Verifying Setup | [Lab 0](labs/lab0-setup.md) |

### Section 1: Getting Started with Ollama

| # | Topic | Task | Lab |
|---|-------|------|-----|
| 1.1 | Ollama Introduction — The Three Rings | — | — |
| 1.2 | Running Your First Model — SRE Log Analysis | Task 1 | [Lab 1](labs/lab1-first-sre-query.md) |
| 1.3 | Essential Ollama CLI Commands — Docker Analogy | Task 2 | [Lab 2](labs/lab2-cli-explorer.md) |
| 1.4 | Models and Model Parameters — Size, Quantization, Context | Task 3 | [Lab 3](labs/lab3-model-parameters.md) |
| 1.5 | Running Different Models — Same Alert, Different Brains | Task 4 | [Lab 4](labs/lab4-model-comparison.md) |

### Section 2: Building AI Applications with Ollama

| # | Topic | Task | Lab |
|---|-------|------|-----|
| 2.1 | Ollama REST API — /api/generate, /api/chat, Streaming, JSON Mode | Task 5 | [Lab 5](labs/lab5-ollama-api.md) |
| 2.2 | OpenAI Compatibility — One-Line Swap, Local to Cloud | Task 6 | [Lab 6](labs/lab6-openai-compat.md) |

### Section 3: Customising & Sharing Models

| # | Topic | Task | Lab |
|---|-------|------|-----|
| 3.1 | Custom Modelfile — Dockerfile for AI | Task 7 | [Lab 7](labs/lab7-custom-modelfile.md) |
| 3.2 | Community Integrations — Open Web UI (ChatGPT for Your Team) | Task 8 | [Lab 8](labs/lab8-open-webui.md) |

### Section 4: Vision Models (Bonus)

| # | Topic | Task | Lab |
|---|-------|------|-----|
| 4.1 | Vision Models — AI That Can See Your Screenshots | Task 9 | [Lab 9](labs/lab9-vision.md) |

### Section 5: Docker Model Runner (Bonus)

| # | Topic | Task | Lab |
|---|-------|------|-----|
| 5.1 | Docker Model Runner — Local LLMs Without Leaving Docker | Task 10 | [Lab 10](labs/lab10-docker-model-runner.md) |

---

## Prerequisites

```bash
# Install Ollama
brew install ollama          # macOS
# curl -fsSL https://ollama.com/install.sh | sh   # Linux

# Start the server
ollama serve &

# Pull models (~4GB each — do this before the workshop)
ollama pull qwen2.5-coder:7b    # Required
ollama pull llama3.1:8b          # Optional (Task 4 comparison)
ollama pull llava:7b             # Optional (Task 9 vision)

# Docker Desktop 4.40+ with Model Runner enabled (Task 10)
# Enable: Docker Desktop → Settings → Model Runner → Enable
docker model pull ai/llama3.2    # Optional (Task 10)

# Python packages
pip install requests openai

# Docker (Task 8 only)
# docker must be installed and running
```

**No API keys. No credit cards. No cloud accounts.**

---

## How to Follow Along

1. **Watch the video** — I write every line from scratch on camera
2. **Follow the [labs](labs/)** — step-by-step guides with concepts and code
3. **After the video** — clone this repo for the complete working code

```bash
git clone https://github.com/Sagar2366/ai-assisted-devops-workshop.git
cd ai-assisted-devops-workshop/episode-2-local-llms
```

---

## Run the Tasks

```bash
# Verify your setup first
python3 demos/ollama/verify_ollama.py

# Section 1: Getting Started with Ollama
python3 demos/ollama/task1_first_sre_query.py
python3 demos/ollama/task2_cli_explorer.py
python3 demos/ollama/task3_model_parameters.py
python3 demos/ollama/task4_model_comparison.py

# Section 2: Building AI Applications
python3 demos/ollama/task5_ollama_api.py
python3 demos/ollama/task6_openai_compat.py

# Section 3: Customising & Sharing Models
python3 demos/ollama/task7_custom_modelfile.py
python3 demos/ollama/task8_open_webui.py

# Section 4: Vision Models (Bonus)
python3 demos/ollama/task9_vision.py

# Section 5: Docker Model Runner (Bonus)
python3 demos/ollama/task10_docker_model_runner.py
```

---

## File Structure

```
episode-2-local-llms/
├── README.md
├── demos/
│   └── ollama/
│       ├── verify_ollama.py            # Setup: environment check
│       ├── task1_first_sre_query.py    # S1: Local LLM + K8s log analysis
│       ├── task2_cli_explorer.py       # S1: CLI commands (Docker analogy)
│       ├── task3_model_parameters.py   # S1: Model metadata + SRE guide
│       ├── task4_model_comparison.py   # S1: Side-by-side model benchmark
│       ├── task5_ollama_api.py         # S2: /api/generate, /api/chat, streaming, JSON
│       ├── task6_openai_compat.py      # S2: OpenAI SDK → local Ollama
│       ├── task7_custom_modelfile.py   # S3: Build a custom SRE model
│       ├── task8_open_webui.py         # S3: Launch Open Web UI via Docker
│       ├── task9_vision.py            # S4: Vision model image analysis
│       ├── task10_docker_model_runner.py # S5: Docker Model Runner + OpenAI SDK
│       └── Modelfile.sre-assistant     # S3: Custom model definition
└── labs/
    ├── lab0-setup.md                   # Setup
    ├── lab1-first-sre-query.md         # Section 1
    ├── lab2-cli-explorer.md            # Section 1
    ├── lab3-model-parameters.md        # Section 1
    ├── lab4-model-comparison.md        # Section 1
    ├── lab5-ollama-api.md              # Section 2
    ├── lab6-openai-compat.md           # Section 2
    ├── lab7-custom-modelfile.md        # Section 3
    ├── lab8-open-webui.md              # Section 3
    ├── lab9-vision.md                  # Section 4 (Bonus)
    └── lab10-docker-model-runner.md    # Section 5 (Bonus)
```

---

## Labs

### Section 0: Prerequisites
- [Lab 0: Setup](labs/lab0-setup.md)

### Section 1: Getting Started with Ollama
- [Lab 1: First SRE Query](labs/lab1-first-sre-query.md)
- [Lab 2: CLI Explorer](labs/lab2-cli-explorer.md)
- [Lab 3: Model Parameters](labs/lab3-model-parameters.md)
- [Lab 4: Model Comparison](labs/lab4-model-comparison.md)

### Section 2: Building AI Applications
- [Lab 5: Ollama API Deep Dive](labs/lab5-ollama-api.md)
- [Lab 6: OpenAI-Compatible API](labs/lab6-openai-compat.md)

### Section 3: Customising & Sharing Models
- [Lab 7: Custom Modelfile](labs/lab7-custom-modelfile.md)
- [Lab 8: Open Web UI](labs/lab8-open-webui.md)

### Section 4: Vision Models (Bonus)
- [Lab 9: Vision Models](labs/lab9-vision.md)

### Section 5: Docker Model Runner (Bonus)
- [Lab 10: Docker Model Runner](labs/lab10-docker-model-runner.md)

---

## Cost

**$0.00** — this entire episode is free. No API keys, no billing, no cloud accounts.

---

## What Comes Next

| Episode | Topic | What You Build |
|---------|-------|----------------|
| **Ep 3** | Claude API Deep Dive | Model tiers, thinking mode, prompt caching, 200K context |
| **Ep 4** | AWS Bedrock for Enterprise SRE | IAM auth, multi-provider gateway, enterprise patterns |
| **Ep 5** | Prompt Engineering | Zero-shot, few-shot, chain-of-thought for DevOps |
| **Ep 6** | Tools, Agents & MCP | Function calling, MCP servers — AI that takes action |
| **Ep 7** | DevOps Copilot | RAG, embeddings — AI that searches YOUR runbooks |

> This is part of a 14-episode series: **AI-Assisted DevOps Workshop** — from zero to a full agentic SRE platform.

---

**Built by [Sagar Utekar](https://github.com/Sagar2366)** | CNCF Ambassador | Kubestronaut
