"""
Episode 4: Building Tools, Agents & MCP Servers
File: k8s_tools.py — Kubernetes Tools for AI Agents

Author: Sagar Utekar
Prerequisites: Episodes 1-3 completed; kind cluster running; kubectl configured;
              Python packages: anthropic, requests

Each tool = one capability the agent can use.
Includes 6 tool functions with safety guardrails:
  1. kubectl         — Execute a read-only kubectl command safely
  2. get_pod_logs    — Fetch logs from a specific pod
  3. get_cluster_health — Comprehensive cluster health snapshot
  4. query_prometheus — Execute a PromQL query
  5. scale_deployment — Scale with safety limits (max 10 replicas)
  6. rollback_deployment — Rollback to previous version
"""
import subprocess
import json
from typing import Optional


def kubectl(command: str, namespace: Optional[str] = None, timeout: int = 30) -> dict:
    """Execute a kubectl command safely."""
    # Safety: block dangerous commands
    dangerous = ["delete", "exec", "apply", "patch", "replace", "drain", "cordon", "taint"]
    first_word = command.strip().split()[0] if command.strip() else ""

    if first_word in dangerous:
        return {
            "success": False,
            "error": f"Blocked: '{first_word}' is a restricted command. Use read-only commands.",
            "command": f"kubectl {command}"
        }

    full_cmd = f"kubectl {command}"
    if namespace:
        full_cmd += f" -n {namespace}"

    try:
        result = subprocess.run(
            full_cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "command": full_cmd
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timed out", "command": full_cmd}


def get_pod_logs(pod: str, namespace: str = "default", lines: int = 50, previous: bool = False) -> dict:
    """Get logs from a specific pod."""
    cmd = f"kubectl logs {pod} -n {namespace} --tail={lines}"
    if previous:
        cmd += " --previous"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "logs": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timed out fetching logs"}


def get_cluster_health() -> dict:
    """Get a comprehensive cluster health snapshot."""
    health = {}

    checks = {
        "nodes": "kubectl get nodes -o json",
        "pods_not_running": "kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded -o json",
        "events_warnings": "kubectl get events -A --field-selector type=Warning --sort-by='.lastTimestamp' -o json",
        "resource_usage": "kubectl top nodes --no-headers"
    }

    for name, cmd in checks.items():
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if "json" in cmd:
                try:
                    health[name] = json.loads(result.stdout)
                except json.JSONDecodeError:
                    health[name] = result.stdout
            else:
                health[name] = result.stdout
        except subprocess.TimeoutExpired:
            health[name] = {"error": "timed out"}

    return health


def query_prometheus(query: str, prometheus_url: str = "http://localhost:9090") -> dict:
    """Execute a PromQL query."""
    import requests
    try:
        resp = requests.get(f"{prometheus_url}/api/v1/query", params={"query": query}, timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def scale_deployment(name: str, replicas: int, namespace: str = "default") -> dict:
    """Scale a deployment (with safety limits)."""
    if replicas > 10:
        return {"success": False, "error": "Safety limit: max 10 replicas. Override requires approval."}
    if replicas < 0:
        return {"success": False, "error": "Replicas cannot be negative."}

    cmd = f"kubectl scale deployment/{name} --replicas={replicas} -n {namespace}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timed out"}


def rollback_deployment(name: str, namespace: str = "default") -> dict:
    """Rollback a deployment to previous version."""
    cmd = f"kubectl rollout undo deployment/{name} -n {namespace}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timed out"}


if __name__ == "__main__":
    print("Testing kubectl tool (read-only)...")
    result = kubectl("get pods -A")
    print(json.dumps(result, indent=2))

    print("\nTesting safety block (delete should be blocked)...")
    result = kubectl("delete pod test-pod")
    print(json.dumps(result, indent=2))

    print("\nTesting cluster health snapshot...")
    health = get_cluster_health()
    print(json.dumps(health, indent=2, default=str))
