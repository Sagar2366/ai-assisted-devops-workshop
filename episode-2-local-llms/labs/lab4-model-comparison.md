# Lab 4: Model Comparison — Same Alert, Different Brains

> **Mission:** Send the same OOM alert through two different models and compare quality, speed, and style.

---

## The Concept

Different models have different strengths — even at the same parameter count. A **code-focused** model like `qwen2.5-coder` excels at generating kubectl commands. A **general** model like `llama3.1` gives better explanations and reasoning.

The only way to know which works best for your use case is to test them side by side with the same prompt.

```
  Same prompt → qwen2.5-coder:7b → kubectl commands, concise
  Same prompt → llama3.1:8b       → explanations, reasoning
```

---

## What You'll Build

A Python script that:
1. Sends the same OOM alert to two models
2. Times each response
3. Calculates tokens/second
4. Prints a comparison table

---

## Step 1: The Alert Prompt

```python
SRE_ALERT = """ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)

Analyze this alert. Give me:
1. Root cause (one sentence)
2. Immediate fix (kubectl command)
3. Long-term prevention"""
```

---

## Step 2: Time Each Model

```python
import time

start = time.time()
response = requests.post(OLLAMA_URL, json={...})
elapsed = time.time() - start

data = response.json()
eval_count = data.get("eval_count", 0)
eval_duration = data.get("eval_duration", 0)
tokens_per_sec = eval_count / (eval_duration / 1e9)
```

Ollama returns `eval_count` (tokens generated) and `eval_duration` (nanoseconds). Divide to get tokens/second.

---

## Step 3: Run It

```bash
python3 demos/ollama/task4_model_comparison.py
```

---

## What Success Looks Like

A comparison table showing each model's response time, token count, and generation speed. You'll notice:
- **qwen2.5-coder** gives more precise kubectl commands
- **llama3.1** gives better reasoning and explanation
- Speed varies based on model architecture

---

## Key Takeaway

Same prompt, different models, different results. Choose based on your task: code generation → code-focused model, incident reasoning → general model. Always benchmark with your actual prompts, not synthetic benchmarks.

---

Next: [Lab 5: Ollama API Deep Dive](lab5-ollama-api.md)
