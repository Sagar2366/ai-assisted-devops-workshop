#!/usr/bin/env python3
"""
Task 1: Model Tiers Comparison for SRE
=======================================
Compare Claude Haiku, Sonnet, and Opus analyzing the same
Kubernetes OOMKilled incident to understand tier differences.

Prerequisites:
- pip install anthropic
- export ANTHROPIC_API_KEY=your-key-here
"""

import anthropic
import time

client = anthropic.Anthropic()

# A realistic K8s OOMKilled scenario log
K8S_INCIDENT = """
$ kubectl describe pod payment-service-7d4f8b6c9-x2k4m -n production

Name:         payment-service-7d4f8b6c9-x2k4m
Namespace:    production
Priority:     0
Node:         worker-node-03/10.0.4.17
Start Time:   Mon, 14 Jul 2025 03:42:11 +0000
Labels:       app=payment-service
              pod-template-hash=7d4f8b6c9
              version=v2.3.1
Status:       Running
IP:           10.244.3.87
Controlled By: ReplicaSet/payment-service-7d4f8b6c9

Containers:
  payment-api:
    Container ID:   containerd://a8f3e2d1b9c74f6e8a2d1c3b5e7f9a0b
    Image:          registry.internal/payment-service:v2.3.1
    Port:           8080/TCP
    State:          Waiting
      Reason:       CrashLoopBackOff
    Last State:     Terminated
      Reason:       OOMKilled
      Exit Code:    137
      Started:      Mon, 14 Jul 2025 03:47:22 +0000
      Finished:     Mon, 14 Jul 2025 03:52:08 +0000
    Ready:          False
    Restart Count:  4
    Limits:
      cpu:     500m
      memory:  512Mi
    Requests:
      cpu:     250m
      memory:  256Mi
    Environment:
      JAVA_OPTS:        -Xmx384m -Xms256m
      DB_POOL_SIZE:     20
      CACHE_SIZE_MB:    128
      ENABLE_PROFILING: true
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access

Conditions:
  Type              Status
  Initialized       True
  Ready             False
  ContainersReady   False
  PodScheduled      True

Events:
  Type     Reason     Age                    From               Message
  ----     ------     ----                   ----               -------
  Normal   Scheduled  12m                    default-scheduler  Successfully assigned production/payment-service-7d4f8b6c9-x2k4m to worker-node-03
  Normal   Pulled     12m                    kubelet            Container image "registry.internal/payment-service:v2.3.1" already present on machine
  Normal   Created    12m                    kubelet            Created container payment-api
  Normal   Started    12m                    kubelet            Started container payment-api
  Warning  OOMKilling 7m                     kernel-monitor     Memory cgroup out of memory: Killed process 28491 (java) total-vm:1248632kB, anon-rss:524288kB
  Normal   Pulled     6m (x2 over 7m)       kubelet            Container image "registry.internal/payment-service:v2.3.1" already present on machine
  Warning  OOMKilling 4m                     kernel-monitor     Memory cgroup out of memory: Killed process 29103 (java) total-vm:1302400kB, anon-rss:524288kB
  Warning  BackOff    2m (x3 over 5m)       kubelet            Back-off restarting failed container

$ kubectl top pod payment-service-7d4f8b6c9-x2k4m -n production --containers
POD                                    NAME          CPU(cores)   MEMORY(bytes)
payment-service-7d4f8b6c9-x2k4m       payment-api   487m         509Mi

$ kubectl logs payment-service-7d4f8b6c9-x2k4m -n production --previous | tail -20
2025-07-14 03:51:42.118 WARN  [payment-api] c.p.s.cache.TransactionCache - Cache eviction rate exceeding threshold: 847 evictions/min
2025-07-14 03:51:43.201 WARN  [payment-api] c.p.s.db.ConnectionPool - Pool utilization at 95% (19/20 connections active)
2025-07-14 03:51:44.892 ERROR [payment-api] c.p.s.profiler.MemoryProfiler - Heap usage critical: 371MB/384MB (96.6%)
2025-07-14 03:51:45.003 WARN  [payment-api] c.p.s.cache.TransactionCache - Off-heap direct buffer allocation: 142MB
2025-07-14 03:51:47.441 ERROR [payment-api] java.lang.OutOfMemoryError: Direct buffer memory
2025-07-14 03:51:47.442 ERROR [payment-api] c.p.s.handler.PaymentHandler - Failed to process transaction txn-8847291
2025-07-14 03:52:07.998 INFO  [payment-api] c.p.s.Application - Received SIGKILL, shutting down...
"""

ANALYSIS_PROMPT = f"""Analyze this Kubernetes incident and provide:
1. Root cause
2. Immediate fix
3. Long-term prevention

Incident Data:
{K8S_INCIDENT}
"""


def analyze_with_model(model_name: str, model_id: str):
    """Run the same analysis with a specific model and measure performance."""
    print(f"\n{'─' * 65}")
    print(f"  Model: {model_name} ({model_id})")
    print(f"{'─' * 65}")

    start_time = time.time()
    message = client.messages.create(
        model=model_id,
        max_tokens=1024,
        messages=[{"role": "user", "content": ANALYSIS_PROMPT}]
    )
    elapsed = time.time() - start_time

    print(f"\n  Response Time: {elapsed:.2f}s")
    print(f"  Input Tokens:  {message.usage.input_tokens}")
    print(f"  Output Tokens: {message.usage.output_tokens}")
    print(f"\n  Analysis:")
    # Indent and display first 500 chars of the response
    analysis_text = message.content[0].text[:500]
    for line in analysis_text.split("\n"):
        print(f"  {line}")
    print("  ...")
    return elapsed, message.usage


def main():
    print("=" * 65)
    print("  TASK 1: MODEL TIERS COMPARISON FOR SRE")
    print("  Comparing Haiku vs Sonnet vs Opus on K8s OOMKilled Analysis")
    print("=" * 65)

    models = [
        ("Haiku 3.5", "claude-haiku-35-20241022"),
        ("Sonnet 4", "claude-sonnet-4-20250514"),
        ("Opus 4", "claude-opus-4-20250514"),
    ]

    results = []
    for name, model_id in models:
        elapsed, usage = analyze_with_model(name, model_id)
        results.append((name, elapsed, usage))

    # Summary comparison
    print(f"\n{'=' * 65}")
    print("  COMPARISON SUMMARY")
    print(f"{'=' * 65}")
    print(f"  {'Model':<12} {'Time (s)':<10} {'Input':<10} {'Output':<10}")
    print(f"  {'─' * 42}")
    for name, elapsed, usage in results:
        print(f"  {name:<12} {elapsed:<10.2f} {usage.input_tokens:<10} {usage.output_tokens:<10}")

    # Key Learning
    print(f"\n{'=' * 65}")
    print("  KEY LEARNING")
    print(f"{'=' * 65}")
    print("""
  - Haiku: Fastest, cheapest — use for alert triage and log classification
  - Sonnet: Best balance — use for incident analysis and runbook queries
  - Opus: Deepest reasoning — use for architecture reviews and post-mortems

  Match model tier to task complexity for optimal cost/quality tradeoff.
    """)
    print("  Next: task2_thinking_mode.py — Extended thinking for complex analysis")
    print(f"{'=' * 65}")


if __name__ == "__main__":
    main()
