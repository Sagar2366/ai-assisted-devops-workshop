# Episode 5: Build a DevOps Copilot

- Build a complete CLI copilot that diagnoses Kubernetes issues
- SAFE / RESTRICTED / BLOCKED command classification
- Audit logging for every tool execution
- Interactive CLI: diagnose, health, investigate, ask

## Setup

```bash
export ANTHROPIC_API_KEY="your-key-here"
pip install anthropic
kind create cluster --name workshop
kubectl apply -f test_workloads.yaml
```

## Files

| File | Description |
|------|-------------|
| `test_workloads.yaml` | 3 K8s deployments: healthy, ImagePullBackOff, CrashLoopBackOff |
| `k8s_tools.py` | K8sTools class with safety rules and audit trail |
| `copilot.py` | DevOps Copilot agent engine |
| `cli.py` | Interactive CLI interface |
