#!/usr/bin/env python3
"""
Task 6: OpenAI-Compatible API — One-Line Swap, Local to Cloud
Use the OpenAI Python SDK with Ollama. Same code runs local or cloud.
AI-Assisted DevOps Workshop | Episode 2 | Sagar Utekar

Prerequisites:
  ollama serve &
  ollama pull qwen2.5-coder:7b
  pip install openai
"""

from openai import OpenAI


def main():
    print("=" * 65)
    print("Task 6: OpenAI-Compatible API — One-Line Swap")
    print("=" * 65)

    # Experiment 1: OpenAI SDK pointing at local Ollama
    print("\nExperiment 1: OpenAI SDK → Local Ollama")
    print("-" * 65)

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )

    response = client.chat.completions.create(
        model="qwen2.5-coder:7b",
        messages=[
            {"role": "system", "content": "You are a senior SRE. Be concise and actionable."},
            {"role": "user", "content": "Write a Prometheus alert rule for pod restart rate > 5 per minute."}
        ],
        temperature=0.1
    )

    print(f"Response:\n{response.choices[0].message.content}")

    # Experiment 2: Multi-turn conversation
    print("\n" + "=" * 65)
    print("Experiment 2: Multi-Turn Conversation")
    print("-" * 65)

    messages = [
        {"role": "system", "content": "You are an SRE. Remember details from the conversation. Be concise."},
        {"role": "user", "content": "Our monitoring stack is Prometheus + Grafana + Loki on EKS."}
    ]

    reply1 = client.chat.completions.create(
        model="qwen2.5-coder:7b", messages=messages, temperature=0.1
    )
    assistant_msg = reply1.choices[0].message.content
    print(f"Turn 1: {assistant_msg[:150]}...")

    messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": "Given our stack, what dashboards should I set up for SLO tracking?"})

    reply2 = client.chat.completions.create(
        model="qwen2.5-coder:7b", messages=messages, temperature=0.1
    )
    print(f"\nTurn 2: {reply2.choices[0].message.content[:200]}...")

    # Show the swap
    print("\n" + "=" * 65)
    print("THE ONE-LINE SWAP")
    print("-" * 65)
    print("""
  # LOCAL (free, private, air-gapped)
  client = OpenAI(
      base_url="http://localhost:11434/v1",  # ← Ollama
      api_key="ollama"
  )

  # CLOUD (better reasoning, 200K context)
  client = OpenAI(
      api_key=os.environ["OPENAI_API_KEY"]   # ← OpenAI cloud
  )

  # The rest of your code is IDENTICAL.
  # Same messages, same parameters, same response format.
""")

    print("=" * 65)
    print("Key Learning: Ollama speaks OpenAI's language.")
    print("  Any tool built for OpenAI now works with your local LLM.")
    print("  Develop locally (free) → deploy to cloud (when you need to).")
    print("  This is why the OpenAI-compatible API matters for production.")
    print("=" * 65)

    print("\nTask 6 Complete!")
    print("Next: python3 demos/ollama/task7_custom_modelfile.py")


if __name__ == "__main__":
    main()
