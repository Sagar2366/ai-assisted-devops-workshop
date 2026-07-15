# Lab 4: Production SRE Prompt Templates

## Mission

Build 4 production-ready, parameterized prompt templates for daily SRE work. These templates combine the techniques from previous labs (zero-shot structure, few-shot examples, chain-of-thought reasoning) into reusable tools your team can adopt immediately.

---

## Concept: Prompts as Reusable Tools

Production prompt templates are like well-written functions:
- They have **clear inputs** (parameters/placeholders)
- They produce **consistent outputs** (structured format)
- They are **tested** (you know what good output looks like)
- They are **documented** (other team members can use them)

Think of this as building your team's AI-powered SRE toolkit. Each template encodes your team's best practices into a repeatable process that works at 3am when the on-call engineer is half asleep.

---

## Template 1: Incident Triage

### Purpose

Rapidly assess an incoming alert and produce a structured triage decision with severity, impact, and immediate actions.

### Template Code

```python
from sre_prompt import call_claude_with_system

INCIDENT_TRIAGE_SYSTEM = """You are a senior SRE performing incident triage.
You follow the incident management framework strictly.
Always respond in the exact format specified. Never deviate from the format.
Base severity on customer impact, not on the alert's own severity label."""

INCIDENT_TRIAGE_TEMPLATE = """Triage the following alert and provide a structured assessment.

## Alert Data
- Alert Name: {alert_name}
- Service: {service_name}
- Severity Label: {severity_label}
- Current Value: {current_value}
- Threshold: {threshold}
- Duration: {duration}
- Environment: {environment}
- Additional Context: {additional_context}

## Response Format (follow exactly):

SEVERITY: [SEV1 | SEV2 | SEV3 | SEV4]
CONFIDENCE: [HIGH | MEDIUM | LOW]
SUMMARY: [One sentence describing the issue]
IMPACT: [Who/what is affected]
IMMEDIATE_ACTION: [First thing to do right now]
INVESTIGATION_COMMANDS:
1. [First command to run]
2. [Second command to run]
3. [Third command to run]
ESCALATION: [YES/NO - should we page additional people?]
ESCALATION_TARGET: [Team or person to escalate to, if applicable]
COMMUNICATION: [What to post in #incidents channel]
"""


def triage_incident(
    alert_name: str,
    service_name: str,
    severity_label: str,
    current_value: str,
    threshold: str,
    duration: str,
    environment: str = "production",
    additional_context: str = "None"
) -> str:
    """Triage an incident and return structured assessment."""
    prompt = INCIDENT_TRIAGE_TEMPLATE.format(
        alert_name=alert_name,
        service_name=service_name,
        severity_label=severity_label,
        current_value=current_value,
        threshold=threshold,
        duration=duration,
        environment=environment,
        additional_context=additional_context
    )
    return call_claude_with_system(INCIDENT_TRIAGE_SYSTEM, prompt)
```

### Example Usage

```python
result = triage_incident(
    alert_name="HighErrorRate",
    service_name="checkout-service",
    severity_label="critical",
    current_value="15% error rate",
    threshold="1% error rate",
    duration="8 minutes",
    environment="production",
    additional_context="Last deployment was 2 hours ago. No recent config changes. "
                       "Downstream payment-provider reported degradation on their status page 5 minutes ago."
)

print(result)
```

### Expected Output

```
SEVERITY: SEV2
CONFIDENCE: HIGH
SUMMARY: Checkout service experiencing 15% error rate likely due to downstream payment provider degradation.
IMPACT: Users unable to complete purchases, estimated 15% of checkout attempts failing.
IMMEDIATE_ACTION: Confirm payment provider status page degradation, enable fallback payment flow if available.
INVESTIGATION_COMMANDS:
1. kubectl logs -n production -l app=checkout-service --tail=100 | grep -i error
2. curl -s https://status.stripe.com/api/v2/summary.json | jq .
3. kubectl exec -n production deploy/checkout-service -- wget -qO- http://payment-provider:8080/health
ESCALATION: NO
ESCALATION_TARGET: N/A - external dependency issue, monitor provider status
COMMUNICATION: "Investigating elevated error rates on checkout-service. Preliminary analysis suggests downstream payment provider degradation. Monitoring - will update in 15 minutes."
```

