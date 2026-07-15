# Lab 5: Streaming — Real-Time Incident Narration

## Mission

Stream AI responses for real-time incident updates. When every second counts during an outage, you should not wait for the full analysis to finish before you start acting.

---

## The Concept: kubectl logs -f vs kubectl logs

| Non-Streaming | Streaming |
|---|---|
| `kubectl logs pod-name` | `kubectl logs -f pod-name` |
| Wait for completion, get everything at once | See events as they happen in real time |
| 10-second wait, then full analysis dumps | Tokens arrive immediately, one by one |
| Blocks incident response | Team can start acting on partial info |

**The difference in practice:**
- **Non-streaming**: Your on-call SRE stares at a spinner for 15 seconds while Claude generates a full analysis. They cannot act until it finishes.
- **Streaming**: The first actionable sentence appears in under a second. By the time the full response completes, the SRE has already started remediation.

---

## Why Streaming Matters for SRE

1. **Long analyses should not block incident response.** A comprehensive root cause analysis might take 10-15 seconds to generate. Streaming lets responders see the first findings immediately.

2. **Team members can start acting on partial information.** If the first sentence is "The root cause is database connection pool exhaustion," the DBA can start investigating before the full remediation plan finishes generating.

3. **Better UX for incident dashboards.** Real-time streaming output on a shared incident channel gives the team confidence that the system is working, not hung.

4. **Timeout resilience.** If a network issue cuts the connection, you still have everything generated so far.

---

## Step 1: Basic Streaming with text_stream

The simplest way to stream — iterate over text chunks as they arrive.

```python
import anthropic

client = anthropic.Anthropic()

incident_data = """
INCIDENT: Payment processing failures
TIME: 2024-01-15 14:30-14:50 UTC
IMPACT: 100% of payment transactions failing
SERVICES AFFECTED: payment-service, order-service, api-gateway
SYMPTOMS:
- payment-service pods entering CrashLoopBackOff
- Database connection pool exhausted (50/50)
- Istio circuit breaker OPEN
- Order retry queue at 100% capacity
METRICS:
- Error rate: 0% → 100% over 5 minutes
- p99 latency: 200ms → timeout (10s)
- Pod restarts: 0 → 12 in 10 minutes
- DB active connections: 45 → 100 (max)
"""

print("=== Streaming Incident Analysis ===\n")

with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"""Given this incident data, provide a step-by-step remediation plan.
Start with the most urgent action first.

{incident_data}"""
    }]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print("\n\n=== Stream Complete ===")
```

---

## Step 2: Event-Based Streaming for More Control

When you need to track token usage, handle different event types, or build custom UIs.

```python
import anthropic

client = anthropic.Anthropic()

print("=== Event-Based Streaming ===\n")

with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"""Analyze this incident and provide:
1. Root cause (one sentence)
2. Immediate actions (bullet points)
3. Prevention measures for the future

{incident_data}"""
    }]
) as stream:
    for event in stream:
        if event.type == "content_block_delta":
            print(event.delta.text, end="", flush=True)

    # Get final message with full metadata
    final_message = stream.get_final_message()

    print(f"\n\n--- Stream Metadata ---")
    print(f"Tokens used: {final_message.usage.output_tokens}")
    print(f"Input tokens: {final_message.usage.input_tokens}")
    print(f"Stop reason: {final_message.stop_reason}")
    print(f"Model: {final_message.model}")
```

---

## Step 3: Build a Real-Time Incident Narrator

Combine streaming with a structured incident response workflow.

```python
import anthropic
import time
from datetime import datetime

client = anthropic.Anthropic()


def stream_incident_analysis(incident_context: str, question: str) -> dict:
    """Stream an incident analysis and return the complete result with metadata."""
    result = {
        "text": "",
        "tokens_used": 0,
        "time_to_first_token": None,
        "total_time": None,
    }

    start_time = time.time()
    first_token_received = False

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Analyzing: {question}")
    print("-" * 50)

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=[{
            "type": "text",
            "text": """You are an SRE incident response assistant. Provide concise, 
actionable analysis. Start with the most critical information first. 
Use bullet points for action items. Be direct — this is an active incident."""
        }],
        messages=[{
            "role": "user",
            "content": f"""Incident Context:
{incident_context}

Question: {question}"""
        }]
    ) as stream:
        for text in stream.text_stream:
            if not first_token_received:
                result["time_to_first_token"] = time.time() - start_time
                first_token_received = True
            print(text, end="", flush=True)
            result["text"] += text

        final_message = stream.get_final_message()
        result["tokens_used"] = final_message.usage.output_tokens
        result["total_time"] = time.time() - start_time

    print(f"\n\n[Time to first token: {result['time_to_first_token']:.2f}s | "
          f"Total: {result['total_time']:.2f}s | "
          f"Tokens: {result['tokens_used']}]")
    print("=" * 50)

    return result


# Simulate an incident response workflow
print("=" * 50)
print("  INCIDENT NARRATOR — Real-Time Analysis")
print("=" * 50)

# Phase 1: Initial assessment
stream_incident_analysis(
    incident_data,
    "What is the most likely root cause? Answer in one sentence."
)

# Phase 2: Immediate actions
stream_incident_analysis(
    incident_data,
    "What are the top 3 actions to take RIGHT NOW to restore service?"
)

# Phase 3: Blast radius
stream_incident_analysis(
    incident_data,
    "What is the blast radius? Which downstream services and customers are affected?"
)
```

