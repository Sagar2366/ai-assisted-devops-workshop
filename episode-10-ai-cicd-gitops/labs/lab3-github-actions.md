# Lab 3: AI-Powered GitHub Action

> **Mission:** Build a GitHub Action that triggers AI-powered code review on every pull request — automated, consistent, and catches issues before human reviewers even look.

---

## The Concept

### Why AI in GitHub Actions?

Manual code review is a bottleneck. PRs sit for hours or days waiting for human attention. An AI-powered GitHub Action runs instantly on every PR, catches the obvious issues (security, bugs, anti-patterns), and lets human reviewers focus on architecture and design decisions.

> **Analogy:** Like installing a security checkpoint at the entrance of a building. Guards (humans) still patrol inside, but the checkpoint catches prohibited items before they even enter — freeing guards to focus on real threats, not bag searches.

---

### GitHub Action Workflow Structure

| Component | Purpose |
|-----------|---------|
| `on: pull_request` | Triggers when a PR is opened or updated |
| `actions/checkout` | Gets the code |
| `gh pr diff` | Extracts the diff for the PR |
| Claude API call | Sends diff for AI review |
| PR comment | Posts findings back to the pull request |

---

## What You'll Build

A complete GitHub Actions workflow file that:
1. Triggers on pull request events (opened, synchronize)
2. Extracts the PR diff
3. Sends the diff to Claude for code review
4. Posts review findings as a PR comment

---

## Step 1: Workflow YAML Structure

```yaml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: read
  pull-requests: write

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Get PR diff
        id: diff
        run: |
          gh pr diff ${{ github.event.pull_request.number }} > pr_diff.txt
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Run AI Review
        id: review
        run: |
          python3 review.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Post Review Comment
        run: |
          gh pr comment ${{ github.event.pull_request.number }} --body-file review_output.md
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Step 2: The Review Script (called by the action)

```python
#!/usr/bin/env python3
import anthropic
import os

client = anthropic.Anthropic()

# Read the diff extracted in the previous step
with open("pr_diff.txt", "r") as f:
    diff = f.read()

# Truncate if too large (Claude handles ~100k tokens but be sensible)
if len(diff) > 50000:
    diff = diff[:50000] + "\n\n[... truncated — diff too large for full review ...]"

SYSTEM_PROMPT = """You are a senior code reviewer running as a GitHub Action.
Review the PR diff and return findings in Markdown format suitable for a PR comment.

Structure your response as:
## AI Code Review

### Critical Issues
(issues that must be fixed before merge)

### Suggestions
(improvements that would make the code better)

### Summary
(one-paragraph assessment: is this PR safe to merge?)

Be concise. Skip trivial style issues. Focus on bugs, security, and logic errors."""

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": f"Review this PR diff:\n\n```diff\n{diff}\n```"}
    ]
)

review_text = message.content[0].text

with open("review_output.md", "w") as f:
    f.write(review_text)

print(review_text)
```

---

## Step 3: Generate the Full Action Programmatically

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": """Generate a complete GitHub Actions workflow file (.github/workflows/ai-review.yml) that:
1. Triggers on pull_request (opened, synchronize)
2. Has permissions for contents:read and pull-requests:write
3. Checks out the repo with fetch-depth: 0
4. Installs Python and the anthropic SDK
5. Extracts the PR diff using gh CLI
6. Calls Claude API to review the diff
7. Posts the review as a PR comment using gh CLI

Use secrets.ANTHROPIC_API_KEY for the API key.
Return ONLY the YAML — no explanation."""}
    ]
)

print(message.content[0].text)
```

---

## Run It

```bash
python3 demos/task3_github_action.py
```

---

## What Success Looks Like

The script generates a complete, valid GitHub Actions workflow YAML that:
- Triggers on the correct PR events
- Has proper permissions set
- Extracts the diff using `gh pr diff`
- Calls Claude with a structured review prompt
- Posts findings back to the PR as a comment
- Handles edge cases (large diffs, API failures)

When deployed to a real repo, every PR gets an AI review comment within 30-60 seconds of opening.

---

## Key Takeaway

GitHub Actions + Claude API = automated code review on every PR. The workflow is simple: trigger on PR, get diff, call Claude, post comment. The real power is in the system prompt — tuning it to your team's standards, your language, and your production concerns turns generic AI review into a team-specific quality gate.

---

Next: [Lab 4: ArgoCD Risk Gate](lab4-argocd-risk-gate.md)
