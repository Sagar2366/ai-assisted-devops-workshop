#!/usr/bin/env python3
"""
Task 4: Large Context Window — Analyzing Massive Log Files
============================================================
Feed a large synthetic log file into Claude's 200K context window
and demonstrate natural language log analysis.

Claude's 200K token context window can hold ~150,000 words — equivalent
to thousands of log lines. This lets you analyze entire incident timelines
without splitting, summarizing, or losing context.

Prerequisites:
- pip install anthropic
- export ANTHROPIC_API_KEY=your-key-here
"""

import anthropic
from datetime import datetime, timedelta
import random
import json

client = anthropic.Anthropic()

print("=" * 65)
print("  TASK 4: Large Context Window — Analyzing Massive Log Files")
print("=" * 65)
print()
print("  Claude's 200K context window can ingest thousands of log lines")
print("  and find patterns that would require complex grep/awk pipelines.")
print()


# =============================================================================
# Generate Synthetic Log Data
# =============================================================================

def generate_synthetic_logs(num_lines=200):
    """
    Generate realistic synthetic logs with a hidden incident pattern:
    - Normal traffic from 10:00 to 10:20
    - DB connection timeouts begin at 10:20
    - API errors cascade starting at 10:22
    - Pod restarts triggered at 10:25
    - Recovery begins at 10:30
    """
    logs = []
    base_time = datetime(2024, 1, 15, 10, 0, 0)

    services = ["order-service", "payment-service", "inventory-service", "user-service", "gateway"]
    endpoints = ["/api/orders", "/api/payments", "/api/inventory", "/api/users", "/api/health"]
    ips = ["192.168.1.100", "192.168.1.101", "192.168.1.102", "10.0.2.15", "10.0.2.16"]
    pods = {
        "payment-service": "payment-service-7d4f8b6c9-x2k4m",
        "order-service": "order-service-5b8d9a3f1-m7n2p",
        "inventory-service": "inventory-service-4c6e7d2a8-k9j3q",
        "user-service": "user-service-8f2a1b5c3-w4v6t",
        "gateway": "gateway-9e3d7c4b1-r8s5u",
    }

    def fmt_time(t):
        return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{random.randint(100,999)}Z"

    def normal_access_log(t):
        ip = random.choice(ips)
        endpoint = random.choice(endpoints)
        status = random.choices([200, 201, 304], weights=[70, 15, 15])[0]
        latency = random.randint(12, 95)
        return f'{fmt_time(t)} [INFO] nginx: {ip} - GET {endpoint} {status} {latency}ms'

    def normal_app_log(t):
        service = random.choice(services)
        messages = [
            f"Request processed successfully in {random.randint(10, 50)}ms",
            f"Cache hit for session {random.randint(1000, 9999)}",
            f"Health check passed — connections: {random.randint(5, 20)}/50",
            f"Metrics exported: latency_p99={random.randint(30, 80)}ms",
        ]
        return f'{fmt_time(t)} [INFO] {service}: {random.choice(messages)}'

    def structured_log(t, level, service, msg, extra=None):
        entry = {
            "timestamp": fmt_time(t),
            "level": level,
            "service": service,
            "message": msg,
        }
        if extra:
            entry.update(extra)
        return json.dumps(entry)

    # Phase 1: Normal traffic (10:00 - 10:19) ~80 lines
    for i in range(80):
        t = base_time + timedelta(seconds=random.randint(0, 1140))
        if random.random() < 0.6:
            logs.append(normal_access_log(t))
        else:
            logs.append(normal_app_log(t))

    # Phase 2: DB timeouts begin (10:20 - 10:22) ~40 lines
    incident_start = base_time + timedelta(minutes=20)
    for i in range(40):
        t = incident_start + timedelta(seconds=random.randint(0, 120))

        roll = random.random()
        if roll < 0.3:
            # DB timeout errors
            timeout_ms = random.choice([30000, 30000, 30000, 15000, 45000])
            logs.append(
                f'{fmt_time(t)} [ERROR] payment-service: Connection to postgres-primary:5432 timed out after {timeout_ms}ms'
            )
        elif roll < 0.45:
            # Connection pool warnings
            pool_active = random.randint(45, 50)
            logs.append(
                structured_log(t, "WARN", "payment-service",
                               f"Connection pool near exhaustion: {pool_active}/50 active",
                               {"pool_active": pool_active, "pool_max": 50})
            )
        elif roll < 0.55:
            # Retry warnings
            attempt = random.randint(1, 5)
            logs.append(
                f'{fmt_time(t)} [WARN] order-service: Retry attempt {attempt}/5 for payment processing'
            )
        else:
            # Normal traffic continues
            logs.append(normal_access_log(t))

    # Phase 3: API errors cascade (10:22 - 10:25) ~45 lines
    cascade_start = base_time + timedelta(minutes=22)
    for i in range(45):
        t = cascade_start + timedelta(seconds=random.randint(0, 180))

        roll = random.random()
        if roll < 0.25:
            # 5xx errors at nginx level
            ip = random.choice(ips)
            endpoint = random.choice(["/api/orders", "/api/payments"])
            logs.append(
                f'{fmt_time(t)} [ERROR] nginx: {ip} - POST {endpoint} 503 0ms upstream_timeout'
            )
        elif roll < 0.4:
            # Circuit breaker activation
            logs.append(
                structured_log(t, "ERROR", "order-service",
                               "Circuit breaker OPEN for payment-service — 10 consecutive failures",
                               {"circuit": "payment-service", "state": "OPEN", "failures": 10})
            )
        elif roll < 0.55:
            # Continued DB timeouts
            logs.append(
                f'{fmt_time(t)} [ERROR] payment-service: Connection to postgres-primary:5432 timed out after 30000ms'
            )
        elif roll < 0.65:
            # Health check failures
            logs.append(
                f'{fmt_time(t)} [WARN] kubelet: Liveness probe failed for {pods["payment-service"]}: connection refused'
            )
        else:
            # Degraded normal traffic
            ip = random.choice(ips)
            endpoint = random.choice(endpoints)
            latency = random.randint(200, 5000)
            status = random.choices([200, 503, 504], weights=[40, 35, 25])[0]
            logs.append(
                f'{fmt_time(t)} [{"INFO" if status == 200 else "ERROR"}] nginx: {ip} - GET {endpoint} {status} {latency}ms'
            )

    # Phase 4: Pod restarts (10:25 - 10:30) ~35 lines
    restart_start = base_time + timedelta(minutes=25)
    for i in range(35):
        t = restart_start + timedelta(seconds=random.randint(0, 300))

        roll = random.random()
        if roll < 0.2:
            # OOMKilled
            logs.append(
                f'{fmt_time(t)} [ERROR] kubelet: Pod {pods["payment-service"]} exceeded memory limit (512Mi), OOMKilled'
            )
        elif roll < 0.35:
            # Pod restart
            restart_count = random.randint(1, 4)
            logs.append(
                structured_log(t, "WARN", "kubelet",
                               f"Container restarted: {pods['payment-service']}",
                               {"restart_count": restart_count, "reason": "CrashLoopBackOff"})
            )
        elif roll < 0.45:
            # Kubernetes events
            logs.append(
                f'{fmt_time(t)} [INFO] kube-controller: Scaling payment-service from 3 to 5 replicas (CPU > 80%)'
            )
        elif roll < 0.55:
            # Gradual recovery
            logs.append(
                f'{fmt_time(t)} [INFO] payment-service: New connection established to postgres-replica-2:5432'
            )
        else:
            # Mixed traffic during recovery
            ip = random.choice(ips)
            endpoint = random.choice(endpoints)
            status = random.choices([200, 503], weights=[60, 40])[0]
            latency = random.randint(50, 2000)
            logs.append(
                f'{fmt_time(t)} [{"INFO" if status == 200 else "ERROR"}] nginx: {ip} - GET {endpoint} {status} {latency}ms'
            )

    # Sort all logs by timestamp for realism
    logs.sort()
    return logs


