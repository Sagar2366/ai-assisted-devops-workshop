# Lab 1: Function Calling — Define Tools the LLM Can Call

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

> **Mission:** Learn how to define tool schemas that tell Claude exactly what actions it can take — the first step toward building an autonomous DevOps agent.

---

## Concept: What Is Function Calling?

Think of function calling like giving an SRE a **runbook catalog**. The SRE does not memorize every system command — they know which runbooks exist, what inputs each needs, and what outputs they produce. Similarly, we give Claude a catalog of tools (JSON schemas) so it knows:

1. **What tools exist** (name + description)
2. **What inputs each needs** (parameters with types)
3. **When to use each tool** (description guides selection)

Claude never executes tools directly — it returns a structured request saying "I want to call this tool with these arguments." Your code handles the actual execution.

---

## The Anatomy of a Tool Definition

```python
tool = {
    "name": "get_pod_status",              # Unique identifier
    "description": "Get the status of a Kubernetes pod in a given namespace",
    "input_schema": {
        "type": "object",
        "properties": {
            "pod_name": {
                "type": "string",
                "description": "Name of the pod to check"
            },
            "namespace": {
                "type": "string",
                "description": "Kubernetes namespace (default: 'default')"
            }
        },
        "required": ["pod_name"]           # Only pod_name is mandatory
    }
}
```

**DevOps analogy:** This is like the header of a runbook — it states the procedure name, what inputs it needs, and what it does. The body (implementation) comes later.

---

## Step-by-Step: Define Your First DevOps Tools

### Step 1: Define a Pod Status Tool

```python
import anthropic
import json

client = anthropic.Anthropic()

# Define tools Claude can use
tools = [
    {
        "name": "get_pod_status",
        "description": "Get the current status of a Kubernetes pod including phase, conditions, and container states",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod_name": {
                    "type": "string",
                    "description": "Name of the pod to check"
                },
                "namespace": {
                    "type": "string",
                    "description": "Kubernetes namespace (default: 'default')"
                }
            },
            "required": ["pod_name"]
        }
    },
    {
        "name": "check_deployment",
        "description": "Check the status of a Kubernetes deployment including replica counts and rollout status",
        "input_schema": {
            "type": "object",
            "properties": {
                "deployment_name": {
                    "type": "string",
                    "description": "Name of the deployment"
                },
                "namespace": {
                    "type": "string",
                    "description": "Kubernetes namespace (default: 'default')"
                }
            },
            "required": ["deployment_name"]
        }
    }
]
```

### Step 2: Send a Message With Tools

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[
        {
            "role": "user",
            "content": "Check if the payment-service pod is running in the production namespace"
        }
    ]
)

# Examine what Claude returns
for block in response.content:
    if block.type == "tool_use":
        print(f"Tool: {block.name}")
        print(f"Input: {json.dumps(block.input, indent=2)}")
    elif block.type == "text":
        print(f"Text: {block.text}")

print(f"\nStop reason: {response.stop_reason}")
```

### Step 3: Observe the Response

When Claude decides a tool is needed, `stop_reason` will be `"tool_use"` and the response will contain a `tool_use` block:

```
Tool: get_pod_status
Input: {
  "pod_name": "payment-service",
  "namespace": "production"
}

Stop reason: tool_use
```

Claude chose the right tool and extracted the right parameters from the natural language query.

---

## Experiment: Add More Tools

Try adding these tools and ask Claude questions that require them:

```python
additional_tools = [
    {
        "name": "get_pod_logs",
        "description": "Retrieve recent logs from a Kubernetes pod",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string", "description": "Pod name"},
                "namespace": {"type": "string", "description": "Namespace"},
                "tail_lines": {"type": "integer", "description": "Number of recent lines (default: 50)"}
            },
            "required": ["pod_name"]
        }
    },
    {
        "name": "scale_deployment",
        "description": "Scale a Kubernetes deployment to a specified number of replicas",
        "input_schema": {
            "type": "object",
            "properties": {
                "deployment_name": {"type": "string", "description": "Deployment name"},
                "namespace": {"type": "string", "description": "Namespace"},
                "replicas": {"type": "integer", "description": "Desired replica count"}
            },
            "required": ["deployment_name", "replicas"]
        }
    }
]
```

---

## What Success Looks Like

- Claude returns `stop_reason: "tool_use"` when a tool is needed
- The `tool_use` block contains the correct tool name
- Parameters are extracted accurately from natural language
- Claude picks the right tool when multiple are available

---

## Key Takeaway

Function calling is the bridge between natural language and structured actions. By defining clear tool schemas with good descriptions, you give Claude the vocabulary to request specific actions. The model never runs the tools — it produces a structured request that your code fulfills.

**Next:** [Lab 2: Tool Execution](lab2-tool-execution.md)
