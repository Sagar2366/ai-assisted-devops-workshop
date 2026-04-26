#!/usr/bin/env python3
"""
Task 1: Your First API Call — Anthropic Claude
Learn what happens behind ChatGPT by making your first LLM API call.
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

    # Step 1: Create the Anthropic client (PRE-FILLED)
    # This connects to the Claude API using your ANTHROPIC_API_KEY
    client = anthropic.Anthropic()

    print("Step 1 Complete: Client created\n")

    # Experiment 1: The simplest possible API call
    print("Experiment 1: Basic API Call")
    print("-" * 65)

    # TODO 1: Create your first API call
    # Use client.messages.create() to send a message to Claude
    # - model: the Claude model to use
    # - max_tokens: maximum length of the response
    # - messages: a list with one dict containing "role" and "content"
    message = client.messages.create(
        model=___,  # TODO: Use "claude-sonnet-4-6-latest"
        max_tokens=___,  # TODO: Use 1024
        messages=[
            {
                "role": "user",
                "content": ___  # TODO: Use "What is Kubernetes and why do DevOps engineers use it?"
            }
        ]
    )

    # TODO 2: Print the response text
    # The response is in message.content[0].text
    print(___)  # TODO: Use message.content[0].text

    # Experiment 2: Try a different question
    print("\n" + "-" * 65)
    print("Experiment 2: Ask About a DevOps Tool")
    print("-" * 65)

    # TODO 3: Make another API call with a different DevOps question
    # Try asking about Prometheus, Terraform, Docker, or any tool you use
    message2 = client.messages.create(
        model="claude-sonnet-4-6-latest",
        max_tokens=1024,
        messages=[
            {
                "role": ___,  # TODO: Use "user"
                "content": ___  # TODO: Ask about any DevOps tool you like
            }
        ]
    )

    print(message2.content[0].text)

    # Experiment 3: Understand tokens
    print("\n" + "-" * 65)
    print("Experiment 3: Understanding Tokens")
    print("-" * 65)

    # TODO 4: Check how many tokens were used
    # The usage info is in message2.usage
    # It has input_tokens (what you sent) and output_tokens (what you got back)
    print(f"Input tokens:  {___}")  # TODO: Use message2.usage.input_tokens
    print(f"Output tokens: {___}")  # TODO: Use message2.usage.output_tokens

    print("\n" + "=" * 65)
    print("Key Learnings:")
    print("- An LLM API call: send a prompt, get a response")
    print("- This is what ChatGPT does behind the scenes")
    print("- Tokens = how the model measures text (roughly 1 per word)")
    print("- You pay per token — input tokens + output tokens")
    print("=" * 65)

    print("\nTask 1 Complete!")
    print("Next: python3 demos/anthropic/task2_system_prompts.py")


if __name__ == "__main__":
    main()
