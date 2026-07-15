#!/usr/bin/env python3
"""
Task 5: AI Script Optimizer
Optimize shell scripts for production — add safety, performance, and reliability.
AI-Assisted DevOps Workshop | Episode 9 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic


def main():
    print("=" * 65)
    print("Task 5: AI Script Optimizer")
    print("Quick-and-Dirty → Production-Hardened")
    print("=" * 65)

    client = anthropic.Anthropic()

    system_prompt = """You are a shell script optimizer focused on production hardening.

Given a script, return:

## Improvements Made
For each change (numbered):
- **What**: what you changed
- **Why**: what failure it prevents
- **Risk without it**: what could go wrong in production

## Optimized Script
```bash
[The complete improved script with inline comments marking improvements]
```

Categories to check:
1. Safety: set -euo pipefail, quoting, input validation
2. Reliability: retries, timeouts, lock files for concurrency
3. Observability: logging with timestamps, exit codes, duration tracking
4. Cleanup: trap EXIT, temp file management with mktemp
5. Performance: avoid subshells in loops, parallel where safe
6. Security: no hardcoded secrets, restricted permissions, safe temp dirs

Do NOT change the script's core logic — only harden it."""

    # Experiment 1: Naive deployment script
    print("\nExperiment 1: Hardening a Deploy Script")
    print("-" * 65)

    naive_deploy = '''#!/bin/bash
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
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Optimize this script for production:\n\n```bash\n{naive_deploy}\n```"}
        ]
    )
    print(message.content[0].text)

    # Experiment 2: Database backup without safety
    print("\n" + "-" * 65)
    print("Experiment 2: Hardening a Database Backup Script")
    print("-" * 65)

    naive_backup = '''#!/bin/bash
# Backup PostgreSQL database
pg_dump -h localhost -U postgres mydb > /backups/mydb_$(date +%Y%m%d).sql
gzip /backups/mydb_$(date +%Y%m%d).sql
aws s3 cp /backups/mydb_$(date +%Y%m%d).sql.gz s3://my-backups/
rm /backups/mydb_*.sql.gz
echo "Backup uploaded"
'''

    message2 = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Optimize this script for production:\n\n```bash\n{naive_backup}\n```"}
        ]
    )
    print(message2.content[0].text)

    # Experiment 3: Container cleanup without guards
    print("\n" + "-" * 65)
    print("Experiment 3: Hardening a Container Cleanup Script")
    print("-" * 65)

    naive_cleanup = '''#!/bin/bash
# Clean up Docker resources
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
docker rmi $(docker images -q --filter "dangling=true")
docker volume rm $(docker volume ls -q --filter "dangling=true")
docker network prune -f
echo "All cleaned up"
'''

    message3 = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Optimize this script for production:\n\n```bash\n{naive_cleanup}\n```"}
        ]
    )
    print(message3.content[0].text)

    print("\n" + "=" * 65)
    print("Key Learning: Script optimization is not rewriting — it is hardening.")
    print("AI adds set -euo pipefail, lock files, rollback logic, health checks,")
    print("logging, and cleanup traps without changing your script's core intent.")
    print("=" * 65)

    print("\nTask 5 Complete!")
    print("Episode 9 done! Next: Episode 10 — AI-Powered CI/CD & GitOps")


if __name__ == "__main__":
    main()
