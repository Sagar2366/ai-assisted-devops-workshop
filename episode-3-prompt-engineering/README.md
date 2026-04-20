# Episode 3: Prompt Engineering for DevOps

- 5 prompt patterns: Role+Context, Few-shot, Chain of Thought, Structured Output, Safety Guardrails
- 4 production-ready prompt templates for SRE workflows
- Prompt testing framework with automated assertions

```
Every prompt = a briefing document for a new hire:

┌──────────────────────────────────┐
│  1. ROLE       → Who are you?    │
│  2. CONTEXT    → What do we do?  │
│  3. TASK       → What to do now? │
│  4. FORMAT     → How to respond? │
│  5. SAFETY     → What to avoid?  │
└──────────────────────────────────┘
Miss one section = bad output.
```

## Setup

```bash
export ANTHROPIC_API_KEY="your-key-here"
pip install anthropic
```

## Files

| File | Description |
|------|-------------|
| `prompt_patterns.py` | All 5 prompt patterns with bad vs good comparisons |
| `prompt_templates.py` | 4 production templates: Incident Commander, Code Reviewer, Postmortem Writer, Terraform Reviewer |
| `prompt_testing.py` | Automated prompt testing framework |
