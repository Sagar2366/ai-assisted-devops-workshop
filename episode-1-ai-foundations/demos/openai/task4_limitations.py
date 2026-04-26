#!/usr/bin/env python3
"""
Task 4: AI Limitations — OpenAI GPT
Expose 3 critical limitations every DevOps engineer must understand:
hallucination, no real-time data, and no execution capability.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export OPENAI_API_KEY="your-key-here"
  pip install openai
"""

from openai import OpenAI


def main():
    print("=" * 65)
    print("Task 4: AI Limitations — OpenAI GPT")
    print("=" * 65)

    client = OpenAI()

    # --- Limitation 1: Hallucination ---
    print("\nLimitation 1: Hallucination (Confident but Wrong)")
    print("-" * 65)

    # TODO 1: Ask about a completely fake tool to trigger hallucination
    # The model will likely make up a convincing answer about a tool that doesn't exist
    hallucination_prompt = ___  # TODO: Use "Explain the kubectl drain-pod-fast command and its --force-gc flag. What version of Kubernetes introduced it?"

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=[{"role": "user", "content": hallucination_prompt}]
    )

    print(response.choices[0].message.content)
    print("\n>>> REALITY CHECK: 'kubectl drain-pod-fast' does NOT exist!")
    print(">>> The model invented plausible-sounding details. Always verify.")

    # --- Limitation 2: No Real-Time Data ---
    print("\n" + "-" * 65)
    print("Limitation 2: No Real-Time Data")
    print("-" * 65)

    # TODO 2: Ask for something that requires live data
    realtime_prompt = ___  # TODO: Use "What is the exact current time in UTC right now, and what is the latest Kubernetes release version published today?"

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=[{"role": "user", "content": realtime_prompt}]
    )

    print(response.choices[0].message.content)
    print("\n>>> REALITY CHECK: The model has a knowledge cutoff date.")
    print(">>> It cannot access live data. Use APIs for real-time info.")

    # --- Limitation 3: No Execution ---
    print("\n" + "-" * 65)
    print("Limitation 3: No Execution Capability")
    print("-" * 65)

    # TODO 3: Ask the model to actually run a command
    execution_prompt = ___  # TODO: Use "Run 'kubectl get pods -A' on my cluster and show me the output."

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=[{"role": "user", "content": execution_prompt}]
    )

    print(response.choices[0].message.content)
    print("\n>>> REALITY CHECK: The model CANNOT execute commands.")
    print(">>> It can only generate text. You need tool use (Task 9+)")
    print(">>> to let an AI trigger real actions.")

    print("\n" + "=" * 65)
    print("Key Learning: AI models have 3 critical limitations:")
    print("  1. Hallucination — they make up plausible-sounding facts")
    print("  2. No real-time  — they have a knowledge cutoff date")
    print("  3. No execution  — they generate text, not actions")
    print("Always verify, always add guardrails, never trust blindly.")
    print("=" * 65)

    print("\nTask 4 Complete!")
    print("Next: python3 demos/openai/task4b_basic_tool.py")


if __name__ == "__main__":
    main()
