#!/usr/bin/env python3
"""
Few-Shot Prompting for DevOps
==============================

Few-shot prompting provides examples to guide the model's responses.
By showing labeled examples of inputs and expected outputs, we teach
the model the pattern, format, and reasoning style we expect - without
any fine-tuning or additional training.

This technique is especially powerful for:
- Classification tasks (severity levels, incident categories)
- Consistent formatting of outputs
- Domain-specific reasoning patterns

Prerequisites:
- pip install anthropic
- export ANTHROPIC_API_KEY="your-api-key"
"""

import anthropic

client = anthropic.Anthropic()


def call_claude(prompt, max_tokens=1024):
    """Send a prompt to Claude and return the response text."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# =============================================================================
# EXPERIMENT 1: Severity Classification with Few-Shot Examples
# =============================================================================

print("=" * 65)
print("EXPERIMENT 1: Severity Classification with Few-Shot Examples")
print("=" * 65)
print()
print("Goal: Teach the model to classify incident severity using")
print("labeled examples of P1, P2, and P3 incidents.")
print()

# Build the few-shot prompt with labeled examples
severity_prompt = """You are an SRE incident classifier. Based on the alert description, classify the severity as P1, P2, or P3.

Here are labeled examples:

---
Example 1:
Alert: "Production database cluster primary node is unreachable. All write operations are failing. Customer-facing API returning 500 errors across all regions."
Classification: P1 - Critical
Reasoning: Complete loss of write capability affecting all customers across all regions. This is a total service outage.

---
Example 2:
Alert: "Kubernetes pod memory usage on checkout-service has exceeded 85% threshold. Auto-scaling has triggered but new pods are taking 45 seconds to become ready."
Classification: P2 - High
Reasoning: Service degradation with increased latency, but auto-scaling is mitigating. Not a complete outage but requires prompt attention.

---
Example 3:
Alert: "Certificate for internal monitoring dashboard expires in 14 days. Grafana dashboards may become inaccessible if not renewed."
Classification: P3 - Medium
Reasoning: No immediate customer impact. Internal tooling affected with ample time to remediate before expiry.

---
Now classify this new alert:

Alert: "Redis sentinel has detected master failover in the session-store cluster. Failover completed in 3.2 seconds but 12 active connections were dropped. Users report intermittent login failures for approximately 15 seconds."
Classification:"""

print("Prompt being sent to Claude:")
print("-" * 65)
print(severity_prompt)
print("-" * 65)
print()

print("Claude's Response:")
print("-" * 65)
response = call_claude(severity_prompt)
print(response)
print("-" * 65)
print()


# =============================================================================
# EXPERIMENT 2: Root Cause Categorization with Few-Shot Examples
# =============================================================================

print("=" * 65)
print("EXPERIMENT 2: Root Cause Categorization with Few-Shot Examples")
print("=" * 65)
print()
print("Goal: Categorize incidents into root cause categories using")
print("labeled examples to guide consistent classification.")
print()

root_cause_prompt = """You are a DevOps root cause analyst. Categorize the following incident into one of these root cause categories:
- Resource Exhaustion
- Configuration Drift
- Dependency Failure
- Code Defect
- Security Incident
- Infrastructure Failure

Here are labeled examples:

---
Example 1:
Incident: "The order-processing service started returning OOMKilled errors at 02:14 UTC. Pod memory limits were set to 512Mi but a recent deployment introduced an unbounded in-memory cache that grew to 2GB under peak load."
Root Cause Category: Resource Exhaustion
Explanation: The service exceeded its allocated memory limits due to unbounded resource consumption (in-memory cache without eviction policy).

---
Example 2:
Incident: "Production Nginx ingress controller started routing traffic to staging backend services after a Helm chart upgrade. The values.yaml in production had not been updated to reflect new upstream service names introduced in v2.4.0."
Root Cause Category: Configuration Drift
Explanation: Production configuration was out of sync with the expected state after an upgrade. The Helm values diverged from what the new chart version required.

