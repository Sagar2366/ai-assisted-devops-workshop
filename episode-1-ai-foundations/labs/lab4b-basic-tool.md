# Lab 4b: Basic Tool Use — The Core of an Agent

> **Mission:** Give the model a tool and watch it DECIDE to use it on its own — this is what separates a chatbot from an agent.

---

## The Concept

A model without tools can only advise. Tools give it hands.

```
  +----------+
  |  MODEL   |---> check_pod_status(namespace)
  |          |---> get_pod_logs(pod)
  | decides  |---> restart_deployment(name)
  |  WHEN    |---> query_prometheus(query)
  | to call  |---> send_slack_message(channel)
  +----------+
```

You define tools as JSON schemas. The model sees your question, sees the available tools, and **decides on its own** whether to call one. You don't tell it "use this tool" — it figures it out.

```
  You: "Are my pods healthy in monitoring?"
       |
       v
  Model sees tools --> decides to call check_pod_status
       |
       v
  [TOOL CALLED] check_pod_status(namespace=monitoring)
  [TOOL RESULT] --> pod table with alertmanager in CrashLoopBackOff
       |
       v
  Model reads result --> reports: "alertmanager-0 is unhealthy"
```

---

## What You'll Build

A simulated `check_pod_status` tool that returns fake pod data. Ask the model about pod health — it decides to call the tool, gets the result, and reports which pods are unhealthy.

---

## Step 1: Define the Tool Function

This simulates what a real Kubernetes API call would return.

```python
def check_pod_status(namespace="default"):
    pods = {
        "monitoring": [
            {"name": "prometheus-0", "status": "Running", "restarts": 0},
            {"name": "grafana-5d4f8b6c5-x2k9m", "status": "Running", "restarts": 0},
            {"name": "alertmanager-0", "status": "CrashLoopBackOff", "restarts": 8},
        ],
        "default": [
            {"name": "nginx-7d4f8b6c5-abc12", "status": "Running", "restarts": 0},
        ]
    }
    return pods.get(namespace, [])
```

---

## Step 2: Define the Tool Schema

Tell the model what the tool does and what parameters it accepts.

**Anthropic:**
```python
tools = [
    {
        "name": "check_pod_status",
        "description": "Check the status of pods in a Kubernetes namespace",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "The Kubernetes namespace to check"
                }
            },
            "required": ["namespace"]
        }
    }
]
```

---

## Step 3: Send the Query with Tools

**Anthropic:**
```python
message = client.messages.create(
    model="claude-sonnet-4-6-latest",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Are my pods healthy in the monitoring namespace?"}]
)
```

---

## Step 4: Handle the Tool Call

The model doesn't call the function directly — it tells you it wants to call it. You execute the function and send the result back.

**Anthropic:**
```python
# Model responds with stop_reason="tool_use"
# Extract the tool call, run the function, send result back
tool_block = next(b for b in message.content if b.type == "tool_use")
result = check_pod_status(**tool_block.input)

# Send the result back to the model
followup = client.messages.create(
    model="claude-sonnet-4-6-latest",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "Are my pods healthy in the monitoring namespace?"},
        {"role": "assistant", "content": message.content},
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_block.id, "content": str(result)}]}
    ]
)
print(followup.content[0].text)
```

---

## The Flow (All Providers)

Every provider has different syntax, but the flow is always:

1. **Define** the tool (name, description, parameters as JSON schema)
2. **Send** the query with tools attached
3. **Model decides** to call the tool (or not)
4. **You execute** the function locally
5. **Send the result back** to the model
6. **Model summarizes** the result for the user

---

## Run It

```bash
python3 demos/{your-provider}/task4b_basic_tool.py
```

---

## What Success Looks Like

The model:
1. Sees your question about pod health
2. Decides to call `check_pod_status(namespace="monitoring")`
3. Gets back the pod table
4. Reports: "alertmanager-0 is in CrashLoopBackOff with 8 restarts"

You never told it to use the tool. It decided on its own.

---

## Key Takeaway

The model DECIDED to use the tool — you never told it to. That decision-making is the core of an agent. In Lab 4 we saw the model can't access live systems — tools fix that. Episode 4 goes deep: multiple tools, error handling, parallel execution.

---

Next: [Lab 5: Conversation History](lab5-conversation-history.md)
