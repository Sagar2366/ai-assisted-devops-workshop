#!/usr/bin/env python3
"""
Task 4: LLM Limitations — Microsoft Agent Framework (Semantic Kernel)
Discover what LLMs can't do — hallucination, no live access, no execution.
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
    print("Task 4: LLM Limitations — MAF (Semantic Kernel)")
    print("=" * 65)

    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(service_id="chat", ai_model_id="gpt-4o"))
    chat_service = kernel.get_service("chat")
    settings = chat_service.get_prompt_execution_settings_class()(max_tokens=512)

    # TODO 1: Define tests that expose LLM limitations
    limitation_tests = [
        {
            "name": "Hallucination",
            "prompt": ___,  # TODO: Use "Explain the kubectl drain-memory command and its flags"
            "why": "There is no 'drain-memory' command — watch if it invents one"
        },
        {
            "name": "No Real-Time Access",
            "prompt": "What is the current CPU utilization of my Kubernetes cluster right now?",
            "why": "LLMs have no access to live systems"
        },
        {
            "name": "No Code Execution",
            "prompt": ___,  # TODO: Use "Run 'kubectl get pods -A' on my cluster and show me the output"
            "why": "LLMs cannot execute commands — they can only generate text"
        }
    ]

    for test in limitation_tests:
        print(f"\n{'=' * 65}")
        print(f"Limitation: {test['name']}")
        print(f"Why: {test['why']}")
        print("-" * 65)

        chat = ChatHistory()
        chat.add_user_message(test["prompt"])
        response = await chat_service.get_chat_message_contents(chat_history=chat, settings=settings)
        print(response[0].content[:300])
        print(f"\n  ⚠ Did it {'make something up' if test['name'] == 'Hallucination' else 'admit the limitation'}?")

    print("\n" + "=" * 65)
    print("Key Learning: LLMs are powerful but have hard limits.")
    print("They can hallucinate, can't access live systems, can't run code.")
    print("Tools (Phase 3) solve the last two. Prompting helps the first.")
    print("=" * 65)

    print("\nTask 4 Complete!")
    print("Next: python3 demos/maf/task5_conversation_history.py")


if __name__ == "__main__":
    asyncio.run(main())
