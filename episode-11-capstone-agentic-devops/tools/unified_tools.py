#!/usr/bin/env python3
"""
Episode 11: Capstone — End-to-End Agentic DevOps Platform
Unified Tool Layer — All tools agents can use.

Author: Sagar Utekar
Series: AI-Assisted DevOps Workshop

Prerequisites:
    - Python 3.10+
    - kubectl configured with cluster access
    - gh CLI authenticated (for GitHub tools)
"""
import subprocess
import json
import os
from datetime import datetime
from typing import Optional


class SREToolkit:
    """All tools available to SRE agents."""

    def __init__(self):
        self.audit_log = []

    def _log(self, agent: str, tool: str, action: str, result_preview: str):
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "tool": tool,
            "action": action,
            "result_preview": result_preview[:200]
        })

    def _run(self, cmd: str, timeout: int = 30) -> str:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return result.stdout or result.stderr or "No output"
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error: {str(e)}"

    # -- Kubernetes Tools --
    def k8s_get(self, resource: str, namespace: str = "default", all_ns: bool = False, output: str = "wide") -> str:
        cmd = f"kubectl get {resource} -o {output}"
        cmd += " -A" if all_ns else f" -n {namespace}"
        return self._run(cmd)

    def k8s_describe(self, resource: str, name: str, namespace: str = "default") -> str:
        return self._run(f"kubectl describe {resource} {name} -n {namespace}")

    def k8s_logs(self, pod: str, namespace: str = "default", lines: int = 50, previous: bool = False) -> str:
        cmd = f"kubectl logs {pod} -n {namespace} --tail={lines}"
        if previous:
            cmd += " --previous"
        return self._run(cmd)

    def k8s_events(self, namespace: str = "default", all_ns: bool = False) -> str:
        cmd = "kubectl get events --sort-by='.lastTimestamp'"
        cmd += " -A" if all_ns else f" -n {namespace}"
        return self._run(cmd)

    def k8s_scale(self, deployment: str, replicas: int, namespace: str = "default") -> str:
        if replicas > 10:
            return "BLOCKED: Max 10 replicas"
        return self._run(f"kubectl scale deployment/{deployment} --replicas={replicas} -n {namespace}")

    def k8s_rollback(self, deployment: str, namespace: str = "default") -> str:
        return self._run(f"kubectl rollout undo deployment/{deployment} -n {namespace}")

    def k8s_restart(self, deployment: str, namespace: str = "default") -> str:
        return self._run(f"kubectl rollout restart deployment/{deployment} -n {namespace}")

    def k8s_cluster_health(self) -> str:
        sections = []
        for title, cmd in [
            ("Nodes", "kubectl get nodes -o wide"),
            ("Problem Pods", "kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded -o wide 2>/dev/null"),
            ("Warnings", "kubectl get events -A --field-selector type=Warning --sort-by='.lastTimestamp' 2>/dev/null | tail -10"),
            ("Deployments", "kubectl get deployments -A -o wide"),
        ]:
            sections.append(f"=== {title} ===\n{self._run(cmd)}")
        return "\n\n".join(sections)

    # -- GitHub Tools --
    def gh_pr_list(self, state: str = "open") -> str:
        return self._run(f"gh pr list --state {state}")

    def gh_pr_diff(self, pr_number: int) -> str:
        return self._run(f"gh pr diff {pr_number}")

    def gh_run_list(self, limit: int = 5) -> str:
        return self._run(f"gh run list --limit {limit}")

    # -- Notification Tools --
    def notify(self, channel: str, message: str) -> str:
        # In production, integrate with Slack/PagerDuty/Teams
        timestamp = datetime.now().strftime("%H:%M:%S")
        notification = f"[{timestamp}] [{channel}] {message}"
        print(f"\n  NOTIFICATION: {notification}")
        self._log("system", "notify", channel, message)
        return f"Sent to {channel}"

    def get_audit_log(self) -> list:
        return self.audit_log


# Singleton toolkit instance
toolkit = SREToolkit()


if __name__ == "__main__":
    print("SREToolkit initialized. Running cluster health check...")
    print(toolkit.k8s_cluster_health())
