# Lab 5: The Multi-Provider Gateway — Routing AI Like Traffic

> **Mission:** Build an AI gateway that intelligently routes requests between local, cloud, and enterprise AI providers based on data sensitivity, latency requirements, and cost constraints. By the end of this lab, you will have a production-ready gateway with circuit breakers, fallbacks, and health checks — the same resilience patterns you use for any distributed system.

---

## Concept: Envoy Proxy for AI

You already route traffic intelligently in your infrastructure:

- Internal service-to-service calls go through a service mesh (Istio/Envoy)
- External API calls go through an API gateway (Kong/AWS API Gateway)
- Sensitive traffic stays within your VPC; public traffic goes through a CDN

The same logic applies to AI requests:

- **Sensitive data** (PII, credentials, proprietary code) must stay within your security boundary
- **Fast triage** (sub-second responses) should hit local models to avoid network latency
- **Complex analysis** (multi-step reasoning) needs the most capable model, regardless of location
- **Cost optimization** means not using a $15/million-token model for a task a $0.20/million-token model handles fine

```
                    ┌─────────────────┐
                    │   AI Gateway    │
                    │  (Your Code)    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌──────▼─────┐  ┌────▼────────┐
     │   Local    │  │   Cloud    │  │  Enterprise │
     │  (Ollama)  │  │ (Claude API)│  │  (Bedrock)  │
     │  Fast/Free │  │  Balanced  │  │  Compliant  │
     └────────────┘  └────────────┘  └─────────────┘
```

**The gateway is your single point of control** — logging, metrics, routing, failover — all in one place.

---

## Step 1: Define the Provider Architecture

```python
import time
import json
import logging
import requests
import boto3
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-gateway")


class Provider(Enum):
    LOCAL = "local"          # Ollama - fast, free, private
    CLOUD = "cloud"          # Claude API - balanced
    ENTERPRISE = "enterprise"  # AWS Bedrock - compliant, governed


class CircuitState(Enum):
    CLOSED = "closed"        # Normal operation - requests flow through
    OPEN = "open"            # Provider failing - reject immediately
    HALF_OPEN = "half_open"  # Testing recovery - allow one request


@dataclass
class CircuitBreaker:
    """Circuit breaker per provider - prevents cascading failures."""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure: float = 0
    last_attempt: float = 0
    threshold: int = 3          # Failures before opening
    timeout: float = 30.0       # Seconds before trying again
    success_threshold: int = 2  # Successes to close from half-open


@dataclass
class ProviderMetrics:
    """Track per-provider performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    blocked_by_circuit: int = 0
    
    @property
    def avg_latency(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency / self.successful_requests
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
```

---

## Step 2: Build the Gateway Core

```python
class AIGateway:
    """
    Multi-provider AI gateway with circuit breakers and intelligent routing.
    
    Think of this as your AI load balancer — it knows the health of each
    provider, routes based on requirements, and fails over gracefully.
    """
    
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
        
        # Circuit breakers - one per provider
        self.circuits = {
            Provider.LOCAL: CircuitBreaker(),
            Provider.CLOUD: CircuitBreaker(),
            Provider.ENTERPRISE: CircuitBreaker(),
        }
        
        # Metrics - one per provider
        self.metrics = {
            Provider.LOCAL: ProviderMetrics(),
            Provider.CLOUD: ProviderMetrics(),
            Provider.ENTERPRISE: ProviderMetrics(),
        }
    
    def route(self, query: str, sensitivity: str = "low",
              complexity: str = "medium", latency: str = "normal") -> dict:
        """
        Route a query to the best available provider.
        
        Args:
            query: The prompt to send
            sensitivity: "low", "medium", "high" - data sensitivity level
            complexity: "low", "medium", "high" - reasoning complexity needed
            latency: "fast", "normal", "relaxed" - response time requirement
        
        Returns:
            dict with "provider", "response", "latency_ms"
        """
        
        # Rule 1: High sensitivity MUST go to enterprise (Bedrock)
        # Just like PCI data MUST stay in your compliant environment
        if sensitivity == "high":
            logger.info("High sensitivity: routing to Enterprise (Bedrock)")
            return self._call_with_metrics(Provider.ENTERPRISE, query)
        
        # Rule 2: Fast latency prefers local (no network round-trip)
        if latency == "fast" and complexity == "low":
            logger.info("Fast + low complexity: routing to Local (Ollama)")
            return self._try_with_fallback(query, 
                preferred=[Provider.LOCAL, Provider.CLOUD, Provider.ENTERPRISE])
        
        # Rule 3: High complexity needs the most capable model
        if complexity == "high":
            logger.info("High complexity: routing to Cloud (Claude API)")
            return self._try_with_fallback(query,
                preferred=[Provider.CLOUD, Provider.ENTERPRISE, Provider.LOCAL])
        
        # Default: try local first (cheapest), fall back through the chain
        logger.info("Default routing: Local -> Cloud -> Enterprise")
        return self._try_with_fallback(query,
            preferred=[Provider.LOCAL, Provider.CLOUD, Provider.ENTERPRISE])
    
    def _try_with_fallback(self, query: str, preferred: list) -> dict:
        """Try providers in order, falling back on failure."""
        
        errors = []
        for provider in preferred:
            if self._circuit_allows(provider):
                try:
                    result = self._call_with_metrics(provider, query)
                    self._record_success(provider)
                    return result
                except Exception as e:
                    self._record_failure(provider)
                    errors.append(f"{provider.value}: {str(e)}")
                    logger.warning(f"Provider {provider.value} failed: {e}")
            else:
                self.metrics[provider].blocked_by_circuit += 1
                logger.info(f"Circuit OPEN for {provider.value}, skipping")
        
        raise Exception(f"All providers unavailable. Errors: {'; '.join(errors)}")
```

