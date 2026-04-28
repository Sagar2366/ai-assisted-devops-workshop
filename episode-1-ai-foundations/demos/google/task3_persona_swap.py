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

def main():
    print("=" * 65)
    print("Task 3: Persona Swap — Google Gemini")
    print("=" * 65)

    alert = """ALERT: OOMKilled
Pod: payment-service-7d4b8c6f5-x2vnm
Namespace: production
Container: payment-api
Memory Limit: 512Mi
Last Restart: 3 times in 10 minutes
Timestamp: 2024-01-15T03:42:18Z"""

    personas = {
        "SRE Engineer": "You are a senior SRE engineer. Focus on: immediate remediation steps with exact kubectl commands, root cause analysis, and monitoring improvements. Be direct and action-oriented.",
        "Security Analyst": "You are a senior security analyst. Focus on: potential security implications of the failure, whether this could indicate an attack (e.g., memory-based DoS), audit trail analysis, and security hardening recommendations.",
        "Cost Analyst": "You are a cloud cost optimization analyst. Focus on: resource waste from restarts, right-sizing recommendations, cost impact of over/under-provisioning, and FinOps best practices for memory limits.",
    }

    print(f"\nAlert: OOMKilled on payment-service (production)")
    print("=" * 65)

    for persona_name, instruction in personas.items():
        print(f"\n{'=' * 60}")
        print(f"  PERSONA: {persona_name}")
        print(f"{'=' * 60}")

        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=instruction)
        response = model.generate_content(f"Analyze this production alert and provide your expert assessment:\n{alert}")

        print(response.text)
        print("-" * 60)
        print(f"  Tokens used: {response.usage_metadata.total_token_count}")

    print("\n" + "=" * 65)
    print("Key Learning: Create a NEW GenerativeModel per persona with")
    print("different system_instruction. Same data + different persona =")
    print("completely different expert analysis.")
    print("=" * 65)

    print("\nTask 3 Complete!")
    print("Next: python3 demos/google/task4_limitations.py")


if __name__ == "__main__":
    main()