# =============================================================================
# Generate and display log summary
# =============================================================================

print("-" * 65)
print("  Generating Synthetic Log Data")
print("-" * 65)
print()

log_lines = generate_synthetic_logs(200)
log_content = "\n".join(log_lines)

print(f"  Generated {len(log_lines)} log lines")
print(f"  Log size: {len(log_content):,} characters")
print()
print("  Sample entries (first 5):")
for line in log_lines[:5]:
    print(f"    {line[:90]}...")
print()
print("  Sample entries (middle — incident zone):")
mid = len(log_lines) // 2
for line in log_lines[mid:mid+5]:
    print(f"    {line[:90]}...")
print()


# =============================================================================
# Analysis Questions
# =============================================================================

questions = [
    {
        "title": "Question 1: Error Detection & Timeline",
        "question": (
            "Analyze these logs and tell me: What errors occurred and when did they start? "
            "Provide a timeline of the first occurrence of each error type."
        ),
    },
    {
        "title": "Question 2: Incident Sequence Reconstruction",
        "question": (
            "What was the sequence of events leading to service degradation? "
            "Reconstruct the incident timeline from initial trigger to cascading failures. "
            "Identify the root cause and the blast radius."
        ),
    },
    {
        "title": "Question 3: Correlation Analysis",
        "question": (
            "Is there a correlation between database connection timeouts and the API errors? "
            "What evidence in the logs supports a causal relationship? "
            "What would you recommend checking first to resolve this incident?"
        ),
    },
]

