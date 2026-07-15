# Episode 4: AWS Bedrock for Enterprise SRE — IAM Auth, Multi-Provider, Enterprise Patterns

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut | Docker Captain

---

## The Three Rings of AI Integration for SRE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    ╔═══════════════════════════════════════════════════════════════════╗     │
│    ║              ENTERPRISE RING (AWS Bedrock)                       ║     │
│    ║                    ← YOU ARE HERE                                ║     │
│    ║   IAM Auth │ Guardrails │ VPC Endpoints │ CloudTrail Audit      ║     │
│    ║                                                                  ║     │
│    ║    ┌───────────────────────────────────────────────────────┐    ║     │
│    ║    │           MIDDLE RING (Cloud API)                     │    ║     │
│    ║    │     Direct API Keys │ Rate Limits │ Pay-per-call      │    ║     │
│    ║    │                                                       │    ║     │
│    ║    │    ┌───────────────────────────────────────────┐      │    ║     │
│    ║    │    │       INNER RING (Local/Ollama)           │      │    ║     │
│    ║    │    │   Zero Cost │ Full Privacy │ Limited      │      │    ║     │
│    ║    │    │   Models │ No Auth Required               │      │    ║     │
│    ║    │    └───────────────────────────────────────────┘      │    ║     │
│    ║    │                                                       │    ║     │
│    ║    └───────────────────────────────────────────────────────┘    ║     │
│    ║                                                                  ║     │
│    ╚═══════════════════════════════════════════════════════════════════╝     │
│                                                                             │
│   INNER RING ──────► MIDDLE RING ──────► ENTERPRISE RING                   │
│   (Local/Ollama)      (Cloud API)         (AWS Bedrock)                     │
│                                                                             │
│   Dev/Experiment  →  Team/Staging    →   Production/Regulated              │
│   No credentials     API key mgmt        IAM roles, SCPs, audit            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Why Bedrock for Production SRE?**

When your incident response automation runs at 3 AM, you need more than an API key in a `.env` file. You need IAM roles, audit trails, guardrails that prevent hallucinated runbook steps from hitting production, and billing that goes through your existing AWS enterprise agreement. That is the Enterprise Ring.

---

## Course Structure

| # | Section | Description | Lab |
|---|---------|-------------|-----|
| 0 | **Environment Setup** | AWS credentials, Bedrock model access, SDK validation | [lab0-setup](labs/lab0-setup/) |
| 1 | **Bedrock Basics** | Invoke models, understand request/response lifecycle | [lab1-bedrock-basics](labs/lab1-bedrock-basics/) |
| 2 | **IAM Authentication** | Roles, policies, cross-account access, temporary credentials | [lab2-iam-auth](labs/lab2-iam-auth/) |
| 3 | **Multi-Model Routing** | Route between Claude, Titan, Llama based on task type & cost | [lab3-multi-model](labs/lab3-multi-model/) |
| 4 | **Guardrails** | Content filters, PII redaction, topic denial for SRE contexts | [lab4-guardrails](labs/lab4-guardrails/) |
| 5 | **Gateway Pattern** | Centralized AI gateway with fallback, retry, and observability | [lab5-gateway-pattern](labs/lab5-gateway-pattern/) |

---

## Prerequisites

Before starting this episode, ensure you have:

| Requirement | Minimum Version | Verification Command |
|-------------|----------------|---------------------|
| AWS Account with Bedrock access | N/A | `aws sts get-caller-identity` |
| Python | 3.9+ | `python3 --version` |
| boto3 | 1.28+ | `pip show boto3` |
| AWS CLI | 2.x | `aws --version` |
| Model access enabled | N/A | AWS Console → Bedrock → Model access |

### Enabling Model Access in Bedrock Console

```bash
# Verify your AWS identity
aws sts get-caller-identity

# Check Bedrock availability in your region
aws bedrock list-foundation-models --query "modelSummaries[].modelId" --output table

# If empty, you need to enable model access:
# Console → Amazon Bedrock → Model access → Manage model access → Select models → Save
```

**Models used in this workshop:**
- `anthropic.claude-3-sonnet-20240229-v1:0` — Primary model for SRE tasks
- `anthropic.claude-3-haiku-20240307-v1:0` — Fast triage and classification
- `amazon.titan-text-express-v1` — Cost-effective summarization
- `meta.llama3-8b-instruct-v1:0` — Open-weight alternative for non-sensitive tasks

---

## File Structure

