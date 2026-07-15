# Lab 0: Environment Setup

> **Mission:** Get your environment ready for AI-powered CI/CD — install dependencies, configure API keys, and verify GitHub integration.

---

## Prerequisites

- Python 3.10 or higher
- An Anthropic API key
- A GitHub personal access token (for PR review features)

---

## Step 1: Install Dependencies

```bash
pip install anthropic PyGithub pyyaml
```

---

## Step 2: Export Your API Keys

```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export GITHUB_TOKEN="your-github-token"  # Optional: for live PR integration
```

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
        {"role": "user", "content": "Say 'CI/CD lab ready!' and nothing else."}
    ]
)
print(message.content[0].text)
```

---

## Step 4: Verify GitHub Token (Optional)

```python
from github import Github

g = Github(os.environ.get("GITHUB_TOKEN"))
user = g.get_user()
print(f"Authenticated as: {user.login}")
```

---

## What Success Looks Like

```
CI/CD lab ready!
Authenticated as: your-username
```

---

## Key Takeaway

Two SDKs (`anthropic` for AI, `PyGithub` for GitHub), two API keys. This combination lets AI read your code, review your PRs, and gate your deployments.

---

Next: [Lab 1: Code Reviewer](lab1-code-reviewer.md)
