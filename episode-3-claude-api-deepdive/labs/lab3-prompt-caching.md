# Lab 3: Prompt Caching — Redis for Your AI Context

## Mission

Cache expensive system prompts to save cost on repeated SRE queries. When your team runs hundreds of questions against the same incident runbook, you should not pay full price every single time.

---

## The Concept: Redis for Your AI Context

If you have used Redis to cache database query results, you already understand prompt caching.

| Redis Cache | Prompt Cache |
|---|---|
| First query hits the DB (slow, expensive) | First call loads full runbook into context (cache WRITE — costs extra 25%) |
| Subsequent queries hit Redis (fast, cheap) | Subsequent calls reuse cached context (cache READ — 90% cheaper than re-reading) |
| Keys expire after TTL | Cache expires after 5 minutes of inactivity (like a Redis TTL) |

**The mental model:**

```
First call:   [System Prompt: 4000 tokens] → Cache WRITE (1.25x cost)
Call #2-100:  [System Prompt: cached]       → Cache READ  (0.1x cost)
After 5 min idle: Cache expires             → Next call is a WRITE again
```

---

## Why This Matters for SRE

In a real incident, your team might ask dozens of questions against the same runbook:

- "What's the procedure for DB failover?"
- "What are the rollback steps for the payment service?"
- "What's the escalation path for P1 incidents?"

Without caching, every single query re-reads your entire 4000-token runbook at full price. With caching, you pay once and get 99 queries at 90% off.

---

## Step 1: Set Up Your Runbook as a Cached System Prompt

```python
import anthropic

client = anthropic.Anthropic()

# Simulate a large SRE runbook (in production, load from your actual runbook)
sre_runbook = """
# Production Incident Runbook v2.4

## Database Failover Procedure
1. Confirm primary DB is unresponsive (check pg_isready on primary)
2. Verify replication lag on standby: SELECT pg_last_xact_replay_timestamp()
3. Promote standby: pg_ctl promote -D /var/lib/postgresql/data
4. Update connection pooler (PgBouncer) to point to new primary
5. Verify application connectivity: kubectl exec -it app-pod -- pg_isready -h db-primary
6. Notify #incident-channel with failover completion time

## Kubernetes Pod Crash Recovery
1. Check pod status: kubectl get pods -n production --field-selector=status.phase!=Running
2. Examine crash logs: kubectl logs <pod-name> --previous -n production
3. Check resource limits: kubectl describe pod <pod-name> -n production | grep -A5 Limits
4. If OOMKilled: increase memory limits in deployment manifest
5. If CrashLoopBackOff: check application health endpoint and dependencies
6. Rolling restart if needed: kubectl rollout restart deployment/<name> -n production

## Service Mesh (Istio) Troubleshooting
1. Check sidecar injection: kubectl get pods -n production -o jsonpath='{.items[*].spec.containers[*].name}'
2. Verify mTLS: istioctl authn tls-check <pod-name> -n production
3. Check circuit breaker state: istioctl proxy-config cluster <pod-name> -n production
4. Examine envoy logs: kubectl logs <pod-name> -c istio-proxy -n production
5. Reset circuit breaker: kubectl delete pod <pod-name> -n production (forces new sidecar)

## Escalation Matrix
- P1 (Service Down): Page on-call SRE → 15 min no response → Page SRE Manager → 30 min → VP Engineering
- P2 (Degraded): Slack #incident-channel → 30 min → Page on-call SRE
- P3 (Minor): Jira ticket → Next business day triage
- P4 (Cosmetic): Backlog grooming

## Rollback Procedures
1. Identify last known good revision: kubectl rollout history deployment/<name> -n production
2. Rollback: kubectl rollout undo deployment/<name> --to-revision=<N> -n production
3. Verify: kubectl rollout status deployment/<name> -n production
4. If Helm: helm rollback <release> <revision> -n production
5. Post-rollback: verify all health checks pass, notify stakeholders
"""

# Make the first API call with cache_control on the system prompt
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": sre_runbook,
        "cache_control": {"type": "ephemeral"}
    }],
    messages=[{"role": "user", "content": "What's the procedure for DB failover?"}]
)

print("=== First Call (Cache WRITE) ===")
print(f"Response: {message.content[0].text[:200]}...")
print(f"\nCache creation input tokens: {message.usage.cache_creation_input_tokens}")
print(f"Cache read input tokens: {message.usage.cache_read_input_tokens}")
print(f"Regular input tokens: {message.usage.input_tokens}")
```

---

## Step 2: Make Subsequent Calls (Cache HITs)

```python
import time

# Wait a moment, then ask another question against the same cached runbook
time.sleep(1)

message2 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": sre_runbook,
        "cache_control": {"type": "ephemeral"}
    }],
    messages=[{"role": "user", "content": "What's the escalation path for a P1 incident?"}]
)

print("=== Second Call (Cache READ) ===")
print(f"Response: {message2.content[0].text[:200]}...")
print(f"\nCache creation input tokens: {message2.usage.cache_creation_input_tokens}")
print(f"Cache read input tokens: {message2.usage.cache_read_input_tokens}")
print(f"Regular input tokens: {message2.usage.input_tokens}")
```

---

## Step 3: Check Cache Metrics

