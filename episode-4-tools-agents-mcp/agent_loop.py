"""
Episode 4: Building Tools, Agents & MCP Servers
File: agent_loop.py — Core Agent Loop + Autonomous SRE Agent

Author: Sagar Utekar
Prerequisites: Episodes 1-3 completed; kind cluster running; Claude API key working;
              Python packages: anthropic
              k8s_tools.py and tool_definitions.py in the same directory

The agent loop pattern: Think -> Act -> Observe -> Repeat until done.
This is the pattern you will use for ALL agents in this workshop.
"""
import anthropic
import json
from k8s_tools import (
    kubectl, get_pod_logs, get_cluster_health,
    query_prometheus, scale_deployment, rollback_deployment,
)
from tool_definitions import TOOL_DEFINITIONS

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an autonomous SRE agent responsible for diagnosing and resolving Kubernetes cluster issues.

## Your Approach:
1. ALWAYS start with get_cluster_health to understand the overall state
2. Investigate specific issues using kubectl and get_pod_logs
3. Check metrics with query_prometheus if needed
4. When you've identified the root cause, explain it clearly
5. If a fix is needed and within your permissions, apply it (scale/rollback)
6. Verify the fix worked by checking cluster state again

## Safety Rules:
- You can only READ cluster state (get, describe, logs, top)
- You can SCALE deployments (max 10 replicas)
- You can ROLLBACK deployments to previous version
- You CANNOT delete, exec, or apply arbitrary manifests
- Always explain what you're doing and why before each action

## Communication Style:
- Be direct and concise
- Show your reasoning
- Include the exact commands you ran
- State confidence level: HIGH / MEDIUM / LOW"""


def execute_tool(name: str, input_data: dict) -> str:
    """Route a tool call to the right function."""
    tool_map = {
        "kubectl": kubectl,
        "get_pod_logs": get_pod_logs,
        "get_cluster_health": get_cluster_health,
        "query_prometheus": query_prometheus,
        "scale_deployment": scale_deployment,
        "rollback_deployment": rollback_deployment,
    }

    if name not in tool_map:
        return json.dumps({"error": f"Unknown tool: {name}"})

    result = tool_map[name](**input_data)
    return json.dumps(result, default=str)


def run_agent(task: str, max_steps: int = 10, verbose: bool = True):
    """
    Run the SRE agent on a task.
    The agent will autonomously use tools until it reaches a conclusion.
    """
    messages = [{"role": "user", "content": task}]
    step = 0

    if verbose:
        print(f"\n{'='*70}")
        print(f"SRE AGENT - Task: {task}")
        print(f"{'='*70}\n")

    while step < max_steps:
        step += 1
        if verbose:
            print(f"--- Step {step}/{max_steps} ---")

        # Call the LLM
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages
        )

        # Process the response
        if response.stop_reason == "tool_use":
            tool_results = []
            assistant_content = response.content

            for block in response.content:
                if block.type == "text" and block.text and verbose:
                    print(f"THINKING: {block.text}\n")

                if block.type == "tool_use":
                    if verbose:
                        print(f"ACTION: {block.name}({json.dumps(block.input, indent=2)})")

                    result = execute_tool(block.name, block.input)

                    if verbose:
                        # Show truncated result
                        preview = result[:300] + "..." if len(result) > 300 else result
                        print(f"RESULT: {preview}\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Feed results back
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})

        else:
            # Agent is done
            final_response = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_response += block.text

            if verbose:
                print(f"\n{'='*70}")
                print(f"AGENT CONCLUSION (after {step} steps):")
                print(f"{'='*70}")
                print(final_response)

            return {
                "conclusion": final_response,
                "steps": step,
                "messages": messages
            }

    return {
        "conclusion": "Agent reached maximum steps without conclusion.",
        "steps": step,
        "messages": messages
    }


if __name__ == "__main__":
    # Demo 1: General health check
    run_agent("Check the overall health of the cluster and report any issues.")

    # Demo 2: Specific investigation
    # run_agent("Investigate why pods in the default namespace are having issues. Check logs and events.")
