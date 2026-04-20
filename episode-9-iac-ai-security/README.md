# Episode 9: Infrastructure as Code + AI & Security Scanning

- Generate Terraform from English with security defaults baked in
- K8s manifest security scanner (CIS Benchmark + NSA-CISA guidelines)
- Cluster cost optimization with right-sizing recommendations

## Setup

```bash
export ANTHROPIC_API_KEY="your-key-here"
pip install anthropic
brew install terraform  # optional
```

## Files

| File | Description |
|------|-------------|
| `terraform_generator.py` | English to Terraform with security defaults and cost estimation |
| `k8s_scanner.py` | K8s manifest security scanner |
| `bad_deployment.yaml` | Intentionally insecure manifest for testing the scanner |
| `cost_optimizer.py` | K8s resource cost analyzer |
