#!/usr/bin/env python3
"""
Task 5: Ollama API Deep Dive — Automate Local LLMs
Direct HTTP API: /api/generate, /api/chat, system prompts, streaming, JSON mode.
AI-Assisted DevOps Workshop | Episode 2 | Sagar Utekar

Prerequisites:
  ollama serve &
  ollama pull qwen2.5-coder:7b
  pip install requests
"""

import requests
import json
import sys

OLLAMA_BASE = "http://localhost:11434"


def experiment_1_generate():
    """Basic /api/generate — single prompt, single response."""
    print("Experiment 1: /api/generate — Simple Prompt")
    print("-" * 65)

    response = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json={
            "model": "qwen2.5-coder:7b",
            "prompt": "Write a Prometheus alert rule that fires when pod restart rate exceeds 5 per minute. Give ONLY the YAML.",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096
            }
        }
    )

    result = response.json()
    print(result["response"])
    print(f"\n  Tokens generated: {result.get('eval_count', 'N/A')}")


def experiment_2_chat():
    """Multi-turn /api/chat — conversation with system prompt."""
    print("\nExperiment 2: /api/chat — Multi-Turn with System Prompt")
    print("-" * 65)

    messages = [
        {"role": "system", "content": "You are a senior SRE. Be concise. Give kubectl commands, not general advice."},
        {"role": "user", "content": "A pod named payment-service in production is in CrashLoopBackOff. What do I check first?"}
    ]

    response = requests.post(
        f"{OLLAMA_BASE}/api/chat",
        json={
            "model": "qwen2.5-coder:7b",
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1}
        }
    )

    result = response.json()
    assistant_reply = result["message"]["content"]
    print(f"Turn 1: {assistant_reply}")

    messages.append({"role": "assistant", "content": assistant_reply})
    messages.append({"role": "user", "content": "The logs show 'connection refused to postgres:5432'. Now what?"})

    response2 = requests.post(
        f"{OLLAMA_BASE}/api/chat",
        json={
            "model": "qwen2.5-coder:7b",
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1}
        }
    )

    result2 = response2.json()
    print(f"\nTurn 2: {result2['message']['content']}")


def experiment_3_streaming():
    """Streaming responses — real-time output like ChatGPT."""
    print("\nExperiment 3: Streaming — Real-Time Output")
    print("-" * 65)
    print("Response: ", end="", flush=True)

    response = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json={
            "model": "qwen2.5-coder:7b",
            "prompt": "Explain what happens when a Kubernetes pod gets OOMKilled, in 3 sentences.",
            "stream": True,
            "options": {"temperature": 0.1}
        },
        stream=True
    )

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            token = data.get("response", "")
            print(token, end="", flush=True)
            if data.get("done", False):
                break

    print("\n")


def experiment_4_json_mode():
    """Structured JSON output — parse K8s status as data."""
    print("Experiment 4: JSON Mode — Structured Output")
    print("-" * 65)

    response = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json={
            "model": "qwen2.5-coder:7b",
            "prompt": """Analyze these pods and return a JSON object with keys: "healthy" (list of healthy pod names), "unhealthy" (list of objects with "name", "issue", "action"):

NAME                          READY   STATUS             RESTARTS   AGE
prometheus-server-0            1/1     Running            0          7d
grafana-6b8c4d9f-n3k8p        1/1     Running            0          7d
alertmanager-0                 0/1     CrashLoopBackOff   5          2d
node-exporter-x4m9v            1/1     Running            0          7d
loki-0                         0/1     ImagePullBackOff   0          1d

Return ONLY valid JSON, no explanation.""",
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.0}
        }
    )

    result = response.json()
    raw = result["response"]

    try:
        parsed = json.loads(raw)
        print("  Parsed JSON:")
        print(f"  {json.dumps(parsed, indent=2)}")
    except json.JSONDecodeError:
        print(f"  Raw response (not valid JSON):\n  {raw}")


def main():
    print("=" * 65)
    print("Task 5: Ollama API Deep Dive — Automate Local LLMs")
    print("=" * 65)

    experiment_1_generate()
    experiment_2_chat()
    experiment_3_streaming()
    experiment_4_json_mode()

    print("=" * 65)
    print("Key Learning: Ollama exposes two APIs:")
    print("  /api/generate — single prompt in, single response out")
    print("  /api/chat     — multi-turn with system/user/assistant messages")
    print("  Both support streaming, temperature, JSON mode.")
    print("  This is how you automate local LLMs in scripts and pipelines.")
    print("=" * 65)

    print("\nTask 5 Complete!")
    print("Next: python3 demos/ollama/task6_openai_compat.py")


if __name__ == "__main__":
    main()
