# Episode 1: AI Foundations for SRE & DevOps

- The AI timeline that matters for DevOps: ML → LLMs → GenAI → Agentic AI
- Core concepts: Tokens, Context Windows, Temperature, System Prompts
- Agents = LLM (brain) + Tools (hands) + Reasoning Loop (autonomy)
- MCP (Model Context Protocol) — the universal adapter
- Your first Claude API call with SRE context

```
BEFORE (Traditional SRE)              AFTER (AI-Augmented SRE)

Alert fires                            Alert fires
    ↓                                      ↓
Dashboard → Human reads                LLM receives alert payload
    ↓                                      ↓
Human runs kubectl                     LLM runs kubectl (via tools)
    ↓                                      ↓
Human diagnoses                        LLM reasons about root cause
    ↓                                      ↓
Human applies fix                      LLM applies fix (with guardrails)
    ↓                                      ↓
Human writes postmortem at 4 PM        LLM generates postmortem immediately

The PAYLOAD destination shifted        Same infra. New destination.
from human dashboards to AI agents.    That is the only change.
```

## Setup

```bash
export ANTHROPIC_API_KEY="your-key-here"
pip install anthropic
```

## Files

| File | Description |
|------|-------------|
| `first_api_call.py` | First DevOps-aware Claude API call |
