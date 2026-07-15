# Episode 10: AI-Powered CI/CD & GitOps

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

---

## What You'll Learn

Build AI gates into your CI/CD pipeline — automated code review, pipeline optimization, risk assessment for deployments, and intelligent changelog generation. Every commit gets an AI safety net.

---

## 6 Tasks

| Task | Name | What You Learn |
|------|------|----------------|
| 1 | Code Reviewer | AI reviews diffs for bugs, security issues, and best practices |
| 2 | Pipeline Optimizer | AI analyzes GitHub Actions YAML and suggests optimizations |
| 3 | GitHub Action | Build a complete GitHub Action with AI-powered review |
| 4 | ArgoCD Risk Gate | AI risk scoring before ArgoCD syncs to production |
| 5 | Commit Analyzer | AI categorizes commits and generates release notes |
| 6 | Full Pipeline | End-to-end: commit → review → risk-gate → deploy |

All tasks use real CI/CD scenarios — GitHub Actions, ArgoCD manifests, production deployments. No toy examples.

---

## Prerequisites

- Python 3.10+
- Anthropic API key (`export ANTHROPIC_API_KEY="your-key-here"`)
- `pip install anthropic PyGithub`
- Familiarity with GitHub Actions and ArgoCD concepts

---

## How to Follow Along

1. **Watch the video** — I write every line from scratch, explaining as I go
2. **Follow the [labs](labs/)** — step-by-step guides for each task with concepts, code patterns, and expected output
3. **After the video** — clone this repo for the complete code

```bash
git clone https://github.com/Sagar2366/ai-assisted-devops-workshop.git
cd ai-assisted-devops-workshop/episode-10-ai-cicd-gitops
pip install anthropic PyGithub
```

---

## What Comes Next

| Episode | Topic | What You Build |
|---------|-------|----------------|
| **Ep 11** | AI Incident Response | Auto-triage, runbook execution, war-room assistant |
| **Ep 12** | AI Observability | Log anomaly detection, metric correlation, alert tuning |
| **Ep 13** | AI Security Ops | Vulnerability assessment, compliance checking, threat detection |

> This is part of a 14-episode series: **AI-Assisted DevOps Workshop** — from zero to a full agentic SRE platform.

---

## Links

- [Labs](labs/) — step-by-step guides for each task
  - [Lab 0: Setup](labs/lab0-setup.md)
  - [Lab 1: Code Reviewer](labs/lab1-code-reviewer.md)
  - [Lab 2: Pipeline Optimizer](labs/lab2-pipeline-optimizer.md)
  - [Lab 3: GitHub Actions](labs/lab3-github-actions.md)
  - [Lab 4: ArgoCD Risk Gate](labs/lab4-argocd-risk-gate.md)
  - [Lab 5: Commit Analyzer](labs/lab5-commit-analyzer.md)
  - [Lab 6: Full Pipeline](labs/lab6-full-pipeline.md)
- [Demos](demos/) — complete working scripts
- [GitHub Action Workflow](demos/github-action.yml) — ready-to-use workflow file

---

**Built by [Sagar Utekar](https://github.com/Sagar2366)** | CNCF Ambassador | Kubestronaut
