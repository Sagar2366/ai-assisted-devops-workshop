# Lab 3: Persona Swap — Same Alert, Different Experts

This lab demonstrates how **system prompting** fundamentally shifts the lens through which an AI model analyzes a production incident. By fanning out a single alert to three distinct personas, you can generate a multi-dimensional triage report automatically.

---

## Mission
Send the same production incident to three different AI personas and compare how each expert analyzes the root cause and suggests remediation.

---

## The Concept: Why Parallel Personas?

In traditional automation, a script follows a single logical path. In LLM-based triage, the model follows a **Linguistic Lens**. Without a persona, an LLM provides a generic summary; with a persona, it mimics a **Cross-Functional War Room**.

### 1. Fighting "Blind Spot" Bias
During a P0 incident, an SRE might only look at the latest CI/CD pipeline, while the real issue is a latent mTLS certificate expiry. By fanning out the alert to three "experts" in parallel, you ensure that the "Network" and "Security" angles are investigated even if the on-call engineer is purely "DevOps" focused.

### 2. Pattern Matching vs. Log Analysis
The LLM isn't "logged into your cluster." It is performing high-speed pattern matching against millions of historical post-mortems:
* **SRE Lens:** Matches symptoms to **Deployment Patterns** (Canary failures, OOMKills).
* **Network Lens:** Matches symptoms to **Infrastructure Patterns** (Egress rules, DNS TTLs).
* **Security Lens:** Matches symptoms to **Policy Patterns** (RBAC, IAM, NetworkPolicies).

### 3. The "Intersection of Truth"
The value of this lab isn't just the three separate answers—it's where they **overlap**. If the SRE persona flags "Deploy #1042" and the Network persona flags "Connection Refused," your most likely culprit is a **Service or Ingress configuration change** within that specific deployment.

---

## Step-by-Step Implementation

### 1. Define the Multi-Dimensional Alert
The incident is designed to be ambiguous. Is it a bad code push? A DNS failure? A blocked port?

```python
alert = """Analyze this incident and give me a 3-step remediation plan:

ALERT: ServiceUnavailable
Namespace: production
Service: payment-api
Symptoms:
  - 503 errors spiking to 40% of requests
  - Intermittent connection timeouts from frontend to payment-api
  - payment-api pods are running (not crashing)
  - Started after deploy #1042 at 14:32 UTC
  - External payment gateway calls also failing
Last Log: "connection refused: upstream payment-gateway.internal:8443"
"""
```

### 2. Configure the Expert Personas
Define the system prompts that will guide the model's focus.

```python
personas = [
    (
        "SRE Engineer",
        "You are a senior SRE. Focus on deploy health, rollout strategy, and reliability. Provide kubectl commands."
    ),
    (
        "Network Engineer",
        "You are a senior network engineer. Focus on connectivity, DNS, and TLS issues causing 'connection refused'."
    ),
    (
        "Security Engineer",
        "You are a senior security engineer. Focus on permissions, mTLS, and NetworkPolicy changes in the deploy."
    ),
]
```

---

## Complete Implementation (Python)

```python
#!/usr/bin/env python3
import os
import sys
import anthropic

def main():
    # 1. Environment Safety Check
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    client = anthropic.Anthropic()

    # 2. The Multi-Dimensional Alert (The "Input")
    alert = """Analyze this incident and give me a 3-step remediation plan:
ALERT: ServiceUnavailable
Namespace: production
Service: payment-api
Symptoms:
  - 503 errors spiking to 40% of requests
  - Intermittent connection timeouts from frontend to payment-api
  - payment-api pods are running (not crashing)
  - Started after deploy #1042 at 14:32 UTC
  - External payment gateway calls also failing
Last Log: "connection refused: upstream payment-gateway.internal:8443"
"""

    # 3. Define the Expert Personas (The "Lenses")
    personas = [
        (
            "SRE Engineer",
            "You are a senior SRE. Focus on deploy health, rollout strategy, and reliability. Provide kubectl commands."
        ),
        (
            "Network Engineer",
            "You are a senior network engineer. Focus on connectivity, DNS, and TLS issues causing 'connection refused'."
        ),
        (
            "Security Engineer",
            "You are a senior security engineer. Focus on permissions, mTLS, and NetworkPolicy changes in the deploy."
        ),
    ]

    # 4. The Fan-Out Loop
    # We send the same alert to each persona to get a 360-degree triage report.
    for name, system_prompt in personas:
        print(f"\n{'='*60}")
        print(f"  PERSONA: {name}")
        print(f"{'='*60}")

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            system=system_prompt,
            messages=[{"role": "user", "content": alert}]
        )
        print(message.content[0].text)

if __name__ == "__main__":
    main()
```

---

## What Success Looks Like

| Expert | Primary Focus | Likely Recommendation |
| :--- | :--- | :--- |
| **SRE** | Deploy #1042 | `kubectl rollout undo` to restore service immediately. |
| **Network** | `internal:8443` | Check CoreDNS logs and test egress to the gateway. |
| **Security** | Auth/Policy | Verify if the new deploy changed the `ServiceAccount` or `NetworkPolicy`. |

## Key Takeaway
System prompts are not just "flavor"—they are **functional filters**. In a real-world DevOps pipeline, fanning out alerts to multiple personas ensures that the "blind spots" of one engineering discipline are covered by another before a human even starts triaging.

---
**Next:** [Lab 4: Limitations](lab4-limitations.md)
