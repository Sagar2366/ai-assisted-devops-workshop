# Lab 1: AI Script Generator

> **Mission:** Describe what you want in plain English — get a production-ready shell script with error handling, logging, and safety guards.

---

## The Concept

### Why AI Script Generation Matters for SRE

Every SRE writes the same scripts over and over — disk checks, log rotation, health probes, deployment wrappers. The patterns are well-known but tedious to write correctly every time.

> **Analogy:** Like having a senior SRE pair-programming with you who has written 10,000 bash scripts and remembers every edge case — `set -euo pipefail`, proper quoting, signal traps, cleanup functions.

---

### The Pattern: Natural Language → Structured Prompt → Script

1. You describe what the script should do in plain English
2. The AI receives a system prompt that enforces SRE best practices
3. Output: a complete, commented, production-ready script

---

## What You'll Build

A Python script that takes a natural language description and generates a complete bash script with:
- `set -euo pipefail` for safety
- Proper error handling and cleanup traps
- Logging with timestamps
- Input validation
- Comments explaining each section

---

## Step 1: The System Prompt

This is the key — tell the AI to act as a senior shell scripting expert:

```python
SYSTEM_PROMPT = """You are a senior SRE who writes production-grade shell scripts.

Every script you generate MUST include:
1. #!/bin/bash and set -euo pipefail
2. A header comment with description, usage, and prerequisites
3. Logging function with timestamps
4. Input validation for all arguments
5. Cleanup trap (trap cleanup EXIT)
6. Error handling with meaningful exit codes
7. Comments explaining non-obvious logic

Output ONLY the script — no explanation before or after."""
```

---

## Step 2: Generate a Script

```python
import anthropic

client = anthropic.Anthropic()

request = "Monitor disk usage on all mounted filesystems. If any partition exceeds 85%, send an alert to a Slack webhook. Log all checks to /var/log/disk-monitor.log."

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": f"Generate a bash script that does the following:\n\n{request}"}
    ]
)

print(message.content[0].text)
```

---

## Step 3: Try Different Requests

```python
requests = [
    "Rotate application logs older than 7 days, compress them with gzip, and delete archives older than 30 days",
    "Health check script that verifies a Kubernetes pod is running, the HTTP endpoint returns 200, and memory usage is below 80%",
    "Automated backup script for PostgreSQL that creates a dump, uploads to S3, and verifies the upload checksum",
]
```

---

## Run It

```bash
python3 demos/task1_script_generator.py
```

---

## What Success Looks Like

The AI generates a complete bash script with:
- Proper shebang and `set -euo pipefail`
- A logging function with ISO timestamps
- Input validation (checks for required tools like `curl`, `df`)
- A cleanup trap
- The actual disk monitoring logic
- Slack webhook integration
- Meaningful exit codes

---

## Key Takeaway

The system prompt is everything. Without it, you get a basic script. With the right constraints ("must include error handling, traps, logging"), you get production-grade output every time. The AI knows the patterns — you just need to tell it which ones to apply.

---

Next: [Lab 2: Script Fixer](lab2-script-fixer.md)
