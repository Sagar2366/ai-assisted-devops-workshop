#!/usr/bin/env python3
"""
Task 1: Your First API Call — Anthropic Claude
Send a Kubernetes question to Claude and get a response.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic

def main():
    print("=" * 65)
    print("Task 1: Your First API Call — Anthropic Claude")
    print("=" * 65)

    client = anthropic.Anthropic()

    # Experiment 1: Basic API call
    print("\nExperiment 1: Basic API Call")
    print("-" * 65)

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "What is Kubernetes and why do DevOps engineers use it?"}
        ]
    )
    print(message.content[0].text)

    # Experiment 2: Different question
    print("\n" + "-" * 65)
    print("Experiment 2: Different Question")
    print("-" * 65)

    message2 = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Explain Prometheus in 3 sentences"}
        ]
    )
    print(message2.content[0].text)

    # Experiment 3: Token usage
    print("\n" + "-" * 65)
    print("Experiment 3: Token Usage")
    print("-" * 65)
    print(f"Input tokens:  {message2.usage.input_tokens}")
    print(f"Output tokens: {message2.usage.output_tokens}")

    print("\n" + "=" * 65)
    print("Key Learning: Send a prompt (tokens in), get a response (tokens out).")
    print("That's inference. Same pattern across all providers.")
    print("=" * 65)

    print("\nTask 1 Complete!")
    print("Next: python3 demos/anthropic/task2_system_prompts.py")


if __name__ == "__main__":
    main()
