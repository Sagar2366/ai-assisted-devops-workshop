# Lab 4: Large Context Window — Grep on Steroids

## Mission

Analyze massive log files using the full 200K context window. Move beyond pattern matching into natural-language investigation of complex incidents.

---

## The Concept: Grep on Steroids

| grep | Claude 200K Context |
|---|---|
| Find lines matching a pattern | Understand entire log narratives |
| You need to know what to look for | Ask questions in natural language |
| One pattern at a time | Correlate multiple signals simultaneously |
| `grep -E "ERROR\|WARN" app.log` | "Find me the sequence of events that led to the outage" |

**The power shift:**
- **grep**: You are the detective. The tool finds evidence you already suspect exists.
- **Claude 200K**: The AI is the detective. You feed it everything, and it finds patterns you did not know to look for.

---

## Understanding the 200K Context Window

The 200K token context window translates to approximately:

- ~150,000 words
- ~500 pages of text
- ~10,000 lines of dense log output
- An entire day's worth of application logs from a moderately busy service

This means you can feed Claude an entire incident timeline — from the first warning sign to the resolution — and ask it to piece together the story.

---

## Step 1: Count Tokens Before Sending

Always count tokens first. You do not want to hit limits mid-analysis during an incident.

```python
import anthropic

client = anthropic.Anthropic()

# Load your log file
with open("/var/log/incident-2024-01-15.log", "r") as f:
    large_log_content = f.read()

# Count tokens before sending
token_count = client.messages.count_tokens(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": large_log_content}]
)
print(f"Input tokens: {token_count.input_tokens}")
print(f"Fits in context: {token_count.input_tokens < 200000}")
print(f"Context utilization: {token_count.input_tokens / 200000 * 100:.1f}%")
```

---

## Step 2: Generate Realistic Incident Logs

For this lab, we will generate a synthetic but realistic incident scenario — a cascading failure that starts with database connection pool exhaustion and leads to pod crashes.

