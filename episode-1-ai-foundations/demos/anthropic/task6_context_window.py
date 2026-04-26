#!/usr/bin/env python3
"""
Task 6: Context Window Management
Learn how to manage long conversations by truncating old messages.
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
    system = "You are a helpful assistant. Be concise in your responses."

    # Build a long conversation — 15 turns
    print("Building a 15-turn conversation...")
    print("-" * 65)

    conversation = []

    for i in range(1, 16):
        msg = f"This is message number {i}. Please acknowledge it."
        conversation.append({"role": "user", "content": msg})

        response = client.messages.create(
            model="claude-sonnet-4-6-latest",
            max_tokens=128,
            system=system,
            messages=conversation
        )
        reply = response.content[0].text
        conversation.append({"role": "assistant", "content": reply})
        print(f"Turn {i}: Sent and received")

    print(f"\nTotal messages: {len(conversation)}")

    # Test with FULL history — agent remembers everything
    print("\n" + "=" * 65)
    print("Test 1: Full History — Agent Remembers Everything")
    print("-" * 65)

    test_msg = "What was my very first message number?"
    conversation.append({"role": "user", "content": test_msg})
    response = client.messages.create(
        model="claude-sonnet-4-6-latest",
        max_tokens=256,
        system=system,
        messages=conversation
    )
    print(f"Question: {test_msg}")
    print(f"Response: {response.content[0].text}")
    conversation.append({"role": "assistant", "content": response.content[0].text})

    # Sliding window — keep only last 5 exchanges
    print("\n" + "=" * 65)
    print("Test 2: Sliding Window — Only Last 5 Exchanges")
    print("-" * 65)

    # TODO 1: Implement sliding window truncation
    # Keep only the last 10 messages (5 user + 5 assistant pairs)
    truncated = conversation[___:]  # TODO: Use -10

    truncated.append({"role": "user", "content": test_msg})
    response = client.messages.create(
        model="claude-sonnet-4-6-latest",
        max_tokens=256,
        system=system,
        messages=___  # TODO: Use truncated
    )
    print(f"Question: {test_msg}")
    print(f"Response: {response.content[0].text}")
    print("\nAgent likely CANNOT answer — first message was truncated.")

    # Token budget estimation
    print("\n" + "=" * 65)
    print("Experiment: Token Budget")
    print("-" * 65)

    def estimate_tokens(text):
        return len(text) // 4

    messages_text = [m["content"] for m in conversation if m["role"] == "user"]
    total_tokens = sum(estimate_tokens(m) for m in messages_text)

    # TODO 2: Calculate how many messages fit in a 1000-token budget
    token_budget = 1000
    messages_in_budget = 0
    tokens_used = 0

    for msg in reversed(messages_text):
        msg_tokens = estimate_tokens(msg)
        if tokens_used + msg_tokens <= ___:  # TODO: Use token_budget
            messages_in_budget += 1
            tokens_used += msg_tokens
        else:
            break

    print(f"Total estimated tokens: {total_tokens}")
    print(f"With {token_budget} token budget: can keep last {messages_in_budget} messages")

    print("\n" + "=" * 65)
    print("Key Learning: Context window = everything the model sees.")
    print("Too much history = expensive and slow. Too little = amnesia.")
    print("Sliding window: simple. Token budget: precise.")
    print("=" * 65)

    print("\nTask 6 Complete!")
    print("Next: python3 demos/anthropic/task7_summarization.py")


if __name__ == "__main__":
    main()
