#!/usr/bin/env python3
"""
Chain-of-Thought Prompting for DevOps
=====================================

Chain-of-thought (CoT) prompting encourages step-by-step reasoning for complex
problems. Instead of asking the model to jump directly to a conclusion, CoT
prompts guide the model through intermediate reasoning steps, producing deeper
and more accurate analysis -- especially valuable for complex root cause
analysis in distributed systems.

Prerequisites:
    - anthropic SDK: pip install anthropic
    - ANTHROPIC_API_KEY environment variable set

Usage:
    python task3_chain_of_thought.py
"""

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-20250514"


def call_claude(prompt, max_tokens=1024):
    """Send a prompt to Claude and return the response text."""
    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# ============================================================
# Introduction
# ============================================================
print("=" * 65)
print("CHAIN-OF-THOUGHT PROMPTING FOR DEVOPS")
print("Encouraging step-by-step reasoning for complex problems")
print("=" * 65)
print()
print("Chain-of-thought prompting produces deeper, more structured")
print("analysis than simple prompts by guiding the model through")
print("intermediate reasoning steps before reaching a conclusion.")
print()

# ============================================================
# Experiment 1: Simple Prompt vs CoT Prompt
# ============================================================
print("=" * 65)
print("EXPERIMENT 1: Simple Prompt vs Chain-of-Thought Prompt")
print("Scenario: Cascading failure across multiple microservices")
print("=" * 65)
print()

incident_description = """
Incident Report - Severity 1 - Production Outage

Timeline:
- 14:02 UTC: Monitoring alerts fire for increased latency on payment-service (p99 > 5s)
- 14:05 UTC: order-service starts returning 503 errors (rate: 34%)
- 14:07 UTC: user-session-service memory usage spikes to 95%
- 14:08 UTC: inventory-service connection pool exhausted (max 200 connections)
- 14:10 UTC: API gateway starts rate limiting all inbound traffic
- 14:12 UTC: Redis cluster node 3 reports "maxmemory reached"
- 14:15 UTC: Kubernetes HPA scales payment-service from 5 to 25 pods
- 14:16 UTC: Node pool memory pressure triggers pod evictions
- 14:18 UTC: Database replica lag exceeds 30 seconds
- 14:20 UTC: Full outage declared - all services degraded

Infrastructure:
- Kubernetes cluster (3 node pools, 45 nodes total)
- PostgreSQL primary + 3 read replicas
- Redis cluster (6 nodes, 3 primary + 3 replica)
- Service mesh: Istio with mTLS
- Message queue: RabbitMQ (3-node cluster)

Recent Changes (last 24h):
- 12:00 UTC: Deployed payment-service v2.4.1 (added retry logic for failed transactions)
- 10:00 UTC: Updated Istio sidecar injection to v1.19.3
- 08:00 UTC: Scaled down Redis cluster from 9 to 6 nodes (cost optimization)
"""

# --- Simple prompt ---
print("-" * 65)
print("Approach A: Simple Prompt (no CoT guidance)")
print("-" * 65)
print()

simple_prompt = f"""What caused this production outage?

{incident_description}

Provide the root cause and fix."""

print("PROMPT SENT:")
print(simple_prompt[:200] + "...[incident details]...")
print()
print("RESPONSE:")
print()
simple_response = call_claude(simple_prompt)
print(simple_response)
print()

# --- CoT prompt ---
print("-" * 65)
print("Approach B: Chain-of-Thought Prompt")
print("-" * 65)
print()

cot_prompt = f"""Analyze this production outage step by step. Think through the
causal chain carefully before reaching your conclusion.

{incident_description}

Let's work through this systematically:
1. First, identify the earliest anomaly and what could trigger it
2. Then, trace how each subsequent failure relates to the previous one
3. Consider which recent changes could have introduced the initial fault
4. Evaluate whether the cascading failures were caused by the root issue or by the system's response to it
5. Finally, state the root cause with supporting evidence and recommend a fix

Show your reasoning at each step."""

print("PROMPT SENT:")
print(cot_prompt[:300] + "...[incident details]...")
print()
print("RESPONSE:")
print()
cot_response = call_claude(cot_prompt, max_tokens=2048)
print(cot_response)
print()

print("-" * 65)
print("COMPARISON: Notice how the CoT prompt produces a causal chain")
print("analysis rather than jumping to a single conclusion. It traces")
print("the failure propagation path and evaluates multiple hypotheses.")
print("-" * 65)
print()

# ============================================================
# Experiment 2: "Let's think step by step" for Network Debugging
# ============================================================
print("=" * 65)
print("EXPERIMENT 2: Multi-Step Debugging with 'Let's think step by step'")
print("Scenario: Complex Kubernetes networking issue")
print("=" * 65)
print()

networking_issue = """
Problem: Intermittent connection timeouts between pods in namespace "checkout"
and pods in namespace "inventory" in our Kubernetes cluster.

Observed Behavior:
- ~15% of requests from checkout-service to inventory-service timeout after 30s
- Timeouts are not correlated with load (happen at 2am and 2pm equally)
- Direct pod-to-pod connectivity via IP works (curl from checkout pod to inventory pod IP succeeds)
- DNS resolution of inventory-service.inventory.svc.cluster.local is correct
- Istio sidecar proxies show "upstream_reset_before_response_started" errors
- kube-proxy iptables rules appear correct
- No packet drops reported by CNI plugin (Calico)
- Issue started 3 days ago
- Network policies were updated 4 days ago to restrict cross-namespace traffic
- Istio VirtualService for inventory-service has a 30s timeout configured
- Envoy access logs show some requests going to pods that are in "Terminating" state
- HPA for inventory-service scales between 3-15 pods based on CPU

Cluster Info:
- Kubernetes 1.28, Calico CNI, Istio 1.19
- CoreDNS with node-local-dns cache enabled
- kube-proxy in iptables mode
"""

