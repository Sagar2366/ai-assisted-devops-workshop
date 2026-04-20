#!/usr/bin/env python3
"""
Episode 2: Prompt Caching — Save 90% on Repeated Calls
AI-Assisted DevOps Workshop | Sagar Utekar

Cache your system prompts and runbooks. Pay once for the cache write,
then 90% less on every subsequent call with the same prefix.

Prerequisites:
  export ANTHROPIC_API_KEY="your-key-here"
  pip install anthropic
"""
import anthropic

client = anthropic.Anthropic()

# This large system prompt gets cached — you pay ONCE
# Subsequent calls with the same prefix are 90% cheaper
SYSTEM_PROMPT = """You are an expert SRE assistant for our production Kubernetes platform.

## Our Infrastructure
- 3 EKS clusters: us-east-1 (prod), eu-west-1 (staging), ap-south-1 (DR)
- Service mesh: Istio 1.20
- Monitoring: Prometheus + Grafana + Loki
- CI/CD: GitHub Actions + ArgoCD
- Secrets: HashiCorp Vault

## Our Runbooks
### Pod CrashLoopBackOff
1. Check pod logs: kubectl logs <pod> -n <ns> --previous
2. Check events: kubectl describe pod <pod> -n <ns>
3. Check resource limits vs actual usage
4. Check recent deployments: kubectl rollout history
5. If OOM: increase memory limits by 50%, redeploy
6. If config error: check ConfigMaps and Secrets

### High Latency Alert
1. Check Istio sidecar: istioctl proxy-status
2. Check upstream services: kubectl get endpoints
3. Check HPA status: kubectl get hpa
4. Check node resources: kubectl top nodes
5. If connection pooling: check Istio DestinationRule

[... imagine 50 more runbooks here ...]
""" + "Additional context: " * 500  # Simulating large context

# First call — creates cache
response1 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=500,
    system=[{
        "type": "text",
        "text": SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"}
    }],
    messages=[{"role": "user", "content": "Pod api-server is CrashLoopBackOff. What should I check first?"}]
)
print(f"Call 1 - Cache WRITE: input={response1.usage.input_tokens} tokens")
print(f"  cache_creation_input_tokens: {response1.usage.cache_creation_input_tokens}")
print(f"  cache_read_input_tokens: {response1.usage.cache_read_input_tokens}")

# Second call — cache HIT (90% cheaper!)
response2 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=500,
    system=[{
        "type": "text",
        "text": SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"}
    }],
    messages=[{"role": "user", "content": "We're seeing high latency on the checkout service. Walk me through diagnosis."}]
)
print(f"\nCall 2 - Cache HIT: input={response2.usage.input_tokens} tokens")
print(f"  cache_creation_input_tokens: {response2.usage.cache_creation_input_tokens}")
print(f"  cache_read_input_tokens: {response2.usage.cache_read_input_tokens}")
print(f"\n  Cache hit = 90% cheaper on the system prompt!")
