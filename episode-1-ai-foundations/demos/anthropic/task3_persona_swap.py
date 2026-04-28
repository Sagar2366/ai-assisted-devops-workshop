#!/usr/bin/env python3
"""
Task 3: Persona Swap — Anthropic Claude
Same alert, 3 different personas. Watch how the system prompt completely changes the response.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic

def main():
    print("=" * 65)
    print("Task 3: Persona Swap — Anthropic Claude")
    print("=" * 65)

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
        ("SRE Engineer", "You are a senior SRE with 10 years of Kubernetes experience. Focus on deploy health, rollout strategy, resource limits, and service reliability. Give kubectl commands."),
        ("Network Engineer", "You are a senior network engineer. Focus on connectivity, DNS resolution, network policies, port access, and TLS/mTLS issues."),
        ("Security Engineer", "You are a senior security engineer. Focus on service account permissions, mTLS misconfiguration, and network policy rule changes."),
    ]

    for name, system_prompt in personas:
        print(f"\n{'=' * 60}")
        print(f"  PERSONA: {name}")
        print(f"{'=' * 60}")

        message = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=512,
            system=system_prompt,
            messages=[{"role": "user", "content": alert}]
        )
        print(message.content[0].text)

    print("\n" + "=" * 65)
    print("Key Learning: Same data, different system prompt = different expert.")
    print("In production, route the same alert to multiple AI personas for")
    print("comprehensive triage — SRE + Security + Network perspectives.")
    print("=" * 65)

    print("\nTask 3 Complete!")
    print("Next: python3 demos/anthropic/task4_limitations.py")


if __name__ == "__main__":
    main()