```
episode-4-aws-bedrock-enterprise/
├── README.md                          # This file
├── labs/
│   ├── lab0-setup/
│   │   ├── README.md                  # Setup instructions
│   │   ├── verify_access.py           # Validate Bedrock connectivity
│   │   └── requirements.txt           # Python dependencies
│   ├── lab1-bedrock-basics/
│   │   ├── README.md                  # Bedrock fundamentals
│   │   ├── invoke_model.py            # Basic model invocation
│   │   ├── streaming_response.py      # Streaming for real-time SRE output
│   │   └── converse_api.py            # Converse API patterns
│   ├── lab2-iam-auth/
│   │   ├── README.md                  # IAM deep dive
│   │   ├── role_assumption.py         # AssumeRole for cross-account
│   │   ├── least_privilege_policy.json # Minimal Bedrock policy
│   │   └── session_credentials.py     # Temporary credential handling
│   ├── lab3-multi-model/
│   │   ├── README.md                  # Multi-model routing
│   │   ├── model_router.py            # Intelligent routing logic
│   │   ├── cost_calculator.py         # Per-model cost tracking
│   │   └── fallback_chain.py          # Graceful degradation patterns
│   ├── lab4-guardrails/
│   │   ├── README.md                  # Guardrails configuration
│   │   ├── create_guardrail.py        # Programmatic guardrail setup
│   │   ├── sre_guardrail_config.json  # SRE-specific content policies
│   │   └── test_guardrail.py          # Validation scenarios
│   └── lab5-gateway-pattern/
│       ├── README.md                  # Gateway architecture
│       ├── gateway_server.py          # FastAPI-based AI gateway
│       ├── middleware/
│       │   ├── auth.py                # Request authentication
│       │   ├── rate_limiter.py        # Team-based rate limiting
│       │   └── metrics.py             # Prometheus metrics export
│       └── docker-compose.yml         # Local gateway stack
├── demos/
│   ├── task1-incident-triage.py       # AI-powered incident classification
│   ├── task2-runbook-generation.py    # Dynamic runbook from alerts
│   ├── task3-log-analysis.py          # Bedrock for log pattern detection
│   ├── task4-capacity-planning.py     # Forecast resource needs
│   └── task5-postmortem-writer.py     # Auto-generate postmortem drafts
└── terraform/
    ├── bedrock-iam.tf                 # IAM roles and policies
    ├── guardrails.tf                  # Guardrail resources
    └── vpc-endpoint.tf                # Private Bedrock access
```

---

## Demo Scripts

Real SRE scenarios powered by AWS Bedrock:

| Demo | Script | Scenario |
|------|--------|----------|
| **Task 1** | [task1-incident-triage.py](demos/task1-incident-triage.py) | Classify incoming PagerDuty alerts by severity using Claude on Bedrock. Route P1s to on-call, auto-acknowledge known issues. |
| **Task 2** | [task2-runbook-generation.py](demos/task2-runbook-generation.py) | Generate context-aware runbooks from alert metadata, historical incidents, and service topology. |
| **Task 3** | [task3-log-analysis.py](demos/task3-log-analysis.py) | Stream CloudWatch logs through Bedrock for anomaly detection and root cause hypothesis generation. |
| **Task 4** | [task4-capacity-planning.py](demos/task4-capacity-planning.py) | Analyze historical metrics and generate capacity forecasts with confidence intervals and scaling recommendations. |
| **Task 5** | [task5-postmortem-writer.py](demos/task5-postmortem-writer.py) | Auto-draft blameless postmortems from incident timelines, Slack threads, and remediation actions. |

---

## Quick Start

```bash
# 1. Clone and navigate
cd episode-4-aws-bedrock-enterprise

# 2. Install dependencies
pip install -r labs/lab0-setup/requirements.txt

# 3. Verify AWS access
python labs/lab0-setup/verify_access.py

# 4. Run your first Bedrock call
python labs/lab1-bedrock-basics/invoke_model.py \
  --prompt "Summarize the top 3 causes of Kubernetes pod evictions"

# 5. Try a full SRE demo
python demos/task1-incident-triage.py --alert-source sample_alerts.json
```

---

## Key Concepts

### Why Not Just Use API Keys?

| Concern | API Key Approach | AWS Bedrock (IAM) Approach |
|---------|-----------------|---------------------------|
| **Secret rotation** | Manual, error-prone | Automatic via STS temporary credentials |
| **Blast radius** | Full account access if leaked | Scoped to specific models and actions |
| **Audit** | Limited vendor logs | Full CloudTrail integration |
| **Network** | Public internet | VPC Endpoints (private) |
| **Billing** | Separate vendor invoice | Consolidated AWS billing, cost tags |
| **Compliance** | Varies by provider | SOC2, HIPAA, FedRAMP via AWS |
| **Team access** | Shared secrets | IAM roles per team/service |

