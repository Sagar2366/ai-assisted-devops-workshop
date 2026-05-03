#!/usr/bin/env python3
"""
Task 10: Docker Model Runner — Local LLMs Without Leaving Docker
Use Docker Desktop's built-in Model Runner with the OpenAI SDK.
AI-Assisted DevOps Workshop | Episode 2 | Sagar Utekar

Prerequisites:
  Docker Desktop 4.40+ with Model Runner enabled
  docker model pull ai/llama3.2
  pip install openai requests
"""

import subprocess
import sys
import time
import json

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: pip install openai")
    sys.exit(1)

DOCKER_MODEL_RUNNER_BASE = "http://localhost:12434/engines/v1"
OLLAMA_BASE = "http://localhost:11434/v1"
MODEL_DOCKER = "ai/llama3.2"
MODEL_OLLAMA = "qwen2.5-coder:7b"

SRE_PROMPT = "A Kubernetes pod is in CrashLoopBackOff with exit code 137 (OOMKilled). Give me 3 kubectl commands to investigate and the most likely root cause."


def check_docker_model_runner():
    """Verify Docker Model Runner is enabled and responding."""
    print("\nStep 1: Checking Docker Model Runner...")
    print("-" * 65)

    try:
        status = subprocess.run(
            ["docker", "model", "status"],
            capture_output=True, text=True, timeout=10
        )
        if status.returncode == 0:
            print(f"Status: {status.stdout.strip()}")
        else:
            print("WARNING: 'docker model status' failed — Model Runner may not be running.")
            print("Enable: Docker Desktop → Settings → Model Runner → Enable")
            print("Also enable: 'Host-side TCP support' on port 12434")
            print(f"stderr: {status.stderr.strip()}")
            return False

        result = subprocess.run(
            ["docker", "model", "list"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            print("ERROR: 'docker model list' failed.")
            return False
        print(f"\nAvailable models:\n{result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("ERROR: Docker CLI not found. Install Docker Desktop 4.40+.")
        return False
    except subprocess.TimeoutExpired:
        print("ERROR: Docker command timed out.")
        return False


def experiment_1_basic_query():
    """Basic SRE query via Docker Model Runner."""
    print("\n" + "=" * 65)
    print("Experiment 1: Basic SRE Query via Docker Model Runner")
    print("-" * 65)

    client = OpenAI(
        base_url=DOCKER_MODEL_RUNNER_BASE,
        api_key="not-needed"
    )

    print(f"Model: {MODEL_DOCKER}")
    print(f"Endpoint: {DOCKER_MODEL_RUNNER_BASE}")
    print(f"Prompt: {SRE_PROMPT[:80]}...")
    print()

    start = time.time()
    response = client.chat.completions.create(
        model=MODEL_DOCKER,
        messages=[
            {"role": "system", "content": "You are a senior SRE. Be concise and actionable."},
            {"role": "user", "content": SRE_PROMPT}
        ],
        temperature=0.1
    )
    elapsed = time.time() - start

    print(f"Response ({elapsed:.1f}s):")
    print(response.choices[0].message.content)

    if response.usage:
        print(f"\nTokens: {response.usage.prompt_tokens} in / {response.usage.completion_tokens} out")


def experiment_2_streaming():
    """Streaming responses from Docker Model Runner."""
    print("\n" + "=" * 65)
    print("Experiment 2: Streaming Response")
    print("-" * 65)

    client = OpenAI(
        base_url=DOCKER_MODEL_RUNNER_BASE,
        api_key="not-needed"
    )

    print("Streaming: ", end="", flush=True)
    stream = client.chat.completions.create(
        model=MODEL_DOCKER,
        messages=[
            {"role": "system", "content": "You are an SRE. Be concise."},
            {"role": "user", "content": "Write a 3-line Prometheus alert rule for high memory usage."}
        ],
        temperature=0.1,
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()


def experiment_3_three_way_swap():
    """Demonstrate the Ollama → Docker Model Runner swap pattern."""
    print("\n" + "=" * 65)
    print("Experiment 3: Three-Way Swap (Ollama vs Docker Model Runner)")
    print("-" * 65)

    prompt = "What does exit code 137 mean in a Kubernetes pod? One sentence."

    backends = [
        ("Ollama", OLLAMA_BASE, MODEL_OLLAMA, "ollama"),
        ("Docker Model Runner", DOCKER_MODEL_RUNNER_BASE, MODEL_DOCKER, "not-needed"),
    ]

    for name, base_url, model, api_key in backends:
        print(f"\n[{name}]  base_url={base_url}")
        try:
            client = OpenAI(base_url=base_url, api_key=api_key)
            start = time.time()
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an SRE. One sentence max."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            elapsed = time.time() - start
            print(f"  Model: {model}")
            print(f"  Response ({elapsed:.1f}s): {response.choices[0].message.content}")
        except Exception as e:
            print(f"  Skipped: {e}")

    print("\nThe swap pattern:")
    print("  Ollama:  base_url='http://localhost:11434/v1'")
    print("  Docker:  base_url='http://localhost:12434/engines/v1'")
    print("  Cloud:   base_url='https://api.openai.com/v1'")
    print("  Same OpenAI SDK. Same code. Different engine.")


def experiment_4_json_mode():
    """Structured JSON output from Docker Model Runner."""
    print("\n" + "=" * 65)
    print("Experiment 4: JSON Mode — Structured Output")
    print("-" * 65)

    client = OpenAI(
        base_url=DOCKER_MODEL_RUNNER_BASE,
        api_key="not-needed"
    )

    response = client.chat.completions.create(
        model=MODEL_DOCKER,
        messages=[
            {"role": "system", "content": "You are an SRE assistant. Respond in JSON only."},
            {"role": "user", "content": """Analyze this alert and respond as JSON with keys: severity, service, root_cause, action.

ALERT: Pod payment-service-7f8b9c6d4-x2k9p OOMKilled
Container memory limit: 256Mi
Peak usage before kill: 254Mi
Restart count: 4"""}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content
    print(f"Raw response:\n{raw}")

    try:
        parsed = json.loads(raw)
        print(f"\nParsed JSON:")
        for k, v in parsed.items():
            print(f"  {k}: {v}")
    except json.JSONDecodeError:
        print("\nNote: Model returned non-JSON. Smaller models may not always follow JSON mode.")


def main():
    print("=" * 65)
    print("Task 10: Docker Model Runner — Local LLMs via Docker Desktop")
    print("=" * 65)

    available = check_docker_model_runner()
    if not available:
        print("\nDocker Model Runner not available. Skipping experiments.")
        print("Enable: Docker Desktop → Settings → Model Runner → Enable")
        print("Then:   docker model pull ai/llama3.2")
        sys.exit(1)

    experiment_1_basic_query()
    experiment_2_streaming()
    experiment_3_three_way_swap()
    experiment_4_json_mode()

    print("\n" + "=" * 65)
    print("Key Learning: Docker Desktop IS your AI runtime.")
    print("  Same OpenAI SDK, same code — just a different base_url.")
    print("  Ollama:  localhost:11434/v1")
    print("  Docker:  localhost:12434/engines/v1")
    print("  Cloud:   api.openai.com/v1")
    print("=" * 65)
    print("\nTask 10 Complete!")
    print("Episode 2 fully complete — all local LLM paths covered.")
    print("Next: Episode 3 — Claude API Deep Dive")


if __name__ == "__main__":
    main()
