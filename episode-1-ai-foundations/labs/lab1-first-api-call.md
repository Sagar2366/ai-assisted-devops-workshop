# Lab 1: Your First LLM API Call

> **Mission:** Send a Kubernetes question to an AI model and get a response — this is what ChatGPT does behind the scenes.

---

## The Concept

You open ChatGPT, type a question, get an answer. But what is actually happening?

An **LLM** (Large Language Model) is the AI brain behind ChatGPT, Claude, Gemini. Your input is a **prompt**. The model reads it as **tokens** — roughly one token per word.

```
"The pod is OOMKilled"

  The | pod | is | OOM | Kill | ed
   1     2    3    4      5     6  = 6 tokens
```

You pay per token. The model has a max capacity called the **context window** — how many tokens fit in one request.

When you send a prompt and get a response — that is **inference** (your part). The millions of dollars spent teaching the model — that is **training** (their part).

```
  TRAINING (their part)         INFERENCE (your part)

  Weeks on GPU clusters         Milliseconds per call
  Costs millions                Costs fractions of a cent
  You DON'T do this             You DO this
```

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
    model="claude-sonnet-4-6-latest",
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

Next: [Lab 2: System Prompts](lab2-system-prompts.md)
