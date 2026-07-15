# Lab 2: Few-Shot Prompting

## Mission

Use few-shot prompting to achieve consistent, structured outputs for incident classification and root cause analysis. By providing 2-3 labeled examples, you teach the model your exact output format and decision criteria.

---

## Concept: What is Few-Shot Prompting?

Few-shot prompting means providing a small number of input-output examples before presenting the actual task. The model learns the pattern from your examples and applies it to new inputs.

### The Analogy

Imagine onboarding a new SRE to your team. Before they handle their first on-call incident, you show them 2-3 past incidents: "Here is what a P1 looks like. Here is how we classified this database issue. Here is the format we use for root cause analysis." Now when they see a new incident, they know exactly what format you expect and what criteria to apply.

That is few-shot prompting — you are onboarding the model with examples.

### When to Use Few-Shot

- When output format consistency matters (incident reports, classifications)
- When you have specific categories the model might not guess correctly
- When zero-shot produces correct but inconsistently formatted outputs
- When you need domain-specific classification rules

---

## Step 1: Severity Classification Without Examples (The Problem)

First, let us see what happens with zero-shot:

```python
from sre_prompt import call_claude

# Zero-shot attempt at severity classification
alert_data = """
Service: payment-gateway
Error: Connection timeout to downstream auth-service
Duration: 3 minutes
Affected Users: ~200 concurrent
Revenue Impact: Transactions failing
"""

zero_shot_prompt = f"""Classify the severity of this incident.

Incident:
{alert_data}"""

print("Zero-shot result:")
print(call_claude(zero_shot_prompt))
```

The output might say "High" or "Critical" or "Sev-2" — it is inconsistent because the model does not know YOUR severity scale.

---

## Step 2: Severity Classification With Examples (The Fix)

```python
from sre_prompt import call_claude

few_shot_prompt = """Classify the severity of incidents using these levels:
- SEV1: Customer-facing service fully down, revenue loss active
- SEV2: Customer-facing service degraded, partial impact
- SEV3: Internal service issue, no direct customer impact yet
- SEV4: Minor issue, no impact, can wait for business hours

Here are examples of correct classifications:

---
INCIDENT: API gateway returning 503 for all requests. 100% of traffic affected. Duration: 5 minutes.
CLASSIFICATION: SEV1
REASONING: Complete service outage affecting all customers with active revenue loss.
ACTION: Page on-call immediately, initiate incident bridge.
---

INCIDENT: Search service returning results 3x slower than normal. 30% of queries timing out.
CLASSIFICATION: SEV2
REASONING: Service degraded but partially functional. Customer experience impacted but not fully blocked.
ACTION: Alert on-call, begin investigation within 15 minutes.
---

INCIDENT: Dev environment CI/CD pipeline failing due to expired credentials.
CLASSIFICATION: SEV4
REASONING: No customer or production impact. Development workflow inconvenience only.
ACTION: Create ticket, fix during business hours.
---

Now classify this incident:

INCIDENT: Payment gateway connection timeout to auth-service. Duration: 3 minutes. ~200 concurrent users affected. Transactions failing.
"""

print("Few-shot result:")
print(call_claude(few_shot_prompt))
```

Notice how the output now follows your exact format: CLASSIFICATION, REASONING, ACTION.

---

## Step 3: Root Cause Categorization

```python
from sre_prompt import call_claude

categorization_prompt = """Categorize the root cause of incidents into one of these categories:
- CAPACITY: Resource exhaustion (CPU, memory, disk, connections)
- DEPENDENCY: External service or dependency failure
- DEPLOYMENT: Recent code or config change caused the issue
- INFRASTRUCTURE: Hardware, network, or cloud provider issue
- DATA: Data corruption, migration issue, or schema problem

Examples:

---
SYMPTOMS: Pod OOMKilled after traffic spike. Memory usage hit 95% before restart.
CATEGORY: CAPACITY
EXPLANATION: Container memory limits exceeded due to increased load.
PREVENTION: Implement HPA, increase memory limits, add memory-based alerts at 80%.
---

SYMPTOMS: Service errors started 10 minutes after deploying v2.3.1. Rollback to v2.3.0 fixed the issue.
CATEGORY: DEPLOYMENT
EXPLANATION: Code change in v2.3.1 introduced a regression.
PREVENTION: Add canary deployment, improve pre-deploy test coverage, implement automatic rollback on error rate spike.
---

SYMPTOMS: All services in us-east-1 experiencing elevated latency. AWS status page shows EBS degradation.
CATEGORY: INFRASTRUCTURE
EXPLANATION: Cloud provider infrastructure issue affecting storage layer.
PREVENTION: Multi-region deployment, automated failover, reduce single-AZ dependencies.
---

Now categorize this incident:

SYMPTOMS: Database connection pool exhausted. Application logs show "too many connections" error. Connection count grew steadily over 6 hours from 50 to 500. No traffic increase observed. Recent config change set connection_max_lifetime to 0 (never expire).
"""

print(call_claude(categorization_prompt))
```

