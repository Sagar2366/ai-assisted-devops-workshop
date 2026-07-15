# Episode 8: Claude Code Deep Dive — Mastering the AI-Powered CLI for DevOps

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

## Overview

Claude Code is not just another AI coding assistant — it is a full-fledged agentic CLI that understands your infrastructure, respects your guardrails, and integrates deeply into DevOps workflows. This episode takes you beyond basic prompting into the advanced features that make Claude Code indispensable for Site Reliability Engineering.

You will learn to configure `CLAUDE.md` files that encode your team's operational knowledge, set up hooks that prevent dangerous actions before they happen, create custom slash commands for repetitive SRE tasks, and connect MCP servers that give Claude Code real-time access to your infrastructure.

## What You Will Learn

| Topic | Outcome |
|-------|---------|
| CLAUDE.md Patterns | Encode team standards, forbidden actions, and repo context |
| Hooks System | Pre/post action hooks for safety guardrails and audit trails |
| Slash Commands | Custom `/commands` for incident response, rollback, health checks |
| MCP Integration | Connect Kubernetes, cloud providers, and observability tools |
| Team Workflows | Shared settings, permission models, onboarding patterns |

## Prerequisites

- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
- Active Anthropic API key or Claude Max subscription
- Familiarity with terminal-based workflows
- A DevOps/infrastructure repository to practice with

## File Tree

```
episode-8-claude-code-deepdive/
├── README.md                          # This file
├── labs/
│   ├── lab0-setup.md                  # Install and configure Claude Code
│   ├── lab1-claude-md.md              # Write CLAUDE.md files for DevOps repos
│   ├── lab2-hooks.md                  # Pre/post hooks for safety and audit
│   ├── lab3-slash-commands.md         # Custom slash commands for SRE
│   ├── lab4-mcp-integration.md        # Connect MCP servers to Claude Code
│   └── lab5-team-workflow.md          # Team patterns with shared settings
└── demos/
    ├── CLAUDE.md.template             # Production CLAUDE.md for a DevOps repo
    ├── hooks/
    │   ├── pre-commit-safety.sh       # Hook blocking dangerous commands
    │   └── post-action-audit.sh       # Hook logging all actions
    ├── task1_claude_md.py             # Generate CLAUDE.md from repo analysis
    ├── task2_hooks_setup.py           # Set up safety hooks programmatically
    ├── task3_slash_commands.py        # Create custom slash commands
    └── task4_mcp_config.py            # Configure MCP servers for Claude Code
```

## Episode Flow

```
Lab 0 (Setup) ──► Lab 1 (CLAUDE.md) ──► Lab 2 (Hooks) ──► Lab 3 (Slash Commands)
                                                                      │
                                                                      ▼
                                              Lab 5 (Team) ◄── Lab 4 (MCP)
```

## Key Concepts

### The Claude Code Configuration Hierarchy

```
~/.claude/settings.json          ← User-level (personal preferences)
    │
    ▼
.claude/settings.json            ← Project-level (team shared)
    │
    ▼
CLAUDE.md                        ← Repo root (project context)
    │
    ▼
subdirectory/CLAUDE.md           ← Directory-specific overrides
```

### Why This Matters for DevOps

1. **Safety by Default** — Hooks prevent `kubectl delete` in production before Claude even tries
2. **Institutional Knowledge** — CLAUDE.md encodes runbooks, architecture decisions, forbidden patterns
3. **Consistent Operations** — Slash commands ensure every team member follows the same procedures
4. **Real-time Context** — MCP servers give Claude live cluster state, not stale documentation

## Running the Labs

Each lab is self-contained. Start with Lab 0 for setup, then proceed sequentially:

```bash
# Verify Claude Code is installed
claude --version

# Start Claude Code in your DevOps repo
cd your-infrastructure-repo
claude

# Or run a specific slash command
claude /your-custom-command
```

## Connection to Other Episodes

- **Episode 5 (MCP Servers)** — Lab 4 builds on MCP concepts from Episode 5
- **Episode 6 (Claude Desktop)** — Contrasts GUI vs CLI workflows
- **Episode 7 (AI Agents)** — Claude Code as an agentic system with tool use

---

*"The best DevOps tooling disappears into your workflow. Claude Code with proper configuration becomes an extension of your team's operational expertise."*
