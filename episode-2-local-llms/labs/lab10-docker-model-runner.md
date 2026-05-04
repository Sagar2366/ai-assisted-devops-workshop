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

1. **Docker Model Runner basics** — enable, pull, chat, API calls (Steps 1-7)
2. **SRE Log Analyzer** — a containerized FastAPI service that analyzes K8s logs using Docker Model Runner as its AI backend, run entirely with `docker compose up` (Step 8)
3. **Open WebUI + Docker Model Runner** — same ChatGPT-like interface from Lab 8, now backed by Docker Model Runner instead of Ollama (Step 9)
4. **Vision Monitor** — real-time webcam analysis using a local vision model, single HTML file talks to Docker Model Runner (Step 10)

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

## Step 8: Build an SRE Log Analyzer with Docker Compose

This is the payoff — build a real containerized service that uses Docker Model Runner as its AI backend. One `docker compose up`, your SRE assistant is live.

### What you're building

A FastAPI service with three endpoints:

| Endpoint | What it does |
|----------|-------------|
| `GET /health` | Health check — shows model name and backend URL |
| `GET /samples` | Lists built-in sample K8s failure scenarios |
| `GET /analyze/{sample}` | Analyzes a built-in sample (oomkilled, crashloop, imagepull) |
| `POST /analyze` | Analyzes any logs you send |

The service runs in a container and talks to Docker Model Runner via `model-runner.docker.internal` — no TCP port exposure needed. The model is declared as a Compose provider, so `docker compose up` handles everything.

### Create the app

Create a folder `demos/docker-model-runner/` with four files:

**`app.py`** — the FastAPI service:

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

**`Dockerfile`**:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`requirements.txt`**:

```
fastapi==0.115.0
uvicorn==0.30.6
openai==1.50.0
pydantic==2.9.0
```

**`compose.yaml`** — this is where the magic happens:

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

Notice what's happening:
- The `llama` service uses `provider: { type: model }` — this is Docker Compose's native Model Runner integration
- `depends_on` ensures the model is ready before the app starts
- The app talks to `model-runner.docker.internal` — the internal DNS name, no port mapping needed
- `docker compose up` pulls the model AND builds/starts the app

### Run it

```bash
cd demos/docker-model-runner

# Start everything
docker compose up --build
```

Docker pulls the model (if not cached), builds the app container, and starts the service. Wait for `Uvicorn running on http://0.0.0.0:8000`.

### Test it

Open a new terminal:

```bash
# Health check
curl http://localhost:8000/health
# {"status":"healthy","model":"ai/llama3.2","backend":"http://model-runner.docker.internal/engines/v1"}

# List available samples
curl http://localhost:8000/samples
# {"available_samples":["oomkilled","crashloop","imagepull"]}

# Analyze the OOMKilled scenario
curl http://localhost:8000/analyze/oomkilled

# Analyze the CrashLoopBackOff scenario
curl http://localhost:8000/analyze/crashloop

# Analyze the ImagePullBackOff scenario
curl http://localhost:8000/analyze/imagepull

# Send your own logs
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"logs": "Pod redis-master-0 evicted due to node pressure. Node memory: 95% used."}'
```

Each response includes the AI analysis, the model name, and which backend was used.

### What to watch for on camera

1. `docker compose up` pulls the model and starts the app in one command
2. The app talks to `model-runner.docker.internal` — no port 12434 needed from inside containers
3. The `provider: type: model` block — models as first-class Compose services
4. Compare the response quality across the three sample scenarios

### Tear down

```bash
docker compose down
```

---

## Step 9: Open WebUI with Docker Model Runner

In Lab 8, you ran Open WebUI with Ollama. Same tool, same ChatGPT-like interface — now backed by Docker Model Runner instead.

### The compose file

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

Key differences from Lab 8's Ollama setup:
- `OPENAI_API_BASE_URL` points to Model Runner's gateway instead of Ollama
- `OLLAMA_BASE_URL` is empty — tells Open WebUI not to look for Ollama
- The `llama` service uses the native `provider` block — model is managed by Compose

### Run it

```bash
cd demos/docker-model-runner

# Start Open WebUI + Docker Model Runner
docker compose -f compose-webui.yaml up
```

