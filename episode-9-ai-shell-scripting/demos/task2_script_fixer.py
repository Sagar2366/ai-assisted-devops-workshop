#!/usr/bin/env python3
"""
Task 2: AI Script Fixer
Feed broken shell scripts to AI — get diagnosed bugs and fixed versions.
AI-Assisted DevOps Workshop | Episode 9 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic


def main():
    print("=" * 65)
    print("Task 2: AI Script Fixer")
    print("Broken Scripts → Diagnosed + Fixed")
    print("=" * 65)

    client = anthropic.Anthropic()

    system_prompt = """You are a shell script debugger and fixer.

When given a broken script:
1. DIAGNOSE: List every bug you find (numbered)
2. EXPLAIN: For each bug, explain WHY it's a problem and what could go wrong in production
3. FIX: Return the complete corrected script with comments marking each fix

Format your response as:
## Bugs Found
1. [Line N] [bug description]
   - Risk: [what could go wrong in production]

## Fixed Script
```bash
[complete fixed script with # FIX: comments on changed lines]
```

Be thorough — check for quoting issues, missing error handling, race conditions, security risks, and logic errors."""

    # Experiment 1: Dangerous deploy script
    print("\nExperiment 1: Dangerous Deploy Script")
    print("-" * 65)

    broken_script_1 = '''#!/bin/bash
# Deploy script - moves new build to production
DEPLOY_DIR=/opt/app
BACKUP_DIR=/opt/backups

rm -rf $DEPLOY_DIR/*
cp -r /tmp/build/* $DEPLOY_DIR
service app restart

if [ $? -eq 0 ]; then
    echo "Deploy successful"
fi
'''

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Fix this script:\n\n```bash\n{broken_script_1}\n```"}
        ]
    )
    print(message.content[0].text)

    # Experiment 2: Log cleanup with race condition
    print("\n" + "-" * 65)
    print("Experiment 2: Log Cleanup with Race Condition")
    print("-" * 65)

    broken_script_2 = '''#!/bin/bash
# Cleanup old logs
LOG_DIR=/var/log/app

# Find and delete logs older than 7 days
for file in $(find $LOG_DIR -name "*.log" -mtime +7); do
    size=$(du -sh $file | cut -f1)
    echo "Deleting $file ($size)"
    rm $file
done

# Check if directory is empty and remove
if [ $(ls $LOG_DIR | wc -l) -eq 0 ]; then
    rmdir $LOG_DIR
fi
echo "Cleanup done: $(date)"
'''

    message2 = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Fix this script:\n\n```bash\n{broken_script_2}\n```"}
        ]
    )
    print(message2.content[0].text)

    # Experiment 3: SSL certificate checker with subtle bugs
    print("\n" + "-" * 65)
    print("Experiment 3: SSL Certificate Checker")
    print("-" * 65)

    broken_script_3 = '''#!/bin/bash
# Check SSL cert expiry for domains
DOMAINS="api.example.com web.example.com admin.example.com"
ALERT_DAYS=30

for domain in $DOMAINS; do
    expiry=$(echo | openssl s_client -connect $domain:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
    expiry_epoch=$(date -d "$expiry" +%s)
    now_epoch=$(date +%s)
    days_left=$(( ($expiry_epoch - $now_epoch) / 86400 ))

    if [ $days_left -lt $ALERT_DAYS ]; then
        curl -X POST https://hooks.slack.com/services/XXX -d "{"text": "SSL cert for $domain expires in $days_left days"}"
    fi
done
'''

    message3 = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Fix this script:\n\n```bash\n{broken_script_3}\n```"}
        ]
    )
    print(message3.content[0].text)

    print("\n" + "=" * 65)
    print("Key Learning: AI script fixing goes beyond syntax checking —")
    print("it catches logic errors, race conditions, security risks, and")
    print("missing safety guards that static analyzers miss entirely.")
    print("=" * 65)

    print("\nTask 2 Complete!")
    print("Next: python3 demos/task3_script_converter.py")


if __name__ == "__main__":
    main()
