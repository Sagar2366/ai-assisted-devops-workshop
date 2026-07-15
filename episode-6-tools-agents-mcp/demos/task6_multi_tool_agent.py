#!/usr/bin/env python3
"""
Episode 6 - Task 6: Multi-Tool Agent Orchestration
====================================================

Build an agent that orchestrates multiple tools to solve a complex
problem - diagnosing high API latency and taking corrective action.

In this task, you will:
- Define 5 tools for a complete SRE toolkit
- Build the agent loop (from task3) with more tools
- Watch the agent investigate, diagnose, and TAKE ACTION
- See how an agent plans and executes a multi-step resolution

Prerequisites:
- pip install anthropic
- ANTHROPIC_API_KEY environment variable set

The key insight: Agents don't just investigate - they can take
CORRECTIVE ACTION. This is the foundation of autonomous operations.
"""

import json
import anthropic
from datetime import datetime

client = anthropic.Anthropic()

# ============================================================
# TOOL DEFINITIONS - Complete SRE Toolkit
# ============================================================

sre_tools = [
    {
        "name": "get_pods",
        "description": "List pods in a namespace with their status, CPU/memory usage, and readiness. Use this to get an overview of what's running and identify unhealthy pods.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {"type": "string", "description": "Kubernetes namespace"},
                "label_selector": {"type": "string", "description": "Label selector (e.g., 'app=api-gateway')"}
            },
            "required": ["namespace"]
        }
    },
    {
        "name": "get_logs",
        "description": "Get recent logs from a pod. Use this to investigate errors, see request patterns, or check for issues in application output.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {"type": "string", "description": "Kubernetes namespace"},
                "pod_name": {"type": "string", "description": "Pod name"},
                "lines": {"type": "integer", "description": "Number of log lines (default: 30)"},
                "since": {"type": "string", "description": "Time duration (e.g., '5m', '1h')"}
            },
            "required": ["namespace", "pod_name"]
        }
    },
    {
        "name": "get_metrics",
        "description": "Get current resource metrics for pods (CPU, memory, network). Use this to check if pods are resource-constrained or overloaded.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {"type": "string", "description": "Kubernetes namespace"},
                "pod_name": {"type": "string", "description": "Specific pod (omit for all pods in namespace)"},
                "metric_type": {
                    "type": "string",
                    "description": "Type of metrics to retrieve",
                    "enum": ["cpu", "memory", "network", "all"]
                }
            },
            "required": ["namespace"]
        }
    },
    {
        "name": "check_deployment_status",
        "description": "Check the status of a deployment including replica count, available replicas, rolling update status, and recent events.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {"type": "string", "description": "Kubernetes namespace"},
                "deployment_name": {"type": "string", "description": "Deployment name"}
            },
            "required": ["namespace", "deployment_name"]
        }
    },
    {
        "name": "scale_deployment",
        "description": "Scale a deployment to a specified number of replicas. Use this to add capacity when pods are overloaded or to scale down after an incident.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {"type": "string", "description": "Kubernetes namespace"},
                "deployment_name": {"type": "string", "description": "Deployment name"},
                "replicas": {"type": "integer", "description": "Desired number of replicas"}
            },
            "required": ["namespace", "deployment_name", "replicas"]
        }
    }
]

# ============================================================
# MOCK IMPLEMENTATIONS - Tell the story of an overloaded API
# ============================================================

# Track state so scaling actually changes things
current_replicas = 2


def get_pods(namespace: str, label_selector: str = None) -> str:
    """Return pod status showing high CPU usage."""
    pods = [
        {
            "name": "api-gateway-7f8d9c4b5-x2k9m",
            "status": "Running",
            "ready": "1/1",
            "cpu": "480m/500m (96%)",
            "memory": "256Mi/512Mi (50%)",
            "restarts": 0,
            "age": "5d"
        },
        {
            "name": "api-gateway-7f8d9c4b5-y3n7p",
            "status": "Running",
            "ready": "1/1",
            "cpu": "495m/500m (99%)",
            "memory": "280Mi/512Mi (55%)",
            "restarts": 0,
            "age": "5d"
        }
    ]
    return json.dumps({
        "namespace": namespace,
        "pods": pods,
        "summary": "2 pods running, both showing very high CPU utilization (>95%)"
    }, indent=2)


