#!/usr/bin/env python3
"""
Task 3: Persona Swap — Same Alert, Different Experts
See how the system prompt changes the entire perspective.
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

    alert = """Analyze this alert and give me a 3-step remediation plan:

ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)"""

    # TODO 1: Define three personas with different system prompts
    # Each persona analyzes the same alert from a completely different angle
    personas = [
        ("SRE Engineer", ___),  # TODO: Use "You are a senior SRE with 10 years of Kubernetes experience. Be concise and actionable."
        ("Network Engineer", ___),  # TODO: Use "You are a senior network engineer. Focus on connectivity, DNS, and network-level issues. Be concise."
        ("Security Engineer", ___),  # TODO: Use "You are a senior security engineer. Focus on security implications, access controls, and compliance. Be concise."
    ]

    for name, system_prompt in personas:
        print("=" * 60)
        print(f"PERSONA: {name}")
        print("=" * 60)

        # TODO 2: Call the API with each persona's system prompt
        message = client.messages.create(
            model="claude-sonnet-4-6-latest",
            max_tokens=512,
            system=___,  # TODO: Use system_prompt
            messages=[{"role": "user", "content": alert}]
        )

        # TODO 3: Print the response
        print(___)  # TODO: Use message.content[0].text
        print()

    print("=" * 65)
    print("Key Learning: Same alert, completely different responses.")
    print("The system prompt shapes the entire perspective.")
    print("=" * 65)

    print("\nTask 3 Complete!")
    print("Next: python3 demos/anthropic/task4_limitations.py")


if __name__ == "__main__":
    main()