system_prompt = (
    "You are a senior SRE analyzing production logs during an incident. "
    "Be precise about timestamps, identify patterns, and provide actionable insights. "
    "Keep responses focused and structured."
)

for i, q in enumerate(questions):
    print("=" * 65)
    print(f"  {q['title']}")
    print("=" * 65)
    print()

    prompt = f"""Here are the production logs from the last 2 hours:

```
{log_content}
```

{q['question']}"""

    # Count tokens before sending
    print("  Counting tokens...")
    token_count = client.messages.count_tokens(
        model="claude-sonnet-4-20250514",
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )
    print(f"  Input tokens: {token_count.input_tokens:,}")
    print()

    # Send to Claude
    print("  Sending to Claude for analysis...")
    print()

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    print(f"  Claude's Analysis:")
    print(f"  {'~' * 60}")
    # Indent the response for readability
    for line in response.content[0].text.split("\n"):
        print(f"  {line}")
    print(f"  {'~' * 60}")
    print()
    print(f"  Output tokens: {response.usage.output_tokens}")
    print(f"  Total tokens used: {token_count.input_tokens + response.usage.output_tokens:,}")
    print()


# =============================================================================
# Key Learning
# =============================================================================

print("=" * 65)
print("  KEY LEARNING")
print("=" * 65)
print("""
  The 200K context window lets you analyze entire incident timelines
  without splitting or summarizing. Key advantages:

  1. FULL CONTEXT: Claude sees all 200 log lines at once — no need to
     pre-filter with grep and risk missing related events.

  2. PATTERN RECOGNITION: Claude identifies correlations across the
     entire timeline (DB timeouts -> API errors -> pod restarts) that
     would require multiple grep passes to discover manually.

  3. NATURAL LANGUAGE QUERIES: Ask questions like "what caused the
     cascade?" instead of writing complex regex patterns.

  4. TOKEN COUNTING: Use count_tokens() to verify your input fits
     within context limits before sending (avoids wasted API calls).

  In production, you could feed Claude:
  - Full kubectl describe output for multiple pods
  - Combined logs from all microservices during an incident
  - Terraform plan output + state file for drift analysis
  - Multiple Prometheus alert definitions for correlation
""")
print("=" * 65)
print("  Next: task5_streaming.py — Real-time streaming responses")
print("=" * 65)
