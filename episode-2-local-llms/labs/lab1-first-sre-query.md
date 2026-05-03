# Lab 1: First SRE Query — AI on Your Laptop

> **Mission:** Feed a real Kubernetes CrashLoopBackOff log to a local LLM and get triage advice — zero cost, zero internet, zero data leakage.

---

## The Concept

### What is Ollama?

Ollama is Docker for AI models. Same mental model: pull a model (like pulling an image), run it (like starting a container), delete it when you're done. The model lives as a file on disk — not a running service you deploy.

| Docker | Ollama | What happens |
|--------|--------|--------------|
| `docker pull nginx` | `ollama pull qwen2.5-coder:7b` | Download to local storage |
| `docker run nginx` | `ollama run qwen2.5-coder:7b` | Start using it |
| `docker images` | `ollama list` | See what's on disk |
| `docker rmi nginx` | `ollama rm qwen2.5-coder:7b` | Free up space |

If you know Docker, you already know Ollama's workflow.

---

### The friction Ollama removes

Open-source models aren't "download and double-click." When Meta releases LLaMA, they release raw weight files — billions of floating-point numbers in a format your laptop doesn't natively understand. Before Ollama, getting one of these models running meant:

- Figuring out the right **storage format** (GGUF? GPTQ? AWQ?) for your hardware
- Manually **quantizing** the weights to fit in your RAM
- Configuring **memory allocation** so the model loads without crashing your system
- Handling **compatibility issues** between model versions, dependencies, and your OS

Ollama handles all of this. It downloads pre-quantized models in the right format, stores them in a standard location, loads them into memory efficiently, and exposes a clean API. You focus on using the model — not on making it run.

> **Analogy:** It's like the difference between compiling Nginx from source with all its dependencies vs running `docker pull nginx`. The end result is the same, but one path has 45 minutes of friction and the other has zero.

---

### How it works under the hood

Ollama wraps **llama.cpp** — a C++ inference engine that runs transformer models on commodity hardware (your laptop's CPU or GPU). The models are stored in **GGUF format** — a single binary file containing the weights, tokenizer, and metadata.

```
  Ollama (CLI/API)
       ↓
  llama.cpp (inference engine)
       ↓
  GGUF file on disk (~4 GB for a 7B model)
       ↓
  Your CPU/GPU does the math
```

When you run `ollama serve`, it starts an HTTP server on port `11434`. Every call to that server loads the model into RAM (or keeps it warm if already loaded) and runs inference. Same pattern as any microservice — except instead of a database behind it, there's a neural network.

---

### Open-weight models — what you're actually running

These aren't models you trained. Companies like Meta (LLaMA), Alibaba (Qwen), and Mistral release trained model weights publicly. "Open-weight" means you can download and run them — the training cost millions of dollars and thousands of GPUs, but inference on the result is free on your hardware.

Think of it like using a pre-built Docker image from Docker Hub — someone else built it, you just run it.

---

### Local vs Cloud — the two paths

In Episode 1, every prompt went over the internet. Here, everything stays on localhost:

```
  Episode 1 (Cloud):     Your Laptop  →  Internet  →  Cloud API  →  Response
  Episode 2 (Local):     Your Laptop  →  localhost:11434  →  Response
```

**When local wins:** Privacy-sensitive logs, rapid iteration, offline environments, cost-sensitive pipelines, quick prototyping.

**When cloud wins:** You need frontier-level reasoning (Claude Opus, GPT-4o), 200K+ token context windows, or you're processing at scale (thousands of requests/second).

For most SRE triage tasks — analyzing a crash log, generating a kubectl command, summarizing an incident — a 7B local model is good enough and costs nothing.

---

### The Ollama API — just HTTP

Ollama exposes a REST API at `http://localhost:11434`. Same HTTP you use for Prometheus, Grafana, or any internal service. `POST` a JSON body with a model name and prompt, get a JSON response with the generated text.

No SDK required — `curl` or `requests.post()` is all you need.

---

## What You'll Build

A Python script that:
1. Sends a real K8s CrashLoopBackOff log to local Ollama
2. Gets root cause analysis and kubectl commands back
3. Generates a kubectl one-liner to find all crashing pods

---

## Step 1: The Ollama API Endpoint

```python
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
```

Port `11434` is Ollama's default. `/api/generate` takes a prompt and returns a response.

---

## Step 2: Send a K8s Log

```python
response = requests.post(
    OLLAMA_URL,
    json={
        "model": "qwen2.5-coder:7b",
        "prompt": "You are a Kubernetes SRE. Analyze this log...",
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_ctx": 4096
        }
    }
)

result = response.json()["response"]
```

- `model` — which local model to use
- `stream: False` — get the full response at once (we'll stream in Task 5)
- `temperature: 0.1` — low randomness for consistent SRE advice
- `num_ctx: 4096` — context window in tokens

---

## Step 3: Run It

```bash
python3 demos/ollama/task1_first_sre_query.py
```

---

## What Success Looks Like

The model identifies:
- **Root cause:** OOM (exit code 137 + OOM event in logs)
- **Immediate fix:** Increase memory limits
- **kubectl command:** Something like `kubectl describe pod` or `kubectl logs`

The quality won't match Claude Opus — this is a 7B model on your laptop. But it's free, instant, and your production logs never left your machine.

---

## Key Takeaway

Local LLMs are the innermost ring of the Three Rings framework. Start here — zero cost, zero risk, zero data leakage. Move to cloud APIs only when local quality isn't enough.

---

Next: [Lab 2: CLI Explorer](lab2-cli-explorer.md)
