#!/usr/bin/env python3
"""
Task 8: Personalized Context — AWS Bedrock
Extract user profile from conversation and use it for personalized responses.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  pip install boto3
  aws configure  (set up AWS credentials)
  Enable Claude model access in AWS Bedrock console
"""

import boto3
import json
import re

def call_bedrock(bedrock, system, messages, max_tokens=256):
    """Helper to call Bedrock and return the assistant text."""
    response = bedrock.invoke_model(
        modelId="anthropic.claude-sonnet-4-20250514-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages
        })
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


def main():
    print("=" * 65)
    print("Task 8: Personalized Context — AWS Bedrock")
    print("=" * 65)

    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"
    )

    system = "You are a helpful agent that provides personalized recommendations."

    # Build conversation with user info (PRE-FILLED)
    print("Building conversation with user details...")
    conversation = []
    conversation_log = []

    user_messages = [
        "Hi, my name is Jamie",
        "I'm an intermediate Python developer",
        "I'm really interested in automation and AI",
        "I want to learn how to build intelligent agents",
        "I prefer detailed technical explanations"
    ]

    for msg in user_messages:
        conversation.append({"role": "user", "content": msg})
        reply = call_bedrock(bedrock, system, conversation)
        conversation.append({"role": "assistant", "content": reply})
        conversation_log.append({"user": msg, "assistant": reply})
        print(f"User: {msg}")

    # Extract user profile
    print("\n" + "=" * 65)
    print("Extracting User Profile")
    print("-" * 65)

    conv_text = ""
    for ex in conversation_log:
        conv_text += f"User: {ex['user']}\nAssistant: {ex['assistant']}\n\n"

    # TODO 1: Ask Claude to extract a structured profile
    extraction_prompt = f"""Analyze this conversation and extract user info as JSON:

Conversation:
{conv_text}

Return ONLY a JSON object:
{{"name": "...", "skill_level": "...", "interests": [...], "goals": [...], "communication_style": "..."}}"""

    response = bedrock.invoke_model(
        modelId="anthropic.claude-sonnet-4-20250514-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 256,
            "messages": [{"role": "user", "content": ___}]  # TODO: Use extraction_prompt
        })
    )
    profile_result = json.loads(response["body"].read())
    profile_json = ___["content"][0]["text"]  # TODO: Use profile_result

    try:
        json_match = re.search(r'\{[^}]+\}', profile_json, re.DOTALL)
        if json_match:
            profile_json = json_match.group(0)
        user_profile = json.loads(profile_json)
    except:
        user_profile = {"name": "Jamie", "skill_level": "intermediate",
                       "interests": ["automation", "AI"], "goals": ["build agents"],
                       "communication_style": "detailed technical"}

    print(f"Name: {user_profile.get('name')}")
    print(f"Level: {user_profile.get('skill_level')}")
    print(f"Interests: {user_profile.get('interests')}")

    # Compare generic vs personalized
    print("\n" + "=" * 65)
    print("Generic vs Personalized Response")
    print("=" * 65)

    test_query = "Recommend a project for me to build"

    # Generic — no context
    print("\nGeneric (no context):")
    reply = call_bedrock(bedrock, system, [{"role": "user", "content": test_query}], max_tokens=512)
    print(reply[:200])

    # TODO 2: Personalized — inject profile as system prompt
    personalized_system = f"""{system}

You are talking to {user_profile.get('name', 'the user')}.
Level: {user_profile.get('skill_level', 'intermediate')}.
Interests: {', '.join(user_profile.get('interests', []))}.
Goals: {', '.join(user_profile.get('goals', []))}.
Prefers: {user_profile.get('communication_style', 'technical')} explanations."""

    print("\nPersonalized (with profile):")
    reply = call_bedrock(bedrock, ___, [{"role": "user", "content": test_query}], max_tokens=512)  # TODO: Use personalized_system
    print(reply[:200])

    print("\n" + "=" * 65)
    print("Key Learning: Extract profile → inject as system prompt → personalized responses")
    print("=" * 65)

    print("\nTask 8 Complete!")
    print("Next: python3 demos/bedrock/task9_simple_tool.py")


if __name__ == "__main__":
    main()
