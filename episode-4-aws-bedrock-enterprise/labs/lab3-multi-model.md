# Lab 3: Multi-Model Strategy — One Gateway, Many Brains

> **Mission:** Use multiple foundation models through a single AWS Bedrock gateway and understand when to deploy each one. By the end of this lab, you will call three different models with the same SRE alert and compare their responses to build an informed routing strategy.

---

## Concept: Bedrock as a Model Marketplace

Think of AWS Bedrock as a **unified observability platform** for AI models.

In the monitoring world, you might run Prometheus for metrics, Datadog for APM, and CloudWatch for AWS-native services — but you access them through a single pane of glass (Grafana, for instance). Each tool has strengths: Prometheus excels at time-series cardinality, Datadog at distributed tracing, CloudWatch at AWS service integration.

Bedrock works the same way for foundation models:

```
Traditional Monitoring              AI Model Strategy
─────────────────────              ─────────────────
Prometheus (metrics)       ←→      Claude (complex reasoning)
Datadog (APM/traces)       ←→      Llama (fast, open-source)
CloudWatch (AWS native)    ←→      Titan (AWS-native, cost-effective)
         │                                  │
    Grafana (unified)              Bedrock (unified API)
```

**Same API client. Same authentication. Same billing. Different brains.**

You do not need separate API keys, separate SDKs, or separate infrastructure. One `boto3` client talks to all of them.

---

## The Scenario

Throughout this lab, we will send the same production alert to three different models and compare their analysis:

```
ALERT: Production API latency p99 jumped from 200ms to 2.5s in the last 5 minutes.
3 pods showing OOMKilled. Redis connection pool exhausted.
```

This is a real-world multi-signal alert — memory pressure, network resource exhaustion, and latency degradation happening simultaneously. A good SRE needs to identify the root cause chain, not just respond to symptoms.

---

## Step 1: Set Up the Bedrock Client

```python
import boto3
import json
import time

# Single client for all models
client = boto3.client("bedrock-runtime", region_name="us-east-1")

# The alert we'll analyze with each model
ALERT = """Production API latency p99 jumped from 200ms to 2.5s in the last 5 minutes.
3 pods showing OOMKilled. Redis connection pool exhausted.

Context:
- Deployment happened 7 minutes ago (image tag: api-v2.4.1)
- Traffic volume is normal (no spike)
- Redis cluster has 3 nodes, all reporting high memory usage
- Pod memory limit: 512Mi, current usage before OOM: 498Mi

What is the most likely root cause chain, and what are the immediate remediation steps?"""
```

---

## Step 2: Call Claude on Bedrock (Complex Analysis)

Claude uses the **Messages API format** — structured, multi-turn capable, and designed for nuanced reasoning.

```python
# Claude - Messages API format
start = time.time()
response = client.invoke_model(
    modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-10-25",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": ALERT}]
    })
)
claude_time = time.time() - start

claude_result = json.loads(response["body"].read())
claude_response = claude_result["content"][0]["text"]

print(f"Claude responded in {claude_time:.2f}s")
print(f"Tokens used: {claude_result['usage']['input_tokens']} in / {claude_result['usage']['output_tokens']} out")
print(f"\n{claude_response}")
```

**Why Claude here:** Claude excels at multi-step causal reasoning. It will likely identify the deployment as the trigger, trace the memory leak to Redis connection handling, and provide ordered remediation steps.

---

## Step 3: Call Llama on Bedrock (Fast Triage)

Llama uses a **prompt-based format** with special tokens for conversation structure.

```python
# Llama - prompt format with special tokens
start = time.time()
response = client.invoke_model(
    modelId="meta.llama3-1-8b-instruct-v1:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
        "prompt": f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{ALERT}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
        "max_gen_len": 1024,
        "temperature": 0.1
    })
)
llama_time = time.time() - start

llama_result = json.loads(response["body"].read())
llama_response = llama_result["generation"]

print(f"Llama responded in {llama_time:.2f}s")
print(f"\n{llama_response}")
```

**Why Llama here:** The 8B parameter model is fast and cheap. For initial triage — "is this a P1 or P3?" — speed matters more than depth.

---

## Step 4: Call Titan on Bedrock (Summarization)

Titan uses an **inputText format** with a nested configuration block.

```python
# Titan - inputText format
start = time.time()
response = client.invoke_model(
    modelId="amazon.titan-text-express-v1",
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
        "inputText": f"Summarize the following alert into a 2-sentence executive summary and assign a severity (P1-P4):\n\n{ALERT}",
        "textGenerationConfig": {
            "maxTokenCount": 1024,
            "temperature": 0.1
        }
    })
)
titan_time = time.time() - start

titan_result = json.loads(response["body"].read())
titan_response = titan_result["results"][0]["outputText"]

print(f"Titan responded in {titan_time:.2f}s")
print(f"\n{titan_response}")
```

