#!/usr/bin/env python3
"""
Task 3: Persona Swap — Same Alert, Different Experts — AWS Bedrock
See how the system prompt changes the entire perspective.
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
    print("Task 3: Persona Swap — AWS Bedrock")
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

    # TODO 1: Define three personas with different system prompts
    # Each persona analyzes the same alert from a completely different angle
    # In Bedrock, system prompt is a top-level "system" field in the JSON body
    personas = [
        ("SRE Engineer", ___),  # TODO: Use "You are a senior SRE with 10 years of Kubernetes experience. Be concise and actionable."
        ("Security Engineer", ___),  # TODO: Use "You are a senior security engineer. Focus on security implications, access controls, and compliance. Be concise."
        ("Cost Analyst", ___),  # TODO: Use "You are a cloud cost analyst. Focus on resource optimization, waste reduction, and cost-effective solutions. Be concise."
    ]

    for name, system_prompt in personas:
        print("=" * 60)
        print(f"PERSONA: {name}")
        print("=" * 60)

        # TODO 2: Call Bedrock with each persona's system prompt
        response = bedrock.invoke_model(
            modelId="anthropic.claude-sonnet-4-20250514-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "system": ___,  # TODO: Use system_prompt
                "messages": [{"role": "user", "content": alert}]
            })
        )

        # TODO 3: Parse and print the response
        result = json.loads(response["body"].read())
        print(___)  # TODO: Use result["content"][0]["text"]
        print()

    print("=" * 65)
    print("Key Learning: Same alert, completely different responses.")
    print("The system prompt shapes the entire perspective.")
    print("In Bedrock, system prompt is a top-level JSON field, not a parameter.")
    print("=" * 65)

    print("\nTask 3 Complete!")
    print("Next: python3 demos/bedrock/task4_limitations.py")


if __name__ == "__main__":
    main()