---

## Step 3: Implement Provider Calls

```python
    def _call_with_metrics(self, provider: Provider, query: str) -> dict:
        """Call a provider and track metrics."""
        
        start = time.time()
        self.metrics[provider].total_requests += 1
        
        if provider == Provider.LOCAL:
            response = self._call_local(query)
        elif provider == Provider.CLOUD:
            response = self._call_cloud(query)
        elif provider == Provider.ENTERPRISE:
            response = self._call_enterprise(query)
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        latency = time.time() - start
        self.metrics[provider].total_latency += latency
        self.metrics[provider].successful_requests += 1
        
        return {
            "provider": provider.value,
            "response": response,
            "latency_ms": round(latency * 1000, 2)
        }
    
    def _call_local(self, query: str) -> str:
        """Call Ollama running locally."""
        
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": "llama3.2",
                "prompt": query,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["response"]
    
    def _call_cloud(self, query: str) -> str:
        """Call Claude API directly."""
        
        import anthropic
        client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": query}]
        )
        return message.content[0].text
    
    def _call_enterprise(self, query: str) -> str:
        """Call Claude via AWS Bedrock (enterprise-governed)."""
        
        response = self.bedrock_client.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-10-25",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": query}]
            })
        )
        
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]
```

---

## Step 4: Implement Circuit Breaker Logic

```python
    def _circuit_allows(self, provider: Provider) -> bool:
        """Check if the circuit breaker allows a request to this provider."""
        
        cb = self.circuits[provider]
        
        if cb.state == CircuitState.CLOSED:
            return True
        
        if cb.state == CircuitState.OPEN:
            # Check if timeout has elapsed - time to try again
            if time.time() - cb.last_failure > cb.timeout:
                cb.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit for {provider.value}: OPEN -> HALF_OPEN (testing recovery)")
                return True
            return False
        
        # HALF_OPEN: allow the test request
        return True
    
    def _record_success(self, provider: Provider):
        """Record a successful call - may close a half-open circuit."""
        
        cb = self.circuits[provider]
        
        if cb.state == CircuitState.HALF_OPEN:
            cb.success_count += 1
            if cb.success_count >= cb.success_threshold:
                cb.state = CircuitState.CLOSED
                cb.failure_count = 0
                cb.success_count = 0
                logger.info(f"Circuit for {provider.value}: HALF_OPEN -> CLOSED (recovered)")
        
        cb.failure_count = 0  # Reset on success
    
    def _record_failure(self, provider: Provider):
        """Record a failed call - may open the circuit."""
        
        cb = self.circuits[provider]
        cb.failure_count += 1
        cb.last_failure = time.time()
        
        if cb.state == CircuitState.HALF_OPEN:
            # Failed during recovery test - back to open
            cb.state = CircuitState.OPEN
            cb.success_count = 0
            logger.warning(f"Circuit for {provider.value}: HALF_OPEN -> OPEN (recovery failed)")
        
        elif cb.failure_count >= cb.threshold:
            cb.state = CircuitState.OPEN
            logger.warning(f"Circuit for {provider.value}: CLOSED -> OPEN (threshold reached: {cb.failure_count} failures)")
```

