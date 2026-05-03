#!/usr/bin/env python3
"""
Task 2: CLI Explorer — Manage Models Like Containers
Ollama CLI mirrors Docker. If you know Docker, you already know Ollama.
AI-Assisted DevOps Workshop | Episode 2 | Sagar Utekar

Prerequisites:
  brew install ollama
  ollama serve &
  ollama pull qwen2.5-coder:7b
"""

import subprocess
import sys


def run_cmd(cmd, description):
    """Run a shell command and print its output."""
    print(f"\n{'=' * 60}")
    print(f"  {description}")
    print(f"  $ {cmd}")
    print("=" * 60)
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=15
        )
        output = result.stdout.strip() or result.stderr.strip()
        if output:
            print(output)
        else:
            print("(no output)")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("  (command timed out)")
        return False


def main():
    print("=" * 65)
    print("Task 2: CLI Explorer — Manage Models Like Containers")
    print("=" * 65)

    print("\nDocker vs Ollama — you already know these commands:")
    print("-" * 65)
    print(f"  {'Docker':<30} {'Ollama':<30}")
    print(f"  {'docker pull nginx':<30} {'ollama pull llama3.1:8b':<30}")
    print(f"  {'docker images':<30} {'ollama list':<30}")
    print(f"  {'docker ps':<30} {'ollama ps':<30}")
    print(f"  {'docker rmi nginx':<30} {'ollama rm llama3.1:8b':<30}")
    print(f"  {'docker inspect nginx':<30} {'ollama show llama3.1:8b':<30}")

    # List local models
    run_cmd("ollama list", "LIST — What models are on my machine?  (docker images)")

    # Show model details
    run_cmd(
        "ollama show qwen2.5-coder:7b --modelfile 2>/dev/null || ollama show qwen2.5-coder:7b",
        "SHOW — Inspect model metadata  (docker inspect)"
    )

    # Running models
    run_cmd("ollama ps", "PS — What models are currently loaded?  (docker ps)")

    # Version
    run_cmd("ollama --version", "VERSION — What Ollama version am I running?")

    print("\n" + "=" * 65)
    print("Key Learning: If you know Docker, you know Ollama.")
    print("  pull = download model  |  list = local models  |  ps = running models")
    print("  show = inspect metadata  |  rm = delete model  |  run = interactive chat")
    print("  Models are like container images — pull once, run many times.")
    print("=" * 65)

    print("\nTask 2 Complete!")
    print("Next: python3 demos/ollama/task3_model_parameters.py")


if __name__ == "__main__":
    main()
