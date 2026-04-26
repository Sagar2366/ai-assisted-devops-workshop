# Episode 1: AI Foundations for SRE & DevOps

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

<!-- [Watch on YouTube](https://youtube.com/...) -->

---

## What You'll Learn

Every concept is taught through code — you run it first, then understand what happened. **2 phases x 5 frameworks = 40 hands-on labs.** Each lab has TODO markers (`___`) with hints. Fill in the blanks, run the script, see the result.

| Phase | Tasks | What You Learn |
|-------|-------|----------------|
| **Phase 1: Basics** | task1-task4 | API calls, system prompts, persona swap, LLM limitations |
| **Phase 2: Memory & Context** | task5-task8 | Multi-turn conversation, context window, summarization, personalization |

> **Tool Use** (tasks 9-12) continues in Episode 4. **Multi-Agent Orchestration** (tasks 13-16) continues in Episode 11.

| Framework | SDK | Auth | Cost |
|-----------|-----|------|------|
| **Google Gemini** | `google-generativeai` | `GOOGLE_API_KEY` | **Free** |
| **Anthropic Claude** | `anthropic` | `ANTHROPIC_API_KEY` | Paid |
| **OpenAI GPT** | `openai` | `OPENAI_API_KEY` | Paid |
| **AWS Bedrock** | `boto3` | IAM credentials | Paid |
| **MAF (Semantic Kernel)** | `semantic-kernel` | `OPENAI_API_KEY` | Paid |

---

## Getting Started

### Prerequisites

```bash
# Google Gemini (free — recommended for getting started)
export GOOGLE_API_KEY="your-key-here"     # Free from aistudio.google.com
pip install google-generativeai

# Anthropic (primary paid option)
export ANTHROPIC_API_KEY="your-key-here"   # Get from console.anthropic.com
pip install anthropic

# OpenAI (optional)
export OPENAI_API_KEY="your-key-here"      # Get from platform.openai.com
pip install openai

# AWS Bedrock (optional — enterprise)
pip install boto3
aws configure

# Microsoft Agent Framework (optional)
pip install semantic-kernel
```

### Verify Your Environment

```bash
python3 demos/verify_environment.py
```

---

## Hands-On Labs

Pick a framework and work through all 8 tasks. Then try a second framework — same tasks, different SDK patterns.

### Phase 1: Basics (Tasks 1-4)

| Task | What It Teaches |
|------|----------------|
| `task1_first_api_call.py` | Your first LLM API call — what ChatGPT does behind the scenes |
| `task2_system_prompts.py` | System prompts change everything — one line, different expert |
| `task3_persona_swap.py` | Same alert, 3 personas — SRE, Security, Cost Analyst |
| `task4_limitations.py` | Hallucination, no live access, no execution |

```bash
# Google Gemini (free!)
python3 demos/google/task1_first_api_call.py
python3 demos/google/task2_system_prompts.py
python3 demos/google/task3_persona_swap.py
python3 demos/google/task4_limitations.py

# Anthropic Claude
python3 demos/anthropic/task1_first_api_call.py
# ... same pattern

# OpenAI / Bedrock / MAF — same task names in each folder
```

### Phase 2: Memory & Context (Tasks 5-8)

| Task | What It Teaches |
|------|----------------|
| `task5_conversation_history.py` | Multi-turn conversations — maintaining message history |
| `task6_context_window.py` | Sliding window truncation, token budgets |
| `task7_summarization.py` | Compress old messages, keep key info |
| `task8_personalization.py` | Extract user profile, personalize responses |

```bash
python3 demos/google/task5_conversation_history.py
python3 demos/google/task6_context_window.py
python3 demos/google/task7_summarization.py
python3 demos/google/task8_personalization.py
```

### Side-by-Side Comparison

```bash
# Same alert through ALL providers — skips any not configured
python3 demos/all_providers.py
```

### No API Key? Free Alternatives

**Google Gemini (free API — recommended):**
```bash
pip install google-generativeai
export GOOGLE_API_KEY="your-key"  # Free from aistudio.google.com
python3 demos/google/task1_first_api_call.py
```

**Ollama (local, free):**
```bash
ollama run llama3.2:3b "You are a senior SRE. A pod named api-server has restarted 15 times. Last log: 'out of memory'. Memory limit 256Mi, usage 255Mi. Give a 3-step fix."
```

---

## File Structure

```
demos/
├── verify_environment.py              # Check your setup
├── all_providers.py                   # Side-by-side comparison
├── google/                            # 8 tasks — Google Gemini (FREE)
│   ├── task1_first_api_call.py
│   ├── task2_system_prompts.py
│   ├── task3_persona_swap.py
│   ├── task4_limitations.py
│   ├── task5_conversation_history.py
│   ├── task6_context_window.py
│   ├── task7_summarization.py
│   └── task8_personalization.py
├── anthropic/                         # 8 tasks — Anthropic Claude
│   └── task1–task8 (same structure)
├── openai/                            # 8 tasks — OpenAI GPT
│   └── task1–task8 (same structure)
├── bedrock/                           # 8 tasks — AWS Bedrock
│   └── task1–task8 (same structure)
└── maf/                               # 8 tasks — Semantic Kernel
    └── task1–task8 (same structure)
```

---

## What's Covered in Theory (Hands-On in Later Episodes)

Episode 1 introduces these concepts in theory — you'll build them hands-on in later episodes:

| Concept | Theory in Ep 1 | Hands-On In |
|---------|---------------|-------------|
| Tool Use / Function Calling | Act 4 | **Episode 4** |
| Prompt Engineering (zero-shot, few-shot, chain-of-thought) | Act 2 | **Episode 3** |
| RAG, Embeddings, Vector DBs | Act 5 | **Episode 5** |
| LangChain | Act 5 | **Episode 4-5** |
| LangGraph | Act 5 | **Episode 4, 11** |
| MCP (Model Context Protocol) | Act 5 | **Episode 4** |
| Multi-Agent Orchestration | Act 4 | **Episode 11** |

---

## Cost

This entire episode costs **$0.00** if you use Google Gemini (free tier). With paid providers: ~$0.25.

---

## Homework

- Get your API key (free: aistudio.google.com, or paid: console.anthropic.com)
- Complete all 8 tasks for at least one provider
- Try a second provider — compare the SDK patterns
- Try the hallucination test with your own questions
- Read [Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents) by Anthropic

---

## What's Next

**Episode 2: Local & Remote LLMs** — Set up Ollama for free local inference, Claude API for cloud, Bedrock for enterprise, and Gemini for free cloud. Four backends, one unified client.

<!-- [Watch Episode 2 →](../episode-2-llms-local-remote/) -->
