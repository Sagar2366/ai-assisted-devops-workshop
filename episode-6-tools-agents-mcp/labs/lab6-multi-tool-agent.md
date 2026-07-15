# Lab 6: Multi-Tool Agent — Agent with Multiple Tools

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut

> **Mission:** Build an agent that orchestrates kubectl, Docker, and Helm tools together to investigate and resolve complex DevOps scenarios.

---

## Concept: Multi-Tool Orchestration

Real incidents do not live in a single tool's domain. A deployment failure might involve:
- **kubectl:** Pod status, logs, events
- **Docker:** Image verification, registry checks
- **Helm:** Release history, values inspection

A multi-tool agent combines all of these, letting Claude decide which tool to use at each step.

**DevOps analogy:** An SRE during an incident switches between terminals — one for kubectl, one for Docker, one for monitoring. The multi-tool agent is all those terminals in one, with Claude as the SRE deciding what to check next.

---

## Step-by-Step: Build the Multi-Tool Agent

### Step 1: Define All Tool Domains

```python
import anthropic
import json

client = anthropic.Anthropic()

tools = [
    # --- Kubernetes Tools ---
    {
        "name": "kubectl_get_pods",
        "description": "List pods in a namespace with status and readiness",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {"type": "string", "description": "K8s namespace"},
                "label_selector": {"type": "string", "description": "Label filter (e.g., app=web)"}
            },
            "required": []
        }
    },
    {
        "name": "kubectl_logs",
        "description": "Get pod logs for debugging",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string"},
                "namespace": {"type": "string"},
                "tail_lines": {"type": "integer"}
            },
            "required": ["pod_name"]
        }
    },
    {
        "name": "kubectl_describe",
        "description": "Describe a K8s resource with events and conditions",
        "input_schema": {
            "type": "object",
            "properties": {
                "resource_type": {"type": "string", "enum": ["pod", "deployment", "service"]},
                "name": {"type": "string"},
                "namespace": {"type": "string"}
            },
            "required": ["resource_type", "name"]
        }
    },
    # --- Docker Tools ---
    {
        "name": "docker_inspect_image",
        "description": "Inspect a Docker image for layers, size, and config",
        "input_schema": {
            "type": "object",
            "properties": {
                "image": {"type": "string", "description": "Image name with tag"}
            },
            "required": ["image"]
        }
    },
    {
        "name": "docker_check_registry",
        "description": "Check if an image exists in the container registry",
        "input_schema": {
            "type": "object",
            "properties": {
                "image": {"type": "string", "description": "Image name with tag"},
                "registry": {"type": "string", "description": "Registry URL"}
            },
            "required": ["image"]
        }
    },
    # --- Helm Tools ---
    {
        "name": "helm_release_history",
        "description": "Get release history showing past deployments and rollbacks",
        "input_schema": {
            "type": "object",
            "properties": {
                "release_name": {"type": "string"},
                "namespace": {"type": "string"}
            },
            "required": ["release_name"]
        }
    },
    {
        "name": "helm_get_values",
        "description": "Get the current values for a Helm release",
        "input_schema": {
            "type": "object",
            "properties": {
                "release_name": {"type": "string"},
                "namespace": {"type": "string"}
            },
            "required": ["release_name"]
        }
    }
]
```

### Step 2: Implement Tool Handlers

```python
def execute_tool(name: str, args: dict) -> str:
    """Route tool calls to implementations."""
    handlers = {
        "kubectl_get_pods": _kubectl_get_pods,
        "kubectl_logs": _kubectl_logs,
        "kubectl_describe": _kubectl_describe,
        "docker_inspect_image": _docker_inspect_image,
        "docker_check_registry": _docker_check_registry,
        "helm_release_history": _helm_release_history,
        "helm_get_values": _helm_get_values,
    }
    handler = handlers.get(name)
    if not handler:
        return json.dumps({"error": f"Unknown tool: {name}"})
    return handler(**args)


def _kubectl_get_pods(namespace="default", label_selector=None):
    pods = [
        {"name": "api-server-6f8d9c", "status": "Running", "ready": "1/1", "restarts": 0},
        {"name": "api-server-7a2b3e", "status": "ImagePullBackOff", "ready": "0/1", "restarts": 0},
        {"name": "worker-5d4c8b", "status": "Running", "ready": "1/1", "restarts": 0},
    ]
    return json.dumps({"namespace": namespace, "pods": pods})


def _kubectl_logs(pod_name, namespace="default", tail_lines=50):
    logs = {
        "api-server-7a2b3e": [
            "Error: ErrImagePull",
            "Failed to pull image 'registry.internal/api-server:v2.5.0'",
            "Error: unauthorized: authentication required",
        ]
    }
    return json.dumps({"pod": pod_name, "logs": logs.get(pod_name, ["No logs available"])})


def _kubectl_describe(resource_type, name, namespace="default"):
    return json.dumps({
        "resource": f"{resource_type}/{name}",
        "events": [
            "Warning  Failed   3m  kubelet  Failed to pull image: unauthorized",
            "Warning  Failed   2m  kubelet  Error: ErrImagePull",
            "Normal   BackOff  1m  kubelet  Back-off pulling image",
        ],
        "image": "registry.internal/api-server:v2.5.0"
    })


def _docker_inspect_image(image):
    if "v2.5.0" in image:
        return json.dumps({"error": "Image not found locally", "image": image})
    return json.dumps({"image": image, "size": "145MB", "created": "2024-01-10"})


def _docker_check_registry(image, registry="registry.internal"):
    if "v2.5.0" in image:
        return json.dumps({
            "exists": False,
            "image": image,
            "registry": registry,
            "note": "Tag v2.5.0 does not exist. Latest available: v2.4.3"
        })
    return json.dumps({"exists": True, "image": image})


def _helm_release_history(release_name, namespace="default"):
    return json.dumps({
        "release": release_name,
        "history": [
            {"revision": 3, "status": "failed", "chart": "api-server-0.3.0",
             "description": "Upgrade failed: image pull error"},
            {"revision": 2, "status": "superseded", "chart": "api-server-0.2.8",
             "description": "Upgrade complete"},
            {"revision": 1, "status": "superseded", "chart": "api-server-0.2.5",
             "description": "Install complete"},
        ]
    })


def _helm_get_values(release_name, namespace="default"):
    return json.dumps({
        "release": release_name,
        "values": {
            "image": {"repository": "registry.internal/api-server", "tag": "v2.5.0"},
            "replicas": 2,
            "resources": {"limits": {"memory": "512Mi", "cpu": "500m"}}
        }
    })
```

