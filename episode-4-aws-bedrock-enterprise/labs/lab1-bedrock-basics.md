# Lab 1: Bedrock Basics — Your First Enterprise AI Call

> **Mission:** Make your first Bedrock API call with Claude and understand the `invoke_model` pattern. By the end of this lab, you will be able to send SRE-relevant prompts to Claude through Bedrock and parse structured responses.

---

## Concept: Bedrock as a Managed Gateway

Think of AWS Bedrock like an **API Gateway that sits in front of AI models**. Just as an API Gateway handles authentication, rate limiting, throttling, and logging for your microservices — Bedrock does the same for AI models.

```
Without Bedrock:
  Your App --> [manage keys] --> [manage scaling] --> [manage infra] --> AI Model

With Bedrock:
  Your App --> [IAM Auth] --> Bedrock Gateway --> AI Model
                                |
                                +--> CloudTrail (audit)
                                +--> CloudWatch (metrics)
                                +--> VPC Endpoints (network isolation)
```

You do not manage the inference infrastructure. You send a request, you get a response. AWS handles GPUs, scaling, availability, and patching — the same way RDS handles your database infrastructure.

For an SRE, this means:
- **No GPU fleet to page about at 3 AM**
- **No model serving infrastructure to maintain**
- **Same observability stack** you already use (CloudWatch, X-Ray)
- **Same security controls** (IAM, VPC, KMS)

---

## The invoke_model Pattern

Every Bedrock call follows the same three-step pattern:

1. **Create a client** (bedrock-runtime, not bedrock)
2. **Build a request body** (model-specific format)
3. **Parse the response** (read the body stream)

```python
"""
Bedrock Basics: Your First AI Call
Makes a simple request to Claude via AWS Bedrock.
"""

import boto3
import json

print("=" * 65)
print("BEDROCK BASICS: FIRST API CALL")
print("=" * 65)

# Step 1: Create the Bedrock Runtime client
# Note: "bedrock-runtime" is for inference (invoke_model)
#        "bedrock" is for management (list_models, etc.)
client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Step 2: Build the request
model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
request_body = {
    "anthropic_version": "bedrock-2023-10-25",
    "max_tokens": 1024,
    "messages": [
        {
            "role": "user",
            "content": "Analyze this K8s pod crash: CrashLoopBackOff with OOMKilled reason, memory limit 256Mi"
        }
    ]
}

print(f"\nModel:  {model_id}")
print(f"Prompt: {request_body['messages'][0]['content'][:60]}...")
print("-" * 65)

# Step 3: Invoke the model
response = client.invoke_model(
    modelId=model_id,
    contentType="application/json",
    accept="application/json",
    body=json.dumps(request_body)
)

# Step 4: Parse the response
result = json.loads(response["body"].read())
answer = result["content"][0]["text"]

print("\nClaude's Analysis:")
print("-" * 65)
print(answer)
print("-" * 65)
print(f"\nTokens used — Input: {result['usage']['input_tokens']}, "
      f"Output: {result['usage']['output_tokens']}")
print("=" * 65)
```

---

## Understanding the Request Structure

Each part of the request body serves a specific purpose:

```python
request_body = {
    # Required: Tells Bedrock which message format version to use
    "anthropic_version": "bedrock-2023-10-25",

    # Required: Maximum tokens in the response (controls cost and length)
    "max_tokens": 1024,

    # Required: The conversation messages
    "messages": [
        {"role": "user", "content": "Your prompt here"}
    ],

    # Optional: System prompt (sets behavior/persona)
    "system": "You are an SRE expert. Be concise and actionable.",

    # Optional: Controls randomness (0.0 = deterministic, 1.0 = creative)
    "temperature": 0.3
}
```

---

## Direct Claude API vs. Bedrock API

| Aspect | Direct Claude API | AWS Bedrock |
|--------|-------------------|-------------|
| **Authentication** | Anthropic API key | AWS IAM credentials |
| **Billing** | Anthropic account | AWS account (consolidated billing) |
| **Network** | Public internet | VPC endpoints available |
| **Audit logging** | Custom implementation | CloudTrail (automatic) |
| **Rate limiting** | Per API key | Per account, adjustable via quota |
| **Model** | Same Claude model | Same Claude model |
| **Compliance** | Anthropic SOC2 | AWS compliance (HIPAA, FedRAMP, etc.) |
| **Multi-model** | Anthropic models only | Claude + Llama + Titan + others |
| **Cost control** | API key spending limits | AWS Budgets, SCPs, tag-based allocation |

