# Lab 5: AI Script Optimizer

> **Mission:** Take a working-but-fragile script and have AI add safety guards, performance improvements, and production hardening.

---

## The Concept

### The "Works on My Machine" Problem

Most scripts are written to solve the immediate problem. They work — until they don't. Missing error handling, no logging, no cleanup, no input validation. AI optimization adds all the production hardening patterns that separate a prototype from a reliable automation.

> **Analogy:** Like a code review from a paranoid senior SRE who has been burned by every possible failure mode. They don't change what your script does — they armor it against everything that can go wrong.

---

### Optimization Categories

| Category | What AI Adds |
|----------|-------------|
| Safety | `set -euo pipefail`, quoted variables, input validation |
| Reliability | Retry logic, timeout guards, lock files |
| Observability | Logging with timestamps, exit code reporting |
| Cleanup | Trap handlers, temp file management |
| Performance | Parallel execution, avoiding subshells in loops |
| Security | No hardcoded secrets, restricted permissions, safe temp dirs |

---

## What You'll Build

A Python script that takes a "quick and dirty" script and returns an optimized version with explanations for every improvement.

---

## Step 1: The Optimizer Prompt

```python
SYSTEM_PROMPT = """You are a shell script optimizer focused on production hardening.

Given a script, return:

## Improvements Made
For each change:
- What: what you changed
- Why: what failure it prevents
- Risk without it: what could go wrong in production

## Optimized Script
The complete improved script with comments marking each improvement.

Categories to check:
1. Safety: set -euo pipefail, quoting, input validation
2. Reliability: retries, timeouts, lock files
3. Observability: logging, exit codes, timing
4. Cleanup: trap EXIT, temp file management
5. Performance: avoid subshells in loops, parallel where safe
6. Security: no hardcoded secrets, mktemp instead of /tmp/fixed-name

Do NOT change the script's core logic — only harden it."""
```

---

## Step 2: Optimize a Real Script

```python
naive_script = '''#!/bin/bash
# Quick deploy script
cd /opt/app
git pull
npm install
npm run build
pm2 restart app
echo "Done"
'''

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": f"Optimize this script for production:\n\n```bash\n{naive_script}\n```"}
    ]
)
print(message.content[0].text)
```

---

## Run It

```bash
python3 demos/task5_script_optimizer.py
```

---

## What Success Looks Like

The AI returns improvements like:
1. Added `set -euo pipefail` — prevents silent failures
2. Added lock file — prevents concurrent deploys
3. Added rollback on failure — reverts git pull if build fails
4. Added health check after restart — verifies deploy succeeded
5. Added logging with timestamps — audit trail for debugging
6. Replaced `cd` with absolute paths — prevents wrong-directory execution

---

## Key Takeaway

Script optimization is not about rewriting — it is about hardening. AI knows every production failure pattern and adds guards against all of them in seconds. Use this on every script before it goes to production.

---

**Episode 9 Complete!**

Next Episode: [Episode 10: AI-Powered CI/CD & GitOps](../../episode-10-ai-cicd-gitops/README.md)
