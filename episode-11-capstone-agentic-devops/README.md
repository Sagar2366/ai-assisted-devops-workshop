# Episode 11: Capstone — End-to-End Agentic DevOps Platform

- Multi-agent DevOps platform with Agent Mesh architecture
- Shared tool layer with audit logging
- 3 specialized agents: Diagnosis, Incident Response, Security Scanning
- FastAPI gateway with webhook receiver for Alertmanager/GitHub

## Files

| File | Description |
|------|-------------|
| `tools/unified_tools.py` | Shared SREToolkit with audit logging |
| `agents/base_agent.py` | Base agent class with tool-use loop |
| `agents/diagnosis_agent.py` | Cluster health analysis |
| `agents/incident_agent.py` | Incident response (TRIAGE → VERIFY → REPORT) |
| `agents/security_agent.py` | Security scanning |
| `api/server.py` | FastAPI gateway with 7 endpoints |
| `run.py` | Entry point |
| `demo.sh` | curl commands to test all endpoints |