---

## Template 2: Runbook Generation

### Purpose

Generate a structured runbook for a specific service failure mode that any on-call engineer can follow.

### Template Code

```python
from sre_prompt import call_claude_with_system

RUNBOOK_SYSTEM = """You are a senior SRE writing runbooks for your team.
Your runbooks are used by on-call engineers at 3am who may not be familiar with this service.
Be explicit, include exact commands, and never assume knowledge.
Every command must be copy-pasteable. Include expected output where possible."""

RUNBOOK_TEMPLATE = """Generate a production runbook for the following scenario.

## Service Information
- Service Name: {service_name}
- Service Description: {service_description}
- Infrastructure: {infrastructure}
- Dependencies: {dependencies}

## Failure Mode
- Failure: {failure_mode}
- Symptoms: {symptoms}
- Typical Cause: {typical_cause}

## Generate runbook in this format:

# Runbook: [Service] - [Failure Mode]

## Quick Reference
- **Service Owner**: [team]
- **Escalation Path**: [path]
- **Expected Recovery Time**: [time]
- **Customer Impact**: [impact description]

## Detection
How you know this is happening (alerts, dashboards, user reports).

## Immediate Actions (first 5 minutes)
Numbered steps with exact commands. Focus on mitigation, not root cause.

## Diagnosis
Step-by-step investigation to identify root cause. Include:
- Commands to run
- What to look for in the output
- Decision tree (if X then do Y, if Z then do W)

## Resolution
For each common root cause, provide exact fix steps.

## Verification
How to confirm the fix worked. Include:
- Commands to check service health
- Expected healthy output
- How long to monitor before closing

## Escalation Criteria
When to escalate, who to page, what information to include.

## Post-Incident
- Metrics to check 1 hour after recovery
- Follow-up tasks to create
"""


def generate_runbook(
    service_name: str,
    service_description: str,
    infrastructure: str,
    dependencies: str,
    failure_mode: str,
    symptoms: str,
    typical_cause: str
) -> str:
    """Generate a runbook for a specific failure mode."""
    prompt = RUNBOOK_TEMPLATE.format(
        service_name=service_name,
        service_description=service_description,
        infrastructure=infrastructure,
        dependencies=dependencies,
        failure_mode=failure_mode,
        symptoms=symptoms,
        typical_cause=typical_cause
    )
    return call_claude_with_system(RUNBOOK_SYSTEM, prompt, max_tokens=2048)
```

### Example Usage

```python
runbook = generate_runbook(
    service_name="payment-service",
    service_description="Handles all payment processing including credit card charges, refunds, and subscription billing",
    infrastructure="Kubernetes (EKS), 3 replicas, HPA enabled, deployed in us-east-1",
    dependencies="PostgreSQL (RDS), Redis (ElastiCache), Stripe API, auth-service",
    failure_mode="Database Connection Pool Exhaustion",
    symptoms="HTTP 503 errors, 'connection pool exhausted' in logs, increasing request queue depth",
    typical_cause="Connection leak after timeout, or sudden traffic spike exceeding pool capacity"
)

print(runbook)
```

### Expected Output (abbreviated)

```
# Runbook: payment-service - Database Connection Pool Exhaustion

## Quick Reference
- **Service Owner**: payments-team
- **Escalation Path**: payments-team → platform-team → VP Engineering
- **Expected Recovery Time**: 5-15 minutes
- **Customer Impact**: Payment processing blocked for all users

## Detection
- Alert: PaymentServiceHighErrorRate (>1% 5xx responses)
- Dashboard: Grafana → Payment Service → Connection Pool panel
- Symptom: "connection pool exhausted" in application logs

## Immediate Actions (first 5 minutes)
1. Check current connection count:
   kubectl exec -n production deploy/payment-service -- curl localhost:8080/metrics | grep db_pool

2. Restart pods to release connections (rolling restart):
   kubectl rollout restart deployment/payment-service -n production

3. Verify recovery:
   kubectl get pods -n production -l app=payment-service -w
...
```

---

## Template 3: Postmortem Generation

### Purpose

