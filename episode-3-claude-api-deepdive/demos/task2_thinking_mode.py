#!/usr/bin/env python3
"""
Task 2: Extended Thinking for Cascading Failure Analysis
=========================================================
Use Claude's extended thinking capability to analyze a complex
multi-service cascading failure that requires deep reasoning.

Prerequisites:
- pip install anthropic
- export ANTHROPIC_API_KEY=your-key-here
"""

import anthropic
import time

client = anthropic.Anthropic()

# A complex multi-service cascading failure scenario
CASCADING_FAILURE = """
=== INCIDENT REPORT: Multi-Service Cascading Failure ===
Timestamp: 2025-07-14 02:15:00 UTC
Duration: 47 minutes
Severity: P1 — Customer-facing payment processing down

--- TIMELINE ---
02:15 - PagerDuty alert: PostgreSQL connection pool exhausted (primary DB)
02:17 - Payment API error rate spikes from 0.1% to 45%
02:19 - Order Service p99 latency: 340ms → 30,200ms
02:21 - Frontend 504 Gateway Timeout errors reported by customers
02:23 - RabbitMQ queue depth: order-processing queue backing up (0 → 84,000 msgs)
02:25 - Kubernetes HPA scaling Order Service replicas: 3 → 12 (making it worse)

--- METRICS SNAPSHOT (02:25 UTC) ---
PostgreSQL (primary):
  - Active connections: 200/200 (max_connections reached)
  - CPU utilization: 95%
  - Replication lag: 12 seconds
  - Slow queries: 47 queries > 5s (normally 0)
  - Lock waits: 23 transactions waiting on advisory locks
  - Bloat: payments table 340% bloated (last VACUUM: 6 days ago)

Payment API (4 replicas):
  - HTTP 503 rate: 45%
  - Connection pool wait time: 28s (timeout at 30s)
  - Active DB connections per pod: 50 (pool max: 50)
  - Heap memory: 89% utilized
  - Thread pool: 200/200 threads blocked on DB connection acquire

Order Service (scaled to 12 replicas by HPA):
  - HTTP timeout rate: 67%
  - Circuit breaker to Payment API: OPEN
  - Retry storms: ~3,400 retries/sec to Payment API
  - Each new replica opening 50 DB connections (adding load)

Frontend (Nginx Ingress):
  - 504 Gateway Timeout: 34% of requests
  - Active connections: 12,847 (normally ~2,000)
  - Upstream response time: 31s average

RabbitMQ:
  - order-processing queue: 84,000 messages (growing ~2,000/sec)
  - Consumer count: 0 (all consumers crashed/timed out)
  - Memory usage: 78% of high watermark
  - Disk free alarm: approaching threshold

--- RECENT CHANGES (last 24h) ---
- 01:30 UTC: Deployed payment-service v2.3.1 (added transaction profiling)
- 23:00 UTC (previous day): Marketing campaign launched (30% traffic increase)
- 20:00 UTC (previous day): Disabled scheduled VACUUM on payments table (ticket OPS-4421: "VACUUM causing latency spikes during peak hours")

--- CONFIGURATION ---
PostgreSQL max_connections: 200
Payment API pool size per pod: 50 (4 pods = 200 total, matching DB max)
Order Service timeout to Payment API: 30s
Order Service retry policy: 3 retries with exponential backoff (base 2s)
HPA scaling metric: CPU > 70% (scales up aggressively)
Circuit breaker: opens after 10 consecutive failures, half-open after 60s
"""

ANALYSIS_PROMPT = f"""You are a senior SRE investigating a cascading failure. Analyze this incident thoroughly:

1. Identify the root cause chain (what triggered what)
2. Explain why the HPA autoscaling made things worse
3. Identify the 3 key mistakes in the system configuration
4. Provide the exact sequence of commands to mitigate RIGHT NOW
5. Design preventive measures to avoid recurrence

Incident Data:
{CASCADING_FAILURE}
"""


