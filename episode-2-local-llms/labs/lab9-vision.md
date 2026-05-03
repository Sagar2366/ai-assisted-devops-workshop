# Lab 9: Vision Models — AI That Can See Your Screenshots

> **Mission:** Run a vision-capable model on Ollama and analyze an image locally — a preview of what Claude's vision does at scale in Episode 3.

---

## The Concept

### What are vision models?

Most models you've used so far are text-only — they read text, generate text. Vision models (also called multi-modal models) accept images alongside text. You pass an image + a text prompt, and the model analyzes both together.

This isn't OCR — the model actually understands visual content. It can read graphs, interpret trends, describe diagrams, and answer questions about what it sees.

---

### SRE use cases for vision

| Use case | What you'd pass | What you'd get back |
|---|---|---|
| **Grafana dashboard triage** | Screenshot of a dashboard during an incident | "CPU spiked at 14:32, memory is flat — compute-bound, not a leak" |
| **Architecture diagram review** | PNG of your infra diagram | "Single point of failure: one NAT gateway for all AZs" |
| **Error screenshot from Slack** | Screenshot someone pasted during an incident | Extracted error message + analysis |
| **Cloud console analysis** | AWS Console screenshot | "3 of 5 targets unhealthy in us-east-1a" |

---

### Local vs Cloud vision

Ollama's vision models (LLaVA, based on LLaMA + CLIP) are small — 7B parameters. They can describe images and answer basic questions, but they miss details and nuance on complex dashboards.

Claude's vision (Episode 3) uses the full Sonnet/Opus model — much more accurate for SRE triage. Think of this lab as a proof of concept. Episode 3 takes it to production quality.

```
  Ollama vision (local):   "The graph shows a spike"
  Claude vision (cloud):   "CPU spiked from 15% to 94% at 14:32, correlating with
                            the drop in request throughput at 14:33"
```

---

## What You'll Build

A Python script that sends an image to a local vision model and gets a description back — all running on your laptop.

---

## Step 1: Pull a Vision Model

```bash
ollama pull llava:7b
```

LLaVA (Large Language and Vision Assistant) is ~4.7 GB. It combines LLaMA for text with CLIP for image understanding.

---

## Step 2: Try It Interactively First

```bash
ollama run llava:7b

>>> What do you see in this image? /path/to/your/screenshot.png
```

The interactive CLI can accept image file paths directly.

---

## Step 3: Use the API

For automation, send images via the REST API as base64-encoded data:

```python
import requests
import base64

with open("screenshot.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llava:7b",
        "prompt": "You are an SRE. Describe what you see in this monitoring dashboard. What looks abnormal?",
        "images": [image_data],
        "stream": False
    }
)

print(response.json()["response"])
```

The `images` field takes a list of base64-encoded strings. You can pass multiple images in one call.

---

## Step 4: Run It

```bash
python3 demos/ollama/task9_vision.py
```

---

## What Success Looks Like

The model describes the image contents — identifying charts, text, colors, and trends. For a Grafana screenshot, it might say something like "I see a time series graph with a sharp spike in the metric around the middle of the time range." It won't be as precise as Claude's vision, but it demonstrates the concept.

---

## Limitations of Local Vision

- **Detail accuracy** — small models miss specific numbers, axis labels, small text
- **Complex layouts** — multi-panel Grafana dashboards can confuse 7B models
- **Speed** — vision inference is slower than text-only (more computation per image)
- **RAM** — LLaVA needs ~5-6 GB RAM on top of your text model

For quick "what am I looking at?" queries, local vision works. For accurate incident triage from dashboards, you'll want Claude's vision in Episode 3.

---

## Key Takeaway

Vision models let AI see your screenshots — dashboards, diagrams, error pages. Local vision (LLaVA on Ollama) is a proof of concept. Cloud vision (Claude in Episode 3) is production-quality. Both use the same concept: image + text prompt → analysis.

---

---

Next: [Lab 10: Docker Model Runner](lab10-docker-model-runner.md)
