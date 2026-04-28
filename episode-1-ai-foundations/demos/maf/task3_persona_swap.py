#!/usr/bin/env python3
"""
Task 3: Persona Swap — Microsoft Agent Framework (Semantic Kernel)
Same alert, 3 experts. System messages shape the entire response.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export OPENAI_API_KEY="your-key-here"
  pip install semantic-kernel
"""

import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatHistory

async def main():
    print("=" * 65)
    print("Task 3: Persona Swap — MAF (Semantic Kernel)")
    print("=" * 65)

    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(service_id="chat", ai_model_id="gpt-4o"))
    chat_service = kernel.get_service("chat")
    settings = chat_service.get_prompt_execution_settings_class()(max_tokens=512)

    alert = """ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)"""

    personas = {
        "SRE Engineer": "You are a senior SRE. Focus on immediate remediation, resource tuning, and preventing recurrence. Be specific with kubectl commands.",
        "Security Engineer": "You are a security engineer. Analyze for security implications — is this an attack? data exposure? compliance risk? Focus on threat assessment.",
        "Cost Analyst": "You are a cloud cost analyst. Focus on resource efficiency, right-sizing, and cost impact. Provide specific cost optimization recommendations.",
    }

    for persona_name, system_prompt in personas.items():
        print(f"\n{'=' * 65}")
        print(f"Persona: {persona_name}")
        print("-" * 65)

        chat = ChatHistory()
        chat.add_system_message(system_prompt)
        chat.add_user_message(f"Analyze this alert:\n{alert}")

        response = await chat_service.get_chat_message_contents(chat_history=chat, settings=settings)
        print(response[0].content)

    print("\n" + "=" * 65)
    print("Key Learning: Same data, different system message = different expert.")
    print("The system message is the most powerful lever you have.")
    print("=" * 65)

    print("\nTask 3 Complete!")
    print("Next: python3 demos/maf/task4_limitations.py")


if __name__ == "__main__":
    asyncio.run(main())
