#!/usr/bin/env python3
"""
Task 5: Multi-Provider Gateway
===============================

A production-grade multi-provider AI gateway implementing the
"Three Rings" fallback pattern for SRE workloads:
  Ring 1: Ollama (local) - fastest, zero cost, full data privacy
  Ring 2: Claude API (cloud) - high quality, moderate cost
  Ring 3: AWS Bedrock (enterprise) - governed, auditable, compliant

Features:
  - Circuit breaker pattern (track failures per provider)
  - Health check for each provider
  - Retry with exponential backoff
  - Realistic SRE scenario (incident analysis query)
  - Cost tracking per provider
  - Response time comparison

Prerequisites:
  pip install boto3 anthropic requests
"""

import json
import time
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("[WARN] 'requests' not installed - Ollama provider unavailable")

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("[WARN] 'anthropic' not installed - Claude API provider unavailable")

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
    print("[WARN] 'boto3' not installed - AWS Bedrock provider unavailable")


# =============================================================================
# Circuit Breaker Pattern
# =============================================================================

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"        # Normal operation - requests flow through
    OPEN = "OPEN"            # Failures exceeded threshold - reject fast
    HALF_OPEN = "HALF_OPEN"  # Testing recovery - allow one probe request


@dataclass
class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures per provider.

    State transitions:
      CLOSED -> OPEN: when failure_count >= threshold
      OPEN -> HALF_OPEN: after recovery_timeout elapses
      HALF_OPEN -> CLOSED: on success
      HALF_OPEN -> OPEN: on failure
    """
    provider_name: str
    failure_threshold: int = 3
    recovery_timeout: float = 30.0  # seconds before HALF_OPEN probe
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    state: CircuitState = CircuitState.CLOSED

    def record_success(self):
        """Reset circuit breaker on successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    def record_failure(self):
        """Track failure and trip breaker if threshold reached."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def allow_request(self) -> bool:
        """Check if the circuit breaker allows a request through."""
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if self.last_failure_time and \
               (time.time() - self.last_failure_time) >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        # HALF_OPEN: allow one test request
        return True


# =============================================================================
# Cost Tracker
# =============================================================================

@dataclass
class CostTracker:
    """Track costs and usage per provider."""
    records: dict = field(default_factory=lambda: {
        "ollama": {"requests": 0, "total_cost_usd": 0.0, "total_tokens_est": 0},
        "claude_api": {"requests": 0, "total_cost_usd": 0.0, "total_tokens_est": 0},
        "bedrock": {"requests": 0, "total_cost_usd": 0.0, "total_tokens_est": 0},
    })

    # Approximate cost per 1K tokens (blended input + output)
    COST_PER_1K_TOKENS = {
        "ollama": 0.0,        # Local inference - zero API cost
        "claude_api": 0.008,  # Claude 3.5 Sonnet direct pricing
        "bedrock": 0.010,     # Bedrock Claude with AWS governance markup
    }

    def record_usage(self, provider: str, estimated_tokens: int = 600):
        """Record a request and estimate cost."""
        if provider in self.records:
            self.records[provider]["requests"] += 1
            self.records[provider]["total_tokens_est"] += estimated_tokens
            cost = (estimated_tokens / 1000.0) * self.COST_PER_1K_TOKENS.get(provider, 0)
            self.records[provider]["total_cost_usd"] += cost

    def get_summary(self) -> str:
        """Return formatted cost summary."""
        lines = []
        total_cost = 0.0
        total_requests = 0
        for provider, data in self.records.items():
            if data["requests"] > 0:
                lines.append(
                    f"    {provider:>12}: {data['requests']:>3} requests, "
                    f"~{data['total_tokens_est']:>5} tokens, "
                    f"${data['total_cost_usd']:.4f}"
                )
                total_cost += data["total_cost_usd"]
                total_requests += data["requests"]
        if not lines:
            lines.append("    (no requests recorded in this session)")
        lines.append(f"    {'TOTAL':>12}: {total_requests:>3} requests, "
                     f"${total_cost:.4f}")
        return "\n".join(lines)


# =============================================================================
# Provider Implementations
# =============================================================================

class OllamaProvider:
    """Ring 1: Local Ollama instance - zero cost, lowest latency."""

    def __init__(self, base_url="http://localhost:11434", model="llama3.2"):
        self.base_url = base_url
        self.model = model
        self.name = "ollama"

    def health_check(self) -> bool:
        """Check if Ollama is running and responsive."""
        if not HAS_REQUESTS:
            return False
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def query(self, prompt: str) -> str:
        """Send a query to Ollama."""
        if not HAS_REQUESTS:
            raise RuntimeError("requests library not available")
        resp = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")


class ClaudeAPIProvider:
    """Ring 2: Anthropic Claude API (cloud) - high quality reasoning."""

    def __init__(self, model="claude-sonnet-4-20250514"):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = model
        self.name = "claude_api"

    def health_check(self) -> bool:
        """Check if Claude API credentials are configured."""
        if not HAS_ANTHROPIC:
            return False
        if not self.api_key:
            return False
        return self.api_key.startswith("sk-ant-")

    def query(self, prompt: str) -> str:
        """Send a query to Claude API using the anthropic library."""
        if not HAS_ANTHROPIC:
            raise RuntimeError("anthropic library not available")
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")

        client = anthropic.Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text


class BedrockProvider:
    """Ring 3: AWS Bedrock (enterprise) - governed, auditable, compliant."""

    def __init__(self, region="us-east-1",
                 model_id="us.anthropic.claude-sonnet-4-20250514-v1:0"):
        self.region = region
        self.model_id = model_id
        self.name = "bedrock"

    def health_check(self) -> bool:
        """Check if AWS Bedrock credentials are configured."""
        if not HAS_BOTO3:
            return False
        try:
            sts = boto3.client("sts")
            sts.get_caller_identity()
            return True
        except Exception:
            return False

    def query(self, prompt: str) -> str:
        """Send a query to AWS Bedrock."""
        if not HAS_BOTO3:
            raise RuntimeError("boto3 library not available")

        client = boto3.client("bedrock-runtime", region_name=self.region)
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.1,
            "messages": [{"role": "user", "content": prompt}],
        })
        response = client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=body,
        )
        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]


# =============================================================================
# Multi-Provider Gateway
# =============================================================================

class MultiProviderGateway:
    """
    AI Gateway implementing the Three Rings fallback pattern.

    Routing priority (try in order):
      1. Ollama (local) - zero cost, lowest latency, full privacy
      2. Claude API (cloud) - high quality, moderate cost
      3. AWS Bedrock (enterprise) - governed, auditable, highest cost
    """

    def __init__(self):
        self.providers = [
            OllamaProvider(),
            ClaudeAPIProvider(),
            BedrockProvider(),
        ]
        self.circuit_breakers = {
            p.name: CircuitBreaker(provider_name=p.name)
            for p in self.providers
        }
        self.cost_tracker = CostTracker()
        self.response_times = {}

    def health_check_all(self) -> dict:
        """Run health checks on all providers."""
        results = {}
        for provider in self.providers:
            healthy = provider.health_check()
            results[provider.name] = healthy
        return results

    def _retry_with_backoff(self, provider, prompt: str,
                            max_retries: int = 3) -> str:
        """
        Retry a provider query with exponential backoff.

        Backoff schedule: 0.5s, 1.0s, 2.0s
        """
        for attempt in range(max_retries):
            try:
                start = time.time()
                result = provider.query(prompt)
                elapsed = time.time() - start

                # Record metrics on success
                self.response_times[provider.name] = elapsed
                self.circuit_breakers[provider.name].record_success()
                self.cost_tracker.record_usage(provider.name)
                return result

            except Exception as e:
                wait_time = 0.5 * (2 ** attempt)  # 0.5s, 1.0s, 2.0s
                if attempt < max_retries - 1:
                    print(f"      [{provider.name}] Attempt {attempt + 1} failed: "
                          f"{type(e).__name__}")
                    print(f"      [{provider.name}] Retrying in {wait_time:.1f}s "
                          f"(exponential backoff)...")
                    time.sleep(wait_time)
                else:
                    # Final attempt failed - trip circuit breaker
                    self.circuit_breakers[provider.name].record_failure()
                    raise

    def query(self, prompt: str) -> tuple:
        """
        Route query through the Three Rings fallback chain.

        Order: Ollama (local) -> Claude API (cloud) -> Bedrock (enterprise)
        Skips providers with tripped circuit breakers or failed health checks.

        Returns:
            tuple: (response_text, provider_name) or raises RuntimeError
        """
        errors = []

        for provider in self.providers:
            breaker = self.circuit_breakers[provider.name]

            # Check circuit breaker
            if not breaker.allow_request():
                print(f"      [{provider.name}] Circuit breaker "
                      f"{breaker.state.value} - skipping")
                errors.append((provider.name, "Circuit breaker open"))
                continue

            # Check provider health
            if not provider.health_check():
                print(f"      [{provider.name}] Health check failed - skipping")
                errors.append((provider.name, "Health check failed"))
                continue

            # Attempt query with retry and exponential backoff
            try:
                print(f"      [{provider.name}] Attempting query...")
                result = self._retry_with_backoff(provider, prompt)
                elapsed = self.response_times.get(provider.name, 0)
                print(f"      [{provider.name}] Success! ({elapsed:.2f}s)")
                return result, provider.name
            except Exception as e:
                print(f"      [{provider.name}] All retries exhausted: {e}")
                errors.append((provider.name, str(e)))
                continue

        # All providers in the chain failed
        error_summary = "; ".join(f"{name}: {err}" for name, err in errors)
        raise RuntimeError(f"All providers failed - {error_summary}")

    def get_circuit_status(self) -> dict:
        """Get circuit breaker status for all providers."""
        return {
            name: {
                "state": cb.state.value,
                "failures": cb.failure_count,
                "threshold": cb.failure_threshold,
            }
            for name, cb in self.circuit_breakers.items()
        }


# =============================================================================
# SRE Incident Analysis Scenario
# =============================================================================

SRE_INCIDENT_PROMPT = """You are an SRE assistant. Analyze this production incident:

