#!/usr/bin/env python3
"""
Task 6: Context Window Management — OpenAI GPT
Sliding window truncation. When conversations get too long,
keep only the most recent N messages to stay within limits.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export OPENAI_API_KEY="your-key-here"
  pip install openai
"""

from openai import OpenAI


def main():
    print("=" * 65)
    print("Task 6: Context Window Management — OpenAI GPT")
    print("=" * 65)

    client = OpenAI()

    # Simulated long incident conversation
    incident_messages = [
        {"role": "system", "content": "You are an SRE assistant helping with an ongoing incident."},
        {"role": "user",   "content": "Alert: High CPU on web-server-01, usage at 95%."},
        {"role": "assistant", "content": "Check top processes with `top -bn1 | head -20`. Likely a runaway process."},
        {"role": "user",   "content": "It's the Java app, PID 4521, using 89% CPU."},
        {"role": "assistant", "content": "Take a thread dump: `jstack 4521 > /tmp/threaddump.txt`. Check for deadlocks."},
        {"role": "user",   "content": "Thread dump shows 200 threads blocked on database connections."},
        {"role": "assistant", "content": "Connection pool exhaustion. Check your DB connection pool settings and active queries."},
        {"role": "user",   "content": "Found a slow query taking 45 seconds. Should I kill it?"},
        {"role": "assistant", "content": "Yes, identify the query ID with `SHOW PROCESSLIST` and kill it. Then add an index."},
        {"role": "user",   "content": "Killed the query. CPU dropping. Now at 45%."},
        {"role": "assistant", "content": "Good progress. Monitor for 10 minutes. If stable, update the index to prevent recurrence."},
        {"role": "user",   "content": "It's been stable for 15 minutes. CPU at 12%. What should I document?"},
    ]

    print(f"Total messages in incident log: {len(incident_messages)}")

    # TODO 1: Define the sliding window size
    # We keep the system message + the last N user/assistant pairs
    # A small window forces the model to work with limited context
    WINDOW_SIZE = ___  # TODO: Use 6

    # Build the truncated message list
    system_msg = incident_messages[0]  # Always keep the system message
    conversation = incident_messages[1:]  # Everything after system

    # TODO 2: Slice the conversation to keep only the last WINDOW_SIZE messages
    # This is the sliding window — old messages are dropped
    truncated = ___  # TODO: Use conversation[-WINDOW_SIZE:]

    # Combine system message + truncated window
    windowed_messages = [system_msg] + truncated

    print(f"\nAfter windowing (keeping last {WINDOW_SIZE}):")
    print(f"  Messages sent to API: {len(windowed_messages)}")
    print(f"  Messages dropped: {len(incident_messages) - len(windowed_messages)}")

    print("\n--- Messages in Window ---")
    for msg in windowed_messages:
        role = msg["role"].upper()
        content = msg["content"][:70] + "..." if len(msg["content"]) > 70 else msg["content"]
        print(f"  [{role}] {content}")

    # Send the windowed messages
    print("\n" + "-" * 65)
    print("Response with Limited Context:")
    print("-" * 65)

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=windowed_messages
    )

    print(response.choices[0].message.content)

    # Show what's lost
    print("\n" + "-" * 65)
    print("What the Model LOST (dropped messages):")
    print("-" * 65)
    dropped = conversation[:-WINDOW_SIZE]
    for msg in dropped:
        role = msg["role"].upper()
        content = msg["content"][:70] + "..." if len(msg["content"]) > 70 else msg["content"]
        print(f"  [DROPPED {role}] {content}")

    print("\n" + "=" * 65)
    print("Key Learning: Sliding window is the simplest context strategy.")
    print("Pros: Easy, predictable token usage.")
    print("Cons: Loses early context (root cause details, initial symptoms).")
    print("Better strategy: Summarize old messages (see Task 7).")
    print("=" * 65)

    print("\nTask 6 Complete!")
    print("Next: python3 demos/openai/task7_summarization.py")


if __name__ == "__main__":
    main()
