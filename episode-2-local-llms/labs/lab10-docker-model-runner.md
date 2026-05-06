# Lab 10: Docker Model Runner — Local LLMs Without Leaving Docker

> **Mission:** Run LLMs through Docker Desktop's built-in Model Runner — same OpenAI-compatible API as Lab 6, zero additional tools.

---

## The Concept

Since Docker Desktop 4.40, Docker runs LLMs natively. No Ollama, no separate install. Models pull from Docker Hub like container images.

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
│                     │  Runs as HOST PROCESS      │
│                     │  (not inside VM/container) │
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

**Key details:**

- **Host-based execution** — inference engine runs as a native host process, not in a VM. This is why Apple Silicon GPU acceleration works at full speed.
- **Engine-agnostic** — llama.cpp by default; supports vLLM or NVIDIA NIMs.
- **OCI Artifacts** — models use the same format as container images, so they work with any registry and fit into existing CI/CD pipelines.
- **Two access paths** — containers use `model-runner.docker.internal`; host processes use `localhost:12434` (requires TCP enabled).
- **On-demand loading** — the API loads a pulled model automatically on first request. It unloads after 5 minutes of inactivity. Only one model is active in memory at a time.
- **Model size matters** — tiny models (135M–360M params) are fast but hallucinate on knowledge tasks. Use 7B+ (Qwen 2.5 Coder, Llama 3.2) for real SRE reasoning.

### Ollama vs Docker Model Runner

| Dimension | Ollama | Docker Model Runner |
|-----------|--------|---------------------|
| **Install** | Separate binary | Built into Docker Desktop |
| **Model source** | ollama.com/library | Docker Hub `ai/` namespace |
| **API port** | 11434 | 12434 |
| **API format** | Ollama native + OpenAI compat | OpenAI compat + Ollama compat |
| **GPU support** | CPU + GPU | Metal, CUDA, ROCm, Vulkan |
| **Inference engine** | llama.cpp only | Pluggable: llama.cpp, vLLM, NVIDIA NIMs |
| **Execution model** | Standalone server | Host process via Docker Desktop |
| **Model format** | Ollama-specific | OCI Artifacts |
| **Default quantization** | Varies | Q4_K_M |
| **Hugging Face** | No | Yes (`hf.co/` GGUF models) |
| **Docker Compose** | Manual network config | Native `provider` integration |
| **Standalone** | Yes | Requires Docker Desktop 4.40+ |
| **Custom Modelfiles** | Yes | No |
| **Best for** | Dev experimentation, custom models | Docker-native workflows |

They coexist — Docker Model Runner is also Ollama-compatible, so tools built for Ollama work with minimal changes. Choose Ollama for standalone/air-gapped setups or custom Modelfiles; choose Docker Model Runner if your team is already Docker-native.

---

## What You'll Build

1. **Steps 1–7** — Enable, pull, chat, and call the API
2. **Step 8** — SRE Log Analyzer: containerized FastAPI service backed by Model Runner, run with `docker compose up`
3. **Step 9** — Open WebUI + Docker Model Runner (same UI as Lab 8, different backend)
4. **Step 10** — Vision Monitor: real-time webcam analysis via a local vision model

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

# SRE Log Analyzer (Step 8)
cd demos/docker-model-runner && docker compose up --build
# Then: curl http://localhost:8000/analyze/oomkilled

# Vision Monitor (Step 10)
docker model pull ai/smolvlm:500M-Q8_0
open demos/docker-model-runner/vision-monitor.html
```

---

## Step 1: Enable Docker Model Runner

**Option A: GUI** — Docker Desktop → **Settings** → **Model Runner** → **Enable Docker Model Runner** → check **"Enable host-side TCP support"** → set port to `12434` → Apply & Restart.

**Option B: CLI:**

```bash
docker desktop enable model-runner --tcp 12434
```

> **Most common gotcha:** Without host-side TCP enabled, port 12434 is inaccessible from your host — only containers can reach it via `model-runner.docker.internal`.

**Windows:** Also check **"Enable GPU backed inference"** if you have NVIDIA + CUDA (requires GPU paravirtualization in WSL2).

Verify:

```bash
docker model status   # Should show: "Docker Model Runner is running"
docker model list     # Empty at first
```

If `docker model` shows "unknown command," upgrade Docker Desktop to 4.40+.

---

## Step 2: Pull a Model

```bash
docker model pull ai/llama3.2
```

Models live under the `ai/` namespace on Docker Hub. Default quantization: Q4_K_M. Tags follow `{model}:{parameters}-{quantization}`:

```bash
docker model pull ai/smollm2:360M-Q4_K_M
docker model pull ai/llama3.2                # latest tag
docker model pull ai/qwen2.5-coder:7B-Q8_0
```

Available models:

| Model | Parameters | Size | Best for |
|-------|-----------|------|----------|
| `ai/smollm2` | 135M–360M | ~256MB | Testing, fast responses |
| `ai/llama3.2` | 1B–3B | ~2GB | General purpose |
| `ai/qwen2.5-coder` | 7B | ~4GB | Code-focused |
| `ai/deepseek-r1` | varies | ~5GB+ | Advanced reasoning |

Like `docker run`, `docker model run` auto-pulls if the model isn't local. Hugging Face GGUF models also work:

```bash
docker model pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF
```

---

## Step 3: Interactive Chat and Model Management

```bash
# Single prompt
docker model run ai/llama3.2 "You are a K8s SRE. What causes OOMKilled?"