INCIDENT REPORT:
- Service: payment-gateway (Kubernetes, 12 replicas)
- Alert: P99 latency exceeded 5s (SLO threshold: 2s)
- Duration: 15 minutes and counting
- Impact: 12% of transactions timing out, revenue loss ~$4,200/min
- Recent changes: Deployed v2.4.1 (added retry logic to upstream calls)
- Metrics:
  * CPU utilization: 45% (normal)
  * Memory utilization: 62% (normal)
  * Connection pool: 95% capacity (CRITICAL)
  * Upstream timeout rate: 34% (was 2% before deploy)
  * Active threads per pod: 847 (normal: ~200)

Provide a concise analysis:
1. Most likely root cause (one sentence)
2. Immediate mitigation action
3. Long-term fix recommendation

Keep response under 100 words."""


# =============================================================================
# Main Demo
# =============================================================================

def main():
    print("=" * 65)
    print("  TASK 5: Multi-Provider Gateway")
    print("  Three Rings Pattern: Local -> Cloud -> Enterprise")
    print("=" * 65)
    print()

    gateway = MultiProviderGateway()

    # -----------------------------------------------------------------
    # Experiment 1: Provider Health Checks
    # -----------------------------------------------------------------
    print("-" * 65)
    print("  Experiment 1: Provider Health Checks")
    print("-" * 65)
    print()

    health = gateway.health_check_all()
    provider_labels = {
        "ollama": "Ring 1 - Ollama (local)",
        "claude_api": "Ring 2 - Claude API (cloud)",
        "bedrock": "Ring 3 - AWS Bedrock (enterprise)",
    }

    for provider_name, is_healthy in health.items():
        status = "HEALTHY" if is_healthy else "UNAVAILABLE"
        icon = "[OK]" if is_healthy else "[--]"
        label = provider_labels.get(provider_name, provider_name)
        print(f"    {icon} {label:<38} {status}")

    available_count = sum(1 for v in health.values() if v)
    print()
    print(f"    Available providers: {available_count}/3")

    if available_count == 0:
        print()
        print("    NOTE: No providers currently available for live queries.")
        print("    To enable providers:")
        print("      - Ollama: Install and run 'ollama serve'")
        print("      - Claude API: export ANTHROPIC_API_KEY=sk-ant-...")
        print("      - Bedrock: aws configure (with bedrock:InvokeModel access)")
        print()
        print("    Running in demonstration mode with simulated responses.")
    print()

    # -----------------------------------------------------------------
    # Experiment 2: Gateway Routing with Fallback (SRE Scenario)
    # -----------------------------------------------------------------
    print("-" * 65)
    print("  Experiment 2: Gateway Routing with Fallback")
    print("-" * 65)
    print()
    print("    SRE Scenario: Production Incident Analysis")
    print("    Service: payment-gateway | Alert: P99 latency breach")
    print()
    print("    Fallback chain: Ollama -> Claude API -> AWS Bedrock")
    print()

    try:
        response, used_provider = gateway.query(SRE_INCIDENT_PROMPT)
        print()
        print(f"    Response from [{used_provider}]:")
        print("    " + "-" * 50)
        for line in response.strip().split("\n"):
            print(f"      {line}")
        print("    " + "-" * 50)
    except RuntimeError as e:
        print(f"      [gateway] All providers unavailable: {e}")
        print()
        print("    Simulated incident analysis (demonstration):")
        print("    " + "-" * 50)
        print("      1. Root cause: New retry logic in v2.4.1 multiplied")
        print("         upstream connections 3x, exhausting the connection")
        print("         pool and causing thread starvation across all pods.")
        print("      2. Immediate mitigation: Rollback to v2.4.0 or set")
        print("         max retries to 1 with a 500ms timeout cap.")
        print("      3. Long-term fix: Implement circuit breaker pattern on")
        print("         upstream calls with adaptive pool sizing based on")
        print("         retry configuration and load-shedding at saturation.")
        print("    " + "-" * 50)
    print()

    # -----------------------------------------------------------------
    # Experiment 3: Circuit Breaker Status
    # -----------------------------------------------------------------
    print("-" * 65)
    print("  Experiment 3: Circuit Breaker Status")
    print("-" * 65)
    print()
    print("    Current circuit breaker state per provider:")
    print()

    status = gateway.get_circuit_status()
    print(f"    {'Provider':<12} {'State':<12} {'Failures':<12} {'Threshold'}")
    print(f"    {'-'*12} {'-'*12} {'-'*12} {'-'*10}")
    for name, info in status.items():
        print(f"    {name:<12} {info['state']:<12} "
              f"{info['failures']:<12} {info['threshold']}")
    print()

    # -----------------------------------------------------------------
    # Experiment 4: Simulated Circuit Breaker Trip
    # -----------------------------------------------------------------
    print("-" * 65)
    print("  Experiment 4: Circuit Breaker Trip Simulation")
    print("-" * 65)
    print()
    print("    Simulating consecutive failures to show state transitions:")
    print()

    sim_breaker = CircuitBreaker(provider_name="ollama_sim", failure_threshold=3)
    print(f"    Initial: state={sim_breaker.state.value}, "
          f"failures={sim_breaker.failure_count}")

    for i in range(1, 4):
        sim_breaker.record_failure()
        print(f"    After failure {i}: state={sim_breaker.state.value}, "
              f"failures={sim_breaker.failure_count}, "
              f"allows_request={sim_breaker.allow_request()}")

    print()
    print("    Simulating recovery timeout elapsed (30s)...")
    sim_breaker.last_failure_time = time.time() - 31
    allows = sim_breaker.allow_request()
    print(f"    After timeout: state={sim_breaker.state.value}, "
          f"allows_request={allows}")

    sim_breaker.record_success()
    print(f"    After success: state={sim_breaker.state.value}, "
          f"failures={sim_breaker.failure_count}")
    print()
    print("    State Machine:")
    print("      CLOSED --(3 failures)--> OPEN --(30s timeout)--> HALF_OPEN")
    print("      HALF_OPEN --(success)--> CLOSED")
    print("      HALF_OPEN --(failure)--> OPEN")
    print()

    # -----------------------------------------------------------------
    # Experiment 5: Response Time Comparison
    # -----------------------------------------------------------------
    print("-" * 65)
    print("  Experiment 5: Response Time Comparison")
    print("-" * 65)
    print()

    if gateway.response_times:
        print("    Measured response times from live queries:")
        print()
        sorted_times = sorted(gateway.response_times.items(), key=lambda x: x[1])
        for name, elapsed in sorted_times:
            bar_len = int(elapsed * 10)
            bar = "#" * min(bar_len, 40)
            print(f"    {name:>12}: {elapsed:6.2f}s |{bar}|")
        print()
        fastest = sorted_times[0]
        print(f"    Fastest provider: {fastest[0]} ({fastest[1]:.2f}s)")
    else:
        print("    No live response times recorded (providers unavailable).")
        print()
        print("    Typical latency ranges in production:")
        print(f"      {'ollama':<12}: 0.5 - 3.0s  (local GPU, no network hop)")
        print(f"      {'claude_api':<12}: 1.0 - 5.0s  (network + inference)")
        print(f"      {'bedrock':<12}: 1.5 - 6.0s  (AWS routing + inference)")
        print()
        print("    The Three Rings pattern always tries the fastest provider")
        print("    first (local), falling back only when unavailable.")
    print()

    # -----------------------------------------------------------------
    # Experiment 6: Cost Tracking per Provider
    # -----------------------------------------------------------------
    print("-" * 65)
    print("  Experiment 6: Cost Tracking per Provider")
    print("-" * 65)
    print()
    print("    Session cost breakdown:")
    print()
    print(gateway.cost_tracker.get_summary())
    print()
    print("    Cost model (per 1K tokens):")
    print(f"      {'ollama':<12}: $0.0000  (free - local inference)")
    print(f"      {'claude_api':<12}: $0.0080  (Anthropic direct pricing)")
    print(f"      {'bedrock':<12}: $0.0100  (includes AWS governance markup)")
    print()
    print("    Cost optimization strategy:")
    print("      - Route high-volume, simple queries to Ollama ($0)")
    print("      - Use Claude API for quality-critical analysis")
    print("      - Reserve Bedrock for compliance-required workloads")
    print("      - 80% of SRE queries can use the cheapest provider")
    print()

    # -----------------------------------------------------------------
    # Key Learning
    # -----------------------------------------------------------------
    print("=" * 65)
    print("  Key Learning: The Three Rings Pattern")
    print("  (local -> cloud -> enterprise)")
    print("=" * 65)
    print()
    print("    The Three Rings pattern provides defense-in-depth for AI:")
    print()
    print("    Ring 1 - Local (Ollama):")
    print("      - Zero cost, lowest latency, full data privacy")
    print("      - Best for: development, sensitive data, high-volume queries")
    print("      - Trade-off: limited model capability, local GPU required")
    print()
    print("    Ring 2 - Cloud (Claude API):")
    print("      - Moderate cost, highest quality reasoning")
    print("      - Best for: complex incident analysis, root cause investigation")
    print("      - Trade-off: data traverses network, usage-based billing")
    print()
    print("    Ring 3 - Enterprise (AWS Bedrock):")
    print("      - Highest cost, full governance and audit trail")
    print("      - Best for: regulated workloads, compliance (SOC2/HIPAA/GDPR)")
    print("      - Trade-off: additional latency, vendor coupling")
    print()
    print("    Combined with circuit breakers, health checks, and exponential")
    print("    backoff, this pattern maximizes availability while optimizing")
    print("    for cost and performance. The gateway routes transparently -")
    print("    application code never needs to know which provider responded.")
    print()
    print("=" * 65)
    print("  Episode 4 Complete!")
    print("=" * 65)


if __name__ == "__main__":
    main()
