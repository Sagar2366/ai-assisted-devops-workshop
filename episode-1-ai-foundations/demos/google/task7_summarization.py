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

def main():
    print("=" * 65)
    print("Task 7: Summarization Memory — Google Gemini")
    print("=" * 65)

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

    print("\n--- Phase 1: Build conversation history ---")
    print("-" * 65)
    for msg in conversation_messages:
        response = chat.send_message(msg)
        print(f"  User: {msg[:65]}...")
        print(f"  Gemini: {response.text[:80]}...")
        print()

    print(f"History length: {len(chat.history)} entries")

    # Summarize
    print("\n--- Phase 2: Summarize the conversation ---")
    print("-" * 65)

    transcript = ""
    for entry in chat.history:
        transcript += f"{entry.role}: {entry.parts[0].text}\n\n"

    summarization_prompt = "Summarize this SRE conversation into a concise context block. Include: the engineer's name, their infrastructure details, the specific problem, tools they use, what has been tried, and any constraints. Format as bullet points.\n\nConversation:\n" + transcript

    summary_model = genai.GenerativeModel("gemini-2.5-flash")
    summary_response = summary_model.generate_content(summarization_prompt)
    summary = summary_response.text

    print("Generated Summary:")
    print(summary)

    # New chat with summary
    print("\n--- Phase 3: New chat with summary in system_instruction ---")
    print("-" * 65)

    summarized_instruction = f"You are a senior Kubernetes SRE. Here is the context from a previous conversation with this engineer:\n\n{summary}\n\nContinue helping them based on this context. Be concise and actionable."

    model_with_memory = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction=summarized_instruction
    )

    chat_new = model_with_memory.start_chat()

    test_questions = [
        "What was my name and company again?",
        "Given the budget constraints, what free solutions can fix the memory leak?",
    ]

    for question in test_questions:
        response = chat_new.send_message(question)
        print(f"  User: {question}")
        print(f"  Gemini: {response.text}")
        print()

    # Compare token usage
    print("=" * 65)
    print("TOKEN COMPARISON")
    print("=" * 65)
    full_chars = sum(len(e.parts[0].text) for e in chat.history)
    print(f"  Full conversation chars:   {full_chars}")
    print(f"  Summary chars:             {len(summary)}")
    print(f"  Compression ratio:         {len(summary)/full_chars:.1%}")

    print("\n" + "=" * 65)
    print("Key Learning: Summarize old context -> inject into system_instruction.")
    print("Huge token savings while retaining key facts.")
    print("=" * 65)

    print("\nTask 7 Complete!")
    print("Next: python3 demos/google/task8_personalization.py")


if __name__ == "__main__":
    main()
