# Lab 0: Platform Setup

> **Mission:** Get the Agentic DevOps Platform running locally with all dependencies configured.

In production SRE work, a platform that cannot bootstrap itself reliably will fail at 3 AM when you need it most. This lab sets up every component of the Agentic DevOps Platform.

---

## Prerequisites Check

Before installing anything, verify your system meets the minimum requirements.

> **Analogy:** Think of prerequisites like a pilot's pre-flight checklist. Missing one item does not mean the plane cannot physically move — it means you cannot guarantee a safe flight. A missing dependency may let the platform start but fail unpredictably under load.

### Python 3.10+

```bash
python3 --version
# Expected: Python 3.10.x or higher

# macOS: brew install python@3.12
# Ubuntu: sudo apt install python3.12 python3.12-venv
```

Python 3.10+ is required for structural pattern matching (`match/case`) used in agent routing.

### Docker

```bash
docker --version
# Expected: Docker version 24.x or higher

docker info > /dev/null 2>&1 && echo "Docker is running" || echo "Docker is NOT running"
```

### Ollama (Local LLM Runtime)

```bash
ollama --version
# Expected: ollama version 0.3.x or higher

# Install if missing:
curl -fsSL https://ollama.com/install.sh | sh

# Pull the required model
ollama pull llama3.1:8b
```

---

## Install Python Dependencies

Create an isolated virtual environment to prevent dependency conflicts with other tools on your workstation.

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install all platform dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

The `requirements.txt` includes:

```text
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0
pydantic>=2.5.0
langchain>=0.1.0
langchain-anthropic>=0.1.0
langgraph>=0.0.40
ollama>=0.1.6
boto3>=1.34.0
python-dotenv>=1.0.0
structlog>=23.2.0
prometheus-client>=0.19.0
```

> **Analogy:** A `requirements.txt` is like a runbook's "tools needed" section. Just as an SRE runbook lists exactly which CLI tools and access levels are required before starting an incident response procedure, this file declares every library the platform needs to function.

---

## Configure LLM Backends

The Agentic DevOps Platform supports three LLM backends. You need at least one configured, but production deployments use all three with fallback routing.

### Ollama (Local Development)

```bash
curl -s http://localhost:11434/api/tags | python3 -m json.tool
# Expected: JSON listing available models including llama3.1:8b
```

### Anthropic Claude (Cloud - High Capability)

```bash
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":50,"messages":[{"role":"user","content":"ping"}]}'
```

### AWS Bedrock (Enterprise - VPC Isolated)

```bash
aws bedrock list-foundation-models \
  --query "modelSummaries[?contains(modelId,'anthropic')].[modelId]" \
  --output table
```

> **Analogy:** These three backends are like on-call tiers. Ollama is your local team (fast, always available, limited scope). Anthropic API is your escalation path (higher capability, external dependency). Bedrock is your enterprise backbone (governed, auditable, VPC-contained).

---

## Environment Variables Setup

Create a `.env` file in the project root:

```bash
cat > .env << 'EOF'
# === LLM Configuration ===
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-20250514-v1:0

# === Platform Configuration ===
PLATFORM_HOST=0.0.0.0
PLATFORM_PORT=8000
LOG_LEVEL=info
ENVIRONMENT=development

# === Agent Configuration ===
AGENT_TIMEOUT_SECONDS=30
MAX_CONCURRENT_AGENTS=5
HEALTH_CHECK_INTERVAL=10

# === Observability ===
METRICS_ENABLED=true
METRICS_PORT=9090
EOF
```

Verify the configuration:

```bash
python3 -c "
from dotenv import dotenv_values
config = dotenv_values('.env')
for key in ['OLLAMA_BASE_URL', 'PLATFORM_PORT', 'AGENT_TIMEOUT_SECONDS']:
    status = 'OK' if config.get(key) else 'MISSING'
    print(f'  {key}: {status}')
"
```

---

## Start the Platform

Launch the platform using uvicorn:

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --log-level info

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Loading agent: incident-commander
# INFO:     Loading agent: capacity-planner
# INFO:     Loading agent: chaos-engineer
# INFO:     Loading agent: deploy-guardian
# INFO:     All agents initialized successfully
```

The `--reload` flag enables hot-reloading during development. In production, omit this and use `--workers 4` instead.

---

## Verify Health Endpoint

Once the platform is running, verify all components are healthy:

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

Expected response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agents": {
    "incident-commander": {"status": "ready", "backend": "anthropic"},
    "capacity-planner": {"status": "ready", "backend": "ollama"},
    "chaos-engineer": {"status": "ready", "backend": "ollama"},
    "deploy-guardian": {"status": "ready", "backend": "anthropic"}
  },
  "backends": {
    "ollama": {"status": "connected", "models_loaded": 1},
    "anthropic": {"status": "connected", "model": "claude-sonnet-4-20250514"},
    "bedrock": {"status": "not_configured"}
  },
  "uptime_seconds": 3.7
}
```

If any agent shows `"status": "error"`, check the logs:

```bash
curl -s http://localhost:8000/health | python3 -c "
import json, sys
health = json.load(sys.stdin)
for name, info in health.get('agents', {}).items():
    if info['status'] != 'ready':
        print(f'DEGRADED: {name} -> {info}')
"
```

---

## What Success Looks Like

When this lab is complete:

1. The health endpoint returns HTTP 200 with `"status": "healthy"`
2. All four agents report `"status": "ready"` with their assigned backends
3. At least one LLM backend (Ollama minimum) shows `"status": "connected"`
4. The platform responds within 100ms for the health check

In production, you would encode these checks into a Kubernetes readiness probe so the platform only receives traffic once all agents are initialized.

---

## Key Takeaway

A multi-agent platform needs multiple services configured — LLM backends, agent definitions, observability pipelines — but starts with a single command. The complexity is in the configuration, not the operation. Invest in setup automation so that day-to-day operation is a single `uvicorn` command away from a fully functional system. The pattern you followed — prerequisites, dependencies, configuration, launch, verify — is the universal deployment pattern for any distributed system.

---

Next: [Lab 1: Architecture](lab1-architecture.md)
