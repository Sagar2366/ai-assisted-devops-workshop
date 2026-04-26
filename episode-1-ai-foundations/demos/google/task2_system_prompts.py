#!/usr/bin/env python3
"""
Task 2: System Prompts — Google Gemini
See how system_instruction transforms Gemini from a generic chatbot into an SRE expert.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export GOOGLE_API_KEY="your-key-here"   # Free from aistudio.google.com
  pip install google-generativeai
"""

import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# ── The Alert ────────────────────────────────────────────────────────────────
alert = ___  # TODO: Use the multi-line string below
# """ALERT: OOMKilled
# Pod: payment-service-7d4b8c6f5-x2vnm
# Namespace: production
# Container: payment-api
# Memory Limit: 512Mi
# Last Restart: 3 times in 10 minutes
# Timestamp: 2024-01-15T03:42:18Z"""

print("=" * 60)
print("TASK 2: System Prompts — Before vs After")
print("=" * 60)

# ── Test 1: WITHOUT system instruction (generic response) ────────────────────
print("\n--- Test 1: WITHOUT system_instruction ---")
print("-" * 60)

model_generic = genai.GenerativeModel("gemini-2.5-flash")
response_generic = model_generic.generate_content(f"Analyze this alert:\n{alert}")
print(response_generic.text)
print("-" * 60)

# ── Test 2: WITH system instruction (SRE expert response) ────────────────────
print("\n--- Test 2: WITH system_instruction ---")
print("-" * 60)

sre_instruction = ___  # TODO: Use "You are a senior SRE with 10 years of Kubernetes experience. When analyzing alerts, always provide: 1) Root cause analysis, 2) Immediate mitigation steps with exact commands, 3) Long-term prevention strategy. Be concise and actionable."

model_sre = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=sre_instruction
)

response_sre = model_sre.generate_content(f"Analyze this alert:\n{alert}")
print(___)  # TODO: Use response_sre.text
print("-" * 60)

# ── Compare ──────────────────────────────────────────────────────────────────
print("\nComparison:")
print(f"  Generic response length:  {len(response_generic.text)} chars")
print(f"  SRE expert response length: {len(response_sre.text)} chars")

# ── Key Learning ─────────────────────────────────────────────────────────────
print("""
KEY LEARNING — System Prompts Across Providers:
================================================
  Gemini:    system_instruction parameter in GenerativeModel()
             genai.GenerativeModel("gemini-2.5-flash", system_instruction="...")

  OpenAI:    {"role": "system", "content": "..."} in messages list

  Anthropic: system="..." parameter in messages.create()

  Pattern:   All providers support system-level instructions — just different syntax.
  Key Idea:  System prompts turn a general model into a domain expert.
  Bonus:     Gemini is FREE — experiment with different system prompts at zero cost!
""")

print("Next: task3_persona_swap.py — Same alert, three expert personas")
print("Task 2 Complete!")
