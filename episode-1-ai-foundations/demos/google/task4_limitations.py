#!/usr/bin/env python3
"""
Task 4: AI Limitations — Google Gemini
Discover what AI models CANNOT do: hallucination, no real-time data, no code execution.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export GOOGLE_API_KEY="your-key-here"   # Free from aistudio.google.com
  pip install google-generativeai
"""

import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")

print("=" * 60)
print("TASK 4: AI Limitations — What Gemini CANNOT Do")
print("=" * 60)

# ── Limitation 1: Hallucination ──────────────────────────────────────────────
print("\n--- Limitation 1: HALLUCINATION ---")
print("-" * 60)
print("Asking about a completely fake kubectl command...\n")

hallucination_prompt = ___
# TODO: Use "Explain the kubectl autoheal command and show 3 examples of using it in production. Include all available flags."

response1 = model.generate_content(hallucination_prompt)
print(response1.text)
print("-" * 60)
print("REALITY CHECK: 'kubectl autoheal' does NOT exist!")
print("The model may confidently describe a fake command. Always verify.")
print("-" * 60)

# ── Limitation 2: No Real-Time Data ─────────────────────────────────────────
print("\n--- Limitation 2: NO REAL-TIME DATA ---")
print("-" * 60)
print("Asking about current cluster state...\n")

realtime_prompt = ___
# TODO: Use "What is the current CPU utilization of my Kubernetes cluster right now? List all pods that are currently running in the default namespace."

response2 = model.generate_content(realtime_prompt)
print(response2.text)
print("-" * 60)
print("REALITY CHECK: Gemini has NO access to your infrastructure!")
print("It cannot query live systems, metrics, or dashboards.")
print("-" * 60)

# ── Limitation 3: No Code Execution ─────────────────────────────────────────
print("\n--- Limitation 3: NO CODE EXECUTION ---")
print("-" * 60)
print("Asking it to run a command...\n")

execution_prompt = ___
# TODO: Use "Run 'kubectl get nodes' on my cluster and show me the output. Then restart the payment-service deployment."

response3 = model.generate_content(execution_prompt)
print(response3.text)
print("-" * 60)
print("REALITY CHECK: Gemini CANNOT execute commands!")
print("It generates text that looks like output, but nothing actually runs.")
print("-" * 60)

# ── Summary ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("LIMITATION SUMMARY")
print("=" * 60)
limitations = [
    ("Hallucination",    "May invent plausible-sounding but fake information"),
    ("No Real-Time Data", "Cannot access live systems, metrics, or current state"),
    ("No Code Execution", "Cannot run commands — only generates text responses"),
]
for name, desc in limitations:
    print(f"  {name:20s} — {desc}")

# ── Key Learning ─────────────────────────────────────────────────────────────
print("""
KEY LEARNING — Limitations Apply to ALL Providers:
====================================================
  Gemini, OpenAI, Anthropic — ALL share these same three limitations:

  1. Hallucination:    All models can confidently generate wrong information.
  2. No Real-Time:     None can access live infrastructure without tool integration.
  3. No Execution:     None can run code unless connected to an execution environment.

  SRE Rule:  NEVER trust AI output without verification.
  Pattern:   AI assists analysis — humans verify and execute.
  Bonus:     Gemini is FREE — safe to experiment and learn these boundaries!
""")

print("Next: python3 demos/google/task4b_basic_tool.py")
print("Task 4 Complete!")
