#!/usr/bin/env python3
"""
Task 7: Summarization — Microsoft Agent Framework (Semantic Kernel)
Compress old conversation into a summary to save context space.
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
    print("Task 7: Summarization — MAF (Semantic Kernel)")
    print("=" * 65)

    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(service_id="chat", ai_model_id="gpt-4o"))
    chat_service = kernel.get_service("chat")
    settings = chat_service.get_prompt_execution_settings_class()(max_tokens=512)

    # Build up a conversation
    chat = ChatHistory()
    chat.add_system_message("You are a DevOps tutor. Be concise.")

    exchanges = [
        "What is CI/CD?",
        "What tools are commonly used for CI/CD?",
        "How does GitHub Actions compare to Jenkins?",
        "What are the best practices for pipeline design?",
    ]

    print("Building conversation...")
    for q in exchanges:
        chat.add_user_message(q)
        response = await chat_service.get_chat_message_contents(chat_history=chat, settings=settings)
        reply = response[0].content
        chat.add_assistant_message(reply)
        print(f"  Q: {q}")

    print(f"\nConversation: {len(chat.messages)} messages")

    # Summarize the conversation
    print("\n--- Summarizing ---")

    # TODO 1: Build the summarization prompt
    conv_text = ""
    for m in chat.messages:
        if m.role != "system":
            conv_text += f"{m.role}: {m.content}\n\n"

    summary_prompt = ___  # TODO: Use f"Summarize this conversation in 2-3 sentences, capturing the key topics and conclusions:\n\n{conv_text}"

    summary_chat = ChatHistory()
    summary_chat.add_user_message(summary_prompt)
    response = await chat_service.get_chat_message_contents(chat_history=summary_chat, settings=settings)
    summary = response[0].content
    print(f"Summary: {summary}")

    # Use summary for new conversation
    print("\n--- New Conversation with Summary ---")

    # TODO 2: Create new chat with summary injected as system context
    new_chat = ChatHistory()
    new_chat.add_system_message(f"You are a DevOps tutor. Previous conversation summary: {___}")  # TODO: Use summary
    new_chat.add_user_message("Based on what we discussed, should I use GitHub Actions or Jenkins for a small team?")

    response = await chat_service.get_chat_message_contents(chat_history=new_chat, settings=settings)
    print(f"Reply: {response[0].content[:300]}")

    # Compare sizes
    print(f"\n--- Comparison ---")
    print(f"  Original: {len(conv_text)} chars ({len(chat.messages)} messages)")
    print(f"  Summary:  {len(summary)} chars (1 message)")
    print(f"  Savings:  {(1 - len(summary)/len(conv_text))*100:.0f}%")

    print("\n" + "=" * 65)
    print("Key Learning: Summarize old context to stay within token limits")
    print("while retaining the essential information.")
    print("=" * 65)

    print("\nTask 7 Complete!")
    print("Next: python3 demos/maf/task8_personalization.py")


if __name__ == "__main__":
    asyncio.run(main())