```python
import anthropic
from datetime import datetime, timedelta
import random

client = anthropic.Anthropic()

# Simulate a realistic incident log: DB connection pool exhaustion → API errors → Pod crashes
def generate_incident_logs():
    """Generate a realistic cascading failure log sequence."""
    logs = []
    base_time = datetime(2024, 1, 15, 14, 30, 0)

    # Phase 1: Early warnings (14:30 - 14:35)
    warnings = [
        ("payment-service-7b4d9f8-x2k4q", "INFO", "Database connection pool: 45/50 active connections"),
        ("payment-service-7b4d9f8-x2k4q", "INFO", "Request latency p99: 245ms (threshold: 500ms)"),
        ("order-service-5c8a2e1-m9n3p", "INFO", "Healthcheck passed: upstream dependencies OK"),
        ("payment-service-7b4d9f8-x2k4q", "WARN", "Database connection pool: 48/50 active connections"),
        ("istio-proxy", "INFO", "upstream_cx_active: 48, upstream_cx_total: 12847"),
        ("payment-service-7b4d9f8-x2k4q", "WARN", "Slow query detected: SELECT * FROM transactions WHERE status='pending' took 1.2s"),
        ("payment-service-7b4d9f8-r7h2j", "WARN", "Database connection pool: 49/50 active connections"),
        ("hpa-controller", "INFO", "payment-service: current replicas=3, desired replicas=3, cpu=67%"),
        ("payment-service-7b4d9f8-x2k4q", "ERROR", "Database connection pool EXHAUSTED: 50/50 - new connections will block"),
        ("payment-service-7b4d9f8-r7h2j", "ERROR", "Database connection pool EXHAUSTED: 50/50 - new connections will block"),
    ]

    # Phase 2: Cascading failures (14:35 - 14:40)
    cascade = [
        ("payment-service-7b4d9f8-x2k4q", "ERROR", "Connection acquisition timeout after 5000ms - no available connections in pool"),
        ("order-service-5c8a2e1-m9n3p", "ERROR", "POST /api/v1/payments returned 503: upstream service unavailable"),
        ("istio-proxy", "WARN", "upstream_rq_503: 12 in last 30s, circuit breaker threshold: 50"),
        ("payment-service-7b4d9f8-x2k4q", "ERROR", "java.sql.SQLException: Cannot acquire connection from pool - timeout expired"),
        ("payment-service-7b4d9f8-r7h2j", "ERROR", "java.sql.SQLException: Cannot acquire connection from pool - timeout expired"),
        ("api-gateway-6d3f1a9-k4p2w", "ERROR", "502 Bad Gateway: payment-service.production.svc.cluster.local:8080"),
        ("order-service-5c8a2e1-m9n3p", "ERROR", "Failed to process order ORD-89234: payment service timeout after 10s"),
        ("order-service-5c8a2e1-m9n3p", "ERROR", "Failed to process order ORD-89235: payment service timeout after 10s"),
        ("istio-proxy", "ERROR", "upstream_rq_503: 47 in last 30s, circuit breaker threshold: 50"),
        ("payment-service-7b4d9f8-x2k4q", "ERROR", "Liveness probe failed: HTTP probe failed with statuscode: 503"),
        ("order-service-5c8a2e1-m9n3p", "WARN", "Retry queue depth: 156 messages (threshold: 200)"),
        ("istio-proxy", "ERROR", "Circuit breaker OPEN for payment-service.production.svc.cluster.local:8080"),
        ("api-gateway-6d3f1a9-k4p2w", "ERROR", "503 Service Unavailable: circuit breaker open for payment-service"),
        ("hpa-controller", "INFO", "payment-service: current replicas=3, desired replicas=5, cpu=94%"),
        ("payment-service-7b4d9f8-x2k4q", "ERROR", "Liveness probe failed: HTTP probe failed with statuscode: 503"),
        ("order-service-5c8a2e1-m9n3p", "ERROR", "Retry queue depth: 198 messages (threshold: 200)"),
    ]

    # Phase 3: Pod crashes and recovery attempts (14:40 - 14:50)
    crashes = [
        ("kubelet", "WARN", "Pod payment-service-7b4d9f8-x2k4q failed liveness probe 3 times consecutively"),
        ("kubelet", "ERROR", "Killing container payment-service in pod payment-service-7b4d9f8-x2k4q: liveness probe failed"),
        ("kube-scheduler", "INFO", "Successfully assigned production/payment-service-7b4d9f8-x2k4q to node-pool-3-abc12"),
        ("payment-service-7b4d9f8-x2k4q", "INFO", "Container starting: initializing connection pool..."),
        ("payment-service-7b4d9f8-x2k4q", "ERROR", "Failed to initialize: cannot connect to postgres-primary.production.svc:5432 - connection refused"),
        ("kubelet", "ERROR", "Container payment-service in pod payment-service-7b4d9f8-x2k4q exited with code 1"),
        ("kubelet", "WARN", "Back-off restarting failed container payment-service in pod payment-service-7b4d9f8-x2k4q"),
        ("payment-service-7b4d9f8-r7h2j", "ERROR", "OutOfMemoryError: Java heap space - connection wait threads exhausted heap"),
        ("kubelet", "ERROR", "Pod payment-service-7b4d9f8-r7h2j OOMKilled: memory limit 512Mi exceeded"),
        ("order-service-5c8a2e1-m9n3p", "ERROR", "Retry queue FULL: 200/200 messages - dropping new retry requests"),
        ("alertmanager", "CRITICAL", "FIRING: PaymentServiceDown - 0/3 pods ready for >5 minutes"),
        ("alertmanager", "CRITICAL", "FIRING: OrderProcessingBacklog - retry queue at 100% capacity"),
        ("postgres-primary-0", "WARN", "max_connections (100) reached - rejecting new connections"),
        ("postgres-primary-0", "ERROR", "FATAL: too many connections for role 'payment_svc_user'"),
        ("hpa-controller", "WARN", "payment-service: unable to scale - 2/5 pods in CrashLoopBackOff"),
        ("payment-service-7b4d9f8-x2k4q", "ERROR", "CrashLoopBackOff: back-off 2m40s restarting failed container"),
        ("kube-state-metrics", "INFO", "payment-service deployment: 1/5 replicas available, 2 unavailable, 2 crashloopbackoff"),
        ("pagerduty-webhook", "INFO", "Incident INC-4521 created: PaymentServiceDown - paging on-call SRE"),
        ("order-service-5c8a2e1-m9n3p", "WARN", "Enabling graceful degradation: queuing orders for async processing"),
        ("postgres-primary-0", "INFO", "Active connections: 100/100 (payment_svc_user: 62, order_svc_user: 23, analytics: 15)"),
    ]

    # Assemble with timestamps
    offset = 0
    for phase_logs in [warnings, cascade, crashes]:
        for pod, level, msg in phase_logs:
            ts = base_time + timedelta(seconds=offset)
            logs.append(f"{ts.isoformat()}Z [{level:8s}] [{pod}] {msg}")
            offset += random.randint(5, 45)

    return "\n".join(logs)

incident_logs = generate_incident_logs()
print(f"Generated {len(incident_logs.splitlines())} log lines")
print(f"Log size: {len(incident_logs)} characters")
```

