# Lab 3: Agent Router

> **Mission:** Build an intelligent router that classifies intent and delegates to the right specialist agent.

---

## The Problem

Your agentic DevOps platform has multiple specialist agents — one for Kubernetes troubleshooting, one for Infrastructure as Code review, one for observability queries, one for incident response. When an engineer types a request, how does the system know which agent should handle it?

> **Analogy:** Think of a hospital triage nurse. A patient walks in and describes their symptoms. The triage nurse does not treat the patient — they assess urgency, classify the problem, and route to the correct specialist. Your agent router performs the same function: fast classification, confident delegation, and a fallback when symptoms are ambiguous.

Without a reliable router, requests go to the wrong agent, responses are irrelevant, and engineers lose trust in the platform.

---

## Intent Classification Approaches

There are three strategies for routing, each with trade-offs:

| Approach | Speed | Accuracy | Cost |
|----------|-------|----------|------|
| Keyword matching | <1ms | Medium | Free |
| LLM-based classification | 200-800ms | High | Per-request |
| Hybrid (keyword first, LLM fallback) | 1ms typical, 500ms edge cases | High | Minimal |

> **Analogy:** Keyword matching is like a phone tree ("Press 1 for billing"). LLM-based routing is like speaking to a human operator. The hybrid approach is the phone tree with a "Press 0 for operator" escape hatch.

---

## Step 1: Define Agent Capabilities Registry

Every specialist agent must declare what it can handle. This registry is the source of truth for routing decisions.

```python
AGENT_REGISTRY = {
    "kubernetes": {
        "description": "Troubleshoots Kubernetes workloads, pods, deployments, and cluster issues",
        "keywords": ["pod", "deploy", "kubectl", "namespace", "crashloopbackoff",
                     "oom", "node", "service", "ingress", "helm", "k8s", "container",
                     "replica", "statefulset", "daemonset", "pvc", "configmap"],
        "patterns": [r"why is .+ (crashing|failing|pending|restarting)",
                     r"scale .+ to \d+", r"rollback .+"],
        "examples": ["Why is my pod crashing?", "Scale the frontend to 5 replicas"]
    },
    "iac": {
        "description": "Reviews and generates Terraform, Pulumi, and CloudFormation code",
        "keywords": ["terraform", "tf", "pulumi", "cloudformation", "module",
                     "provider", "resource", "state", "plan", "apply", "drift",
                     "hcl", "infrastructure"],
        "patterns": [r"review .+ (terraform|infrastructure)", r"create .+ (module|resource)"],
        "examples": ["Review this Terraform module", "Create an S3 bucket with encryption"]
    },
    "observability": {
        "description": "Queries metrics, logs, and traces from Prometheus, Grafana, and Datadog",
        "keywords": ["metric", "alert", "grafana", "prometheus", "datadog",
                     "latency", "error rate", "p99", "dashboard", "log", "trace",
                     "slo", "sli", "throughput"],
        "patterns": [r"(show|get|what is) .+ (latency|error rate|throughput)",
                     r"why .+ (alerting|firing)"],
        "examples": ["What is the p99 latency for the auth service?", "Why is the SLO alerting?"]
    },
    "incident": {
        "description": "Coordinates incident response, runbooks, and post-mortems",
        "keywords": ["incident", "outage", "pagerduty", "runbook", "postmortem",
                     "rollback", "escalate", "sev1", "sev2", "downtime", "blast radius"],
        "patterns": [r"(declare|start|open) .+ incident", r"who is on.call"],
        "examples": ["Declare a SEV2 incident for payment failures", "Run the database failover runbook"]
    }
}
```

---

## Step 2: Build Keyword-Based Router

The keyword router is fast, deterministic, and requires no external calls. It handles 70-80% of requests without touching the LLM.

```python
import re
from collections import Counter


def keyword_route(query: str, registry: dict) -> dict:
    """Route based on keyword frequency and pattern matching."""
    query_lower = query.lower()
    scores = Counter()

    for agent_name, config in registry.items():
        # Score keyword matches
        for keyword in config["keywords"]:
            if keyword in query_lower:
                scores[agent_name] += 1

        # Score pattern matches (weighted higher)
        for pattern in config["patterns"]:
            if re.search(pattern, query_lower):
                scores[agent_name] += 3

    if not scores:
        return {"agent": None, "confidence": 0.0, "method": "keyword"}

    top_agent = scores.most_common(1)[0]
    total_score = sum(scores.values())
    confidence = top_agent[1] / total_score if total_score > 0 else 0.0

    return {
        "agent": top_agent[0],
        "confidence": round(confidence, 2),
        "method": "keyword",
        "scores": dict(scores)
    }
```

---

## Step 3: Build LLM-Based Router

When keywords are ambiguous or absent, use Claude to classify intent. The key is a tight, structured prompt that returns JSON.

```python
import anthropic


def llm_route(query: str, registry: dict) -> dict:
    """Use Claude to classify intent when keyword matching is insufficient."""
    client = anthropic.Anthropic()

    agent_descriptions = "\n".join(
        f"- {name}: {config['description']}"
        for name, config in registry.items()
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[{"role": "user", "content": query}],
        system=f"""You are an intent classifier for a DevOps platform.
Classify the user's request to ONE of these agents:

{agent_descriptions}

Respond with JSON only:
{{"agent": "<agent_name>", "confidence": <0.0-1.0>, "reasoning": "<one sentence>"}}

If the request needs multiple agents, respond:
{{"agents": ["<agent1>", "<agent2>"], "confidence": <0.0-1.0>, "reasoning": "<one sentence>"}}"""
    )

    import json
    result = json.loads(response.content[0].text)
    result["method"] = "llm"
    return result
```