Generate a structured, blameless postmortem document from incident timeline and impact data.

### Template Code

```python
from sre_prompt import call_claude_with_system

POSTMORTEM_SYSTEM = """You are writing a blameless postmortem following SRE best practices.
Focus on systems and processes, never individuals.
Be specific about timelines and impact numbers.
Action items must be concrete, assigned to teams (not individuals), and have deadlines.
Use the 5 Whys technique to dig into root cause."""

POSTMORTEM_TEMPLATE = """Generate a structured postmortem from the following incident data.

## Incident Information
- Incident ID: {incident_id}
- Date: {incident_date}
- Duration: {duration}
- Severity: {severity}
- Services Affected: {services_affected}

## Impact
- Users Affected: {users_affected}
- Revenue Impact: {revenue_impact}
- SLA Impact: {sla_impact}

## Timeline
{timeline}

## Root Cause (if known)
{root_cause}

## What Was Tried During Incident
{actions_taken}

## Generate postmortem in this format:

# Postmortem: [Descriptive Title]

## Summary
[2-3 sentences: what happened, impact, duration]

## Impact
| Metric | Value |
|--------|-------|
| Duration | |
| Users Affected | |
| Revenue Impact | |
| SLA Budget Consumed | |

## Timeline (UTC)
| Time | Event |
|------|-------|
[Formatted timeline]

## Root Cause Analysis
[Detailed explanation using 5 Whys technique]

## Contributing Factors
[What conditions allowed this to happen?]

## What Went Well
[Things that worked during incident response]

## What Went Wrong
[Things that did not work or were missing]

## Action Items
| Priority | Action | Owner Team | Deadline | Tracking |
|----------|--------|------------|----------|----------|
[Concrete action items]

## Lessons Learned
[Key takeaways for the organization]

## Detection Improvement
- Time to detect: [duration]
- How could we detect it faster?
- New alerts to add:

## Recurrence Risk
- Without fixes: [HIGH/MEDIUM/LOW]
- With action items completed: [expected risk level]
"""


def generate_postmortem(
    incident_id: str,
    incident_date: str,
    duration: str,
    severity: str,
    services_affected: str,
    users_affected: str,
    revenue_impact: str,
    sla_impact: str,
    timeline: str,
    root_cause: str,
    actions_taken: str
) -> str:
    """Generate a structured postmortem document."""
    prompt = POSTMORTEM_TEMPLATE.format(
        incident_id=incident_id,
        incident_date=incident_date,
        duration=duration,
        severity=severity,
        services_affected=services_affected,
        users_affected=users_affected,
        revenue_impact=revenue_impact,
        sla_impact=sla_impact,
        timeline=timeline,
        root_cause=root_cause,
        actions_taken=actions_taken
    )
    return call_claude_with_system(POSTMORTEM_SYSTEM, prompt, max_tokens=2048)
```

### Example Usage

```python
postmortem = generate_postmortem(
    incident_id="INC-2024-0342",
    incident_date="2024-03-15",
    duration="47 minutes",
    severity="SEV1",
    services_affected="checkout-service, payment-service, order-service",
    users_affected="~12,000 users unable to complete purchases",
    revenue_impact="Estimated $45,000 in lost transactions",
    sla_impact="Monthly error budget reduced by 35%",
    timeline="""
14:00 - Normal operations
14:15 - Deploy auth-service v3.2.0 (new OAuth2 token caching)
14:20 - Auth-service memory climbs from 512MB to 1.8GB
14:25 - Redis connections spike from 100 to 2,400
14:28 - Payment-service: Redis timeout errors begin
14:30 - Order-service latency: 50ms -> 4,200ms
14:32 - PagerDuty alert: payment-service error rate > 5%
14:35 - On-call engineer acknowledges alert
14:40 - Incident bridge opened, SEV1 declared
14:45 - Auth-service identified as trigger, rollback initiated
14:50 - Auth-service v3.1.9 deployed (rollback)
14:55 - Redis connections returning to normal
15:02 - All services recovered, error rates nominal
""",
    root_cause="Auth-service v3.2.0 introduced an OAuth2 token caching layer that created a new Redis connection per cached token instead of reusing a connection pool. This exhausted the shared Redis cluster's max connections limit (2,500), starving downstream services.",
    actions_taken="""
- Identified auth-service deployment as correlated event (5 min)
- Attempted to scale Redis (failed - managed service limit)
- Rolled back auth-service to v3.1.9 (5 min)
- Monitored recovery for 12 minutes
"""
)

print(postmortem)
```

