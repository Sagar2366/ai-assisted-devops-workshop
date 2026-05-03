# Lab 7: Custom Modelfile — Package SRE Expertise into a Model

> **Mission:** Create a custom Ollama model with a baked-in SRE persona, low temperature, and specific context length — then compare it against the raw model.

---

## The Concept

A **Modelfile** is like a **Dockerfile for AI**. It starts with a base model, layers on configuration, and produces a reusable custom model.

```
  Dockerfile                          Modelfile
  ──────────                          ─────────
  FROM ubuntu:22.04                   FROM qwen2.5-coder:7b
  ENV NODE_ENV=production             PARAMETER temperature 0.1
  COPY app.js /app/                   SYSTEM "You are an SRE..."
  docker build -t myapp .             ollama create sre-assistant -f Modelfile
```

The custom model bakes in:
- **System prompt** — always active, no need to send it every call
- **Temperature** — locked to 0.1 for consistent SRE advice
- **Context length** — set to 4096 tokens

Anyone on your team can `ollama run sre-assistant` and get the same SRE persona without knowing the prompt engineering.

---

## What You'll Build

A Python script that:
1. Creates a Modelfile with SRE expertise
2. Builds it with `ollama create`
3. Compares the raw model vs custom model on the same alert
4. Verifies the model appears in `ollama list`

---

## Step 1: The Modelfile

```
FROM qwen2.5-coder:7b

PARAMETER temperature 0.1
PARAMETER num_ctx 4096

SYSTEM """You are an expert SRE assistant with deep knowledge of:
- Kubernetes (EKS, GKE, AKS, kind, minikube)
- Monitoring (Prometheus, Grafana, Loki, Datadog)
- CI/CD (GitHub Actions, ArgoCD, Jenkins)
- Infrastructure (Terraform, Helm, Kustomize)

Rules:
1. Always give kubectl/helm commands, not general advice
2. Start with the most likely root cause
3. Include rollback commands when suggesting changes
4. Flag any destructive operations with a WARNING
5. Be concise — SREs are in incident mode, not reading essays
"""
```

---

## Step 2: Build the Model

```bash
ollama create sre-assistant -f Modelfile.sre-assistant
```

This creates a new local model called `sre-assistant` based on `qwen2.5-coder:7b` with the SRE persona baked in.

---

## Step 3: Compare Raw vs Custom

Send the same OOM alert to both:

```python
raw_response = ask_ollama(alert, "qwen2.5-coder:7b")
custom_response = ask_ollama(alert, "sre-assistant")
```

The custom model should give more focused, kubectl-heavy responses because the system prompt is always active.

---

## Step 4: Run It

```bash
python3 demos/ollama/task7_custom_modelfile.py
```

---

## What Success Looks Like

- `ollama list` shows `sre-assistant` alongside your other models
- The custom model's responses are more focused and actionable than the raw model
- Anyone can now run `ollama run sre-assistant` for SRE help

---

## Key Takeaway

A Modelfile packages expertise into a reusable, shareable model. Bake in your team's system prompt, temperature, and context length. Share with `ollama create` + `ollama push`. Like a Dockerfile for AI — reproducible, versioned, portable.

---

Next: [Lab 8: Open Web UI](lab8-open-webui.md)
