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

    # Step 1: Create the Bedrock client (PRE-FILLED)
    # Key difference: no API key in code — uses AWS IAM credentials
    # Your security team will love this
    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"
    )

    print("Step 1 Complete: Bedrock client created (IAM auth)\n")

    # Experiment 1: Basic API call via Bedrock
    print("Experiment 1: Basic API Call")
    print("-" * 65)

    # TODO 1: Make your first Bedrock API call
    # Bedrock uses invoke_model() with a JSON body
    # The body format follows Anthropic's API since we're calling Claude via Bedrock
    response = bedrock.invoke_model(
        modelId=___,  # TODO: Use "anthropic.claude-sonnet-4-20250514-v1:0"
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": ___  # TODO: Use "What is Kubernetes and why do DevOps engineers use it?"
                }
            ]
        })
    )

    # TODO 2: Parse and print the response
    # Bedrock returns a streaming body — read it and parse JSON
    result = json.loads(response["body"].read())
    print(___)  # TODO: Use result["content"][0]["text"]

    # Experiment 2: Compare the authentication models
    print("\n" + "-" * 65)
    print("Experiment 2: Authentication Comparison")
    print("-" * 65)
    print("Anthropic: ANTHROPIC_API_KEY in environment → API key in header")
    print("OpenAI:    OPENAI_API_KEY in environment → API key in header")
    print("Bedrock:   aws configure → IAM role → no key in code")
    print("\nBedrock: every call is logged, IAM-controlled, compliance-ready.")

    print("\n" + "=" * 65)
    print("Key Learning: Same Claude model, different access path.")
    print("Direct API = simple. Bedrock = enterprise controls.")
    print("=" * 65)

    print("\nTask 1 Complete!")
    print("Next: python3 demos/bedrock/task2_system_prompts.py")


if __name__ == "__main__":
    main()
