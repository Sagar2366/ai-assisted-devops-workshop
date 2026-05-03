#!/usr/bin/env python3
"""
Task 3: Model Parameters — Choose the Right Model for the Job
Understand parameters, quantization, and context length through the SRE lens.
AI-Assisted DevOps Workshop | Episode 2 | Sagar Utekar

Prerequisites:
  ollama serve &
  ollama pull qwen2.5-coder:7b
  pip install requests
"""

import requests
import json

OLLAMA_URL = "http://localhost:11434"


def get_model_info(model_name):
    """Query Ollama API for model metadata."""
    response = requests.post(
        f"{OLLAMA_URL}/api/show",
        json={"name": model_name}
    )
    if response.status_code == 200:
        return response.json()
    return None


def get_local_models():
    """List all locally available models."""
    response = requests.get(f"{OLLAMA_URL}/api/tags")
    if response.status_code == 200:
        return response.json().get("models", [])
    return []


def format_size(size_bytes):
    """Convert bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    print("=" * 65)
    print("Task 3: Model Parameters — Choose the Right Model")
    print("=" * 65)

    # List all local models
    print("\nExperiment 1: What Models Do I Have?")
    print("-" * 65)

    models = get_local_models()
    if not models:
        print("  No models found! Run: ollama pull qwen2.5-coder:7b")
        return

    print(f"  {'Model':<30} {'Size':<12} {'Modified'}")
    print(f"  {'-'*30} {'-'*12} {'-'*20}")
    for m in models:
        name = m.get("name", "unknown")
        size = format_size(m.get("size", 0))
        modified = m.get("modified_at", "unknown")[:19]
        print(f"  {name:<30} {size:<12} {modified}")

    # Deep dive into a model
    print("\n" + "=" * 65)
    print("Experiment 2: Deep Dive into Model Metadata")
    print("-" * 65)

    target_model = models[0]["name"] if models else "qwen2.5-coder:7b"
    info = get_model_info(target_model)

    if info:
        details = info.get("details", {})
        params = info.get("parameters", "")
        model_info = info.get("model_info", {})

        print(f"  Model:          {target_model}")
        print(f"  Family:         {details.get('family', 'unknown')}")
        print(f"  Parameter Size: {details.get('parameter_size', 'unknown')}")
        print(f"  Quantization:   {details.get('quantization_level', 'unknown')}")
        print(f"  Format:         {details.get('format', 'unknown')}")

        if model_info:
            for key, value in model_info.items():
                if "context_length" in key.lower():
                    print(f"  Context Length:  {value:,} tokens")
                elif "embedding_length" in key.lower():
                    print(f"  Embedding Size:  {value:,}")

    # SRE decision guide
    print("\n" + "=" * 65)
    print("Experiment 3: SRE Model Selection Guide")
    print("-" * 65)

    print("""
  Model Size  | RAM Needed | Best For (SRE Context)
  ------------|------------|----------------------------------------
  1-3B        | 2-4 GB     | Log classification, simple formatting
  7-8B        | 6-8 GB     | K8s triage, kubectl generation, alerting
  14B         | 12-16 GB   | Incident reasoning, multi-step diagnosis
  32-70B      | 32-64 GB   | Runbook generation, complex root cause

  Quantization:
  Q4_K_M  = 4-bit  → smallest, fastest, ~90% quality (use this)
  Q8_0    = 8-bit  → better quality, 2x size
  F16     = 16-bit → full quality, 4x size (need serious GPU)

  Rule of thumb: Start with 7B Q4. Move up ONLY when quality drops.
  For most SRE tasks (log triage, kubectl help), 7B is enough.""")

    print("\n" + "=" * 65)
    print("Key Learning: Model size ≠ always better.")
    print("  7B handles 80% of SRE tasks. Save 14B+ for complex reasoning.")
    print("  Quantization (Q4) gives you 90% quality at 25% the memory.")
    print("=" * 65)

    print("\nTask 3 Complete!")
    print("Next: python3 demos/ollama/task4_model_comparison.py")


if __name__ == "__main__":
    main()
