#!/usr/bin/env python3
"""
Episode 11: Capstone — End-to-End Agentic DevOps Platform
Cluster Diagnosis Agent — Specialized for cluster health analysis.

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
    {"name": "cluster_health", "description": "Get comprehensive cluster health.", "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_pods", "description": "List pods.", "input_schema": {"type": "object", "properties": {"namespace": {"type": "string"}, "all_ns": {"type": "boolean", "default": True}}}},
    {"name": "get_logs", "description": "Get pod logs.", "input_schema": {"type": "object", "properties": {"pod": {"type": "string"}, "namespace": {"type": "string", "default": "default"}, "previous": {"type": "boolean", "default": False}}, "required": ["pod"]}},
    {"name": "describe_pod", "description": "Describe a pod.", "input_schema": {"type": "object", "properties": {"pod": {"type": "string"}, "namespace": {"type": "string", "default": "default"}}, "required": ["pod"]}},
    {"name": "get_events", "description": "Get K8s events.", "input_schema": {"type": "object", "properties": {"all_ns": {"type": "boolean", "default": True}}}},
]


class DiagnosisAgent(SREAgent):
    def __init__(self):
        super().__init__(
            name="DiagnosisAgent",
            system_prompt="""You diagnose Kubernetes cluster issues.
Start with cluster_health, then investigate unhealthy resources.
For each issue: identify root cause, severity, and recommended fix.
Output a prioritized issue list.""",
            tools=TOOLS
        )
        self.register_tool("cluster_health", lambda: toolkit.k8s_cluster_health())
        self.register_tool("get_pods", lambda namespace="default", all_ns=True: toolkit.k8s_get("pods", namespace, all_ns))
        self.register_tool("get_logs", lambda pod, namespace="default", previous=False: toolkit.k8s_logs(pod, namespace, previous=previous))
        self.register_tool("describe_pod", lambda pod, namespace="default": toolkit.k8s_describe("pod", pod, namespace))
        self.register_tool("get_events", lambda all_ns=True: toolkit.k8s_events(all_ns=all_ns))


if __name__ == "__main__":
    agent = DiagnosisAgent()
    result = agent.run("Full cluster diagnosis - find all issues, prioritize by severity")
    print(result["conclusion"])
