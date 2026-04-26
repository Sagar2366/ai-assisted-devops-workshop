#!/usr/bin/env python3
"""
Task 1: Your First API Call — OpenAI GPT
Same task as the Anthropic lab, different provider. Notice the pattern is almost identical.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export OPENAI_API_KEY="your-key-here"
  pip install openai
"""

from openai import OpenAI

def main():
    print("=" * 65)
    print("Task 1: Your First API Call — OpenAI GPT")
    print("=" * 65)

    # Step 1: Create the OpenAI client (PRE-FILLED)
    # This connects to the OpenAI API using your OPENAI_API_KEY
    client = OpenAI()

    print("Step 1 Complete: Client created\n")

    # Experiment 1: Basic API call
    print("Experiment 1: Basic API Call")
    print("-" * 65)

    # TODO 1: Create your first OpenAI API call
    # OpenAI uses client.chat.completions.create()
    # - model: the GPT model to use
    # - max_tokens: maximum length of the response
    # - messages: a list of dicts with "role" and "content"
    response = client.chat.completions.create(
        model=___,  # TODO: Use "gpt-4o"
        max_tokens=___,  # TODO: Use 1024
        messages=[
            {
                "role": "user",
                "content": ___  # TODO: Use "What is Kubernetes and why do DevOps engineers use it?"
            }
        ]
    )

    # TODO 2: Print the response text
    # OpenAI pattern: response.choices[0].message.content
    print(___)  # TODO: Use response.choices[0].message.content

    # Experiment 2: Compare with Anthropic
    print("\n" + "-" * 65)
    print("Experiment 2: Notice the Pattern")
    print("-" * 65)
    print("Anthropic: client.messages.create(model, max_tokens, messages)")
    print("OpenAI:    client.chat.completions.create(model, max_tokens, messages)")
    print("\nSame idea, slightly different SDK. The pattern is universal.")

    # Experiment 3: Check usage
    print("\n" + "-" * 65)
    print("Experiment 3: Token Usage")
    print("-" * 65)

    # TODO 3: Print token usage
    # OpenAI pattern: response.usage.prompt_tokens and response.usage.completion_tokens
    print(f"Input tokens:  {___}")  # TODO: Use response.usage.prompt_tokens
    print(f"Output tokens: {___}")  # TODO: Use response.usage.completion_tokens

    print("\n" + "=" * 65)
    print("Key Learning: Same pattern, different SDK.")
    print("Anthropic calls them 'input/output tokens'")
    print("OpenAI calls them 'prompt/completion tokens'")
    print("Same concept, different names.")
    print("=" * 65)

    print("\nTask 1 Complete!")
    print("Next: python3 demos/openai/task2_system_prompts.py")


if __name__ == "__main__":
    main()
