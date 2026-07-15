#!/usr/bin/env python3
"""
Zero-Shot Prompting for DevOps

This script demonstrates zero-shot prompting techniques for DevOps and SRE tasks.
Zero-shot prompting means giving the model clear, specific instructions without
providing any examples. The model relies entirely on its pre-trained knowledge
to generate responses.

Prerequisites:
    - pip install anthropic
    - Export your API key: export ANTHROPIC_API_KEY="your-key-here"

Usage:
    python task1_zero_shot.py
"""

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-20250514"


def call_claude(prompt: str) -> str:
    """Send a zero-shot prompt to Claude and return the response."""
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def main():
    print("=" * 65)
    print("ZERO-SHOT PROMPTING FOR DEVOPS")
    print("=" * 65)
    print()
    print("What is Zero-Shot Prompting?")
    print("-" * 65)
    print("""
Zero-shot prompting is when you give the AI model a task with clear
instructions but WITHOUT providing any examples of the expected output.
The model uses only its pre-trained knowledge to respond.

This is the simplest prompting technique and works well when:
  - The task is straightforward and well-defined
  - The model has strong prior knowledge of the domain
  - You need quick answers without crafting examples

Let's see how it performs on real SRE/DevOps scenarios...
""")

    # =========================================================
    # Experiment 1: Analyze a Kubernetes Error
    # =========================================================
    print("=" * 65)
    print("EXPERIMENT 1: Analyze a Kubernetes Error (Zero-Shot)")
    print("=" * 65)
    print()

    prompt1 = """You are a Kubernetes expert. Analyze the following error and provide:
1. Root cause analysis
2. Immediate remediation steps
3. Long-term prevention strategies

Error from kubectl describe pod:
---
Name:         payment-service-7d4b8c6f9-x2k4m
Namespace:    production
Status:       Running
Containers:
  payment-api:
    State:          Waiting
      Reason:       CrashLoopBackOff
    Last State:     Terminated
      Reason:       OOMKilled
      Exit Code:    137
    Ready:          False
    Restart Count:  8
    Limits:
      memory: 256Mi
    Requests:
      memory: 128Mi
Events:
  Warning  BackOff  2m (x8 over 10m)  kubelet  Back-off restarting failed container
---"""

    print("Prompt being sent:")
    print("-" * 65)
    print(prompt1)
    print("-" * 65)
    print()
    print("Claude's Response:")
    print("-" * 65)
    response1 = call_claude(prompt1)
    print(response1)
    print()

    # =========================================================
    # Experiment 2: Generate kubectl Commands
    # =========================================================
    print("=" * 65)
    print("EXPERIMENT 2: Generate kubectl Commands (Zero-Shot)")
    print("=" * 65)
    print()

    prompt2 = """Generate a sequence of kubectl commands to debug a pod that is not
starting in a Kubernetes cluster. The pod name is "order-processor-5f8d7a3b1-mn9p2"
in the "staging" namespace.

Provide the commands in the order they should be executed, explain what
each command does, and describe what to look for in the output."""

    print("Prompt being sent:")
    print("-" * 65)
    print(prompt2)
    print("-" * 65)
    print()
    print("Claude's Response:")
    print("-" * 65)
    response2 = call_claude(prompt2)
    print(response2)
    print()

    # =========================================================
    # Experiment 3: Alert Triage with Zero-Shot
    # =========================================================
    print("=" * 65)
    print("EXPERIMENT 3: Alert Triage (Zero-Shot)")
    print("=" * 65)
    print()

    prompt3 = """You are an on-call SRE receiving the following Prometheus alert.
Provide a structured triage response including severity assessment,
immediate investigation steps, and escalation criteria.

Alert:
---
ALERT: HighErrorRate
  Severity: critical
  Service: api-gateway
  Description: Error rate for api-gateway has exceeded 5% for the last 10 minutes
  Current Value: 12.4%
  Threshold: 5%
  Labels:
    cluster: prod-us-east-1
    namespace: ingress
    pod_regex: api-gateway-.*
  Annotations:
    dashboard: https://grafana.internal/d/api-gateway
    runbook: https://wiki.internal/runbooks/api-gateway-errors
  Started: 2024-03-15T14:23:00Z
---"""

    print("Prompt being sent:")
    print("-" * 65)
    print(prompt3)
    print("-" * 65)
    print()
    print("Claude's Response:")
    print("-" * 65)
    response3 = call_claude(prompt3)
    print(response3)
    print()

    # =========================================================
    # Key Learnings
    # =========================================================
    print("=" * 65)
    print("KEY LEARNING: Zero-Shot Prompting Strengths")
    print("=" * 65)
    print("""
Zero-shot prompting works well for DevOps/SRE tasks because:

1. BROAD KNOWLEDGE: Claude has extensive training on Kubernetes, cloud
   infrastructure, and operational practices - no examples needed.

2. SPEED: You can get immediate answers without spending time crafting
   examples. Great for incident response when time is critical.

3. FLEXIBILITY: Works across a wide range of tasks - error analysis,
   command generation, alert triage, architecture review.

4. SIMPLICITY: Easy to construct prompts on the fly during incidents
   or when exploring unfamiliar systems.

Limitations to be aware of:
- Output format can be unpredictable without examples
- May not match your team's specific conventions or runbook style
- Complex multi-step reasoning may benefit from few-shot examples

When zero-shot isn't enough, add examples to guide the output format
and style. That's few-shot prompting - covered next!
""")

    print("=" * 65)
    print("Next: task2_few_shot.py - Learn how adding examples improves")
    print("      output consistency and format control.")
    print("=" * 65)


if __name__ == "__main__":
    main()
