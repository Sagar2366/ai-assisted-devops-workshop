# Lab 3: Chain-of-Thought Prompting

## Mission

Use Chain-of-Thought (CoT) prompting to solve complex, multi-step SRE troubleshooting problems. By forcing the model to show its reasoning step by step, you get more accurate diagnoses and catch subtle issues that direct prompting misses.

---

## Concept: What is Chain-of-Thought Prompting?

Chain-of-Thought prompting asks the model to break down its reasoning into explicit steps before reaching a conclusion. Instead of jumping directly to an answer, the model "thinks out loud."

### The Analogy

Picture a senior SRE debugging a production outage on an incident bridge. They do not just say "It's the database." Instead, they walk through their reasoning:

"OK, the error rate spiked at 14:23. Let me check what changed around that time... I see a deployment at 14:20. But the deployment was to a different service. Let me look at dependencies... the deployed service talks to Redis, and Redis is shared with the failing service. Let me check Redis metrics... connection count spiked at 14:22. That's our root cause — the deployment opened too many Redis connections and starved the other service."

That structured reasoning process is Chain-of-Thought. It catches the indirect dependency that a quick "what's wrong?" would miss.

### When to Use Chain-of-Thought

- Complex incidents with multiple possible causes
- Situations where correlating timelines matters
- Multi-service dependency analysis
- Capacity planning calculations
- Change risk assessments with cascading effects

---

## Step 1: Zero-Shot vs. Chain-of-Thought Comparison

```python
from sre_prompt import call_claude

# A complex incident scenario
scenario = """
Timeline of events:
- 14:00 - All metrics normal
- 14:15 - Deploy: auth-service v3.2.0 (added OAuth2 token caching layer)
- 14:20 - Auth-service memory usage increases from 512MB to 1.8GB
- 14:25 - Redis connection count jumps from 100 to 2,400
- 14:28 - Payment-service starts logging "Redis connection timeout" errors
- 14:30 - Order-service latency increases from 50ms to 4,200ms
- 14:32 - Alert fires: payment-service error rate > 5%
- 14:35 - Alert fires: order-service p99 latency > 5000ms
- 14:38 - Customer support reports checkout failures

Current state:
- auth-service: Running but using 1.8GB memory (limit: 2GB)
- payment-service: 12% error rate
- order-service: p99 latency 4,500ms
- Redis: 2,400 connections (max: 2,500)
- All other services: normal
"""

# Zero-shot approach
zero_shot_prompt = f"""What is the root cause of this incident and how should we fix it?

{scenario}"""

# Chain-of-Thought approach
cot_prompt = f"""Analyze this incident step by step. For each step, explain your reasoning before moving to the next.

Step 1: Identify the trigger event (what changed?)
Step 2: Trace the cause-and-effect chain
Step 3: Identify the root cause vs. symptoms
Step 4: Determine why existing safeguards did not prevent this
Step 5: Recommend immediate fix
Step 6: Recommend long-term prevention

{scenario}"""

print("=== ZERO-SHOT ===")
print(call_claude(zero_shot_prompt))
print("\n" + "="*60 + "\n")
print("=== CHAIN-OF-THOUGHT ===")
print(call_claude(cot_prompt))
```

Notice how the CoT version traces the full dependency chain and identifies that the auth-service caching layer is the root cause, while the zero-shot might jump to "Redis is overloaded" without explaining why.

---

## Step 2: The "Think Step by Step" Technique

Sometimes all you need is a simple trigger phrase:

```python
from sre_prompt import call_claude

capacity_problem = """
Current state of our Kubernetes cluster:
- 5 worker nodes, each with 16GB RAM and 8 CPU cores
- Current total usage: 62GB RAM (77.5%), 28 CPU cores (70%)
- We need to deploy a new ML inference service:
  - Each replica needs: 4GB RAM, 2 CPU cores
  - Minimum 3 replicas for HA
  - Expected to scale to 8 replicas during peak
  - Peak hours: 9am-5pm weekdays
- We also have a planned deployment next week:
  - Monitoring stack upgrade requiring 2GB additional RAM per node
- Node auto-scaling is enabled but takes 4 minutes to provision

Question: Can we safely deploy the ML service tomorrow? What risks exist?
"""

# Without CoT
direct_prompt = f"Answer this question:\n{capacity_problem}"

# With CoT
cot_prompt = f"""Think step by step about this capacity planning question. Show your calculations at each step.

{capacity_problem}"""

print("=== DIRECT ===")
print(call_claude(direct_prompt))
print("\n" + "="*60 + "\n")
print("=== STEP BY STEP ===")
print(call_claude(cot_prompt))
```

The step-by-step version will show actual math:
- Current free: 18GB RAM, 12 CPU cores
- ML service minimum: 12GB RAM, 6 CPU cores
- ML service peak: 32GB RAM, 16 CPU cores (exceeds available!)
- Plus monitoring upgrade: 10GB additional RAM needed next week

---

## Step 3: Structured Chain-of-Thought for Incident Analysis