---

## Step 5: Add Health Checks

```python
    def health_check(self) -> dict:
        """
        Check health of all providers.
        
        Run this on a schedule (like a /healthz endpoint)
        to proactively detect issues before they affect users.
        """
        
        health = {}
        
        for provider in Provider:
            try:
                start = time.time()
                
                if provider == Provider.LOCAL:
                    resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                    resp.raise_for_status()
                    
                elif provider == Provider.CLOUD:
                    # Lightweight check - just verify auth works
                    import anthropic
                    client = anthropic.Anthropic()
                    client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "ping"}]
                    )
                    
                elif provider == Provider.ENTERPRISE:
                    # Verify Bedrock access
                    self.bedrock_client.invoke_model(
                        modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
                        contentType="application/json",
                        accept="application/json",
                        body=json.dumps({
                            "anthropic_version": "bedrock-2023-10-25",
                            "max_tokens": 10,
                            "messages": [{"role": "user", "content": "ping"}]
                        })
                    )
                
                latency = time.time() - start
                health[provider.value] = {
                    "status": "healthy",
                    "latency_ms": round(latency * 1000, 2),
                    "circuit": self.circuits[provider].state.value
                }
                
            except Exception as e:
                health[provider.value] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "circuit": self.circuits[provider].state.value
                }
        
        return health
    
    def get_metrics(self) -> dict:
        """Return metrics for all providers (expose via /metrics endpoint)."""
        
        return {
            provider.value: {
                "total_requests": self.metrics[provider].total_requests,
                "success_rate": f"{self.metrics[provider].success_rate:.2%}",
                "avg_latency_ms": round(self.metrics[provider].avg_latency * 1000, 2),
                "circuit_state": self.circuits[provider].state.value,
                "blocked_by_circuit": self.metrics[provider].blocked_by_circuit
            }
            for provider in Provider
        }
```

---

## Step 6: Use the Gateway

```python
# Initialize the gateway
gateway = AIGateway(ollama_url="http://localhost:11434")

# Scenario 1: Fast triage of a simple alert
# Routes to: Local (Ollama) - fast, no network round-trip
result = gateway.route(
    query="Classify this alert severity (P1-P4): CPU usage at 85% for 10 minutes",
    sensitivity="low",
    complexity="low",
    latency="fast"
)
print(f"Provider: {result['provider']} | Latency: {result['latency_ms']}ms")
print(f"Response: {result['response'][:200]}")
print()

# Scenario 2: Complex incident analysis
# Routes to: Cloud (Claude API) - best reasoning capability
result = gateway.route(
    query="""Analyze this multi-signal incident:
    - API latency p99: 200ms -> 2.5s (5 min ago)
    - 3 pods OOMKilled
    - Redis connection pool exhausted
    - Deployment 7 minutes ago (api-v2.4.1)
    What is the root cause chain?""",
    sensitivity="low",
    complexity="high",
    latency="normal"
)
print(f"Provider: {result['provider']} | Latency: {result['latency_ms']}ms")
print(f"Response: {result['response'][:200]}")
print()

# Scenario 3: Query involving customer data
# Routes to: Enterprise (Bedrock) - compliant, governed, audited
result = gateway.route(
    query="Analyze why customer ID 12345's API calls are failing with auth errors since the last IAM policy change",
    sensitivity="high",
    complexity="medium",
    latency="normal"
)
print(f"Provider: {result['provider']} | Latency: {result['latency_ms']}ms")
print(f"Response: {result['response'][:200]}")
```

---

## Step 7: Verify Health and Metrics

```python
# Check provider health
print("=" * 60)
print("PROVIDER HEALTH CHECK")
print("=" * 60)
health = gateway.health_check()
for provider, status in health.items():
    indicator = "OK" if status["status"] == "healthy" else "FAIL"
    print(f"  [{indicator}] {provider:<12} | circuit: {status['circuit']}")
    if "latency_ms" in status:
        print(f"       latency: {status['latency_ms']}ms")
    if "error" in status:
        print(f"       error: {status['error']}")

# View routing metrics
print()
print("=" * 60)
print("ROUTING METRICS")
print("=" * 60)
metrics = gateway.get_metrics()
for provider, data in metrics.items():
    print(f"  {provider:<12} | requests: {data['total_requests']:<5} | "
          f"success: {data['success_rate']:<7} | "
          f"avg latency: {data['avg_latency_ms']}ms | "
          f"circuit: {data['circuit_state']}")
```

