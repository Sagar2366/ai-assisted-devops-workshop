#!/usr/bin/env python3
"""
Task 7: Conversation Summarization — Anthropic Claude
Compress old SRE conversation history while preserving key context.
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

    print("Building SRE conversation with user details...")
    print("-" * 65)

    system = "You are a senior SRE assistant that remembers conversation details."
    conversation = []
    conversation_log = []

    topics = [
        "My name is Sagar and I'm an SRE at Acme Corp",
        "We run EKS with 50 microservices in production",
        "I'm looking into AI tools for incident response",
        "The payment-service pod keeps OOMing after deploys",
        "Memory limit is 256Mi but usage peaks at 255Mi",
        "We use ArgoCD for deployments and Prometheus for monitoring",
        "Our budget for AI tooling is $500 per month",
        "Team of 5 SREs covering 3 time zones",
        "We need automated triage to reduce MTTR",
        "Biggest pain point is getting paged at 3 AM for the same OOM issue"
    ]

    for i, topic in enumerate(topics, 1):
        conversation.append({"role": "user", "content": topic})
        response = client.messages.create(
            model="claude-opus-4-7", max_tokens=256,
            system=system, messages=conversation
        )
        reply = response.content[0].text
        conversation.append({"role": "assistant", "content": reply})
        conversation_log.append({"user": topic, "assistant": reply})
        print(f"Turn {i}: {topic[:50]}...")

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

    summary_prompt = f"""Summarize this conversation in 2-3 sentences.
Preserve: names, tools/platforms mentioned, specific problems, constraints (budget, team size), and any decisions made.

Conversation:
{old_text}

Create a concise summary:"""

    summary_response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=256,
        messages=[{"role": "user", "content": summary_prompt}]
    )
    summary_text = summary_response.content[0].text
    print(f"Summary: {summary_text}")

    # New conversation with summary
    print("\n" + "=" * 65)
    print("Testing: Summary in System Prompt vs No Summary")
    print("=" * 65)

    summary_system = f"""{system}

Here is context from a previous conversation:
{summary_text}

Use this context to personalize your responses."""

    new_conversation = []
    for ex in recent_exchanges:
        new_conversation.append({"role": "user", "content": ex["user"]})
        r = client.messages.create(
            model="claude-opus-4-7", max_tokens=256,
            system=summary_system, messages=new_conversation
        )
        new_conversation.append({"role": "assistant", "content": r.content[0].text})

    test_questions = ["What's my name and company?", "What tools do we use for deployments?", "What's our monthly budget?"]

    print("\nWith Summary (in system prompt):")
    for q in test_questions:
        new_conversation.append({"role": "user", "content": q})
        r = client.messages.create(
            model="claude-opus-4-7", max_tokens=128,
            system=summary_system, messages=new_conversation
        )
        new_conversation.append({"role": "assistant", "content": r.content[0].text})
        print(f"  Q: {q} -> A: {r.content[0].text[:80]}")

    print("\nWithout Summary (recent only):")
    recent_only = []
    for ex in recent_exchanges:
        recent_only.append({"role": "user", "content": ex["user"]})
        r = client.messages.create(
            model="claude-opus-4-7", max_tokens=256,
            system=system, messages=recent_only
        )
        recent_only.append({"role": "assistant", "content": r.content[0].text})

    for q in test_questions:
        recent_only.append({"role": "user", "content": q})
        r = client.messages.create(
            model="claude-opus-4-7", max_tokens=128,
            system=system, messages=recent_only
        )
        recent_only.append({"role": "assistant", "content": r.content[0].text})
        print(f"  Q: {q} -> A: {r.content[0].text[:80]}")

    print("\n" + "=" * 65)
    print("Key Learning: Summarization compresses history while keeping key facts.")
    print("Pattern: summarize old -> inject into system prompt -> fresh conversation retains context")
    print("=" * 65)

    print("\nTask 7 Complete!")
    print("Next: python3 demos/anthropic/task8_personalization.py")


if __name__ == "__main__":
    main()
