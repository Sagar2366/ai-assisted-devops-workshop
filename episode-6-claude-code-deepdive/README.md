# Episode 6: Claude Code Deep Dive for DevOps

- CLAUDE.md for persistent infrastructure context
- MCP integration with your K8s cluster
- PreToolUse safety hooks — block dangerous commands before execution
- PostToolUse audit hooks — log all tool executions to JSON

```
Contextual Exoskeleton — configure once, use daily:

  CLAUDE.md     → MEMORY      (infra context, runbooks, conventions)
  MCP Servers   → HANDS       (K8s cluster, Prometheus, GitHub)
  Hooks         → REFLEXES    (safety checks, audit logging)
```

## Setup

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

## Files

| File | Description |
|------|-------------|
| `CLAUDE.md.example` | Template: infrastructure context file for Claude Code |
| `hooks_config.json` | Claude Code settings with safety + audit hooks |
| `safety_hook.py` | PreToolUse hook — blocks dangerous commands |
| `audit_hook.py` | PostToolUse hook — logs all tool executions |
