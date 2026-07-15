# Episode 5: Prompt Engineering for SRE & DevOps

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

## Overview

Master the art and science of prompt engineering specifically for Site Reliability Engineering and DevOps workflows. This episode transforms you from writing ad-hoc prompts to building production-grade prompt systems that deliver consistent, reliable results for incident response, troubleshooting, and operational excellence.

## What You Will Learn

| Technique | SRE Application | Key Benefit |
|-----------|----------------|-------------|
| Zero-Shot Prompting | Quick K8s troubleshooting | Rapid triage without examples |
| Few-Shot Prompting | Incident classification | Pattern matching from examples |
| Chain-of-Thought | Root cause analysis | Step-by-step reasoning |
| Production Templates | Runbooks, postmortems | Reusable, consistent output |
| Prompt Testing | Regression testing | Reliability at scale |
| Anti-Patterns | Avoiding bad prompts | Prevent costly mistakes |

## Prerequisites

- Python 3.9+
- Anthropic API key (`export ANTHROPIC_API_KEY="your-key"`)
- Familiarity with Kubernetes concepts (pods, deployments, services)
- Basic understanding of SRE practices (SLOs, incident response, postmortems)
- Completion of Episodes 1-4 (recommended)

## File Structure

```
episode-5-prompt-engineering/
├── README.md
├── labs/
│   ├── lab0-setup.md              # Environment setup and verification
│   ├── lab1-zero-shot.md          # Zero-shot prompting for quick SRE tasks
│   ├── lab2-few-shot.md           # Few-shot with incident examples
│   ├── lab3-chain-of-thought.md   # CoT for multi-step troubleshooting
│   ├── lab4-templates.md          # 4 production templates
│   ├── lab5-testing-framework.md  # Build prompt regression tests
│   └── lab6-anti-patterns.md      # Common prompt mistakes in DevOps
└── demos/
    ├── task1_zero_shot.py         # Zero-shot K8s troubleshooting
    ├── task2_few_shot.py          # Few-shot with labeled incident examples
    ├── task3_chain_of_thought.py  # CoT for root cause analysis
    ├── task4_production_templates.py  # 4 reusable SRE prompt templates
    ├── task5_testing_framework.py # Automated prompt regression testing
    └── task6_anti_patterns.py     # Bad vs good prompts side by side
```

## Episode Flow

```
Lab 0: Setup (10 min)
  └─> Lab 1: Zero-Shot (20 min) ─── Quick wins, immediate results
       └─> Lab 2: Few-Shot (25 min) ─── Teaching by example
            └─> Lab 3: Chain-of-Thought (30 min) ─── Deep reasoning
                 └─> Lab 4: Templates (35 min) ─── Production-ready systems
                      └─> Lab 5: Testing (30 min) ─── Quality assurance
                           └─> Lab 6: Anti-Patterns (20 min) ─── What NOT to do
```

## Quick Start

```bash
# 1. Clone and navigate
cd episode-5-prompt-engineering

# 2. Set up environment
export ANTHROPIC_API_KEY="your-key-here"
pip install anthropic

# 3. Verify setup
python demos/task1_zero_shot.py

# 4. Follow the labs in order
# Start with labs/lab0-setup.md
```

## Key Concepts

### The Prompt Engineering Spectrum

```
Simple ──────────────────────────────────────────────── Complex
  │                                                        │
Zero-Shot    Few-Shot    Chain-of-Thought    Templates    Systems
  │              │              │                │           │
"Fix this"  "Like these   "Think step      Structured   Full prompt
             examples..."   by step..."     frameworks   pipelines
```

### Why Prompt Engineering Matters for SRE

1. **Consistency** - Same incident type gets same quality response every time
2. **Speed** - Pre-built templates reduce MTTR during incidents
3. **Knowledge capture** - Encode tribal knowledge into prompt patterns
4. **Scalability** - One good template serves the entire on-call rotation
5. **Auditability** - Structured outputs integrate with existing tooling

## Connecting to the Workshop Series

| Episode | Focus | Connection to Episode 5 |
|---------|-------|------------------------|
| 1 | Foundations | Basic API calls we now optimize |
| 2 | CLI Tools | Prompts that power CLI interactions |
| 3 | Monitoring | Alerts that feed our prompt templates |
| 4 | K8s Operations | Scenarios we troubleshoot here |
| **5** | **Prompt Engineering** | **Master the craft** |
| 6 | Advanced Agents | Complex chains built on these patterns |

## Resources

- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)
- [Claude API Documentation](https://docs.anthropic.com/en/api)
- [SRE Book - Google](https://sre.google/sre-book/table-of-contents/)
- [Kubernetes Troubleshooting Guide](https://kubernetes.io/docs/tasks/debug/)

## Links

- [Lab 0: Setup](labs/lab0-setup.md)
- [Lab 1: Zero-Shot Prompting](labs/lab1-zero-shot.md)
- [Lab 2: Few-Shot Prompting](labs/lab2-few-shot.md)
- [Lab 3: Chain-of-Thought](labs/lab3-chain-of-thought.md)
- [Lab 4: Production Templates](labs/lab4-templates.md)
- [Lab 5: Testing Framework](labs/lab5-testing-framework.md)
- [Lab 6: Anti-Patterns](labs/lab6-anti-patterns.md)
- [Demos](demos/)

---

*Episode 5 of the AI-Assisted DevOps Workshop Series*
