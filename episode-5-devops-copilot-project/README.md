# Episode 5: Build a DevOps Copilot

- Build a complete CLI copilot that diagnoses Kubernetes issues
- SAFE / RESTRICTED / BLOCKED command classification
- Audit logging for every tool execution
- Interactive CLI: diagnose, health, investigate, ask

```
SRE Diagnostic Ladder (never skip a rung):

  1. BROAD     → kubectl get pods -A (what's the overall state?)
       ↓
  2. NARROW    → kubectl describe pod <failing-pod>
       ↓
  3. DEEP      → kubectl logs <pod> --previous
       ↓
  4. ACT       → kubectl rollout restart / scale / patch
       ↓
  5. VERIFY    → kubectl get pods (did it work?)
```

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
