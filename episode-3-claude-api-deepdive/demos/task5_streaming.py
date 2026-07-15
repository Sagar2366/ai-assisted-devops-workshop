#!/usr/bin/env python3
"""
Task 5: Streaming — Real-Time Incident Analysis
=================================================
Stream Claude's incident analysis in real-time, demonstrating
how streaming enables faster incident response.

During a production incident, every second counts. Streaming lets your
team see Claude's first insights in under a second, instead of waiting
5-10 seconds for the full analysis to complete.

Prerequisites:
- pip install anthropic
- export ANTHROPIC_API_KEY=your-key-here
"""

import anthropic
import time

client = anthropic.Anthropic()

print("=" * 65)
print("  TASK 5: Streaming — Real-Time Incident Analysis")
print("=" * 65)
print()
print("  During incidents, waiting 5-10s for a full response feels like")
print("  an eternity. Streaming delivers the first tokens in <1 second.")
print()


# =============================================================================
# Incident Scenario
# =============================================================================

incident_prompt = """You are a senior SRE responding to a production incident. Here is the alert:

PRODUCTION ALERT — Severity: P1
Time: 2024-01-15 10:25:00 UTC
Duration: 5 minutes and escalating

Symptoms:
- Multiple services returning 5xx errors (error rate jumped from 0.1% to 34%)
- Load balancer health checks failing for 3/5 backend pods (payment-service)
- Database replica lag increasing: primary->replica-1 lag is 45s (normal: <1s)
- Connection pool exhaustion on payment-service: 50/50 connections in use
- Customer-facing impact confirmed: checkout flow failing for ~30% of users
- PagerDuty triggered for on-call SRE and database team

Recent Changes (last 2 hours):
- 09:30 UTC: payment-service deployed v2.14.3 (added new payment provider integration)
- 10:00 UTC: Scheduled database maintenance window started on replica-2 (routine vacuum)

Provide:
1. Immediate triage steps (first 60 seconds)
2. Root cause hypothesis based on the evidence
3. Remediation plan with rollback criteria
4. Communication template for stakeholders"""

print("-" * 65)
print("  Incident Scenario (P1 Production Outage)")
print("-" * 65)
print()
print("  Symptoms:")
print("  - 5xx error rate: 0.1% -> 34%")
print("  - 3/5 payment-service pods failing health checks")
print("  - Database replica lag: 45s (normal <1s)")
print("  - Connection pool exhausted: 50/50")
print("  - Customer checkout failing for ~30% of users")
print()


# =============================================================================
# Experiment 1: Non-Streaming (Traditional) Approach
# =============================================================================

print("=" * 65)
print("  Experiment 1: Non-Streaming (Traditional) Response")
print("=" * 65)
print()
print("  Sending request and waiting for complete response...")
print()

start_time = time.time()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": incident_prompt}],
)

total_time_non_streaming = time.time() - start_time

# Display the response
response_text = response.content[0].text
print(f"  Response received ({len(response_text)} chars):")
print(f"  {'~' * 60}")
# Show first 15 lines to keep output manageable
lines = response_text.split("\n")
for line in lines[:15]:
    print(f"  {line}")
if len(lines) > 15:
    print(f"  ... ({len(lines) - 15} more lines)")
print(f"  {'~' * 60}")
print()
print(f"  Time to first token: {total_time_non_streaming:.2f}s (same as total — you wait for everything)")
print(f"  Total time: {total_time_non_streaming:.2f}s")
print(f"  Output tokens: {response.usage.output_tokens}")
print()
print("  Problem: Your team stared at a blank screen for")
print(f"  {total_time_non_streaming:.1f} seconds during a P1 incident!")
print()


# =============================================================================
# Experiment 2: Streaming with text_stream
# =============================================================================

print("=" * 65)
print("  Experiment 2: Streaming Response (text_stream)")
print("=" * 65)
print()
print("  Streaming analysis as it generates:")
print()
print(f"{'─' * 65}")

start_time = time.time()
first_token_time = None
streamed_text = ""

with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": incident_prompt}],
) as stream:
    for text in stream.text_stream:
        if first_token_time is None:
            first_token_time = time.time()
        print(text, end="", flush=True)
        streamed_text += text

total_time_streaming = time.time() - start_time
ttft = first_token_time - start_time if first_token_time else total_time_streaming

