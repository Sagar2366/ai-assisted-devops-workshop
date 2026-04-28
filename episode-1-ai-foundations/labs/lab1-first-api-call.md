# Lab 1: Your First LLM API Call

> **Mission:** Send a Kubernetes question to an AI model and get a response — this is what ChatGPT does behind the scenes.

---

## The Concept
## GenAI — what is this whole thing?

GenAI is AI that **creates** new stuff — text, code, answers — instead of just labelling things. It's a new category of software that can write back to you.

> **Analogy:** Old AI: "Is this email spam? Yes/No." GenAI: "Write a reply to this email."

---

## LLM — the engine behind GenAI

An LLM (Large Language Model) is a program that has read almost everything ever written — books, docs, code, the internet — and learned how language works from all of it.

> **Analogy:** Imagine a student who read every textbook, every Stack Overflow answer, every Kubernetes doc — and can now answer any question from memory. That student is the LLM.

---

## Training — when the model went to school

Training is a one-time process where the company (Anthropic, OpenAI) feeds the model trillions of words and teaches it patterns. Thousands of GPUs. Weeks. Millions of dollars. Once done, the knowledge lives inside the model forever.

> **Analogy:** You studying for 12 years. You don't re-read every book before answering someone — you just know. Training already happened. You're not doing it.

---

## Inference — when you actually use the model

Inference is when you send a question and the model answers from its trained knowledge. One API call. Milliseconds. Fractions of a cent. This is your job — not training.

> **Analogy:** Your friend studied medicine for 7 years (training). You call them and ask "what's this rash?" — they answer instantly (inference). They don't re-read med school textbooks for each call.

---

## Tokens — the unit the model actually reads

The model doesn't read words — it reads chunks called tokens. Roughly 1 token per word. `OOMKilled` might be 3 tokens. Everything you send and receive is counted in tokens. You pay per token.

The **context window** is the max number of tokens that fit in one call (e.g. Claude = 200K). When the conversation gets too long, the oldest tokens fall off.

> **Analogy:** Like how a book is made of words, the model sees a book made of tokens. The context window is the max page count it can hold at once — when the book gets too long, old pages fall off.

---

## Prompt — everything you send to the model

A prompt has 3 layers:

1. **System prompt** — who the model is and how to behave
2. **Conversation history** — all past turns, which you manually include every call
3. **User message** — your actual question right now

The model has **zero memory** between calls — you carry the history yourself.

> **Analogy:** Like sending a letter with: a cover page ("You are a senior doctor"), all previous letters stapled behind it, and your new question on top. Every single letter must have the full stack — the doctor forgets everything the moment you leave the room.

---

## Prompt engineering — getting better answers by asking better

Same model, totally different output based on how you write the prompt. Add role, context, constraint, and output format. Vague in = vague out. Specific in = specific out.

| Vague prompt | Specific prompt |
|---|---|
| "Fix my car" | "My 2019 Honda Civic makes a grinding noise at 60 kmph on left turns — what's the exact issue and fix?" |
| Generic blog-post answer | Targeted diagnosis for your exact situation |

> **Analogy:** Same mechanic, completely different quality of answer — depending on how well you described the problem.

---

## Models — different sizes, different trade-offs

The same company ships multiple models. You pick based on the task complexity and cost budget. Same API call, different model string.

| Model tier | Speed | Cost | Use case |
|---|---|---|---|
| Opus / frontier | Slow | High | Complex reasoning, architecture decisions |
| Sonnet / mid | Balanced | Medium | Daily SRE tasks — good default |
| Haiku / small | Fast | Low | Simple classification, quick lookups |

> **Analogy:** Like doctors — a GP handles most things fast and cheap. A specialist is slower, costs more, but handles complex cases. You don't send every headache to a neurosurgeon.

---

## Billing — you pay per token, input + output

Both directions are billed separately. Bigger models cost more per token. Most SRE tasks cost fractions of a cent per call.

```
Total cost = (input tokens × input rate) + (output tokens × output rate)
```

Cost levers:
- Shorter prompts = fewer input tokens
- Right-sized model for the task = lower rate
- Avoid sending full log files as context every call

