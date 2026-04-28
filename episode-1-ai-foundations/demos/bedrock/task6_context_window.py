#!/usr/bin/env python3
"""
Task 6: Context Window Management — AWS Bedrock
Learn how to manage long conversations by truncating old messages.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  pip install boto3
  aws configure  (set up AWS credentials)
  Enable Claude model access in AWS Bedrock console
"""

import boto3
import json

def call_bedrock(bedrock, system, messages, max_tokens=128):
    """Helper to call Bedrock and return the assistant text."""
    response = bedrock.invoke_model(
        modelId="anthropic.claude-sonnet-4-6",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages
        })
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


def main():
    print("=" * 65)
    print("Task 6: Context Window Management — AWS Bedrock")
    print("=" * 65)

    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"
    )

    system = "You are a helpful assistant. Be concise in your responses."

    # Build a long conversation — 15 turns
    print("Building a 15-turn conversation...")
    print("-" * 65)

    conversation = []

    for i in range(1, 16):
        msg = f"This is message number {i}. Please acknowledge it."
        conversation.append({"role": "user", "content": msg})
        reply = call_bedrock(bedrock, system, conversation)
        conversation.append({"role": "assistant", "content": reply})
        print(f"Turn {i}: Sent and received")

    print(f"\nTotal messages: {len(conversation)}")

    # Test with full history
    print("\n" + "=" * 65)
    print("Test 1: Full History — Agent Remembers Everything")
    print("-" * 65)

    test_msg = "What was my very first message number?"
    conversation.append({"role": "user", "content": test_msg})
    reply = call_bedrock(bedrock, system, conversation, max_tokens=256)
    print(f"Question: {test_msg}")
    print(f"Response: {reply}")
    conversation.append({"role": "assistant", "content": reply})

    # Sliding window — keep only last 5 exchanges
    print("\n" + "=" * 65)
    print("Test 2: Sliding Window — Only Last 5 Exchanges")
    print("-" * 65)

    truncated = conversation[-10:]
    truncated.append({"role": "user", "content": test_msg})
    reply = call_bedrock(bedrock, system, truncated, max_tokens=256)
    print(f"Question: {test_msg}")
    print(f"Response: {reply}")
    print("\nAgent likely CANNOT answer — first message was truncated.")

    # Token budget estimation
    print("\n" + "=" * 65)
    print("Experiment: Token Budget")
    print("-" * 65)

    def estimate_tokens(text):
        return len(text) // 4

    messages_text = [m["content"] for m in conversation if m["role"] == "user"]
    total_tokens = sum(estimate_tokens(m) for m in messages_text)

    token_budget = 1000
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
    print("Too much history = expensive and slow. Too little = amnesia.")
    print("Sliding window: simple. Token budget: precise.")
    print("=" * 65)

    print("\nTask 6 Complete!")
    print("Next: python3 demos/bedrock/task7_summarization.py")


if __name__ == "__main__":
    main()
