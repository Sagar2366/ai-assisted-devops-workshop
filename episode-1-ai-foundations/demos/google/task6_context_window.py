#!/usr/bin/env python3
"""
Task 6: Context Window & Sliding Window — Google Gemini
Demonstrate context limits with a sliding window strategy using chat history.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export GOOGLE_API_KEY="your-key-here"   # Free from aistudio.google.com
  pip install google-generativeai
"""

import google.generativeai as genai
from google.generativeai.types import content_types
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("=" * 60)
print("TASK 6: Context Window — Sliding Window Strategy")
print("=" * 60)

# ── Step 1: Build a long conversation ────────────────────────────────────────
print("\n--- Phase 1: Build a long conversation ---")
print("-" * 60)

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="You are a Kubernetes SRE. Be very concise — 2 sentences max per answer."
)

messages = [
    "My name is Alex and I manage a 50-node Kubernetes cluster running e-commerce workloads.",
    "We just had an OOMKill on payment-service. Memory limit is 512Mi.",
    "The HPA is set to scale at 70% CPU but memory is the bottleneck.",
    "We use Prometheus and Grafana for monitoring. Alert manager sends to Slack.",
    "Our CI/CD pipeline is ArgoCD with GitHub Actions for builds.",
    "Database is PostgreSQL on CloudSQL, connected via Cloud SQL Proxy sidecar.",
    "We want to implement pod disruption budgets for zero-downtime deployments.",
]

# Build the full conversation
chat_full = model.start_chat()
for msg in messages:
    response = chat_full.send_message(msg)
    print(f"  User: {msg[:60]}...")
    print(f"  Gemini: {response.text[:80]}...")
    print()

print(f"Full history length: {len(chat_full.history)} entries")
print("-" * 60)

# ── Step 2: Test full context recall ─────────────────────────────────────────
print("\n--- Phase 2: Full context recall ---")
print("-" * 60)

response_full = chat_full.send_message("What is my name and what monitoring stack do I use?")
print(f"Full context response: {response_full.text}")
print("-" * 60)

# ── Step 3: Sliding window — keep only last N exchanges ─────────────────────
print("\n--- Phase 3: Sliding window (memory loss demo) ---")
print("-" * 60)

WINDOW_SIZE = ___  # TODO: Use 4 (keep only last 4 history entries = 2 exchanges)

# Slice the history to keep only the last N entries
recent_history = ___  # TODO: Use chat_full.history[-WINDOW_SIZE:]

print(f"Original history: {len(chat_full.history)} entries")
print(f"Window size:      {WINDOW_SIZE} entries")
print(f"Kept entries:     {len(recent_history)} entries")
print()

# Show what we kept
print("Entries in the sliding window:")
for i, entry in enumerate(recent_history):
    preview = entry.parts[0].text[:70] + "..." if len(entry.parts[0].text) > 70 else entry.parts[0].text
    print(f"  [{i}] {entry.role.upper()}: {preview}")
print()

# Create a new chat with only the windowed history
chat_windowed = model.start_chat(history=recent_history)

response_windowed = chat_windowed.send_message("What is my name and what monitoring stack do I use?")
print(f"Windowed response: {response_windowed.text}")
print("-" * 60)

# ── Compare ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("COMPARISON: Full Context vs Sliding Window")
print("=" * 60)
print(f"  Full context answer:    {response_full.text[:120]}...")
print(f"  Sliding window answer:  {response_windowed.text[:120]}...")
print()
print("  Notice: The sliding window LOST early context (name, monitoring stack)!")
print("  This is the fundamental trade-off: tokens saved vs context lost.")

# ── Key Learning ─────────────────────────────────────────────────────────────
print("""
KEY LEARNING — Sliding Window Across Providers:
=================================================
  Gemini:    model.start_chat(history=recent_history)
             Pass sliced history to a new chat session.

  OpenAI:    messages = messages[-WINDOW:]
             Just slice the messages list before sending.

  Anthropic: Same as OpenAI — slice the messages list.

  Pattern:   All providers need the same strategy — only the syntax differs.
  Trade-off: Smaller window = cheaper + faster, but risks losing critical context.
  Bonus:     Gemini is FREE — test different window sizes without cost concerns!
""")

print("Next: task7_summarization.py — Smarter memory with conversation summaries")
print("Task 6 Complete!")
