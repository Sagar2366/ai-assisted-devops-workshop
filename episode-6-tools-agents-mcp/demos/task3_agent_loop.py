#!/usr/bin/env python3
"""
AI-Assisted DevOps Workshop | Episode 6 | Sagar Utekar
=======================================================
Task 3: The Core Agent Loop - Find and Fix Crashing Pods

Build an autonomous agent that investigates and resolves Kubernetes
pod failures using a think -> act -> observe -> repeat loop.

In this task, you will:
- Define 3 tools: get_pods, get_pod_logs, restart_deployment
- Build the core agent loop (while stop_reason == "tool_use")
- Watch Claude autonomously diagnose and fix a CrashLoopBackOff
- See the full cycle: list pods -> find crash -> get logs -> restart

Prerequisites:
- pip install anthropic
- ANTHROPIC_API_KEY environment variable set

The key insight: An agent is just a WHILE LOOP. Claude thinks, acts,
observes, and repeats until the problem is solved.
"""

import json
import anthropic

# Initialize the Anthropic client
client = anthropic.Anthropic()

# =================================================================
# TOOL DEFINITIONS
# =================================================================
# Three tools that give Claude the ability to investigate and fix pods.

tools = [
    {
        "name": "get_pods",
        "description": (
            "List all pods in a Kubernetes namespace with their current "
            "status, readiness, and restart count. Use this to discover "
            "which pods are healthy and which are failing."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "The Kubernetes namespace to list pods from (e.g., 'default', 'production')"
                }
            },
            "required": ["namespace"]
        }
    },
    {
        "name": "get_pod_logs",
        "description": (
            "Retrieve recent log lines from a specific Kubernetes pod. "
            "Use this to investigate why a pod is crashing, erroring, "
            "or behaving unexpectedly."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "The Kubernetes namespace where the pod is running"
                },
                "pod_name": {
                    "type": "string",
                    "description": "The full name of the pod to get logs from"
                }
            },
            "required": ["namespace", "pod_name"]
        }
    },
    {
        "name": "restart_deployment",
        "description": (
            "Perform a rolling restart of a Kubernetes deployment. This "
            "recreates all pods in the deployment. Use this to recover "
            "from crashes after the root cause is understood."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "The Kubernetes namespace of the deployment"
                },
                "deployment_name": {
                    "type": "string",
                    "description": "The name of the deployment to restart (e.g., 'payment-service')"
                }
            },
            "required": ["namespace", "deployment_name"]
        }
    }
]


# =================================================================
# SIMULATED ENVIRONMENT (Mock Kubernetes Cluster)
# =================================================================
# These functions return realistic mock data showing a CrashLoopBackOff
# scenario. In production, they would call kubectl or the K8s API.

def get_pods(namespace: str) -> str:
    """Simulate: kubectl get pods -n <namespace>"""
    mock_data = {
        "production": [
            {
                "name": "api-gateway-6d8f7c5b4-x9k2m",
                "status": "Running",
                "ready": "1/1",
                "restarts": 0,
                "age": "5d"
            },
            {
                "name": "payment-service-7f8d9c4b5-cd4ym",
                "status": "CrashLoopBackOff",
                "ready": "0/1",
                "restarts": 14,
                "age": "3h"
            },
            {
                "name": "user-service-5c4d3e2f1-a8b9c",
                "status": "Running",
                "ready": "1/1",
                "restarts": 0,
                "age": "5d"
            },
            {
                "name": "redis-cache-0",
                "status": "Running",
                "ready": "1/1",
                "restarts": 0,
                "age": "30d"
            }
        ]
    }
    pods = mock_data.get(namespace, [])
    if not pods:
        return json.dumps({"error": f"No pods found in namespace '{namespace}'"})
    return json.dumps({"namespace": namespace, "pods": pods}, indent=2)


def get_pod_logs(namespace: str, pod_name: str) -> str:
    """Simulate: kubectl logs <pod_name> -n <namespace>"""
    if "payment-service" in pod_name:
        return """2024-01-15T14:30:01Z [INFO] Starting payment-service v2.4.1
2024-01-15T14:30:02Z [INFO] Connecting to Stripe API...
2024-01-15T14:30:03Z [INFO] Loading configuration from /etc/config/app.yaml
2024-01-15T14:30:04Z [ERROR] Failed to parse config: missing required field 'STRIPE_API_KEY'
2024-01-15T14:30:04Z [ERROR] Environment variable STRIPE_API_KEY is not set
2024-01-15T14:30:05Z [FATAL] Cannot start without payment gateway credentials. Exiting.
2024-01-15T14:30:05Z [INFO] Process exited with code 1
--- Previous restart logs show same error (restart count: 14) ---"""
    elif "api-gateway" in pod_name:
        return """2024-01-15T14:30:01Z [INFO] Request: GET /api/v1/health - 200 OK (12ms)
2024-01-15T14:30:02Z [INFO] Request: POST /api/v1/payments - 502 Bad Gateway
2024-01-15T14:30:03Z [WARN] Upstream payment-service is unavailable
2024-01-15T14:30:04Z [INFO] Request: GET /api/v1/users - 200 OK (45ms)"""
    else:
        return f"No recent logs available for pod '{pod_name}' in namespace '{namespace}'"


def restart_deployment(namespace: str, deployment_name: str) -> str:
    """Simulate: kubectl rollout restart deployment/<name> -n <namespace>"""
    return json.dumps({
        "status": "success",
        "message": f"deployment.apps/{deployment_name} restarted",
        "namespace": namespace,
        "timestamp": "2024-01-15T14:35:00Z",
        "note": "Rolling restart initiated. New pods will be created with updated config."
    }, indent=2)


