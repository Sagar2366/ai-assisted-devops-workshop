#!/usr/bin/env python3
"""
Task 9: Basic Tool Use — Pod Health Checker — AWS Bedrock
See the model DECIDE to call a tool — the core of what makes an agent.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  pip install boto3
  aws configure
"""

import boto3
import json

POD_STATUS_DB = {
    "monitoring": """NAME                          READY   STATUS             RESTARTS   AGE
prometheus-server-0            1/1     Running            0          7d
grafana-6b8c4d9f-n3k8p        1/1     Running            0          7d
alertmanager-0                 0/1     CrashLoopBackOff   5          2d
node-exporter-x4m9v            1/1     Running            0          7d"""
}


def main():
    print("=" * 65)
    print("Task 9: Basic Tool Use — Pod Health Checker — AWS Bedrock")
    print("=" * 65)

    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

    tool_config = {
        "tools": [
            {
                "toolSpec": {
                    "name": "check_pod_status",
                    "description": "Check the status of Kubernetes pods in a namespace.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "namespace": {
                                    "type": "string",
                                    "description": "Kubernetes namespace to check"
                                }
                            },
                            "required": ["namespace"]
                        }
                    }
                }
            }
        ]
    }

    def execute_tool(namespace):
        print(f"\n  [TOOL CALLED] check_pod_status(namespace={namespace})")
        result = POD_STATUS_DB.get(namespace, f"No pods in '{namespace}'")
        print(f"  [TOOL RESULT]\n{result}\n")
        return result

    query = "Are my pods healthy in the monitoring namespace?"
    print(f"\nQuery: {query}")
    print("-" * 40)

    messages = [{"role": "user", "content": [{"text": query}]}]

    response = bedrock.converse(
        modelId="anthropic.claude-sonnet-4-6",
        system=[{"text": "You are an SRE assistant. Use check_pod_status to inspect pods. Flag anything not Running."}],
        messages=messages,
        toolConfig=tool_config
    )

    if response["stopReason"] == "tool_use":
        for block in response["output"]["message"]["content"]:
            if "toolUse" in block:
                tu = block["toolUse"]
                result = execute_tool(**tu["input"])

                messages.append(response["output"]["message"])
                messages.append({
                    "role": "user",
                    "content": [{"toolResult": {
                        "toolUseId": tu["toolUseId"],
                        "content": [{"text": str(result)}]
                    }}]
                })

                final = bedrock.converse(
                    modelId="anthropic.claude-sonnet-4-6",
                    system=[{"text": "You are an SRE assistant. Summarize pod health. Flag anything not Running."}],
                    messages=messages,
                    toolConfig=tool_config
                )
                print(f"Agent: {final['output']['message']['content'][0]['text']}")
    else:
        print(f"Agent: {response['output']['message']['content'][0]['text']}")

    print("\n" + "=" * 65)
    print("Key Learning: YOU defined the tool. The MODEL decided to call it.")
    print("That is the core of an agent — the model chooses when to act.")
    print("We go deep on tools in Episode 4.")
    print("=" * 65)

    print("\nTask 9 Complete!")
    print("All tasks complete! Try another provider: demos/google/, demos/openai/")


if __name__ == "__main__":
    main()
