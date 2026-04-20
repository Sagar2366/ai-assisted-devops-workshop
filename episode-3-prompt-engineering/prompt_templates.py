"""
Episode 3: Prompt Engineering for DevOps
File: prompt_templates.py — Production-Ready Prompt Templates for DevOps

Author: Sagar Utekar
Prerequisites: Anthropic API key working; Python anthropic package installed (pip install anthropic)

Contains 4 production templates:
  1. incident_commander — Assess severity, root cause, mitigation, comms
  2. code_reviewer_sre — Review K8s manifests / Terraform for production readiness
  3. postmortem_writer — Generate blameless postmortems from incident data
  4. terraform_reviewer — Review Terraform for safety, cost, and blast radius
"""
import anthropic

client = anthropic.Anthropic()

TEMPLATES = {
    "incident_commander": """You are an Incident Commander for a production outage.

## Current Incident
{incident_details}

## Your Responsibilities:
1. Assess severity (P1-P4) based on blast radius and duration
2. Identify the most likely root cause from available data
3. Recommend immediate mitigation (not root cause fix)
4. Draft customer communication if P1/P2
5. Assign follow-up actions

## Output Format:
**Severity:** P[1-4] — [reason]
**Blast Radius:** [affected users/services]
**Root Cause Hypothesis:** [most likely cause]
**Immediate Mitigation:**
- Step 1: [action + command]
- Step 2: [action + command]
**Customer Comms:** [draft if P1/P2, "N/A" if P3/P4]
**Follow-ups:**
- [ ] [action item + owner]""",

    "code_reviewer_sre": """You are reviewing a Kubernetes manifest or Terraform file for production readiness.

## Review the following:
{code}

## Check for:
1. **Resource Limits** — Are CPU/memory requests and limits set?
2. **Health Checks** — Are liveness and readiness probes configured?
3. **Security** — Is it running as non-root? Are security contexts set?
4. **High Availability** — Pod disruption budgets? Anti-affinity?
5. **Observability** — Are labels/annotations set for monitoring?
6. **Networking** — Network policies? Service mesh annotations?

## Output Format:
For each issue:
- CRITICAL / WARNING / INFO
- What's wrong
- How to fix (with code snippet)""",

    "postmortem_writer": """You are writing a blameless postmortem.

## Incident Data:
{incident_data}

## Write a postmortem following this structure:
1. **Title:** Brief, descriptive
2. **Summary:** 2-3 sentences
3. **Impact:** Duration, affected users, revenue impact
4. **Timeline:** Chronological events (detect → respond → mitigate → resolve)
5. **Root Cause:** Technical explanation
6. **Contributing Factors:** What made it worse
7. **What Went Well:** Things that worked
8. **What Went Wrong:** Things that failed
9. **Action Items:** Specific, assigned, with due dates
10. **Lessons Learned:** Key takeaways

Keep it blameless — focus on systems, not people.""",

    "terraform_reviewer": """You are reviewing Terraform code for an AWS infrastructure change.

## Code:
{code}

## Check for:
1. **State Safety** — Will this destroy/recreate resources unexpectedly?
2. **Cost Impact** — Estimated cost change?
3. **Security** — Public access, encryption, IAM permissions?
4. **Blast Radius** — What depends on changed resources?
5. **Rollback Plan** — How to undo if something goes wrong?

## Output:
- RISK LEVEL: LOW / MEDIUM / HIGH / CRITICAL
- Changes Summary (create/modify/destroy counts)
- Issues found (with severity)
- Estimated cost delta
- Recommended: APPROVE / APPROVE WITH CHANGES / BLOCK"""
}


if __name__ == "__main__":
    # Demo: Use the incident commander template
    incident = """
- Alert: HTTP 5xx rate > 10% on checkout service
- Started: 14:30 UTC (45 minutes ago)
- Affected: All checkout attempts failing for EU region
- Recent change: DNS migration to Route53 completed 2 hours ago
- Monitoring shows: checkout pods healthy, database healthy, but EU traffic hitting US endpoints
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": TEMPLATES["incident_commander"].format(incident_details=incident)
        }]
    )
    print(response.content[0].text)
