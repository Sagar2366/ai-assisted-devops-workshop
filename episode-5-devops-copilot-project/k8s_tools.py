"""
Episode 5: Build a DevOps Copilot
AI-Assisted DevOps Workshop

Kubernetes tools for the DevOps Copilot.
Each function = one tool the agent can use.

Author: Sagar Utekar

Prerequisites:
    - Python 3.10+
    - kubectl configured and pointing to your cluster
    - kind cluster with test workloads deployed (see test_workloads.yaml)
"""
import subprocess
import json
from datetime import datetime
from typing import Optional


class K8sTools:
    """Collection of Kubernetes tools with safety guardrails."""

    # Commands the agent is ALLOWED to run
    SAFE_COMMANDS = {"get", "describe", "logs", "top", "explain", "api-resources", "version", "cluster-info"}
    # Commands that need explicit permission
    RESTRICTED_COMMANDS = {"scale", "rollout"}
    # Commands that are BLOCKED
    BLOCKED_COMMANDS = {"delete", "exec", "apply", "patch", "replace", "edit", "drain", "cordon", "taint"}

    def __init__(self, auto_approve_restricted: bool = False):
        self.auto_approve = auto_approve_restricted
        self.audit_log = []

    def _log(self, action: str, command: str, result: str):
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "command": command,
            "result_preview": result[:200]
        })

    def _run(self, cmd: str, timeout: int = 30) -> str:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            output = result.stdout or result.stderr or "No output"
            self._log("executed", cmd, output)
            return output
        except subprocess.TimeoutExpired:
            self._log("timeout", cmd, "Command timed out")
            return "ERROR: Command timed out"

    def kubectl(self, command: str) -> str:
        """Execute a kubectl command with safety checks."""
        parts = command.strip().split()
        verb = parts[0] if parts else ""

        if verb in self.BLOCKED_COMMANDS:
            msg = f"BLOCKED: '{verb}' is not allowed. Agent can only use: {', '.join(self.SAFE_COMMANDS | self.RESTRICTED_COMMANDS)}"
            self._log("blocked", f"kubectl {command}", msg)
            return msg

        if verb in self.RESTRICTED_COMMANDS and not self.auto_approve:
            msg = f"APPROVAL REQUIRED: 'kubectl {command}' needs human approval."
            self._log("needs_approval", f"kubectl {command}", msg)
            return msg

        return self._run(f"kubectl {command}")

    def get_pods(self, namespace: str = "default", all_namespaces: bool = False) -> str:
        cmd = "kubectl get pods -o wide"
        cmd += " -A" if all_namespaces else f" -n {namespace}"
        return self._run(cmd)

    def get_pod_logs(self, pod: str, namespace: str = "default", lines: int = 50, previous: bool = False) -> str:
        cmd = f"kubectl logs {pod} -n {namespace} --tail={lines}"
        if previous:
            cmd += " --previous"
        return self._run(cmd)

    def describe_pod(self, pod: str, namespace: str = "default") -> str:
        return self._run(f"kubectl describe pod {pod} -n {namespace}")

    def get_events(self, namespace: str = "default", all_namespaces: bool = False) -> str:
        cmd = "kubectl get events --sort-by='.lastTimestamp'"
        cmd += " -A" if all_namespaces else f" -n {namespace}"
        return self._run(cmd)

    def get_deployments(self, namespace: str = "default", all_namespaces: bool = False) -> str:
        cmd = "kubectl get deployments -o wide"
        cmd += " -A" if all_namespaces else f" -n {namespace}"
        return self._run(cmd)

    def get_node_status(self) -> str:
        return self._run("kubectl get nodes -o wide")

    def get_cluster_health(self) -> str:
        """Comprehensive cluster health check."""
        sections = []
        checks = [
            ("Nodes", "kubectl get nodes -o wide"),
            ("Problem Pods", "kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded -o wide 2>/dev/null"),
            ("Recent Warnings", "kubectl get events -A --field-selector type=Warning --sort-by='.lastTimestamp' 2>/dev/null | tail -15"),
            ("Deployments", "kubectl get deployments -A -o wide"),
        ]
        for title, cmd in checks:
            output = self._run(cmd)
            sections.append(f"=== {title} ===\n{output}")
        return "\n\n".join(sections)

    def scale_deployment(self, name: str, replicas: int, namespace: str = "default") -> str:
        if replicas > 10:
            return "SAFETY: Max 10 replicas allowed."
        return self._run(f"kubectl scale deployment/{name} --replicas={replicas} -n {namespace}")

    def rollback_deployment(self, name: str, namespace: str = "default") -> str:
        return self._run(f"kubectl rollout undo deployment/{name} -n {namespace}")

    def get_audit_log(self) -> list:
        return self.audit_log


if __name__ == "__main__":
    # Quick demo: test the tools against your cluster
    tools = K8sTools(auto_approve_restricted=False)

    print("=== Cluster Health ===")
    print(tools.get_cluster_health())

    print("\n=== Safety Test: Blocked Command ===")
    print(tools.kubectl("delete pod test-pod"))

    print("\n=== Safety Test: Restricted Command ===")
    print(tools.kubectl("scale deployment/web-frontend --replicas=2"))

    print("\n=== Audit Log ===")
    for entry in tools.get_audit_log():
        print(f"  [{entry['timestamp']}] {entry['action']}: {entry['command']}")
