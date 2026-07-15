#!/usr/bin/env python3
"""
Task 3: Prompt Caching for SRE Runbook Queries
================================================
Cache a large SRE runbook as a system prompt and make multiple
queries against it to demonstrate cost savings with prompt caching.

Prerequisites:
- pip install anthropic
- export ANTHROPIC_API_KEY=your-key-here
"""

import anthropic
import time

client = anthropic.Anthropic()

# A comprehensive SRE runbook (2000+ tokens) to cache as system context
SRE_RUNBOOK = """
# Site Reliability Engineering Runbook
# Organization: Production Operations Team
# Last Updated: 2025-07-01
# Classification: Internal Use Only

## 1. DATABASE FAILOVER PROCEDURES

### 1.1 PostgreSQL Primary Failover
Prerequisites: Confirm primary is truly unresponsive (not just slow).

Step 1: Verify primary status
  $ pg_isready -h primary-db.internal -p 5432
  $ psql -h primary-db.internal -c "SELECT pg_is_in_recovery();"

Step 2: Check replication lag on standby
  $ psql -h standby-db.internal -c "SELECT now() - pg_last_xact_replay_timestamp() AS lag;"
  ACCEPTABLE LAG: < 5 seconds for promotion

Step 3: Promote standby to primary
  $ psql -h standby-db.internal -c "SELECT pg_promote();"

Step 4: Update connection strings
  $ kubectl set env deployment/payment-service DB_HOST=standby-db.internal -n production
  $ kubectl set env deployment/order-service DB_HOST=standby-db.internal -n production
  $ kubectl set env deployment/user-service DB_HOST=standby-db.internal -n production

Step 5: Verify applications reconnect
  $ kubectl rollout restart deployment/payment-service -n production
  $ watch "kubectl get pods -n production | grep payment"

Step 6: Update DNS (for non-K8s consumers)
  $ aws route53 change-resource-record-sets --hosted-zone-id Z1234 --change-batch file://failover-dns.json

Recovery Time Objective (RTO): 5 minutes
Recovery Point Objective (RPO): < 5 seconds of data loss

### 1.2 Redis Cluster Failover
Step 1: Identify failed master
  $ redis-cli -h redis-cluster.internal cluster nodes | grep fail

Step 2: Force failover from replica
  $ redis-cli -h redis-replica-01.internal CLUSTER FAILOVER TAKEOVER

Step 3: Verify cluster health
  $ redis-cli -h redis-cluster.internal cluster info | grep cluster_state

## 2. KUBERNETES POD RESTART PROCEDURES

### 2.1 Single Pod Restart (Graceful)
  $ kubectl delete pod <pod-name> -n <namespace> --grace-period=30

### 2.2 Deployment Rolling Restart
  $ kubectl rollout restart deployment/<name> -n <namespace>
  $ kubectl rollout status deployment/<name> -n <namespace> --timeout=300s

### 2.3 Force Restart (Stuck Terminating)
  $ kubectl delete pod <pod-name> -n <namespace> --force --grace-period=0

### 2.4 CrashLoopBackOff Recovery
Step 1: Check logs
  $ kubectl logs <pod-name> -n <namespace> --previous

Step 2: Check events
  $ kubectl describe pod <pod-name> -n <namespace> | tail -20

Step 3: Check resource limits
  $ kubectl top pod <pod-name> -n <namespace> --containers

Step 4: If OOMKilled — increase memory limits:
  $ kubectl patch deployment <name> -n <namespace> -p '{"spec":{"template":{"spec":{"containers":[{"name":"<container>","resources":{"limits":{"memory":"1Gi"}}}]}}}}'

### 2.5 Node Drain (for maintenance)
  $ kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --grace-period=60
  $ kubectl uncordon <node-name>

## 3. INCIDENT SEVERITY CLASSIFICATIONS

### P1 — Critical (Customer-Facing Outage)
- Definition: Complete service unavailability or data loss affecting >5% of users
- Response Time: Immediate (< 5 minutes)
- Escalation: VP Engineering + On-call SRE + Service Owner
- Communication: StatusPage update within 10 minutes
- War Room: Mandatory, Slack #incident-war-room
- Examples:
  * Payment processing completely down
  * Authentication service unavailable
  * Data corruption or loss detected
  * Security breach confirmed

### P2 — High (Degraded Service)
- Definition: Significant degradation affecting user experience, partial functionality loss
- Response Time: < 15 minutes
- Escalation: On-call SRE + Service Owner
- Communication: StatusPage update within 30 minutes
- Examples:
  * API latency > 10x normal (p99 > 5s)
  * Error rate > 5% but service partially functional
  * Single availability zone failure (redundancy compromised)
  * Background job processing backed up > 1 hour

### P3 — Medium (Minor Impact)
- Definition: Minor issues not significantly affecting users
- Response Time: < 1 hour
- Escalation: On-call SRE
- Communication: Internal Slack notification
- Examples:
  * Non-critical microservice degraded
  * Monitoring gaps detected
  * Certificate expiring within 7 days
  * Disk usage > 80% on non-critical systems

### P4 — Low (Informational)
- Definition: Issues requiring attention but no immediate impact
- Response Time: Next business day
- Escalation: Team backlog
- Examples:
  * Technical debt items
  * Non-urgent security patches
  * Optimization opportunities
  * Documentation updates needed

## 4. ESCALATION POLICIES

### 4.1 On-Call Rotation
- Primary on-call: First responder (5 min SLA)
- Secondary on-call: Backup if primary doesn't acknowledge (10 min SLA)
- Engineering Manager: Auto-escalation after 15 min without acknowledgment

### 4.2 Escalation Matrix
| Severity | 0-5 min      | 5-15 min        | 15-30 min          | 30+ min            |
|----------|--------------|-----------------|--------------------|--------------------|
| P1       | Primary SRE  | Secondary SRE   | Eng Manager + VP   | CTO + StatusPage   |
| P2       | Primary SRE  | Secondary SRE   | Eng Manager        | Service Owner      |
| P3       | Primary SRE  | Secondary SRE   | —                  | —                  |
| P4       | Backlog      | —               | —                  | —                  |

### 4.3 Communication Channels
- P1/P2: Slack #incident-war-room + PagerDuty + StatusPage
- P3: Slack #ops-alerts
- P4: Jira ticket in OPS project

## 5. COMMON TROUBLESHOOTING STEPS

### 5.1 High CPU Usage
Step 1: Identify top consumers
  $ kubectl top pods -n <namespace> --sort-by=cpu
Step 2: Profile the process
  $ kubectl exec -it <pod> -- top -H -p 1
Step 3: Check for hot loops or GC pressure
  $ kubectl exec -it <pod> -- jstack 1 | grep -A 20 "RUNNABLE"

### 5.2 High Memory Usage
Step 1: Check current usage vs limits
  $ kubectl top pods -n <namespace> --sort-by=memory --containers
Step 2: Heap dump (Java)
  $ kubectl exec -it <pod> -- jmap -dump:live,format=b,file=/tmp/heap.hprof 1
  $ kubectl cp <pod>:/tmp/heap.hprof ./heap.hprof
Step 3: Check for memory leaks
  $ kubectl exec -it <pod> -- jstat -gc 1 1000

### 5.3 Network Connectivity Issues
Step 1: DNS resolution
  $ kubectl exec -it <pod> -- nslookup <service-name>
Step 2: TCP connectivity
  $ kubectl exec -it <pod> -- nc -zv <host> <port>
Step 3: Check network policies
  $ kubectl get networkpolicies -n <namespace> -o yaml

### 5.4 Disk Pressure
Step 1: Check node disk usage
  $ kubectl describe node <node> | grep -A 5 "Conditions"
Step 2: Find large files in pod
  $ kubectl exec -it <pod> -- du -sh /* 2>/dev/null | sort -rh | head -10
Step 3: Clean up if needed
  $ kubectl exec -it <pod> -- find /tmp -mtime +7 -delete

### 5.5 SSL/TLS Certificate Issues
Step 1: Check certificate expiry
  $ echo | openssl s_client -connect <host>:443 2>/dev/null | openssl x509 -noout -dates
Step 2: Verify cert-manager status
  $ kubectl get certificates -A
  $ kubectl describe certificate <name> -n <namespace>
Step 3: Force renewal
  $ kubectl delete secret <tls-secret> -n <namespace>
  $ kubectl annotate certificate <name> cert-manager.io/issuer-name- -n <namespace>
"""

