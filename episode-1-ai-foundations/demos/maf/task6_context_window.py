#!/usr/bin/env python3
"""
Task 6: Context Window Management — Microsoft Agent Framework (Semantic Kernel)
Sliding window to keep conversation within token limits.
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
    print("Task 6: Context Window — MAF (Semantic Kernel)")
    print("=" * 65)

    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(service_id="chat", ai_model_id="gpt-4o"))
    chat_service = kernel.get_service("chat")
    settings = chat_service.get_prompt_execution_settings_class()(max_tokens=256)

    WINDOW_SIZE = 6

    full_chat = ChatHistory()
    full_chat.add_system_message("You are a DevOps assistant. Be concise.")

    questions = [
        "What is Docker?",
        "How does Docker relate to Kubernetes?",
        "What is a Kubernetes Service?",
        "Explain Ingress controllers",
        "What is Helm?",
        "How do ConfigMaps work?",
        "What is a StatefulSet?",
        "Explain the difference between DaemonSet and Deployment",
    ]

    for i, q in enumerate(questions, 1):
        print(f"\n--- Turn {i}: {q} ---")
        full_chat.add_user_message(q)

        # Create windowed chat — keep system + last N messages
        windowed = ChatHistory()
        windowed.add_system_message("You are a DevOps assistant. Be concise.")

        all_msgs = [m for m in full_chat.messages if m.role != "system"]
        recent = all_msgs[-WINDOW_SIZE:]
        for m in recent:
            if m.role == "user":
                windowed.add_user_message(m.content)
            else:
                windowed.add_assistant_message(m.content)

        response = await chat_service.get_chat_message_contents(chat_history=windowed, settings=settings)
        reply = response[0].content
        full_chat.add_assistant_message(reply)

        print(f"  Window: {len(recent)} msgs (of {len(all_msgs)} total)")
        print(f"  Reply: {reply[:150]}...")

    # Test memory loss
    print("\n--- Memory Test ---")
    full_chat.add_user_message("What was the first thing I asked you about?")
    windowed = ChatHistory()
    windowed.add_system_message("You are a DevOps assistant. Be concise.")
    all_msgs = [m for m in full_chat.messages if m.role != "system"]
    for m in all_msgs[-WINDOW_SIZE:]:
        if m.role == "user":
            windowed.add_user_message(m.content)
        else:
            windowed.add_assistant_message(m.content)

    response = await chat_service.get_chat_message_contents(chat_history=windowed, settings=settings)
    reply = response[0].content
    print(f"Reply: {reply[:200]}")
    print(f"\n(First question was about Docker — can the model remember?)")

    print("\n" + "=" * 65)
    print("Key Learning: Sliding window keeps context small but loses old info.")
    print("Trade-off: cost/speed vs memory. Summarization (Task 7) helps.")
    print("=" * 65)

    print("\nTask 6 Complete!")
    print("Next: python3 demos/maf/task7_summarization.py")


if __name__ == "__main__":
    asyncio.run(main())
