#!/usr/bin/env python3
"""
Episode 6 - Task 2: Tool Execution — Full Round-Trip
=====================================================

Execute tool calls from Claude and feed results back to get a final answer.

In this task, you will:
- Send tools to Claude and detect tool_use in the response
- Execute the requested function locally
- Send the tool_result back to Claude
- Get Claude's final answer that incorporates the tool result

Prerequisites:
- pip install anthropic
- ANTHROPIC_API_KEY environment variable set

The key insight: Claude does NOT execute tools. It requests them.
YOUR code runs the function and returns the result. This is the
handshake between AI reasoning and real-world actions.
"""

import json
import anthropic

# Initialize the Anthropic client
client = anthropic.Anthropic()

# =================================================================
# TOOL DEFINITIONS
# =================================================================

tools = [
    {
        "name": "check_pod_health",
        "description": (
            "Check the health of a Kubernetes pod including its status, "
            "readiness, restart count, and any error conditions. Use this "
            "to determine if a pod is healthy or needs attention."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Kubernetes namespace (e.g., 'default', 'production')"
                },
                "pod_name": {
                    "type": "string",
                    "description": "Name of the pod to check"
                }
            },
            "required": ["namespace", "pod_name"]
        }
    },
    {
        "name": "get_pod_events",
        "description": (
            "Get recent Kubernetes events for a pod. Events show "
            "scheduling decisions, image pulls, container starts/stops, "
            "and error messages from the kubelet."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Kubernetes namespace"
                },
                "pod_name": {
                    "type": "string",
                    "description": "Name of the pod"
                }
            },
            "required": ["namespace", "pod_name"]
        }
    }
]

# =================================================================
# TOOL IMPLEMENTATIONS (Mock — replace with real kubectl in prod)
# =================================================================

MOCK_POD_DATA = {
    ("production", "payment-service-7d4b8c"): {
        "pod": "payment-service-7d4b8c",
        "namespace": "production",
        "status": "Running",
        "phase": "Running",
        "ready": "1/1",
        "restarts": 0,
        "age": "5d",
        "conditions": {
            "Ready": True,
            "ContainersReady": True,
            "PodScheduled": True
        },
        "health": "HEALTHY"
    },
    ("production", "order-service-3e8b1a"): {
        "pod": "order-service-3e8b1a",
        "namespace": "production",
        "status": "CrashLoopBackOff",
        "phase": "Running",
        "ready": "0/1",
        "restarts": 14,
        "age": "2h",
        "conditions": {
            "Ready": False,
            "ContainersReady": False,
            "PodScheduled": True
        },
        "last_termination": {
            "reason": "OOMKilled",
            "exit_code": 137,
            "finished_at": "2024-01-15T10:28:00Z"
        },
        "health": "UNHEALTHY"
    }
}

MOCK_EVENTS = {
    ("production", "payment-service-7d4b8c"): [
        {"type": "Normal", "reason": "Scheduled", "age": "5d",
         "message": "Successfully assigned to worker-node-02"},
        {"type": "Normal", "reason": "Pulled", "age": "5d",
         "message": "Container image already present on machine"},
        {"type": "Normal", "reason": "Started", "age": "5d",
         "message": "Started container app"},
    ],
    ("production", "order-service-3e8b1a"): [
        {"type": "Normal", "reason": "Scheduled", "age": "2h",
         "message": "Successfully assigned to worker-node-01"},
        {"type": "Normal", "reason": "Pulled", "age": "2h",
         "message": "Container image pulled successfully"},
        {"type": "Warning", "reason": "OOMKilled", "age": "5m",
         "message": "Container exceeded memory limit (128Mi)"},
        {"type": "Warning", "reason": "BackOff", "age": "2m",
         "message": "Back-off restarting failed container"},
        {"type": "Normal", "reason": "Pulling", "age": "1m",
         "message": "Pulling image order-service:v2.1.0"},
    ]
}


def check_pod_health(namespace: str, pod_name: str) -> str:
    """Simulate kubectl get pod + conditions check."""
    key = (namespace, pod_name)
    if key in MOCK_POD_DATA:
        return json.dumps(MOCK_POD_DATA[key], indent=2)
    return json.dumps({
        "error": f"Pod '{pod_name}' not found in namespace '{namespace}'"
    })


def get_pod_events(namespace: str, pod_name: str) -> str:
    """Simulate kubectl get events for a pod."""
    key = (namespace, pod_name)
    if key in MOCK_EVENTS:
        return json.dumps({
            "pod": pod_name,
            "namespace": namespace,
            "events": MOCK_EVENTS[key]
        }, indent=2)
    return json.dumps({
        "error": f"No events found for pod '{pod_name}' in namespace '{namespace}'"
    })


