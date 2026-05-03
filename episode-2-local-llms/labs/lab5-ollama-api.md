# Lab 5: Ollama API Deep Dive — Automate Local LLMs

> **Mission:** Master both Ollama APIs — `/api/generate` and `/api/chat` — plus streaming, system prompts, and JSON mode.

---

## The Concept

### Why API over CLI?

So far you've been running Ollama interactively — type a prompt, read the response. That's great for exploration, but useless for automation. You can't put `ollama run` in a CI/CD pipeline, a monitoring webhook, or a Python-based incident responder.

The REST API changes that. Your code sends an HTTP request, gets a JSON response — same pattern you already use for Prometheus (`/api/v1/query`), Grafana (`/api/dashboards`), or any internal microservice. Ollama is just another local service your automation can talk to.

```
  Interactive:    You  →  terminal  →  ollama run  →  read output with your eyes
  Automated:      Script  →  HTTP POST  →  localhost:11434  →  JSON response  →  next step in pipeline
```

---

### How an AI-powered app works — the request/response cycle

Every AI application — whether it's ChatGPT, a Slack bot, or your custom SRE triage tool — follows the same basic flow:

```
  1. User input (or automated trigger — alert, webhook, cron job)
       ↓
  2. Your app builds a prompt (add context, system instructions, format rules)
       ↓
  3. HTTP POST to the LLM endpoint (Ollama, OpenAI, Claude — same pattern)
       ↓
  4. LLM generates tokens one at a time, returns response
       ↓
  5. Your app processes the output (parse JSON, extract commands, format for Slack)
       ↓
  6. Result delivered (terminal, web UI, PagerDuty comment, Jira ticket)
```

This is the pattern behind every AI integration you'll build in this series. The LLM is a stateless function: input in, output out. Your app carries the state.

---

### Two APIs, two use cases

Ollama exposes two HTTP endpoints:

| API | Use Case | Input | When to use |
|-----|----------|-------|-------------|
| `/api/generate` | Single prompt → single response | `prompt` (string) | One-shot tasks: analyze this log, generate this YAML |
| `/api/chat` | Multi-turn conversation | `messages` (array) | Follow-up questions, incident investigation with context |

> **Analogy:** `/api/generate` is like sending a single email. `/api/chat` is like a Slack thread — you see the full conversation history and the model responds in context.

`/api/chat` uses the same `messages` format as OpenAI: `system`, `user`, `assistant` roles. This is the same pattern from Episode 1 — it works everywhere.

---

### Streaming — watch the model think

By default, you wait for the full response. With streaming, tokens arrive one at a time — like `kubectl logs -f` or watching ChatGPT type. Useful for UIs where you want to show progress, or for long responses where you want to start processing early.

---

### JSON mode — structured output for pipelines

When you're feeding LLM output into another tool (a script, a dashboard, PagerDuty), you need valid JSON, not prose. `"format": "json"` tells Ollama to constrain the output to valid JSON. Combine with `temperature: 0.0` for maximum consistency. This is how you turn an LLM into an automation-friendly API instead of a chatbot.

---

## What You'll Build

Four experiments:
1. `/api/generate` — basic prompt/response
2. `/api/chat` — multi-turn with system prompt
3. Streaming — real-time token output
4. JSON mode — structured output for automation

---

## Experiment 1: /api/generate

```python
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5-coder:7b",
        "prompt": "Write a Prometheus alert rule for pod restart rate > 5/min. YAML only.",
        "stream": False,
        "options": {"temperature": 0.1, "num_ctx": 4096}
    }
)
print(response.json()["response"])
```

---

## Experiment 2: /api/chat with System Prompt

```python
response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen2.5-coder:7b",
        "messages": [
            {"role": "system", "content": "You are a senior SRE. Give kubectl commands, not general advice."},
            {"role": "user", "content": "A pod in production is CrashLoopBackOff. What do I check first?"}
        ],
        "stream": False
    }
)
print(response.json()["message"]["content"])
```

Note the response path: `/api/generate` → `result["response"]`, `/api/chat` → `result["message"]["content"]`.

---

## Experiment 3: Streaming

```python
response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "qwen2.5-coder:7b", "prompt": "...", "stream": True},
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line)
        print(data.get("response", ""), end="", flush=True)
        if data.get("done"):
            break
```

Two `stream` flags: one in the JSON body (tells Ollama), one in `requests.post()` (tells Python to read incrementally).

---

## Experiment 4: JSON Mode

```python
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5-coder:7b",
        "prompt": "Analyze these pods and return JSON with 'healthy' and 'unhealthy' lists...",
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.0}
    }
)
parsed = json.loads(response.json()["response"])
```

`"format": "json"` constrains the model to output valid JSON. Use `temperature: 0.0` for maximum consistency.

---

## Step 5: Run It

```bash
python3 demos/ollama/task5_ollama_api.py
```

---

## Key Takeaway

Ollama has two APIs: `generate` for simple prompts, `chat` for conversations. Both support streaming, temperature, and JSON mode. This is how you automate local LLMs in scripts and CI/CD pipelines.

---

## You should also know: the native Ollama Python library

There's a third way to talk to Ollama — `pip install ollama` gives you a dedicated Python library:

```python
import ollama
response = ollama.generate(model="qwen2.5-coder:7b", prompt="Why is this pod OOMKilled?")
print(response["response"])
```

It wraps the same REST API under the hood. We use raw `requests` in this episode so you understand exactly what's happening at the HTTP level. In Lab 6 we use the `openai` SDK for portability. The native `ollama` library is a third option — simpler syntax, but locks you into Ollama as the backend. Pick the right tool for your use case.

---

Next: [Lab 6: OpenAI-Compatible API](lab6-openai-compat.md)
