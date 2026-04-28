#!/usr/bin/env python3
"""
Task 2: System Prompts — Anthropic Claude
See how a system prompt transforms a generic response into expert SRE triage.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic

def main():
    print("=" * 65)
    print("Task 2: System Prompts — Anthropic Claude")
    print("=" * 65)

    client = anthropic.Anthropic()

    alert = """Analyze this alert and give me a 3-step remediation plan:

ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)"""

    # Experiment 1: Without system prompt
    print("\nExperiment 1: No System Prompt (Generic)")
    print("-" * 65)

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": alert}]
    )
    print(message.content[0].text)

    # Experiment 2: With SRE system prompt
    print("\n" + "=" * 65)
    print("Experiment 2: With SRE System Prompt")
    print("-" * 65)

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system="You are a senior SRE with 10 years of Kubernetes experience. Be concise and actionable. Give kubectl commands, not general advice.",
        messages=[{"role": "user", "content": alert}]
    )
    print(message.content[0].text)

    print("\n" + "=" * 65)
    print("Key Learning: One system prompt line transforms generic advice")
    print("into expert SRE triage with actionable kubectl commands.")
    print("=" * 65)

    print("\nTask 2 Complete!")
    print("Next: python3 demos/anthropic/task3_persona_swap.py")


if __name__ == "__main__":
    main()
