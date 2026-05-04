"""
SRE Log Analyzer — Docker Model Runner Demo
A FastAPI service that analyzes Kubernetes logs using a local LLM.
AI-Assisted DevOps Workshop | Episode 2, Lab 10 | Sagar Utekar
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="SRE Log Analyzer", version="1.0.0")

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://model-runner.docker.internal/engines/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "ai/llama3.2")

client = OpenAI(base_url=LLM_BASE_URL, api_key="not-needed")

SYSTEM_PROMPT = """You are a senior SRE assistant. When given Kubernetes logs or alerts:
1. Identify the root cause
2. Assess severity (critical/warning/info)
3. Give 2-3 actionable kubectl commands to investigate or fix
Be concise. No fluff."""

SAMPLE_LOGS = {
    "oomkilled": """Pod payment-service-7f8b9c6d4-x2k9p OOMKilled
Container memory limit: 256Mi
Peak usage before kill: 254Mi
Restart count: 4
Last restart: 2 minutes ago""",
    "crashloop": """Pod api-gateway-5d9f8b7c6-k3m2n CrashLoopBackOff
Exit code: 1
Back-off restarting failed container
Events:
  Warning  BackOff  2m (x5 over 8m)  kubelet  Back-off restarting failed container""",
    "imagepull": """Pod frontend-8b7c6d5f4-j2k1m ImagePullBackOff
Failed to pull image "registry.internal/frontend:v2.3.1"
Error: unauthorized: authentication required
Events:
  Warning  Failed  1m (x3 over 5m)  kubelet  Failed to pull image""",
}


class AnalyzeRequest(BaseModel):
    logs: str


class AnalyzeResponse(BaseModel):
    analysis: str
    model: str
    backend: str


@app.get("/health")
def health():
    return {"status": "healthy", "model": MODEL_NAME, "backend": LLM_BASE_URL}


@app.get("/samples")
def samples():
    return {"available_samples": list(SAMPLE_LOGS.keys()), "usage": "POST /analyze with {\"logs\": \"...\"} or GET /analyze/{sample_name}"}


@app.get("/analyze/{sample_name}")
def analyze_sample(sample_name: str):
    if sample_name not in SAMPLE_LOGS:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_name}' not found. Available: {list(SAMPLE_LOGS.keys())}")
    return _analyze(SAMPLE_LOGS[sample_name])


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_logs(req: AnalyzeRequest):
    return _analyze(req.logs)


def _analyze(logs: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze these Kubernetes logs:\n\n{logs}"},
        ],
        temperature=0.1,
    )
    return {
        "analysis": response.choices[0].message.content,
        "model": MODEL_NAME,
        "backend": LLM_BASE_URL,
    }
