#!/usr/bin/env python3
"""
Task 5: Conversation History — Google Gemini
Multi-turn conversation using chat sessions. Watch Gemini remember context.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export GOOGLE_API_KEY="your-key-here"   # Free from aistudio.google.com
  pip install google-generativeai
"""

import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def main():
    print("=" * 65)
    print("Task 5: Conversation History — Google Gemini")
    print("=" * 65)

    model = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction="You are a senior Kubernetes SRE. Give concise, practical answers."
    )

    chat = model.start_chat()

    print(f"\nChat started. History length: {len(chat.history)}")

    # Turn 1: Introduce the problem
    print("\n--- Turn 1: The Problem ---")
    print("-" * 65)
    message1 = "Our payment-service pod keeps getting OOMKilled in production. Memory limit is 512Mi. It restarts about 3 times every 10 minutes."

    response1 = chat.send_message(message1)
    print(f"User: {message1}")
    print(f"\nGemini: {response1.text}")
    print(f"\nHistory length after Turn 1: {len(chat.history)}")

    # Turn 2: Follow-up
    print("\n--- Turn 2: Follow-up ---")
    print("-" * 65)
    message2 = "What kubectl commands should I run first to diagnose this?"

    response2 = chat.send_message(message2)
    print(f"User: {message2}")
    print(f"\nGemini: {response2.text}")
    print(f"\nHistory length after Turn 2: {len(chat.history)}")

    # Turn 3: Deeper dive
    print("\n--- Turn 3: Deeper dive ---")
    print("-" * 65)
    message3 = "Based on your suggestions, I found the container is using 480Mi at idle. What should I set the new limits to?"

    response3 = chat.send_message(message3)
    print(f"User: {message3}")
    print(f"\nGemini: {response3.text}")
    print(f"\nHistory length after Turn 3: {len(chat.history)}")

    # Inspect the full history
    print("\n" + "=" * 65)
    print("FULL CONVERSATION HISTORY")
    print("=" * 65)
    for i, entry in enumerate(chat.history):
        role = entry.role.upper()
        text_preview = entry.parts[0].text[:100] + "..." if len(entry.parts[0].text) > 100 else entry.parts[0].text
        print(f"  [{i}] {role}: {text_preview}")

    print("\n" + "=" * 65)
    print("Key Learning: Gemini auto-manages history via chat sessions.")
    print("OpenAI/Anthropic require you to manage the messages list manually.")
    print("=" * 65)

    print("\nTask 5 Complete!")
    print("Next: python3 demos/google/task6_context_window.py")


if __name__ == "__main__":
    main()
