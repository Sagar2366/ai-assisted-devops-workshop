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
        modelId="anthropic.claude-sonnet-4-20250514-v1:0",
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

    system = "You are a friendly customer support agent. Remember details that customers share with you."

    # In Bedrock (Anthropic format), conversation history is a list of messages
    # you maintain yourself. Each turn you append the user message and the assistant response.

    # TODO 1: Initialize the conversation history
    # This is just a Python list that holds all messages
    conversation = ___  # TODO: Use []

    print("Step 1 Complete: Conversation history initialized\n")

    # Turn 1: Customer introduces themselves (PRE-FILLED — shows the pattern)
    print("Turn 1: Customer Introduction")
    message_1 = "Hi, my name is Sarah and I'm having trouble with my account"

    conversation.append({"role": "user", "content": message_1})

    assistant_reply = call_bedrock(bedrock, system, conversation)
    conversation.append({"role": "assistant", "content": assistant_reply})

    print(f"User: {message_1}")
    print(f"Agent: {assistant_reply}")

    # Turn 2: Follow-up question
    print("\nTurn 2: Follow-up Question")
    message_2 = "Can you tell me what name I just gave you?"

    # TODO 2: Append the user message and call Bedrock with full history
    conversation.append({"role": "user", "content": ___})  # TODO: Use message_2

    assistant_reply = call_bedrock(bedrock, system, ___)  # TODO: Use conversation
    conversation.append({"role": "assistant", "content": assistant_reply})

    print(f"User: {message_2}")
    print(f"Agent: {assistant_reply}")

    # Turn 3: Another follow-up
    print("\nTurn 3: Another Follow-up")
    message_3 = "What was my issue again?"

    # TODO 3: Complete the third turn
    conversation.append({"role": "user", "content": ___})  # TODO: Use message_3

    assistant_reply = call_bedrock(bedrock, ___, conversation)  # TODO: Use system
    conversation.append({"role": "assistant", "content": assistant_reply})

    print(f"User: {message_3}")
    print(f"Agent: {assistant_reply}")

    print(f"\nTotal messages in history: {len(conversation)}")

    print("\n" + "=" * 65)
    print("Key Learning: Bedrock has NO built-in memory.")
    print("YOU maintain the conversation list. Each invoke_model call sends")
    print("the FULL history in the JSON body. The model sees everything you include.")
    print("=" * 65)

    print("\nTask 5 Complete!")
    print("Next: python3 demos/bedrock/task6_context_window.py")


if __name__ == "__main__":
    main()
