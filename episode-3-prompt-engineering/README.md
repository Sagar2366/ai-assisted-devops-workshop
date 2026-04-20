# Episode 3: Prompt Engineering for DevOps

- 5 prompt patterns: Role+Context, Few-shot, Chain of Thought, Structured Output, Safety Guardrails
- 4 production-ready prompt templates for SRE workflows
- Prompt testing framework with automated assertions

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
