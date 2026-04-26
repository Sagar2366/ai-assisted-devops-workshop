#!/usr/bin/env python3
"""
Task 7: Conversation Summarization
Compress old conversation history while preserving key information.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic

def main():
    print("=" * 65)
    print("Task 7: Conversation Summarization — Anthropic Claude")
    print("=" * 65)

    client = anthropic.Anthropic()

    # Build a 10-turn conversation with user details (PRE-FILLED)
    print("Building conversation with user details...")
    print("-" * 65)

    system = "You are a helpful assistant that remembers conversation details."
    conversation = []
    conversation_log = []

    topics = [
        "My name is Alex and I'm a software engineer",
        "I work primarily with Python and JavaScript",
        "I'm interested in learning about AI agents",
        "My current project involves building a chatbot",
        "The chatbot needs to remember user preferences",
        "I also need it to handle long conversations",
        "Cost optimization is important for my use case",
        "I have a budget constraint of $100/month",
        "The chatbot will serve about 1000 users",
        "Each user might have 10-20 message conversations"
    ]

    for i, topic in enumerate(topics, 1):
        conversation.append({"role": "user", "content": topic})
        response = client.messages.create(
            model="claude-sonnet-4-6-latest", max_tokens=256,
            system=system, messages=conversation
        )
        reply = response.content[0].text
        conversation.append({"role": "assistant", "content": reply})
        conversation_log.append({"user": topic, "assistant": reply})
        print(f"Turn {i}: {topic[:50]}...")

    # Split: old (first 7) vs recent (last 3)
    old_exchanges = conversation_log[:7]
    recent_exchanges = conversation_log[7:]

    print(f"\nOld exchanges to summarize: {len(old_exchanges)}")
    print(f"Recent exchanges to keep: {len(recent_exchanges)}")

    # Summarize old exchanges
    print("\n" + "=" * 65)
    print("Summarizing Old Messages")
    print("-" * 65)

    old_text = ""
    for ex in old_exchanges:
        old_text += f"User: {ex['user']}\nAssistant: {ex['assistant']}\n\n"

    # TODO 1: Ask Claude to summarize the old conversation
    summary_prompt = f"""Summarize this conversation. Extract key information:
- User's name
- Technical skills
- Goals and constraints

Conversation:
{old_text}

Create a concise summary (2-3 sentences):"""

    summary_response = client.messages.create(
        model="claude-sonnet-4-6-latest",
        max_tokens=256,
        messages=[{"role": "user", "content": ___}]  # TODO: Use summary_prompt
    )
    summary_text = ___.content[0].text  # TODO: Use summary_response

    print(f"Summary: {summary_text}")

    # Create new conversation with summary + recent context
    print("\n" + "=" * 65)
    print("Testing: Summary + Recent vs Recent Only")
    print("=" * 65)

    # TODO 2: Build new conversation starting with summary as context
    new_conversation = []
    context_message = f"Previous conversation summary about the user: {summary_text}"
    new_conversation.append({"role": "user", "content": ___})  # TODO: Use context_message
    ack = client.messages.create(
        model="claude-sonnet-4-6-latest", max_tokens=64,
        system=system, messages=new_conversation
    )
    new_conversation.append({"role": "assistant", "content": ack.content[0].text})

    # Replay recent exchanges
    for ex in recent_exchanges:
        new_conversation.append({"role": "user", "content": ex["user"]})
        r = client.messages.create(
            model="claude-sonnet-4-6-latest", max_tokens=256,
            system=system, messages=new_conversation
        )
        new_conversation.append({"role": "assistant", "content": r.content[0].text})

    # Test: ask about OLD info
    test_questions = ["What's my name?", "What programming languages do I use?", "What's my monthly budget?"]

    print("\nWith Summary:")
    for q in test_questions:
        new_conversation.append({"role": "user", "content": q})
        r = client.messages.create(
            model="claude-sonnet-4-6-latest", max_tokens=128,
            system=system, messages=new_conversation
        )
        new_conversation.append({"role": "assistant", "content": r.content[0].text})
        print(f"  Q: {q} → A: {r.content[0].text[:80]}")

    # Without summary — only recent
    print("\nWithout Summary (recent only):")
    recent_only = []
    for ex in recent_exchanges:
        recent_only.append({"role": "user", "content": ex["user"]})
        r = client.messages.create(
            model="claude-sonnet-4-6-latest", max_tokens=256,
            system=system, messages=recent_only
        )
        recent_only.append({"role": "assistant", "content": r.content[0].text})

    for q in test_questions:
        recent_only.append({"role": "user", "content": q})
        r = client.messages.create(
            model="claude-sonnet-4-6-latest", max_tokens=128,
            system=system, messages=recent_only
        )
        recent_only.append({"role": "assistant", "content": r.content[0].text})
        print(f"  Q: {q} → A: {r.content[0].text[:80]}")

    print("\n" + "=" * 65)
    print("Key Learning: Summarization compresses history while keeping key facts.")
    print("Pattern: summarize old → start fresh thread → inject summary → replay recent")
    print("=" * 65)

    print("\nTask 7 Complete!")
    print("Next: python3 demos/anthropic/task8_personalization.py")


if __name__ == "__main__":
    main()