---

## Step 3: Feed Logs to Claude and Investigate

Structure your prompt with logs first, questions last. This leverages the model's attention pattern — it pays strongest attention to the beginning and end of the context.

```python
# Best practice: Logs first, questions last
def analyze_incident(logs: str, question: str) -> str:
    """Send logs to Claude and ask an analytical question."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Here are the production incident logs from today's outage:

<logs>
{logs}
</logs>

Based on these logs, please answer the following question:

{question}"""
        }]
    )
    return message.content[0].text

# Investigation 1: Timeline of errors
print("=" * 60)
print("INVESTIGATION 1: Error Timeline")
print("=" * 60)
result = analyze_incident(
    incident_logs,
    "What errors occurred and in what order? Provide a timeline."
)
print(result)

# Investigation 2: Root cause analysis
print("\n" + "=" * 60)
print("INVESTIGATION 2: Root Cause Sequence")
print("=" * 60)
result = analyze_incident(
    incident_logs,
    "What was the sequence of events leading to the pod crashes? Identify the root cause."
)
print(result)

# Investigation 3: Correlation analysis
print("\n" + "=" * 60)
print("INVESTIGATION 3: Correlation Patterns")
print("=" * 60)
result = analyze_incident(
    incident_logs,
    "Are there any correlation patterns between the API errors and DB connection issues? What is the causal chain?"
)
print(result)
```

---

## Step 4: Advanced — Multi-Source Log Analysis

In real incidents, you often need to correlate logs from multiple sources.

```python
# Combine logs from multiple sources with clear delimiters
def multi_source_analysis(log_sources: dict, question: str) -> str:
    """Analyze logs from multiple sources simultaneously."""
    combined = ""
    for source_name, source_logs in log_sources.items():
        combined += f"\n<logs source=\"{source_name}\">\n{source_logs}\n</logs>\n"

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""I have logs from multiple sources during a production incident:

{combined}

Question: {question}

Please correlate events across all sources in your analysis."""
        }]
    )
    return message.content[0].text

# Example: correlate application logs with infrastructure metrics
log_sources = {
    "application": incident_logs,
    "postgres": """2024-01-15T14:32:00Z [WARN] connection pool utilization at 90%
2024-01-15T14:35:12Z [ERROR] max_connections reached (100/100)
2024-01-15T14:35:45Z [ERROR] FATAL: remaining connection slots reserved for superuser
2024-01-15T14:38:00Z [INFO] longest running query: 47s (SELECT * FROM transactions WHERE...)
2024-01-15T14:40:00Z [WARN] checkpoint taking too long: 12s (target: 5s)""",
    "kubernetes-events": """14:40:01 Warning  Unhealthy   pod/payment-service-7b4d9f8-x2k4q  Liveness probe failed
14:40:31 Normal   Killing     pod/payment-service-7b4d9f8-x2k4q  Stopping container
14:40:35 Normal   Scheduled   pod/payment-service-7b4d9f8-x2k4q  Assigned to node-pool-3
14:41:02 Warning  BackOff     pod/payment-service-7b4d9f8-x2k4q  Back-off restarting
14:42:15 Warning  OOMKilled   pod/payment-service-7b4d9f8-r7h2j  Memory limit exceeded"""
}

result = multi_source_analysis(
    log_sources,
    "Correlate the database connection issues with the pod crashes. What's the full causal chain from initial symptom to service outage?"
)
print(result)
```

