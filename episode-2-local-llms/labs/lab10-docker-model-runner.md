# Lab 10: Docker Model Runner — Local LLMs Without Leaving Docker

> **Mission:** Run LLMs through Docker Desktop's built-in Model Runner — same OpenAI-compatible API you learned in Lab 6, zero additional tools.

---

## The Concept

### Docker as an AI runtime

You already know Docker for containers. Since Docker Desktop 4.40, Docker also runs LLMs natively. No Ollama. No separate install. Models pull from Docker Hub, same as container images.

> **Analogy:** Ollama is like installing a standalone web server (nginx binary). Docker Model Runner is like discovering your container engine already has a built-in web server — same result, fewer moving parts.

### Architecture

```
┌──────────────────────────────────────────────────┐
│  Docker Desktop                                  │
│  ┌────────────────────────────────────────────┐  │
│  │  Inference Engine (pluggable)              │  │
│  │  • llama.cpp (default, CPU + GPU)          │  │
│  │  • vLLM (powerful GPUs, production)        │  │
│  │  • NVIDIA NIMs (containerized inference)   │  │
│  └──────────────────┬─────────────────────────┘  │
│                     │  Runs as HOST PROCESS       │
│                     │  (not inside VM/container)  │
│  ┌──────────────────▼─────────────────────────┐  │
│  │  OpenAI-Compatible Gateway                 │  │
│  │                                            │  │
│  │  From host:      localhost:12434           │  │
│  │  From container: model-runner.docker.internal │
│  │  Path:           /engines/v1               │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  GPU: Metal (Apple), CUDA (NVIDIA),              │
│       ROCm (AMD), Vulkan (any GPU)               │
└──────────────────────────────────────────────────┘
```

Key architecture details:

1. **Host-based execution** — the inference engine runs as a native host process, NOT inside a VM or container. This is why Apple Silicon GPU acceleration works at full speed — there's no VM overhead. This is fundamentally different from running Ollama inside a Docker container.

2. **Engine-agnostic** — ships with llama.cpp by default, but the architecture supports swapping in vLLM (for powerful GPU clusters) or NVIDIA NIMs (containerized inference). Ollama is tied to llama.cpp only.

3. **OCI Artifacts** — models are packaged as standard OCI artifacts (same format as container images). This means they work with any container registry, can be versioned with tags, and fit into existing CI/CD pipelines.

4. **Two access paths** — containers reach the gateway via the internal DNS name `model-runner.docker.internal`. Host processes use `localhost:12434` (requires TCP to be enabled). The Docker socket also works from the host without TCP.

5. **On-demand loading** — when you call the API, Model Runner loads the requested model automatically (if already pulled). You don't need to `docker model run` first. The model stays in memory until another model is requested or a 5-minute inactivity timeout is reached. **Only one model is active in memory at a time** — others are cached on disk and swap in when requested.

6. **Small model expectations** — tiny models (135M-360M parameters like SmolLM2) are fast but will hallucinate on knowledge-heavy questions. They work well for testing API integration and simple tasks. For actual SRE reasoning, use 7B+ models like Qwen 2.5 Coder or Llama 3.2.

### Ollama vs Docker Model Runner

| Dimension | Ollama | Docker Model Runner |
|-----------|--------|---------------------|
| **Install** | Separate binary | Built into Docker Desktop |
| **Model source** | ollama.com/library | Docker Hub `ai/` namespace |
| **API port** | 11434 | 12434 |
| **API format** | Ollama native + OpenAI compat | OpenAI compat + Ollama compat |
| **GPU support** | CPU + GPU | Apple Silicon (Metal), NVIDIA (CUDA), AMD (ROCm), Vulkan (any GPU) |
| **Inference engine** | llama.cpp only | Pluggable: llama.cpp, vLLM, NVIDIA NIMs |
| **Execution model** | Standalone server process | Host process via Docker Desktop (not in VM) |
| **Model format** | Ollama-specific | OCI Artifacts (standard container registry format) |
| **Default quantization** | Varies per model | Q4_K_M |
| **Hugging Face** | No | Yes (`hf.co/` GGUF models) |
| **Docker Compose** | Manual network config | Native `provider` integration |
| **Standalone** | Yes (no Docker needed) | Requires Docker Desktop 4.40+ |
| **Custom Modelfiles** | Yes | No (use Compose or config) |
| **Best for** | Dev experimentation, custom models | Docker-native workflows, Compose stacks |

> **SRE take:** If your team already runs everything in Docker, Model Runner means zero new tooling. If you need custom Modelfiles or an air-gapped machine without Docker Desktop, stick with Ollama. Both expose OpenAI-compatible APIs — your code works with either.

### Why this matters for DevOps

Three reasons Docker Model Runner is relevant for DevOps teams:

