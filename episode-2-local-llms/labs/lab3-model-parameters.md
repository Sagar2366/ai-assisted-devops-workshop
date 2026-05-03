# Lab 3: Model Parameters — Choose the Right Model for the Job

> **Mission:** Understand model size, quantization, and context length — then pick the right model for each SRE task.

---

## The Concept

### Parameters — the model's stored knowledge

Parameters are numerical weights learned during training. Think of them as "knowledge units" — more parameters means the model absorbed more patterns from its training data. A 7B model has 7 billion of these weights. GPT-4 is rumored to be over 1 trillion.

> **Analogy:** Parameters are like books on a shelf. A library with 7 billion books has more knowledge than one with 3 billion — but it also takes up more physical space (RAM) and is slower to search (inference speed).

The catch: more parameters doesn't always mean better for your specific task. A 7B model fine-tuned for code often beats a generic 70B model at generating kubectl commands.

---

### Quantization — JPEG compression for AI

Full-precision models store each weight as a 16-bit floating point number (F16). Quantization compresses these to 4-bit or 8-bit integers — same idea as JPEG compression. You lose a tiny amount of quality but the file is 4x smaller and inference is faster.

```
  F16 (full precision):    14 GB on disk,  needs 16 GB RAM,  100% quality
  Q8  (8-bit quantized):    7 GB on disk,  needs  8 GB RAM,   95% quality
  Q4  (4-bit quantized):  3.5 GB on disk,  needs  5 GB RAM,   90% quality
```

For SRE tasks — log analysis, alert triage, kubectl generation — the quality difference between Q4 and F16 is almost unnoticeable. You'd need to be doing creative writing or complex mathematical reasoning to feel the loss.

> **Analogy:** Like streaming video at 720p vs 4K. For watching a conference talk, 720p is perfectly fine and uses a quarter of the bandwidth. You only need 4K when pixel-level detail matters.

---

### Context length — the model's working memory

Context length is how many tokens the model can hold in a single request — your prompt AND its response combined. If your K8s log dump is 10,000 tokens and the context window is 4,096, the model literally cannot see all of it. Tokens past the limit are silently dropped.

- 4,096 tokens ≈ 3,000 words ≈ ~80 lines of logs
- 8,192 tokens ≈ 6,000 words ≈ ~160 lines of logs  
- 128K tokens ≈ a small book (cloud models like Claude)

> **Analogy:** Context length is like a whiteboard. You can only fit so much on it at once. When it's full, you have to erase the oldest stuff to write new things. Cloud models have a massive whiteboard (200K tokens). Local models have a smaller one — big enough for most SRE tasks, but you can't paste an entire 5,000-line log file.

**Practical rule:** For local models, keep prompts focused. Don't paste an entire log file — extract the relevant 20-50 lines first.

---

### Model families — who made what

| Family | Company | Strengths | Notable Sizes |
|--------|---------|-----------|---------------|
| Qwen | Alibaba | Code generation, following instructions | 0.5B, 7B, 14B, 72B |
| LLaMA | Meta | General reasoning, well-rounded | 3B, 8B, 70B, 405B |
| Mistral | Mistral AI | Fast inference, European AI | 7B, 22B |
| DeepSeek | DeepSeek | Code, math, reasoning | 7B, 67B |
| Phi | Microsoft | Surprisingly good for tiny size | 3B, 14B |

For this workshop we use `qwen2.5-coder:7b` — strong at code tasks, 4 GB on disk, runs fine on 8 GB RAM.

---

### SRE model sizing — what to use when

```
  1-3B    → Log classification, simple formatting, quick lookups
  7-8B    → K8s triage, kubectl generation, alerting     ← YOUR LAPTOP SWEET SPOT
  14B     → Incident reasoning, multi-step diagnosis
  32-70B  → Runbook generation, complex root cause analysis (needs 32-64 GB RAM)
```

**The 80/20 rule:** A 7B Q4 model handles 80% of daily SRE tasks. Only reach for bigger when you're consistently getting low-quality answers on complex multi-step reasoning.

---

## What You'll Build

A Python script that queries Ollama's `/api/show` and `/api/tags` endpoints to display model metadata, then shows an SRE decision guide.

---

## Step 1: List Models via API

```python
response = requests.get("http://localhost:11434/api/tags")
models = response.json().get("models", [])
```

---

## Step 2: Get Model Details

```python
response = requests.post(
    "http://localhost:11434/api/show",
    json={"name": "qwen2.5-coder:7b"}
)
info = response.json()
details = info.get("details", {})

print(f"Family:         {details.get('family')}")
print(f"Parameter Size: {details.get('parameter_size')}")
print(f"Quantization:   {details.get('quantization_level')}")
```

---

## Step 3: Run It

```bash
python3 demos/ollama/task3_model_parameters.py
```

---

## What Success Looks Like

You see your model's family (e.g., qwen2), parameter count (7.6B), quantization level (Q4_K_M), and context length. The SRE guide helps you decide which model to use for which task.

---

## Quantization Quick Reference

| Level | Bits | Size vs F16 | Quality | When to Use |
|-------|------|-------------|---------|-------------|
| Q4_K_M | 4-bit | ~25% | ~90% | Default choice — best balance |
| Q8_0 | 8-bit | ~50% | ~95% | When Q4 quality isn't enough |
| F16 | 16-bit | 100% | 100% | Only with serious GPU |

---

## Key Takeaway

7B Q4 handles 80% of SRE tasks — log triage, kubectl generation, alert analysis. Only move up to 14B+ when quality genuinely drops. Bigger ≠ always better when you're optimizing for speed and RAM.

---

Next: [Lab 4: Model Comparison](lab4-model-comparison.md)