```python
from sre_prompt import call_claude_with_system

system_prompt = """You are a senior SRE performing root cause analysis. 
Always structure your analysis using this framework:

1. OBSERVE: What are the symptoms? What is the blast radius?
2. ORIENT: What changed recently? What are the dependencies?
3. HYPOTHESIZE: What are the possible causes? Rank by likelihood.
4. TEST: What would you check to confirm/deny each hypothesis?
5. CONCLUDE: What is the root cause? What is the fix?
6. PREVENT: How do we prevent this class of issue?

Show your reasoning at each step. Do not skip steps."""

incident_data = """
Incident: Users in EU region reporting intermittent 504 errors on the API.

Data collected:
- Global error rate: 2.1% (normally 0.1%)
- EU-specific error rate: 8.7%
- US error rate: 0.2% (normal)
- APAC error rate: 0.15% (normal)
- EU load balancer health checks: 2/3 backends healthy
- DNS resolution for api.example.com: resolving correctly
- EU backend pod count: 3 (expected: 3)
- Pod restarts in last hour: eu-api-pod-3 restarted 4 times
- Last deployment: 6 hours ago (unrelated billing service in US)
- SSL certificate expiry: 45 days remaining
- eu-api-pod-3 logs: "failed to connect to cache-eu-primary:6379"
- cache-eu-primary status: Running but accepting no connections
- cache-eu-primary memory: 8.0GB / 8.0GB (100%)
"""

response = call_claude_with_system(system_prompt, f"Analyze this incident:\n\n{incident_data}")
print(response)
```

---

## Step 4: Chain-of-Thought for Change Risk Assessment

```python
from sre_prompt import call_claude

terraform_change = """
We plan to apply this Terraform change to production:

```hcl
# Change 1: Increase RDS instance size
resource "aws_db_instance" "primary" {
-  instance_class = "db.r5.xlarge"
+  instance_class = "db.r5.2xlarge"
   apply_immediately = true
}

# Change 2: Modify security group
resource "aws_security_group_rule" "api_to_db" {
-  from_port = 5432
-  to_port   = 5432
+  from_port = 5432
+  to_port   = 5433
   cidr_blocks = ["10.0.0.0/16"]
}

# Change 3: Update auto-scaling
resource "aws_autoscaling_group" "api" {
-  min_size = 3
-  max_size = 10
+  min_size = 2
+  max_size = 15
}
```

Context: This is being applied during business hours. The database serves 3 microservices.
"""

cot_prompt = f"""Assess the risk of this Terraform change. Think through each change independently, then consider their combined effect.

For each change, reason through:
- What will happen during the apply?
- What could go wrong?
- Is it reversible?
- What is the blast radius?

Then provide an overall risk assessment.

{terraform_change}"""

print(call_claude(cot_prompt))
```

---

## Step 5: Multi-Hypothesis Debugging

```python
from sre_prompt import call_claude

debugging_scenario = """
A Kubernetes service 'recommendation-engine' is experiencing intermittent failures.

Observations:
- Failures happen roughly every 5 minutes, lasting 10-30 seconds each time
- During failures: HTTP 503 responses from the service
- Pod CPU: 15% (low)
- Pod Memory: 60% (normal)
- Pod restart count: 0
- HPA: 3 replicas, no scaling events
- Network policies: allow all within namespace
- Readiness probe: HTTP GET /healthz every 10s, timeout 5s
- The /healthz endpoint queries the database
- Database connection pool: 20 connections per pod
- Database max connections: 100
- A cron job runs every 5 minutes that does batch processing using 40 DB connections
"""

prompt = f"""Debug this issue using multi-hypothesis reasoning.

Generate at least 3 hypotheses, then systematically evaluate each one against the evidence. Eliminate hypotheses that don't fit ALL the observations. Show your reasoning for each elimination.

{debugging_scenario}"""

print(call_claude(prompt))
```

The CoT approach should identify that the cron job (40 connections every 5 minutes) combined with the 3 pods (60 connections) hits the max_connections limit (100), causing the healthz probe to fail (it queries the DB), which makes the readiness probe fail, which removes the pod from the service temporarily.

---

## What Success Looks Like

After completing this lab, you can:

- Use Chain-of-Thought to debug complex multi-service incidents
- Apply structured reasoning frameworks (OBSERVE/ORIENT/HYPOTHESIZE/TEST/CONCLUDE)
- Show the model how to work through capacity planning with actual calculations
- Generate multi-hypothesis analysis that eliminates possibilities systematically
- Catch indirect causes and cascading failures that zero-shot misses

Example CoT output structure:

```
Step 1 - OBSERVE: Three services affected, but only in EU region...
Step 2 - ORIENT: No deployments in EU recently, but cache-eu-primary at 100% memory...
Step 3 - HYPOTHESIZE: 
  H1 (HIGH): Redis OOM causing connection rejection → pod health failures
  H2 (LOW): Network partition — but only one pod affected, not all
  H3 (LOW): DNS issue — but resolution is working correctly
Step 4 - TEST: Confirm H1 by checking Redis maxmemory-policy and eviction stats
Step 5 - CONCLUDE: Redis memory exhaustion is root cause...
Step 6 - PREVENT: Set maxmemory-policy to allkeys-lru, add memory alerts at 80%...
```

---

## Key Takeaway

Chain-of-Thought prompting is essential for complex problems where the answer is not obvious. By forcing explicit reasoning steps, you get three benefits: (1) more accurate conclusions because the model cannot skip logical steps, (2) visible reasoning you can audit and correct, and (3) better handling of multi-factor problems where causes interact. Use CoT whenever an incident involves timelines, dependencies, or multiple possible causes.

---

## Next

[Lab 4: Production Templates](lab4-templates.md) — Build 4 reusable SRE prompt templates for daily work
