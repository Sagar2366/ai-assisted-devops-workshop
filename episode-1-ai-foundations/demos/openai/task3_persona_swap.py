#!/usr/bin/env python3
"""
Task 3: Persona Swap — OpenAI GPT
Same alert, 3 different personas. Watch how the system message completely changes the response.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export OPENAI_API_KEY="your-key-here"
  pip install openai
"""

from openai import OpenAI

def main():
    print("=" * 65)
    print("Task 3: Persona Swap — OpenAI GPT")
    print("=" * 65)

    client = OpenAI()

    alert = """Analyze this alert:

ALERT: HighErrorRate
Service: payment-gateway
Error Rate: 12.5% (threshold: 1%)
Duration: 45 minutes
Affected Endpoints: /api/v1/charge, /api/v1/refund
Region: us-east-1
HTTP 500 Count: 3,420 in last hour"""

    personas = {
        "SRE Engineer": "You are a senior SRE focused on reliability and uptime. Prioritize immediate remediation, blast radius assessment, and preventing recurrence. Be concise and actionable.",
        "Security Engineer": "You are a security engineer focused on threat detection. Analyze alerts for signs of intrusion, data exfiltration, or vulnerability exploitation. Recommend security hardening steps.",
        "Cost Analyst": "You are a cloud cost analyst. Evaluate the financial impact of incidents including lost revenue, wasted compute, and recovery costs. Suggest cost-optimized solutions.",
    }

    for persona_name, system_msg in personas.items():
        print(f"\nPersona: {persona_name}")
        print("-" * 65)

        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": alert}
            ]
        )
        print(response.choices[0].message.content)
        print()

    print("=" * 65)
    print("Key Learning: Same data, 3 completely different analyses.")
    print("The system message IS the persona. In production, you can")
    print("route the same alert to multiple AI personas simultaneously.")
    print("=" * 65)

    print("\nTask 3 Complete!")
    print("Next: python3 demos/openai/task4_limitations.py")


if __name__ == "__main__":
    main()
