#!/usr/bin/env python3
"""
Task 8: Personalization — Google Gemini
Build a user profile from conversation, extract as JSON, and compare generic vs personalized responses.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export GOOGLE_API_KEY="your-key-here"   # Free from aistudio.google.com
  pip install google-generativeai
"""

import google.generativeai as genai
import os
import json

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def main():
    print("=" * 65)
    print("Task 8: Personalization — Google Gemini")
    print("=" * 65)

    # Phase 1: Gather user context through conversation
    print("\n--- Phase 1: Gather user context ---")
    print("-" * 65)

    model = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction="You are a friendly DevOps assistant. Ask brief follow-up questions to understand the user's environment. Keep responses to 2 sentences."
    )

    chat = model.start_chat()

    user_messages = [
        "Hi, I'm Marcus. I'm an SRE at a healthcare startup.",
        "We run on AWS EKS with about 30 microservices. Mostly Python and Go.",
        "Our biggest pain point is deployment rollbacks — they take forever.",
        "We use Helm charts and ArgoCD. Our team is just 3 SREs for everything.",
        "I prefer runbook-style answers with exact commands I can copy-paste.",
    ]

    for msg in user_messages:
        response = chat.send_message(msg)
        print(f"  Marcus: {msg}")
        print(f"  Assistant: {response.text[:100]}...")
        print()

    # Phase 2: Extract user profile as JSON
    print("\n--- Phase 2: Extract user profile ---")
    print("-" * 65)

    transcript = ""
    for entry in chat.history:
        transcript += f"{entry.role}: {entry.parts[0].text}\n\n"

    extraction_prompt = "Extract a user profile from this conversation as valid JSON. Include these fields: name, role, company_type, cloud_provider, orchestration, num_services, languages, tools (list), team_size, pain_points (list), preferred_response_style. Only output the JSON, no markdown formatting.\n\nConversation:\n" + transcript

    extraction_model = genai.GenerativeModel("gemini-2.5-flash")
    profile_response = extraction_model.generate_content(extraction_prompt)

    profile_text = profile_response.text.strip()
    if profile_text.startswith("```"):
        profile_text = profile_text.split("\n", 1)[1]
        if profile_text.endswith("```"):
            profile_text = profile_text.rsplit("```", 1)[0]
        profile_text = profile_text.strip()

    try:
        profile = json.loads(profile_text)
        print("Extracted Profile:")
        print(json.dumps(profile, indent=2))
    except json.JSONDecodeError:
        print("Raw profile (could not parse as JSON):")
        print(profile_text)
        profile = {"raw": profile_text}

    # Phase 3: Compare generic vs personalized
    print("\n--- Phase 3: Generic vs Personalized ---")
    print("-" * 65)

    test_question = "How should I handle a failed deployment that needs immediate rollback?"

    print("\n  GENERIC RESPONSE (no personalization):")
    generic_model = genai.GenerativeModel("gemini-2.5-flash")
    generic_response = generic_model.generate_content(test_question)
    print(f"  {generic_response.text}")

    print("\n  PERSONALIZED RESPONSE (with user profile):")
    personalized_instruction = f"You are a DevOps assistant personalized for this user:\n\n{json.dumps(profile, indent=2)}\n\nAlways tailor responses to their specific stack (AWS EKS, Helm, ArgoCD), team size (small), and preferred style (runbook with exact commands). Reference their tools by name."

    personalized_model = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction=personalized_instruction
    )
    personalized_response = personalized_model.generate_content(test_question)
    print(f"  {personalized_response.text}")

    # Compare
    print("\n" + "=" * 65)
    print("COMPARISON")
    print("=" * 65)
    print(f"  Generic response length:       {len(generic_response.text)} chars")
    print(f"  Personalized response length:  {len(personalized_response.text)} chars")
    print("\n  Notice how the personalized response:")
    print("  - References specific tools (Helm, ArgoCD, EKS)")
    print("  - Gives copy-paste commands (user's preferred style)")
    print("  - Considers the small team size in recommendations")

    print("\nTask 8 Complete!")
    print("Next: python3 demos/google/task9_basic_tool.py")


if __name__ == "__main__":
    main()
