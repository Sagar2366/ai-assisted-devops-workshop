#!/usr/bin/env python3
"""
Task 8: User Personalization — OpenAI GPT
Build a user profile from conversation, extract it as JSON,
then compare generic vs personalized responses.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export OPENAI_API_KEY="your-key-here"
  pip install openai
"""

import json
from openai import OpenAI


def main():
    print("=" * 65)
    print("Task 8: User Personalization — OpenAI GPT")
    print("=" * 65)

    client = OpenAI()

    # Simulated conversation that reveals user preferences
    past_conversation = [
        {"role": "user",      "content": "I'm running a GKE cluster with 50 nodes."},
        {"role": "assistant", "content": "That's a substantial GKE setup. What can I help with?"},
        {"role": "user",      "content": "I prefer Terraform over Pulumi for IaC."},
        {"role": "assistant", "content": "Terraform is great for GKE. Noted."},
        {"role": "user",      "content": "We use Datadog for monitoring and PagerDuty for alerting."},
        {"role": "assistant", "content": "Solid observability stack. Datadog + PagerDuty integrate well."},
        {"role": "user",      "content": "Our team is small — just 3 SREs — so automation is critical."},
        {"role": "assistant", "content": "With a small team, automation is essential. I'll keep that in mind."},
    ]

    # Step 1: Extract user profile as JSON
    print("Step 1: Extracting User Profile from Conversation")
    print("-" * 65)

    # TODO 1: Write the extraction prompt to pull structured data from conversation
    extraction_prompt = ___  # TODO: Use "Analyze this conversation and extract a user profile as JSON with these fields: cloud_provider, cluster_size, iac_tool, monitoring_tool, alerting_tool, team_size, key_priorities. Respond with ONLY valid JSON, no markdown.\n\nConversation:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in past_conversation])

    profile_response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=256,
        messages=[{"role": "user", "content": extraction_prompt}]
    )

    profile_text = profile_response.choices[0].message.content
    print(f"Extracted Profile:\n{profile_text}")

    try:
        profile = json.loads(profile_text)
    except json.JSONDecodeError:
        print("Warning: Could not parse as JSON, using raw text")
        profile = {"raw": profile_text}

    # Step 2: Generic response (no personalization)
    print("\n" + "-" * 65)
    print("Step 2: Generic Response (No Personalization)")
    print("-" * 65)

    question = "How should I set up autoscaling for my cluster?"

    generic_response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=[
            {"role": "system", "content": "You are a DevOps assistant."},
            {"role": "user",   "content": question}
        ]
    )

    print(f"Question: {question}")
    print(f"\nGeneric Response:\n{generic_response.choices[0].message.content}")

    # Step 3: Personalized response
    print("\n" + "-" * 65)
    print("Step 3: Personalized Response (With User Profile)")
    print("-" * 65)

    # TODO 2: Build a personalized system message using the extracted profile
    # Include the user's tools, cloud provider, and constraints
    personalized_system = ___  # TODO: Use f"You are a DevOps assistant. Here is the user's profile:\n{json.dumps(profile, indent=2)}\n\nTailor all recommendations to their specific stack, tools, and team size. Reference their actual tools by name."

    personalized_response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=[
            {"role": "system", "content": personalized_system},
            {"role": "user",   "content": question}
        ]
    )

    print(f"Question: {question}")
    print(f"\nPersonalized Response:\n{personalized_response.choices[0].message.content}")

    print("\n" + "=" * 65)
    print("Key Learning: Extract structured profiles from conversations,")
    print("then inject them as system context. The personalized response")
    print("mentions GKE, Terraform, Datadog by name — not generic advice.")
    print("This is how you build AI assistants that learn about users.")
    print("=" * 65)

    print("\nTask 8 Complete!")
    print("Next: python3 demos/openai/task9_simple_tool.py")


if __name__ == "__main__":
    main()
