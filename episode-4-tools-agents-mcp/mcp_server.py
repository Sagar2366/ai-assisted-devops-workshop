"""
Episode 4: Building Tools, Agents & MCP Servers
File: mcp_server.py — Kubernetes MCP Server

Author: Sagar Utekar
Prerequisites: Episodes 1-3 completed; kind cluster running; kubectl configured;
              Python packages: mcp[cli] (pip install mcp[cli])

Exposes K8s cluster operations as MCP tools.
Connect this to Claude Code, Claude Desktop, or any MCP client.

Usage:
  python3 mcp_server.py                          # Start on stdio
  claude mcp add kubernetes-sre -- python3 /path/to/mcp_server.py  # Add to Claude Code
"""
import json
import subprocess
import sys
from typing import Any

# MCP SDK
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP(
    name="kubernetes-sre",
    version="1.0.0",
)

# --- TOOLS ------------------------------------------------------------------


@mcp.tool()
def get_pods(namespace: str = "default", all_namespaces: bool = False) -> str:
    """List pods in a namespace or across all namespaces. Use this as a starting point for cluster investigation."""
    cmd = "kubectl get pods -o wide"
    if all_namespaces:
        cmd += " -A"
    else:
        cmd += f" -n {namespace}"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout or result.stderr


@mcp.tool()
def describe_resource(resource_type: str, name: str, namespace: str = "default") -> str:
    """Get detailed information about a Kubernetes resource (pod, deployment, service, node, etc.)."""
    cmd = f"kubectl describe {resource_type} {name} -n {namespace}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout or result.stderr


@mcp.tool()
def get_logs(pod_name: str, namespace: str = "default", tail_lines: int = 100, previous: bool = False) -> str:
    """Get logs from a pod. Set previous=true to get logs from a crashed container."""
    cmd = f"kubectl logs {pod_name} -n {namespace} --tail={tail_lines}"
    if previous:
        cmd += " --previous"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout or result.stderr


@mcp.tool()
def get_events(namespace: str = "default", all_namespaces: bool = False) -> str:
    """Get recent Kubernetes events. Useful for debugging scheduling, pulling, and crash issues."""
    cmd = "kubectl get events --sort-by='.lastTimestamp'"
    if all_namespaces:
        cmd += " -A"
    else:
        cmd += f" -n {namespace}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout or result.stderr


@mcp.tool()
def get_resource_usage() -> str:
    """Get CPU and memory usage for all nodes. Requires metrics-server."""
    result = subprocess.run(
        "kubectl top nodes 2>/dev/null || echo 'metrics-server not installed'",
        shell=True, capture_output=True, text=True, timeout=30
    )
    return result.stdout or result.stderr


@mcp.tool()
def get_deployments(namespace: str = "default", all_namespaces: bool = False) -> str:
    """List deployments with their status, replicas, and age."""
    cmd = "kubectl get deployments -o wide"
    if all_namespaces:
        cmd += " -A"
    else:
        cmd += f" -n {namespace}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout or result.stderr


@mcp.tool()
def scale_deployment(name: str, replicas: int, namespace: str = "default") -> str:
    """Scale a deployment to a specific number of replicas. Safety limit: max 10."""
    if replicas > 10:
        return "ERROR: Safety limit -- max 10 replicas. Manual intervention required for higher."
    if replicas < 0:
        return "ERROR: Replicas cannot be negative."

    cmd = f"kubectl scale deployment/{name} --replicas={replicas} -n {namespace}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout or result.stderr


@mcp.tool()
def rollback_deployment(name: str, namespace: str = "default") -> str:
    """Rollback a deployment to its previous version."""
    cmd = f"kubectl rollout undo deployment/{name} -n {namespace}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout or result.stderr


@mcp.tool()
def get_cluster_summary() -> str:
    """Get a comprehensive cluster summary: nodes, namespaces, pod counts, and any issues."""
    sections = []

    commands = {
        "Nodes": "kubectl get nodes -o wide",
        "Namespaces": "kubectl get namespaces",
        "All Pods (summary)": "kubectl get pods -A --no-headers | awk '{print $4}' | sort | uniq -c | sort -rn",
        "Problem Pods": "kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers 2>/dev/null || echo 'All pods healthy'",
        "Recent Warnings": "kubectl get events -A --field-selector type=Warning --sort-by='.lastTimestamp' --no-headers 2>/dev/null | tail -10"
    }

    for title, cmd in commands.items():
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        sections.append(f"=== {title} ===\n{result.stdout or result.stderr or 'No data'}")

    return "\n\n".join(sections)


# --- RESOURCES ---------------------------------------------------------------


@mcp.resource("k8s://cluster/info")
def cluster_info() -> str:
    """Basic cluster connection info."""
    result = subprocess.run(
        "kubectl cluster-info 2>/dev/null | head -5",
        shell=True, capture_output=True, text=True, timeout=10
    )
    return result.stdout or "Cluster not reachable"


# --- RUN SERVER --------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
