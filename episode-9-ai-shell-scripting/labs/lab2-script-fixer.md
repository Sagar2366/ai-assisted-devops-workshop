# Lab 2: AI Script Fixer

> **Mission:** Paste a broken shell script — the AI diagnoses the bugs, explains what went wrong, and returns a fixed version.

---

## The Concept

### Why Script Fixing Matters

Shell scripts fail silently. A missing quote, an unset variable, a wrong redirect — bash won't warn you until production breaks at 3 AM. AI can spot these bugs instantly because it has seen every shell scripting mistake ever posted on Stack Overflow.

> **Analogy:** Like running `shellcheck` but with understanding. ShellCheck catches syntax — AI catches logic errors, race conditions, and missing edge cases too.

---

### Common Shell Script Bugs AI Catches

| Bug Type | Example | Impact |
|----------|---------|--------|
| Unquoted variables | `rm -rf $DIR/` | Deletes `/` if DIR is empty |
| Missing error checks | No `set -e` | Script continues after failures |
| Race conditions | Check-then-act without locks | Concurrent runs corrupt data |
| Signal handling | No trap on EXIT | Temp files left behind |
| Word splitting | `for f in $(find ...)` | Breaks on filenames with spaces |

---

## What You'll Build

A Python script that:
1. Takes a broken shell script as input
2. Sends it to Claude with a "script doctor" system prompt
3. Returns: diagnosis (what is wrong), explanation (why it is wrong), and fixed script

---

## Step 1: The Script Doctor Prompt

```python
SYSTEM_PROMPT = """You are a shell script debugger and fixer.

When given a broken script:
1. DIAGNOSE: List every bug you find (numbered)
2. EXPLAIN: For each bug, explain WHY it's a problem and what could go wrong
3. FIX: Return the complete corrected script

Format your response as:
## Bugs Found
1. [bug description]
   - Why it matters: [explanation]

## Fixed Script
```bash
[complete fixed script]
```

Be thorough — check for quoting issues, missing error handling, race conditions, and logic errors."""
```

---

## Step 2: Feed a Broken Script

```python
broken_script = '''#!/bin/bash
# Deploy script
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
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": f"Fix this script:\n\n```bash\n{broken_script}\n```"}
    ]
)
print(message.content[0].text)
```

---

## Step 3: Try More Broken Scripts

Feed scripts with increasingly subtle bugs — from obvious syntax errors to dangerous logic issues like `rm -rf $UNSET_VAR/`.

---

## Run It

```bash
python3 demos/task2_script_fixer.py
```

---

## What Success Looks Like

The AI identifies issues like:
1. No `set -euo pipefail` — script continues after `rm -rf` fails
2. Unquoted `$DEPLOY_DIR` — dangerous if variable is empty
3. No backup before destructive `rm -rf`
4. No validation that `/tmp/build/` exists
5. No rollback on failed restart

And returns a fixed version with all issues resolved.

---

## Key Takeaway

AI script fixing is not just syntax checking — it catches logic errors, security risks, and missing safety guards that static analyzers miss. The "script doctor" system prompt forces structured output: diagnosis, explanation, fix.

---

Next: [Lab 3: Script Converter](lab3-script-converter.md)
