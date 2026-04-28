#!/usr/bin/env python3
"""
Task 8: Personalized Context — Microsoft Agent Framework (Semantic Kernel)
Extract user profile from conversation and personalize responses.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export OPENAI_API_KEY="your-key-here"
  pip install semantic-kernel
"""

import asyncio
import json
import re
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatHistory

async def main():
    print("=" * 65)
    print("Task 8: Personalized Context — MAF (Semantic Kernel)")
    print("=" * 65)

    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(service_id="chat", ai_model_id="gpt-4o"))
    chat_service = kernel.get_service("chat")
    settings = chat_service.get_prompt_execution_settings_class()(max_tokens=512)

    print("Building conversation with user details...")
    chat = ChatHistory()
    chat.add_system_message("You are a helpful agent that provides personalized recommendations.")

    user_messages = [
        "Hi, my name is Jamie",
        "I'm an intermediate Python developer",
        "I'm really interested in automation and AI",
        "I want to learn how to build intelligent agents",
        "I prefer detailed technical explanations"
    ]

    for msg in user_messages:
        chat.add_user_message(msg)
        response = await chat_service.get_chat_message_contents(chat_history=chat, settings=settings)
        chat.add_assistant_message(response[0].content)
        print(f"  User: {msg}")

    # Extract user profile
    print("\n" + "=" * 65)
    print("Extracting User Profile")
    print("-" * 65)

    conv_text = ""
    for m in chat.messages:
        if m.role != "system":
            conv_text += f"{m.role}: {m.content}\n\n"

    extraction_prompt = f"Analyze this conversation and extract user info as JSON:\n\n{conv_text}\n\nReturn ONLY a JSON object:\n{{\"name\": \"...\", \"skill_level\": \"...\", \"interests\": [...], \"goals\": [...], \"communication_style\": \"...\"}}"

    extract_chat = ChatHistory()
    extract_chat.add_user_message(extraction_prompt)
    response = await chat_service.get_chat_message_contents(chat_history=extract_chat, settings=settings)
    profile_json = response[0].content

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

    print("\nGeneric (no context):")
    generic_chat = ChatHistory()
    generic_chat.add_user_message(test_query)
    response = await chat_service.get_chat_message_contents(chat_history=generic_chat, settings=settings)
    print(response[0].content[:200])

    personalized_system = f"""You are a helpful agent that provides personalized recommendations.
You are talking to {user_profile.get('name', 'the user')}.
Level: {user_profile.get('skill_level', 'intermediate')}.
Interests: {', '.join(user_profile.get('interests', []))}.
Goals: {', '.join(user_profile.get('goals', []))}.
Prefers: {user_profile.get('communication_style', 'technical')} explanations."""

    print("\nPersonalized (with profile):")
    personal_chat = ChatHistory()
    personal_chat.add_system_message(personalized_system)
    personal_chat.add_user_message(test_query)
    response = await chat_service.get_chat_message_contents(chat_history=personal_chat, settings=settings)
    print(response[0].content[:200])

    print("\n" + "=" * 65)
    print("Key Learning: Extract profile -> inject as system context -> personalized responses.")
    print("SK's ChatHistory makes this pattern clean and provider-agnostic.")
    print("=" * 65)

    print("\nTask 8 Complete!")
    print("Next: python3 demos/maf/task9_basic_tool.py")


if __name__ == "__main__":
    asyncio.run(main())
