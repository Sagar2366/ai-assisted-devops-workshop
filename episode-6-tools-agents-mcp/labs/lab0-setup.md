# Lab 0: Environment Setup

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

> **Mission:** Verify your environment is ready for building AI-powered DevOps tools, agents, and MCP servers.

---

## Prerequisites Checklist

| Requirement | Minimum Version | Purpose |
|-------------|----------------|---------|
| Python | 3.10+ | Runtime for all demos |
| pip | Latest | Package management |
| anthropic SDK | Latest | Claude API access |
| mcp package | Latest | MCP server framework |
| kubectl | 1.28+ | Kubernetes CLI (optional) |
| Docker | 24+ | Container operations |

---

## Step 1: Python Environment

```bash
# Check Python version
python3 --version
# Expected: Python 3.10.x or higher

# Create a virtual environment (recommended)
python3 -m venv ~/.venvs/episode6
source ~/.venvs/episode6/bin/activate
```

---

## Step 2: Install Required Packages

```bash
# Core packages
pip install anthropic mcp

# Verify installations
python3 -c "import anthropic; print(f'anthropic SDK: {anthropic.__version__}')"
python3 -c "import mcp; print('mcp package: OK')"
```

---

## Step 3: API Key Configuration

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"

# Verify it works
python3 -c "
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model='claude-sonnet-4-6',
    max_tokens=50,
    messages=[{'role': 'user', 'content': 'Say hello in 5 words'}]
)
print(response.content[0].text)
"
```

---

## Step 4: kubectl Check (Optional)

```bash
# Check kubectl
kubectl version --client

# Verify cluster access (if available)
kubectl cluster-info

# If no cluster, that is fine — labs use mocked responses
```

---

## Step 5: Verify Full Setup

```python
#!/usr/bin/env python3
"""Verify Episode 6 environment setup."""
import sys, os, subprocess

checks = []
v = sys.version_info
checks.append(("Python 3.10+", v.major == 3 and v.minor >= 10))

try:
    import anthropic
    checks.append(("anthropic SDK", True))
except ImportError:
    checks.append(("anthropic SDK", False))

try:
    import mcp
    checks.append(("mcp package", True))
except ImportError:
    checks.append(("mcp package", False))

checks.append(("ANTHROPIC_API_KEY set", bool(os.getenv("ANTHROPIC_API_KEY"))))

print("=" * 50)
print("Episode 6 Environment Check")
print("=" * 50)
for name, status in checks:
    icon = "[PASS]" if status else "[FAIL]"
    print(f"  {icon} {name}")
print("=" * 50)
```

---

## What Success Looks Like

```
==================================================
Episode 6 Environment Check
==================================================
  [PASS] Python 3.10+
  [PASS] anthropic SDK
  [PASS] mcp package
  [PASS] ANTHROPIC_API_KEY set
==================================================
```

---

## Key Takeaway

A working environment is the foundation for everything that follows. If kubectl is unavailable, every lab still works — we mock Kubernetes responses where needed.

**Next:** [Lab 1: Function Calling](lab1-function-calling.md)
