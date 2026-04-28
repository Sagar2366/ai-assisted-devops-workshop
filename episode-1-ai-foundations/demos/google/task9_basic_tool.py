#!/usr/bin/env python3
"""
Task 9: Basic Tool Use — Pod Health Checker — Google Gemini
See the model DECIDE to call a tool — the core of what makes an agent.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export GOOGLE_API_KEY="your-key-here"
  pip install google-generativeai
"""

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
import os

POD_STATUS_DB = {
    "monitoring": """NAME                          READY   STATUS             RESTARTS   AGE
prometheus-server-0            1/1     Running            0          7d
grafana-6b8c4d9f-n3k8p        1/1     Running            0          7d
alertmanager-0                 0/1     CrashLoopBackOff   5          2d
node-exporter-x4m9v            1/1     Running            0          7d"""
}


def main():
    print("=" * 65)
    print("Task 9: Basic Tool Use — Pod Health Checker — Google Gemini")
    print("=" * 65)

    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    check_pod_func = FunctionDeclaration(
        name="check_pod_status",
        description="Check the status of Kubernetes pods in a namespace.",
        parameters={
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Kubernetes namespace to check"
                }
            },
            "required": ["namespace"]
        }
    )
    tool = Tool(function_declarations=[check_pod_func])

    model = genai.GenerativeModel(
        "gemini-2.5-flash",
        tools=[tool],
        system_instruction="You are an SRE assistant. Use check_pod_status to inspect pods. Flag anything not Running."
    )

    def execute_tool(namespace):
        print(f"\n  [TOOL CALLED] check_pod_status(namespace={namespace})")
        result = POD_STATUS_DB.get(namespace, f"No pods in '{namespace}'")
        print(f"  [TOOL RESULT]\n{result}\n")
        return result

    query = "Are my pods healthy in the monitoring namespace?"
    print(f"\nQuery: {query}")
    print("-" * 40)

    chat = model.start_chat()
    response = chat.send_message(query)

    for part in response.candidates[0].content.parts:
        if hasattr(part, 'function_call') and part.function_call:
            fc = part.function_call
            result = execute_tool(**{k: v for k, v in fc.args.items()})

            response = chat.send_message(
                genai.protos.Content(parts=[
                    genai.protos.Part(function_response=genai.protos.FunctionResponse(
                        name=fc.name,
                        response={"result": result}
                    ))
                ])
            )
            print(f"Agent: {response.text}")
        elif hasattr(part, 'text') and part.text:
            print(f"Agent: {part.text}")

    print("\n" + "=" * 65)
    print("Key Learning: YOU defined the tool. The MODEL decided to call it.")
    print("That is the core of an agent — the model chooses when to act.")
    print("We go deep on tools in Episode 4.")
    print("=" * 65)

    print("\nTask 9 Complete!")
    print("All tasks complete! Try another provider: demos/google/, demos/openai/")


if __name__ == "__main__":
    main()
