#!/usr/bin/env python3
"""
Task 9: Basic Tool Use — Pod Health Checker — OpenAI GPT
See the model DECIDE to call a tool — the core of what makes an agent.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export OPENAI_API_KEY="your-key-here"
  pip install openai
"""

import openai
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
    print("Task 9: Basic Tool Use — Pod Health Checker — OpenAI GPT")
    print("=" * 65)

    client = openai.OpenAI()

    tools = [
        {
            "type": "function",
            "function": {
                "name": "check_pod_status",
                "description": "Check the status of Kubernetes pods in a namespace.",
                "parameters": {
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
    ]

    def execute_tool(namespace):
        print(f"\n  [TOOL CALLED] check_pod_status(namespace={namespace})")
        result = POD_STATUS_DB.get(namespace, f"No pods in '{namespace}'")
        print(f"  [TOOL RESULT]\n{result}\n")
        return result

    query = "Are my pods healthy in the monitoring namespace?"
    print(f"\nQuery: {query}")
    print("-" * 40)

    messages = [
        {"role": "system", "content": "You are an SRE assistant. Use check_pod_status to inspect pods. Flag anything not Running."},
        {"role": "user", "content": query}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
    )

    msg = response.choices[0].message
    if msg.tool_calls:
        tc = msg.tool_calls[0]
        args = json.loads(tc.function.arguments)
        result = execute_tool(**args)

        messages.append(msg)
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": str(result)
        })

        final = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools
        )
        print(f"Agent: {final.choices[0].message.content}")
    else:
        print(f"Agent: {msg.content}")

    print("\n" + "=" * 65)
    print("Key Learning: YOU defined the tool. The MODEL decided to call it.")
    print("That is the core of an agent — the model chooses when to act.")
    print("We go deep on tools in Episode 4.")
    print("=" * 65)

    print("\nTask 9 Complete!")
    print("All tasks complete! Try another provider: demos/google/, demos/openai/")


if __name__ == "__main__":
    main()
