#!/usr/bin/env python3
"""
Task 1: First Gemini API Call — Google Gemini
Make your first call to Google's Gemini model and inspect the response.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export GOOGLE_API_KEY="your-key-here"   # Free from aistudio.google.com
  pip install google-generativeai
"""

import google.generativeai as genai
import os

# ── Configure the SDK ────────────────────────────────────────────────────────
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# ── Step 1: Create a Generative Model ────────────────────────────────────────
# Gemini is FREE to use via Google AI Studio — perfect for learning!
model = genai.GenerativeModel(___)  # TODO: Use "gemini-2.5-flash"

# ── Step 2: Send your first prompt ───────────────────────────────────────────
prompt = ___  # TODO: Use "Explain Kubernetes pods in 3 sentences for an SRE."

print("=" * 60)
print("TASK 1: First Gemini API Call")
print("=" * 60)
print(f"\nPrompt: {prompt}\n")
print("-" * 60)

response = model.generate_content(prompt)

# ── Step 3: Print the response ───────────────────────────────────────────────
print("Gemini Response:")
print("-" * 60)
print(___)  # TODO: Use response.text
print("-" * 60)

# ── Step 4: Inspect token usage ──────────────────────────────────────────────
print("\nToken Usage:")
print("-" * 60)
usage = response.usage_metadata
print(f"  Prompt tokens:     {___}")  # TODO: Use usage.prompt_token_count
print(f"  Response tokens:   {usage.candidates_token_count}")
print(f"  Total tokens:      {usage.total_token_count}")
print("-" * 60)

# ── Key Learning ─────────────────────────────────────────────────────────────
print("""
KEY LEARNING — Gemini vs Other Providers:
=========================================
  Gemini:   genai.GenerativeModel("gemini-2.5-flash")
            model.generate_content("prompt")
            response.text

  OpenAI:   client.chat.completions.create(model=..., messages=[...])
            response.choices[0].message.content

  Anthropic: client.messages.create(model=..., messages=[...])
            response.content[0].text

  Pattern:  All three follow Create Model/Client -> Send Prompt -> Read Response
  Bonus:    Gemini is FREE via Google AI Studio — best for learning!
""")

print("Next: task2_system_prompts.py — Give Gemini an SRE personality")
print("Task 1 Complete!")
