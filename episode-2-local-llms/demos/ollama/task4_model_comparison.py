#!/usr/bin/env python3
"""
Task 4: Model Comparison — Same Alert, Different Brains
Run the same SRE alert through multiple local models and compare quality + speed.
AI-Assisted DevOps Workshop | Episode 2 | Sagar Utekar

Prerequisites:
  ollama serve &
  ollama pull qwen2.5-coder:7b
  ollama pull llama3.1:8b
  pip install requests
"""

import requests
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

SRE_ALERT = """ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)

Analyze this alert. Give me:
1. Root cause (one sentence)
2. Immediate fix (kubectl command)
3. Long-term prevention"""


def ask_ollama(prompt, model):
    """Query Ollama and return response + timing."""
    start = time.time()
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_ctx": 4096}
        }
    )
    elapsed = time.time() - start
    data = response.json()
    return {
        "text": data.get("response", ""),
        "time": elapsed,
        "eval_count": data.get("eval_count", 0),
        "eval_duration": data.get("eval_duration", 0),
    }


def get_local_models():
    """Get list of locally available models."""
    response = requests.get("http://localhost:11434/api/tags")
    if response.status_code == 200:
        return [m["name"] for m in response.json().get("models", [])]
    return []


def main():
    print("=" * 65)
    print("Task 4: Model Comparison — Same Alert, Different Brains")
    print("=" * 65)

    models_to_test = ["qwen2.5-coder:7b", "llama3.1:8b"]

    available = get_local_models()
    models_to_test = [m for m in models_to_test if m in available]

    if not models_to_test:
        print("\nNo test models found! Pull at least one:")
        print("  ollama pull qwen2.5-coder:7b")
        print("  ollama pull llama3.1:8b")
        return

    if len(models_to_test) == 1:
        print(f"\nOnly {models_to_test[0]} available. For comparison, also pull:")
        for m in ["qwen2.5-coder:7b", "llama3.1:8b"]:
            if m not in available:
                print(f"  ollama pull {m}")
        print(f"\nRunning with {models_to_test[0]} only...\n")

    results = {}

    for model in models_to_test:
        print(f"\n{'=' * 60}")
        print(f"  MODEL: {model}")
        print(f"{'=' * 60}")
        print("  Generating response...")

        result = ask_ollama(SRE_ALERT, model)
        results[model] = result

        print(f"\n{result['text']}")
        print(f"\n  --- Stats ---")
        print(f"  Time:   {result['time']:.1f}s")
        if result['eval_count'] > 0:
            tokens_per_sec = result['eval_count'] / (result['eval_duration'] / 1e9) if result['eval_duration'] > 0 else 0
            print(f"  Tokens: {result['eval_count']}")
            print(f"  Speed:  {tokens_per_sec:.1f} tokens/sec")

    # Comparison table
    if len(results) > 1:
        print(f"\n{'=' * 65}")
        print("COMPARISON SUMMARY")
        print(f"{'=' * 65}")
        print(f"  {'Model':<25} {'Time':<10} {'Tokens':<10} {'Speed'}")
        print(f"  {'-'*25} {'-'*10} {'-'*10} {'-'*15}")
        for model, r in results.items():
            tokens = r['eval_count']
            if r['eval_duration'] > 0:
                speed = f"{tokens / (r['eval_duration'] / 1e9):.1f} tok/s"
            else:
                speed = "N/A"
            print(f"  {model:<25} {r['time']:<10.1f}s {tokens:<10} {speed}")

    print(f"\n{'=' * 65}")
    print("Key Learning: Same prompt, different models, different results.")
    print("  - Code-focused models (qwen2.5-coder) excel at kubectl generation")
    print("  - General models (llama3.1) give better reasoning and explanation")
    print("  - Speed varies — pick based on your latency requirements")
    print("=" * 65)

    print("\nTask 4 Complete!")
    print("Next: python3 demos/ollama/task5_ollama_api.py")


if __name__ == "__main__":
    main()
