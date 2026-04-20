#!/usr/bin/env python3
"""
Episode 11: Capstone — End-to-End Agentic DevOps Platform
Security Scanner Agent — Scans Kubernetes resources for security issues.

Author: Sagar Utekar
Series: AI-Assisted DevOps Workshop

Prerequisites:
    - Python 3.10+
    - anthropic Python SDK (pip install anthropic)
    - ANTHROPIC_API_KEY environment variable set
    - kubectl configured with cluster access
"""
from agents.base_agent import SREAgent
from tools.unified_tools import toolkit

TOOLS = [
    {"name": "get_deployments", "description": "List deployments.", "input_schema": {"type": "object", "properties": {"all_ns": {"type": "boolean", "default": True}}}},
    {"name": "get_resource_yaml", "description": "Get resource YAML.", "input_schema": {"type": "object", "properties": {"resource": {"type": "string"}, "name": {"type": "string"}, "namespace": {"type": "string", "default": "default"}}, "required": ["resource", "name"]}},
    {"name": "get_pods", "description": "List pods.", "input_schema": {"type": "object", "properties": {"namespace": {"type": "string"}, "all_ns": {"type": "boolean", "default": True}}}},
    {"name": "notify", "description": "Send notification.", "input_schema": {"type": "object", "properties": {"channel": {"type": "string"}, "message": {"type": "string"}}, "required": ["channel", "message"]}},
]


class SecurityAgent(SREAgent):
    def __init__(self):
        super().__init__(
            name="SecurityAgent",
            system_prompt="""You scan Kubernetes resources for security issues.
Check: running as root, privileged, no resource limits, secrets in env, host namespaces, latest tags, no network policies.
Output: severity (CRITICAL/WARNING/INFO), resource, issue, fix.""",
            tools=TOOLS
        )
        self.register_tool("get_deployments", lambda all_ns=True: toolkit.k8s_get("deployments", all_ns=all_ns))
        self.register_tool("get_resource_yaml", lambda resource, name, namespace="default": toolkit._run(f"kubectl get {resource} {name} -n {namespace} -o yaml"))
        self.register_tool("get_pods", lambda namespace="default", all_ns=True: toolkit.k8s_get("pods", namespace, all_ns))
        self.register_tool("notify", lambda channel, message: toolkit.notify(channel, message))


if __name__ == "__main__":
    agent = SecurityAgent()
    result = agent.run("Scan all resources in namespace 'default' for security issues. Check every deployment's YAML for misconfigurations.")
    print(result["conclusion"])
