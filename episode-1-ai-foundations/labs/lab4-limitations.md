# Lab 4: Where LLMs Break — Limitations

> **Mission:** Expose three fundamental LLM limitations — no live access, no execution, and hallucination.

---

## The Concept

LLMs answer from memory (training data). They do NOT have:

1. **Live cluster access** — "Is my pod healthy?" → "I don't have access to your infrastructure"
2. **Execution ability** — "Run kubectl get pods" → gives you the command, can't run it
3. **Guaranteed accuracy** — ask about a fake kubectl flag → invents one with full confidence

```
  You: "What is the exact flag for graceful restart timeout?"

  LLM: "kubectl rollout restart --graceful-period=30"
                |
                v
       THIS FLAG DOES NOT EXIST
       The model said it with full confidence
```

This is called **hallucination** — the model gives a confident answer that is completely wrong.

---

## What You'll Build

Three questions designed to break the model:
1. Ask about live cluster state
2. Ask it to execute a command
3. Set a hallucination trap with fake kubectl flags

---

## Step 1: Define the Test Questions

```python
questions = [
    ("Live cluster state", "Is my api-server pod in production namespace healthy right now?"),
    ("Execute a command", "Run 'kubectl get pods -n production' and show me the output."),
    ("Hallucination trap", "What is the exact flag for graceful restart timeout in kubectl rollout restart?"),
]
```

---

## Step 2: Send Each Question

**Anthropic:**
```python
for title, question in questions:
    print(f"\n{'='*60}")
    print(f"  TEST: {title}")
    print(f"{'='*60}")

    message = client.messages.create(
        model="claude-sonnet-4-6-latest",
        max_tokens=1024,
        messages=[{"role": "user", "content": question}]
    )
    print(message.content[0].text)
```

---

## Run It

```bash
python3 demos/{your-provider}/task4_limitations.py
```

---

## What Success Looks Like

**Question 1 (Live state):** The model admits it can't access your cluster. Good — it's honest here.

**Question 2 (Execute):** The model shows you the command but can't actually run it. It can TELL you the command but can't EXECUTE it.

**Question 3 (Hallucination):** The model confidently gives you a kubectl flag that doesn't exist. This is the dangerous one — it sounds right, looks right, and is completely wrong.

---

## Why This Matters

**Rule:** Never run an AI-generated command in production without reading it first.

These three limitations are exactly why agents exist:
- Can't access your cluster → **give it tools** (Episode 4)
- Can't execute commands → **give it tools** (Episode 4)
- Hallucination → **add guardrails and verification** (Episode 9)

---

## Key Takeaway

LLMs answer from training data, not live systems. They can't access your cluster, can't execute commands, and will confidently make things up. Understanding these limits is essential before building anything production-grade.

---

## Complete Code (Anthropic)

If you get stuck, here's the full working script:

```python
#!/usr/bin/env python3
"""Task 4: Where LLMs Break — Hallucination and Limitations"""
import anthropic

def main():
    client = anthropic.Anthropic()
    system = "You are a senior SRE with 10 years of Kubernetes experience. Be concise and actionable."

    questions = [
        ("Live cluster state", "Is my api-server pod in the production namespace healthy right now?"),
        ("Execute a command", "Run 'kubectl get pods -n production' and show me the output."),
        ("Hallucination trap", "What is the exact flag for graceful restart timeout in kubectl rollout restart?"),
    ]

    for label, question in questions:
        print(f"\n{'='*60}")
        print(f"  TEST: {label}")
        print(f"{'='*60}")

        message = client.messages.create(
            model="claude-sonnet-4-6-latest",
            max_tokens=512,
            system=system,
            messages=[{"role": "user", "content": question}]
        )
        print(message.content[0].text)

if __name__ == "__main__":
    main()
```

---

Next: [Lab 5: Conversation History](lab5-conversation-history.md)
