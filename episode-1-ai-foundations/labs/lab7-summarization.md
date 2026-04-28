# Lab 7: Summarization — Smart Memory

> **Mission:** Compress a long SRE conversation into a summary and prove the AI retains key context at a fraction of the token cost.

---

## The Concept

Truncation throws away old messages. Summarization compresses them instead.

```
  BEFORE (10 turns, ~2000 tokens):
  "My name is Sagar, I'm an SRE at Acme..."
  "We use EKS with 50 microservices..."
  "The payment pod keeps crashing..."
  "Budget is limited to $500/month..."

  AFTER SUMMARIZATION (1 paragraph, ~200 tokens):
  "Sagar is an SRE at Acme Corp running EKS with 50
   microservices. Payment pod OOM at 256Mi. Budget: $500/month."
```

10 turns become 2 sentences. The AI still knows name, stack, constraints — at a fraction of the token cost.

---

## What You'll Build

1. Take the long SRE conversation from Lab 6
2. Ask the model to summarize it
3. Start a new conversation with only the summary
4. Ask follow-up questions — prove the AI still has the key context

---

## Step 1: Summarize the Old Conversation

```python
summary_prompt = """Summarize this conversation in 2-3 sentences.
Preserve: names, tools/platforms mentioned, specific problems, constraints (budget, team size), and any decisions made.

Conversation:
"""

# Append the full conversation history to the prompt
for msg in conversation:
    summary_prompt += f"\n{msg['role']}: {msg['content']}"
```

**Anthropic:**
```python
message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=256,
    messages=[{"role": "user", "content": summary_prompt}]
)
summary = message.content[0].text
print("SUMMARY:", summary)
```

---

## Step 2: Start a New Conversation with the Summary

Inject the summary into the system prompt of a fresh conversation:

```python
system_prompt = f"""You are a senior SRE assistant. Here is context from a previous conversation:

{summary}

Use this context to personalize your responses."""
```

---

## Step 3: Ask a Follow-Up Question

```python
message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    system=system_prompt,
    messages=[{"role": "user", "content": "What's the most cost-effective way to fix my problem?"}]
)
print(message.content[0].text)
```

---

## Run It

```bash
python3 demos/{your-provider}/task7_summarization.py
```

---

## What Success Looks Like

The AI answers referencing Sagar's name, EKS setup, the payment pod OOM issue, and the $500/month budget — even though it's a fresh conversation. All that context came from the 2-sentence summary, not the original 10 turns.

Compare token usage: the summary uses ~200 tokens vs ~2000 for the full history. Same quality, 90% fewer tokens.

---

## Key Takeaway

Summarization > truncation. Compress old messages instead of dropping them. This is how production agents handle long-running incident threads without blowing the context window.

---

## Complete Code (Anthropic)

If you get stuck, here's the full working script:

```python
#!/usr/bin/env python3
"""Task 7: Conversation Summarization"""
import anthropic

def main():
    client = anthropic.Anthropic()
    system = "You are a senior SRE assistant that remembers conversation details."

    # Build 10-turn SRE conversation
    topics = [
        "My name is Sagar and I'm an SRE at Acme Corp",
        "We run EKS with 50 microservices in production",
        "I'm looking into AI tools for incident response",
        "The payment-service pod keeps OOMing after deploys",
        "Memory limit is 256Mi but usage peaks at 255Mi",
        "We use ArgoCD for deployments and Prometheus for monitoring",
        "Our budget for AI tooling is $500 per month",
        "Team of 5 SREs covering 3 time zones",
        "We need automated triage to reduce MTTR",
        "Biggest pain point is getting paged at 3 AM for the same OOM issue"
    ]

    conversation = []
    conversation_log = []
    for topic in topics:
        conversation.append({"role": "user", "content": topic})
        response = client.messages.create(
            model="claude-opus-4-7", max_tokens=256,
            system=system, messages=conversation
        )
        reply = response.content[0].text
        conversation.append({"role": "assistant", "content": reply})
        conversation_log.append({"user": topic, "assistant": reply})

    # Split: old (first 7) vs recent (last 3)
    old_exchanges = conversation_log[:7]
    recent_exchanges = conversation_log[7:]

    # Summarize old exchanges
    old_text = ""
    for ex in old_exchanges:
        old_text += f"User: {ex['user']}\nAssistant: {ex['assistant']}\n\n"

    summary_prompt = f"""Summarize this conversation in 2-3 sentences.
Preserve: names, tools/platforms mentioned, specific problems, constraints (budget, team size), and any decisions made.

Conversation:
{old_text}

Create a concise summary:"""

    summary_response = client.messages.create(
        model="claude-opus-4-7", max_tokens=256,
        messages=[{"role": "user", "content": summary_prompt}]
    )
    summary_text = summary_response.content[0].text
    print(f"Summary: {summary_text}")

    # Inject summary into system prompt
    summary_system = f"""{system}

Here is context from a previous conversation:
{summary_text}

Use this context to personalize your responses."""

    # Test with summary
    new_conversation = []
    for ex in recent_exchanges:
        new_conversation.append({"role": "user", "content": ex["user"]})
        r = client.messages.create(
            model="claude-opus-4-7", max_tokens=256,
            system=summary_system, messages=new_conversation
        )
        new_conversation.append({"role": "assistant", "content": r.content[0].text})

    test_questions = ["What's my name and company?", "What tools do we use for deployments?", "What's our monthly budget?"]
    print("\nWith Summary:")
    for q in test_questions:
        new_conversation.append({"role": "user", "content": q})
        r = client.messages.create(
            model="claude-opus-4-7", max_tokens=128,
            system=summary_system, messages=new_conversation
        )
        new_conversation.append({"role": "assistant", "content": r.content[0].text})
        print(f"  Q: {q} -> A: {r.content[0].text[:80]}")

if __name__ == "__main__":
    main()
```

---

Next: [Lab 8: Personalization](lab8-personalization.md)