def get_logs(namespace: str, pod_name: str, lines: int = 30, since: str = "5m") -> str:
    """Return logs showing slow responses."""
    return f"""=== Logs from {pod_name} (last {since}) ===
2024-01-15T14:30:01Z [INFO] GET /api/v1/products - 200 OK (2340ms) - SLOW
2024-01-15T14:30:01Z [WARN] Request queue depth: 47 (threshold: 20)
2024-01-15T14:30:02Z [INFO] POST /api/v1/orders - 200 OK (3100ms) - SLOW
2024-01-15T14:30:02Z [WARN] Thread pool exhausted: 50/50 threads busy
2024-01-15T14:30:03Z [INFO] GET /api/v1/users - 200 OK (1890ms) - SLOW
2024-01-15T14:30:03Z [WARN] Connection pool at capacity: 100/100
2024-01-15T14:30:04Z [ERROR] Request timeout: GET /api/v1/inventory (5000ms exceeded)
2024-01-15T14:30:05Z [INFO] GET /api/v1/products - 200 OK (2780ms) - SLOW
2024-01-15T14:30:05Z [WARN] P99 latency: 3200ms (SLA target: 500ms)
2024-01-15T14:30:06Z [INFO] Health check: OK (but degraded performance)"""


def get_metrics(namespace: str, pod_name: str = None, metric_type: str = "all") -> str:
    """Return metrics showing resource saturation."""
    return json.dumps({
        "namespace": namespace,
        "timestamp": "2024-01-15T14:30:00Z",
        "pods": [
            {
                "name": "api-gateway-7f8d9c4b5-x2k9m",
                "cpu": {
                    "usage": "480m",
                    "limit": "500m",
                    "utilization_percent": 96,
                    "throttled": True,
                    "throttle_count_last_5m": 342
                },
                "memory": {
                    "usage": "256Mi",
                    "limit": "512Mi",
                    "utilization_percent": 50
                },
                "network": {
                    "rx_bytes_per_sec": "12.5MB",
                    "tx_bytes_per_sec": "8.3MB",
                    "connections_active": 850
                }
            },
            {
                "name": "api-gateway-7f8d9c4b5-y3n7p",
                "cpu": {
                    "usage": "495m",
                    "limit": "500m",
                    "utilization_percent": 99,
                    "throttled": True,
                    "throttle_count_last_5m": 518
                },
                "memory": {
                    "usage": "280Mi",
                    "limit": "512Mi",
                    "utilization_percent": 55
                },
                "network": {
                    "rx_bytes_per_sec": "14.1MB",
                    "tx_bytes_per_sec": "9.7MB",
                    "connections_active": 920
                }
            }
        ],
        "analysis": {
            "bottleneck": "CPU",
            "cpu_throttled": True,
            "memory_ok": True,
            "recommendation": "Pods are CPU-saturated. Consider scaling horizontally."
        }
    }, indent=2)


def check_deployment_status(namespace: str, deployment_name: str) -> str:
    """Return deployment status showing only 2 replicas."""
    global current_replicas
    return json.dumps({
        "deployment": deployment_name,
        "namespace": namespace,
        "replicas": {
            "desired": current_replicas,
            "current": current_replicas,
            "ready": current_replicas,
            "available": current_replicas
        },
        "strategy": "RollingUpdate",
        "max_replicas_allowed": 10,
        "hpa": {
            "enabled": False,
            "note": "HorizontalPodAutoscaler not configured"
        },
        "last_scaling_event": "2024-01-10T08:00:00Z (5 days ago)",
        "conditions": [
            {"type": "Available", "status": "True"},
            {"type": "Progressing", "status": "True"}
        ]
    }, indent=2)


def scale_deployment(namespace: str, deployment_name: str, replicas: int) -> str:
    """Scale the deployment (simulated)."""
    global current_replicas
    old_replicas = current_replicas
    current_replicas = replicas
    return json.dumps({
        "status": "success",
        "action": "scale",
        "deployment": deployment_name,
        "namespace": namespace,
        "previous_replicas": old_replicas,
        "new_replicas": replicas,
        "message": f"deployment.apps/{deployment_name} scaled from {old_replicas} to {replicas} replicas",
        "estimated_ready_time": "60-90 seconds",
        "timestamp": datetime.now().isoformat()
    }, indent=2)


def execute_tool(name: str, inputs: dict) -> str:
    """Route tool calls to implementations."""
    tool_map = {
        "get_pods": get_pods,
        "get_logs": get_logs,
        "get_metrics": get_metrics,
        "check_deployment_status": check_deployment_status,
        "scale_deployment": scale_deployment,
    }
    if name in tool_map:
        return tool_map[name](**inputs)
    return json.dumps({"error": f"Unknown tool: {name}"})


# ============================================================
# THE MULTI-TOOL AGENT
# ============================================================

