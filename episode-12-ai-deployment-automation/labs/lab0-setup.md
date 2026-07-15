# Lab 0: Environment Setup

> **Mission:** Prepare your environment with the tools and API access needed for AI-powered deployment automation.

## Prerequisites

Before starting this episode, ensure you have:

- Python 3.9 or higher installed
- An Anthropic API key (get one at https://console.anthropic.com)
- Docker installed (for testing generated Dockerfiles)
- kubectl installed (for validating generated manifests)

## Step 1: Install Required Packages

```bash
pip install anthropic pyyaml
```

**What these packages do:**
- `anthropic` — Official Python SDK for the Claude API
- `pyyaml` — YAML parsing and generation for Kubernetes manifests

## Step 2: Configure Your API Key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

To persist across sessions, add this to your shell profile:

```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## Step 3: Verify the Setup

```python
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say 'Deployment automation ready!' in one line."}]
)
print(message.content[0].text)
```

Run it:

```bash
python -c "
import anthropic
client = anthropic.Anthropic()
msg = client.messages.create(model='claude-sonnet-4-20250514', max_tokens=100, messages=[{'role':'user','content':'Say deployment automation ready'}])
print(msg.content[0].text)
"
```

## Step 4: Clone the Sample Apps

The `demos/sample-apps/` directory contains pre-built sample applications for testing:

```bash
ls demos/sample-apps/
# python-app/  node-app/
```

Each app is a minimal but realistic service that the AI will analyze.

## Step 5: Verify Docker (Optional)

If you want to build and test the generated Dockerfiles:

```bash
docker --version
docker run --rm hello-world
```

## What Success Looks Like

- [x] Python 3.9+ is installed
- [x] `anthropic` and `pyyaml` packages are installed
- [x] `ANTHROPIC_API_KEY` is set and working
- [x] Sample apps are accessible in the `demos/sample-apps/` directory
- [x] Docker is available (optional, for testing builds)

## Key Takeaway

> A well-configured environment is the foundation for AI-assisted automation. With the Anthropic SDK and sample applications ready, you can focus on building intelligent deployment pipelines rather than fighting tooling issues.

**Next:** Lab 1 — AI Application Analyzer
