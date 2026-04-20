"""
Episode 5: Build a DevOps Copilot
AI-Assisted DevOps Workshop

DevOps Copilot -- Main agent engine.
Autonomous K8s diagnosis and remediation using the SRE Diagnostic Ladder.

Author: Sagar Utekar

Prerequisites:
    - Python 3.10+
    - anthropic Python SDK (pip install anthropic)
    - ANTHROPIC_API_KEY environment variable set
    - kubectl configured and pointing to your cluster
    - k8s_tools.py in the same directory or parent tools/ directory
"""
import anthropic
import json
import sys
import os

# Support both flat layout (all files in same dir) and nested layout (tools/k8s_tools.py)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append('..')
from k8s_tools import K8sTools

client = anthropic.Anthropic()
k8s = K8sTools(auto_approve_restricted=True)  # For demo; in prod, set False

SYSTEM_PROMPT = """You are the DevOps Copilot — an autonomous SRE agent built by a CNCF Ambassador and Kubestronaut.

## Your Mission
Diagnose and resolve Kubernetes cluster issues autonomously. You think like a senior SRE:
1. Start broad (cluster health) then narrow down
2. Always check data before drawing conclusions
3. Explain your reasoning — teams learn from your investigation
4. When you find an issue, fix it if safe, or recommend the fix

## Investigation Methodology
Follow the SRE diagnostic flow:
1. GET THE BIG PICTURE — cluster health, node status, pod overview
2. IDENTIFY SYMPTOMS — which pods are unhealthy, what errors exist
3. GATHER EVIDENCE — logs, events, describe output for affected resources
4. FORM HYPOTHESIS — based on evidence, what's the root cause
5. VERIFY — check if hypothesis explains ALL symptoms
6. ACT — apply fix if within permissions, or recommend

## Output Style
- Be direct, no fluff
- Include exact commands you ran
- Show evidence for your conclusions
- Rate confidence: HIGH / MEDIUM / LOW
- If multiple issues exist, prioritize by severity

## Safety
- Read-only commands: always allowed
- Scale/rollback: allowed (max 10 replicas)
- Delete/exec/apply: NEVER — suggest to the human instead"""

# Tool definitions for Claude API
TOOLS = [
    {
        "name": "get_cluster_health",
        "description": "Get comprehensive cluster health: nodes, problem pods, warning events, deployments. ALWAYS use this first.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "get_pods",
        "description": "List pods with status. Use all_namespaces=true for cluster-wide view.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {"type": "string", "default": "default"},
                "all_namespaces": {"type": "boolean", "default": False}
            }
        }
    },
    {
        "name": "get_pod_logs",
        "description": "Get logs from a pod. Set previous=true for crashed container logs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod": {"type": "string"},
                "namespace": {"type": "string", "default": "default"},
                "lines": {"type": "integer", "default": 50},
                "previous": {"type": "boolean", "default": False}
            },
            "required": ["pod"]
        }
    },
    {
        "name": "describe_pod",
        "description": "Get detailed pod info: events, conditions, container status, resource usage.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod": {"type": "string"},
                "namespace": {"type": "string", "default": "default"}
            },
            "required": ["pod"]
        }
    },
    {
        "name": "get_events",
        "description": "Get Kubernetes events — scheduling failures, image pulls, health check failures.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {"type": "string", "default": "default"},
                "all_namespaces": {"type": "boolean", "default": False}
            }
        }
    },
    {
        "name": "get_deployments",
        "description": "List deployments with replica counts and status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {"type": "string", "default": "default"},
                "all_namespaces": {"type": "boolean", "default": False}
            }
        }
    },
    {
        "name": "kubectl",
        "description": "Run any read-only kubectl command. Use for commands not covered by other tools.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "kubectl command without 'kubectl' prefix"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "scale_deployment",
        "description": "Scale a deployment. Safety limit: max 10 replicas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "replicas": {"type": "integer"},
                "namespace": {"type": "string", "default": "default"}
            },
            "required": ["name", "replicas"]
        }
    },
    {
        "name": "rollback_deployment",
        "description": "Rollback a deployment to its previous version.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "namespace": {"type": "string", "default": "default"}
            },
            "required": ["name"]
        }
    }
]


def execute_tool(name: str, inputs: dict) -> str:
    """Route tool calls to K8sTools."""
    method = getattr(k8s, name, None)
    if method:
        return method(**inputs)
    return f"Unknown tool: {name}"


def run_copilot(task: str, max_steps: int = 15):
    """Run the DevOps Copilot."""
    messages = [{"role": "user", "content": task}]
    step = 0

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    DEVOPS COPILOT                            ║
║                                                              ║
║  Task: {task[:50]:<50s}  ║
╚══════════════════════════════════════════════════════════════╝
""")

    while step < max_steps:
        step += 1
        print(f"┌─ Step {step}/{max_steps} ─────────────────────────────────────────┐")

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "text" and block.text:
                    print(f"│ THINKING: {block.text[:80]}")
                if block.type == "tool_use":
                    print(f"│ ACTION:   {block.name}({json.dumps(block.input)[:60]})")
                    result = execute_tool(block.name, block.input)
                    # Show truncated result
                    lines = result.strip().split('\n')
                    preview = '\n'.join(lines[:5])
                    if len(lines) > 5:
                        preview += f"\n  ... ({len(lines)-5} more lines)"
                    print(f"│ RESULT:   {preview}")
                    print(f"│")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            # Final answer
            print(f"└──────────────────────────────────────────────────────────┘")
            print(f"\n{'='*60}")
            print("COPILOT REPORT")
            print(f"{'='*60}")
            for block in response.content:
                if hasattr(block, "text"):
                    print(block.text)
            print(f"\n[Completed in {step} steps]")

            # Print audit log
            print(f"\n{'='*60}")
            print("AUDIT LOG")
            print(f"{'='*60}")
            for entry in k8s.get_audit_log():
                print(f"  [{entry['timestamp']}] {entry['action']}: {entry['command']}")

            return

        print(f"└──────────────────────────────────────────────────────────┘\n")

    print(f"\n[Agent reached max steps ({max_steps})]")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "Investigate the cluster. Find all unhealthy pods, diagnose each issue, and fix what you can."

    run_copilot(task)