---

## Step 4: Streaming with a Progress Indicator

For longer analyses, show progress to keep the team informed.

```python
import anthropic
import sys

client = anthropic.Anthropic()


def stream_with_progress(prompt: str, expected_sections: list[str]):
    """Stream response and highlight when key sections are reached."""
    current_text = ""
    sections_found = []

    print("\n[STREAMING] ", end="", flush=True)

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            current_text += text
            print(text, end="", flush=True)

            # Check if we have hit a new section
            for section in expected_sections:
                if section.lower() in current_text.lower() and section not in sections_found:
                    sections_found.append(section)
                    # Visual indicator that a section was found
                    sys.stderr.write(f"\n  >> Section found: {section}\n")
                    sys.stderr.flush()

        final_message = stream.get_final_message()

    print(f"\n\n[COMPLETE] {final_message.usage.output_tokens} tokens generated")
    print(f"[SECTIONS] Found {len(sections_found)}/{len(expected_sections)}: {sections_found}")


# Use it for a structured incident report
stream_with_progress(
    f"""Generate a structured incident report for:

{incident_data}

Include these sections: Summary, Root Cause, Impact, Timeline, Remediation, Prevention""",
    expected_sections=["Summary", "Root Cause", "Impact", "Timeline", "Remediation", "Prevention"]
)
```

---

## Step 5: Comparing Streaming vs Non-Streaming Performance

```python
import anthropic
import time

client = anthropic.Anthropic()

prompt_messages = [{
    "role": "user",
    "content": f"""Provide a detailed incident analysis with remediation steps for:

{incident_data}"""
}]

# Non-streaming: measure total wait time
print("=== Non-Streaming ===")
start = time.time()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=prompt_messages
)
non_stream_time = time.time() - start
print(f"Time to ANY output: {non_stream_time:.2f}s (user waits this long)")
print(f"Output tokens: {response.usage.output_tokens}")
print(f"First 100 chars: {response.content[0].text[:100]}...")

# Streaming: measure time to first token
print("\n=== Streaming ===")
start = time.time()
first_token_time = None

with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=prompt_messages
) as stream:
    for text in stream.text_stream:
        if first_token_time is None:
            first_token_time = time.time() - start
        # Consume the rest silently
        pass
    final = stream.get_final_message()

total_stream_time = time.time() - start
print(f"Time to FIRST token: {first_token_time:.2f}s (user sees output immediately)")
print(f"Time to completion: {total_stream_time:.2f}s")
print(f"Output tokens: {final.usage.output_tokens}")
print(f"\nImprovement: User sees output {non_stream_time - first_token_time:.2f}s sooner with streaming")
```

**Expected comparison:**

```
=== Non-Streaming ===
Time to ANY output: 8.34s (user waits this long)
Output tokens: 487

=== Streaming ===
Time to FIRST token: 0.52s (user sees output immediately)
Time to completion: 8.41s
Output tokens: 487

Improvement: User sees output 7.82s sooner with streaming
```

---

## What Success Looks Like

Text appears token by token in the terminal, like watching a live feed:

```
=== Streaming Incident Analysis ===

Based on the incident data, here is the immediate remediation plan:

**1. URGENT — Restore Database Connectivity (Do this NOW)**
- Increase max_connections on postgres-primary from 100 to 200
- Kill idle connections: SELECT pg_terminate_backend(pid) FROM pg_stat_activity
  WHERE state = 'idle' AND query_start < now() - interval '5 minutes'

**2. Recover Payment Service Pods**
- Delete CrashLoopBackOff pods: kubectl delete pods -l app=payment-service
  --field-selector=status.phase=Failed -n production
- Temporarily increase connection pool timeout to 15s to prevent cascading...

[Time to first token: 0.48s | Total: 6.21s | Tokens: 342]
```

The first actionable line ("Increase max_connections") appeared in under a second. An SRE reading this in real time could start the database fix while the rest of the plan is still generating.

---

## Key Takeaway

Streaming transforms AI from a batch tool into a real-time assistant — critical for incident response where every second counts. The total generation time is the same, but the perceived latency drops from seconds to milliseconds. For any SRE tooling that surfaces AI analysis to humans during incidents, streaming should be the default, not the exception.
