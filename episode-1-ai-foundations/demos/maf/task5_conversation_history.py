#!/usr/bin/env python3
"""
Task 5: Conversation History — Microsoft Agent Framework (Semantic Kernel)
Multi-turn conversations using ChatHistory. SK manages state for you.
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
    print("Task 5: Conversation History — MAF (Semantic Kernel)")
    print("=" * 65)

    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(service_id="chat", ai_model_id="gpt-4o"))
    chat_service = kernel.get_service("chat")
    settings = chat_service.get_prompt_execution_settings_class()(max_tokens=512)

    # TODO 1: Create a ChatHistory with a system message
    chat = ___  # TODO: Use ChatHistory()
    chat.add_system_message("You are a Kubernetes tutor. Build on previous answers. Be concise.")

    messages = [
        "What is a Pod in Kubernetes?",
        "How is that different from a Deployment?",
        "Can you give me a YAML example of a Deployment with 3 replicas?"
    ]

    for i, msg in enumerate(messages, 1):
        print(f"\n--- Turn {i} ---")
        print(f"User: {msg}")

        # TODO 2: Add user message and get response
        chat.add_user_message(___)  # TODO: Use msg

        response = await chat_service.get_chat_message_contents(chat_history=chat, settings=settings)
        reply = response[0].content

        # TODO 3: Add assistant response to history
        chat.add_assistant_message(___)  # TODO: Use reply
        print(f"Assistant: {reply[:200]}...")

    # Show history stats
    print(f"\n--- History ---")
    print(f"  Total messages: {len(chat.messages)}")
    for m in chat.messages:
        print(f"  [{m.role}] {str(m.content)[:60]}...")

    print("\n" + "=" * 65)
    print("Key Learning: ChatHistory manages multi-turn state automatically.")
    print("Add user messages, get responses, add assistant replies.")
    print("SK handles the message format for the underlying provider.")
    print("=" * 65)

    print("\nTask 5 Complete!")
    print("Next: python3 demos/maf/task6_context_window.py")


if __name__ == "__main__":
    asyncio.run(main())
