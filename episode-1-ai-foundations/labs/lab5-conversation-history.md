# Lab 5: Conversation History — Memory

> **Mission:** Build a multi-turn K8s troubleshooting conversation where the AI remembers what you said in previous messages.

---

## The Concept

Every API call is independent. The model has no memory between calls.

Watch — two separate API calls:

```python
# Call 1
response = ask("My name is Sagar and I am an SRE at Acme Corp.")
# AI: "Nice to meet you, Sagar!"

# Call 2 — fresh request, no history
response = ask("What is my name and where do I work?")
# AI: "I don't know your name or where you work."
```

It forgot your name instantly. Every call starts fresh. That's a chatbot.

**The fix:** Send the full conversation history with every request.

```
  SHORT-TERM MEMORY              LONG-TERM MEMORY
  (within this conversation)     (across sessions)

  "Checked logs - OOM after      "payment-svc OOMed 3 times
   deploy #847."                  this month. Same root cause."

  Lives in: context window       Lives in: external store
```

Every message — yours AND the AI's — goes back in the next request. There is no magic. You manage the history yourself.

---

## What You'll Build

A multi-turn K8s troubleshooting conversation:
- Message 1: Describe the OOM problem
- Message 2: Ask about logs
- Message 3: Ask for a fix

The AI remembers everything from previous turns because you send the full history each time.

---

## Step 1: Start the Conversation

```python
conversation = []

# Turn 1: Describe the problem
conversation.append({
    "role": "user",
    "content": "I'm seeing OOM kills on my api-server pod in production. Memory limit is 256Mi, usage hits 255Mi."
})
```

---

## Step 2: Send and Append the Response

**Anthropic:**
```python
message = client.messages.create(
    model="claude-sonnet-4-6-latest",
    max_tokens=1024,
    messages=conversation
)
response_text = message.content[0].text

# Append the AI's response to history
conversation.append({"role": "assistant", "content": response_text})
print("Turn 1:", response_text)
```

---

## Step 3: Continue the Conversation

```python
# Turn 2: Ask about logs — AI remembers the OOM context
conversation.append({
    "role": "user",
    "content": "What should I look for in the logs to find the root cause?"
})

message = client.messages.create(
    model="claude-sonnet-4-6-latest",
    max_tokens=1024,
    messages=conversation
)
response_text = message.content[0].text
conversation.append({"role": "assistant", "content": response_text})
print("Turn 2:", response_text)

# Turn 3: Ask for a fix — AI remembers both previous turns
conversation.append({
    "role": "user",
    "content": "Give me the kubectl commands to fix this."
})
# ... same pattern
```

---

## How Each Provider Handles History

| Provider | How memory works |
|----------|----------------|
| Anthropic | You manage a `messages` list, append each turn, send the full list |
| Google Gemini | `model.start_chat()` manages history automatically |
| OpenAI | You manage a `messages` list, same as Anthropic |
| AWS Bedrock | You manage a `messages` list, same as Anthropic |
| MAF | `ChatHistory()` object — add user and assistant messages |

---

## Run It

```bash
python3 demos/{your-provider}/task5_conversation_history.py
```

---

## What Success Looks Like

Each turn builds on the previous one. In Turn 3, when you ask for kubectl commands, the AI references the specific pod name, memory limit, and OOM context from Turn 1 — without you repeating it. It remembers because you sent the full history.

---

## Key Takeaway

Memory at the API level is manual — you send the full conversation every time. The model itself remembers nothing between calls. But what happens when the conversation gets too long to fit?

---

## Complete Code (Anthropic)

If you get stuck, here's the full working script:

```python
#!/usr/bin/env python3
"""Task 5: Conversation History — Multi-Turn K8s Troubleshooting"""
import anthropic

def main():
    client = anthropic.Anthropic()
    system = "You are a senior SRE assistant. Remember details from the conversation."
    conversation = []

    # Turn 1: Describe the problem
    message_1 = "I'm seeing OOM kills on my api-server pod in production. Memory limit is 256Mi, usage hits 255Mi."
    conversation.append({"role": "user", "content": message_1})
    response = client.messages.create(
        model="claude-sonnet-4-6-latest", max_tokens=512,
        system=system, messages=conversation
    )
    assistant_reply = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_reply})
    print(f"User: {message_1}")
    print(f"Agent: {assistant_reply}")

    # Turn 2: Ask about logs
    message_2 = "What should I look for in the logs to find the root cause?"
    conversation.append({"role": "user", "content": message_2})
    response = client.messages.create(
        model="claude-sonnet-4-6-latest", max_tokens=512,
        system=system, messages=conversation
    )
    assistant_reply = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_reply})
    print(f"\nUser: {message_2}")
    print(f"Agent: {assistant_reply}")

    # Turn 3: Ask for the fix
    message_3 = "Give me the kubectl commands to fix this."
    conversation.append({"role": "user", "content": message_3})
    response = client.messages.create(
        model="claude-sonnet-4-6-latest", max_tokens=512,
        system=system, messages=conversation
    )
    assistant_reply = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_reply})
    print(f"\nUser: {message_3}")
    print(f"Agent: {assistant_reply}")

    print(f"\nTotal messages in history: {len(conversation)}")

if __name__ == "__main__":
    main()
```

---

Next: [Lab 6: Context Window Management](lab6-context-window.md)
