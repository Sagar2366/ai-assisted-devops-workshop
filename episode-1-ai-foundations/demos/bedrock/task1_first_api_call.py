#!/usr/bin/env python3
"""
Task 1: Your First API Call — AWS Bedrock
Same task, enterprise provider. No API key in code — uses IAM credentials.
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
    print("Task 1: Your First API Call — AWS Bedrock")
    print("=" * 65)

    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"
    )

    # Experiment 1: Basic API call
    print("\nExperiment 1: Basic API Call")
    print("-" * 65)

    response = bedrock.invoke_model(
        modelId="anthropic.claude-sonnet-4-6",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": "What is Kubernetes and why do DevOps engineers use it?"}
            ]
        })
    )

    result = json.loads(response["body"].read())
    print(result["content"][0]["text"])

    # Experiment 2: Token usage
    print("\n" + "-" * 65)
    print("Experiment 2: Token Usage")
    print("-" * 65)
    print(f"Input tokens:  {result['usage']['input_tokens']}")
    print(f"Output tokens: {result['usage']['output_tokens']}")

    print("\n" + "=" * 65)
    print("Key Learning: Same Claude model, different access path.")
    print("Direct API = simple. Bedrock = enterprise controls (IAM, logging).")
    print("=" * 65)

    print("\nTask 1 Complete!")
    print("Next: python3 demos/bedrock/task2_system_prompts.py")


if __name__ == "__main__":
    main()
