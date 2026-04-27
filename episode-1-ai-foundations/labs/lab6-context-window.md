# Lab 6: Context Window Management

> **Mission:** Understand what happens when conversations overflow the context window, and implement sliding window truncation.

---

## The Concept

The context window has a limit. Everything has to fit in one box:

```
  +-------------------------------+
  |       CONTEXT WINDOW          |
  |                               |
  |  System prompt                |
  |  Conversation history         |
  |  Tool definitions             |
  |  Tool results                 |
  |  Your new prompt              |
  |                               |
  |  Everything must fit          |
  +-------------------------------+
```

When the conversation gets too long, something has to go. The simplest approach: **sliding window** — drop the oldest messages, keep the recent ones.

---

## What You'll Build

Build a long SRE conversation (10+ turns), then truncate it to fit a smaller window. Compare:
1. Full history response — AI knows everything
2. Truncated response — AI lost the early context

---

## Step 1: Build a Long Conversation

Simulate a 10-turn K8s troubleshooting thread:

```python
conversation = [
    {"role": "user", "content": "My name is Sagar, I'm an SRE at Acme Corp."},
    {"role": "assistant", "content": "Nice to meet you, Sagar!"},
    {"role": "user", "content": "We run EKS with 50 microservices."},
    {"role": "assistant", "content": "That's a substantial setup."},
    {"role": "user", "content": "Our budget is $500/month for AI tools."},
    {"role": "assistant", "content": "Understood, I'll keep cost in mind."},
    {"role": "user", "content": "The payment-service pod keeps OOMing."},
    {"role": "assistant", "content": "Let's investigate the memory usage."},
    {"role": "user", "content": "Memory limit is 256Mi, usage peaks at 255Mi."},
    {"role": "assistant", "content": "That's critically close to the limit."},
]
```

---

## Step 2: Ask a Question with Full History

```python
conversation.append({
    "role": "user",
    "content": "Based on everything you know about me, what's your recommendation?"
})

# Send full conversation — AI knows name, company, budget, problem
message = client.messages.create(
    model="claude-sonnet-4-6-latest",
    max_tokens=1024,
    messages=conversation
)
print("FULL HISTORY:", message.content[0].text)
```

---

## Step 3: Truncate and Ask Again

```python
WINDOW_SIZE = 4  # Keep only last 4 messages
truncated = conversation[-WINDOW_SIZE:]

message = client.messages.create(
    model="claude-sonnet-4-6-latest",
    max_tokens=1024,
    messages=truncated
)
print("TRUNCATED:", message.content[0].text)
```

---

## Run It

```bash
python3 demos/{your-provider}/task6_context_window.py
```

---

## What Success Looks Like

**Full history:** The AI recommends solutions tailored to Sagar's EKS setup, references the $500 budget, and targets the payment-service pod specifically.

**Truncated:** The AI gives generic OOM advice — it doesn't know your name, your budget, or that you're running EKS. That context was in the old messages that got dropped.

---

## Key Takeaway

Context windows overflow. Sliding window is the simplest fix — but you lose old messages. What if the important info (name, role, budget) was in those old messages? Lab 7 fixes that with summarization.

---

## Complete Code (Anthropic)

If you get stuck, here's the full working script:

```python
#!/usr/bin/env python3
"""Task 6: Context Window Management"""
import anthropic

def main():
    client = anthropic.Anthropic()
    system = "You are a helpful SRE assistant. Remember details from the conversation."

    # Build 10-turn SRE conversation
    topics = [
        "My name is Sagar, I'm an SRE at Acme Corp.",
        "We run EKS with 50 microservices.",
        "Our budget is $500/month for AI tools.",
        "The payment-service pod keeps OOMing.",
        "Memory limit is 256Mi, usage peaks at 255Mi.",
        "We use ArgoCD for deployments.",
        "Prometheus and Grafana for monitoring.",
        "Team of 5 SREs covering 3 time zones.",
        "Biggest pain point is OOM after every deploy.",
        "We need a cost-effective solution."
    ]

    conversation = []
    for topic in topics:
        conversation.append({"role": "user", "content": topic})
        response = client.messages.create(
            model="claude-sonnet-4-6-latest", max_tokens=128,
            system=system, messages=conversation
        )
        conversation.append({"role": "assistant", "content": response.content[0].text})

    # Test 1: Full history
    test_msg = "Based on everything you know about me, what's your recommendation?"
    conversation.append({"role": "user", "content": test_msg})
    response = client.messages.create(
        model="claude-sonnet-4-6-latest", max_tokens=512,
        system=system, messages=conversation
    )
    print("FULL HISTORY:", response.content[0].text)
    conversation.append({"role": "assistant", "content": response.content[0].text})

    # Test 2: Sliding window — last 3 exchanges only
    truncated = conversation[-6:]
    truncated.append({"role": "user", "content": test_msg})
    response = client.messages.create(
        model="claude-sonnet-4-6-latest", max_tokens=512,
        system=system, messages=truncated
    )
    print("\nTRUNCATED:", response.content[0].text)

    # Token budget estimation
    def estimate_tokens(text):
        return len(text) // 4

    messages_text = [m["content"] for m in conversation if m["role"] == "user"]
    token_budget = 500
    messages_in_budget = 0
    tokens_used = 0
    for msg in reversed(messages_text):
        msg_tokens = estimate_tokens(msg)
        if tokens_used + msg_tokens <= token_budget:
            messages_in_budget += 1
            tokens_used += msg_tokens
        else:
            break
    print(f"\nWith {token_budget} token budget: can keep last {messages_in_budget} messages")

if __name__ == "__main__":
    main()
```

---

Next: [Lab 7: Summarization](lab7-summarization.md)
