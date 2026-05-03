#!/usr/bin/env python3
"""
Verify Ollama Setup — Pre-Workshop Environment Check
Confirms Ollama is installed, running, and models are pulled.
AI-Assisted DevOps Workshop | Episode 2 | Sagar Utekar

Run this BEFORE the workshop:
  python3 demos/ollama/verify_ollama.py
"""

import subprocess
import requests
import shutil
import sys

REQUIRED_MODELS = ["qwen2.5-coder:7b"]
OPTIONAL_MODELS = ["llama3.1:8b"]


def check_ollama_installed():
    """Check if ollama binary is on PATH."""
    return shutil.which("ollama") is not None


def check_ollama_running():
    """Check if Ollama server is responding."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def get_local_models():
    """Get list of locally available models."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            return [m["name"] for m in response.json().get("models", [])]
    except requests.ConnectionError:
        pass
    return []


def check_docker():
    """Check if Docker is available (needed for Task 8)."""
    result = subprocess.run(
        "docker info", shell=True, capture_output=True, text=True
    )
    return result.returncode == 0


def main():
    print("=" * 65)
    print("AI-Assisted DevOps Workshop — Episode 2 Environment Check")
    print("=" * 65)

    all_ok = True

    # 1. Ollama installed
    installed = check_ollama_installed()
    print(f"\n  Ollama installed:  {'[OK]' if installed else '[MISSING]'}")
    if not installed:
        print("    Install: https://ollama.com/download")
        print("    macOS:   brew install ollama")
        print("    Linux:   curl -fsSL https://ollama.com/install.sh | sh")
        all_ok = False

    # 2. Ollama running
    running = check_ollama_running()
    print(f"  Ollama running:   {'[OK]' if running else '[NOT RUNNING]'}")
    if not running:
        print("    Start with: ollama serve &")
        all_ok = False

    # 3. Required models
    if running:
        local_models = get_local_models()

        for model in REQUIRED_MODELS:
            found = model in local_models
            print(f"  Model {model}:  {'[OK]' if found else '[MISSING]'}")
            if not found:
                print(f"    Pull with: ollama pull {model}")
                all_ok = False

        for model in OPTIONAL_MODELS:
            found = model in local_models
            status = "[OK]" if found else "[OPTIONAL]"
            print(f"  Model {model}:    {status}")
            if not found:
                print(f"    For Task 4 comparison: ollama pull {model}")

        print(f"\n  Total models available: {len(local_models)}")
        if local_models:
            print(f"    {', '.join(local_models[:8])}")

    # 4. Python packages
    packages_ok = True
    for pkg in ["requests", "openai"]:
        try:
            __import__(pkg)
            print(f"  Python {pkg}:  [OK]")
        except ImportError:
            print(f"  Python {pkg}:  [MISSING]  pip install {pkg}")
            packages_ok = False
            all_ok = False

    # 5. Docker (optional — Task 8)
    docker_ok = check_docker()
    print(f"  Docker (Task 8):  {'[OK]' if docker_ok else '[OPTIONAL] Install for Task 8'}")

    # Summary
    print("\n" + "=" * 65)
    if all_ok:
        print("ALL CHECKS PASSED — Ready for Episode 2!")
    else:
        print("SOME CHECKS FAILED — Fix the items above before starting.")
    print("=" * 65)

    print("\nQuick Setup (if needed):")
    print("  ollama serve &")
    print("  ollama pull qwen2.5-coder:7b")
    print("  ollama pull llama3.1:8b")
    print("  pip install requests openai")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
