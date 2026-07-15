# Episode 11: Infrastructure as Code Security with AI

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut | Docker Captain

## Overview

In this episode, we harness AI to transform Infrastructure as Code (IaC) security from a reactive afterthought into a proactive, intelligent process. You will learn how to generate secure Terraform configurations from natural language, scan Kubernetes manifests for misconfigurations, audit Dockerfiles for vulnerabilities, validate against CIS benchmarks, and auto-remediate findings — all powered by Claude's understanding of security best practices.

## Why AI for IaC Security?

Traditional static analysis tools rely on pattern matching and fixed rule sets. AI-powered security scanning brings:

- **Contextual Understanding** — Understands intent, not just syntax
- **Natural Language Generation** — Describe what you want, get secure IaC
- **Intelligent Remediation** — Fixes that preserve functionality while hardening security
- **CIS/CVE Awareness** — References real benchmarks and vulnerability databases
- **Cross-Resource Analysis** — Detects issues spanning multiple resources

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   AI-Powered IaC Security                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │ Natural   │───▶│   Claude AI  │───▶│ Secure Terraform │  │
│  │ Language  │    │   Engine     │    │ / K8s / Docker   │  │
│  └───────────┘    └──────┬───────┘    └──────────────────┘  │
│                          │                                    │
│                          ▼                                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Security Analysis Pipeline                 │  │
│  ├───────────┬──────────┬──────────────┬─────────────────┤  │
│  │ Terraform │ K8s YAML │  Dockerfile  │   Compliance    │  │
│  │ Review    │ Scanner  │  Auditor     │   Checker       │  │
│  └─────┬─────┴────┬─────┴──────┬───────┴────────┬────────┘  │
│        │           │            │                │            │
│        ▼           ▼            ▼                ▼            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            AI-Powered Remediation Engine                │  │
│  │  (Generate fixes, explain rationale, preserve intent)  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## File Tree

```
episode-11-iac-ai-security/
├── README.md
├── labs/
│   ├── lab0-setup.md
│   ├── lab1-terraform-generator.md
│   ├── lab2-terraform-reviewer.md
│   ├── lab3-k8s-security-scanner.md
│   ├── lab4-dockerfile-scanner.md
│   ├── lab5-compliance-checker.md
│   └── lab6-remediation.md
└── demos/
    ├── task1_terraform_generator.py
    ├── task2_terraform_reviewer.py
    ├── task3_k8s_security_scanner.py
    ├── task4_dockerfile_scanner.py
    ├── task5_compliance_checker.py
    ├── task6_remediation.py
    └── sample-manifests/
        ├── insecure-deployment.yaml
        ├── insecure-dockerfile
        └── insecure-terraform.tf
```

## Learning Objectives

| Lab | Topic | Key Skills |
|-----|-------|------------|
| Lab 0 | Environment Setup | Python, Anthropic SDK, sample files |
| Lab 1 | Terraform Generator | Natural language to secure IaC |
| Lab 2 | Terraform Reviewer | AI code review for security and cost |
| Lab 3 | K8s Security Scanner | RBAC, SecurityContext, network policies |
| Lab 4 | Dockerfile Scanner | Base images, secrets, layer optimization |
| Lab 5 | Compliance Checker | CIS Kubernetes Benchmark validation |
| Lab 6 | Remediation Engine | Auto-fix with explanations |

## Security Domains Covered

- **Terraform**: Public S3 buckets, open security groups, unencrypted resources, IAM misconfigurations
- **Kubernetes**: Privileged containers, missing resource limits, RBAC over-permissions, missing network policies
- **Docker**: Running as root, embedded secrets, unversioned base images, unnecessary packages
- **Compliance**: CIS Kubernetes Benchmark v1.8, CIS AWS Foundations Benchmark

## Prerequisites

- Python 3.10+
- Anthropic API key (`ANTHROPIC_API_KEY`)
- Basic familiarity with Terraform, Kubernetes, and Docker
- Completed Episodes 1-10 (recommended)

## Quick Start

```bash
# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Install dependencies
pip install anthropic pyyaml

# Run any demo
python demos/task1_terraform_generator.py
```

## Episode Flow

```
Lab 0 (Setup) → Lab 1 (Generate) → Lab 2 (Review) → Lab 3 (K8s Scan)
                                                            │
Lab 6 (Remediate) ← Lab 5 (Compliance) ← Lab 4 (Docker) ←─┘
```

---

*Part of the AI-Assisted DevOps Workshop Series*
