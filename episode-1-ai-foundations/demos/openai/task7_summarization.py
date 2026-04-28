#!/usr/bin/env python3
"""
Task 7: Conversation Summarization — OpenAI GPT
Compress old conversation into a summary and inject it as context.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export OPENAI_API_KEY="your-key-here"
  pip install openai
"""

from openai import OpenAI

def main():
    print("=" * 65)
    print("Task 7: Conversation Summarization — OpenAI GPT")
    print("=" * 65)

    client = OpenAI()

    old_conversation = [
        {"role": "user",      "content": "We're seeing 500 errors on the checkout API."},
        {"role": "assistant", "content": "Check the API gateway logs and backend health."},
        {"role": "user",      "content": "Gateway logs show timeouts to payment-service."},
        {"role": "assistant", "content": "Payment service might be overloaded. Check its CPU and memory."},
        {"role": "user",      "content": "Payment service CPU is fine but memory is at 95%."},
        {"role": "assistant", "content": "Memory pressure is likely causing GC pauses. Check GC logs."},
        {"role": "user",      "content": "GC logs show full GC every 2 seconds. Heap is 512MB."},
        {"role": "assistant", "content": "Increase heap to 1GB and add memory limits in the deployment."},
    ]

    print(f"Old conversation: {len(old_conversation)} messages")

    # Summarize
    print("\nStep 1: Summarizing old conversation...")
    print("-" * 65)

    summarization_prompt = "Summarize this conversation into 3-4 bullet points. Focus on: the problem, root cause found, and actions taken. Be concise.\n\nConversation:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in old_conversation])

    summary_response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=256,
        messages=[{"role": "user", "content": summarization_prompt}]
    )
    summary = summary_response.choices[0].message.content
    print(f"Summary:\n{summary}")

    # Use summary as context
    print("\n" + "-" * 65)
    print("Step 2: New question with summary as context")
    print("-" * 65)

    new_question = "The memory fix worked but now we see connection pool exhaustion. Is it related?"

    system_with_summary = f"You are an SRE assistant. Here is a summary of our previous conversation:\n\n{summary}\n\nUse this context to answer follow-up questions."

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=[
            {"role": "system", "content": system_with_summary},
            {"role": "user",   "content": new_question}
        ]
    )
    print(f"Question: {new_question}")
    print(f"\nResponse:\n{response.choices[0].message.content}")

    # Without context
    print("\n" + "-" * 65)
    print("Step 3: Same question WITHOUT summary (no context)")
    print("-" * 65)

    response_no_ctx = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=[
            {"role": "system", "content": "You are an SRE assistant."},
            {"role": "user",   "content": new_question}
        ]
    )
    print(f"Question: {new_question}")
    print(f"\nResponse (no context):\n{response_no_ctx.choices[0].message.content}")

    print("\n" + "=" * 65)
    print("Key Learning: Summarization compresses long conversations")
    print("into short context. You trade some detail for massive token savings.")
    print("=" * 65)

    print("\nTask 7 Complete!")
    print("Next: python3 demos/openai/task8_personalization.py")


if __name__ == "__main__":
    main()
