#!/usr/bin/env python3
"""
Task 4: AI Limitations — Anthropic Claude
Discover what AI models CANNOT do: hallucination, no real-time data, no code execution.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic

def main():
    print("=" * 65)
    print("Task 4: AI Limitations — Anthropic Claude")
    print("=" * 65)

    client = anthropic.Anthropic()

    # Limitation 1: Hallucination
    print("\nLimitation 1: Hallucination (Confident but Wrong)")
    print("-" * 65)

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        messages=[{"role": "user", "content": "Explain the kubectl autoheal command and show 3 examples of using it in production. Include all available flags."}]
    )
    print(message.content[0].text)
    print("\n>>> REALITY CHECK: 'kubectl autoheal' does NOT exist!")
    print(">>> The model may confidently describe a fake command. Always verify.")

    # Limitation 2: No Real-Time Data
    print("\n" + "-" * 65)
    print("Limitation 2: No Real-Time Data")
    print("-" * 65)

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        messages=[{"role": "user", "content": "What is the current CPU utilization of my Kubernetes cluster right now? List all pods that are currently running in the default namespace."}]
    )
    print(message.content[0].text)
    print("\n>>> REALITY CHECK: Claude has NO access to your infrastructure!")
    print(">>> It cannot query live systems, metrics, or dashboards.")

    # Limitation 3: No Code Execution
    print("\n" + "-" * 65)
    print("Limitation 3: No Execution Capability")
    print("-" * 65)

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        messages=[{"role": "user", "content": "Run 'kubectl get nodes' on my cluster and show me the output. Then restart the payment-service deployment."}]
    )
    print(message.content[0].text)
    print("\n>>> REALITY CHECK: Claude CANNOT execute commands!")
    print(">>> It generates text that looks like output, but nothing actually runs.")

    print("\n" + "=" * 65)
    print("Key Learning: AI models have 3 critical limitations:")
    print("  1. Hallucination — they make up plausible-sounding facts")
    print("  2. No real-time  — they have a knowledge cutoff date")
    print("  3. No execution  — they generate text, not actions")
    print("NEVER run AI-generated commands in production without reading them first.")
    print("=" * 65)

    print("\nTask 4 Complete!")
    print("Next: python3 demos/anthropic/task5_conversation_history.py")


if __name__ == "__main__":
    main()
