#!/usr/bin/env python3
"""
Episode 11: Capstone — End-to-End Agentic DevOps Platform
Incident Response Agent — TRIAGE -> INVESTIGATE -> DIAGNOSE -> REMEDIATE -> VERIFY -> REPORT flow.

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
    {"name": "cluster_health", "description": "Quick cluster health check.", "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_logs", "description": "Get pod logs.", "input_schema": {"type": "object", "properties": {"pod": {"type": "string"}, "namespace": {"type": "string", "default": "default"}, "previous": {"type": "boolean", "default": False}}, "required": ["pod"]}},
    {"name": "describe_pod", "description": "Describe pod.", "input_schema": {"type": "object", "properties": {"pod": {"type": "string"}, "namespace": {"type": "string", "default": "default"}}, "required": ["pod"]}},
    {"name": "get_events", "description": "Get events.", "input_schema": {"type": "object", "properties": {"namespace": {"type": "string", "default": "default"}}}},
    {"name": "scale", "description": "Scale deployment.", "input_schema": {"type": "object", "properties": {"deployment": {"type": "string"}, "replicas": {"type": "integer"}, "namespace": {"type": "string", "default": "default"}}, "required": ["deployment", "replicas"]}},
    {"name": "rollback", "description": "Rollback deployment.", "input_schema": {"type": "object", "properties": {"deployment": {"type": "string"}, "namespace": {"type": "string", "default": "default"}}, "required": ["deployment"]}},
    {"name": "restart", "description": "Restart deployment.", "input_schema": {"type": "object", "properties": {"deployment": {"type": "string"}, "namespace": {"type": "string", "default": "default"}}, "required": ["deployment"]}},
    {"name": "notify", "description": "Send notification.", "input_schema": {"type": "object", "properties": {"channel": {"type": "string"}, "message": {"type": "string"}}, "required": ["channel", "message"]}},
]


class IncidentAgent(SREAgent):
    def __init__(self):
        super().__init__(
            name="IncidentAgent",
            system_prompt="""You handle production incidents autonomously.
Protocol: TRIAGE -> INVESTIGATE -> DIAGNOSE -> REMEDIATE -> VERIFY -> REPORT.
You can: scale (max 10), rollback, restart.
You cannot: delete, exec, apply.
Always verify after remediation. Always notify slack-incidents.""",
            tools=TOOLS,
            max_steps=15
        )
        self.register_tool("cluster_health", lambda: toolkit.k8s_cluster_health())
        self.register_tool("get_logs", lambda pod, namespace="default", previous=False: toolkit.k8s_logs(pod, namespace, previous=previous))
        self.register_tool("describe_pod", lambda pod, namespace="default": toolkit.k8s_describe("pod", pod, namespace))
        self.register_tool("get_events", lambda namespace="default": toolkit.k8s_events(namespace))
        self.register_tool("scale", lambda deployment, replicas, namespace="default": toolkit.k8s_scale(deployment, replicas, namespace))
        self.register_tool("rollback", lambda deployment, namespace="default": toolkit.k8s_rollback(deployment, namespace))
        self.register_tool("restart", lambda deployment, namespace="default": toolkit.k8s_restart(deployment, namespace))
        self.register_tool("notify", lambda channel, message: toolkit.notify(channel, message))


if __name__ == "__main__":
    agent = IncidentAgent()
    result = agent.run("""ALERT: PodCrashLooping
Severity: critical
Service: payment-service
Namespace: default
Description: Payment service has restarted 15 times

Handle this incident: investigate, diagnose, fix if safe, and report to slack-incidents.""")
    print(result["conclusion"])
