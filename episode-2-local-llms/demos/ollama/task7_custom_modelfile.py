#!/usr/bin/env python3
"""
Task 7: Custom Modelfile — Package SRE Expertise into a Model
Create a custom Ollama model with baked-in SRE persona and settings.
AI-Assisted DevOps Workshop | Episode 2 | Sagar Utekar

Prerequisites:
  ollama serve &
  ollama pull qwen2.5-coder:7b
  pip install requests
"""

import subprocess
import requests
import os
import tempfile

OLLAMA_URL = "http://localhost:11434/api/generate"

MODELFILE_CONTENT = """FROM qwen2.5-coder:7b

PARAMETER temperature 0.1
PARAMETER num_ctx 4096

SYSTEM \"\"\"You are an expert SRE assistant with deep knowledge of:
- Kubernetes (EKS, GKE, AKS, kind, minikube)
- Monitoring (Prometheus, Grafana, Loki, Datadog)
- CI/CD (GitHub Actions, ArgoCD, Jenkins)
- Infrastructure (Terraform, Helm, Kustomize)

Rules:
1. Always give kubectl/helm commands, not general advice
2. Start with the most likely root cause
3. Include rollback commands when suggesting changes
4. Flag any destructive operations with a WARNING
5. Be concise — SREs are in incident mode, not reading essays
\"\"\"
"""

SRE_ALERT = """ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)

Give me a remediation plan."""


def ask_ollama(prompt, model):
    """Query a model via Ollama API."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_ctx": 4096}
        }
    )
    return response.json().get("response", "")


def main():
    print("=" * 65)
    print("Task 7: Custom Modelfile — Package SRE Expertise")
    print("=" * 65)

    # Step 1: Show the Modelfile
    print("\nStep 1: The Modelfile")
    print("-" * 65)
    print(MODELFILE_CONTENT)

    # Step 2: Create the Modelfile and build
    print("Step 2: Building Custom Model")
    print("-" * 65)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    modelfile_path = os.path.join(script_dir, "Modelfile.sre-assistant")

    with open(modelfile_path, "w") as f:
        f.write(MODELFILE_CONTENT)
    print(f"  Wrote Modelfile to: {modelfile_path}")

    result = subprocess.run(
        f"ollama create sre-assistant -f {modelfile_path}",
        shell=True, capture_output=True, text=True, timeout=60
    )
    if result.returncode == 0:
        print("  Model 'sre-assistant' created successfully!")
    else:
        print(f"  Error: {result.stderr}")
        return

    # Step 3: Compare raw vs custom
    print("\n" + "=" * 65)
    print("Step 3: Compare — Raw Model vs Custom SRE Model")
    print("=" * 65)

    print("\n--- RAW MODEL (qwen2.5-coder:7b) ---")
    raw_response = ask_ollama(SRE_ALERT, "qwen2.5-coder:7b")
    print(raw_response[:500])

    print("\n--- CUSTOM MODEL (sre-assistant) ---")
    custom_response = ask_ollama(SRE_ALERT, "sre-assistant")
    print(custom_response[:500])

    # Step 4: Verify it's in the model list
    print("\n" + "=" * 65)
    print("Step 4: Verify — Model is Now in Your Library")
    print("-" * 65)

    result = subprocess.run(
        "ollama list | grep sre-assistant",
        shell=True, capture_output=True, text=True
    )
    if result.stdout:
        print(f"  {result.stdout.strip()}")
    print("\n  Anyone on your team can now run: ollama run sre-assistant")

    print("\n" + "=" * 65)
    print("Key Learning: A Modelfile packages expertise into a reusable model.")
    print("  - Bake in your SRE system prompt, temperature, context length")
    print("  - Share with your team: ollama create + ollama push")
    print("  - Like a Dockerfile for AI — reproducible, versioned, portable")
    print("=" * 65)

    print("\nTask 7 Complete!")
    print("Next: python3 demos/ollama/task8_open_webui.py")


if __name__ == "__main__":
    main()