**Why Titan here:** For generating concise summaries that go into Slack notifications or PagerDuty annotations, you want brevity and cost-effectiveness, not a dissertation.

---

## Step 5: Compare Results

```python
print("=" * 70)
print("MODEL COMPARISON FOR INCIDENT ANALYSIS")
print("=" * 70)

print(f"\n{'Model':<20} {'Response Time':<15} {'Best For'}")
print("-" * 70)
print(f"{'Claude Sonnet':<20} {claude_time:.2f}s{'':<10} {'Root cause analysis, remediation planning'}")
print(f"{'Llama 3.1 8B':<20} {llama_time:.2f}s{'':<10} {'Fast triage, initial classification'}")
print(f"{'Titan Express':<20} {titan_time:.2f}s{'':<10} {'Summaries, notifications, logging'}")
```

---

## Model Selection Strategy

### When to Use Each Model

| Factor | Claude | Llama 3.1 (8B) | Titan Express |
|--------|--------|-----------------|---------------|
| **Complexity** | Multi-signal correlation, RCA | Single-signal triage | Summarization |
| **Urgency** | Post-incident review | Real-time alerting | Notification generation |
| **Cost** | Higher per token | Lower per token | Lowest per token |
| **Accuracy** | Highest for reasoning | Good for classification | Good for extraction |
| **Data sensitivity** | Via Bedrock (compliant) | Via Bedrock (compliant) | Via Bedrock (compliant) |
| **Latency tolerance** | Seconds acceptable | Sub-second preferred | Sub-second preferred |

### Decision Matrix for SRE Workflows

```python
def select_model(alert_type, urgency, complexity):
    """Select the right model for the job."""
    
    # P1 real-time triage: speed wins
    if urgency == "immediate" and complexity == "low":
        return "meta.llama3-1-8b-instruct-v1:0"
    
    # Complex multi-signal incidents: depth wins
    if complexity == "high":
        return "us.anthropic.claude-sonnet-4-20250514-v1:0"
    
    # Notification/summary generation: cost wins
    if alert_type == "notification":
        return "amazon.titan-text-express-v1"
    
    # Default: balanced choice
    return "us.anthropic.claude-sonnet-4-20250514-v1:0"
```

---

## Exercise: Build an Alert Router

Create a function that routes different types of alerts to the appropriate model:

```python
def route_alert(alert):
    """Route an alert to the best model based on its characteristics."""
    
    # Classify the alert
    signals = count_signals(alert)  # How many distinct symptoms?
    has_deployment = "deploy" in alert.lower()
    needs_rca = signals > 2 or has_deployment
    
    if needs_rca:
        # Complex: use Claude for root cause analysis
        model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
        prompt_style = "messages"
    elif "summarize" in alert.lower() or "notify" in alert.lower():
        # Summary: use Titan for cost-effective generation
        model_id = "amazon.titan-text-express-v1"
        prompt_style = "inputText"
    else:
        # Fast triage: use Llama for quick classification
        model_id = "meta.llama3-1-8b-instruct-v1:0"
        prompt_style = "prompt"
    
    return call_model(model_id, prompt_style, alert)


def count_signals(alert):
    """Count distinct problem signals in an alert."""
    indicators = ["latency", "oom", "memory", "cpu", "connection",
                  "timeout", "error rate", "5xx", "disk", "network"]
    return sum(1 for i in indicators if i in alert.lower())
```

**Challenge:** Extend this router to handle:
1. Alerts that mention sensitive data (route to Bedrock-only models for compliance)
2. Alerts during business hours vs. off-hours (adjust cost tolerance)
3. Repeated alerts (use cheaper models for known issues)

---

## What Success Looks Like

After completing this lab, you can:

- [x] Call Claude, Llama, and Titan through the same Bedrock client
- [x] Understand the different request formats each model requires
- [x] Compare response quality, latency, and cost across models
- [x] Make informed decisions about which model to use for which SRE task
- [x] Build routing logic that selects models based on alert characteristics

---

## Key Takeaway

> **Enterprise AI is not about picking one model — it is about deploying the right model for the right job.**

Just as no SRE team uses a single tool for all observability (you would not run Prometheus queries to check if a webpage loads), no AI-powered operations platform should rely on a single model. Claude for depth. Llama for speed. Titan for cost. Bedrock gives you one gateway to all of them.

The best SRE teams will build model selection into their runbooks the same way they build tool selection into their incident response today.
