#!/usr/bin/env python3
"""
Task 8: Open Web UI — ChatGPT for Your Team, Free & Private
Launch a ChatGPT-like interface connected to your local Ollama models.
AI-Assisted DevOps Workshop | Episode 2 | Sagar Utekar

Prerequisites:
  ollama serve &
  docker installed and running
  pip install requests
"""

import subprocess
import requests
import time
import sys

OPEN_WEBUI_PORT = 3000
OPEN_WEBUI_URL = f"http://localhost:{OPEN_WEBUI_PORT}"
CONTAINER_NAME = "open-webui-workshop"


def check_docker():
    """Verify Docker is running."""
    result = subprocess.run(
        "docker info", shell=True, capture_output=True, text=True
    )
    return result.returncode == 0


def check_ollama():
    """Verify Ollama is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def check_container_exists():
    """Check if our container already exists."""
    result = subprocess.run(
        f"docker ps -a --filter name={CONTAINER_NAME} --format '{{{{.Status}}}}'",
        shell=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def launch_open_webui():
    """Launch Open Web UI container."""
    status = check_container_exists()

    if status and "Up" in status:
        print(f"  Container '{CONTAINER_NAME}' is already running!")
        return True

    if status:
        print(f"  Removing stopped container '{CONTAINER_NAME}'...")
        subprocess.run(
            f"docker rm {CONTAINER_NAME}", shell=True, capture_output=True
        )

    print("  Launching Open Web UI...")
    print(f"  $ docker run -d -p {OPEN_WEBUI_PORT}:8080 \\")
    print(f"      --add-host=host.docker.internal:host-gateway \\")
    print(f"      -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \\")
    print(f"      --name {CONTAINER_NAME} \\")
    print(f"      ghcr.io/open-webui/open-webui:main")
    print()

    result = subprocess.run(
        f"docker run -d -p {OPEN_WEBUI_PORT}:8080 "
        f"--add-host=host.docker.internal:host-gateway "
        f"-e OLLAMA_BASE_URL=http://host.docker.internal:11434 "
        f"--name {CONTAINER_NAME} "
        f"ghcr.io/open-webui/open-webui:main",
        shell=True, capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"  Error: {result.stderr.strip()}")
        return False

    print(f"  Container started: {result.stdout.strip()[:12]}")
    return True


def wait_for_webui(timeout=60):
    """Wait for Open Web UI to become ready."""
    print(f"\n  Waiting for UI to start (up to {timeout}s)...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(OPEN_WEBUI_URL, timeout=3)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(3)
        elapsed = int(time.time() - start)
        print(f"  ... {elapsed}s", end="\r")
    return False


def verify_models_detected():
    """Check if Open Web UI can see Ollama models."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m["name"] for m in models]
    except requests.ConnectionError:
        pass
    return []


def main():
    print("=" * 65)
    print("Task 8: Open Web UI — ChatGPT for Your Team")
    print("=" * 65)

    # Pre-flight checks
    print("\nPre-Flight Checks")
    print("-" * 65)

    docker_ok = check_docker()
    print(f"  Docker:  {'[OK]' if docker_ok else '[MISSING] Install Docker first'}")

    ollama_ok = check_ollama()
    print(f"  Ollama:  {'[OK]' if ollama_ok else '[MISSING] Run: ollama serve &'}")

    if not docker_ok:
        print("\n  Docker is required for Open Web UI.")
        print("  Install: https://docs.docker.com/get-docker/")
        return

    if not ollama_ok:
        print("\n  Ollama must be running. Start it with: ollama serve &")
        return

    # Show available models
    models = verify_models_detected()
    print(f"  Models:  {len(models)} available — {', '.join(models[:5])}")

    # Launch
    print("\n" + "=" * 65)
    print("Launching Open Web UI")
    print("-" * 65)

    if not launch_open_webui():
        return

    if wait_for_webui():
        print(f"\n  [OK] Open Web UI is ready!")
        print(f"\n  Open in your browser: {OPEN_WEBUI_URL}")
        print(f"  First visit: create an admin account (stays local)")
        print(f"  Select any model from the dropdown — they're your Ollama models")
    else:
        print(f"\n  UI is still starting. Check: {OPEN_WEBUI_URL}")
        print(f"  Container logs: docker logs {CONTAINER_NAME}")

    # Cleanup instructions
    print(f"\n" + "=" * 65)
    print("Cleanup (when done)")
    print("-" * 65)
    print(f"  docker stop {CONTAINER_NAME}")
    print(f"  docker rm {CONTAINER_NAME}")

    print("\n" + "=" * 65)
    print("Key Learning: ChatGPT-like interface, zero cost, fully private.")
    print("  - Runs on your machine or your team's server")
    print("  - All your Ollama models appear automatically")
    print("  - No data ever leaves your network")
    print("  - Share with your team — one Docker command")
    print("=" * 65)

    print("\nTask 8 Complete!")
    print("All Ollama tasks complete!")
    print("Next episode part: Multi-Provider Showdown, Prompt Caching, Unified Client")


if __name__ == "__main__":
    main()
