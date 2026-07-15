# Lab 2: Extended Thinking — The SRE's Internal Monologue

## Mission

Use extended thinking for deep root cause analysis of complex, multi-service cascading failures where surface-level answers are not enough.

---

## Concept: The Internal Monologue

When a senior SRE investigates a cascading failure, they do not just blurt out an answer. They think through it step by step, checking each system, following the dependency chain, and ruling out possibilities before arriving at a conclusion.

**Without extended thinking** (just the answer):
> "The frontend is timing out because the API server is returning 503s."

**With extended thinking** (shows reasoning):
> "Let me trace this... frontend timeouts started at 03:42... API 503s started at 03:41... the API depends on the database connection pool... pool exhaustion started at 03:40... the pool has 20 max connections but I see 20 active queries stuck on a table lock... there was a migration deployed at 03:38 that added an index on a large table... that is the root cause."

Extended thinking gives you the AI's reasoning chain — the same kind of systematic debugging your best engineers do mentally.

---

## How Extended Thinking Works

The `thinking` parameter tells Claude to reason through the problem before responding. You control how much thinking budget to allocate:

```python
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    messages=[{"role": "user", "content": "..."}]
)
```

Key parameters:
- `type: "enabled"` — Turns on extended thinking
- `budget_tokens` — Maximum tokens Claude can use for internal reasoning (minimum: 1024)

> **Analogy:** `budget_tokens` is like setting a time-box for your incident investigation. A 1024-token budget is like saying "give me a quick 2-minute assessment." A 10000-token budget is "take 30 minutes to really dig into this."

---

## The Scenario: A Cascading Multi-Service Failure

Here is a complex production incident with multiple services failing in sequence:

```python
INCIDENT_DATA = """
=== CASCADING FAILURE INCIDENT REPORT ===
Time: 2024-03-15 03:38 - 03:55 UTC
Severity: SEV-1
Services affected: postgres-primary, api-gateway, payment-service, frontend, queue-worker

=== TIMELINE OF ALERTS (in order received) ===

03:42:15 - ALERT: frontend-web - Error rate > 5% (current: 12%)
           HTTP 504 Gateway Timeout responses spiking
           Affected endpoints: /checkout, /order-status, /account

03:42:01 - ALERT: api-gateway - Response latency p99 > 5s (current: 12.4s)
           Upstream connection timeouts to payment-service
           Healthy backends: 1/4

03:41:45 - ALERT: payment-service - Pod restarts detected
           payment-service-7d4b8-{a,b,c} CrashLoopBackOff
           Reason: "connection refused to postgres-primary:5432"

03:41:30 - ALERT: queue-worker - Queue depth > 10000 (current: 34,521)
           Consumer lag increasing: 2,400 messages/sec intake, 0 messages/sec processed
           Dead letter queue filling: payment.process.dlq

03:40:55 - ALERT: postgres-primary - Active connections: 200/200 (pool exhausted)
           Waiting queries: 147
           Longest running query: 245s
           Lock wait events: 89

=== INFRASTRUCTURE CONTEXT ===

PostgreSQL Configuration:
  max_connections: 200
  connection pool (pgbouncer): max_client_conn=200, default_pool_size=20
  Current locks: ACCESS EXCLUSIVE on table "transactions" (held for 247s)

Recent Changes (from deploy log):
  03:38:00 - Database migration #447 applied: "ALTER TABLE transactions ADD COLUMN reconciled_at TIMESTAMP; CREATE INDEX idx_transactions_reconciled ON transactions(reconciled_at);"
  03:37:00 - Deployment: payment-service v2.3.1 (no code changes, dependency update only)

Service Dependencies:
  frontend -> api-gateway -> payment-service -> postgres-primary
  queue-worker -> postgres-primary

Connection Pool Status (pgbouncer):
  active: 200/200
  waiting: 147
  idle: 0
  longest_wait: 45s

=== METRICS SNAPSHOT AT 03:42 ===

postgres-primary:
  CPU: 98%
  IOPS: 15,000 (baseline: 2,000)
  Disk queue depth: 47
  Replication lag: 12s (baseline: <100ms)

payment-service pods:
  Restart count: 3 each in last 5 minutes
  Last log: "sqlalchemy.exc.OperationalError: could not connect to server: Connection refused"

queue-worker:
  Processing rate: 0 msg/sec (baseline: 2,400 msg/sec)
  Memory: stable at 256Mi
  CPU: 2% (baseline: 45%)
"""
```