# =================================================================
# TOOL DISPATCHER
# =================================================================

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Route tool calls to their implementations."""
    dispatch = {
        "check_pod_health": check_pod_health,
        "get_pod_events": get_pod_events,
    }
    if tool_name not in dispatch:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    try:
        return dispatch[tool_name](**tool_input)
    except Exception as e:
        return json.dumps({"error": f"Execution failed: {str(e)}"})


# =================================================================
# FULL ROUND-TRIP DEMONSTRATION
# =================================================================

def demonstrate_round_trip():
    """Show the complete tool execution cycle."""
    print("=" * 65)
    print("EXPERIMENT 1: Full Tool Execution Round-Trip")
    print("=" * 65)
    print()

    user_question = "Is the order-service-3e8b1a pod healthy in the production namespace?"
    print(f"User Question: {user_question}")
    print("-" * 65)

    # --- STEP 1: Send message with tools ---
    print("\n[STEP 1] Sending message to Claude with tool definitions...")
    messages = [{"role": "user", "content": user_question}]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    print(f"  Stop reason: {response.stop_reason}")

    # --- STEP 2: Detect tool_use in response ---
    if response.stop_reason != "tool_use":
        print("  Claude answered directly (no tool needed).")
        for block in response.content:
            if block.type == "text":
                print(f"  Response: {block.text}")
        return

    print("\n[STEP 2] Claude wants to call a tool! Extracting request...")

    # Append the assistant's response to messages
    messages.append({"role": "assistant", "content": response.content})

    # --- STEP 3: Execute the function ---
    print("\n[STEP 3] Executing tool call(s)...")
    tool_results = []
    for block in response.content:
        if block.type == "text" and block.text:
            print(f"  Claude's thinking: {block.text}")
        elif block.type == "tool_use":
            print(f"  Tool requested: {block.name}")
            print(f"  Arguments: {json.dumps(block.input, indent=4)}")
            print(f"  Tool Use ID: {block.id}")

            # Execute the tool
            result = execute_tool(block.name, block.input)
            print(f"\n  Execution result:")
            for line in result.split("\n")[:8]:
                print(f"    {line}")
            if result.count("\n") > 8:
                print(f"    ... ({result.count(chr(10))} lines total)")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            })

    # --- STEP 4: Send tool_result back to Claude ---
    print(f"\n[STEP 4] Sending tool_result back to Claude...")
    messages.append({"role": "user", "content": tool_results})

    final_response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    # --- STEP 5: Get Claude's final answer ---
    print(f"\n[STEP 5] Claude's final answer (informed by tool result):")
    print("-" * 65)
    for block in final_response.content:
        if block.type == "text":
            print(block.text)
    print("-" * 65)


def demonstrate_healthy_pod():
    """Show the round-trip for a healthy pod."""
    print()
    print("=" * 65)
    print("EXPERIMENT 2: Checking a Healthy Pod")
    print("=" * 65)
    print()

    user_question = "Check if payment-service-7d4b8c is healthy in production"
    print(f"User Question: {user_question}")
    print("-" * 65)

    messages = [{"role": "user", "content": user_question}]

    # First call - Claude requests a tool
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                print(f"\n  [TOOL] {block.name}({json.dumps(block.input)})")
                result = execute_tool(block.name, block.input)
                print(f"  [RESULT] {result[:80]}...")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        messages.append({"role": "user", "content": tool_results})

        # Get final answer
        final_response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        print(f"\n  Claude's analysis:")
        print("-" * 65)
        for block in final_response.content:
            if block.type == "text":
                print(block.text)
        print("-" * 65)


def demonstrate_error_handling():
    """Show what happens when a tool returns an error."""
    print()
    print("=" * 65)
    print("EXPERIMENT 3: Error Handling — Pod Not Found")
    print("=" * 65)
    print()

    user_question = "Check the health of the ghost-pod in the staging namespace"
    print(f"User Question: {user_question}")
    print("-" * 65)

    messages = [{"role": "user", "content": user_question}]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                print(f"\n  [TOOL] {block.name}({json.dumps(block.input)})")
                result = execute_tool(block.name, block.input)
                print(f"  [RESULT] {result}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        messages.append({"role": "user", "content": tool_results})

        final_response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        print(f"\n  Claude's response to the error:")
        print("-" * 65)
        for block in final_response.content:
            if block.type == "text":
                print(block.text)
        print("-" * 65)

    print()
    print("  Key Observation: Claude adapts gracefully to error results.")
    print("  Always return errors as content (not exceptions) so Claude")
    print("  can inform the user about what went wrong.")


# =================================================================
# MAIN EXECUTION
# =================================================================

if __name__ == "__main__":
    print()
    print("=" * 65)
    print("  EPISODE 6 - TASK 2: TOOL EXECUTION (FULL ROUND-TRIP)")
    print("  Send Tools -> Detect tool_use -> Execute -> Return Result")
    print("=" * 65)
    print()
    print("The message flow:")
    print("  1. User asks a question")
    print("  2. Claude responds with tool_use (stop_reason='tool_use')")
    print("  3. Your code executes the requested function")
    print("  4. You send the result back as tool_result")
    print("  5. Claude produces its final answer using the result")
    print()

    # Run demonstrations
    demonstrate_round_trip()
    demonstrate_healthy_pod()
    demonstrate_error_handling()

    # Key Learning
    print()
    print("=" * 65)
    print("KEY LEARNING")
    print("=" * 65)
    print("""
    1. The round-trip has 5 parts:
       User message -> Claude tool_use -> Execute -> tool_result -> Final answer

    2. The tool_use_id links each result to its request:
       tool_results.append({
           "type": "tool_result",
           "tool_use_id": block.id,  # Must match!
           "content": result_string
       })

    3. Tool results are ALWAYS strings (or list of content blocks).
       JSON.dumps() your structured data before returning it.

    4. Errors should be returned as content, not raised as exceptions.
       Claude will adapt its response based on error information.

    5. The assistant message (with tool_use) MUST be appended before
       the tool_result message. The conversation structure is:
       [user] -> [assistant with tool_use] -> [user with tool_result] -> [assistant final]
    """)

    print("=" * 65)
    print("Next: task3_agent_loop.py")
    print("  -> Build the agent loop that keeps calling tools until done")
    print("=" * 65)
