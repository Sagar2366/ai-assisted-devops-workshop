#!/usr/bin/env python3
"""
Task 7: Summarization Memory — Google Gemini
Compress long conversation history into a summary and inject it into a new chat.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export GOOGLE_API_KEY="your-key-here"   # Free from aistudio.google.com
  pip install google-generativeai
"""

import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("=" * 60)
print("TASK 7: Summarization Memory — Compress & Continue")
print("=" * 60)

# ── Step 1: Build a long conversation ────────────────────────────────────────
print("\n--- Phase 1: Build conversation history ---")
print("-" * 60)

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="You are a Kubernetes SRE. Be concise — 2 sentences max."
)

chat = model.start_chat()

conversation_messages = [
    "I'm Priya, SRE at FinTech Corp. We run 200+ microservices on GKE.",
    "Our payment-service keeps OOMKilling. Current limit is 512Mi, usage spikes to 1Gi during peak.",
    "We use Prometheus + Grafana for monitoring, PagerDuty for alerting.",
    "Our deployment strategy is blue-green using Istio service mesh.",
    "The Java-based payment service has a known memory leak in the connection pool.",
    "We tried increasing limits to 1Gi but finance rejected the cost increase.",
]

for msg in conversation_messages:
    response = chat.send_message(msg)
    print(f"  User: {msg[:65]}...")
    print(f"  Gemini: {response.text[:80]}...")
    print()

print(f"History length: {len(chat.history)} entries")
print("-" * 60)

# ── Step 2: Summarize the conversation ───────────────────────────────────────
print("\n--- Phase 2: Summarize the conversation ---")
print("-" * 60)

# Build a transcript from the chat history
transcript = ""
for entry in chat.history:
    transcript += f"{entry.role}: {entry.parts[0].text}\n\n"

summarization_prompt = ___
# TODO: Use "Summarize this SRE conversation into a concise context block. Include: the engineer's name, their infrastructure details, the specific problem, tools they use, what has been tried, and any constraints. Format as bullet points.\n\nConversation:\n" + transcript

summary_model = genai.GenerativeModel("gemini-2.5-flash")
summary_response = summary_model.generate_content(summarization_prompt)
summary = summary_response.text

print("Generated Summary:")
print(summary)
print("-" * 60)

# ── Step 3: Start a NEW chat with the summary as context ────────────────────
print("\n--- Phase 3: New chat with summary in system_instruction ---")
print("-" * 60)

summarized_instruction = ___
# TODO: Use f"You are a senior Kubernetes SRE. Here is the context from a previous conversation with this engineer:\n\n{summary}\n\nContinue helping them based on this context. Be concise and actionable."

model_with_memory = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=summarized_instruction
)

chat_new = model_with_memory.start_chat()

# Test that the new chat remembers key details
test_questions = [
    "What was my name and company again?",
    "Given the budget constraints, what free solutions can fix the memory leak?",
]

for question in test_questions:
    response = chat_new.send_message(question)
    print(f"  User: {question}")
    print(f"  Gemini: {response.text}")
    print()

print("-" * 60)

# ── Compare Token Usage ─────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TOKEN COMPARISON")
print("=" * 60)
print(f"  Original history entries:  {len(chat.history)}")
print(f"  Summary length:            {len(summary)} chars")
print(f"  New chat history entries:  {len(chat_new.history)}")
print()
full_chars = sum(len(e.parts[0].text) for e in chat.history)
print(f"  Full conversation chars:   {full_chars}")
print(f"  Summary chars:             {len(summary)}")
print(f"  Compression ratio:         {len(summary)/full_chars:.1%}")

# ── Key Learning ─────────────────────────────────────────────────────────────
print("""
KEY LEARNING — Summarization Memory Across Providers:
======================================================
  Gemini:    Summarize with generate_content(), then inject summary into
             system_instruction of a new GenerativeModel.

  OpenAI:    Summarize with chat.completions.create(), then prepend summary
             as a system message in the new messages list.

  Anthropic: Summarize with messages.create(), then add summary to the
             system= parameter of the next call.

  Pattern:   Summarize old context -> Inject into new conversation.
  Trade-off: Lossy compression — some details may be lost, but huge token savings.
  Bonus:     Gemini is FREE — the summarization call itself costs nothing!
""")

print("Next: task8_personalization.py — Build a user profile from conversation")
print("Task 7 Complete!")
