#!/usr/bin/env python3
"""
Task 5: Conversation History — Multi-Turn Conversations — AWS Bedrock
Learn how to maintain context across multiple turns with Bedrock.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  pip install boto3
  aws configure  (set up AWS credentials)
  Enable Claude model access in AWS Bedrock console
"""

import boto3
import json

def call_bedrock(bedrock, system, messages):
    """Helper to call Bedrock and return the assistant text."""
    response = bedrock.invoke_model(
        modelId="anthropic.claude-sonnet-4-6",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "system": system,
            "messages": messages
        })
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


def main():
    print("=" * 65)
    print("Task 5: Conversation History — AWS Bedrock")
    print("=" * 65)

    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"
    )

    system = "You are a senior SRE assistant. Remember details from the conversation."
    conversation = []

    # Turn 1
    print("\nTurn 1: Describe the Problem")
    print("-" * 65)
    message_1 = "I'm seeing OOM kills on my api-server pod in production. Memory limit is 256Mi."

    conversation.append({"role": "user", "content": message_1})
    assistant_reply = call_bedrock(bedrock, system, conversation)
    conversation.append({"role": "assistant", "content": assistant_reply})

    print(f"User: {message_1}")
    print(f"Agent: {assistant_reply}")

    # Turn 2
    print("\nTurn 2: Follow-up Question")
    print("-" * 65)
    message_2 = "Can you tell me what pod and memory limit I just mentioned?"

    conversation.append({"role": "user", "content": message_2})
    assistant_reply = call_bedrock(bedrock, system, conversation)
    conversation.append({"role": "assistant", "content": assistant_reply})

    print(f"User: {message_2}")
    print(f"Agent: {assistant_reply}")

    # Turn 3
    print("\nTurn 3: Ask for the Fix")
    print("-" * 65)
    message_3 = "Give me the kubectl commands to fix the issue."

    conversation.append({"role": "user", "content": message_3})
    assistant_reply = call_bedrock(bedrock, system, conversation)
    conversation.append({"role": "assistant", "content": assistant_reply})

    print(f"User: {message_3}")
    print(f"Agent: {assistant_reply}")

    print(f"\nTotal messages in history: {len(conversation)}")

    print("\n" + "=" * 65)
    print("Key Learning: Bedrock has NO built-in memory.")
    print("YOU maintain the conversation list. Each invoke_model call sends")
    print("the FULL history in the JSON body.")
    print("=" * 65)

    print("\nTask 5 Complete!")
    print("Next: python3 demos/bedrock/task6_context_window.py")


if __name__ == "__main__":
    main()
