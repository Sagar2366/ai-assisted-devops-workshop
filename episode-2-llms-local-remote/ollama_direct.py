#!/usr/bin/env python3
"""
Episode 2: Query Local Ollama via HTTP API
AI-Assisted DevOps Workshop | Sagar Utekar

Prerequisites:
  brew install ollama
  ollama serve &
  ollama pull qwen2.5-coder:7b
"""
import requests

def ask_local_llm(prompt: str, model: str = "qwen2.5-coder:7b") -> str:
    """Query local Ollama - works offline, free, private."""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temp for DevOps — we want deterministic
                "num_ctx": 4096
            }
        }
    )
    return response.json()["response"]

# Test it
if __name__ == "__main__":
    result = ask_local_llm("""
As a Kubernetes expert, write a kubectl command to:
1. Find all pods in CrashLoopBackOff across all namespaces
2. Show their restart counts
""")
    print(result)
