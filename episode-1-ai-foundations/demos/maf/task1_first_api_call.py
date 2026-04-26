#!/usr/bin/env python3
"""
Task 1: Your First API Call — Microsoft Agent Framework (Semantic Kernel)
Higher-level abstraction over LLMs. Same task, different paradigm.
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
    print("Task 1: Your First API Call — MAF (Semantic Kernel)")
    print("=" * 65)

    # Step 1: Create the kernel and add an AI service (PRE-FILLED)
    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(service_id="chat", ai_model_id="gpt-4o"))

    print("Step 1 Complete: Kernel created with OpenAI service\n")

    # Experiment 1: Basic call via Semantic Kernel
    print("Experiment 1: Basic API Call")
    print("-" * 65)

    # TODO 1: Create a chat history and add a user message
    chat = ___  # TODO: Use ChatHistory()
    chat.add_user_message(___)  # TODO: Use "What is Kubernetes and why do DevOps engineers use it?"

    # TODO 2: Get a response from the AI service
    chat_service = kernel.get_service("chat")
    response = await chat_service.get_chat_message_contents(
        chat_history=___,  # TODO: Use chat
        settings=chat_service.get_prompt_execution_settings_class()(max_tokens=1024)
    )

    print(response[0].content)

    # Experiment 2: Compare with direct SDKs
    print("\n" + "-" * 65)
    print("Experiment 2: Notice the Paradigm Shift")
    print("-" * 65)
    print("Direct SDKs:  client.messages.create(model, messages)")
    print("Semantic Kernel: kernel → service → chat_history → get_chat_message_contents()")
    print("\nSemantic Kernel adds abstraction: swap providers without changing logic.")

    print("\n" + "=" * 65)
    print("Key Learning: Semantic Kernel wraps LLM providers behind a")
    print("unified interface. Change the service, keep the code.")
    print("=" * 65)

    print("\nTask 1 Complete!")
    print("Next: python3 demos/maf/task2_system_prompts.py")


if __name__ == "__main__":
    asyncio.run(main())
