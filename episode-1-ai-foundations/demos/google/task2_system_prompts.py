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

def main():
    print("=" * 65)
    print("Task 2: System Prompts — Google Gemini")
    print("=" * 65)

    alert = """ALERT: OOMKilled
Pod: payment-service-7d4b8c6f5-x2vnm
Namespace: production
Container: payment-api
Memory Limit: 512Mi
Last Restart: 3 times in 10 minutes
Timestamp: 2024-01-15T03:42:18Z"""

    # Experiment 1: Without system instruction
    print("\nExperiment 1: No System Instruction (Generic)")
    print("-" * 65)

    model_generic = genai.GenerativeModel("gemini-2.5-flash")
    response_generic = model_generic.generate_content(f"Analyze this alert:\n{alert}")
    print(response_generic.text)

    # Experiment 2: With system instruction
    print("\n" + "=" * 65)
    print("Experiment 2: With SRE System Instruction")
    print("-" * 65)

    sre_instruction = "You are a senior SRE with 10 years of Kubernetes experience. When analyzing alerts, always provide: 1) Root cause analysis, 2) Immediate mitigation steps with exact commands, 3) Long-term prevention strategy. Be concise and actionable."

    model_sre = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction=sre_instruction
    )
    response_sre = model_sre.generate_content(f"Analyze this alert:\n{alert}")
    print(response_sre.text)

    # Compare
    print("\n" + "-" * 65)
    print("Comparison:")
    print(f"  Generic response length:  {len(response_generic.text)} chars")
    print(f"  SRE expert response length: {len(response_sre.text)} chars")

    print("\n" + "=" * 65)
    print("Key Learning: system_instruction in GenerativeModel() turns")
    print("Gemini into a domain expert. Same concept as Anthropic's system param.")
    print("=" * 65)

    print("\nTask 2 Complete!")
    print("Next: python3 demos/google/task3_persona_swap.py")


if __name__ == "__main__":
    main()