# Interactive session (Ctrl+C to exit)
docker model run ai/llama3.2
```

Management commands mirror Docker's container verbs:

```bash
docker model list
docker model pull ai/deepseek-r1
docker model rm ai/smollm2
docker model status
docker model configure --context-size 8192 ai/llama3.2
```

---

## Step 4: Use the OpenAI-Compatible API

Two access paths:

```
From host:       http://localhost:12434/engines/v1
From container:  http://model-runner.docker.internal/engines/v1
```

The model loads on-demand — no `docker model run` needed first.

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

Port `12434` instead of `11434`. Model name uses `ai/` prefix. Everything else is identical to Lab 6.

---

## Step 5: The Three-Way Swap

One codebase, three backends — just swap the client:

```python
from openai import OpenAI
import os

# Ollama (Lab 6)
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# Docker Model Runner (this lab)
client = OpenAI(base_url="http://localhost:12434/engines/v1", api_key="not-needed")

# OpenAI Cloud
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# Same code below — zero changes needed
response = client.chat.completions.create(
    model="...",  # model name changes per backend
    messages=[...]
)
```

---

## Step 6: Docker Compose Integration

Declare models as service dependencies — `docker compose up` handles the rest:

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

Containers use `model-runner.docker.internal` — no port mapping or TCP enable needed for container-to-model communication.

---

## Step 7: Run It

```bash
python3 demos/ollama/task10_docker_model_runner.py
```

---

## Step 8: SRE Log Analyzer with Docker Compose

A FastAPI service with four endpoints:

| Endpoint | What it does |
|----------|-------------|
| `GET /health` | Health check — shows model name and backend URL |
| `GET /samples` | Lists built-in sample K8s failure scenarios |
| `GET /analyze/{sample}` | Analyzes a built-in sample (`oomkilled`, `crashloop`, `imagepull`) |
| `POST /analyze` | Analyzes logs you send |

Create `demos/docker-model-runner/` with these four files:

**`app.py`:**

```python
"""SRE Log Analyzer — Docker Model Runner Demo"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="SRE Log Analyzer", version="1.0.0")

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://model-runner.docker.internal/engines/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "ai/llama3.2")

client = OpenAI(base_url=LLM_BASE_URL, api_key="not-needed")

SYSTEM_PROMPT = """You are a senior SRE assistant. When given Kubernetes logs or alerts:
1. Identify the root cause
2. Assess severity (critical/warning/info)
3. Give 2-3 actionable kubectl commands to investigate or fix
Be concise. No fluff."""

SAMPLE_LOGS = {
    "oomkilled": """Pod payment-service-7f8b9c6d4-x2k9p OOMKilled
Container memory limit: 256Mi
Peak usage before kill: 254Mi
Restart count: 4
Last restart: 2 minutes ago""",

    "crashloop": """Pod api-gateway-5d9f8b7c6-k3m2n CrashLoopBackOff
Exit code: 1
Back-off restarting failed container
Events:
  Warning  BackOff  2m (x5 over 8m)  kubelet  Back-off restarting failed container""",

    "imagepull": """Pod frontend-8b7c6d5f4-j2k1m ImagePullBackOff