Open [http://localhost:3000](http://localhost:3000) in your browser. Create an account (local only, no data leaves your machine), select `ai/llama3.2` as the model, and start chatting.

### What to show on camera

1. Open WebUI is identical to the Lab 8 experience — same UI, different backend
2. Swap between Ollama (Lab 8) and Docker Model Runner (this step) by changing one env var
3. The `provider` block makes `docker compose up` handle the model automatically

### Tear down

```bash
docker compose -f compose-webui.yaml down -v
```

---

## What Success Looks Like

Docker Model Runner responds to your SRE query through the OpenAI SDK — same quality as Ollama, running entirely within Docker Desktop. The SRE Log Analyzer shows a complete Compose-based app using Model Runner as the AI backend. Open WebUI proves the same ChatGPT-like interface works with both Ollama and Docker Model Runner — one env var swap.

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

## Step 10: Vision Model — Real-Time Camera Analysis

Docker Model Runner supports multimodal (vision) models. In this step you'll run a local vision model that analyzes your webcam feed in real-time — think "AI security camera for your server room" but running entirely on your laptop.

### Pull the vision model

```bash
docker model pull ai/smolvlm:500M-Q8_0
```

SmolVLM is a 500M parameter vision-language model. Small enough to run fast on any machine, capable enough to describe images and flag anomalies.

### The demo app

Open `demos/docker-model-runner/vision-monitor.html` in your browser:

```bash
# macOS
open demos/docker-model-runner/vision-monitor.html

# Linux
xdg-open demos/docker-model-runner/vision-monitor.html

# Or just double-click the file
```

Grant camera access when prompted.

### How it works

The app captures a JPEG frame from your webcam and sends it to Docker Model Runner's vision endpoint:

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

Same OpenAI vision API format — `image_url` with base64 data. Works identically to OpenAI's GPT-4 Vision, just running locally.

### What to do

1. Click **"Analyze Once"** — sends a single frame, gets a description
2. Click **"Start Monitoring"** — sends frames every 3 seconds (configurable)
3. Try different prompts:
   - `"Describe what you see in one sentence"`
   - `"Is there a person in this image? Yes or no."`
   - `"List all objects visible. Format as a bullet list."`
4. Try pointing your camera at:
   - Your screen showing a Grafana dashboard
   - A terminal with error logs
   - Server rack or networking equipment
   - A whiteboard with architecture diagrams

### Configuration options

| Setting | Default | What it controls |
|---------|---------|-----------------|
| Model | `ai/smolvlm:500M-Q8_0` | Vision model to use |
| Endpoint | `http://localhost:12434/engines/v1` | Docker Model Runner gateway |
| Interval | 3000ms | Time between analysis frames |
| Prompt | SRE server room monitoring | What the model looks for |

### Why this matters for SRE

Real-world applications of local vision + SRE:
- **Dashboard screenshot analysis** — feed Grafana screenshots to the model, get natural-language summaries
- **Physical infrastructure monitoring** — server room cameras analyzed locally (no data leaves the building)
- **Alert triage** — paste screenshots of alert dashboards, get AI-powered context
- **Documentation** — point camera at whiteboard diagrams, get them converted to text

### Limitations of 500M vision models

SmolVLM at 500M is fast but imprecise. It will:
- Describe general scene content
- Identify obvious objects (people, screens, text)
- Miss fine details (small text on screens, specific error messages)

For production quality, use `ai/llava:7b` (pull it with `docker model pull ai/llava:7b`) — slower but significantly more accurate.

### Tear down

Just close the browser tab. No containers to stop — the HTML talks directly to Docker Model Runner's API.

---

## Key Takeaway

Docker Model Runner gives you local LLMs without installing anything beyond Docker Desktop. Same OpenAI-compatible API, same code pattern from Lab 6 — your investment in learning the OpenAI SDK pays off across Ollama, Docker, and cloud.

---

**Episode 2 complete.** You now have the full local ring — Ollama setup, CLI, model parameters, model comparison, REST API, OpenAI compatibility, custom Modelfile, Open WebUI, vision, and Docker Model Runner.

Next episode: [Episode 3: Claude API Deep Dive](../../episode-3-claude-api-deepdive/)
