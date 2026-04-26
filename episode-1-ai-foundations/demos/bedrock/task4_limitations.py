#!/usr/bin/env python3
"""
Task 4: Where LLMs Break — Hallucination and Limitations — AWS Bedrock
Expose the fundamental limitations of LLMs by asking things they cannot do.
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
    print("Task 4: Where LLMs Break — AWS Bedrock")
    print("=" * 65)

    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"
    )

    system = "You are a senior SRE with 10 years of Kubernetes experience. Be concise and actionable."

    # TODO 1: Define three questions that expose LLM limitations
    # Question 1: Ask about LIVE cluster state (model has no access)
    # Question 2: Ask it to EXECUTE a command (model cannot run things)
    # Question 3: Ask about a specific flag (model may hallucinate)
    questions = [
        ("Live cluster state", ___),  # TODO: Use "Is my api-server pod in the production namespace healthy right now?"
        ("Execute a command", ___),  # TODO: Use "Run 'kubectl get pods -n production' and show me the output."
        ("Hallucination trap", ___),  # TODO: Use "What is the exact flag for graceful restart timeout in kubectl rollout restart?"
    ]

    for label, question in questions:
        print("=" * 60)
        print(f"TEST: {label}")
        print(f"QUESTION: {question}")
        print("=" * 60)

        # TODO 2: Call Bedrock with each question
        response = bedrock.invoke_model(
            modelId="anthropic.claude-sonnet-4-20250514-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "system": ___,  # TODO: Use system
                "messages": [{"role": "user", "content": ___}]  # TODO: Use question
            })
        )

        # TODO 3: Parse and print the response
        result = json.loads(response["body"].read())
        print(___)  # TODO: Use result["content"][0]["text"]
        print()

    print("=" * 65)
    print("Key Learnings:")
    print("- LLMs cannot access live systems (no cluster, no logs)")
    print("- LLMs cannot execute commands (can only suggest them)")
    print("- LLMs hallucinate — make up facts with full confidence")
    print("- NEVER run AI-generated commands without reading them first")
    print("- These limitations are why AGENTS exist (Episode 4)")
    print("=" * 65)

    print("\nTask 4 Complete!")
    print("Next: python3 demos/bedrock/task5_conversation_history.py")


if __name__ == "__main__":
    main()
