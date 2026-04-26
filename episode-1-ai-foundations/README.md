# Episode 1: AI Foundations for SRE & DevOps

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

<!-- [Watch on YouTube](https://youtube.com/...) -->

---

## What You'll Learn

Every concept is taught through code — you run it first, then understand what happened.

- Make your first LLM API call (what ChatGPT does behind the scenes)
- System prompts — one line changes everything
- Persona swap — same K8s alert, 3 different expert analyses
- Where LLMs break — hallucination, no live access, no action
- Multi-turn conversations — how memory works at the API level
- Context window management — what happens when conversations get too long

**40 hands-on labs** across 5 frameworks. Each lab has TODO markers (`___`) with hints — fill in the blanks, run the script, see the result.

---

## Prerequisites

- Python 3.10+
- At least one API key (Google Gemini is free)

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/Sagar2366/ai-assisted-devops-workshop.git
cd ai-assisted-devops-workshop/episode-1-ai-foundations
```

### 2. Set up your API key

```bash
# Google Gemini (FREE — recommended to get started)
export GOOGLE_API_KEY="your-key-here"   # Get free key from aistudio.google.com
pip install google-generativeai
```

Other providers (optional):

```bash
# Anthropic Claude
export ANTHROPIC_API_KEY="your-key-here"   # console.anthropic.com
pip install anthropic

# OpenAI GPT
export OPENAI_API_KEY="your-key-here"      # platform.openai.com
pip install openai

# AWS Bedrock
pip install boto3
aws configure

# Microsoft Agent Framework (Semantic Kernel)
pip install semantic-kernel
```

### 3. Verify your environment

```bash
python3 demos/verify_environment.py
```

### 4. Run your first lab

```bash
python3 demos/google/task1_first_api_call.py
```

---

## How It Works

Each task is a Python script with `___` blanks and `# TODO` hints. You fill in the blanks, run the script, and see the AI respond with SRE-themed output.

```
You fill the blank → Run the script → AI responds → You learn the concept
```

Example (task1 — first API call):

```python
# TODO 1: Create the API request
response = client.messages.create(
    model=___,           # TODO: Use "claude-sonnet-4-6-latest"
    max_tokens=1024,
    messages=[{"role": "user", "content": alert}]
)
```

You replace `___` with the correct value, run it, and the LLM triages a K8s pod crash alert.

---

## Hands-On Labs

### Phase 1: Basics (Tasks 1-4)

| Task | File | What You Learn |
|------|------|----------------|
| 1 | `task1_first_api_call.py` | Your first LLM API call — send a K8s alert, get SRE triage |
| 2 | `task2_system_prompts.py` | System prompts — one line turns a generic response into expert advice |
| 3 | `task3_persona_swap.py` | Same alert, 3 personas — SRE, Security Engineer, Cost Analyst |
| 4 | `task4_limitations.py` | Hallucination test — ask about fake K8s resources, see what breaks |

```bash
python3 demos/google/task1_first_api_call.py
python3 demos/google/task2_system_prompts.py
python3 demos/google/task3_persona_swap.py
python3 demos/google/task4_limitations.py
```

### Phase 2: Memory & Context (Tasks 5-8)

| Task | File | What You Learn |
|------|------|----------------|
| 5 | `task5_conversation_history.py` | Multi-turn conversations — AI remembers context across messages |
| 6 | `task6_context_window.py` | Sliding window truncation — what happens when conversations get too long |
| 7 | `task7_summarization.py` | Compress old messages into summaries, keep key info |
| 8 | `task8_personalization.py` | Extract user profile, personalize SRE responses |

```bash
python3 demos/google/task5_conversation_history.py
python3 demos/google/task6_context_window.py
python3 demos/google/task7_summarization.py
python3 demos/google/task8_personalization.py
```

### Compare All Providers Side-by-Side

```bash
python3 demos/all_providers.py
```

Sends the same K8s alert through every configured provider — skips any you haven't set up.

---

## Supported Frameworks

| Framework | Folder | Auth | Cost |
|-----------|--------|------|------|
| Google Gemini | `demos/google/` | `GOOGLE_API_KEY` | **Free** |
| Anthropic Claude | `demos/anthropic/` | `ANTHROPIC_API_KEY` | Paid |
| OpenAI GPT | `demos/openai/` | `OPENAI_API_KEY` | Paid |
| AWS Bedrock | `demos/bedrock/` | IAM credentials | Paid |
| MAF (Semantic Kernel) | `demos/maf/` | `OPENAI_API_KEY` | Paid |

Pick one framework. Complete all 8 tasks. Then try a second — same tasks, different SDK. You'll see the pattern is identical.

---

## File Structure

```
episode-1-ai-foundations/
├── demos/
│   ├── verify_environment.py          # Check your setup
│   ├── all_providers.py               # Side-by-side comparison
│   ├── google/                        # Google Gemini (FREE)
│   │   ├── task1_first_api_call.py
│   │   ├── task2_system_prompts.py
│   │   ├── task3_persona_swap.py
│   │   ├── task4_limitations.py
│   │   ├── task5_conversation_history.py
│   │   ├── task6_context_window.py
│   │   ├── task7_summarization.py
│   │   └── task8_personalization.py
│   ├── anthropic/                     # Anthropic Claude
│   │   └── task1–task8
│   ├── openai/                        # OpenAI GPT
│   │   └── task1–task8
│   ├── bedrock/                       # AWS Bedrock
│   │   └── task1–task8
│   └── maf/                           # Semantic Kernel
│       └── task1–task8
└── README.md
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'anthropic'` | Run `pip install anthropic` (or whichever SDK) |
| `AuthenticationError` / `Invalid API key` | Check your `export` — key must be set in the same terminal session |
| `RateLimitError` | Wait 60 seconds and retry, or switch to Google Gemini (generous free tier) |
| `Connection refused` (Bedrock) | Run `aws configure` and ensure your IAM role has `bedrock:InvokeModel` permission |
| Script runs but output is empty | Check that you filled in all `___` blanks — the script won't work with placeholders |

---

## No API Key? Free Alternatives

**Google Gemini (free API — recommended):**
```bash
pip install google-generativeai
export GOOGLE_API_KEY="your-key"  # Free from aistudio.google.com
python3 demos/google/task1_first_api_call.py
```

**Ollama (local, completely free):**
```bash
ollama run llama3.2:3b "You are a senior SRE. A pod named api-server has restarted 15 times. Last log: 'out of memory'. Memory limit 256Mi, usage 255Mi. Give a 3-step fix."
```

---

## Cost

This entire episode costs **$0.00** if you use Google Gemini (free tier). With paid providers: ~$0.25 total for all 8 tasks.

---

## Homework

1. Complete all 8 tasks for at least one provider (Google Gemini recommended — it's free)
2. Pick a second provider and redo tasks 1-4 — compare the SDK patterns
3. Run `demos/all_providers.py` — see all providers side by side
4. Try the hallucination test (task 4) with your own DevOps questions
5. Read [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) by Anthropic

---

## What Comes Next

| Episode | Topic | What You Build |
|---------|-------|----------------|
| **Ep 2** | Local & Remote LLMs | Ollama local + Claude cloud + Bedrock enterprise |
| **Ep 3** | Prompt Engineering | Zero-shot, few-shot, chain-of-thought for DevOps |
| **Ep 4** | Tools, Agents & MCP | Give AI hands — tool use, function calling, MCP servers |
| **Ep 5** | DevOps Copilot | RAG, embeddings, vector DBs — AI that searches YOUR runbooks |

> Tool Use (tasks 9-12) continues in Episode 4. Multi-Agent Orchestration (tasks 13-16) continues in Episode 11.

<!-- [Watch Episode 2 →](../episode-2-llms-local-remote/) -->

---

**Built by [Sagar Utekar](https://github.com/Sagar2366)** | CNCF Ambassador | Kubestronaut
