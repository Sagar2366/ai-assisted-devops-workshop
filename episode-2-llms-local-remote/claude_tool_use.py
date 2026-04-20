#!/usr/bin/env python3
"""
Episode 2: Claude API with Tool Use — Foundation for Agents
AI-Assisted DevOps Workshop | Sagar Utekar

The LLM decides which kubectl/helm commands to run, executes them,
reads the output, and reasons about what to do next. This is the
core agent loop pattern used throughout the workshop.

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
  kind create cluster --name workshop (or any K8s cluster)
"""
import anthropic
import json
import subprocess

client = anthropic.Anthropic()

# Define tools the LLM can use
tools = [
    {
        "name": "run_kubectl",
        "description": "Execute a kubectl command against the Kubernetes cluster. Use this to inspect pods, services, deployments, logs, and events.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The kubectl command to run (without the 'kubectl' prefix). Example: 'get pods -n production'"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "run_helm",
        "description": "Execute a helm command. Use for checking releases, values, and history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The helm command to run (without 'helm' prefix). Example: 'list -A'"
                }
            },
            "required": ["command"]
        }
    }
]

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool call from the LLM."""
    if tool_name == "run_kubectl":
        try:
            result = subprocess.run(
                f"kubectl {tool_input['command']}",
                shell=True, capture_output=True, text=True, timeout=30
            )
            return result.stdout or result.stderr or "Command completed with no output"
        except subprocess.TimeoutExpired:
            return "ERROR: Command timed out after 30 seconds"
    elif tool_name == "run_helm":
        try:
            result = subprocess.run(
                f"helm {tool_input['command']}",
                shell=True, capture_output=True, text=True, timeout=30
            )
            return result.stdout or result.stderr or "Command completed with no output"
        except subprocess.TimeoutExpired:
            return "ERROR: Command timed out after 30 seconds"
    return f"Unknown tool: {tool_name}"

def chat_with_tools(user_message: str):
    """Send a message and handle tool calls in a loop."""
    messages = [{"role": "user", "content": user_message}]

    print(f"\n{'='*60}")
    print(f"USER: {user_message}")
    print(f"{'='*60}\n")

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system="You are a senior SRE. Use the provided tools to investigate and diagnose issues. Always verify your findings with actual cluster data before drawing conclusions.",
            tools=tools,
            messages=messages
        )

        # Check if the model wants to use tools
        if response.stop_reason == "tool_use":
            # Process all tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"AGENT RUNNING: {block.name}({json.dumps(block.input)})")
                    result = execute_tool(block.name, block.input)
                    print(f"RESULT: {result[:200]}...")
                    print()
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
                elif block.type == "text" and block.text:
                    print(f"AGENT THINKING: {block.text}")

            # Feed results back to the model
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            # Final response
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nAGENT CONCLUSION:\n{block.text}")
            break

# Run it!
if __name__ == "__main__":
    chat_with_tools("Check the health of all pods in the default namespace. If any are failing, diagnose why.")
