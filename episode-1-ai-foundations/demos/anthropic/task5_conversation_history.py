#!/usr/bin/env python3
"""
Task 5: Conversation History — Multi-Turn Conversations
Learn how to maintain context across multiple turns with Anthropic Claude.
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
    system = "You are a friendly customer support agent. Remember details that customers share with you."

    # In Anthropic, conversation history is a list of messages you maintain yourself.
    # Each turn you append the user message and the assistant response.

    # TODO 1: Initialize the conversation history
    # This is just a Python list that holds all messages
    conversation = ___  # TODO: Use []

    print("Step 1 Complete: Conversation history initialized\n")

    # Turn 1: Customer introduces themselves (PRE-FILLED — shows the pattern)
    print("Turn 1: Customer Introduction")
    message_1 = "Hi, my name is Sarah and I'm having trouble with my account"

    conversation.append({"role": "user", "content": message_1})

    response = client.messages.create(
        model="claude-sonnet-4-6-latest",
        max_tokens=512,
        system=system,
        messages=conversation
    )
    assistant_reply = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_reply})

    print(f"User: {message_1}")
    print(f"Agent: {assistant_reply}")

    # Turn 2: Follow-up question
    print("\nTurn 2: Follow-up Question")
    message_2 = "Can you tell me what name I just gave you?"

    # TODO 2: Append the user message and call the API with full history
    conversation.append({"role": "user", "content": ___})  # TODO: Use message_2

    response = client.messages.create(
        model="claude-sonnet-4-6-latest",
        max_tokens=512,
        system=system,
        messages=___  # TODO: Use conversation
    )
    assistant_reply = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_reply})

    print(f"User: {message_2}")
    print(f"Agent: {assistant_reply}")

    # Turn 3: Another follow-up
    print("\nTurn 3: Another Follow-up")
    message_3 = "What was my issue again?"

    # TODO 3: Complete the third turn
    conversation.append({"role": "user", "content": ___})  # TODO: Use message_3

    response = client.messages.create(
        model="claude-sonnet-4-6-latest",
        max_tokens=512,
        system=___,  # TODO: Use system
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
