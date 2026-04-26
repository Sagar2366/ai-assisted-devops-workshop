#!/usr/bin/env python3
"""
Task 3: Persona Swap — Google Gemini
Same OOM alert analyzed by three different expert personas via system_instruction.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export GOOGLE_API_KEY="your-key-here"   # Free from aistudio.google.com
  pip install google-generativeai
"""

import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# ── The Same Alert for All Personas ──────────────────────────────────────────
alert = """ALERT: OOMKilled
Pod: payment-service-7d4b8c6f5-x2vnm
Namespace: production
Container: payment-api
Memory Limit: 512Mi
Last Restart: 3 times in 10 minutes
Timestamp: 2024-01-15T03:42:18Z"""

# ── Define Three Expert Personas ─────────────────────────────────────────────
personas = {
    "SRE Engineer": ___,
    # TODO: Use "You are a senior SRE engineer. Focus on: immediate remediation steps with exact kubectl commands, root cause analysis, and monitoring improvements. Be direct and action-oriented."

    "Security Analyst": ___,
    # TODO: Use "You are a senior security analyst. Focus on: potential security implications of the failure, whether this could indicate an attack (e.g., memory-based DoS), audit trail analysis, and security hardening recommendations."

    "Cost Analyst": ___,
    # TODO: Use "You are a cloud cost optimization analyst. Focus on: resource waste from restarts, right-sizing recommendations, cost impact of over/under-provisioning, and FinOps best practices for memory limits."
}

print("=" * 60)
print("TASK 3: Persona Swap — Three Experts, One Alert")
print("=" * 60)
print(f"\nAlert: OOMKilled on payment-service (production)")
print("=" * 60)

# ── Run Each Persona ─────────────────────────────────────────────────────────
for persona_name, instruction in personas.items():
    print(f"\n{'=' * 60}")
    print(f"  PERSONA: {persona_name}")
    print(f"{'=' * 60}")

    model = ___  # TODO: Use genai.GenerativeModel("gemini-2.5-flash", system_instruction=instruction)

    response = model.generate_content(f"Analyze this production alert and provide your expert assessment:\n{alert}")

    print(response.text)
    print("-" * 60)
    print(f"  Tokens used: {response.usage_metadata.total_token_count}")
    print("-" * 60)

# ── Key Learning ─────────────────────────────────────────────────────────────
print("""
KEY LEARNING — Persona Swap Pattern:
=====================================
  Gemini:    Create a NEW GenerativeModel per persona with different system_instruction
             genai.GenerativeModel("gemini-2.5-flash", system_instruction=persona)

  OpenAI:    Swap the system message in the messages list per call

  Anthropic: Change the system= parameter per call

  Pattern:   Same data + different persona = completely different expert analysis.
  Real Use:  In production, route alerts to multiple AI personas for comprehensive triage.
  Bonus:     Gemini is FREE — test dozens of personas without spending a penny!
""")

print("Next: task4_limitations.py — Discover what AI cannot do")
print("Task 3 Complete!")
