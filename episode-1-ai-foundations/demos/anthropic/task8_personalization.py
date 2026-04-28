#!/usr/bin/env python3
"""
Task 8: Personalized Context — SRE Profile Extraction — Anthropic Claude
Extract a structured SRE profile from conversation and use it for personalized responses.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic
import json
import re

def main():
    print("=" * 65)
    print("Task 8: Personalized Context — Anthropic Claude")
    print("=" * 65)

    client = anthropic.Anthropic()
    system = "You are a helpful DevOps assistant that provides personalized recommendations."

    print("Building conversation with SRE details...")
    conversation = []
    conversation_log = []

    user_messages = [
        "Hi, I'm Sagar, an SRE at Acme Corp",
        "We run EKS with about 50 microservices in production",
        "We use ArgoCD for deployments and Prometheus for monitoring",
        "Our team is 5 SREs covering 3 time zones",
        "Biggest pain point is OOM kills on payment-service after every deploy. Budget is $500/month for AI tools."
    ]

    for msg in user_messages:
        conversation.append({"role": "user", "content": msg})
        r = client.messages.create(
            model="claude-opus-4-7", max_tokens=256,
            system=system, messages=conversation
        )
        reply = r.content[0].text
        conversation.append({"role": "assistant", "content": reply})
        conversation_log.append({"user": msg, "assistant": reply})
        print(f"User: {msg}")

    # Extract SRE profile
    print("\n" + "=" * 65)
    print("Extracting SRE Profile")
    print("-" * 65)

    conv_text = ""
    for ex in conversation_log:
        conv_text += f"User: {ex['user']}\nAssistant: {ex['assistant']}\n\n"

    extraction_prompt = f"""Extract a user profile from this conversation as JSON.
Include: name, role, company, cloud_provider, tools, team_size, pain_points, budget.

Conversation:
{conv_text}

Return ONLY a JSON object:
{{"name": "...", "role": "...", "company": "...", "cloud_provider": "...", "tools": [...], "team_size": "...", "pain_points": [...], "budget": "..."}}"""

    profile_response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=256,
        messages=[{"role": "user", "content": extraction_prompt}]
    )
    profile_json = profile_response.content[0].text

    try:
        json_match = re.search(r'\{[^}]+\}', profile_json, re.DOTALL)
        if json_match:
            profile_json = json_match.group(0)
        user_profile = json.loads(profile_json)
    except:
        user_profile = {"name": "Sagar", "role": "SRE", "company": "Acme Corp",
                       "cloud_provider": "EKS", "tools": ["ArgoCD", "Prometheus"],
                       "team_size": "5", "pain_points": ["OOM kills"], "budget": "$500/month"}

    print(f"Name: {user_profile.get('name')}")
    print(f"Role: {user_profile.get('role')}")
    print(f"Company: {user_profile.get('company')}")
    print(f"Tools: {user_profile.get('tools')}")
    print(f"Pain Points: {user_profile.get('pain_points')}")

    # Compare generic vs personalized
    print("\n" + "=" * 65)
    print("Generic vs Personalized Response")
    print("=" * 65)

    test_query = "How should I handle a failed deployment?"

    print("\nGeneric (no context):")
    r = client.messages.create(
        model="claude-opus-4-7", max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": test_query}]
    )
    print(r.content[0].text[:200])

    personalized_system = f"""{system}

You are talking to {user_profile.get('name', 'the user')}, {user_profile.get('role', 'an engineer')} at {user_profile.get('company', 'their company')}.
Cloud: {user_profile.get('cloud_provider', 'unknown')}.
Tools: {', '.join(user_profile.get('tools', []))}.
Team: {user_profile.get('team_size', 'unknown')} engineers.
Pain points: {', '.join(user_profile.get('pain_points', []))}.
Budget: {user_profile.get('budget', 'unknown')}.
Tailor all responses to their specific stack, tools, and constraints."""

    print("\nPersonalized (with profile):")
    r = client.messages.create(
        model="claude-opus-4-7", max_tokens=512,
        system=personalized_system,
        messages=[{"role": "user", "content": test_query}]
    )
    print(r.content[0].text[:200])

    print("\n" + "=" * 65)
    print("Key Learning: Extract profile -> inject as system prompt -> personalized responses")
    print("The AI stops giving generic advice and starts referencing your actual tools.")
    print("=" * 65)

    print("\nTask 8 Complete!")
    print("Next: python3 demos/anthropic/task9_basic_tool.py")


if __name__ == "__main__":
    main()
