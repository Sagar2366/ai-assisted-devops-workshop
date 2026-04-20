"""
Episode 7: AI-Assisted Shell Scripting & Automation
AI Shell Script Fixer

Paste a broken script -> AI finds bugs, explains them, and fixes them.

Author: Sagar Utekar
Prerequisites:
    - Claude API key set as ANTHROPIC_API_KEY environment variable
    - Python anthropic package installed (pip install anthropic)
"""
import anthropic

client = anthropic.Anthropic()

# A deliberately broken backup script (3 bugs + poor practices)
BROKEN_SCRIPT = '''#!/bin/bash
# Backup script - written during 2 AM incident, "works on my machine"

BACKUP_DIR=/tmp/backups
SOURCE_DIR=$1
RETENTION_DAYS=7

# Bug 1: No quoting - breaks on paths with spaces
mkdir -p $BACKUP_DIR

# Bug 2: Wrong variable expansion - should be $(date ...) not `date ...`
# Also no error checking if tar fails
TIMESTAMP=`date +%Y%m%d`
tar czf $BACKUP_DIR/backup-$TIMESTAMP.tar.gz $SOURCE_DIR

# Bug 3: Missing quotes around variable in find - glob expansion risk
find $BACKUP_DIR -name *.tar.gz -mtime +$RETENTION_DAYS -delete

# No error checking at all
echo "Backup done"
'''

def fix_script(script: str) -> str:
    """Send a broken script to AI for analysis and fixing."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="""You are a senior shell script auditor. When given a script:

1. List EVERY bug, security issue, and bad practice. For each:
   - Line number (approximate)
   - What is wrong
   - Why it is dangerous
   - The fix

2. Then output the COMPLETE fixed script with:
   - All bugs fixed
   - set -euo pipefail added
   - Proper error handling
   - Proper quoting
   - A usage() function
   - A cleanup trap

Format your response as:
## Bugs Found
(numbered list)

## Fixed Script
```bash
(complete script)
```""",
        messages=[{
            "role": "user",
            "content": f"Find all bugs and fix this script:\n\n```bash\n{script}\n```"
        }]
    )

    return response.content[0].text


def review_and_improve(script: str) -> str:
    """Review a working script and suggest improvements."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="""You review shell scripts for production readiness. Score each category 1-5:

1. Error Handling (set -e, traps, exit codes)
2. Security (quoting, input validation, no hardcoded secrets)
3. Maintainability (comments, functions, naming)
4. Portability (POSIX compliance, no unnecessary bashisms)
5. Robustness (edge cases, race conditions, atomicity)

Output a scorecard, then specific improvements with before/after examples.""",
        messages=[{
            "role": "user",
            "content": f"Review this script for production readiness:\n\n```bash\n{script}\n```"
        }]
    )

    return response.content[0].text


if __name__ == "__main__":
    print("=" * 60)
    print("BROKEN SCRIPT:")
    print("=" * 60)
    print(BROKEN_SCRIPT)

    print("\n" + "=" * 60)
    print("AI ANALYSIS:")
    print("=" * 60)
    result = fix_script(BROKEN_SCRIPT)
    print(result)