### Step 3: The Multi-Tool Agent Loop

```python
def run_multi_tool_agent(query: str, max_iterations: int = 10) -> str:
    """Agent that orchestrates kubectl, Docker, and Helm tools."""
    system_prompt = """You are a Senior SRE investigating infrastructure issues.
You have access to kubectl, Docker, and Helm tools.
Investigate systematically:
1. Start with the broadest view (list pods, check status)
2. Drill into specifics (logs, describe, image checks)
3. Cross-reference across tools (Helm values vs actual images)
4. Provide a clear root cause and remediation steps."""

    messages = [{"role": "user", "content": query}]

    print("=" * 65)
    print(f"Multi-Tool Agent Investigation")
    print(f"Query: {query}")
    print("=" * 65)

    for i in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            final = "".join(b.text for b in response.content if b.type == "text")
            print(f"\n{'=' * 65}")
            print("INVESTIGATION COMPLETE")
            print("=" * 65)
            print(final)
            return final

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type == "text" and block.text.strip():
                    print(f"\n  [REASONING] {block.text.strip()[:120]}")
                if block.type == "tool_use":
                    print(f"  [TOOL CALL] {block.name}({json.dumps(block.input)})")
                    result = execute_tool(block.name, block.input)
                    print(f"  [RESULT]    {result[:100]}...")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})

    return "Investigation reached maximum iterations."


# Run the investigation
run_multi_tool_agent(
    "The api-server deployment is failing after a Helm upgrade. "
    "Some pods are not starting. Investigate the issue across all tools available."
)
```

---

## Solving "Why Is My Pod Crashing?" Autonomously

The real power of multi-tool agents is solving open-ended questions like "why is my pod crashing?" without human guidance. Here is how the agent approaches it:

```
Question: "Why is my pod crashing?"

Agent's autonomous investigation:
├── Step 1: kubectl_get_pods → finds pod in CrashLoopBackOff
├── Step 2: kubectl_logs → sees "Failed to pull image: unauthorized"
├── Step 3: kubectl_describe → confirms ErrImagePull, reads image tag
├── Step 4: docker_check_registry → tag v2.5.0 does not exist!
├── Step 5: helm_release_history → last upgrade attempted v2.5.0
├── Step 6: helm_get_values → confirms the bad tag in values
└── Conclusion: Image tag typo in Helm values. Fix: use v2.4.3 or rollback.
```

The agent decides the investigation path at each step based on accumulated evidence. No human intervention needed between steps.

---

## Expected Investigation Flow

The agent will typically:
1. `kubectl_get_pods` — See the ImagePullBackOff pod
2. `kubectl_describe` — See the image pull error
3. `docker_check_registry` — Discover tag v2.5.0 does not exist
4. `helm_release_history` — See the failed upgrade
5. `helm_get_values` — Confirm the values reference v2.5.0
6. Synthesize: "Root cause is a non-existent image tag in the Helm values. Remediation: rollback to revision 2 or fix the tag to v2.4.3."

---

## What Success Looks Like

- The agent uses tools from multiple domains (K8s + Docker + Helm)
- It answers "why is my pod crashing?" without human guidance between steps
- Investigation is systematic — broad to specific
- Cross-tool correlation catches the root cause
- Claude decides which tool to call at each step based on prior results
- The final answer includes both diagnosis AND remediation steps
- The agent stops on its own when it has a complete answer

---

## Key Takeaway

Multi-tool agents mirror how experienced SREs work — they do not investigate in a single tool's silo. By combining kubectl, Docker, and Helm tools, Claude can trace a problem from symptom (pod not starting) through infrastructure (image pull error) to root cause (wrong tag in Helm values). The agent loop handles the orchestration; your job is defining the right tools with clear descriptions so the model can select them intelligently.

**Workshop complete!** You have progressed from basic function calling to a full multi-tool DevOps agent.
