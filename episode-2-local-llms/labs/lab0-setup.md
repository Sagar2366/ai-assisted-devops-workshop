# Lab 0: Ollama Setup

> **Mission:** Get Ollama installed, running, and models pulled before writing any code.

---

## Why Run LLMs Locally?

In Episode 1, every API call went over the internet — your K8s logs, your OOM alerts, your incident data, all sent to someone else's server. That works for learning. It doesn't work when you're debugging a production outage at 3 AM with sensitive customer data in the logs.

Local LLMs solve four problems at once:

| Problem | Cloud API | Local Ollama |
|---------|-----------|--------------|
| **Privacy** | Your crash logs travel across the internet to a third-party server | Data never leaves your machine — analyze PII-laden logs freely |
| **Latency** | 200-500ms network round trip per call | Instant — localhost, no network hop |
| **Cost** | Pay per token, adds up fast in pipelines | $0.00 forever, no billing surprises |
| **Availability** | Internet goes down = your AI tooling breaks | Works offline, air-gapped, on a plane |

**The SRE decision framework:** Start local. Move to cloud only when you *need* something local can't give you — larger context windows, frontier reasoning, or multi-modal input. That's the Three Rings model from this series.

**Compliance angle:** If your org has SOC2, HIPAA, or GDPR requirements, "we send production logs to a third-party AI provider" is a conversation with legal. "We run inference on-prem, data never leaves our network" is not.

---

## What You Need

- A laptop (macOS, Linux, or Windows with WSL)
- 8 GB+ RAM (16 GB recommended)
- ~10 GB disk space for models
- Docker (only for Task 8)

**Cost: $0.00** — everything in this episode is free and runs locally.

---

## Step 1: Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows (WSL)
curl -fsSL https://ollama.com/install.sh | sh
```

Or download from [ollama.com/download](https://ollama.com/download).

---

## Step 2: Start the Server

```bash
ollama serve &
```

Ollama runs a local HTTP server on port `11434`. Every API call in this episode hits `http://localhost:11434`.

Verify it's running:
```bash
curl http://localhost:11434
# Should return: "Ollama is running"
```

---

## Step 3: Pull Models

```bash
# Required — used in Tasks 1-8
ollama pull qwen2.5-coder:7b

# Optional — used in Task 4 for model comparison
ollama pull llama3.1:8b
```

Each model is ~4 GB. Pull them before the workshop — don't wait for live download.

---

## Step 4: Install Python Packages

```bash
pip install requests openai
```

- `requests` — for direct Ollama HTTP API (Tasks 1-5)
- `openai` — for OpenAI-compatible API (Task 6)

---

## Step 5: Verify Everything

```bash
python3 demos/ollama/verify_ollama.py
```

You should see all checks pass:
```
  Ollama installed:  [OK]
  Ollama running:    [OK]
  Model qwen2.5-coder:7b:  [OK]
  Python requests:   [OK]
  Python openai:     [OK]
  ALL CHECKS PASSED — Ready for Episode 2!
```

---

## Docker (Task 8 Only)

Task 8 launches Open Web UI via Docker. If you don't have Docker, you can skip Task 8 — the other 7 tasks don't need it.

```bash
# Verify Docker is working
docker info
```

---

## You're Ready

Move on to [Lab 1: First SRE Query](lab1-first-sre-query.md).

---

**No API keys, no credit cards, no cloud accounts.** Everything runs on your machine.