> **Analogy:** Like a phone call billed by the word — you pay for what you said AND what they said back. Rambling 10,000-word prompts = expensive calls.

---

## Hallucination — when the model confidently makes stuff up

The model's job is to produce the most likely next token — not to check if it's true. So sometimes it invents a command, flag, or fact with full confidence. It doesn't know it's wrong. You have to catch it.

```bash
# Example: this flag does not exist
kubectl rollout restart --graceful-period=30
# The model said it with full confidence. Always verify before running in prod.
```

> **Analogy:** Your brilliant friend who studied everything — but when they don't know something, instead of saying "I don't know", they confidently make up a plausible-sounding answer. The danger is they sound equally confident when they're right AND when they're wrong.

**Rule: never run an AI-generated command in production without reading it first.**

---

## The whole story in one paragraph

GenAI uses an LLM — trained once on everything — that you use via inference. You send a prompt (measured in tokens), billed per token, shaped by prompt engineering, through a model sized to your needs. It answers from memory. Sometimes that memory is wrong — that's hallucination. Verify before you run anything.


---

## What You'll Build

A Python script that sends a Kubernetes question to an LLM and prints the response. One API call — that's it.

---

## Step 1: Import the SDK

Create a new file `task1_first_api_call.py`:

**Anthropic:**
```python
import anthropic
```

**Google Gemini:**
```python
import google.generativeai as genai
```

**OpenAI:**
```python
from openai import OpenAI
```

---

## Step 2: Create the Client

The client is your connection to the AI provider. It handles authentication using the API key you exported in Lab 0.

**Anthropic:**
```python
client = anthropic.Anthropic()
```

**Google Gemini:**
```python
model = genai.GenerativeModel("gemini-2.5-flash")
```

**OpenAI:**
```python
client = OpenAI()
```

---

## Step 3: Send a Kubernetes Question

This is the actual API call. You send a prompt, the model returns a response.

**Anthropic:**
```python
message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What is Kubernetes and why do DevOps engineers use it?"}
    ]
)
```

**Google Gemini:**
```python
response = model.generate_content("What is Kubernetes and why do DevOps engineers use it?")
```

**OpenAI:**
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "What is Kubernetes and why do DevOps engineers use it?"}
    ]
)
```

---

## Step 4: Print the Response

Every provider wraps the response differently. This is the one line you'll use everywhere:

**Anthropic:**
```python
print(message.content[0].text)
```

**Google Gemini:**
```python
print(response.text)
```

**OpenAI:**
```python
print(response.choices[0].message.content)
```

---

## Response Extraction Cheat Sheet

| Provider | How to get the text |
|----------|-------------------|
| Anthropic | `message.content[0].text` |
| Google Gemini | `response.text` |
| OpenAI | `response.choices[0].message.content` |
| AWS Bedrock | `result["content"][0]["text"]` |
| MAF | Returned directly as string |

---

## Run It

```bash
python3 demos/{your-provider}/task1_first_api_call.py
```

---

## What Success Looks Like

The AI explains Kubernetes — container orchestration, scaling, self-healing, declarative config. The exact wording will vary each time (LLMs are non-deterministic), but you should get a clear, detailed explanation.

---

## Key Takeaway

An LLM API call = send a prompt (tokens in), get a response (tokens out). That is inference. But the response is generic — it reads like a blog post, not expert SRE advice. Lab 2 fixes that.

---

## Complete Code (Anthropic)

If you get stuck, here's the full working script:

```python
#!/usr/bin/env python3
"""Task 1: Your First API Call — Anthropic Claude"""
import anthropic

def main():
    client = anthropic.Anthropic()

    # Experiment 1: Basic API call
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "What is Kubernetes and why do DevOps engineers use it?"}
        ]
    )
    print(message.content[0].text)

    # Experiment 2: Different question
    message2 = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Explain Prometheus in 3 sentences"}
        ]
    )
    print(message2.content[0].text)

    # Experiment 3: Token usage
    print(f"Input tokens:  {message2.usage.input_tokens}")
    print(f"Output tokens: {message2.usage.output_tokens}")

if __name__ == "__main__":
    main()
```

---

Next: [Lab 2: System Prompts](lab2-system-prompts.md)