# Queries that an on-call SRE might ask during different incidents
QUERIES = [
    {
        "scenario": "Database failover during outage",
        "query": "Our primary PostgreSQL database is unresponsive and we need to failover. What are the exact steps, including how to check replication lag and what the acceptable lag threshold is?"
    },
    {
        "scenario": "Classifying a new incident",
        "query": "We're seeing API latency at 15x normal with p99 at 8 seconds and error rate at 7%. Users can still access the service but it's very slow. Is this a P1 or P2? What's the response time SLA and who do I escalate to?"
    },
    {
        "scenario": "Pod stuck in CrashLoopBackOff",
        "query": "I have a pod in CrashLoopBackOff that's been OOMKilled multiple times. What's the step-by-step procedure to diagnose and fix this? Include the commands to check previous logs and increase memory limits."
    },
]


def query_with_cache(query_num: int, scenario: str, query: str):
    """Query the cached runbook and display cache metrics."""
    print(f"\n{'─' * 65}")
    print(f"  Query {query_num}: {scenario}")
    print(f"{'─' * 65}")
    print(f"  Question: {query[:80]}...")

    start_time = time.time()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=[{
            "type": "text",
            "text": SRE_RUNBOOK,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{"role": "user", "content": query}]
    )
    elapsed = time.time() - start_time

    # Extract cache metrics
    cache_creation = getattr(message.usage, "cache_creation_input_tokens", 0) or 0
    cache_read = getattr(message.usage, "cache_read_input_tokens", 0) or 0
    input_tokens = message.usage.input_tokens

    print(f"\n  Response Time: {elapsed:.2f}s")
    print(f"  Input Tokens:  {input_tokens}")
    print(f"  Output Tokens: {message.usage.output_tokens}")
    print(f"  Cache Write:   {cache_creation} tokens")
    print(f"  Cache Read:    {cache_read} tokens")

    # Show if cache was hit or miss
    if cache_creation > 0:
        print(f"  Cache Status:  MISS (wrote {cache_creation} tokens to cache)")
    elif cache_read > 0:
        print(f"  Cache Status:  HIT (read {cache_read} tokens from cache)")
    else:
        print(f"  Cache Status:  No caching applied")

    # Display response (truncated)
    response_text = message.content[0].text
    print(f"\n  Answer (first 400 chars):")
    for line in response_text[:400].split("\n"):
        print(f"    {line}")
    print("    ...")

    return {
        "elapsed": elapsed,
        "input_tokens": input_tokens,
        "output_tokens": message.usage.output_tokens,
        "cache_creation": cache_creation,
        "cache_read": cache_read,
    }


