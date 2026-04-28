# Lab 3: Persona Swap — Same Alert, Different Experts

> **Mission:** Send the same production incident to three different AI personas and compare how each expert analyzes it.

---

## The Concept

Same alert. Three different system prompts. Three completely different analyses.

- **SRE Engineer** — deploy rollback, pod health, resource limits, rollout strategy
- **Network Engineer** — connection refused, DNS resolution, network policies, TLS/mTLS
- **Security Engineer** — service account permissions, mTLS misconfiguration, network policy rules, audit trail

### Why this works: "Attention Weighting"
The system prompt isn't just a tone shift; it acts as a **functional filter**. By assigning a persona, you force the model to prioritize specific "attention weights" in its training data to turning a generic assistant into a specialized domain expert. This creates a **multi-angle triage report** where each expert looks for different root-cause candidates in the same data.

---

## What You'll Build

Loop through three personas, send the same production incident to each, and print all three responses side by side to simulate a cross-functional war room.

---

## Step 1: Define the Multi-Dimensional Alert

This alert is deliberately ambiguous—a 503 spike with a failed external gateway call after a deploy. Each expert will find something different in it.

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

---

## Step 2: Define the Personas

```python
personas = [
    (
        "SRE Engineer",
        "You are a senior SRE with 10 years of Kubernetes experience. Focus on deploy health, rollout strategy, resource limits, and service reliability. Give kubectl commands."
    ),
    (
        "Network Engineer",
        "You are a senior network engineer. Focus on connectivity, DNS resolution, network policies, port access, and TLS/mTLS issues."
    ),
    (
        "Security Engineer",
        "You are a senior security engineer. Focus on service account permissions, mTLS misconfiguration, and network policy rule changes."
    ),
]
```

---

## Step 3: Loop Through Each Persona

Send the same alert with each persona's system prompt.

```python
for title, system_prompt in personas:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": alert}]
    )
    print(message.content[0].text)
```

---

## What Success Looks Like

* **SRE Engineer:** Looks at deploy #1042 — suggests `rollout undo`, checks pod readiness probes, and reviews resource limits.
* **Network Engineer:** Focuses on `connection refused` on port 8443 — checks DNS resolution of `payment-gateway.internal` and inspects egress network policies.
* **Security Engineer:** Asks what deploy #1042 changed in terms of IAM — checks if `ServiceAccount` permissions were modified or if mTLS is failing.

**Same incident — completely different analysis from each expert.**

---

## Key Takeaway

The system prompt isn't decoration — it fundamentally changes what the model focuses on. In production, you can swap personas for **multi-angle incident analysis**: one alert, three expert opinions. This prevents "tunnel vision" by ensuring that the "Security" and "Network" blind spots are automatically covered by the AI during a high-pressure triage.

---

## Complete Code (Anthropic)

```python
#!/usr/bin/env python3
"""Task 3: Persona Swap — Same Alert, Different Experts"""
import anthropic
import os

def main():
    client = anthropic.Anthropic()

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

    personas = [
        ("SRE Engineer", "You are a senior SRE. Focus on deploy health, rollout strategy, and reliability. Be concise."),
        ("Network Engineer", "You are a senior network engineer. Focus on connectivity, DNS, and TLS issues. Be concise."),
        ("Security Engineer", "You are a senior security engineer. Focus on permissions, mTLS, and network security. Be concise."),
    ]

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

Next: [Lab 4: Limitations](lab4-limitations.md)