---

## Step-by-Step: Using Extended Thinking

Create a file called `thinking_analysis.py`:

```python
import anthropic

client = anthropic.Anthropic()

INCIDENT_DATA = """
=== CASCADING FAILURE INCIDENT REPORT ===
Time: 2024-03-15 03:38 - 03:55 UTC
Severity: SEV-1
Services affected: postgres-primary, api-gateway, payment-service, frontend, queue-worker

=== TIMELINE OF ALERTS (in order received) ===

03:42:15 - ALERT: frontend-web - Error rate > 5% (current: 12%)
           HTTP 504 Gateway Timeout responses spiking
           Affected endpoints: /checkout, /order-status, /account

03:42:01 - ALERT: api-gateway - Response latency p99 > 5s (current: 12.4s)
           Upstream connection timeouts to payment-service
           Healthy backends: 1/4

03:41:45 - ALERT: payment-service - Pod restarts detected
           payment-service-7d4b8-{a,b,c} CrashLoopBackOff
           Reason: "connection refused to postgres-primary:5432"

03:41:30 - ALERT: queue-worker - Queue depth > 10000 (current: 34,521)
           Consumer lag increasing: 2,400 messages/sec intake, 0 messages/sec processed
           Dead letter queue filling: payment.process.dlq

03:40:55 - ALERT: postgres-primary - Active connections: 200/200 (pool exhausted)
           Waiting queries: 147
           Longest running query: 245s
           Lock wait events: 89

=== INFRASTRUCTURE CONTEXT ===

PostgreSQL Configuration:
  max_connections: 200
  connection pool (pgbouncer): max_client_conn=200, default_pool_size=20
  Current locks: ACCESS EXCLUSIVE on table "transactions" (held for 247s)

Recent Changes (from deploy log):
  03:38:00 - Database migration #447 applied: "ALTER TABLE transactions ADD COLUMN reconciled_at TIMESTAMP; CREATE INDEX idx_transactions_reconciled ON transactions(reconciled_at);"
  03:37:00 - Deployment: payment-service v2.3.1 (no code changes, dependency update only)

Service Dependencies:
  frontend -> api-gateway -> payment-service -> postgres-primary
  queue-worker -> postgres-primary

Connection Pool Status (pgbouncer):
  active: 200/200
  waiting: 147
  idle: 0
  longest_wait: 45s

=== METRICS SNAPSHOT AT 03:42 ===

postgres-primary:
  CPU: 98%
  IOPS: 15,000 (baseline: 2,000)
  Disk queue depth: 47
  Replication lag: 12s (baseline: <100ms)

payment-service pods:
  Restart count: 3 each in last 5 minutes
  Last log: "sqlalchemy.exc.OperationalError: could not connect to server: Connection refused"

queue-worker:
  Processing rate: 0 msg/sec (baseline: 2,400 msg/sec)
  Memory: stable at 256Mi
  CPU: 2% (baseline: 45%)
"""

PROMPT = f"""You are a senior SRE investigating a SEV-1 cascading failure.

Analyze this incident data and provide:
1. The root cause (not the symptoms)
2. The full causal chain (how one failure cascaded)
3. Immediate mitigation steps
4. Long-term prevention measures

Incident data:
{INCIDENT_DATA}
"""

print("=" * 65)
print("Extended Thinking: Cascading Failure Analysis")
print("=" * 65)
print("\nSending incident data to Claude with extended thinking enabled...")
print("(This may take 15-30 seconds as Claude reasons through the cascade)\n")

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    messages=[{"role": "user", "content": PROMPT}]
)

# Process the response blocks
print("=" * 65)
print("THINKING PROCESS (Internal Monologue)")
print("=" * 65)

for block in message.content:
    if block.type == "thinking":
        print(block.thinking)

print("\n")
print("=" * 65)
print("FINAL ANALYSIS (Response)")
print("=" * 65)

for block in message.content:
    if block.type == "text":
        print(block.text)

print("\n")
print("=" * 65)
print("TOKEN USAGE")
print("=" * 65)
print(f"Input tokens: {message.usage.input_tokens}")
print(f"Output tokens: {message.usage.output_tokens}")
```

