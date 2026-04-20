#!/usr/bin/env python3
"""
Episode 11: Capstone — End-to-End Agentic DevOps Platform
Agentic SRE Platform — API Server. Unified interface for all SRE agents.

Author: Sagar Utekar
Series: AI-Assisted DevOps Workshop

Prerequisites:
    - Python 3.10+
    - fastapi (pip install fastapi)
    - uvicorn (pip install uvicorn)
    - anthropic Python SDK (pip install anthropic)
    - ANTHROPIC_API_KEY environment variable set
    - kubectl configured with cluster access
"""
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.diagnosis_agent import DiagnosisAgent
from agents.incident_agent import IncidentAgent
from agents.security_agent import SecurityAgent
from tools.unified_tools import toolkit

app = FastAPI(
    title="Agentic SRE Platform",
    description="AI-powered SRE platform by Sagar Utekar | CNCF Ambassador",
    version="1.0.0"
)

# Agent pool
agents = {
    "diagnosis": DiagnosisAgent(),
    "incident": IncidentAgent(),
    "security": SecurityAgent(),
}


# -- Models --
class DiagnoseRequest(BaseModel):
    query: str = "Investigate the cluster and report all issues."


class IncidentRequest(BaseModel):
    alert_name: str
    severity: str = "warning"
    service: str = "unknown"
    namespace: str = "default"
    description: str = ""


class ScanRequest(BaseModel):
    namespace: str = "default"
    scan_type: str = "security"  # security, cost, full


# -- Endpoints --
@app.get("/health")
def health():
    return {"status": "ok", "agents": list(agents.keys()), "platform": "Agentic SRE"}


@app.post("/diagnose")
def diagnose(req: DiagnoseRequest):
    result = agents["diagnosis"].run(req.query)
    return result


@app.post("/incident")
def handle_incident(req: IncidentRequest, background_tasks: BackgroundTasks):
    alert_text = f"""ALERT: {req.alert_name}
Severity: {req.severity}
Service: {req.service}
Namespace: {req.namespace}
Description: {req.description}

Handle this incident: investigate, diagnose, fix if safe, and report to slack-incidents."""

    # Run in background for webhook integrations
    result = agents["incident"].run(alert_text)
    return result


@app.post("/scan")
def security_scan(req: ScanRequest):
    task = f"Scan all resources in namespace '{req.namespace}' for security issues. Check every deployment's YAML for misconfigurations."
    result = agents["security"].run(task)
    return result


@app.post("/webhook/alertmanager")
def alertmanager_webhook(payload: dict):
    """Receive Alertmanager webhooks and trigger incident response."""
    results = []
    for alert in payload.get("alerts", []):
        alert_data = {
            "alert_name": alert.get("labels", {}).get("alertname", "Unknown"),
            "severity": alert.get("labels", {}).get("severity", "warning"),
            "service": alert.get("labels", {}).get("service", "unknown"),
            "namespace": alert.get("labels", {}).get("namespace", "default"),
            "description": alert.get("annotations", {}).get("description", ""),
        }
        result = agents["incident"].run(json.dumps(alert_data))
        results.append(result)
    return {"processed": len(results), "results": results}


@app.get("/audit")
def get_audit_log():
    """Get the full audit trail."""
    return toolkit.get_audit_log()


@app.post("/ask")
def ask_copilot(req: DiagnoseRequest):
    """Free-form question to the platform."""
    result = agents["diagnosis"].run(req.query)
    return result
