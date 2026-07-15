# Lab 3: Agent Loop — Think, Act, Observe

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

> **Mission:** Build the core agent loop that lets Claude repeatedly think, take actions, and observe results until a problem is fully resolved.

---

## Concept: What Makes an Agent?

An agent is not a single API call — it is a **loop**. The difference between a chatbot and an agent is persistence: an agent keeps working until the job is done.

**DevOps analogy:** An SRE working an incident does not stop after one command. They:
1. **Think:** "The pod is crashing. Let me check logs."
2. **Act:** Run `kubectl logs`
3. **Observe:** "OOMKilled. Memory limit too low."
4. **Think:** "I should check the resource limits..."
5. **Act:** Run `kubectl describe pod`
6. **Observe:** "Memory limit is 128Mi but the app needs 512Mi."
7. **Think:** "I have enough information to provide a recommendation."

The agent loop is this same cycle, automated.

---

## The Agent Loop Pattern

```
while not done:
    response = claude.think(messages)

    if response.stop_reason == "end_turn":
        done = True  # Claude has finished
    elif response.stop_reason == "tool_use":
        results = execute_tools(response)
        messages.append(assistant_message)
        messages.append(tool_results)
```

---

## Step-by-Step: Build the Loop

### Step 1: Define Tools and Implementations

```python
import anthropic
import json

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_pod_status",
        "description": "Get current pod status including phase and restarts",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string", "description": "Pod name"},
                "namespace": {"type": "string", "description": "Namespace"}
            },
            "required": ["pod_name"]
        }
    },
    {
        "name": "get_pod_logs",
        "description": "Get recent logs from a pod",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string", "description": "Pod name"},
                "namespace": {"type": "string", "description": "Namespace"},
                "tail_lines": {"type": "integer", "description": "Lines to retrieve"}
            },
            "required": ["pod_name"]
        }
    },
    {
        "name": "describe_pod",
        "description": "Get detailed pod description including events, resource limits, and conditions",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string", "description": "Pod name"},
                "namespace": {"type": "string", "description": "Namespace"}
            },
            "required": ["pod_name"]
        }
    }
]


def execute_tool(name: str, inputs: dict) -> str:
    """Execute tool and return result."""
    if name == "get_pod_status":
        return json.dumps({
            "pod": inputs["pod_name"],
            "status": "CrashLoopBackOff",
            "ready": "0/1",
            "restarts": 8,
            "last_restart": "2 minutes ago"
        })
    elif name == "get_pod_logs":
        return json.dumps({
            "pod": inputs["pod_name"],
            "logs": [
                "2024-01-15T10:23:01Z Starting application...",
                "2024-01-15T10:23:02Z Connecting to database...",
                "2024-01-15T10:23:03Z ERROR: java.lang.OutOfMemoryError: Java heap space",
                "2024-01-15T10:23:03Z FATAL: Application terminated"
            ]
        })
    elif name == "describe_pod":
        return json.dumps({
            "pod": inputs["pod_name"],
            "containers": [{
                "name": "main",
                "image": "payment-service:v2.3.1",
                "resources": {"limits": {"memory": "128Mi", "cpu": "250m"}},
                "last_state": {"terminated": {"reason": "OOMKilled", "exit_code": 137}}
            }],
            "events": [
                "Warning  OOMKilled  2m  kubelet  Container exceeded memory limit",
                "Normal   Pulling    1m  kubelet  Pulling image payment-service:v2.3.1",
                "Warning  BackOff    30s kubelet  Back-off restarting failed container"
            ]
        })
    return json.dumps({"error": f"Unknown tool: {name}"})
```

### Step 2: The Agent Loop

```python
def run_agent(user_query: str, max_iterations: int = 10) -> str:
    """Run the agent loop until Claude finishes or we hit max iterations."""
    messages = [{"role": "user", "content": user_query}]

    print(f"{'=' * 65}")
    print(f"Agent Query: {user_query}")
    print(f"{'=' * 65}\n")

    for i in range(max_iterations):
        print(f"{'-' * 65}")
        print(f"Iteration {i + 1}")
        print(f"{'-' * 65}")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        # Check if Claude is done
        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text
            print(f"\n[AGENT COMPLETE]\n{final_text}")
            return final_text

        # Process tool calls
        if response.stop_reason == "tool_use":
            # Append assistant response
            messages.append({"role": "assistant", "content": response.content})

            # Execute tools
            tool_results = []
            for block in response.content:
                if block.type == "text" and block.text:
                    print(f"  [THINK] {block.text}")
                if block.type == "tool_use":
                    print(f"  [ACT]   {block.name}({json.dumps(block.input)})")
                    result = execute_tool(block.name, block.input)
                    print(f"  [OBSERVE] {result[:100]}...")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})

    return "Max iterations reached without resolution."
```

### Step 3: Run It

```python
result = run_agent(
    "The payment-service pod keeps crashing. Investigate and tell me the root cause and fix."
)
```

---

## Expected Output Flow

```
=================================================================
Agent Query: The payment-service pod keeps crashing...
=================================================================

-----------------------------------------------------------------
Iteration 1
-----------------------------------------------------------------
  [THINK] Let me check the pod status first.
  [ACT]   get_pod_status({"pod_name": "payment-service"})
  [OBSERVE] {"pod": "payment-service", "status": "CrashLoopBackOff"...

-----------------------------------------------------------------
Iteration 2
-----------------------------------------------------------------
  [THINK] CrashLoopBackOff with 8 restarts. Let me check logs.
  [ACT]   get_pod_logs({"pod_name": "payment-service"})
  [OBSERVE] {"logs": [..., "ERROR: OutOfMemoryError"...

-----------------------------------------------------------------
Iteration 3
-----------------------------------------------------------------
  [THINK] OOM error. Let me check resource limits.
  [ACT]   describe_pod({"pod_name": "payment-service"})
  [OBSERVE] {"containers": [{"resources": {"limits": {"memory": "128Mi"}}...

-----------------------------------------------------------------
Iteration 4
-----------------------------------------------------------------

[AGENT COMPLETE]
Root Cause: The payment-service pod is being OOMKilled because...
Fix: Increase the memory limit from 128Mi to at least 512Mi...
```

---

## What Success Looks Like

- The agent iterates multiple times, gathering information progressively
- Each iteration shows the think-act-observe pattern
- Claude stops on its own when it has enough information
- The final answer synthesizes all observations into a diagnosis

---

## Key Takeaway

The agent loop is deceptively simple — it is just a while loop with an LLM call inside. The power comes from Claude's ability to decide what to investigate next based on what it has already learned. Each iteration adds context, building toward a complete diagnosis just like an experienced SRE would.

**Next:** [Lab 4: MCP Introduction](lab4-mcp-intro.md)
