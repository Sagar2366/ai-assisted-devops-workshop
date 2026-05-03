# Lab 6: OpenAI-Compatible API — One-Line Swap

> **Mission:** Use the OpenAI Python SDK with your local Ollama server — same code runs local or cloud.

---

## The Concept

### The problem: vendor lock-in starts at line 1

In Episode 1, you wrote different code for each provider — `anthropic.Anthropic()` for Claude, `OpenAI()` for GPT, `genai.GenerativeModel()` for Gemini. Different SDKs, different response formats, different import statements. Switch providers and you're rewriting your integration.

The OpenAI API format has become a de facto standard. Not because OpenAI is the best — but because it was first, most tools support it, and it's good enough. Ollama, LiteLLM, vLLM, and dozens of other tools now speak this same protocol.

---

### One codebase, two backends

Ollama exposes an **OpenAI-compatible endpoint** at `http://localhost:11434/v1`. This means the `openai` Python SDK — the same one from Episode 1 — works with local models.

The swap is two lines:

```python
# LOCAL — free, private, air-gapped
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# CLOUD — better reasoning, 200K context
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

# Everything below is IDENTICAL. Same messages, same parameters.
```

**The workflow for SRE teams:** Develop and test locally (free, private, instant). When the local model's quality isn't enough — say, you're building an incident summarizer that needs to handle 50-page postmortems — swap one environment variable and point at a cloud provider. No code changes.

| | Development | Production |
|---|---|---|
| **Endpoint** | `http://localhost:11434/v1` | `https://api.openai.com/v1` |
| **API key** | Any string (Ollama ignores it) | Real key from provider |
| **Model** | `qwen2.5-coder:7b` | `gpt-4o` or `claude-sonnet-4-6` |
| **Cost** | $0.00 | Pay per token |
| **Code changes** | None | None |

This pattern extends beyond OpenAI — any provider with an OpenAI-compatible API (Azure OpenAI, Together AI, Groq) works the same way. You're not locked into any one vendor.

---

## What You'll Build

A Python script that:
1. Creates an OpenAI client pointing at local Ollama
2. Makes a chat completion call (same API as Episode 1)
3. Demonstrates multi-turn conversation
4. Shows the one-line swap pattern

---

## Step 1: Create the Client

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
```

`api_key="ollama"` — Ollama doesn't check API keys, but the SDK requires one. Any string works.

---

## Step 2: Make a Chat Completion

```python
response = client.chat.completions.create(
    model="qwen2.5-coder:7b",
    messages=[
        {"role": "system", "content": "You are a senior SRE. Be concise and actionable."},
        {"role": "user", "content": "Write a Prometheus alert rule for pod restart rate > 5 per minute."}
    ],
    temperature=0.1
)

print(response.choices[0].message.content)
```

Same `client.chat.completions.create()` from Episode 1. Same `response.choices[0].message.content` path.

---

## Step 3: Run It

```bash
python3 demos/ollama/task6_openai_compat.py
```

---

## What Success Looks Like

You get a Prometheus alert rule from your **local** model using the **OpenAI SDK**. The response format is identical to what you'd get from `api.openai.com`.

---

## Key Takeaway

Ollama speaks OpenAI's language. Any tool, library, or framework built for OpenAI now works with your local LLM — zero code changes. Develop locally for free, deploy to cloud when you need to.

---

Next: [Lab 7: Custom Modelfile](lab7-custom-modelfile.md)
