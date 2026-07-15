# Lab 3: AI Script Converter

> **Mission:** Convert scripts between languages — bash to Python, Python to Go — preserving logic while adding idiomatic error handling for the target language.

---

## The Concept

### Why Convert Scripts?

Bash is great for quick automation but terrible for maintainability at scale. When a 200-line bash script becomes business-critical, you need to convert it to a language with proper error handling, testing, and type safety.

> **Analogy:** Like translating a book between languages. A word-for-word translation is useless — you need someone who understands both languages fluently and can express the same MEANING idiomatically in the target language.

---

### Conversion Challenges AI Handles

| From | To | AI Handles |
|------|------|-----------|
| Bash | Python | subprocess calls, pathlib, try/except, argparse |
| Bash | Go | os/exec, error returns, flag package |
| Python | Bash | Removing OOP, using coreutils equivalents |
| Any | Any | Preserving logic while using target idioms |

---

## What You'll Build

A Python script that converts shell scripts to other languages while:
- Preserving the original logic exactly
- Using idiomatic patterns for the target language
- Adding proper error handling
- Including equivalent comments

---

## Step 1: The Converter Prompt

```python
SYSTEM_PROMPT = """You are a polyglot script converter specializing in DevOps languages.

When converting a script:
1. Preserve the EXACT same logic and behavior
2. Use IDIOMATIC patterns for the target language (not literal translation)
3. Add proper error handling native to the target language
4. Keep all comments, translating them to match the new code
5. Add type hints (Python) or type declarations (Go) where appropriate

Output ONLY the converted script — no explanation."""
```

---

## Step 2: Convert Bash to Python

```python
bash_script = '''#!/bin/bash
set -euo pipefail

NAMESPACE="${1:-default}"
THRESHOLD=80

for pod in $(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}'); do
    cpu=$(kubectl top pod "$pod" -n "$NAMESPACE" --no-headers | awk '{print $2}' | tr -d 'm')
    if [ "$cpu" -gt "$THRESHOLD" ]; then
        echo "[ALERT] Pod $pod using ${cpu}m CPU (threshold: ${THRESHOLD}m)"
    fi
done
'''

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": f"Convert this bash script to Python with proper error handling:\n\n```bash\n{bash_script}\n```"}
    ]
)
print(message.content[0].text)
```

---

## Run It

```bash
python3 demos/task3_script_converter.py
```

---

## What Success Looks Like

The bash script becomes idiomatic Python using:
- `subprocess.run()` with error checking
- `argparse` for the namespace argument
- `try/except` blocks
- Type hints
- A `main()` function with `if __name__ == "__main__"`

---

## Key Takeaway

AI conversion is not search-and-replace — it understands the INTENT of each line and expresses it idiomatically in the target language. The system prompt ensures it adds proper error handling rather than doing a naive line-by-line translation.

---

Next: [Lab 4: Script Explainer](lab4-script-explainer.md)