### The Gateway Pattern for SRE Teams

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Incident    │────►│   AI Gateway     │────►│  AWS Bedrock    │
│  Response    │     │                  │     │                 │
│  Automation  │     │  - Auth (IAM)    │     │  Claude 3       │
├──────────────┤     │  - Rate Limit    │     │  Titan          │
│  Runbook     │────►│  - Model Router  │────►│  Llama 3        │
│  Engine      │     │  - Cost Tracker  │     │                 │
├──────────────┤     │  - Guardrails    │     │  (Fallback      │
│  Log         │────►│  - Retry/Circuit │     │   Chain)        │
│  Analysis    │     │  - Metrics       │     │                 │
└──────────────┘     └──────────────────┘     └─────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  Observability   │
                     │  - Prometheus    │
                     │  - CloudWatch    │
                     │  - Cost Explorer │
                     └──────────────────┘
```

---

## Cost Note

**AWS Bedrock Pricing Model:**

- **Pay-per-token** — No upfront commitment, no reserved capacity required
- **No idle cost** — You pay only when models are invoked
- **Enterprise billing** — Costs flow through your existing AWS account and enterprise discount programs (EDPs)
- **Cost allocation tags** — Tag requests by team, service, or environment for chargeback

| Model | Input (per 1K tokens) | Output (per 1K tokens) | Typical SRE Use |
|-------|----------------------|------------------------|-----------------|
| Claude 3 Sonnet | $0.003 | $0.015 | Incident analysis, runbooks |
| Claude 3 Haiku | $0.00025 | $0.00125 | Alert triage, classification |
| Titan Text Express | $0.0002 | $0.0006 | Summarization, extraction |
| Llama 3 8B | $0.0003 | $0.0006 | Non-sensitive batch tasks |

**Estimated workshop cost:** Running all labs and demos costs approximately **$0.50 - $2.00** total. Production SRE workloads (thousands of daily invocations) typically run **$50-200/month** depending on model selection and prompt engineering efficiency.

> **Tip:** Use Claude 3 Haiku for high-volume triage (90% of requests), escalate to Sonnet only for complex analysis. This "model tiering" pattern reduces costs by 80%+ without sacrificing quality on critical paths.

---

## What Comes Next

| Episode | Title | Focus |
|---------|-------|-------|
| **Episode 5** | Observability & Cost Control | Prometheus metrics for AI calls, cost dashboards, token budget alerts, OpenTelemetry traces for LLM pipelines |
| **Episode 6** | Production Pipelines | CI/CD for prompt engineering, A/B testing model versions, canary deployments for AI-powered SRE tools |
| **Episode 7** | Multi-Cloud AI Strategy | Azure OpenAI + AWS Bedrock + GCP Vertex AI — unified abstraction layer, failover across providers, data residency compliance |

---

## Learning Objectives

By the end of this episode, you will be able to:

1. **Invoke Bedrock models** using boto3 with proper IAM authentication
2. **Design least-privilege IAM policies** scoped to specific Bedrock models and actions
3. **Implement multi-model routing** that selects the optimal model based on task complexity and cost
4. **Configure Guardrails** to prevent dangerous outputs in SRE automation (e.g., blocking hallucinated `kubectl delete` commands)
5. **Build a production AI gateway** with retry logic, circuit breakers, and observability
6. **Estimate and control costs** using model tiering and token budgets

---

## SRE Context: When to Use Each Ring

| Scenario | Ring | Rationale |
|----------|------|-----------|
| Experimenting with prompts on your laptop | Inner (Ollama) | Zero cost, instant feedback, no credentials |
| Team staging environment | Middle (Cloud API) | Shared API key, moderate governance |
| Production incident automation | Enterprise (Bedrock) | IAM auth, audit trail, guardrails, SLA |
| Regulated environment (SOC2/HIPAA) | Enterprise (Bedrock) | VPC endpoints, CloudTrail, compliance |
| Cost-sensitive batch processing | Enterprise (Bedrock) | Provisioned throughput, billing tags |

---

## Troubleshooting

```bash
# "Access denied" — Model not enabled
aws bedrock list-foundation-models --query "modelSummaries[?modelId=='anthropic.claude-3-sonnet-20240229-v1:0'].modelLifecycle"

# "Region not available" — Bedrock not in your region
aws bedrock list-foundation-models --region us-east-1

# "Throttled" — Request rate exceeded
# Solution: Implement exponential backoff (covered in lab5)

# Verify IAM permissions
aws bedrock-runtime invoke-model \
  --model-id "anthropic.claude-3-haiku-20240307-v1:0" \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":10,"messages":[{"role":"user","content":[{"type":"text","text":"ping"}]}]}' \
  --content-type "application/json" \
  /dev/stdout
```

---

## Contributing

Found an issue or want to add a scenario? This workshop is built by and for the SRE community.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-sre-scenario`)
3. Add your lab or demo with tests
4. Submit a PR with a description of the SRE use case

---

*Part of the AI-Assisted DevOps Workshop Series — Bringing practical AI integration to Site Reliability Engineering.*
