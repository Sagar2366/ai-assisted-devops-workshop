# Lab 1: Model Tiers — Choosing the Right Tool for the Job

## Mission

Understand which Claude model to use for different SRE tasks by sending the same incident data to all three tiers and observing the difference in depth, speed, and cost.

---

## Concept: Model Tiers as Team Roles

Think of the Claude model family like your on-call escalation chain:

| Model | Team Analogy | Characteristics |
|-------|-------------|-----------------|
| **Haiku 3.5** | Junior on-call engineer | Fast triage, handles routine alerts, knows when to escalate |
| **Sonnet 4** | Senior SRE | Balanced depth and speed, handles most incidents end-to-end |
| **Opus 4** | Principal architect | Deep reasoning, architecture reviews, complex failure analysis |

You would not page your Principal Architect at 3 AM for a simple pod restart. Similarly, you should not burn Opus tokens on alert classification. Match the model to the task.

---

## The Scenario: A Pod OOMKilled in Production

Here is a realistic Kubernetes log snippet from a production incident:

```python
K8S_LOG = """
TIMESTAMP                 NAMESPACE    POD                              EVENT
2024-03-15T03:42:01Z     payments     payment-processor-7d4b8f9-x2k4n  Normal   Scheduled  Successfully assigned payments/payment-processor-7d4b8f9-x2k4n to node-pool-2-abc123
2024-03-15T03:42:03Z     payments     payment-processor-7d4b8f9-x2k4n  Normal   Pulled     Container image "payments-svc:v2.3.1" already present on machine
2024-03-15T03:42:03Z     payments     payment-processor-7d4b8f9-x2k4n  Normal   Created    Created container payment-processor
2024-03-15T03:42:04Z     payments     payment-processor-7d4b8f9-x2k4n  Normal   Started    Started container payment-processor
2024-03-15T03:47:22Z     payments     payment-processor-7d4b8f9-x2k4n  Warning  Unhealthy  Readiness probe failed: HTTP probe failed with statuscode: 503
2024-03-15T03:48:01Z     payments     payment-processor-7d4b8f9-x2k4n  Warning  Unhealthy  Liveness probe failed: HTTP probe failed with statuscode: 503
2024-03-15T03:48:31Z     payments     payment-processor-7d4b8f9-x2k4n  Normal   Killing    Container payment-processor failed liveness probe, will be restarted
2024-03-15T03:48:33Z     payments     payment-processor-7d4b8f9-x2k4n  Warning  OOMKilled  Container payment-processor exceeded memory limit (512Mi), current usage: 523Mi
2024-03-15T03:48:33Z     payments     payment-processor-7d4b8f9-x2k4n  Warning  BackOff    Back-off restarting failed container

kubectl top pod payment-processor-7d4b8f9-x2k4n -n payments --containers:
NAME                CPU(cores)   MEMORY(bytes)
payment-processor   245m         523Mi

Resource limits from deployment spec:
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"

Recent deployments:
  v2.3.0 -> v2.3.1 deployed 2024-03-15T03:30:00Z (15 min before crash)
  Changelog: "Added batch payment reconciliation job running every 5 min"
"""
```

---

## Step-by-Step: Compare All Three Models

Create a file called `model_comparison.py`:

