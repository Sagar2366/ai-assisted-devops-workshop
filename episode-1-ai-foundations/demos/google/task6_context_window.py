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
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def main():
    print("=" * 65)
    print("Task 6: Context Window — Sliding Window Strategy")
    print("=" * 65)

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
    print("\n--- Phase 1: Build a long conversation ---")
    print("-" * 65)

    chat_full = model.start_chat()
    for msg in messages:
        response = chat_full.send_message(msg)
        print(f"  User: {msg[:60]}...")
        print(f"  Gemini: {response.text[:80]}...")
        print()

    print(f"Full history length: {len(chat_full.history)} entries")

    # Test full context recall
    print("\n--- Phase 2: Full context recall ---")
    print("-" * 65)

    response_full = chat_full.send_message("What is my name and what monitoring stack do I use?")
    print(f"Full context response: {response_full.text}")

    # Sliding window — keep only last 4 entries
    print("\n--- Phase 3: Sliding window (memory loss demo) ---")
    print("-" * 65)

    WINDOW_SIZE = 4
    recent_history = chat_full.history[-WINDOW_SIZE:]

    print(f"Original history: {len(chat_full.history)} entries")
    print(f"Window size:      {WINDOW_SIZE} entries")
    print(f"Kept entries:     {len(recent_history)} entries\n")

    print("Entries in the sliding window:")
    for i, entry in enumerate(recent_history):
        preview = entry.parts[0].text[:70] + "..." if len(entry.parts[0].text) > 70 else entry.parts[0].text
        print(f"  [{i}] {entry.role.upper()}: {preview}")

    # Create a new chat with only the windowed history
    chat_windowed = model.start_chat(history=recent_history)
    response_windowed = chat_windowed.send_message("What is my name and what monitoring stack do I use?")
    print(f"\nWindowed response: {response_windowed.text}")

    # Compare
    print("\n" + "=" * 65)
    print("COMPARISON: Full Context vs Sliding Window")
    print("=" * 65)
    print(f"  Full context:    {response_full.text[:120]}...")
    print(f"  Sliding window:  {response_windowed.text[:120]}...")
    print("\n  Notice: The sliding window LOST early context (name, monitoring stack)!")

    print("\n" + "=" * 65)
    print("Key Learning: Smaller window = cheaper, but risks losing critical context.")
    print("Summarization (Task 7) is a smarter strategy.")
    print("=" * 65)

    print("\nTask 6 Complete!")
    print("Next: python3 demos/google/task7_summarization.py")


if __name__ == "__main__":
    main()
