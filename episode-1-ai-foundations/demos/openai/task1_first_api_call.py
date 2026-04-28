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

    client = OpenAI()

    # Experiment 1: Basic API call
    print("\nExperiment 1: Basic API Call")
    print("-" * 65)

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "What is Kubernetes and why do DevOps engineers use it?"}
        ]
    )
    print(response.choices[0].message.content)

    # Experiment 2: Different question
    print("\n" + "-" * 65)
    print("Experiment 2: Different Question")
    print("-" * 65)

    response2 = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Explain Prometheus in 3 sentences"}
        ]
    )
    print(response2.choices[0].message.content)

    # Experiment 3: Token usage
    print("\n" + "-" * 65)
    print("Experiment 3: Token Usage")
    print("-" * 65)
    print(f"Input tokens:  {response2.usage.prompt_tokens}")
    print(f"Output tokens: {response2.usage.completion_tokens}")

    print("\n" + "=" * 65)
    print("Key Learning: Same pattern, different SDK.")
    print("Anthropic: input/output tokens. OpenAI: prompt/completion tokens.")
    print("Same concept, different names.")
    print("=" * 65)

    print("\nTask 1 Complete!")
    print("Next: python3 demos/openai/task2_system_prompts.py")


if __name__ == "__main__":
    main()