---

## Routing Rules Reference

| Data Sensitivity | Complexity | Latency Need | Route To | Rationale |
|-----------------|-----------|-------------|----------|-----------|
| High (PII/secrets) | Any | Any | Enterprise (Bedrock) | Compliance requirement — data must not leave governed boundary |
| Low | Low | Fast | Local (Ollama) | No network latency, zero cost, maximum speed |
| Low | High | Normal | Cloud (Claude API) | Best reasoning capability for complex problems |
| Medium | Medium | Normal | Cloud with Enterprise fallback | Balanced capability with compliant fallback |
| Any | Any | Any (all providers down) | Error + PagerDuty alert | Fail safely, notify humans |

---

## Step 8: Add Retry Logic with Exponential Backoff

```python
import random

def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    """
    Retry a provider call with exponential backoff and jitter.
    
    Same pattern as retrying failed HTTP requests or database connections.
    The jitter prevents thundering herd when multiple callers retry simultaneously.
    """
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise  # Final attempt failed, propagate
            
            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            logger.warning(
                f"Attempt {attempt + 1} failed: {e}. "
                f"Retrying in {delay:.1f}s..."
            )
            time.sleep(delay)
```

---

## Exercise: Extend the Gateway for Your Organization

Add custom routing rules that reflect your organization's requirements:

```python
class CustomAIGateway(AIGateway):
    """Extended gateway with organization-specific routing rules."""
    
    def route(self, query: str, sensitivity: str = "low",
              complexity: str = "medium", latency: str = "normal",
              **kwargs) -> dict:
        
        # Custom rule: After business hours, prefer cheaper providers
        if self._is_off_hours():
            if sensitivity != "high":
                return self._try_with_fallback(query,
                    preferred=[Provider.LOCAL, Provider.ENTERPRISE])
        
        # Custom rule: During incidents, prefer fastest available
        if kwargs.get("incident_active"):
            return self._try_with_fallback(query,
                preferred=[Provider.LOCAL, Provider.CLOUD, Provider.ENTERPRISE])
        
        # Custom rule: Specific teams always use enterprise
        if kwargs.get("team") in ["security", "compliance", "finance"]:
            return self._call_with_metrics(Provider.ENTERPRISE, query)
        
        # Fall through to default routing
        return super().route(query, sensitivity, complexity, latency)
    
    def _is_off_hours(self) -> bool:
        """Check if current time is outside business hours."""
        from datetime import datetime
        hour = datetime.now().hour
        return hour < 8 or hour > 18
```

**Challenge ideas:**
1. Add a cost tracker that switches to cheaper models when budget threshold is hit
2. Implement request queuing for non-urgent queries during peak load
3. Add A/B testing — route 10% of traffic to a new model and compare quality
4. Build a feedback loop — if users report bad responses, adjust routing weights

---

## What Success Looks Like

After completing this lab, you can verify:

- [x] Your gateway routes sensitive data exclusively to the enterprise provider
- [x] Fast/simple queries hit the local provider first (sub-second response)
- [x] Complex queries route to the most capable model available
- [x] When a provider fails, the circuit breaker opens and traffic reroutes automatically
- [x] When a failed provider recovers, the circuit breaker gradually closes
- [x] Health checks proactively detect provider issues
- [x] Metrics give you visibility into routing patterns and provider performance
- [x] The gateway handles total provider failure gracefully (all circuits open = clear error)

---

## Key Takeaway

> **Production AI needs the same resilience patterns as any distributed system — circuit breakers, fallbacks, health checks, and intelligent routing.**

You would never deploy a production service with a single database, no connection pooling, no retry logic, and no health checks. AI providers deserve the same engineering rigor.

The gateway pattern gives you:
- **Resilience:** No single provider failure takes down your AI capability
- **Compliance:** Sensitive data automatically stays within governed boundaries
- **Cost control:** Cheap models handle simple tasks; expensive models handle hard ones
- **Observability:** You know exactly where your AI traffic goes and how it performs

This is not over-engineering. This is treating AI as what it is in production: a distributed dependency that can fail, that costs money, and that handles sensitive data. Engineer it accordingly.
