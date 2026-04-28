#!/usr/bin/env python3
"""
Task 6: Context Window Management — Anthropic Claude
Learn how conversations overflow the context window using a real SRE scenario.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic

def main():
    print("=" * 65)
    print("Task 6: Context Window Management — Anthropic Claude")
    print("=" * 65)

    client = anthropic.Anthropic()
    system = "You are a helpful SRE assistant. Remember details from the conversation."

    # Build a 10-turn SRE conversation
    print("Building a 10-turn SRE conversation...")
    print("-" * 65)

    conversation = []

    topics = [
        "My name is Sagar, I'm an SRE at Acme Corp.",
        "We run EKS with 50 microservices.",
        "Our budget is $500/month for AI tools.",
        "The payment-service pod keeps OOMing.",
        "Memory limit is 256Mi, usage peaks at 255Mi.",
        "We use ArgoCD for deployments.",
        "Prometheus and Grafana for monitoring.",
        "Team of 5 SREs covering 3 time zones.",
        "Biggest pain point is OOM after every deploy.",
        "We need a cost-effective solution."
    ]

    for i, topic in enumerate(topics, 1):
        conversation.append({"role": "user", "content": topic})
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=128,
            system=system,
            messages=conversation
        )
        reply = response.content[0].text
        conversation.append({"role": "assistant", "content": reply})
        print(f"Turn {i}: {topic[:50]}...")

    print(f"\nTotal messages: {len(conversation)}")

    # Test with full history
    print("\n" + "=" * 65)
    print("Test 1: Full History — Agent Remembers Everything")
    print("-" * 65)

    test_msg = "Based on everything you know about me, what's your recommendation?"
    conversation.append({"role": "user", "content": test_msg})
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        system=system,
        messages=conversation
    )
    print(f"Question: {test_msg}")
    print(f"Response: {response.content[0].text}")
    conversation.append({"role": "assistant", "content": response.content[0].text})

    # Sliding window — keep only last 3 exchanges
    print("\n" + "=" * 65)
    print("Test 2: Sliding Window — Only Last 3 Exchanges")
    print("-" * 65)

    truncated = conversation[-6:]
    truncated.append({"role": "user", "content": test_msg})
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        system=system,
        messages=truncated
    )
    print(f"Question: {test_msg}")
    print(f"Response: {response.content[0].text}")
    print("\nNotice: It lost the name, the budget, the company — all dropped from the window.")

    # Token budget estimation
    print("\n" + "=" * 65)
    print("Experiment: Token Budget")
    print("-" * 65)

    def estimate_tokens(text):
        return len(text) // 4

    messages_text = [m["content"] for m in conversation if m["role"] == "user"]
    total_tokens = sum(estimate_tokens(m) for m in messages_text)

    token_budget = 500
    messages_in_budget = 0
    tokens_used = 0

    for msg in reversed(messages_text):
        msg_tokens = estimate_tokens(msg)
        if tokens_used + msg_tokens <= token_budget:
            messages_in_budget += 1
            tokens_used += msg_tokens
        else:
            break

    print(f"Total estimated tokens: {total_tokens}")
    print(f"With {token_budget} token budget: can keep last {messages_in_budget} messages")

    print("\n" + "=" * 65)
    print("Key Learning: Context window = everything the model sees.")
    print("Too much history = expensive. Too little = amnesia.")
    print("Sliding window: simple but lossy. Summarization (Task 7) is smarter.")
    print("=" * 65)

    print("\nTask 6 Complete!")
    print("Next: python3 demos/anthropic/task7_summarization.py")


if __name__ == "__main__":
    main()
