#!/usr/bin/env python3
"""
Task 5: Conversation History — OpenAI GPT
Multi-turn conversation with memory. Maintain a messages list and
watch the AI remember context across turns.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export OPENAI_API_KEY="your-key-here"
  pip install openai
"""

from openai import OpenAI

def main():
    print("=" * 65)
    print("Task 5: Conversation History — OpenAI GPT")
    print("=" * 65)

    client = OpenAI()

    messages = [{"role": "system", "content": "You are a Kubernetes troubleshooting assistant. Be concise. Remember all context from our conversation."}]

    user_turns = [
        "My pod keeps crashing with OOMKilled status. The memory limit is 256Mi.",
        "I checked and the application uses about 300Mi at peak. What should I set the limit to?",
        "I updated the limit. Now how do I verify the pod is stable?"
    ]

    for i, user_msg in enumerate(user_turns, 1):
        print(f"\n--- Turn {i} ---")
        print(f"User: {user_msg}")
        print("-" * 65)

        messages.append({"role": "user", "content": user_msg})

        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=512,
            messages=messages
        )

        assistant_msg = response.choices[0].message.content
        print(f"Assistant: {assistant_msg}")

        messages.append({"role": "assistant", "content": assistant_msg})

    # Show the full conversation log
    print("\n" + "=" * 65)
    print("Full Conversation History Sent on Last Call:")
    print("-" * 65)
    for msg in messages:
        role = msg["role"].upper()
        content = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]
        print(f"  [{role}] {content}")

    print(f"\nTotal messages in history: {len(messages)}")

    print("\n" + "=" * 65)
    print("Key Learning: AI has no built-in memory.")
    print("YOU manage the conversation history by sending the full")
    print("messages list every turn. The model 'remembers' because")
    print("you resend everything. This is why context windows matter.")
    print("=" * 65)

    print("\nTask 5 Complete!")
    print("Next: python3 demos/openai/task6_context_window.py")


if __name__ == "__main__":
    main()
