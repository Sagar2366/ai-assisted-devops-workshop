#!/usr/bin/env python3
"""
Task 5: Conversation History — Multi-Turn K8s Troubleshooting
Build a multi-turn conversation where the AI remembers previous context.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic

def main():
    print("=" * 65)
    print("Task 5: Conversation History — Anthropic Claude")
    print("=" * 65)

    client = anthropic.Anthropic()
    system = "You are a senior SRE assistant. Remember details from the conversation."

    conversation = []

    # Turn 1: Describe the OOM problem
    print("\nTurn 1: Describe the Problem")
    print("-" * 65)
    message_1 = "I'm seeing OOM kills on my api-server pod in production. Memory limit is 256Mi, usage hits 255Mi."

    conversation.append({"role": "user", "content": message_1})
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        system=system,
        messages=conversation
    )
    assistant_reply = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_reply})

    print(f"User: {message_1}")
    print(f"Agent: {assistant_reply}")

    # Turn 2: Ask about logs
    print("\nTurn 2: Ask About Logs")
    print("-" * 65)
    message_2 = "What should I look for in the logs to find the root cause?"

    conversation.append({"role": "user", "content": message_2})
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        system=system,
        messages=conversation
    )
    assistant_reply = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_reply})

    print(f"User: {message_2}")
    print(f"Agent: {assistant_reply}")

    # Turn 3: Ask for kubectl commands to fix it
    print("\nTurn 3: Ask for the Fix")
    print("-" * 65)
    message_3 = "Give me the kubectl commands to fix this."

    conversation.append({"role": "user", "content": message_3})
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        system=system,
        messages=conversation
    )
    assistant_reply = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_reply})

    print(f"User: {message_3}")
    print(f"Agent: {assistant_reply}")

    print(f"\nTotal messages in history: {len(conversation)}")

    print("\n" + "=" * 65)
    print("Key Learning: Anthropic has NO built-in memory.")
    print("YOU maintain the conversation list. Each API call sends")
    print("the FULL history. The model sees everything you include.")
    print("=" * 65)

    print("\nTask 5 Complete!")
    print("Next: python3 demos/anthropic/task6_context_window.py")


if __name__ == "__main__":
    main()