```python
import anthropic
import time

client = anthropic.Anthropic()

K8S_LOG = """
TIMESTAMP                 NAMESPACE    POD                              EVENT
2024-03-15T03:42:01Z     payments     payment-processor-7d4b8f9-x2k4n  Normal   Scheduled  Successfully assigned payments/payment-processor-7d4b8f9-x2k4n to node-pool-2-abc123
2024-03-15T03:42:03Z     payments     payment-processor-7d4b8f9-x2k4n  Normal   Pulled     Container image "payments-svc:v2.3.1" already present on machine
2024-03-15T03:42:03Z     payments     payment-processor-7d4b8f9-x2k4n  Normal   Created    Created container payment-processor
2024-03-15T03:42:04Z     payments     payment-processor-7d4b8f9-x2k4n  Normal   Started    Started container payment-processor
2024-03-15T03:47:22Z     payments     payment-processor-7d4b8f9-x2k4n  Warning  Unhealthy  Readiness probe failed: HTTP probe failed with statuscode: 503
2024-03-15T03:48:01Z     payments     payment-processor-7d4b8f9-x2k4n  Warning  Unhealthy  Liveness probe failed: HTTP probe failed with statuscode: 503
2024-03-15T03:48:31Z     payments     payment-processor-7d4b8f9-x2k4n  Normal   Killing    Container payment-processor failed liveness probe, will be restarted
2024-03-15T03:48:33Z     payments     payment-processor-7d4b8f9-x2k4n  Warning  OOMKilled  Container payment-processor exceeded memory limit (512Mi), current usage: 523Mi
2024-03-15T03:48:33Z     payments     payment-processor-7d4b8f9-x2k4n  Warning  BackOff    Back-off restarting failed container

kubectl top pod payment-processor-7d4b8f9-x2k4n -n payments --containers:
NAME                CPU(cores)   MEMORY(bytes)
payment-processor   245m         523Mi

Resource limits from deployment spec:
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"

Recent deployments:
  v2.3.0 -> v2.3.1 deployed 2024-03-15T03:30:00Z (15 min before crash)
  Changelog: "Added batch payment reconciliation job running every 5 min"
"""

PROMPT = f"""Analyze this Kubernetes incident and provide:
1. What happened
2. Root cause
3. Recommended fix

Logs:
{K8S_LOG}
"""

models = [
    ("claude-haiku-35-20241022", "Haiku 3.5 (Junior On-Call)"),
    ("claude-sonnet-4-20250514", "Sonnet 4 (Senior SRE)"),
    ("claude-opus-4-20250514", "Opus 4 (Principal Architect)"),
]

for model_id, label in models:
    print("=" * 65)
    print(f"Model: {label}")
    print(f"ID: {model_id}")
    print("=" * 65)

    start_time = time.time()

    message = client.messages.create(
        model=model_id,
        max_tokens=1024,
        messages=[{"role": "user", "content": PROMPT}]
    )

    elapsed = time.time() - start_time

    print(f"\nResponse time: {elapsed:.2f}s")
    print(f"Input tokens: {message.usage.input_tokens}")
    print(f"Output tokens: {message.usage.output_tokens}")
    print(f"\n{message.content[0].text}")
    print("\n")
```

Run it:

```bash
python model_comparison.py
```

---

## Decision Matrix: Which Model for Which Task?

Use this as your operational guide:

| Task | Recommended Model | Why |
|------|-------------------|-----|
| Alert triage/classification | Haiku | Fast, cheap, good enough |
| Incident root cause analysis | Sonnet | Balanced depth and speed |
| Architecture review | Opus | Deep reasoning needed |
| Log pattern matching | Haiku | High volume, simple pattern |
| Runbook generation | Sonnet | Needs context understanding |
| Post-mortem writing | Opus | Complex narrative synthesis |
| Health check parsing | Haiku | Repetitive, structured output |
| Capacity planning analysis | Sonnet | Needs trend interpretation |
| Security audit review | Opus | Subtle reasoning, high stakes |

---

## Cost Comparison for This Lab

Assuming the same prompt (~400 input tokens) and ~300 output tokens:

| Model | Input Cost | Output Cost | Total | Relative |
|-------|-----------|-------------|-------|----------|
| Haiku 3.5 | $0.00032 | $0.0012 | $0.00152 | 1x |
| Sonnet 4 | $0.0012 | $0.0045 | $0.0057 | 3.75x |
| Opus 4 | $0.006 | $0.0225 | $0.0285 | 18.75x |

> At scale (10,000 alerts/day), choosing Haiku over Opus for triage saves ~$270/day.

---

## What Success Looks Like

Each model returns useful but differently-detailed analysis:

**Haiku** (fast, ~1-2s): Identifies OOMKilled, points to memory limit exceeded, suggests increasing limits.

**Sonnet** (balanced, ~3-5s): Connects the recent deployment (v2.3.1) to the memory spike, identifies the batch reconciliation job as the likely cause, suggests both a resource increase and code-level investigation.

**Opus** (thorough, ~8-15s): Provides the full causal chain — new batch job runs every 5 minutes, memory accumulates without proper cleanup, crosses the 512Mi limit within ~5 minutes of first execution. Recommends immediate mitigation (increase limits), short-term fix (add memory profiling), and long-term solution (streaming reconciliation instead of batch loading).

---

## Key Takeaway

Match model capability to task complexity — don't use Opus for alert triage, and don't use Haiku for architecture reviews. The right model is the one that gives you sufficient quality at the speed and cost your task demands. Build your AI-powered SRE tooling with model routing: fast models for high-volume tasks, powerful models for high-stakes decisions.