The model itself is identical — the difference is entirely in the delivery mechanism and enterprise controls around it.

---

## Exercise: SRE Incident Analysis

Build a more complete incident analysis call with a system prompt and structured output:

```python
"""
Exercise: SRE Incident Query via Bedrock
Sends a realistic incident scenario and parses the response.
"""

import boto3
import json
from datetime import datetime

print("=" * 65)
print("SRE INCIDENT ANALYSIS VIA BEDROCK")
print("=" * 65)

client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Realistic incident scenario
incident_data = """
INCIDENT REPORT:
- Service: payment-gateway
- Alert: Latency P99 spike from 200ms to 4500ms
- Duration: Started 12 minutes ago
- Error rate: Increased from 0.1% to 15%
- Recent changes: Deployed v2.3.1 twenty minutes ago
- Affected: 30% of checkout requests timing out
- Dependencies: Redis cluster, PostgreSQL, Stripe API
- Redis memory: 89% utilized (threshold: 85%)
- PostgreSQL connections: 180/200 max
"""

request_body = {
    "anthropic_version": "bedrock-2023-10-25",
    "max_tokens": 2048,
    "temperature": 0.2,
    "system": (
        "You are a Senior SRE performing incident response. "
        "Provide analysis in this exact format:\n"
        "1. SEVERITY ASSESSMENT\n"
        "2. MOST LIKELY ROOT CAUSE\n"
        "3. IMMEDIATE ACTIONS (numbered, in priority order)\n"
        "4. ROLLBACK RECOMMENDATION (yes/no with reasoning)\n"
        "Be concise and actionable. No fluff."
    ),
    "messages": [
        {
            "role": "user",
            "content": f"Analyze this incident and recommend actions:\n{incident_data}"
        }
    ]
}

print(f"\nTimestamp: {datetime.now().isoformat()}")
print(f"Scenario: Payment gateway latency spike")
print("-" * 65)

response = client.invoke_model(
    modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps(request_body)
)

result = json.loads(response["body"].read())
analysis = result["content"][0]["text"]

print("\nAI-Assisted Incident Analysis:")
print("-" * 65)
print(analysis)
print("-" * 65)
print(f"\nModel:        {result.get('model', 'claude-sonnet')}")
print(f"Input tokens: {result['usage']['input_tokens']}")
print(f"Output tokens:{result['usage']['output_tokens']}")
print(f"Stop reason:  {result.get('stop_reason', 'end_turn')}")
print("=" * 65)
```

---

## Handling Errors Gracefully

In production SRE tooling, always handle Bedrock errors:

```python
import boto3
import json
from botocore.exceptions import ClientError

print("=" * 65)
print("BEDROCK CALL WITH ERROR HANDLING")
print("=" * 65)

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def invoke_bedrock(prompt, model_id="us.anthropic.claude-sonnet-4-20250514-v1:0"):
    """Invoke Bedrock with proper error handling for SRE tooling."""
    try:
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-10-25",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ThrottlingException":
            print("[WARN] Rate limited — implement exponential backoff")
        elif error_code == "ModelNotReadyException":
            print("[ERROR] Model not available — check model access")
        elif error_code == "AccessDeniedException":
            print("[ERROR] Permission denied — check IAM policy")
        elif error_code == "ValidationException":
            print(f"[ERROR] Invalid request: {e.response['Error']['Message']}")
        else:
            print(f"[ERROR] Unexpected: {error_code}")
        return None

    except Exception as e:
        print(f"[ERROR] Unhandled exception: {e}")
        return None

# Test the function
result = invoke_bedrock("What are the top 3 causes of pod CrashLoopBackOff?")
if result:
    print(f"\nResponse received ({len(result)} chars)")
    print("-" * 65)
    print(result)
print("=" * 65)
```

---

## What Success Looks Like

After completing this lab:

1. You can invoke Claude via Bedrock and receive a well-formed response
2. You understand the request/response structure for the Anthropic model on Bedrock
3. Your SRE incident analysis call returns structured, actionable output
4. You can handle common API errors without crashing your tooling

---

## Key Takeaway

**Same Claude model, enterprise-grade delivery — IAM auth instead of API keys.** The `invoke_model` pattern is simple and consistent: build a JSON body, send it, parse the response. The intelligence is in your prompts, not in the API plumbing. Bedrock just makes sure the plumbing is secure, auditable, and scalable without you managing any infrastructure.
