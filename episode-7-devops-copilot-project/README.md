# Episode 7: Building a DevOps Copilot with AI Safety Guardrails

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

---

## Overview

In this episode, we build a complete **AI-powered DevOps Copilot** — a CLI tool that translates natural language into infrastructure commands while enforcing a rigorous **three-tier safety system**. This is the culmination of everything we have learned: prompt engineering, tool use, structured output, and responsible AI deployment in production environments.

The key theme of this episode is **SAFETY**. An AI copilot that can run `kubectl delete namespace production` without guardrails is not a tool — it is a liability. We build safety into every layer.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    DevOps Copilot CLI                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────┐    ┌──────────────────┐    ┌────────────────┐   │
│  │  CLI      │───▶│  Command         │───▶│  Safety        │   │
│  │  Interface│    │  Classifier      │    │  Guardrails    │   │
│  └───────────┘    └──────────────────┘    └────────────────┘   │
│       │                    │                       │             │
│       │                    │                       │             │
│       ▼                    ▼                       ▼             │
│  ┌───────────┐    ┌──────────────────┐    ┌────────────────┐   │
│  │  Natural  │    │  Claude API      │    │  Audit         │   │
│  │  Language │───▶│  (anthropic SDK) │    │  Logger        │   │
│  │  Parser   │    └──────────────────┘    └────────────────┘   │
│  └───────────┘                                    │             │
│                                                   ▼             │
│                                          ┌────────────────┐     │
│                                          │  audit_log.json│     │
│                                          └────────────────┘     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│              Three-Tier Safety Classification                    │
│                                                                 │
│  ┌─────────────┐  ┌─────────────────┐  ┌───────────────────┐   │
│  │  SAFE       │  │  RESTRICTED     │  │  BLOCKED          │   │
│  │  (auto-run) │  │  (confirm first)│  │  (always denied)  │   │
│  │             │  │                 │  │                   │   │
│  │ kubectl get │  │ kubectl scale   │  │ kubectl delete ns │   │
│  │ docker ps   │  │ docker stop     │  │ rm -rf /          │   │
│  │ helm list   │  │ helm upgrade    │  │ docker system prune│  │
│  └─────────────┘  └─────────────────┘  └───────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features

- **Interactive CLI** — Persistent prompt loop with command history
- **AI Command Classification** — Claude classifies every command into SAFE / RESTRICTED / BLOCKED
- **Three-Tier Safety System** — SAFE commands auto-execute, RESTRICTED require confirmation, BLOCKED are always denied
- **JSON Audit Logging** — Every action, decision, and outcome is logged with timestamps
- **Natural Language Interface** — "show me crashing pods" becomes `kubectl get pods --field-selector=status.phase=Failed`
- **Complete Copilot** — All components wired together into a production-ready tool

---

## File Tree

```
episode-7-devops-copilot-project/
├── README.md
├── labs/
│   ├── lab0-setup.md              # Environment setup
│   ├── lab1-cli-interface.md      # Build the CLI prompt loop
│   ├── lab2-command-classification.md  # Classify commands by risk
│   ├── lab3-safety-guardrails.md  # Three-tier safety enforcement
│   ├── lab4-audit-logging.md      # JSON audit trail
│   ├── lab5-natural-language.md   # NL → kubectl/docker translation
│   └── lab6-full-copilot.md       # Wire it all together
└── demos/
    ├── task1_cli_interface.py     # Basic CLI with prompt loop
    ├── task2_command_classification.py  # AI classifies commands
    ├── task3_safety_guardrails.py # SAFE/RESTRICTED/BLOCKED enforcement
    ├── task4_audit_logging.py     # JSON audit with timestamps
    ├── task5_natural_language.py  # NL → infrastructure commands
    └── task6_full_copilot.py      # Complete DevOps copilot
```

---

## The Safety Problem

AI copilots that can run commands are **dangerous** without guardrails:

| Without Guardrails | With Guardrails |
|---|---|
| AI runs `kubectl delete namespace production` | BLOCKED — destructive command denied |
| AI runs `rm -rf /` silently | BLOCKED — filesystem destruction denied |
| No record of what AI did | Every action logged with timestamp + user |
| No human oversight | RESTRICTED commands require confirmation |

This episode builds the guardrails that make an AI copilot safe for production use.

---

## Prerequisites

- Python 3.10+
- Anthropic API key (`export ANTHROPIC_API_KEY="your-key"`)
- `pip install anthropic rich` (Rich for terminal formatting)
- Basic familiarity with kubectl/docker commands
- Episodes 1-6 completed (recommended)

---

## How to Follow Along

1. Start with `labs/lab0-setup.md` to verify your environment
2. Work through labs 1-6 sequentially — each builds on the previous
3. Reference the corresponding `demos/taskN_*.py` for working code
4. The final `task6_full_copilot.py` is the complete, runnable system

```bash
cd episode-7-devops-copilot-project
python3 demos/task1_cli_interface.py
```

---

## 6 Tasks — Progressive Build

| Task | Name | What You Build |
|------|------|----------------|
| 1 | CLI Interface | Interactive prompt loop with command history |
| 2 | Command Classification | AI classifies commands as SAFE / RESTRICTED / BLOCKED |
| 3 | Safety Guardrails | Three-tier system: auto-run, confirm, deny |
| 4 | Audit Logging | JSON log for every action with timestamp, user, command |
| 5 | Natural Language | "Show me crashing pods" → kubectl get pods --field-selector=status.phase=Failed |
| 6 | Full Copilot | Wire it all together into a working CLI tool |

---

## Episode Progression

| Episode | Topic | Key Skill |
|---------|-------|-----------|
| 1 | First API Call | SDK basics |
| 2 | Prompt Engineering | System prompts |
| 3 | Structured Output | JSON responses |
| 4 | Tool Use | Function calling |
| 5 | Multi-turn Conversations | Context management |
| 6 | Agents | Autonomous loops |
| **7** | **DevOps Copilot** | **Safety + Integration** |

---

## Links

- [Lab 0: Setup](labs/lab0-setup.md)
- [Lab 1: CLI Interface](labs/lab1-cli-interface.md)
- [Lab 2: Command Classification](labs/lab2-command-classification.md)
- [Lab 3: Safety Guardrails](labs/lab3-safety-guardrails.md)
- [Lab 4: Audit Logging](labs/lab4-audit-logging.md)
- [Lab 5: Natural Language](labs/lab5-natural-language.md)
- [Lab 6: Full Copilot](labs/lab6-full-copilot.md)

---

*Build AI that operations teams can trust.*