---
Example 3:
Incident: "Payment processing halted at 14:30 UTC. Investigation revealed that the third-party payment gateway (Stripe) was experiencing a regional outage in us-east-1. Our retry logic exhausted all attempts within 30 seconds."
Root Cause Category: Dependency Failure
Explanation: An external service dependency became unavailable, and our system's resilience mechanisms (retries) were insufficient to handle the duration of the outage.

---
Example 4:
Incident: "The Kubernetes cluster nodes in zone-b became unreachable after an AWS availability zone experienced network connectivity issues. Pod evictions triggered but PodDisruptionBudgets prevented sufficient replicas from scheduling in healthy zones."
Root Cause Category: Infrastructure Failure
Explanation: Underlying cloud infrastructure failure in a specific availability zone caused node-level failures beyond the application's control.

---
Now categorize this new incident:

Incident: "Deployment pipeline pushed a Terraform change that modified the security group rules for the database tier. The change removed the ingress rule allowing traffic from the application subnet (10.0.2.0/24). All application-to-database connections failed immediately after apply. The Terraform state showed the rule was present in the previous plan but a teammate had manually deleted it from the console last week, causing Terraform to treat it as a new addition and then remove it during reconciliation."
Root Cause Category:"""

print("Prompt being sent to Claude:")
print("-" * 65)
print(root_cause_prompt)
print("-" * 65)
print()

print("Claude's Response:")
print("-" * 65)
response = call_claude(root_cause_prompt)
print(response)
print("-" * 65)
print()


# =============================================================================
# EXPERIMENT 3: Zero-Shot vs Few-Shot Comparison
# =============================================================================

print("=" * 65)
print("EXPERIMENT 3: Zero-Shot vs Few-Shot Comparison")
print("=" * 65)
print()
print("Goal: Demonstrate the difference in output quality and")
print("consistency between zero-shot and few-shot prompting")
print("on the same input.")
print()

# The alert we want to analyze
test_alert = "Kubernetes CrashLoopBackOff detected on pod analytics-worker-7f8b9c6d4-xk2mv in namespace data-pipeline. Container restarted 5 times in the last 10 minutes. Last exit code: 137. Node memory pressure detected on node pool-standard-2xlarge-03."

# --- Zero-Shot Version ---
print("--- ZERO-SHOT APPROACH ---")
print("-" * 65)

zero_shot_prompt = f"""Analyze this Kubernetes alert and provide a structured incident response:

Alert: "{test_alert}"

Provide: severity, likely cause, immediate actions, and follow-up tasks."""

print("Zero-Shot Prompt:")
print(zero_shot_prompt)
print("-" * 65)
print()

print("Zero-Shot Response:")
print("-" * 65)
zero_shot_response = call_claude(zero_shot_prompt)
print(zero_shot_response)
print("-" * 65)
print()

# --- Few-Shot Version ---
print("--- FEW-SHOT APPROACH ---")
print("-" * 65)

few_shot_prompt = f"""You are a Kubernetes incident responder. Analyze alerts and provide structured incident responses following this exact format.

Here are examples of properly analyzed alerts:

---
Example 1:
Alert: "OOMKilled on pod payment-service-5d4f8c7b2-abc12 in namespace payments. Container restarted 3 times in 5 minutes. Last exit code: 137. Memory usage peaked at 498Mi against 512Mi limit."
Analysis:
  Severity: P2 - High
  Likely Cause: Memory limit exceeded. Exit code 137 indicates OOMKill. Container memory peaked near its 512Mi limit suggesting either a memory leak or insufficient resource allocation.
  Immediate Actions:
    1. Check recent deployments to payments namespace for code changes
    2. Review memory usage trends: kubectl top pod -n payments
    3. Temporarily increase memory limit if safe: kubectl set resources deployment/payment-service -n payments --limits=memory=1Gi
  Follow-up Tasks:
    1. Profile application memory usage under load
    2. Review heap dump if available
    3. Update resource requests/limits based on actual usage patterns
    4. Add memory usage alerting at 70% threshold

