#!/usr/bin/env python3
"""
Episode 2: Ollama with OpenAI-Compatible API
AI-Assisted DevOps Workshop | Sagar Utekar

Any tool that works with OpenAI works with Ollama — swap with one line.

Prerequisites:
  pip install openai
  ollama serve &
  ollama pull qwen2.5-coder:7b
"""
from openai import OpenAI

# Point OpenAI client at local Ollama
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Ollama doesn't need a real key
)

response = client.chat.completions.create(
    model="qwen2.5-coder:7b",
    messages=[
        {"role": "system", "content": "You are an SRE. Be concise."},
        {"role": "user", "content": "Write a Prometheus alert rule for pod restart rate > 5 per minute"}
    ],
    temperature=0.1
)

print(response.choices[0].message.content)