```python
def print_cache_metrics(message, call_number):
    """Display cache performance metrics for a given API response."""
    print(f"\n{'='*50}")
    print(f"Call #{call_number} Cache Metrics")
    print(f"{'='*50}")
    print(f"Cache write tokens: {message.usage.cache_creation_input_tokens}")
    print(f"Cache read tokens:  {message.usage.cache_read_input_tokens}")
    print(f"Regular input tokens: {message.usage.input_tokens}")
    print(f"Output tokens: {message.usage.output_tokens}")

    if message.usage.cache_creation_input_tokens > 0:
        print(f"Status: CACHE MISS (wrote to cache)")
    elif message.usage.cache_read_input_tokens > 0:
        print(f"Status: CACHE HIT (read from cache)")
    else:
        print(f"Status: NO CACHING (prompt too short or caching not triggered)")

# Run multiple queries to demonstrate caching behavior
queries = [
    "What's the procedure for DB failover?",
    "How do I troubleshoot Istio mTLS issues?",
    "What are the rollback steps using Helm?",
    "How do I handle a pod in CrashLoopBackOff?",
    "What's the P2 escalation process?",
]

for i, query in enumerate(queries, 1):
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=[{
            "type": "text",
            "text": sre_runbook,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{"role": "user", "content": query}]
    )
    print_cache_metrics(msg, i)
```

---

## Step 4: Calculate Cost Savings

```python
# Cost calculation for Claude Sonnet
# Pricing (per million tokens):
#   Regular input:    $3.00
#   Cache write:      $3.75 (25% more than regular)
#   Cache read:       $0.30 (90% less than regular)
#   Output:           $15.00

system_prompt_tokens = 4000  # Our runbook size
num_queries = 100
avg_query_tokens = 50  # Average user question length
avg_output_tokens = 200  # Average response length

# WITHOUT caching: every call pays full input price
no_cache_input_cost = (system_prompt_tokens + avg_query_tokens) * num_queries * (3.00 / 1_000_000)
no_cache_output_cost = avg_output_tokens * num_queries * (15.00 / 1_000_000)
no_cache_total = no_cache_input_cost + no_cache_output_cost

# WITH caching: first call is a write, remaining 99 are reads
cache_write_cost = system_prompt_tokens * 1 * (3.75 / 1_000_000)  # First call
cache_read_cost = system_prompt_tokens * 99 * (0.30 / 1_000_000)  # Subsequent calls
cache_query_cost = avg_query_tokens * num_queries * (3.00 / 1_000_000)  # User queries (not cached)
cache_output_cost = avg_output_tokens * num_queries * (15.00 / 1_000_000)
cache_total = cache_write_cost + cache_read_cost + cache_query_cost + cache_output_cost

savings = no_cache_total - cache_total
savings_pct = (savings / no_cache_total) * 100

print("=" * 60)
print("COST COMPARISON: 100 Queries Against a 4000-Token Runbook")
print("=" * 60)
print(f"\n{'Category':<30} {'Without Cache':<15} {'With Cache':<15}")
print(f"{'-'*60}")
print(f"{'System prompt input':<30} ${no_cache_input_cost - (avg_query_tokens * num_queries * 3.00 / 1_000_000):.4f}      ${cache_write_cost + cache_read_cost:.4f}")
print(f"{'User query input':<30} ${avg_query_tokens * num_queries * 3.00 / 1_000_000:.4f}      ${cache_query_cost:.4f}")
print(f"{'Output':<30} ${no_cache_output_cost:.4f}      ${cache_output_cost:.4f}")
print(f"{'-'*60}")
print(f"{'TOTAL':<30} ${no_cache_total:.4f}      ${cache_total:.4f}")
print(f"\n{'Savings':<30} ${savings:.4f} ({savings_pct:.1f}%)")
```

**Expected output:**

```
============================================================
COST COMPARISON: 100 Queries Against a 4000-Token Runbook
============================================================

Category                       Without Cache   With Cache
------------------------------------------------------------
System prompt input            $1.2000         $0.1337
User query input               $0.0150         $0.0150
Output                         $0.3000         $0.3000
------------------------------------------------------------
TOTAL                          $1.5150         $0.4487

Savings                        $1.0663 (70.4%)
```

---

## Important Constraints

| Model | Minimum Cacheable Prompt Size |
|---|---|
| claude-haiku-35-20241022 | 1024 tokens |
| claude-sonnet-4-20250514 | 2048 tokens |
| claude-opus-4-20250514 | 2048 tokens |

If your system prompt is smaller than the minimum, caching will not activate. For SRE runbooks, this is rarely an issue — most runbooks easily exceed 2048 tokens.

**Other considerations:**
- Cache TTL is 5 minutes of inactivity. If no request hits the cache for 5 minutes, it expires.
- The `cache_control` marker must be placed on the same content block each time. Changing the text invalidates the cache.
- You can cache multiple blocks — useful for separating static runbooks from dynamic context.

---

## What Success Looks Like

```
=== First Call (Cache WRITE) ===
Cache creation input tokens: 4000    ← System prompt written to cache
Cache read input tokens: 0           ← Nothing to read yet
Regular input tokens: 50             ← Just the user query

=== Second Call (Cache READ) ===
Cache creation input tokens: 0       ← No write needed
Cache read input tokens: 4000        ← Reading from cache (90% cheaper!)
Regular input tokens: 50             ← Just the user query
```

First call shows `cache_creation_input_tokens > 0` (the cache WRITE). Subsequent calls show `cache_read_input_tokens > 0` (cache HITs at 90% discount).

---

## Key Takeaway

Prompt caching turns expensive repeated context into a one-time cost — essential for high-volume SRE automation. Any time your system has a stable system prompt that gets hit with many different user queries (runbook Q&A, log analysis, alert triage), prompt caching should be your default. The 25% write premium pays for itself after just 2 cache reads.