Run it:

```bash
python thinking_analysis.py
```

---

## Understanding the Response Structure

When extended thinking is enabled, `message.content` contains multiple blocks:

```python
# The response contains a list of content blocks
for block in message.content:
    if block.type == "thinking":
        # This is Claude's internal reasoning — not shown to end users
        # in production, but invaluable for debugging and understanding
        print(f"Thinking: {block.thinking[:200]}...")
    elif block.type == "text":
        # This is the final, polished response
        print(f"Response: {block.text[:200]}...")
```

The thinking block always comes before the text block. Think of it as:
- **Thinking block** = the SRE's whiteboard during the incident (scratch work, hypotheses, eliminations)
- **Text block** = the incident summary posted to the team channel (clear, structured, actionable)

---

## Comparing: With and Without Thinking

To see the difference clearly, try the same prompt without thinking:

```python
# WITHOUT extended thinking
message_no_thinking = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    messages=[{"role": "user", "content": PROMPT}]
)

# WITH extended thinking
message_with_thinking = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    messages=[{"role": "user", "content": PROMPT}]
)
```

You will notice the thinking-enabled response typically:
- Correctly identifies the database migration as the root cause (not the symptoms)
- Traces the full cascade in the correct causal order (migration -> lock -> pool exhaustion -> service failures -> user impact)
- Distinguishes between the trigger and the contributing factors
- Provides more specific mitigation steps

---

## Budget Tokens: How Much Thinking Is Enough?

| Budget | Use Case | Analogy |
|--------|----------|---------|
| 1,024 | Simple triage with brief reasoning | Quick glance at the dashboard |
| 5,000 | Standard incident analysis | 10-minute investigation |
| 10,000 | Complex cascading failures | 30-minute deep dive |
| 32,000 | Architecture-level review | Full post-mortem analysis |

> **Rule of thumb:** Start with 10,000 for incident analysis. If the thinking output appears truncated or incomplete, increase the budget. If it is spending tokens on obvious steps, reduce it.

---

## What Success Looks Like

The **thinking block** shows step-by-step reasoning through the cascade:

```
Let me analyze this incident chronologically...

The alerts arrived in reverse order of causation. Let me reorder by actual trigger time:
1. 03:38:00 - Migration #447 applied (ALTER TABLE + CREATE INDEX on "transactions")
2. This takes an ACCESS EXCLUSIVE lock on the transactions table...
3. The transactions table is heavily used by payment-service...
4. With the lock held for 247s, all queries touching this table queue up...
5. Connection pool fills to 200/200 as queries cannot complete...
6. New connections are refused -> payment-service pods crash...
7. API gateway loses 3/4 backends -> latency spikes...
8. Frontend gets 504s from gateway -> user-facing errors...

The root cause is NOT the payment-service crash (symptom).
The root cause IS the unguarded DDL migration run against a production
table during active traffic hours.

The CREATE INDEX on a large table without CONCURRENTLY took an exclusive
lock that blocked all DML on the transactions table...
```

The **final response** presents a clear, structured analysis with the correct root cause and actionable remediation steps.

---

## Key Takeaway

Extended thinking reveals the AI's reasoning chain — invaluable for understanding complex incidents. When you need to trust the analysis (SEV-1 incidents, post-mortems, architecture decisions), enable thinking so you can verify the reasoning, not just the conclusion. It is the difference between an answer you accept on faith and an answer you can validate step by step.