1. **One tool instead of two** — your team already has Docker Desktop. Instead of Docker + Ollama, you just use Docker. One install, one upgrade cycle, one thing to manage.
2. **Compose integration** — declare AI model dependencies in `compose.yaml` alongside your app services. `docker compose up` handles the model too.
3. **Docker Hub models** — same pull/push/tag workflow your team already knows. Browse models at [hub.docker.com/u/ai](https://hub.docker.com/u/ai).

### Is Docker Model Runner an Ollama killer?

No. They serve different niches:

- **Ollama** works standalone — no Docker Desktop needed. Great for air-gapped machines, Raspberry Pi, custom Modelfiles, and teams that don't use Docker.
- **Docker Model Runner** is for teams already in the Docker ecosystem. Engine-agnostic architecture (can swap llama.cpp for vLLM or NVIDIA NIMs), native Compose integration, and Docker Hub as the model registry.

They coexist. In fact, Docker Model Runner's API is also Ollama-compatible — tools built for Ollama can talk to Docker Model Runner with minimal changes.

---

## What You'll Build

A Python script that:
1. Verifies Docker Model Runner is enabled
2. Pulls a model via Docker CLI
3. Runs inference via the OpenAI-compatible gateway on port 12434
4. Demonstrates the Ollama → Docker Model Runner swap (same code, different `base_url`)

---

## Quick Demo

```bash
# Enable: Docker Desktop → Settings → Model Runner → Enable
# IMPORTANT: Also enable "host-side TCP support" on port 12434
docker model status
docker model pull ai/llama3.2
docker model run ai/llama3.2 "You are an SRE. What causes OOMKilled in Kubernetes?"
docker model list
python3 demos/ollama/task10_docker_model_runner.py
```

---

## Step 1: Enable Docker Model Runner

**Option A: GUI** — Open Docker Desktop → **Settings** → **Model Runner** → **Enable Docker Model Runner**.

**Option B: CLI** — Or enable from the terminal:

```bash
# Enable Model Runner
docker desktop enable model-runner

# Enable with host-side TCP on port 12434 (needed for host access)
docker desktop enable model-runner --tcp 12434
```

**Important:** If using the GUI, also check **"Enable host-side TCP support"** and set the port to `12434`. Without this, the OpenAI-compatible API won't be accessible from your host machine — only from inside Docker containers via `model-runner.docker.internal`. This is the most common gotcha.

**Windows users:** Also check **"Enable GPU backed inference"** if you have an NVIDIA GPU with CUDA support. You'll need NVIDIA drivers installed and GPU paravirtualization enabled for WSL2.

Apply and restart Docker Desktop. Then verify:

```bash
# Check if Model Runner is active
docker model status

# Should show: "Docker Model Runner is running"

# List models (empty at first)
docker model list
```

If `docker model` shows "unknown command," your Docker Desktop version is too old (need 4.40+).

The CLI commands mirror Docker's container commands — if you know `docker pull`, `docker run`, `docker rm`, you already know `docker model pull`, `docker model run`, `docker model rm`.

---

## Step 2: Pull a Model from Docker Hub

```bash
docker model pull ai/llama3.2
```

Models live under the `ai/` namespace on Docker Hub ([hub.docker.com/u/ai](https://hub.docker.com/u/ai)). Same pull workflow as container images. Default quantization: Q4_K_M.

Model tags follow the scheme `{model}:{parameters}-{quantization}`:

```bash
docker model pull ai/smollm2:360M-Q4_K_M    # 360M params, 4-bit quantization
docker model pull ai/llama3.2                # latest tag (default)
docker model pull ai/qwen2.5-coder:7B-Q8_0  # 7B params, 8-bit quantization
```

Available models:

| Model | Parameters | Size | Best for |
|-------|-----------|------|----------|
| `ai/smollm2` | ~135M-360M | ~256MB | Testing, quick experiments, fast responses |
| `ai/llama3.2` | 1B-3B | ~2GB | General purpose, strong reasoning |
| `ai/qwen2.5-coder` | 7B | ~4GB | Code-focused (same family as our Ollama model) |
| `ai/deepseek-r1` | varies | ~5GB+ | Advanced reasoning |

Just like `docker run`, if you `docker model run` a model that isn't pulled yet, it downloads automatically:

```bash
# Pulls if not local, then runs — same as docker run
docker model run ai/smollm2 "What is Kubernetes?"
```

Hugging Face GGUF models also work:

```bash
docker model pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF
```

List what you've pulled:

```bash
docker model list
```

---

## Step 3: Interactive Chat and Model Management

Two ways to interact via CLI:

```bash
# Single prompt (runs and exits — like a one-shot docker exec)
docker model run ai/llama3.2 "You are a K8s SRE. What causes OOMKilled?"

# Interactive mode (starts a chat session — like docker run -it)
docker model run ai/llama3.2
>>> You are a K8s SRE. A pod is in CrashLoopBackOff with exit code 137. Give me 3 kubectl commands to investigate.
```

Exit interactive mode with `Ctrl+C`.

Model management — same verbs as Docker containers:

```bash
docker model list                    # List local models
docker model pull ai/deepseek-r1    # Download a model
docker model rm ai/smollm2          # Remove a model
docker model status                  # Check if runner is active
docker model configure --context-size 8192 ai/llama3.2   # Adjust parameters
```

---

## Step 4: Use the OpenAI-Compatible API

This is the key insight — Docker Model Runner exposes the same OpenAI-compatible API that Ollama does (Lab 6), just on a different port.

Two access paths depending on where your code runs:

```
From host process:       http://localhost:12434/engines/v1
From Docker container:   http://model-runner.docker.internal/engines/v1
```

You don't need to `docker model run` first — if the model is already pulled, the API loads it on-demand when you make a request. The model stays in memory for 5 minutes of inactivity, then unloads automatically.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:12434/engines/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="ai/llama3.2",
    messages=[
        {"role": "system", "content": "You are a senior SRE. Be concise."},
        {"role": "user", "content": "Write a Prometheus alert rule for pod restart rate > 5 per minute."}
    ],
    temperature=0.1
)
print(response.choices[0].message.content)
```

Port 12434 instead of 11434. Model name uses `ai/` prefix. Everything else is **identical** to Lab 6.

---

## Step 5: The Three-Way Swap

The payoff from Lab 6's OpenAI compatibility pattern — one codebase, three backends:

```python
from openai import OpenAI
import os

# Backend 1: Ollama (Lab 6)
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# Backend 2: Docker Model Runner (this lab)
client = OpenAI(base_url="http://localhost:12434/engines/v1", api_key="not-needed")

# Backend 3: OpenAI Cloud
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# Same code below. Zero changes.
response = client.chat.completions.create(
    model="...",  # model name changes per backend
    messages=[...]
)
```

The entire "local ring" of the Three Rings framework now has two engines: Ollama and Docker Model Runner. Both are free, both are private, both speak the same API.

---

## Step 6: Docker Compose Integration

Docker Model Runner integrates natively with Compose. Declare AI models as service dependencies:

```yaml
services:
  sre-assistant:
    build: .
    environment:
      - LLM_BASE_URL=http://model-runner.docker.internal/engines/v1
    depends_on:
      llama:
        condition: service_started

  llama:
    provider:
      type: model
      options:
        model: ai/llama3.2
```

`docker compose up` pulls the model and starts the gateway automatically. Your app talks to `model-runner.docker.internal` (the internal DNS name for containers) — no port mapping needed, no TCP enable needed. This is different from host access which requires TCP on port 12434.

> **Note:** The `provider` block with `type: model` is Docker Compose's native integration with Model Runner. The model becomes a first-class service — it starts, stops, and scales alongside your application containers.

---

## Step 7: Run It

```bash
python3 demos/ollama/task10_docker_model_runner.py
```

---

## What Success Looks Like

Docker Model Runner responds to your SRE query through the OpenAI SDK — same quality as Ollama, running entirely within Docker Desktop. The three-way swap demonstrates that your code is truly portable across all local backends.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `docker model` not recognized | Model Runner not enabled or Docker Desktop too old | Docker Desktop 4.40+ → Settings → Model Runner → Enable |
| Connection refused on 12434 | Host-side TCP not enabled | Settings → Model Runner → check "Enable host-side TCP support" → set port 12434 → Apply & Restart |
| `docker model status` says not running | Model Runner disabled or Docker Desktop restarted | Re-enable in Settings → Model Runner |
| Model pull fails | Docker Hub connectivity | Check internet, try `docker pull hello-world` first |
| Slow inference | No GPU acceleration | Docker Desktop → Settings → Resources → check GPU is allocated |
| "model not found" in API call | Wrong model name format | Use `ai/llama3.2` not `llama3.2` — always include `ai/` prefix |
| Port 12434 conflict | Another service on that port | Stop conflicting service or change port in Model Runner settings |
| Works from container but not host | Host-side TCP disabled | The gateway works from containers by default; for host access you must enable TCP (Step 1) |
| WSL2 integration issues (Windows) | Beta bug with Docker Model Runner in WSL2 | Use PowerShell instead of WSL terminal; or wait for fix in upcoming Docker Desktop release |
| GPU not detected (Windows) | "Enable GPU backed inference" not checked | Settings → Model Runner → check all three boxes (enable, TCP, GPU) |

---

## Key Takeaway

Docker Model Runner gives you local LLMs without installing anything beyond Docker Desktop. Same OpenAI-compatible API, same code pattern from Lab 6 — your investment in learning the OpenAI SDK pays off across Ollama, Docker, and cloud.

---

**Episode 2 complete.** You now have the full local ring — Ollama setup, CLI, model parameters, model comparison, REST API, OpenAI compatibility, custom Modelfile, Open WebUI, vision, and Docker Model Runner.

Next episode: [Episode 3: Claude API Deep Dive](../../episode-3-claude-api-deepdive/)
