#!/usr/bin/env python3
"""
Task 7: Conversation Summarization — AWS Bedrock
Compress old conversation history while preserving key information.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  pip install boto3
  aws configure  (set up AWS credentials)
  Enable Claude model access in AWS Bedrock console
"""

import boto3
import json

def call_bedrock(bedrock, system, messages, max_tokens=256):
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
    print("Task 7: Conversation Summarization — AWS Bedrock")
    print("=" * 65)

    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"
    )

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
        reply = call_bedrock(bedrock, system, conversation)
        conversation.append({"role": "assistant", "content": reply})
        conversation_log.append({"user": topic, "assistant": reply})
        print(f"Turn {i}: {topic[:50]}...")

    old_exchanges = conversation_log[:7]
    recent_exchanges = conversation_log[7:]

    # Summarize old exchanges
    print("\n" + "=" * 65)
    print("Summarizing Old Messages")
    print("-" * 65)

    old_text = ""
    for ex in old_exchanges:
        old_text += f"User: {ex['user']}\nAssistant: {ex['assistant']}\n\n"

    summary_prompt = f"""Summarize this conversation. Extract key information:
- User's name
- Technical skills
- Goals and constraints

Conversation:
{old_text}

Create a concise summary (2-3 sentences):"""

    response = bedrock.invoke_model(
        modelId="anthropic.claude-sonnet-4-6",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 256,
            "messages": [{"role": "user", "content": summary_prompt}]
        })
    )
    summary_result = json.loads(response["body"].read())
    summary_text = summary_result["content"][0]["text"]

    print(f"Summary: {summary_text}")

    # New conversation with summary
    print("\n" + "=" * 65)
    print("Testing: Summary + Recent vs Recent Only")
    print("=" * 65)

    new_conversation = []
    context_message = f"Previous conversation summary about the user: {summary_text}"
    new_conversation.append({"role": "user", "content": context_message})
    ack = call_bedrock(bedrock, system, new_conversation, max_tokens=64)
    new_conversation.append({"role": "assistant", "content": ack})

    for ex in recent_exchanges:
        new_conversation.append({"role": "user", "content": ex["user"]})
        reply = call_bedrock(bedrock, system, new_conversation)
        new_conversation.append({"role": "assistant", "content": reply})

    test_questions = ["What's my name?", "What programming languages do I use?", "What's my monthly budget?"]

    print("\nWith Summary:")
    for q in test_questions:
        new_conversation.append({"role": "user", "content": q})
        reply = call_bedrock(bedrock, system, new_conversation, max_tokens=128)
        new_conversation.append({"role": "assistant", "content": reply})
        print(f"  Q: {q} -> A: {reply[:80]}")

    print("\nWithout Summary (recent only):")
    recent_only = []
    for ex in recent_exchanges:
        recent_only.append({"role": "user", "content": ex["user"]})
        reply = call_bedrock(bedrock, system, recent_only)
        recent_only.append({"role": "assistant", "content": reply})

    for q in test_questions:
        recent_only.append({"role": "user", "content": q})
        reply = call_bedrock(bedrock, system, recent_only, max_tokens=128)
        recent_only.append({"role": "assistant", "content": reply})
        print(f"  Q: {q} -> A: {reply[:80]}")

    print("\n" + "=" * 65)
    print("Key Learning: Summarization compresses history while keeping key facts.")
    print("Pattern: summarize old -> start fresh -> inject summary -> replay recent")
    print("=" * 65)

    print("\nTask 7 Complete!")
    print("Next: python3 demos/bedrock/task8_personalization.py")


if __name__ == "__main__":
    main()