Failed to pull image "registry.internal/frontend:v2.3.1"
Error: unauthorized: authentication required
Events:
  Warning  Failed  1m (x3 over 5m)  kubelet  Failed to pull image""",
}


class AnalyzeRequest(BaseModel):
    logs: str


class AnalyzeResponse(BaseModel):
    analysis: str
    model: str
    backend: str


@app.get("/health")
def health():
    return {"status": "healthy", "model": MODEL_NAME, "backend": LLM_BASE_URL}


@app.get("/samples")
def samples():
    return {"available_samples": list(SAMPLE_LOGS.keys())}


@app.get("/analyze/{sample_name}")
def analyze_sample(sample_name: str):
    if sample_name not in SAMPLE_LOGS:
        raise HTTPException(status_code=404, detail=f"Sample not found. Available: {list(SAMPLE_LOGS.keys())}")
    return _analyze(SAMPLE_LOGS[sample_name])


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_logs(req: AnalyzeRequest):
    return _analyze(req.logs)


def _analyze(logs: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze these Kubernetes logs:\n\n{logs}"},
        ],
        temperature=0.1,
    )
    return {
        "analysis": response.choices[0].message.content,
        "model": MODEL_NAME,
        "backend": LLM_BASE_URL,
    }
```

**`Dockerfile`:**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`requirements.txt`:**

```
fastapi==0.115.0
uvicorn==0.30.6
openai==1.50.0
pydantic==2.9.0
```

**`compose.yaml`:**

```yaml
services:
  sre-analyzer:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_BASE_URL=http://model-runner.docker.internal/engines/v1
      - MODEL_NAME=ai/llama3.2
    depends_on:
      llama:
        condition: service_started

  llama:
    provider:
      type: model
      options:
        model: ai/llama3.2
```

### Run and test

```bash
cd demos/docker-model-runner
docker compose up --build
```

Wait for `Uvicorn running on http://0.0.0.0:8000`, then:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/samples
curl http://localhost:8000/analyze/oomkilled
curl http://localhost:8000/analyze/crashloop
curl http://localhost:8000/analyze/imagepull

curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"logs": "Pod redis-master-0 evicted due to node pressure. Node memory: 95% used."}'
```

```bash
docker compose down
```

---

## Step 9: Open WebUI with Docker Model Runner

Same ChatGPT-like interface from Lab 8, backed by Docker Model Runner instead of Ollama. The only differences from Lab 8: `OPENAI_API_BASE_URL` points to Model Runner's gateway, and `OLLAMA_BASE_URL` is cleared.

```yaml
# compose-webui.yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - OPENAI_API_BASE_URL=http://model-runner.docker.internal/engines/v1
      - OPENAI_API_KEY=not-needed
      - OLLAMA_BASE_URL=
    volumes:
      - open-webui-data:/app/backend/data
    depends_on:
      llama:
        condition: service_started
    restart: unless-stopped

  llama:
    provider:
      type: model
      options:
        model: ai/llama3.2

volumes:
  open-webui-data:
```

```bash
docker compose -f compose-webui.yaml up
# Open http://localhost:3000 — create a local account, select ai/llama3.2

docker compose -f compose-webui.yaml down -v
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `docker model` not recognized | Docker Desktop < 4.40 or not enabled | Upgrade to 4.40+ → Settings → Model Runner → Enable |
| Connection refused on 12434 | Host-side TCP not enabled | Settings → Model Runner → enable TCP on 12434 → Apply & Restart |
| Model pull fails | Docker Hub connectivity | Check internet; try `docker pull hello-world` first |
| Slow inference | No GPU acceleration | Settings → Resources → verify GPU allocated |
| "model not found" in API | Wrong model name | Use `ai/llama3.2`, not `llama3.2` — always include `ai/` prefix |
| Port 12434 conflict | Another service on that port | Stop conflicting service or change port in Model Runner settings |
| Works from container, not host | Host-side TCP disabled | Enable TCP (Step 1) |
| WSL2 issues (Windows) | Beta bug | Use PowerShell instead of WSL terminal |
| GPU not detected (Windows) | "Enable GPU backed inference" unchecked | Settings → Model Runner → check all three boxes |

---

## Step 10: Vision Model — Real-Time Camera Analysis

```bash
docker model pull ai/smolvlm:500M-Q8_0
open demos/docker-model-runner/vision-monitor.html   # macOS
# xdg-open ... for Linux; or double-click the file
```

Grant camera access when prompted. The app captures JPEG frames and sends them to the vision endpoint:

```python
response = client.chat.completions.create(
    model="ai/smolvlm:500M-Q8_0",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "You are an SRE monitoring a server room. Describe what you see. Flag any issues."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ]
    }],
    max_tokens=200
)
```

Same OpenAI vision API format as GPT-4 Vision — just running locally.

**Try it:** Click **Analyze Once** for a single frame, or **Start Monitoring** for frames every 3 seconds. Useful prompts: `"Is there a person in this image? Yes or no."` or `"List all visible objects as bullets."` Point at a Grafana dashboard, terminal with errors, or a whiteboard diagram.

**Limitations:** SmolVLM at 500M describes general scene content but misses fine detail (small text, specific error messages). For better accuracy, use `docker model pull ai/llava:7b`.

No teardown needed — just close the browser tab.

---

## Key Takeaway

Docker Model Runner gives you local LLMs without installing anything beyond Docker Desktop. Same OpenAI-compatible API, same code pattern from Lab 6 — your investment in the OpenAI SDK pays off across Ollama, Docker Model Runner, and cloud.

---

**Episode 2 complete.** You now have the full local ring: Ollama + Docker Model Runner, CLI, model parameters, REST API, OpenAI compatibility, Open WebUI, vision, and Compose integration.

Next: [Episode 3: Claude API Deep Dive](../../episode-3-claude-api-deepdive/)
