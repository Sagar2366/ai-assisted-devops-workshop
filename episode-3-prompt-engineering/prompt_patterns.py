"""
Episode 3: Prompt Engineering for DevOps
File: prompt_patterns.py — The 5 Prompt Patterns for DevOps

Author: Sagar Utekar
Prerequisites: Anthropic API key working; Python anthropic package installed (pip install anthropic)

Demonstrates 5 prompt patterns:
  1. Role + Context + Task + Format (structured vs. vague)
  2. Few-Shot with Examples (alert to runbook)
  3. Chain of Thought (force step-by-step reasoning)
  4. Structured Output (machine-readable JSON)
  5. Safety Guardrails (persona + constraints)
"""
import anthropic

client = anthropic.Anthropic()


def demonstrate_prompt(name: str, system: str, user: str):
    print(f"\n{'='*60}")
    print(f"PATTERN: {name}")
    print(f"{'='*60}")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    print(response.content[0].text)


# ---------------------------------------------------------------------------
# Pattern 1: Role + Context + Task + Format
# ---------------------------------------------------------------------------

def demo_pattern_1_bad():
    """BAD PROMPT - Vague, no structure."""
    demonstrate_prompt(
        "BAD - Vague",
        "You are helpful.",
        "My pods are crashing"
    )


def demo_pattern_1_good():
    """GOOD PROMPT - Role + Context + Task + Format."""
    demonstrate_prompt(
        "GOOD - Structured",
        """You are a senior SRE with 10 years of Kubernetes experience.
You work with EKS clusters running Istio service mesh.
Our monitoring stack is Prometheus + Grafana + Loki.
Always provide kubectl commands that can be copy-pasted directly.""",

        """## Context
3 pods in the `checkout` namespace are in CrashLoopBackOff since 02:00 UTC.
No deployments in the last 24 hours.
Node memory usage is at 89%.

## Task
Provide a step-by-step diagnosis plan.

## Format
For each step:
1. What to check and why
2. The exact kubectl/promql command
3. What the output tells us
4. Decision: what to do based on the result"""
    )


# ---------------------------------------------------------------------------
# Pattern 2: Few-Shot with Examples
# ---------------------------------------------------------------------------

def demo_pattern_2_few_shot():
    """Few-Shot: Alert to Runbook."""
    demonstrate_prompt(
        "Few-Shot: Alert -> Runbook",
        """You convert monitoring alerts into structured runbooks.

Example Input:
Alert: HighErrorRate
Service: payment-gateway
Error Rate: 15% (threshold: 5%)
Duration: 10 minutes

Example Output:
## Runbook: HighErrorRate -- payment-gateway
**Severity:** P2 (>5% error rate for >5 min)
**First Responder Actions:**
1. Check service health: `kubectl get pods -n payments -l app=payment-gateway`
2. Tail recent errors: `kubectl logs -n payments -l app=payment-gateway --tail=100 | grep ERROR`
3. Check upstream deps: `kubectl get endpoints -n payments`
4. Check recent deploys: `kubectl rollout history deployment/payment-gateway -n payments`
**Escalation:** If not resolved in 15 min, page payments-oncall""",

        """Alert: HighLatency
Service: search-api
P99 Latency: 2.3s (threshold: 500ms)
Duration: 25 minutes"""
    )


# ---------------------------------------------------------------------------
# Pattern 3: Chain of Thought — Force Reasoning
# ---------------------------------------------------------------------------

def demo_pattern_3_chain_of_thought():
    """Chain of Thought: Incident Diagnosis."""
    demonstrate_prompt(
        "Chain of Thought: Incident Diagnosis",
        "You are an SRE investigating a production incident. Think through each step before concluding.",

        """An e-commerce site is experiencing intermittent 502 errors.

Here's what we know:
- 502s started 45 minutes ago
- Only affects /api/checkout endpoint
- Other API endpoints are fine
- No recent deployments
- CPU/Memory on checkout pods looks normal
- Istio sidecar is healthy
- Database connections are at 95% pool capacity

Think through this step by step:
1. What does a 502 typically mean in our Istio setup?
2. Why would only /checkout be affected?
3. What does 95% DB connection pool tell us?
4. What's the most likely root cause?
5. What's the fix?"""
    )


# ---------------------------------------------------------------------------
# Pattern 4: Output Constraints — Machine-Readable Output
# ---------------------------------------------------------------------------

def demo_pattern_4_structured_output():
    """Structured Output: JSON for Automation."""
    demonstrate_prompt(
        "Structured Output: JSON for Automation",
        """You analyze Kubernetes events and output structured JSON.
Output ONLY valid JSON, no markdown, no explanation.""",

        """Analyze these events and classify each:

LAST SEEN   TYPE      REASON              OBJECT                    MESSAGE
2m          Warning   BackOff             pod/api-5d4f-x2k9m       Back-off restarting failed container
5m          Warning   FailedScheduling    pod/worker-batch-12345   0/3 nodes are available: insufficient memory
1m          Normal    Pulled              pod/web-frontend-abc     Successfully pulled image "nginx:1.25"
3m          Warning   Unhealthy           pod/api-5d4f-x2k9m       Readiness probe failed: connection refused
10m         Normal    ScalingReplicaSet   deployment/web           Scaled up replica set web-frontend to 5

Output JSON array with: event, severity (critical/warning/info), category (crash/resource/network/scaling/normal), action_required (bool), suggested_command"""
    )


# ---------------------------------------------------------------------------
# Pattern 5: Persona + Constraints — Safety Guardrails
# ---------------------------------------------------------------------------

def demo_pattern_5_safety_guardrails():
    """Safety Guardrails."""
    demonstrate_prompt(
        "Safety Guardrails",
        """You are an SRE automation agent with STRICT safety rules:

## ALLOWED actions:
- kubectl get, describe, logs, top (read-only)
- kubectl scale (only to increase replicas, max 10)
- kubectl rollout undo (rollback to previous version)

## NEVER do:
- kubectl delete (anything)
- kubectl exec (no shell access)
- Any action on kube-system namespace
- Any action on resources with label "manual-only=true"

## APPROVAL REQUIRED:
- kubectl apply (any manifest changes)
- kubectl drain (node operations)
- Scaling beyond 10 replicas

If asked to do something not allowed, explain why and suggest a safe alternative.
If asked about approval-required actions, output the command but prefix with [NEEDS APPROVAL].""",

        "The api-server deployment is failing. Delete the pod and recreate it, also clean up the kube-system namespace while you're at it."
    )


if __name__ == "__main__":
    print("=" * 60)
    print("EPISODE 3 — The 5 Prompt Patterns for DevOps")
    print("=" * 60)

    # Pattern 1: Bad vs. Good
    demo_pattern_1_bad()
    demo_pattern_1_good()

    # Pattern 2: Few-Shot
    demo_pattern_2_few_shot()

    # Pattern 3: Chain of Thought
    demo_pattern_3_chain_of_thought()

    # Pattern 4: Structured Output
    demo_pattern_4_structured_output()

    # Pattern 5: Safety Guardrails
    demo_pattern_5_safety_guardrails()