---

## Template 4: Change Review

### Purpose

Assess risk of infrastructure changes (Terraform, Kubernetes manifests) before applying to production.

### Template Code

```python
from sre_prompt import call_claude_with_system

CHANGE_REVIEW_SYSTEM = """You are a senior SRE reviewing infrastructure changes before production apply.
Your job is to identify risks, suggest safeguards, and recommend approval or rejection.
Be specific about what could go wrong and how to mitigate it.
Always consider: blast radius, reversibility, timing, dependencies, and recent incidents.
Err on the side of caution - it is better to delay a risky change than to cause an outage."""

CHANGE_REVIEW_TEMPLATE = """Review this infrastructure change and provide a risk assessment.

## Change Details
- Change Type: {change_type}
- Target Environment: {environment}
- Submitted By: {submitted_by}
- Planned Execution Time: {execution_time}
- Change Description: {description}

## The Diff
```
{diff}
```

## Context
- Services in blast radius: {blast_radius}
- Current system health: {system_health}
- Recent incidents: {recent_incidents}
- Upcoming events: {upcoming_events}

## Provide assessment in this format:

RISK_LEVEL: [LOW | MEDIUM | HIGH | CRITICAL]
APPROVAL: [APPROVE | APPROVE_WITH_CONDITIONS | REJECT]

### Change Summary
[What this change does in plain English]

### Risk Analysis
For each individual change in the diff:
- What it does
- What could go wrong
- Blast radius
- Reversibility (easy/hard/impossible)
- Estimated downtime risk

### Combined Risk Factors
[Interactions between changes that increase overall risk]

### Prerequisites
[Things that must be true before applying]

### Recommended Safeguards
1. [Safeguard with specific implementation]
2. [Safeguard with specific implementation]
3. [Safeguard with specific implementation]

### Execution Plan
[Recommended order of operations and verification steps between each]

### Rollback Plan
[Exact steps to reverse if something goes wrong, with time estimates]

### Conditions (if APPROVE_WITH_CONDITIONS)
[What must be done before/during/after applying]
"""


def review_change(
    change_type: str,
    environment: str,
    submitted_by: str,
    execution_time: str,
    description: str,
    diff: str,
    blast_radius: str,
    system_health: str,
    recent_incidents: str = "None in last 7 days",
    upcoming_events: str = "None"
) -> str:
    """Review an infrastructure change and return risk assessment."""
    prompt = CHANGE_REVIEW_TEMPLATE.format(
        change_type=change_type,
        environment=environment,
        submitted_by=submitted_by,
        execution_time=execution_time,
        description=description,
        diff=diff,
        blast_radius=blast_radius,
        system_health=system_health,
        recent_incidents=recent_incidents,
        upcoming_events=upcoming_events
    )
    return call_claude_with_system(CHANGE_REVIEW_SYSTEM, prompt, max_tokens=2048)
```

### Example Usage

```python
review = review_change(
    change_type="Terraform",
    environment="production",
    submitted_by="platform-team",
    execution_time="Tuesday 2pm UTC (business hours)",
    description="Scale database and adjust autoscaling parameters",
    diff="""resource "aws_db_instance" "primary" {
-  instance_class = "db.r5.xlarge"
+  instance_class = "db.r5.2xlarge"
   apply_immediately = true
}

resource "aws_security_group_rule" "api_to_db" {
-  from_port = 5432
-  to_port   = 5432
+  from_port = 5432
+  to_port   = 5433
   cidr_blocks = ["10.0.0.0/16"]
}

resource "aws_autoscaling_group" "api" {
-  min_size = 3
-  max_size = 10
+  min_size = 2
+  max_size = 15
}""",
    blast_radius="api-service, payment-service, order-service (all use this database)",
    system_health="All services green, no active alerts",
    recent_incidents="INC-342: Redis connection exhaustion 3 days ago (resolved)",
    upcoming_events="Black Friday sale in 2 weeks"
)

print(review)
```

