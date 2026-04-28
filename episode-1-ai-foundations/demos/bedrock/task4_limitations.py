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

    questions = [
        ("Live cluster state", "Is my api-server pod in the production namespace healthy right now?"),
        ("Execute a command", "Run 'kubectl get pods -n production' and show me the output."),
        ("Hallucination trap", "What is the exact flag for graceful restart timeout in kubectl rollout restart?"),
    ]

    for label, question in questions:
        print(f"\n{'=' * 60}")
        print(f"TEST: {label}")
        print(f"QUESTION: {question}")
        print("=" * 60)

        response = bedrock.invoke_model(
            modelId="anthropic.claude-sonnet-4-6",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "system": system,
                "messages": [{"role": "user", "content": question}]
            })
        )

        result = json.loads(response["body"].read())
        print(result["content"][0]["text"])
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
