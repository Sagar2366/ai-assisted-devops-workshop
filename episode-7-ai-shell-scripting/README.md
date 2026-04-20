# Episode 7: AI-Assisted Shell Scripting & Automation

- Generate production bash scripts from English descriptions
- Fix broken scripts automatically (find bugs, suggest fixes)
- Convert one-liners to parameterized production scripts

## Setup

```bash
export ANTHROPIC_API_KEY="your-key-here"
pip install anthropic
```

## Files

| File | Description |
|------|-------------|
| `generator.py` | English descriptions to bash scripts with error handling and logging |
| `fixer.py` | Broken script analyzer — finds bugs, suggests fixes |
| `converter.py` | One-liner to production script converter |
