# Episode 10: AI-Powered Deployment Automation

- Analyze apps and recommend deployment targets
- Generate Dockerfile + K8s manifests + docker-compose from one analysis
- Score manifests on 5 production-readiness dimensions

## Setup

```bash
export ANTHROPIC_API_KEY="your-key-here"
pip install anthropic
```

## Files

| File | Description |
|------|-------------|
| `analyzer.py` | App analyzer — reads code, detects framework, recommends deployment target |
| `triple_generator.py` | Generates Dockerfile + K8s manifests + docker-compose |
| `improver.py` | Manifest scorer — reliability, security, observability, resources, rollout safety |
| `minimal_manifest.yaml` | Deliberately minimal manifest for testing the improver |