---

## Tips for Working with Large Contexts

### 1. Put logs first, questions last (recency bias)

```python
# GOOD: Logs at the top, question at the bottom
content = f"""<logs>\n{logs}\n</logs>\n\nQuestion: {question}"""

# BAD: Question buried in the middle of context
content = f"""Question: {question}\n\n<logs>\n{logs}\n</logs>"""
```

### 2. Use clear delimiters around log sections

XML-style tags help Claude distinguish between log content and your instructions:

```python
content = f"""
<application_logs>
{app_logs}
</application_logs>

<infrastructure_metrics>
{metrics}
</infrastructure_metrics>

<kubernetes_events>
{k8s_events}
</kubernetes_events>

Based on ALL the above sources, what caused the outage?
"""
```

### 3. Ask specific questions rather than "analyze everything"

```python
# GOOD: Specific, actionable questions
questions = [
    "What was the first error that appeared, and which service generated it?",
    "How many seconds elapsed between the first warning and the first pod crash?",
    "Which services were affected, and in what order did they fail?",
    "What is the root cause, and what would have prevented this cascade?",
]

# BAD: Vague, open-ended
bad_question = "Analyze these logs and tell me everything interesting."
```

### 4. Token budget awareness

```python
# Check if logs fit before sending
token_count = client.messages.count_tokens(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": full_prompt}]
)

if token_count.input_tokens > 180000:  # Leave room for output
    print(f"WARNING: {token_count.input_tokens} tokens is close to the 200K limit")
    print("Consider splitting into time windows or filtering by severity")
```

---

## What Success Looks Like

Claude identifies patterns across hundreds of log lines that would take manual grep multiple passes:

```
INVESTIGATION 2: Root Cause Sequence

The pod crashes followed this causal chain:

1. [14:30:00] Database connection pool reached 48/50 (warning sign)
2. [14:31:30] Slow query detected (1.2s) - likely holding connections open
3. [14:32:45] Connection pool EXHAUSTED at 50/50 on both pods
4. [14:34:00] Requests start timing out waiting for connections (5s timeout)
5. [14:35:30] Upstream 503 errors trigger Istio circuit breaker (47/50 threshold)
6. [14:37:00] Circuit breaker OPENS - all traffic to payment-service rejected
7. [14:38:15] Liveness probes fail (service returning 503)
8. [14:40:01] Kubelet kills pod after 3 consecutive failed probes
9. [14:40:35] Restarted pod cannot connect to DB (max_connections already at 100)
10. [14:41:02] Pod enters CrashLoopBackOff

ROOT CAUSE: A slow query held database connections open, exhausting the pool.
The 50-connection limit was too low for the traffic volume, and there was no
circuit breaker between the application and the database connection pool.
```

With grep alone, you would need:
- `grep "EXHAUSTED" logs` to find pool exhaustion
- `grep "Liveness" logs` to find probe failures
- `grep "OOMKilled" logs` to find memory issues
- Manual correlation of timestamps across all results
- Domain knowledge to understand the causal relationships

Claude does all of this in a single pass.

---

## Key Takeaway

The 200K context window lets you analyze entire incident timelines in one shot — no more piecing together grep results. Feed it everything, ask specific questions, and let the model correlate signals across hundreds of log lines that would take a human investigator much longer to piece together manually.
