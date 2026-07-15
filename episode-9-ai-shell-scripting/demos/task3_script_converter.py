#!/usr/bin/env python3
"""
Task 3: AI Script Converter
Convert scripts between languages — bash to Python, Python to Go.
AI-Assisted DevOps Workshop | Episode 9 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic


def main():
    print("=" * 65)
    print("Task 3: AI Script Converter")
    print("Bash → Python → Go — Idiomatic Conversion")
    print("=" * 65)

    client = anthropic.Anthropic()

    system_prompt = """You are a polyglot script converter specializing in DevOps languages.

When converting a script:
1. Preserve the EXACT same logic and behavior
2. Use IDIOMATIC patterns for the target language (not literal translation)
3. Add proper error handling native to the target language
4. Keep all comments, translating them to match the new code
5. Add type hints (Python) or type declarations (Go) where appropriate
6. Use standard libraries — no unnecessary third-party dependencies

Output ONLY the converted script with a brief comment header noting the original language."""

    # Experiment 1: Bash → Python (K8s pod monitor)
    print("\nExperiment 1: Bash → Python (K8s Pod CPU Monitor)")
    print("-" * 65)

    bash_script = '''#!/bin/bash
set -euo pipefail

# Monitor pod CPU usage and alert on high consumers
NAMESPACE="${1:-default}"
THRESHOLD="${2:-80}"
LOG_FILE="/var/log/pod-cpu-monitor.log"

log() {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] $*" | tee -a "$LOG_FILE"
}

log "Starting CPU check for namespace: $NAMESPACE (threshold: ${THRESHOLD}m)"

alert_count=0
for pod in $(kubectl get pods -n "$NAMESPACE" --no-headers -o custom-columns=":metadata.name"); do
    cpu=$(kubectl top pod "$pod" -n "$NAMESPACE" --no-headers 2>/dev/null | awk '{print $2}' | tr -d 'm')
    if [ -n "$cpu" ] && [ "$cpu" -gt "$THRESHOLD" ]; then
        log "[ALERT] Pod $pod using ${cpu}m CPU (threshold: ${THRESHOLD}m)"
        alert_count=$((alert_count + 1))
    fi
done

log "Check complete. Alerts triggered: $alert_count"
exit $((alert_count > 0 ? 1 : 0))
'''

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Convert this bash script to Python with type hints, argparse, and proper subprocess handling:\n\n```bash\n{bash_script}\n```"}
        ]
    )
    print(message.content[0].text)

    # Experiment 2: Bash → Go (health checker)
    print("\n" + "-" * 65)
    print("Experiment 2: Bash → Go (Health Checker)")
    print("-" * 65)

    bash_health = '''#!/bin/bash
set -euo pipefail

# HTTP health checker with retry logic
ENDPOINTS="http://api:8080/health http://web:3000/health http://worker:9090/metrics"
MAX_RETRIES=3
TIMEOUT=5

for endpoint in $ENDPOINTS; do
    retries=0
    while [ $retries -lt $MAX_RETRIES ]; do
        status=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$endpoint" 2>/dev/null || echo "000")
        if [ "$status" = "200" ]; then
            echo "[OK] $endpoint (status: $status)"
            break
        fi
        retries=$((retries + 1))
        echo "[RETRY $retries/$MAX_RETRIES] $endpoint (status: $status)"
        sleep 2
    done
    if [ $retries -eq $MAX_RETRIES ]; then
        echo "[FAIL] $endpoint unreachable after $MAX_RETRIES attempts"
    fi
done
'''

    message2 = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Convert this bash script to Go with proper error handling, goroutines for parallel checks, and structured output:\n\n```bash\n{bash_health}\n```"}
        ]
    )
    print(message2.content[0].text)

    # Experiment 3: Python → Bash (quick conversion)
    print("\n" + "-" * 65)
    print("Experiment 3: Python → Bash (Container Cleanup)")
    print("-" * 65)

    python_script = '''#!/usr/bin/env python3
"""Remove stopped containers and dangling images."""
import subprocess
import sys
from datetime import datetime

def run(cmd: str) -> tuple[str, int]:
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def main():
    print(f"[{datetime.now().isoformat()}] Starting container cleanup")

    # Remove stopped containers
    stdout, rc = run("docker ps -aq --filter status=exited")
    if stdout:
        containers = stdout.split("\\n")
        print(f"Removing {len(containers)} stopped containers...")
        for cid in containers:
            run(f"docker rm {cid}")

    # Remove dangling images
    stdout, rc = run("docker images -q --filter dangling=true")
    if stdout:
        images = stdout.split("\\n")
        print(f"Removing {len(images)} dangling images...")
        for img in images:
            run(f"docker rmi {img}")

    print("Cleanup complete")

if __name__ == "__main__":
    main()
'''

    message3 = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Convert this Python script to bash:\n\n```python\n{python_script}\n```"}
        ]
    )
    print(message3.content[0].text)

    print("\n" + "=" * 65)
    print("Key Learning: AI conversion understands INTENT, not just syntax.")
    print("It uses idiomatic patterns (argparse, goroutines, set -euo pipefail)")
    print("native to each target language — not naive line-by-line translation.")
    print("=" * 65)

    print("\nTask 3 Complete!")
    print("Next: python3 demos/task4_script_explainer.py")


if __name__ == "__main__":
    main()
