#!/usr/bin/env python3
"""
Episode 6 - Task 1: Function Calling (Tool Use) with Claude
============================================================

Learn how to define tools and let Claude decide which ones to call.

In this task, you will:
- Define Kubernetes tools with proper JSON schemas
- Send user questions along with tool definitions to Claude
- Observe how Claude selects the appropriate tool to call

Prerequisites:
- pip install anthropic
- ANTHROPIC_API_KEY environment variable set

The key insight: YOU define the tools, Claude decides WHEN to use them.
"""

import json
import anthropic

# Initialize the Anthropic client
client = anthropic.Anthropic()

# ============================================================
# TOOL DEFINITIONS
# ============================================================
# Tools are defined with JSON Schema. Claude uses the name,
# description, and schema to decide when and how to call them.

k8s_tools = [
    {
        "name": "get_pod_status",
        "description": "Get the current status of a Kubernetes pod including its phase, conditions, and container states. Use this when you need to check if a pod is running, pending, or in an error state.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "The Kubernetes namespace where the pod is located (e.g., 'default', 'production', 'monitoring')"
                },
                "pod_name": {
                    "type": "string",
                    "description": "The name of the pod to check (e.g., 'api-server-7d4b8c6f5-x2k9m')"
                }
            },
            "required": ["namespace", "pod_name"]
        }
    },
    {
        "name": "get_pod_logs",
        "description": "Retrieve recent log lines from a Kubernetes pod. Use this when you need to investigate errors, check application output, or debug issues in a running container.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "The Kubernetes namespace where the pod is located"
                },
                "pod_name": {
                    "type": "string",
                    "description": "The name of the pod to get logs from"
                },
                "lines": {
                    "type": "integer",
                    "description": "Number of recent log lines to retrieve (default: 50)"
                }
            },
            "required": ["namespace", "pod_name"]
        }
    },
    {
        "name": "restart_deployment",
        "description": "Perform a rolling restart of a Kubernetes deployment. Use this when pods need to be recycled to pick up new configuration or to recover from a bad state.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "The Kubernetes namespace where the deployment is located"
                },
                "deployment_name": {
                    "type": "string",
                    "description": "The name of the deployment to restart (e.g., 'api-server', 'payment-service')"
                }
            },
            "required": ["namespace", "deployment_name"]
        }
    }
]


def print_tool_definitions():
    """Display the tool definitions in a readable format."""
    print("=" * 65)
    print("KUBERNETES TOOL DEFINITIONS")
    print("=" * 65)
    print()
    for i, tool in enumerate(k8s_tools, 1):
        print(f"Tool {i}: {tool['name']}")
        print(f"  Description: {tool['description'][:80]}...")
        params = tool['input_schema']['properties']
        print(f"  Parameters: {', '.join(params.keys())}")
        print(f"  Required: {tool['input_schema']['required']}")
        print()


def experiment_1():
    """Experiment 1: Ask about pod status - Claude should call get_pod_status."""
    print("=" * 65)
    print("EXPERIMENT 1: Asking About Pod Status")
    print("=" * 65)
    print()

    user_question = "What's the status of the api-server pod in the production namespace?"
    print(f"User Question: {user_question}")
    print()
    print("Sending to Claude with tool definitions...")
    print("-" * 65)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=k8s_tools,
        messages=[{"role": "user", "content": user_question}]
    )

    print(f"\nStop Reason: {response.stop_reason}")
    print(f"  (stop_reason='tool_use' means Claude wants to call a tool)")
    print()

    # Examine the response content blocks
    for block in response.content:
        if block.type == "text":
            print(f"Claude's Thinking: {block.text}")
        elif block.type == "tool_use":
            print(f"Tool Claude Chose: {block.name}")
            print(f"Tool Use ID: {block.id}")
            print(f"Arguments Claude Provided:")
            print(f"  {json.dumps(block.input, indent=2)}")

    print()
    print("Key Observation: Claude analyzed the question and determined")
    print("that 'get_pod_status' is the right tool. It extracted the")
    print("namespace ('production') and pod name ('api-server') from")
    print("natural language!")


def experiment_2():
    """Experiment 2: Ask about logs - Claude should call get_pod_logs."""
    print()
    print("=" * 65)
    print("EXPERIMENT 2: Asking About Logs")
    print("=" * 65)
    print()

    user_question = "Show me the last 20 lines of logs from the payment-service pod in the default namespace"
    print(f"User Question: {user_question}")
    print()
    print("Sending to Claude with tool definitions...")
    print("-" * 65)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=k8s_tools,
        messages=[{"role": "user", "content": user_question}]
    )

    print(f"\nStop Reason: {response.stop_reason}")
    print()

    for block in response.content:
        if block.type == "text":
            print(f"Claude's Thinking: {block.text}")
        elif block.type == "tool_use":
            print(f"Tool Claude Chose: {block.name}")
            print(f"Tool Use ID: {block.id}")
            print(f"Arguments Claude Provided:")
            print(f"  {json.dumps(block.input, indent=2)}")

    print()
    print("Key Observation: Claude chose 'get_pod_logs' and extracted")
    print("all three parameters: namespace, pod_name, AND the number")
    print("of lines (20) from the natural language request!")


def experiment_3_no_tool_needed():
    """Bonus: Ask a question that does NOT need a tool."""
    print()
    print("=" * 65)
    print("EXPERIMENT 3 (Bonus): Question That Needs No Tool")
    print("=" * 65)
    print()

    user_question = "What are the best practices for setting resource limits on Kubernetes pods?"
    print(f"User Question: {user_question}")
    print()
    print("Sending to Claude with tool definitions...")
    print("-" * 65)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=k8s_tools,
        messages=[{"role": "user", "content": user_question}]
    )

    print(f"\nStop Reason: {response.stop_reason}")
    print()

    for block in response.content:
        if block.type == "text":
            print(f"Claude's Response: {block.text[:200]}...")

    print()
    print("Key Observation: Claude recognized this is a general knowledge")
    print("question and answered directly WITHOUT calling any tool!")
    print("This is the intelligence of tool_choice='auto' (the default).")


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    print()
    print("=" * 65)
    print("  EPISODE 6 - TASK 1: FUNCTION CALLING WITH CLAUDE")
    print("  Defining Tools and Letting Claude Decide")
    print("=" * 65)
    print()

    # Show the tool definitions first
    print_tool_definitions()

    # Run experiments
    experiment_1()
    experiment_2()
    experiment_3_no_tool_needed()

    # Key Learning
    print()
    print("=" * 65)
    print("KEY LEARNING")
    print("=" * 65)
    print("""
    1. Tools are defined with JSON Schema (name, description, input_schema)
    2. Claude reads the descriptions to decide WHICH tool to call
    3. Claude extracts parameters from natural language automatically
    4. With tool_choice='auto' (default), Claude can choose to NOT
       use a tool if the question doesn't need one
    5. The response has stop_reason='tool_use' when Claude wants
       to call a tool, and 'end_turn' when it answers directly
    6. Tool definitions are the CONTRACT between you and Claude -
       clear descriptions lead to better tool selection!
    """)

    print("=" * 65)
    print("Next: task2_tool_execution.py")
    print("  -> Execute the tool calls and feed results back to Claude")
    print("=" * 65)
