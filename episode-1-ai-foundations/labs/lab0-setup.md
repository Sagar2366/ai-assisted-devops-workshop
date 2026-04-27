# Lab 0: Environment Setup

> **Mission:** Get Python + an AI SDK installed and verified before writing any code.

---

## What You Need

- Python 3.10+
- At least one API key (Google Gemini is free)

---

## Step 1: Pick a Provider

| Provider | Cost | Why Pick This |
|----------|------|---------------|
| **Google Gemini** | **Free** | No credit card needed. Best for getting started. |
| Anthropic Claude | Paid | Best reasoning quality. Used in the video demos. |
| OpenAI GPT | Paid | Most popular. Largest ecosystem. |
| AWS Bedrock | Paid | Enterprise. Use if your org already runs on AWS. |
| MAF (Semantic Kernel) | Paid | Microsoft stack. Uses OpenAI under the hood. |

---

## Step 2: Install the SDK

```bash
# Google Gemini (FREE — recommended to start)
pip install google-generativeai

# OR Anthropic Claude
pip install anthropic

# OR OpenAI GPT
pip install openai

# OR AWS Bedrock
pip install boto3

# OR Microsoft Semantic Kernel
pip install semantic-kernel
```

---

## Step 3: Set Your API Key

```bash
# Google Gemini — free key from aistudio.google.com
export GOOGLE_API_KEY="your-key-here"

# Anthropic Claude — key from console.anthropic.com
export ANTHROPIC_API_KEY="your-key-here"

# OpenAI GPT — key from platform.openai.com
export OPENAI_API_KEY="your-key-here"

# AWS Bedrock — use AWS CLI
aws configure
```

**Important:** The key must be set in the same terminal session where you run the scripts. If you open a new terminal, export again.

---

## Step 4: Verify

```bash
python3 -c "import anthropic; print('Anthropic SDK ready')"
# OR
python3 -c "import google.generativeai; print('Gemini SDK ready')"
# OR
python3 -c "import openai; print('OpenAI SDK ready')"
```

If you see `ModuleNotFoundError`, re-run the pip install from Step 2.

---

## You're Ready

Move on to [Lab 1: Your First API Call](lab1-first-api-call.md).

---

**Cost for this entire episode:** $0.00 with Google Gemini free tier. ~$0.25 total with paid providers.
