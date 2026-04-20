# Episode 2: Local & Remote LLMs — Ollama, Claude API, Bedrock

- Run LLMs locally with Ollama (free, private, air-gapped)
- Claude API with tool use — the foundation for agents
- Prompt caching — save 90% on repeated calls
- AWS Bedrock — enterprise multi-model access
- Unified client that switches backends with one parameter

## Setup

```bash
export ANTHROPIC_API_KEY="your-key-here"
pip install anthropic openai requests boto3

# Local LLM
brew install ollama
ollama serve &
ollama pull qwen2.5-coder:7b
```

## Files

| File | Description |
|------|-------------|
| `ollama_direct.py` | Query local Ollama via HTTP API |
| `ollama_openai_compat.py` | Use OpenAI SDK with local Ollama |
| `claude_tool_use.py` | Claude with kubectl/helm tool use |
| `prompt_caching.py` | Prompt caching demo — cache write vs cache hit |
| `bedrock_api.py` | AWS Bedrock with Claude via IAM auth |
| `unified_llm_client.py` | Unified client: Ollama / Claude / Bedrock |
