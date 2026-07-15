#!/usr/bin/env python3
"""
Task 4: AI Script Explainer
Explain complex shell one-liners and pipelines step by step.
AI-Assisted DevOps Workshop | Episode 9 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic


def main():
    print("=" * 65)
    print("Task 4: AI Script Explainer")
    print("Complex Pipelines → Clear Explanations")
    print("=" * 65)

    client = anthropic.Anthropic()

    system_prompt = """You are a shell command explainer for SRE teams.

When given a command or script, explain it in this EXACT format:

## Summary
One sentence: what this command accomplishes overall.

## Step-by-Step Breakdown
For each pipe stage or significant operation:
- **Command**: the exact piece
- **What it does**: plain English explanation
- **Input**: what it receives
- **Output**: what it produces
- **Key flags**: explain non-obvious flags

## Data Flow
Show how data transforms through the pipeline:
input → stage1 (what happens) → stage2 (what happens) → final output

## Failure Points
What can go wrong at each stage and what the symptom would be.

## Simpler Alternative
If a clearer way exists to achieve the same result, show it.

Write for a mid-level engineer — explain jargon, don't assume deep shell expertise."""

    # Experiment 1: Complex K8s pipeline
    print("\nExperiment 1: CrashLoopBackOff Pod Log Extractor")
    print("-" * 65)

    command1 = """kubectl get pods -A -o json | jq -r '.items[] | select(.status.containerStatuses[]?.state.waiting.reason == "CrashLoopBackOff") | "\\(.metadata.namespace)/\\(.metadata.name)"' | xargs -I{} sh -c 'ns=$(echo {} | cut -d/ -f1); pod=$(echo {} | cut -d/ -f2); kubectl logs $pod -n $ns --tail=50 --previous 2>/dev/null || echo "No previous logs for {}"'"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Explain this command:\n\n```bash\n{command1}\n```"}
        ]
    )
    print(message.content[0].text)

    # Experiment 2: Network debugging one-liner
    print("\n" + "-" * 65)
    print("Experiment 2: Network Connection Analyzer")
    print("-" * 65)

    command2 = """ss -tnp | awk 'NR>1 {split($5,a,":"); print a[1]}' | sort | uniq -c | sort -rn | head -20 | while read count ip; do echo "$count connections from $ip ($(dig +short -x $ip 2>/dev/null || echo 'no PTR'))"; done"""

    message2 = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Explain this command:\n\n```bash\n{command2}\n```"}
        ]
    )
    print(message2.content[0].text)

    # Experiment 3: Awk-heavy log parser
    print("\n" + "-" * 65)
    print("Experiment 3: Log Latency Percentile Calculator")
    print("-" * 65)

    command3 = """awk '/request_duration/{gsub(/.*duration=/, ""); gsub(/ms.*/, ""); durations[NR]=$0+0} END{n=asort(durations); printf "p50=%.1fms p95=%.1fms p99=%.1fms max=%.1fms n=%d\\n", durations[int(n*0.5)], durations[int(n*0.95)], durations[int(n*0.99)], durations[n], n}' /var/log/nginx/access.log"""

    message3 = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Explain this command:\n\n```bash\n{command3}\n```"}
        ]
    )
    print(message3.content[0].text)

    print("\n" + "=" * 65)
    print("Key Learning: AI explanation turns tribal knowledge into shared")
    print("understanding. Complex one-liners that only one person understands")
    print("become documented, explainable operations. Understand first, modify second.")
    print("=" * 65)

    print("\nTask 4 Complete!")
    print("Next: python3 demos/task5_script_optimizer.py")


if __name__ == "__main__":
    main()
