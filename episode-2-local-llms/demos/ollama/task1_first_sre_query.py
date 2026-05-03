#!/usr/bin/env python3
"""
Task 1: First SRE Query — AI on Your Laptop
Feed a real K8s CrashLoopBackOff log to a local LLM. Zero cost, zero internet.
AI-Assisted DevOps Workshop | Episode 2 | Sagar Utekar

Prerequisites:
  brew install ollama
  ollama serve &
  ollama pull qwen2.5-coder:7b
  pip install requests
"""

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

K8S_LOG = """E0419 03:14:22.342891   1 pod_workers.go:1298] "Error syncing pod, skipping" err="failed to \\"StartContainer\\" for \\"api-server\\" with CrashLoopBackOff: \\"back-off 5m0s restarting failed container=api-server pod=api-server-7d4f8b6c5-x2k9m_production(uid)\\""
E0419 03:14:22.343012   1 pod_workers.go:1298] "Error syncing pod, skipping" err="container \\"api-server\\" in pod \\"api-server-7d4f8b6c5-x2k9m\\" is waiting to start: CrashLoopBackOff"
W0419 03:14:20.112233   1 oom_linux.go:67] "Got OOM event" pid=12345 containerName="/kubepods/burstable/pod-xyz/container-abc"
I0419 03:14:15.001234   1 kubelet.go:2183] "Container runtime status" status="running"
E0419 03:13:55.998765   1 kuberuntime_manager.go:999] "Container exited with non-zero code" containerName="api-server" exitCode=137"""


def ask_ollama(prompt, model="qwen2.5-coder:7b"):
    """Query local Ollama — works offline, free, private."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096
            }
        }
    )
    return response.json()["response"]


def main():
    print("=" * 65)
    print("Task 1: First SRE Query — AI on Your Laptop")
    print("=" * 65)

    print("\nExperiment 1: Analyze a Real K8s Log")
    print("-" * 65)

    prompt = f"""You are a Kubernetes SRE. Analyze this log and tell me:
1. What is the root cause?
2. What is the immediate fix?
3. What kubectl command should I run first?

Log:
{K8S_LOG}"""

    print("Sending K8s CrashLoopBackOff log to local LLM...")
    print(f"Model: qwen2.5-coder:7b (running on YOUR machine)\n")

    result = ask_ollama(prompt)
    print(f"Analysis:\n{result}")

    print("\n" + "=" * 65)
    print("Experiment 2: Quick kubectl Generation")
    print("-" * 65)

    kubectl_prompt = """As a Kubernetes expert, write a kubectl command to:
1. Find all pods in CrashLoopBackOff across all namespaces
2. Show their restart counts
Give me ONLY the command, no explanation."""

    result2 = ask_ollama(kubectl_prompt)
    print(f"Generated command:\n{result2}")

    print("\n" + "=" * 65)
    print("Key Learning: AI is running on YOUR laptop.")
    print("  - Zero cost (no API key, no billing)")
    print("  - Zero internet (works air-gapped)")
    print("  - Zero data leakage (logs never leave your machine)")
    print("  - This is the innermost ring — start here, move out only when needed.")
    print("=" * 65)

    print("\nTask 1 Complete!")
    print("Next: python3 demos/ollama/task2_cli_explorer.py")


if __name__ == "__main__":
    main()