print(f"\n{'─' * 65}")
print()
print(f"  Time to first token: {ttft:.2f}s")
print(f"  Total time: {total_time_streaming:.2f}s")
print(f"  Streamed chars: {len(streamed_text):,}")
print()
print(f"  Improvement: Team sees first insight in {ttft:.2f}s")
print(f"  instead of waiting {total_time_non_streaming:.2f}s!")
print()


# =============================================================================
# Experiment 3: Event-Based Streaming (Full Control)
# =============================================================================

print("=" * 65)
print("  Experiment 3: Event-Based Streaming (Advanced Control)")
print("=" * 65)
print()
print("  Tracking all stream events for observability:")
print()

# Shorter prompt for this experiment to keep output concise
triage_prompt = """Given a P1 incident with database connection pool exhaustion causing
payment-service pod failures: List the top 5 immediate actions in order of priority.
Be concise — one line per action."""

event_counts = {
    "message_start": 0,
    "content_block_start": 0,
    "content_block_delta": 0,
    "content_block_stop": 0,
    "message_delta": 0,
    "message_stop": 0,
}

start_time = time.time()
first_token_time = None

print(f"  {'~' * 60}")

with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=512,
    messages=[{"role": "user", "content": triage_prompt}],
) as stream:
    for event in stream:
        # Count event types
        if event.type in event_counts:
            event_counts[event.type] += 1

        # Print text deltas as they arrive
        if event.type == "content_block_delta":
            if hasattr(event.delta, "text"):
                if first_token_time is None:
                    first_token_time = time.time()
                print(event.delta.text, end="", flush=True)

    # Get the final message with full usage stats
    final_message = stream.get_final_message()

total_time_events = time.time() - start_time
ttft_events = first_token_time - start_time if first_token_time else total_time_events

print(f"\n  {'~' * 60}")
print()
print("  Stream Event Summary:")
print(f"  {'─' * 40}")
for event_type, count in event_counts.items():
    print(f"    {event_type:<25} {count:>4} events")
print(f"  {'─' * 40}")
print()
print(f"  Final Message Stats:")
print(f"    Model: {final_message.model}")
print(f"    Input tokens: {final_message.usage.input_tokens}")
print(f"    Output tokens: {final_message.usage.output_tokens}")
print(f"    Stop reason: {final_message.stop_reason}")
print(f"    Time to first token: {ttft_events:.2f}s")
print(f"    Total time: {total_time_events:.2f}s")
print()


# =============================================================================
# Summary Comparison
# =============================================================================

print("=" * 65)
print("  TIMING COMPARISON")
print("=" * 65)
print()
print(f"  {'Method':<25} {'Time to First Token':<22} {'Total Time':<15}")
print(f"  {'─' * 60}")
print(f"  {'Non-streaming':<25} {total_time_non_streaming:.2f}s{'':<17} {total_time_non_streaming:.2f}s")
print(f"  {'Streaming (text)':<25} {ttft:.2f}s{'':<17} {total_time_streaming:.2f}s")
print(f"  {'Streaming (events)':<25} {ttft_events:.2f}s{'':<17} {total_time_events:.2f}s")
print(f"  {'─' * 60}")
print()
if ttft > 0:
    improvement = ((total_time_non_streaming - ttft) / total_time_non_streaming) * 100
    print(f"  Perceived latency reduction: {improvement:.0f}%")
    print()


# =============================================================================
# Key Learning
# =============================================================================

print("=" * 65)
print("  KEY LEARNING")
print("=" * 65)
print("""
  Streaming reduces perceived latency dramatically — your team sees
  the first insight in <1s instead of waiting 5-10s for full analysis.

  When to use streaming in SRE workflows:

  1. INCIDENT RESPONSE: Stream triage steps so the on-call engineer
     can start acting on step 1 while steps 2-5 are still generating.

  2. LOG ANALYSIS: Stream findings as Claude processes large log files
     so patterns surface immediately.

  3. RUNBOOK GENERATION: Stream remediation steps during an outage —
     the first action appears in under a second.

  4. CHATOPS: In Slack/Teams bots, streaming shows "typing..." with
     real content appearing progressively (better UX).

  Implementation patterns:
  - text_stream: Simple iteration, best for most use cases
  - Event-based: Full control over message lifecycle, useful for
    building custom UIs or tracking usage in real-time

  Pro tip: Use stream.get_final_message() to access complete usage
  stats after streaming completes — essential for cost tracking.
""")
print("=" * 65)
print("  You've completed Episode 3! Next up:")
print("  Episode 4 — MCP Servers for Tool Integration")
print("=" * 65)
