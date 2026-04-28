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

    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(service_id="chat", ai_model_id="gpt-4o"))

    # Experiment 1: Basic API call
    print("\nExperiment 1: Basic API Call")
    print("-" * 65)

    chat = ChatHistory()
    chat.add_user_message("What is Kubernetes and why do DevOps engineers use it?")

    chat_service = kernel.get_service("chat")
    response = await chat_service.get_chat_message_contents(
        chat_history=chat,
        settings=chat_service.get_prompt_execution_settings_class()(max_tokens=1024)
    )
    print(response[0].content)

    print("\n" + "=" * 65)
    print("Key Learning: Semantic Kernel wraps LLM providers behind a")
    print("unified interface. Change the service, keep the code.")
    print("=" * 65)

    print("\nTask 1 Complete!")
    print("Next: python3 demos/maf/task2_system_prompts.py")


if __name__ == "__main__":
    asyncio.run(main())
