#!/usr/bin/env python3
"""
Prompt Anti-Patterns and Fixes for DevOps

This demo illustrates common prompt engineering mistakes in DevOps/SRE contexts
and shows how to fix them. Each anti-pattern is demonstrated with a BAD prompt
(vague, lacking context, or unstructured) followed by a GOOD prompt (specific,
context-rich, and well-formatted). The contrast highlights how small changes in
prompt construction lead to dramatically better AI-assisted outcomes.

Prerequisites:
    - anthropic SDK: pip install anthropic
    - ANTHROPIC_API_KEY environment variable set
"""

import anthropic

client = anthropic.Anthropic()


def call_claude(prompt: str) -> str:
    """Send a prompt to Claude and return the response text."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def main():
    print("=" * 65)
    print("PROMPT ANTI-PATTERNS AND FIXES FOR DEVOPS")
    print("Learn what NOT to do - and how to fix it")
    print("=" * 65)

    # =========================================================
    # ANTI-PATTERN 1: Vague Ask vs Specific Ask
    # =========================================================
    print("\n")
    print("=" * 65)
    print("ANTI-PATTERN 1: Vague Ask vs Specific Ask")
    print("=" * 65)
    print()
    print("Problem: Vague prompts produce generic, unhelpful responses.")
    print("Fix: Include specific details - error messages, versions,")
    print("     namespaces, and observable symptoms.")
    print()

    print("-" * 65)
    print("BAD PROMPT:")
    print("-" * 65)
    bad_prompt_1 = "How do I fix my Kubernetes cluster?"
    print(f"\n  \"{bad_prompt_1}\"\n")
    print("Response:")
    print("-" * 65)
    bad_response_1 = call_claude(bad_prompt_1)
    print(bad_response_1)

    print()
    print("-" * 65)
    print("GOOD PROMPT:")
    print("-" * 65)
    good_prompt_1 = (
        "My Kubernetes cluster has 3 pods in CrashLoopBackOff state in the "
        "payments namespace. The pods are running image payments-api:v2.3.1 "
        "and the logs show 'connection refused' errors to the PostgreSQL "
        "service at postgres-primary:5432. What are the most likely causes "
        "and what kubectl commands should I run to diagnose this?"
    )
    print(f"\n  \"{good_prompt_1}\"\n")
    print("Response:")
    print("-" * 65)
    good_response_1 = call_claude(good_prompt_1)
    print(good_response_1)

    print()
    print("-" * 65)
    print("COMPARISON NOTE:")
    print("-" * 65)
    print("The BAD prompt returns generic Kubernetes troubleshooting advice.")
    print("The GOOD prompt returns targeted diagnosis steps for a specific")
    print("connectivity issue between payments pods and PostgreSQL, with")
    print("actionable kubectl commands tailored to the exact scenario.")
    print()

    # =========================================================
    # ANTI-PATTERN 2: No Context vs Rich Context
    # =========================================================
    print("\n")
    print("=" * 65)
    print("ANTI-PATTERN 2: No Context vs Rich Context")
    print("=" * 65)
    print()
    print("Problem: Without context, AI guesses your stack, requirements,")
    print("         and constraints - usually incorrectly.")
    print("Fix: Provide service details, SLOs, architecture info, and")
    print("     preferred output formats.")
    print()

    print("-" * 65)
    print("BAD PROMPT:")
    print("-" * 65)
    bad_prompt_2 = "Write a monitoring alert"
    print(f"\n  \"{bad_prompt_2}\"\n")
    print("Response:")
    print("-" * 65)
    bad_response_2 = call_claude(bad_prompt_2)
    print(bad_response_2)

    print()
    print("-" * 65)
    print("GOOD PROMPT:")
    print("-" * 65)
    good_prompt_2 = """Write a monitoring alert for our payment processing service with the following context:

Service: payment-gateway (runs in Kubernetes, 3 replicas)
SLOs:
  - Availability: 99.95% (error budget: 21.6 minutes/month)
  - Latency: p99 < 500ms for /api/v1/charge endpoint
  - Error rate: < 0.1% of total requests

Current architecture:
  - Service mesh: Istio (metrics available via istio_request_duration_milliseconds)
  - Metrics: Prometheus with 15s scrape interval
  - Alerting: Alertmanager with PagerDuty integration

Preferred format: PrometheusRule YAML (API version monitoring.coreos.com/v1)

Metrics to monitor:
  - Request latency (istio_request_duration_milliseconds_bucket)
  - Error rate (istio_requests_total with response_code=~"5..")
  - Pod restart count (kube_pod_container_status_restarts_total)

Include multi-window burn rate alerts for the error budget (1h/6h windows)."""
    print(f"\n  \"{good_prompt_2}\"\n")
    print("Response:")
    print("-" * 65)
    good_response_2 = call_claude(good_prompt_2)
    print(good_response_2)

    print()
    print("-" * 65)
    print("COMPARISON NOTE:")
    print("-" * 65)
    print("The BAD prompt produces a generic alert template that may not")
    print("match your monitoring stack or requirements at all.")
    print("The GOOD prompt produces a production-ready PrometheusRule with")
    print("burn-rate windows, correct metric names, proper labels, and")
    print("SLO-aligned thresholds - ready to apply to your cluster.")
    print()

    # =========================================================
    # ANTI-PATTERN 3: No Format vs Structured Output Format
    # =========================================================
    print("\n")
    print("=" * 65)
    print("ANTI-PATTERN 3: No Format vs Structured Output Format")
    print("=" * 65)
    print()
    print("Problem: Without specifying output structure, you get a wall of")
    print("         unorganized text that is hard to act on.")
    print("Fix: Define the exact output format with sections, fields, and")
    print("     structure you need.")
    print()

    incident_data = """Incident data:
