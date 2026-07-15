# Lab 4: AI Script Explainer

> **Mission:** Paste a complex one-liner or pipeline — the AI breaks it down step by step so you (and your team) understand exactly what it does.

---

## The Concept

### The One-Liner Problem

Every SRE team has "that script" — a 300-character pipeline written by someone who left two years ago. Nobody dares touch it. Nobody fully understands it. It runs in cron and if it breaks, the on-call scrambles.

> **Analogy:** Like having a translator for ancient hieroglyphics. The symbols are powerful — but only if someone can read them. AI reads every shell dialect fluently.

---

### What AI Explains That Comments Don't

| Level | What It Covers |
|-------|---------------|
| Syntax | What each flag and operator does |
| Data flow | How data transforms through each pipe stage |
| Side effects | What files are created, modified, deleted |
| Failure modes | What happens if any stage fails |
| Alternatives | Simpler ways to achieve the same result |

---

## What You'll Build

A Python script that takes complex shell commands and produces:
1. A plain-English summary
2. Step-by-step breakdown of each component
3. Data flow diagram (text-based)
4. Potential failure points
5. Simpler alternatives if they exist

---

## Step 1: The Explainer Prompt

```python
SYSTEM_PROMPT = """You are a shell command explainer for SRE teams.

When given a command or script, explain it in this format:

## Summary
One sentence: what this command accomplishes.

## Step-by-Step Breakdown
For each pipe stage or significant operation:
- What it does
- What its input/output looks like
- Key flags and why they matter

## Data Flow
Show how data transforms: input → stage1 → stage2 → output

## Failure Points
What can go wrong at each stage and what would happen.

## Simpler Alternative (if one exists)
A clearer way to achieve the same result.

Write for a mid-level engineer — no jargon without explanation."""
```

---

## Step 2: Explain a Complex Pipeline

```python
complex_command = "kubectl get pods -A -o json | jq -r '.items[] | select(.status.containerStatuses[]?.state.waiting.reason == \"CrashLoopBackOff\") | \"\\(.metadata.namespace)/\\(.metadata.name)\"' | xargs -I{} sh -c 'ns=$(echo {} | cut -d/ -f1); pod=$(echo {} | cut -d/ -f2); kubectl logs $pod -n $ns --tail=50 --previous 2>/dev/null || echo \"No previous logs for {}\"'"

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": f"Explain this command:\n\n```bash\n{complex_command}\n```"}
    ]
)
print(message.content[0].text)
```

---

## Run It

```bash
python3 demos/task4_script_explainer.py
```

---

## What Success Looks Like

A clear breakdown showing:
1. Summary: "Gets the previous logs from all CrashLoopBackOff pods across all namespaces"
2. Each pipe stage explained with input/output
3. The jq filter dissected (select, string interpolation)
4. Failure points (no previous container, permission errors)
5. A simpler alternative using a for loop

---

## Key Takeaway

AI explanation turns tribal knowledge into shared understanding. Complex one-liners that only one person understands become documented, explainable operations. Use this before modifying inherited scripts — understand first, change second.

---

Next: [Lab 5: Script Optimizer](lab5-script-optimizer.md)
