#!/usr/bin/env python3
"""
Task 1: AI Script Generator
Generate production-ready shell scripts from natural language descriptions.
AI-Assisted DevOps Workshop | Episode 9 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic


def main():
    print("=" * 65)
    print("Task 1: AI Script Generator")
    print("Natural Language → Production Shell Scripts")
    print("=" * 65)

    client = anthropic.Anthropic()

    system_prompt = """You are a senior SRE who writes production-grade shell scripts.

Every script you generate MUST include:
1. #!/bin/bash and set -euo pipefail
2. A header comment with description, usage, and prerequisites
3. Logging function with timestamps
4. Input validation for all arguments
5. Cleanup trap (trap cleanup EXIT)
6. Error handling with meaningful exit codes
7. Comments explaining non-obvious logic

Output ONLY the script — no explanation before or after."""

    # Experiment 1: Disk monitoring script
    print("\nExperiment 1: Disk Usage Monitor with Slack Alerting")
    print("-" * 65)

    request1 = """Monitor disk usage on all mounted filesystems.
If any partition exceeds 85%, send an alert to a Slack webhook URL (passed as argument).
Log all checks to /var/log/disk-monitor.log with timestamps.
Include the hostname, partition, usage percentage, and available space in the alert."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Generate a bash script:\n\n{request1}"}
        ]
    )
    print(message.content[0].text)

    # Experiment 2: Log rotation script
    print("\n" + "-" * 65)
    print("Experiment 2: Log Rotation Script")
    print("-" * 65)

    request2 = """Rotate application logs in /var/log/myapp/.
- Compress logs older than 1 day with gzip
- Delete compressed logs older than 30 days
- Ensure total log directory size never exceeds 5GB (delete oldest first)
- Send a summary report to stdout with counts of rotated/deleted files"""

    message2 = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Generate a bash script:\n\n{request2}"}
        ]
    )
    print(message2.content[0].text)

    # Experiment 3: Kubernetes health check
    print("\n" + "-" * 65)
    print("Experiment 3: Kubernetes Pod Health Check")
    print("-" * 65)

    request3 = """Health check script for Kubernetes pods in a given namespace (argument).
- Check all pods are in Running state
- Verify each pod's readiness probe is passing
- Check pod restart counts (alert if >3 restarts in last hour)
- Output a summary table: POD | STATUS | RESTARTS | AGE
- Exit with code 1 if any pod is unhealthy"""

    message3 = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Generate a bash script:\n\n{request3}"}
        ]
    )
    print(message3.content[0].text)

    # Token usage
    print("\n" + "-" * 65)
    print("Token Usage (last request)")
    print("-" * 65)
    print(f"Input tokens:  {message3.usage.input_tokens}")
    print(f"Output tokens: {message3.usage.output_tokens}")

    print("\n" + "=" * 65)
    print("Key Learning: A well-crafted system prompt enforces production")
    print("standards (set -euo pipefail, traps, logging) on every generated")
    print("script. The AI knows the patterns — you tell it which to apply.")
    print("=" * 65)

    print("\nTask 1 Complete!")
    print("Next: python3 demos/task2_script_fixer.py")


if __name__ == "__main__":
    main()