# =================================================================
# TOOL DISPATCHER
# =================================================================

def execute_tool(name: str, inputs: dict) -> str:
    """Route a tool call to its mock implementation."""
    dispatch = {
        "get_pods": get_pods,
        "get_pod_logs": get_pod_logs,
        "restart_deployment": restart_deployment,
    }
    if name not in dispatch:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        return dispatch[name](**inputs)
    except Exception as e:
        return json.dumps({"error": f"Failed to execute {name}: {str(e)}"})


# =================================================================
# THE CORE AGENT LOOP
# =================================================================

def run_agent(user_query: str, max_iterations: int = 10) -> str:
    """
    The core agent loop pattern:

        response = client.messages.create(...)
        while response.stop_reason == "tool_use":
            execute the requested tool(s)
            append tool_result to messages
            call Claude again

    Claude keeps calling tools until it has enough information,
    then it provides a final answer (stop_reason == "end_turn").
    """
    print("=" * 65)
    print("  AGENT LOOP STARTED")
    print("=" * 65)
    print(f"\n  User: {user_query}\n")

    # Initialize the conversation
    messages = [{"role": "user", "content": user_query}]

    # System prompt gives Claude its SRE role
    system_prompt = (
        "You are a Kubernetes SRE agent. Your job is to investigate "
        "pod issues and resolve them. Use the tools available to: "
        "1) List pods to find problems, "
        "2) Check logs to understand the root cause, "
        "3) Take corrective action (restart deployments). "
        "Always explain your reasoning at each step."
    )

    # First call to Claude
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        tools=tools,
        messages=messages
    )

    iteration = 0

    # === THE AGENT LOOP ===
    # Keep looping while Claude wants to call tools
    while response.stop_reason == "tool_use":
        iteration += 1
        if iteration > max_iterations:
            print(f"\n  [WARNING] Max iterations ({max_iterations}) reached.")
            break

        print("-" * 65)
        print(f"  Iteration {iteration}")
        print("-" * 65)

        # Append Claude's response (with tool_use blocks) to history
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool Claude requested and collect results
        tool_results = []
        for block in response.content:
            if block.type == "text" and block.text:
                print(f"  [THINK]   {block.text[:150]}")
                if len(block.text) > 150:
                    print(f"            ...({len(block.text)} chars total)")
            elif block.type == "tool_use":
                print(f"  [ACT]     {block.name}({json.dumps(block.input)})")

                # Execute the tool
                result = execute_tool(block.name, block.input)

                # Show a preview of what came back
                preview = result.replace("\n", " ")[:100]
                print(f"  [OBSERVE] {preview}...")

                # Collect the tool result
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # Append tool results as a user message
        messages.append({"role": "user", "content": tool_results})

        # Call Claude again with the updated conversation
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

    # === AGENT FINISHED ===
    # stop_reason == "end_turn" means Claude is done investigating
    print()
    print("=" * 65)
    print("  AGENT'S FINAL REPORT")
    print("=" * 65)

    final_text = ""
    for block in response.content:
        if block.type == "text":
            final_text += block.text

    print(f"\n{final_text}\n")
    return final_text


# =================================================================
# MAIN EXECUTION
# =================================================================

if __name__ == "__main__":
    print()
    print("=" * 65)
    print("  EPISODE 6 - TASK 3: THE CORE AGENT LOOP")
    print("  AI-Assisted DevOps Workshop | Sagar Utekar")
    print("=" * 65)
    print()
    print("  Pattern: while response.stop_reason == 'tool_use':")
    print("               execute tool -> append result -> call Claude")
    print()
    print("  Scenario: Pods are crashing in production.")
    print("  Goal: Agent autonomously finds and fixes the issue.")
    print()
    print("  Expected agent reasoning path:")
    print("    1. get_pods            -> discover CrashLoopBackOff")
    print("    2. get_pod_logs        -> find root cause in error logs")
    print("    3. restart_deployment  -> remediate the crashing pod")
    print("    4. Report findings     -> explain what happened and how to fix")
    print()

    # -----------------------------------------------------------------
    # Experiment: Autonomous Pod Diagnosis and Fix
    # -----------------------------------------------------------------
    run_agent(
        "There are reports of payment failures in production. "
        "Please investigate which pods are having issues, "
        "determine the root cause from the logs, and take "
        "corrective action to restore service."
    )

    # Key Learning
    print()
    print("=" * 65)
    print("KEY LEARNING")
    print("=" * 65)
    print("""
    1. The agent loop is deceptively simple:

         response = client.messages.create(...)
         while response.stop_reason == "tool_use":
             results = execute_tools(response)
             messages.append(assistant_response)
             messages.append(tool_results)
             response = client.messages.create(...)

    2. Claude decides WHEN to stop - you don't hard-code the steps.
       It keeps calling tools until it has enough info to answer.

    3. The think -> act -> observe cycle:
       - THINK: Claude reasons about what to do next
       - ACT:   Claude picks a tool and provides arguments
       - OBSERVE: We execute the tool and return results
       - REPEAT: Until stop_reason == "end_turn"

    4. Claude maintains full CONTEXT across the loop - it remembers
       all previous observations when deciding its next action.

    5. This is THE core pattern behind every AI agent:
       Claude Code, GitHub Copilot, ChatGPT plugins - all use
       this same while loop with tool execution.
    """)

    print("=" * 65)
    print("Next: task4_mcp_basics.py")
    print("  -> Expose tools via MCP (Model Context Protocol) standard")
    print("=" * 65)
