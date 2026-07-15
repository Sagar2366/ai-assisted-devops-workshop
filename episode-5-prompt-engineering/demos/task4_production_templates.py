#!/usr/bin/env python3
"""
Production Prompt Templates for SRE
====================================

Creating reusable prompt templates for common SRE tasks.
These templates standardize how we interact with AI for operational work,
ensuring consistent, high-quality outputs across the team.

Prerequisites:
    - anthropic SDK: pip install anthropic
    - ANTHROPIC_API_KEY environment variable set
"""

import anthropic

client = anthropic.Anthropic()

print("=" * 65)
print("TASK 4: Production Prompt Templates for SRE")
print("=" * 65)
print()
print("Building reusable, parameterized prompt templates that")
print("standardize AI-assisted SRE workflows.")
print()


# =============================================================================
# Template 1: Incident Triage
# =============================================================================

def incident_triage_prompt(alert_name, metric_value, threshold, service, namespace):
    """Generate a prompt for triaging a specific alert."""
    return f"""You are an experienced SRE performing incident triage.

Alert Details:
- Alert Name: {alert_name}
- Current Metric Value: {metric_value}
- Threshold: {threshold}
- Affected Service: {service}
- Namespace: {namespace}

Provide triage steps for this alert:
1. Immediate assessment of severity and blast radius
2. Key metrics and logs to check first
3. Potential root causes ranked by likelihood
4. Recommended immediate actions
5. Escalation criteria

Be specific to this service and alert type. Format your response with clear headers and actionable steps."""


# =============================================================================
# Template 2: Runbook Generation
# =============================================================================

def runbook_generation_prompt(service_name, failure_mode, dependencies):
    """Generate a prompt to create a runbook for a specific failure mode."""
    deps_formatted = ", ".join(dependencies)
    return f"""You are an SRE technical writer creating operational runbooks.

Create a runbook for the following scenario:
- Service: {service_name}
- Failure Mode: {failure_mode}
- Dependencies: {deps_formatted}

The runbook should include:
1. Title and severity classification
2. Detection (how this failure manifests in monitoring)
3. Impact assessment template
4. Step-by-step diagnosis procedure
5. Remediation steps (with commands where applicable)
6. Verification steps to confirm resolution
7. Post-incident cleanup
8. Prevention recommendations

Make the runbook actionable for an on-call engineer who may not be familiar with this specific service. Include specific commands and queries where possible."""


# =============================================================================
# Template 3: Postmortem Draft
# =============================================================================

def postmortem_draft_prompt(incident_title, timeline, impact, root_cause):
    """Generate a prompt to draft a postmortem document."""
    return f"""You are an SRE helping draft a blameless postmortem document.

Incident Details:
- Title: {incident_title}
- Timeline: {timeline}
- Impact: {impact}
- Root Cause: {root_cause}

Draft a postmortem document with the following sections:
1. Executive Summary (2-3 sentences)
2. Impact Summary (quantified)
3. Timeline of Events (formatted table)
4. Root Cause Analysis (using 5 Whys technique)
5. Contributing Factors
6. What Went Well
7. What Could Be Improved
8. Action Items (with owners placeholder and priority)
9. Lessons Learned

Follow blameless postmortem principles. Focus on systems and processes, not individuals. Include specific, measurable action items."""


# =============================================================================
# Template 4: Change Review
# =============================================================================

def change_review_prompt(change_type, diff_content, environment):
    """Generate a prompt to review a proposed change."""
    return f"""You are a senior SRE reviewing a proposed change before deployment.

Change Details:
- Change Type: {change_type}
- Target Environment: {environment}
- Diff Content:
```
{diff_content}
```

Review this change for:
1. Potential risks and failure modes
2. Rollback strategy adequacy
3. Impact on dependent services
4. Resource implications (CPU, memory, network)
5. Security considerations
6. Compliance with SRE best practices
7. Missing safeguards (health checks, resource limits, etc.)
8. Recommended improvements

Provide a risk rating (Low/Medium/High/Critical) with justification. List any blocking concerns that should prevent deployment."""


# =============================================================================
# Demo: Template 1 - Incident Triage
# =============================================================================

print("=" * 65)
print("TEMPLATE 1: Incident Triage")
print("=" * 65)
print()

prompt = incident_triage_prompt(
    alert_name="HighMemoryUsage",
    metric_value="92%",
    threshold="85%",
    service="payment-service",
    namespace="production"
)