def main():
    print("=" * 65)
    print("  TASK 3: PROMPT CACHING FOR SRE RUNBOOK QUERIES")
    print("  Cache a large runbook and make multiple queries against it")
    print("=" * 65)

    print(f"\n  Runbook size: ~{len(SRE_RUNBOOK)} characters")
    print("  Strategy: Cache the runbook as system prompt, query 3 times")
    print("  Expected: First call writes cache, subsequent calls read cache")

    results = []
    for i, q in enumerate(QUERIES, 1):
        result = query_with_cache(i, q["scenario"], q["query"])
        results.append(result)
        # Brief pause between calls to ensure cache is available
        if i < len(QUERIES):
            time.sleep(1)

    # Cost analysis
    print(f"\n{'=' * 65}")
    print("  CACHE ECONOMICS ANALYSIS")
    print(f"{'=' * 65}")

    total_cache_write = sum(r["cache_creation"] for r in results)
    total_cache_read = sum(r["cache_read"] for r in results)
    total_input = sum(r["input_tokens"] for r in results)

    print(f"\n  Total input tokens across 3 queries:  {total_input}")
    print(f"  Tokens written to cache:              {total_cache_write}")
    print(f"  Tokens read from cache:               {total_cache_read}")

    # Pricing (Sonnet 4 as of 2025)
    # Input: $3/MTok, Cache write: $3.75/MTok, Cache read: $0.30/MTok
    input_cost_per_mtok = 3.00
    cache_write_cost_per_mtok = 3.75
    cache_read_cost_per_mtok = 0.30

    # Cost without caching (all tokens billed as input)
    runbook_tokens_estimate = total_cache_write if total_cache_write > 0 else total_cache_read
    if runbook_tokens_estimate == 0:
        runbook_tokens_estimate = 2500  # fallback estimate

    cost_without_cache = (runbook_tokens_estimate * 3 * input_cost_per_mtok) / 1_000_000
    cost_with_cache = (
        (total_cache_write * cache_write_cost_per_mtok) +
        (total_cache_read * cache_read_cost_per_mtok) +
        (total_input * input_cost_per_mtok)
    ) / 1_000_000

    print(f"\n  Estimated cost WITHOUT caching: ${cost_without_cache:.6f}")
    print(f"  Estimated cost WITH caching:    ${cost_with_cache:.6f}")
    if cost_without_cache > 0:
        savings_pct = ((cost_without_cache - cost_with_cache) / cost_without_cache) * 100
        print(f"  Savings:                        {savings_pct:.1f}%")

    print(f"\n  At scale (1000 queries/day against same runbook):")
    daily_no_cache = (runbook_tokens_estimate * 1000 * input_cost_per_mtok) / 1_000_000
    daily_cached = (
        (runbook_tokens_estimate * cache_write_cost_per_mtok) +
        (runbook_tokens_estimate * 999 * cache_read_cost_per_mtok)
    ) / 1_000_000
    print(f"  Daily cost without caching: ${daily_no_cache:.4f}")
    print(f"  Daily cost with caching:    ${daily_cached:.4f}")
    print(f"  Daily savings:              ${daily_no_cache - daily_cached:.4f}")
    print(f"  Monthly savings (30 days):  ${(daily_no_cache - daily_cached) * 30:.2f}")

    # Key Learning
    print(f"\n{'=' * 65}")
    print("  KEY LEARNING")
    print(f"{'=' * 65}")
    print("""
  Prompt caching economics:
  - Cache write costs 25% MORE than regular input (one-time cost)
  - Cache reads cost 90% LESS than regular input (repeated savings)
  - Break-even: After just 2 queries against the same cached content

  Best use cases for SRE:
  - Runbook lookups during incidents (same context, different questions)
  - Alert analysis with standard operating procedures cached
  - ChatOps bots with persistent system knowledge
  - Batch processing logs against the same analysis rules

  Cache lifetime: 5 minutes (refreshed on each use)
  Minimum cacheable: 1024 tokens for Sonnet/Opus, 2048 for Haiku
    """)
    print("  Workshop Episode 3 complete!")
    print(f"{'=' * 65}")


if __name__ == "__main__":
    main()