---
Example 2:
Alert: "ImagePullBackOff on pod frontend-v2-6c9d8e5f3-def45 in namespace web. Failed to pull image: registry.internal.io/frontend:v2.3.1. Error: unauthorized."
Analysis:
  Severity: P2 - High
  Likely Cause: Container registry authentication failure. The image exists but credentials are invalid or expired. This often occurs when image pull secrets expire or are rotated without updating the cluster.
  Immediate Actions:
    1. Verify image pull secret: kubectl get secret regcred -n web -o yaml
    2. Check if secret has expired: decode and inspect token expiry
    3. Recreate pull secret if expired: kubectl create secret docker-registry regcred --docker-server=registry.internal.io --docker-username=<user> --docker-password=<new-token> -n web
  Follow-up Tasks:
    1. Implement automated secret rotation with external-secrets operator
    2. Set up monitoring for secret expiry dates
    3. Document registry credential renewal process
    4. Consider using workload identity for registry access

---
Now analyze this new alert using the same structured format:

Alert: "{test_alert}"
Analysis:"""

print("Few-Shot Prompt:")
print(few_shot_prompt)
print("-" * 65)
print()

print("Few-Shot Response:")
print("-" * 65)
few_shot_response = call_claude(few_shot_prompt)
print(few_shot_response)
print("-" * 65)
print()

# --- Comparison Summary ---
print("--- COMPARISON SUMMARY ---")
print("-" * 65)
print("Zero-shot: The model generates a reasonable response but the")
print("format, depth, and structure may vary unpredictably.")
print()
print("Few-shot: The model follows the demonstrated format precisely,")
print("providing consistent structure (Severity, Likely Cause,")
print("Immediate Actions, Follow-up Tasks) with similar depth and")
print("actionable specificity as the examples.")
print()
print("Key differences you may observe:")
print("  1. FORMAT: Few-shot responses match the example structure exactly")
print("  2. DEPTH: Examples set the expectation for level of detail")
print("  3. ACTIONABILITY: Examples demonstrate specific kubectl commands")
print("  4. CONSISTENCY: Few-shot produces predictable, parseable output")
print("-" * 65)
print()


# =============================================================================
# KEY LEARNING
# =============================================================================

print("=" * 65)
print("KEY LEARNING: Few-Shot Prompting Strengths")
print("=" * 65)
print()
print("1. PATTERN TEACHING: Examples implicitly teach the model the")
print("   expected output format without explicit format instructions.")
print()
print("2. DOMAIN CALIBRATION: Labeled examples anchor the model's")
print("   understanding of domain-specific concepts (e.g., what")
print("   constitutes P1 vs P2 in YOUR organization).")
print()
print("3. CONSISTENCY: Few-shot produces more predictable outputs,")
print("   making it easier to parse responses programmatically.")
print()
print("4. REDUCED AMBIGUITY: Rather than describing what you want,")
print("   you SHOW what you want through concrete examples.")
print()
print("5. QUALITY FLOOR: Examples set a minimum quality bar - the")
print("   model will try to match or exceed the demonstrated level")
print("   of detail and specificity.")
print()
print("Best Practices for DevOps Few-Shot Prompts:")
print("  - Use 2-5 diverse examples covering different scenarios")
print("  - Include edge cases that clarify boundaries (e.g., P1 vs P2)")
print("  - Keep examples realistic and from your actual environment")
print("  - Label examples clearly with separators for readability")
print("  - Include reasoning to teach the 'why' not just the 'what'")
print()
print("=" * 65)
print("Next: task3_chain_of_thought.py - Chain-of-thought prompting")
print("      for complex multi-step DevOps reasoning tasks")
print("=" * 65)