def run_agent(user_message: str):
    """
    Run the agent loop - same pattern as task3, but with more tools
    and a scenario where the agent takes corrective action.
    """
    print("=" * 65)
    print("MULTI-TOOL AGENT: Investigating and Resolving")
    print("=" * 65)
    print(f"\nUser: {user_message}")
    print()

    messages = [{"role": "user", "content": user_message}]
    step = 0
    actions_taken = []

    while True:
        step += 1
        print(f"{'=' * 65}")
        print(f"  STEP {step}")
        print(f"{'=' * 65}")

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=sre_tools,
            messages=messages
        )

        # Check if done
        if response.stop_reason == "end_turn":
            print("\n  [COMPLETE] Agent has finished.")
            print("-" * 65)
            print("\n  AGENT'S FINAL REPORT:")
            print("-" * 65)
            for block in response.content:
                if block.type == "text":
                    print(f"\n{block.text}")
            break

        # Process tool calls
        tool_results = []
        for block in response.content:
            if block.type == "text" and block.text:
                print(f"\n  [REASONING] {block.text[:200]}")
                if len(block.text) > 200:
                    print(f"              ...({len(block.text)} chars)")
            elif block.type == "tool_use":
                print(f"\n  [ACTION] {block.name}({json.dumps(block.input)})")

                # Execute the tool
                result = execute_tool(block.name, block.input)

                # Track actions for summary
                actions_taken.append({
                    "step": step,
                    "tool": block.name,
                    "input": block.input,
                    "result_preview": result[:80]
                })

                # Show result
                result_lines = result.split('\n')
                preview = '\n'.join(result_lines[:3])
                print(f"  [RESULT]  {preview}")
                if len(result_lines) > 3:
                    print(f"            ... ({len(result_lines)} lines total)")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # Update message history
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    # Print action summary
    print()
    print("=" * 65)
    print("ACTIONS SUMMARY")
    print("=" * 65)
    for action in actions_taken:
        icon = "!" if action["tool"] == "scale_deployment" else ">"
        print(f"  {icon} Step {action['step']}: {action['tool']}({json.dumps(action['input'])})")
    print(f"\n  Total steps: {step}")
    print(f"  Tools called: {len(actions_taken)}")
    print(f"  Corrective actions: {sum(1 for a in actions_taken if a['tool'] == 'scale_deployment')}")

    return actions_taken


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    print()
    print("=" * 65)
    print("  EPISODE 6 - TASK 6: MULTI-TOOL AGENT ORCHESTRATION")
    print("  From Investigation to Resolution")
    print("=" * 65)
    print()
    print("Scenario: Users are complaining about high API latency.")
    print("The agent will investigate AND take corrective action.")
    print()
    print("Available Tools:")
    for tool in sre_tools:
        print(f"  - {tool['name']}: {tool['description'][:50]}...")
    print()

    # Run the agent
    actions = run_agent(
        "The API latency is very high and users are complaining about "
        "slow response times. Our SLA requires P99 under 500ms but "
        "we're seeing 3+ second responses. Please investigate the "
        "issue and fix it if you can."
    )

    # Key Learning
    print()
    print("=" * 65)
    print("KEY LEARNING")
    print("=" * 65)
    print("""
    1. Multi-tool agents follow the SAME loop pattern as single-tool:
       while stop_reason != "end_turn": execute tools, feed results

    2. The agent PLANS its investigation:
       - Checks pods -> sees high CPU
       - Gets metrics -> confirms CPU saturation
       - Checks deployment -> sees only 2 replicas, no HPA
       - Takes action -> scales to more replicas
       - Reports what it did

    3. Agents can take CORRECTIVE ACTION, not just investigate:
       - This is the foundation of autonomous operations
       - In production, add approval gates for destructive actions

    4. The agent maintains CONTEXT across all steps:
       - Results from step 1 inform decisions in step 3
       - The final report synthesizes ALL findings

    5. Tool DESCRIPTIONS drive the agent's behavior:
       - Clear descriptions = better tool selection
       - Include "Use this when..." guidance

    6. In production, add these safety measures:
       - Confirmation before destructive actions
       - Rate limiting on action tools
       - Audit logging of all actions taken
       - Rollback capabilities
    """)

    print("=" * 65)
    print("CONGRATULATIONS!")
    print("=" * 65)
    print("""
    You've completed Episode 6: Tools, Agents & MCP Servers!

    You now know how to:
    - Define tools with JSON Schema (Task 1)
    - Execute tool calls and feed results back (Task 2)
    - Build the core agent loop (Task 3)
    - Create MCP servers (Tasks 4 & 5)
    - Orchestrate multiple tools for complex problems (Task 6)

    These are the building blocks of:
    - Claude Code's architecture
    - GitHub Copilot Workspace
    - Autonomous SRE agents
    - ChatOps bots that actually DO things
    """)
    print("=" * 65)
