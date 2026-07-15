# Lab 0: Environment Setup

> Episode 7: Build a DevOps Copilot | **Sagar Utekar** | CNCF Ambassador | Kubestronaut

---

## Mission

Get your development environment ready in under 5 minutes so you can focus on building, not debugging setup issues.

---

## Step 1: Install Python Dependencies

```bash
pip install anthropic rich
```

What these do:
- **anthropic** — Official Python SDK for the Claude API
- **rich** — Beautiful terminal formatting (colors, tables, panels)

---

## Step 2: Set Your API Key

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export ANTHROPIC_API_KEY="your-api-key-here"

# Verify it's set
echo $ANTHROPIC_API_KEY
```

Get your API key from: https://console.anthropic.com/settings/keys

---

## Step 3: Verify Everything Works

Create a file called `verify_setup.py`:

```python
#!/usr/bin/env python3
"""Verify Episode 7 environment is ready."""

import sys

def check_anthropic():
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'Setup verified!' and nothing else."}]
        )
        print(f"✓ Anthropic SDK working: {response.content[0].text}")
        return True
    except Exception as e:
        print(f"✗ Anthropic SDK error: {e}")
        return False

def check_rich():
    try:
        from rich.console import Console
        from rich.panel import Panel
        console = Console()
        console.print(Panel("✓ Rich library working", style="green"))
        return True
    except Exception as e:
        print(f"✗ Rich library error: {e}")
        return False

if __name__ == "__main__":
    print("Episode 7 — Environment Check\n")
    results = [check_rich(), check_anthropic()]
    
    if all(results):
        print("\n🎉 All checks passed — you're ready to build!")
    else:
        print("\n⚠️  Some checks failed — fix the errors above before continuing.")
        sys.exit(1)
```

Run it:

```bash
python3 verify_setup.py
```

---

## Step 4: Project Structure

Create this folder structure (or clone the repo):

```
episode-7-devops-copilot-project/
├── README.md
├── labs/
│   ├── lab0-setup.md          ← You are here
│   ├── lab1-cli-interface.md
│   ├── lab2-command-classification.md
│   ├── lab3-safety-guardrails.md
│   ├── lab4-audit-logging.md
│   ├── lab5-natural-language.md
│   └── lab6-full-copilot.md
└── demos/
    ├── task1_cli_interface.py
    ├── task2_command_classification.py
    ├── task3_safety_guardrails.py
    ├── task4_audit_logging.py
    ├── task5_natural_language.py
    └── task6_full_copilot.py
```

---

## What Success Looks Like

```
Episode 7 — Environment Check

╭──────────────────────────────╮
│ ✓ Rich library working       │
╰──────────────────────────────╯
✓ Anthropic SDK working: Setup verified!

🎉 All checks passed — you're ready to build!
```

---

## Key Takeaway

Setup is boring but critical. A broken environment wastes hours. Verify once, build with confidence.

---

**Next → [Lab 1: CLI Interface](lab1-cli-interface.md)**
