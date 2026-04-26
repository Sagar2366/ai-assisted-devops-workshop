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

print("=" * 60)
print("TASK 5: Conversation History — Multi-Turn Chat")
print("=" * 60)

# ── Step 1: Create a model with SRE system instruction ──────────────────────
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="You are a senior Kubernetes SRE. Give concise, practical answers."
)

# ── Step 2: Start a chat session ─────────────────────────────────────────────
chat = ___  # TODO: Use model.start_chat()

print(f"\nChat started. History length: {len(chat.history)}")
print("-" * 60)

# ── Turn 1: Introduce the problem ───────────────────────────────────────────
print("\n--- Turn 1: The Problem ---")
message1 = ___  # TODO: Use "Our payment-service pod keeps getting OOMKilled in production. Memory limit is 512Mi. It restarts about 3 times every 10 minutes."

response1 = chat.send_message(message1)
print(f"User: {message1}")
print(f"\nGemini: {response1.text}")
print(f"\nHistory length after Turn 1: {len(chat.history)}")
print("-" * 60)

# ── Turn 2: Follow-up (Gemini should remember the context) ──────────────────
print("\n--- Turn 2: Follow-up (tests context memory) ---")
message2 = "What kubectl commands should I run first to diagnose this?"

response2 = ___  # TODO: Use chat.send_message(message2)
print(f"User: {message2}")
print(f"\nGemini: {response2.text}")
print(f"\nHistory length after Turn 2: {len(chat.history)}")
print("-" * 60)

# ── Turn 3: Build on previous context ───────────────────────────────────────
print("\n--- Turn 3: Deeper dive (tests accumulated context) ---")
message3 = "Based on your suggestions, I found the container is using 480Mi at idle. What should I set the new limits to?"

response3 = chat.send_message(message3)
print(f"User: {message3}")
print(f"\nGemini: {response3.text}")
print(f"\nHistory length after Turn 3: {len(chat.history)}")
print("-" * 60)

# ── Inspect the Full History ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("FULL CONVERSATION HISTORY")
print("=" * 60)
for i, entry in enumerate(chat.history):
    role = entry.role.upper()
    text_preview = entry.parts[0].text[:100] + "..." if len(entry.parts[0].text) > 100 else entry.parts[0].text
    print(f"  [{i}] {role}: {text_preview}")
print("-" * 60)

# ── Key Learning ─────────────────────────────────────────────────────────────
print("""
KEY LEARNING — Conversation History Across Providers:
======================================================
  Gemini:    chat = model.start_chat()
             chat.send_message("...")
             chat.history — auto-maintained by the SDK!

  OpenAI:    YOU manually manage the messages list:
             messages.append({{"role": "user", "content": "..."}})
             messages.append({{"role": "assistant", "content": response}})

  Anthropic: Same as OpenAI — YOU manage the messages list manually.

  Key Diff:  Gemini auto-manages history. OpenAI/Anthropic require manual tracking.
  Pattern:   Every message grows the context window — tokens add up fast!
  Bonus:     Gemini is FREE — experiment with long conversations at zero cost!
""")

print("Next: task6_context_window.py — What happens when memory gets too long?")
print("Task 5 Complete!")
