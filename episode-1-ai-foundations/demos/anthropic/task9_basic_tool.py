#!/usr/bin/env python3
"""
Task 9: Basic Tool Use — Pod Health Checker — Anthropic Claude
See the model DECIDE to call a tool — the core of what makes an agent.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""

import anthropic
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
    print("Task 9: Basic Tool Use — Pod Health Checker — Anthropic Claude")
    print("=" * 65)

    client = anthropic.Anthropic()

    tools = [
        {
            "name": "check_pod_status",
            "description": "Check the status of Kubernetes pods in a namespace.",
            "input_schema": {
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
    ]

    def execute_tool(namespace):
        print(f"\n  [TOOL CALLED] check_pod_status(namespace={namespace})")
        result = POD_STATUS_DB.get(namespace, f"No pods in '{namespace}'")
        print(f"  [TOOL RESULT]\n{result}\n")
        return result

    query = "Are my pods healthy in the monitoring namespace?"
    print(f"\nQuery: {query}")
    print("-" * 40)

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system="You are an SRE assistant. Use check_pod_status to inspect pods. Flag anything not Running.",
        tools=tools,
        messages=[{"role": "user", "content": query}]
    )

    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(**block.input)

                final = client.messages.create(
                    model="claude-opus-4-7",
                    max_tokens=1024,
                    tools=tools,
                    messages=[
                        {"role": "user", "content": query},
                        {"role": "assistant", "content": response.content},
                        {"role": "user", "content": [
                            {"type": "tool_result", "tool_use_id": block.id, "content": str(result)}
                        ]}
                    ]
                )
                print(f"Agent: {final.content[0].text}")
    else:
        print(f"Agent: {response.content[0].text}")

    print("\n" + "=" * 65)
    print("Key Learning: YOU defined the tool. The MODEL decided to call it.")
    print("That is the core of an agent — the model chooses when to act.")
    print("We go deep on tools in Episode 4.")
    print("=" * 65)

    print("\nTask 9 Complete!")
    print("All tasks complete! Try another provider: demos/google/, demos/openai/")


if __name__ == "__main__":
    main()