---

## Step 4: Implement Fallback Strategy

The hybrid router tries the fast path first and escalates only when confidence is low.

```python
CONFIDENCE_THRESHOLD = 0.6


def hybrid_route(query: str, registry: dict) -> dict:
    """Keyword-first routing with LLM fallback for ambiguous requests."""
    # Fast path: try keyword matching
    keyword_result = keyword_route(query, registry)

    if keyword_result["agent"] and keyword_result["confidence"] >= CONFIDENCE_THRESHOLD:
        return keyword_result

    # Slow path: use LLM for ambiguous or unmatched queries
    llm_result = llm_route(query, registry)
    llm_result["fallback_reason"] = (
        "no_match" if keyword_result["agent"] is None
        else f"low_confidence ({keyword_result['confidence']})"
    )
    return llm_result
```

---

## Step 5: Handle Multi-Agent Requests

Real SRE requests often span multiple domains. "My pod is crashing and the Terraform state is locked" needs both the Kubernetes and IaC agents.

```python
def detect_multi_agent(query: str, registry: dict) -> dict:
    """Detect requests that require coordination between multiple agents."""
    keyword_result = keyword_route(query, registry)
    scores = keyword_result.get("scores", {})

    # Multiple agents score above threshold
    qualifying = {agent: score for agent, score in scores.items() if score >= 2}

    if len(qualifying) > 1:
        return {
            "multi_agent": True,
            "agents": list(qualifying.keys()),
            "primary": max(qualifying, key=qualifying.get),
            "coordination": "parallel" if _are_independent(qualifying.keys()) else "sequential",
            "method": "multi_agent_detection"
        }

    return {"multi_agent": False}


def _are_independent(agents) -> bool:
    """Determine if agent tasks can run in parallel."""
    # Sequential when one agent's output feeds another
    dependencies = {
        ("iac", "kubernetes"),  # IaC changes may affect K8s
        ("incident", "observability"),  # Incident needs metrics context
    }
    agent_list = list(agents)
    for i, a in enumerate(agent_list):
        for b in agent_list[i+1:]:
            if (a, b) in dependencies or (b, a) in dependencies:
                return False
    return True
```

---

## Step 6: Add Confidence Scoring

Confidence scoring lets the system know when to ask for clarification instead of guessing wrong.

```python
def route_with_confidence(query: str, registry: dict) -> dict:
    """Full routing pipeline with confidence-based behavior."""
    result = hybrid_route(query, registry)
    confidence = result.get("confidence", 0.0)

    if confidence >= 0.8:
        result["action"] = "delegate"
        result["message"] = f"Routing to {result['agent']} agent"
    elif confidence >= 0.5:
        result["action"] = "confirm"
        result["message"] = (
            f"I think this is a question for the {result['agent']} agent. "
            f"Should I proceed? (confidence: {confidence:.0%})"
        )
    else:
        result["action"] = "clarify"
        result["message"] = (
            "I'm not sure which specialist can help here. "
            "Could you clarify whether this is about infrastructure, "
            "Kubernetes, observability, or an incident?"
        )

    return result
```

---

## Routing Decisions in Practice

Here is how real SRE queries flow through the router:

```python
# High confidence keyword match — fast path
route_with_confidence("Why is my pod in CrashLoopBackOff?", AGENT_REGISTRY)
# => {"agent": "kubernetes", "confidence": 0.85, "action": "delegate", "method": "keyword"}

# Clear IaC request — fast path
route_with_confidence("Review this Terraform module for security issues", AGENT_REGISTRY)
# => {"agent": "iac", "confidence": 0.90, "action": "delegate", "method": "keyword"}

# Ambiguous request — triggers LLM fallback
route_with_confidence("The system is slow", AGENT_REGISTRY)
# => {"agent": "observability", "confidence": 0.55, "action": "confirm", "method": "llm"}

# Multi-domain request
route_with_confidence("Pod is OOMKilled and the PagerDuty alert is firing", AGENT_REGISTRY)
# => {"multi_agent": True, "agents": ["kubernetes", "incident"], "primary": "kubernetes"}
```

---

## What Success Looks Like

After completing this lab, your router correctly handles these scenarios:

- "Why is my pod crashing?" routes to the **Kubernetes** agent with high confidence
- "Review this Terraform" routes to the **IaC** agent with high confidence
- "What is the p99 latency?" routes to the **Observability** agent
- "Declare a SEV1 incident" routes to the **Incident** agent
- "The system is slow" triggers clarification or LLM-based classification
- "Pod is OOMKilled and Terraform state is locked" detects multi-agent coordination

The router adds less than 5ms of latency on the fast path and gracefully falls back to LLM classification only when needed.

---

## Key Takeaway

The router is the brain of the platform — get routing wrong and nothing else matters. A misrouted request means a wrong answer delivered with confidence, which is worse than no answer at all. Build the fast path for common cases, reserve the expensive LLM path for edge cases, and always give the system an escape hatch to ask for clarification rather than guess.

---

Next: [Lab 4: Specialist Agents](lab4-specialist-agents.md)