- Alert fired at 03:42 UTC for high error rate on checkout service
- 5xx errors jumped from 0.02% to 34% in 2 minutes
- 2,847 customers affected during peak shopping hours
- Root cause: database connection pool exhausted after config change
- Config change deployed at 03:40 UTC by CI/CD pipeline
- Rollback initiated at 04:15 UTC, service restored at 04:18 UTC
- Total downtime: 36 minutes"""

    print("-" * 65)
    print("BAD PROMPT:")
    print("-" * 65)
    bad_prompt_3 = f"Analyze this incident\n\n{incident_data}"
    print(f"\n  \"Analyze this incident\\n\\n{incident_data}\"\n")
    print("Response:")
    print("-" * 65)
    bad_response_3 = call_claude(bad_prompt_3)
    print(bad_response_3)

    print()
    print("-" * 65)
    print("GOOD PROMPT:")
    print("-" * 65)
    good_prompt_3 = f"""Analyze the following incident and provide a structured post-incident report.

{incident_data}

Provide your analysis in EXACTLY this format:

## Summary
(2-3 sentence executive summary)

## Impact
- Severity: (P1/P2/P3/P4)
- Duration: (total minutes)
- Users affected: (number)
- Revenue impact: (estimated, if applicable)

## Timeline (UTC)
| Time | Event |
|------|-------|
(chronological table of events)

## Root Cause
(1 paragraph technical explanation)

## Action Items
| # | Action | Owner | Deadline | Priority |
|---|--------|-------|----------|----------|
(numbered list with specific owners and deadlines)

## Lessons Learned
- What went well:
- What went poorly:
- Where we got lucky:"""
    print(f"\n  \"{good_prompt_3}\"\n")
    print("Response:")
    print("-" * 65)
    good_response_3 = call_claude(good_prompt_3)
    print(good_response_3)

    print()
    print("-" * 65)
    print("COMPARISON NOTE:")
    print("-" * 65)
    print("The BAD prompt yields a free-form narrative that requires manual")
    print("restructuring before it can be shared with stakeholders.")
    print("The GOOD prompt produces a ready-to-share post-incident report")
    print("with clear sections, accountability (owners), and deadlines -")
    print("exactly what leadership and engineering teams need.")
    print()

    # =========================================================
    # COMPARISON SUMMARY TABLE
    # =========================================================
    print("\n")
    print("=" * 65)
    print("COMPARISON SUMMARY TABLE")
    print("=" * 65)
    print()
    print(f"{'Anti-Pattern':<20} {'BAD Approach':<22} {'GOOD Approach':<23}")
    print(f"{'-'*20} {'-'*22} {'-'*23}")
    print(f"{'1. Vague Ask':<20} {'Generic question':<22} {'Specific details +  ':<23}")
    print(f"{'':<20} {'no details':<22} {'error msgs + versions':<23}")
    print(f"{'2. No Context':<20} {'No stack/arch info':<22} {'SLOs + architecture +':<23}")
    print(f"{'':<20} {'guess my setup':<22} {'metrics + format':<23}")
    print(f"{'3. No Format':<20} {'Unstructured dump':<22} {'Explicit sections + ':<23}")
    print(f"{'':<20} {'wall of text':<22} {'tables + owners':<23}")
    print()
    print("-" * 65)
    print("Quality Impact:")
    print("-" * 65)
    print("  BAD prompts  -> Generic, inapplicable, requires rework")
    print("  GOOD prompts -> Specific, actionable, production-ready")
    print()

    # =========================================================
    # KEY LEARNING
    # =========================================================
    print("=" * 65)
    print("Key Learning:")
    print("=" * 65)
    print()
    print("Avoiding prompt anti-patterns is the fastest way to improve AI")
    print("output quality. Remember the three fixes:")
    print()
    print("  1. BE SPECIFIC: Replace vague asks with concrete details -")
    print("     include error messages, versions, namespaces, and symptoms.")
    print()
    print("  2. PROVIDE CONTEXT: Share your stack, SLOs, architecture,")
    print("     and constraints. The AI cannot read your environment.")
    print()
    print("  3. DEFINE FORMAT: Specify exactly what output structure you")
    print("     need - sections, tables, fields, owners, and deadlines.")
    print()
    print("Each fix takes seconds to apply but saves minutes (or hours)")
    print("of rework. Treat prompt writing like writing a good ticket -")
    print("the more context and structure you provide upfront, the better")
    print("the result you get back.")
    print()
    print("=" * 65)
    print("Next: You've completed the Prompt Engineering module!")
    print("=" * 65)


if __name__ == "__main__":
    main()
