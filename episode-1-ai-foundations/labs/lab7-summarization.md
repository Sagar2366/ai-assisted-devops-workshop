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
    model="claude-sonnet-4-6-latest",
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
    model="claude-sonnet-4-6-latest",
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

Next: [Lab 8: Personalization](lab8-personalization.md)