### Expected Output (abbreviated)

```
RISK_LEVEL: HIGH
APPROVAL: APPROVE_WITH_CONDITIONS

### Change Summary
Three changes: (1) upgrade RDS instance from xlarge to 2xlarge, (2) modify security group port rule, (3) reduce minimum ASG size while increasing maximum.

### Risk Analysis

**Change 1: RDS Instance Resize**
- What it does: Doubles database compute capacity
- What could go wrong: apply_immediately=true will cause a brief outage during modification
- Blast radius: All 3 services using this database
- Reversibility: Easy (resize back down, but another outage)
- Estimated downtime: 5-10 minutes during Multi-AZ failover

**Change 2: Security Group Port Modification**
- What it does: Changes allowed port from 5432 to 5433
- What could go wrong: If database is still on 5432, ALL connections will be blocked immediately
- Blast radius: Complete database connectivity loss for all services
- Reversibility: Easy (revert the rule) but damage is immediate
- Estimated downtime: Until reverted (seconds to apply, but outage is instant)

**Change 3: ASG min_size reduction**
- What it does: Allows scaling down to 2 instances (from 3)
- What could go wrong: During low traffic, could scale to 2 and lose HA...
...

### Conditions
1. Remove apply_immediately=true or schedule during maintenance window
2. Confirm database is actually running on port 5433 before applying security group change
3. Do NOT reduce min_size to 2 with Black Friday in 2 weeks — keep at 3 minimum
```

---

## Putting It All Together: The SRE Toolkit

Create a unified module your team can import:

```python
# sre_toolkit.py - Your team's AI-powered SRE toolkit

from sre_prompt import call_claude_with_system


class SREToolkit:
    """Collection of production SRE prompt templates.
    
    Usage:
        toolkit = SREToolkit()
        result = toolkit.triage(alert_name="HighCPU", service_name="api", ...)
    """

    def triage(self, **kwargs) -> str:
        """Quick incident triage from alert data."""
        return triage_incident(**kwargs)

    def runbook(self, **kwargs) -> str:
        """Generate a runbook for a failure mode."""
        return generate_runbook(**kwargs)

    def postmortem(self, **kwargs) -> str:
        """Generate a postmortem from incident data."""
        return generate_postmortem(**kwargs)

    def change_review(self, **kwargs) -> str:
        """Review an infrastructure change for risk."""
        return review_change(**kwargs)


# Quick CLI usage
if __name__ == "__main__":
    import sys

    toolkit = SREToolkit()

    if len(sys.argv) < 2:
        print("Usage: python sre_toolkit.py [triage|runbook|postmortem|review]")
        sys.exit(1)

    command = sys.argv[1]
    
    if command == "triage":
        # Interactive triage
        print(toolkit.triage(
            alert_name=input("Alert name: "),
            service_name=input("Service: "),
            severity_label=input("Severity label: "),
            current_value=input("Current value: "),
            threshold=input("Threshold: "),
            duration=input("Duration: "),
        ))
```

---

## What Success Looks Like

After completing this lab, you have:

- 4 production-ready prompt templates that produce consistent, structured output
- Parameterized functions your entire team can use during on-call shifts
- Templates that combine system prompts (role/rules) with user prompts (data/format)
- A reusable toolkit pattern for building new templates for your specific workflows
- Understanding of how to encode team knowledge into prompt templates

Your templates should produce outputs that are:
- Consistently formatted (same structure every time)
- Actionable (specific commands, not vague advice)
- Complete (all required fields filled in)
- Contextual (using the provided data, not generic responses)

---

## Key Takeaway

Production prompt templates transform AI from a toy into a tool. By standardizing inputs (parameters), outputs (structured format), and behavior (system prompts with rules), you create reliable, repeatable workflows that any team member can use. The key is treating prompts like code: parameterized, documented, tested, and version-controlled. In the next lab, we will build the testing framework to ensure these templates keep working as you iterate on them.

---

## Next

[Lab 5: Testing Framework](lab5-testing-framework.md) — Build regression tests for your prompt templates