def analyze_with_thinking():
    """Run analysis with extended thinking enabled."""
    print(f"\n{'─' * 65}")
    print("  EXPERIMENT 1: Analysis WITH Extended Thinking")
    print(f"{'─' * 65}")

    start_time = time.time()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=16000,
        thinking={
            "type": "enabled",
            "budget_tokens": 10000
        },
        messages=[{"role": "user", "content": ANALYSIS_PROMPT}]
    )
    elapsed = time.time() - start_time

    print(f"\n  Response Time: {elapsed:.2f}s")
    print(f"  Input Tokens:  {message.usage.input_tokens}")
    print(f"  Output Tokens: {message.usage.output_tokens}")

    # Separate thinking from response
    thinking_text = ""
    response_text = ""

    for block in message.content:
        if block.type == "thinking":
            thinking_text = block.thinking
        elif block.type == "text":
            response_text = block.text

    # Display thinking process (truncated)
    print(f"\n  {'─' * 55}")
    print("  THINKING PROCESS (first 800 chars):")
    print(f"  {'─' * 55}")
    for line in thinking_text[:800].split("\n"):
        print(f"    {line}")
    print("    ...")
    print(f"\n  Total thinking length: {len(thinking_text)} characters")

    # Display response (truncated)
    print(f"\n  {'─' * 55}")
    print("  FINAL RESPONSE (first 1000 chars):")
    print(f"  {'─' * 55}")
    for line in response_text[:1000].split("\n"):
        print(f"    {line}")
    print("    ...")

    return elapsed, thinking_text, response_text


def analyze_without_thinking():
    """Run the same analysis without extended thinking for comparison."""
    print(f"\n{'─' * 65}")
    print("  EXPERIMENT 2: Analysis WITHOUT Extended Thinking")
    print(f"{'─' * 65}")

    start_time = time.time()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": ANALYSIS_PROMPT}]
    )
    elapsed = time.time() - start_time

    print(f"\n  Response Time: {elapsed:.2f}s")
    print(f"  Input Tokens:  {message.usage.input_tokens}")
    print(f"  Output Tokens: {message.usage.output_tokens}")

    response_text = message.content[0].text

    # Display response (truncated)
    print(f"\n  {'─' * 55}")
    print("  RESPONSE (first 1000 chars):")
    print(f"  {'─' * 55}")
    for line in response_text[:1000].split("\n"):
        print(f"    {line}")
    print("    ...")

    return elapsed, response_text


def main():
    print("=" * 65)
    print("  TASK 2: EXTENDED THINKING FOR CASCADING FAILURE ANALYSIS")
    print("  Using thinking mode to deeply analyze a multi-service outage")
    print("=" * 65)

    print("\n  Scenario: Multi-service cascading failure involving:")
    print("    - PostgreSQL connection pool exhausted")
    print("    - Payment API returning 503s")
    print("    - Order Service timing out")
    print("    - Frontend showing 504 Gateway Timeouts")
    print("    - RabbitMQ queue backing up")
    print("    - HPA autoscaling making things worse")

    # Run with thinking
    thinking_time, thinking_text, thinking_response = analyze_with_thinking()

    # Run without thinking
    no_thinking_time, no_thinking_response = analyze_without_thinking()

    # Comparison
    print(f"\n{'=' * 65}")
    print("  COMPARISON: Thinking vs Non-Thinking")
    print(f"{'=' * 65}")
    print(f"\n  {'Metric':<30} {'With Thinking':<18} {'Without':<18}")
    print(f"  {'─' * 60}")
    print(f"  {'Response Time':<30} {thinking_time:<18.2f} {no_thinking_time:<18.2f}")
    print(f"  {'Response Length (chars)':<30} {len(thinking_response):<18} {len(no_thinking_response):<18}")
    print(f"  {'Thinking Length (chars)':<30} {len(thinking_text):<18} {'N/A':<18}")

    # Key Learning
    print(f"\n{'=' * 65}")
    print("  KEY LEARNING")
    print(f"{'=' * 65}")
    print("""
  Extended thinking is ideal for:
  - Complex root cause analysis with multiple interacting systems
  - Scenarios requiring causal chain reasoning (A caused B caused C)
  - Architecture-level decisions with many tradeoffs
  - Post-incident reviews needing thorough analysis

  When NOT to use extended thinking:
  - Simple alert triage (use Haiku instead)
  - Log classification or pattern matching
  - Single-system troubleshooting with obvious symptoms

  The thinking block shows Claude's reasoning process — useful for
  understanding HOW it reached its conclusions, not just WHAT they are.
    """)
    print("  Next: task3_prompt_caching.py — Caching SRE runbooks for fast queries")
    print(f"{'=' * 65}")


if __name__ == "__main__":
    main()
