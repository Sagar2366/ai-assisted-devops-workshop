#!/usr/bin/env python3
"""
Task 2: System Prompts — OpenAI GPT
Same system prompt experiment, different provider. See how GPT handles it.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export OPENAI_API_KEY="your-key-here"
  pip install openai
"""

from openai import OpenAI

def main():
    print("=" * 65)
    print("Task 2: System Prompts — OpenAI GPT")
    print("=" * 65)

    client = OpenAI()

    alert = """Analyze this alert and give me a 3-step remediation plan:

ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)"""

    # Experiment 1: Without system prompt
    print("Experiment 1: No System Prompt (Generic)")
    print("-" * 65)

    # TODO 1: Send the alert WITHOUT a system prompt
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=[{"role": "user", "content": ___}]  # TODO: Use alert
    )

    print(response.choices[0].message.content)

    # Experiment 2: With SRE system prompt
    print("\n" + "=" * 65)
    print("Experiment 2: With SRE System Prompt")
    print("-" * 65)

    # TODO 2: Add a system prompt
    # Key difference from Anthropic: system prompt goes as a MESSAGE with role="system"
    # Anthropic has a separate "system" parameter. OpenAI puts it in the messages list.
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=[
            {"role": ___,  "content": ___},  # TODO: Use "system" and "You are a senior SRE with 10 years of Kubernetes experience. Be concise and actionable."
            {"role": "user", "content": alert}
        ]
    )

    # TODO 3: Print the response
    print(___)  # TODO: Use response.choices[0].message.content

    print("\n" + "=" * 65)
    print("Key Difference:")
    print("  Anthropic: system='...' as a separate parameter")
    print("  OpenAI:    {'role': 'system', 'content': '...'} in messages list")
    print("Same concept, different API design.")
    print("=" * 65)

    print("\nTask 2 Complete!")
    print("Next: python3 demos/openai/task3_persona_swap.py")


if __name__ == "__main__":
    main()
