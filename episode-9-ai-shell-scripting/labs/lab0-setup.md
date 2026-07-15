# Lab 0: Environment Setup

> **Mission:** Get your environment ready for AI-powered shell scripting — install dependencies and verify your API key works.

---

## Prerequisites

- Python 3.10 or higher
- An Anthropic API key

---

## Step 1: Install Dependencies

```bash
pip install anthropic
```

---

## Step 2: Export Your API Key

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

Add this to your shell profile (`~/.bashrc`, `~/.zshrc`) so it persists across sessions.

---

## Step 3: Verify the Setup

```python
#!/usr/bin/env python3
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=256,
    messages=[
        {"role": "user", "content": "Say 'Shell scripting lab ready!' and nothing else."}
    ]
)
print(message.content[0].text)
```

---

## What Success Looks Like

```
Shell scripting lab ready!
```

If you see an authentication error, double-check your API key is exported correctly.

---

## Key Takeaway

One dependency (`anthropic`), one environment variable (`ANTHROPIC_API_KEY`). That is all you need to start generating, fixing, and converting shell scripts with AI.

---

Next: [Lab 1: Script Generator](lab1-script-generator.md)
