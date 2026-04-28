# Lab 2: System Prompts — One Line Changes Everything

> **Mission:** Add a system prompt to transform a generic AI response into expert SRE triage advice.

---

## The Concept

The response from Lab 1 was generic — reads like a blog post, not what your senior SRE would say at 3 AM.

Add one line — a **system prompt** — and everything changes.

```
  WITHOUT system prompt:        WITH system prompt:
  "Consider increasing          "1. kubectl set resources
   memory allocation..."          deploy/api-server -c api
                                   --limits=memory=512Mi
  (blog post)                   2. kubectl rollout restart
                                   deploy/api-server -n prod
                                3. Add VPA for auto-tuning"

                                (senior SRE at 3 AM)
```

The system prompt tells the model WHO it is and HOW to respond — before it ever sees your question.

---

## What You'll Build

Send a real K8s OOM alert twice:
1. **Without** a system prompt (generic response)
2. **With** a system prompt: "You are a senior SRE" (expert triage)

Compare the two outputs side by side.

---

## Step 1: Define the Alert

This is a real-world Kubernetes alert — the kind you'd see in PagerDuty or Slack at 3 AM.

```python
alert = """Analyze this alert and give me a 3-step remediation plan:

ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)"""
```

---

## Step 2: Send WITHOUT System Prompt

Same as Lab 1 — just send the alert as a user message.

**Anthropic:**
```python
message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    messages=[{"role": "user", "content": alert}]
)
print("WITHOUT system prompt:")
print(message.content[0].text)
```

---

## Step 3: Send WITH System Prompt

Now add one parameter — the system prompt. This is the only change.

**Anthropic:**
```python
message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    system="You are a senior SRE with 10 years of Kubernetes experience. Be concise and actionable. Give kubectl commands, not general advice.",
    messages=[{"role": "user", "content": alert}]
)
print("WITH system prompt:")
print(message.content[0].text)
```

---

## How Each Provider Sets the System Prompt

| Provider | How to set it |
|----------|--------------|
| Anthropic | `system="You are a senior SRE..."` (separate parameter) |
| Google Gemini | `GenerativeModel("gemini-2.5-flash", system_instruction="...")` |
| OpenAI | `{"role": "system", "content": "..."}` as first message in the array |
| AWS Bedrock | `"system": [{"text": "..."}]` in the request body |
| MAF | `chat.add_system_message("...")` |

---

## Run It

```bash
python3 demos/{your-provider}/task2_system_prompts.py
```

---

## What Success Looks Like

**Without system prompt:** Generic advice — "consider increasing memory allocation," "review application code," "monitor resource usage." Reads like documentation.

**With system prompt:** Actionable kubectl commands, specific numbers, clear steps. Reads like your senior engineer's Slack message at 3 AM.

The difference is dramatic — same question, completely different quality.

---

## Key Takeaway

The system prompt is the most powerful lever you have. One line transforms a generic chatbot into a domain expert. The art of writing better prompts = **prompt engineering** (Episode 3 goes deep).

---

## Complete Code (Anthropic)
Without system, Claude has no instructions on who to be or how to respond. It defaults to its general helpful-assistant mode — which is why you get the generic blog-post answer.

If you get stuck, here's the full working script:

```python
#!/usr/bin/env python3
"""Task 2: System Prompts — One Line Changes Everything"""
import anthropic

def main():
    client = anthropic.Anthropic()

    alert = """Analyze this alert and give me a 3-step remediation plan:

ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)"""

    # Without system prompt
    print("WITHOUT system prompt:")
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": alert}]
    )
    print(message.content[0].text)

    # With system prompt
    print("\nWITH system prompt:")
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system="You are a senior SRE with 10 years of Kubernetes experience. Be concise and actionable.",
        messages=[{"role": "user", "content": alert}]
    )
    print(message.content[0].text)

if __name__ == "__main__":
    main()
```

---

Next: [Lab 3: Persona Swap](lab3-persona-swap.md)
