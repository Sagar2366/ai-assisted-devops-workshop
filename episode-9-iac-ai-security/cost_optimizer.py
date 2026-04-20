"""
Episode 9: Infrastructure as Code + AI & Security Scanning
Tool: AI Cloud Cost Optimizer

Analyzes Kubernetes resource usage and suggests cost savings.
Examines pod resource requests/limits vs actual usage and recommends right-sizing.

Author: Sagar Utekar
Prerequisites:
    - Anthropic API key (set ANTHROPIC_API_KEY env var)
    - pip install anthropic
    - kubectl configured and cluster accessible
    - metrics-server installed (optional, for actual usage data)
"""
import anthropic
import subprocess
import json

client = anthropic.Anthropic()


def get_resource_usage() -> str:
    """Get current resource allocation vs usage."""
    sections = []

    # Pod resource requests vs actual usage
    pods_json = subprocess.run(
        "kubectl get pods -A -o json",
        shell=True, capture_output=True, text=True, timeout=30
    ).stdout

    try:
        pods = json.loads(pods_json)
        resource_data = []
        for pod in pods.get("items", []):
            ns = pod["metadata"]["namespace"]
            if ns.startswith("kube-"):
                continue
            name = pod["metadata"]["name"]
            for container in pod["spec"].get("containers", []):
                requests = container.get("resources", {}).get("requests", {})
                limits = container.get("resources", {}).get("limits", {})
                resource_data.append({
                    "pod": name,
                    "namespace": ns,
                    "container": container["name"],
                    "cpu_request": requests.get("cpu", "not set"),
                    "cpu_limit": limits.get("cpu", "not set"),
                    "memory_request": requests.get("memory", "not set"),
                    "memory_limit": limits.get("memory", "not set"),
                })
        sections.append(f"Resource Allocations:\n{json.dumps(resource_data, indent=2)}")
    except json.JSONDecodeError:
        sections.append("Could not parse pod data")

    # Node usage (if metrics-server available)
    top_result = subprocess.run(
        "kubectl top nodes 2>/dev/null || echo 'metrics-server not available'",
        shell=True, capture_output=True, text=True, timeout=30
    )
    sections.append(f"Node Usage:\n{top_result.stdout}")

    return "\n\n".join(sections)


def optimize():
    """AI cost optimization analysis."""
    usage = get_resource_usage()

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="""You are a cloud cost optimization expert for Kubernetes.

Analyze resource allocation and suggest:
1. Over-provisioned resources (requests >> actual usage)
2. Right-sizing recommendations with exact values
3. Candidates for spot/preemptible instances
4. Unused or idle resources
5. Estimated monthly savings for each recommendation

Be specific with numbers. Show before -> after.""",
        messages=[{
            "role": "user",
            "content": f"Analyze this cluster's resource usage and suggest cost optimizations:\n\n{usage}"
        }]
    )

    print(response.content[0].text)


if __name__ == "__main__":
    print("Analyzing cluster costs...")
    optimize()
