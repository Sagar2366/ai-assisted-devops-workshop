# Lab 2: Tool Execution — Execute Tool Calls and Return Results

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

> **Mission:** Learn how to execute the tool calls Claude requests and feed results back so the model can reason about them.

---

## Concept: The Tool Execution Cycle

When Claude returns a `tool_use` block, the conversation is paused mid-thought. Claude is saying: "I need this information before I can answer." Your job is to:

1. **Extract** the tool name and inputs from the response
2. **Execute** the actual function (kubectl, API call, etc.)
3. **Return** the result in a `tool_result` message
4. **Let Claude continue** reasoning with the new information

**DevOps analogy:** This is like an SRE running a diagnostic command during an incident. They think "I need pod status," run `kubectl get pod`, read the output, and continue their investigation.

---

## Step-by-Step: Execute and Return

### Step 1: Define Your Tool Implementations

```python
import anthropic
import json

client = anthropic.Anthropic()

# Simulated tool implementations (replace with real kubectl in production)
def get_pod_status(pod_name: str, namespace: str = "default") -> str:
    """Simulate kubectl get pod."""
    # In production: subprocess.run(["kubectl", "get", "pod", pod_name, "-n", namespace, "-o", "json"])
    mock_data = {
        "payment-service": {
            "status": "Running",
            "ready": "1/1",
            "restarts": 0,
            "age": "3d",
            "node": "worker-node-02"
        },
        "auth-service": {
            "status": "CrashLoopBackOff",
            "ready": "0/1",
            "restarts": 15,
            "age": "1h",
            "node": "worker-node-01"
        }
    }
    pod = mock_data.get(pod_name, {"status": "NotFound"})
    return json.dumps({"pod": pod_name, "namespace": namespace, **pod})


def check_deployment(deployment_name: str, namespace: str = "default") -> str:
    """Simulate kubectl get deployment."""
    mock_data = {
        "payment-service": {
            "desired": 3, "current": 3, "ready": 3,
            "up_to_date": 3, "available": 3
        },
        "auth-service": {
            "desired": 2, "current": 2, "ready": 0,
            "up_to_date": 2, "available": 0
        }
    }
    dep = mock_data.get(deployment_name, {"error": "Deployment not found"})
    return json.dumps({"deployment": deployment_name, "namespace": namespace, **dep})
```

### Step 2: Build the Tool Dispatcher

```python
def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Dispatch tool calls to their implementations."""
    dispatch = {
        "get_pod_status": get_pod_status,
        "check_deployment": check_deployment,
    }

    if tool_name not in dispatch:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    # Call the function with the provided inputs
    return dispatch[tool_name](**tool_input)
```

### Step 3: Complete the Round Trip

```python
tools = [
    {
        "name": "get_pod_status",
        "description": "Get the current status of a Kubernetes pod",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string", "description": "Pod name"},
                "namespace": {"type": "string", "description": "Namespace (default: 'default')"}
            },
            "required": ["pod_name"]
        }
    },
    {
        "name": "check_deployment",
        "description": "Check deployment status including replica counts",
        "input_schema": {
            "type": "object",
            "properties": {
                "deployment_name": {"type": "string", "description": "Deployment name"},
                "namespace": {"type": "string", "description": "Namespace (default: 'default')"}
            },
            "required": ["deployment_name"]
        }
    }
]

# Initial request
messages = [{"role": "user", "content": "Is the auth-service healthy?"}]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=messages
)

# Process tool calls
if response.stop_reason == "tool_use":
    # Append assistant's response (contains the tool_use block)
    messages.append({"role": "assistant", "content": response.content})

    # Execute each tool call and collect results
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            print(f"Executing: {block.name}({block.input})")
            result = execute_tool(block.name, block.input)
            print(f"Result: {result}\n")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            })

    # Send results back to Claude
    messages.append({"role": "user", "content": tool_results})

    # Get Claude's final answer
    final_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    for block in final_response.content:
        if block.type == "text":
            print(f"Claude's Analysis:\n{block.text}")
```

---

## Understanding the Message Flow

```
User: "Is the auth-service healthy?"
    |
    v
Claude: tool_use(get_pod_status, {pod_name: "auth-service"})
    |
    v
Your Code: executes get_pod_status("auth-service")
    |        returns: {"status": "CrashLoopBackOff", "restarts": 15, ...}
    v
Claude: "The auth-service is NOT healthy. It's in CrashLoopBackOff
         with 15 restarts in the last hour..."
```

---

## Handling Errors Gracefully

```python
def execute_tool_safe(tool_name: str, tool_input: dict) -> str:
    """Execute with error handling."""
    try:
        result = execute_tool(tool_name, tool_input)
        return result
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "tool": tool_name,
            "suggestion": "Check if the resource exists and you have permissions"
        })
```

When you return an error, Claude adapts its response — it might try a different tool, ask for clarification, or explain what went wrong.

---

## What Success Looks Like

- Tool calls are dispatched to the correct implementation
- Results are formatted as strings and returned via `tool_result`
- Claude uses the results to form an informed, accurate answer
- Error cases are handled gracefully

---

## Key Takeaway

Tool execution is the handshake between AI reasoning and real-world actions. Claude decides what information it needs; your code provides it. The `tool_use_id` links each result to its request, ensuring Claude can track multiple parallel tool calls. Always return results — even errors — so Claude can continue reasoning.

**Next:** [Lab 3: Agent Loop](lab3-agent-loop.md)
