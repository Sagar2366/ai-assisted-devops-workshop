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

def main():
    print("=" * 65)
    print("Task 4: AI Limitations — Google Gemini")
    print("=" * 65)

    model = genai.GenerativeModel("gemini-2.5-flash")

    # Limitation 1: Hallucination
    print("\nLimitation 1: HALLUCINATION")
    print("-" * 65)
    print("Asking about a completely fake kubectl command...\n")

    response1 = model.generate_content("Explain the kubectl autoheal command and show 3 examples of using it in production. Include all available flags.")
    print(response1.text)
    print("-" * 65)
    print("REALITY CHECK: 'kubectl autoheal' does NOT exist!")
    print("The model may confidently describe a fake command. Always verify.")

    # Limitation 2: No Real-Time Data
    print("\n" + "-" * 65)
    print("Limitation 2: NO REAL-TIME DATA")
    print("-" * 65)
    print("Asking about current cluster state...\n")

    response2 = model.generate_content("What is the current CPU utilization of my Kubernetes cluster right now? List all pods that are currently running in the default namespace.")
    print(response2.text)
    print("-" * 65)
    print("REALITY CHECK: Gemini has NO access to your infrastructure!")

    # Limitation 3: No Code Execution
    print("\n" + "-" * 65)
    print("Limitation 3: NO CODE EXECUTION")
    print("-" * 65)
    print("Asking it to run a command...\n")

    response3 = model.generate_content("Run 'kubectl get nodes' on my cluster and show me the output. Then restart the payment-service deployment.")
    print(response3.text)
    print("-" * 65)
    print("REALITY CHECK: Gemini CANNOT execute commands!")

    # Summary
    print("\n" + "=" * 65)
    print("LIMITATION SUMMARY")
    print("=" * 65)
    limitations = [
        ("Hallucination",     "May invent plausible-sounding but fake information"),
        ("No Real-Time Data", "Cannot access live systems, metrics, or current state"),
        ("No Code Execution", "Cannot run commands — only generates text responses"),
    ]
    for name, desc in limitations:
        print(f"  {name:20s} — {desc}")

    print("\nSRE Rule: NEVER trust AI output without verification.")
    print("These limitations are why AGENTS exist (Episode 4).")

    print("\nTask 4 Complete!")
    print("Next: python3 demos/google/task5_conversation_history.py")


if __name__ == "__main__":
    main()
