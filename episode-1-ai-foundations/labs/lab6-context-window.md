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

Next: [Lab 7: Summarization](lab7-summarization.md)
