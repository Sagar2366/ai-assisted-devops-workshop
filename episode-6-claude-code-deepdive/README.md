# Episode 6: Claude Code Deep Dive for DevOps

- CLAUDE.md for persistent infrastructure context
- MCP integration with your K8s cluster
- PreToolUse safety hooks — block dangerous commands before execution
- PostToolUse audit hooks — log all tool executions to JSON

## Files

| File | Description |
|------|-------------|
| `CLAUDE.md.example` | Template: infrastructure context file for Claude Code |
| `hooks_config.json` | Claude Code settings with safety + audit hooks |
| `safety_hook.py` | PreToolUse hook — blocks dangerous commands |
| `audit_hook.py` | PostToolUse hook — logs all tool executions |