step_by_step_prompt = f"""You are a senior SRE debugging a complex networking issue in Kubernetes.

{networking_issue}

Let's think step by step to identify the root cause."""

print("-" * 65)
print("Using 'Let's think step by step' trigger phrase")
print("-" * 65)
print()
print("PROMPT SENT:")
print(step_by_step_prompt[:300] + "...[issue details]...")
print()
print("RESPONSE:")
print()
step_response = call_claude(step_by_step_prompt, max_tokens=2048)
print(step_response)
print()

# ============================================================
# Experiment 3: Structured CoT with Numbered Reasoning Steps
# ============================================================
print("=" * 65)
print("EXPERIMENT 3: Structured CoT with Numbered Reasoning Steps")
print("Scenario: Database performance degradation in production")
print("=" * 65)
print()

db_scenario = """
Alert: PostgreSQL primary database CPU at 98%, query latency p99 = 12 seconds

Symptoms:
- Slow queries started 2 hours ago, progressively worsening
- Connection count: 450/500 (near max_connections limit)
- Active queries: 380 (normally ~50)
- Longest running query: 45 minutes (a SELECT with multiple JOINs)
- WAL generation rate: 500MB/min (normally 50MB/min)
- Bloat on 'orders' table: 78% (was 15% yesterday)
- Autovacuum on 'orders' table: last completed 3 days ago
- Lock waits: 124 queries waiting on AccessExclusiveLock
- pg_stat_activity shows 200+ queries in "idle in transaction" state
- Replica lag: 45 seconds and growing
- Disk I/O: 95% utilization, read throughput 800MB/s

Recent Events:
- A data migration job was started 2.5 hours ago (UPDATE on 'orders' table)
- New application release deployed 6 hours ago (added new reporting queries)
- Nightly VACUUM was disabled 4 days ago due to "maintenance window conflicts"
- Table partitioning project for 'orders' is planned but not yet implemented
"""

structured_cot_prompt = f"""Analyze this database incident using the following structured reasoning framework.
You MUST follow these exact steps in order:

{db_scenario}

## Reasoning Framework:

**Step 1 - Identify Symptoms:** List all observable symptoms and categorize them
(performance, capacity, data integrity).

**Step 2 - List Possible Causes:** For each symptom category, enumerate possible
root causes that could produce these symptoms.

**Step 3 - Evaluate Evidence:** For each possible cause, evaluate whether the
available evidence supports or contradicts it. Rate each as "likely", "possible",
or "unlikely" with justification.

**Step 4 - Determine Root Cause:** Based on your evidence evaluation, identify
the primary root cause and any contributing factors. Explain the causal chain.

**Step 5 - Recommend Fix:** Provide immediate mitigation steps (stop the bleeding),
short-term fix (resolve the incident), and long-term prevention measures.

Follow this framework strictly, numbering each step."""

print("-" * 65)
print("Structured CoT with 5-step reasoning framework")
print("-" * 65)
print()
print("PROMPT SENT:")
print(structured_cot_prompt[:400] + "...[scenario + framework]...")
print()
print("RESPONSE:")
print()
structured_response = call_claude(structured_cot_prompt, max_tokens=3000)
print(structured_response)
print()

# ============================================================
# Key Learning
# ============================================================
print("=" * 65)
print("KEY LEARNING: Chain-of-Thought Prompting Strengths")
print("=" * 65)
print()
print("1. DEEPER ANALYSIS: CoT prompts prevent the model from jumping")
print("   to conclusions. By requiring intermediate reasoning steps,")
print("   the model considers multiple hypotheses and evaluates evidence.")
print()
print("2. CAUSAL CHAIN TRACING: For cascading failures, CoT prompts")
print("   help trace the propagation path from root cause through each")
print("   subsequent failure -- critical for complex distributed systems.")
print()
print("3. STRUCTURED REASONING: Numbered reasoning frameworks ensure")
print("   consistent, thorough analysis. The model follows a repeatable")
print("   methodology rather than ad-hoc reasoning.")
print()
print("4. 'LET'S THINK STEP BY STEP': This simple phrase triggers more")
print("   methodical reasoning, even without explicit structure. Useful")
print("   for quick debugging sessions.")
print()
print("5. AUDITABILITY: CoT responses show their work, making it easy")
print("   to verify the reasoning and catch logical errors -- essential")
print("   for post-incident reviews and blameless postmortems.")
print()
print("WHEN TO USE CoT IN DEVOPS:")
print("  - Root cause analysis of complex, multi-service outages")
print("  - Debugging intermittent issues with many possible causes")
print("  - Security incident investigation and forensics")
print("  - Capacity planning with multiple constraints")
print("  - Change impact analysis before production deployments")
print()
print("=" * 65)
print("Next: task4_production_templates.py")
print("  -> Production-ready prompt templates for common DevOps tasks")
print("=" * 65)
