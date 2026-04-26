#!/usr/bin/env python3
"""
Task 2: System Prompts — Microsoft Agent Framework (Semantic Kernel)
System prompts via ChatHistory. See how SK handles persona injection.
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
    print("Task 2: System Prompts — MAF (Semantic Kernel)")
    print("=" * 65)

    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(service_id="chat", ai_model_id="gpt-4o"))
    chat_service = kernel.get_service("chat")
    settings = chat_service.get_prompt_execution_settings_class()(max_tokens=1024)

    alert = """Analyze this alert and give me a 3-step remediation plan:

ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)"""

    # Experiment 1: Without system prompt
    print("Experiment 1: No System Prompt (Generic)")
    print("-" * 65)

    chat = ChatHistory()
    chat.add_user_message(alert)
    response = await chat_service.get_chat_message_contents(chat_history=chat, settings=settings)
    print(response[0].content)

    # Experiment 2: With SRE system prompt
    print("\n" + "=" * 65)
    print("Experiment 2: With SRE System Prompt")
    print("-" * 65)

    # TODO 1: Create chat history with a system message
    chat = ChatHistory()
    chat.add_system_message(___)  # TODO: Use "You are a senior SRE with 10 years of Kubernetes experience. Be concise and actionable."
    chat.add_user_message(___)  # TODO: Use alert

    # TODO 2: Get the response
    response = await chat_service.get_chat_message_contents(
        chat_history=___,  # TODO: Use chat
        settings=settings
    )
    print(response[0].content)

    print("\n" + "=" * 65)
    print("Key Difference — System prompts across providers:")
    print("  Anthropic:        system='...' parameter")
    print("  OpenAI:           {'role': 'system'} in messages")
    print("  Bedrock:          'system': '...' in JSON body")
    print("  Semantic Kernel:  chat.add_system_message('...')")
    print("Same concept, SK provides the cleanest API.")
    print("=" * 65)

    print("\nTask 2 Complete!")
    print("Next: python3 demos/maf/task3_persona_swap.py")


if __name__ == "__main__":
    asyncio.run(main())