print("-" * 65)
print("Generated Prompt:")
print("-" * 65)
print(prompt)
print()

print("-" * 65)
print("API Response:")
print("-" * 65)

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)
print(message.content[0].text)
print()


# =============================================================================
# Demo: Template 2 - Runbook Generation
# =============================================================================

print("=" * 65)
print("TEMPLATE 2: Runbook Generation")
print("=" * 65)
print()

prompt = runbook_generation_prompt(
    service_name="payment-service",
    failure_mode="database connection pool exhaustion",
    dependencies=["PostgreSQL", "Redis", "API Gateway"]
)

print("-" * 65)
print("Generated Prompt:")
print("-" * 65)
print(prompt)
print()

print("-" * 65)
print("API Response:")
print("-" * 65)

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)
print(message.content[0].text)
print()


# =============================================================================
# Demo: Template 3 - Postmortem Draft
# =============================================================================

print("=" * 65)
print("TEMPLATE 3: Postmortem Draft")
print("=" * 65)
print()

prompt = postmortem_draft_prompt(
    incident_title="Payment Processing Outage - 2024-01-15",
    timeline="14:32 UTC - Alert fired for elevated error rates\n"
             "14:35 UTC - On-call engineer acknowledged\n"
             "14:42 UTC - Root cause identified as connection pool exhaustion\n"
             "14:48 UTC - Connection pool limits increased\n"
             "14:55 UTC - Service recovery confirmed\n"
             "15:10 UTC - All-clear declared",
    impact="23 minutes of degraded payment processing. "
           "1,247 failed transactions affecting 892 customers. "
           "Estimated revenue impact: $45,000.",
    root_cause="Database connection pool was configured with a max of 20 connections. "
               "A traffic spike from a flash sale caused connection requests to exceed "
               "the pool capacity, leading to request queuing and eventual timeouts."
)

print("-" * 65)
print("Generated Prompt:")
print("-" * 65)
print(prompt)
print()

print("-" * 65)
print("API Response:")
print("-" * 65)

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)
print(message.content[0].text)
print()


# =============================================================================
# Demo: Template 4 - Change Review
# =============================================================================

print("=" * 65)
print("TEMPLATE 4: Change Review")
print("=" * 65)
print()

k8s_diff = """--- a/deployments/payment-service.yaml
+++ b/deployments/payment-service.yaml
@@ -18,7 +18,7 @@ spec:
       containers:
       - name: payment-service
-        image: payment-service:v2.3.1
+        image: payment-service:v2.4.0
         resources:
           requests:
-            memory: "256Mi"
-            cpu: "250m"
+            memory: "512Mi"
+            cpu: "500m"
           limits:
-            memory: "512Mi"
-            cpu: "500m"
+            memory: "1Gi"
+            cpu: "1000m"
+        readinessProbe:
+          httpGet:
+            path: /health/ready
+            port: 8080
+          initialDelaySeconds: 10
+          periodSeconds: 5"""

prompt = change_review_prompt(
    change_type="Kubernetes Deployment Update",
    diff_content=k8s_diff,
    environment="production"
)

print("-" * 65)
print("Generated Prompt:")
print("-" * 65)
print(prompt)
print()

print("-" * 65)
print("API Response:")
print("-" * 65)

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)
print(message.content[0].text)
print()


# =============================================================================
# Key Learning
# =============================================================================

print("=" * 65)
print("Key Learning: Template Reusability")
print("=" * 65)
print()
print("Production prompt templates provide:")
print()
print("1. CONSISTENCY - Every team member gets the same quality output")
print("   regardless of their prompt engineering experience.")
print()
print("2. PARAMETERIZATION - Templates accept dynamic inputs, making")
print("   them adaptable to any service, alert, or incident.")
print()
print("3. STANDARDIZATION - Outputs follow your organization's")
print("   format requirements (postmortem structure, runbook format).")
print()
print("4. INSTITUTIONAL KNOWLEDGE - Best practices are encoded into")
print("   the templates themselves (blameless culture, 5 Whys, etc).")
print()
print("5. VERSIONING - Templates can be version-controlled, reviewed,")
print("   and improved over time just like any other code artifact.")
print()
print("Build a library of templates for your most common SRE tasks")
print("and share them across your team for maximum impact.")
print()
print("=" * 65)
print("Next: task5_testing_framework.py")
print("=" * 65)