---

## Step 4: Building a Few-Shot Prompt Library

Create reusable few-shot prompts as functions:

```python
from sre_prompt import call_claude


def classify_incident_severity(incident_description: str) -> str:
    """Classify incident severity using few-shot examples."""
    prompt = f"""Classify the severity of incidents using these levels:
- SEV1: Customer-facing service fully down, revenue loss active
- SEV2: Customer-facing service degraded, partial impact
- SEV3: Internal service issue, no direct customer impact yet
- SEV4: Minor issue, no impact, can wait for business hours

Examples:

INCIDENT: Complete database cluster failure. All writes failing. Read replicas stale.
CLASSIFICATION: SEV1
REASONING: Full data layer outage blocking all write operations.
ACTION: Page on-call and DBA team, initiate incident bridge.

INCIDENT: Monitoring system (Prometheus) disk full. No new metrics being stored.
CLASSIFICATION: SEV3
REASONING: Internal observability tool degraded. No direct customer impact but reduces our ability to detect issues.
ACTION: Alert on-call, fix within 1 hour to restore monitoring coverage.

INCIDENT: Staging environment unreachable due to expired TLS cert.
CLASSIFICATION: SEV4
REASONING: Non-production environment. No customer impact.
ACTION: Create ticket for next business day.

Now classify:

INCIDENT: {incident_description}
"""
    return call_claude(prompt)


def categorize_root_cause(symptoms: str) -> str:
    """Categorize incident root cause using few-shot examples."""
    prompt = f"""Categorize the root cause into: CAPACITY | DEPENDENCY | DEPLOYMENT | INFRASTRUCTURE | DATA

Examples:

SYMPTOMS: Redis cluster rejecting connections. Max clients reached (10000/10000).
CATEGORY: CAPACITY
EXPLANATION: Connection pool exhausted at configured maximum.
PREVENTION: Implement connection pooling client-side, increase maxclients, add connection count alerts.

SYMPTOMS: Payment processing failing. Third-party payment provider API returning 503.
CATEGORY: DEPENDENCY
EXPLANATION: External payment provider experiencing outage.
PREVENTION: Implement circuit breaker, add fallback payment provider, queue transactions for retry.

SYMPTOMS: User records returning stale data. Cache invalidation not firing after DB migration added new columns.
CATEGORY: DATA
EXPLANATION: Schema change broke cache invalidation logic.
PREVENTION: Include cache invalidation in migration checklist, add integration tests for cache consistency.

Now categorize:

SYMPTOMS: {symptoms}
"""
    return call_claude(prompt)


# Test the library
print("=== Severity Classification ===")
print(classify_incident_severity(
    "Kubernetes ingress controller pod restarting every 2 minutes. "
    "50% of external traffic getting 502 errors."
))

print("\n=== Root Cause Categorization ===")
print(categorize_root_cause(
    "Service latency increased 10x after deploying new Envoy sidecar version. "
    "CPU usage on sidecar containers jumped from 10% to 95%. "
    "Rolling back sidecar version restored normal latency."
))
```

---

## Step 5: Measuring the Improvement

Run the same incident through both zero-shot and few-shot to see the difference:

```python
from sre_prompt import call_claude

incident = "Elasticsearch cluster yellow status. One node left the cluster 20 minutes ago. Search queries working but slower. Index replication incomplete."

# Zero-shot
zero_shot = f"Classify the severity of this incident: {incident}"

# Few-shot (using our function)
few_shot_result = classify_incident_severity(incident)

print("=== Zero-Shot ===")
print(call_claude(zero_shot))
print("\n=== Few-Shot ===")
print(few_shot_result)
```

The few-shot version will consistently produce:
- The exact severity label from your scale (SEV1-SEV4)
- A REASONING line explaining why
- An ACTION line with next steps

---

## What Success Looks Like

After completing this lab, you can:

- Build few-shot prompts that enforce consistent output formats
- Create a library of reusable classification prompts for your team
- See measurable improvement in output consistency vs. zero-shot
- Understand how many examples are needed (usually 2-3 is sufficient)

Example consistent output:

```
CLASSIFICATION: SEV2
REASONING: Customer-facing search degraded with increased latency. Service functional but impaired.
ACTION: Alert on-call, investigate Elasticsearch cluster health. Consider temporary search result caching.
```

---

## Key Takeaway

Few-shot prompting is your tool for **consistency**. Whenever you need outputs that follow a specific format, use specific labels, or apply your team's classification criteria, add 2-3 examples. The model learns your pattern far more reliably from examples than from lengthy written instructions. Think of examples as "showing" rather than "telling."

---

## Next

[Lab 3: Chain-of-Thought](lab3-chain-of-thought.md) — Step-by-step reasoning for complex multi-step troubleshooting
