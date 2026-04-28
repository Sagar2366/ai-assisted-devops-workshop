#!/usr/bin/env python3
"""
Task 2: System Prompts — AWS Bedrock
Same system prompt experiment via Bedrock. Enterprise path, same concept.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  pip install boto3
  aws configure  (set up AWS credentials)
  Enable Claude model access in AWS Bedrock console
"""

import boto3
import json

def main():
    print("=" * 65)
    print("Task 2: System Prompts — AWS Bedrock")
    print("=" * 65)

    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"
    )

    alert = """Analyze this alert and give me a 3-step remediation plan:

ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)"""

    # Experiment 1: Without system prompt
    print("\nExperiment 1: No System Prompt (Generic)")
    print("-" * 65)

    response = bedrock.invoke_model(
        modelId="anthropic.claude-sonnet-4-6",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": alert}]
        })
    )
    result = json.loads(response["body"].read())
    print(result["content"][0]["text"])

    # Experiment 2: With SRE system prompt
    print("\n" + "=" * 65)
    print("Experiment 2: With SRE System Prompt")
    print("-" * 65)

    response = bedrock.invoke_model(
        modelId="anthropic.claude-sonnet-4-6",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "system": "You are a senior SRE with 10 years of Kubernetes experience. Be concise and actionable. Give kubectl commands, not general advice.",
            "messages": [{"role": "user", "content": alert}]
        })
    )
    result = json.loads(response["body"].read())
    print(result["content"][0]["text"])

    print("\n" + "=" * 65)
    print("Key Learning: System prompt works the same across all providers.")
    print("  Anthropic: system='...' parameter")
    print("  OpenAI:    {'role': 'system'} in messages")
    print("  Bedrock:   'system': '...' in JSON body")
    print("=" * 65)

    print("\nTask 2 Complete!")
    print("Next: python3 demos/bedrock/task3_persona_swap.py")


if __name__ == "__main__":
    main()
