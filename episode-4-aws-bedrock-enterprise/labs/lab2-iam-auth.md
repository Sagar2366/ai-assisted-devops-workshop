# Lab 2: IAM Authentication — Least-Privilege for AI Workloads

> **Mission:** Set up least-privilege IAM policies for AI workloads, just like you would set up RBAC in Kubernetes. By the end of this lab, you will have three role-based policies and understand when to apply each one.

---

## Concept: IAM for AI is Like RBAC for Kubernetes

If you have worked with Kubernetes RBAC, you already know this pattern:

```
Kubernetes RBAC                    AWS IAM for Bedrock
--------------                    -------------------
ClusterRole                   =   IAM Policy
RoleBinding                   =   Policy Attachment
ServiceAccount                =   IAM Role
Namespace scope               =   Resource ARN scope
"get,list" on pods            =   "bedrock:InvokeModel" on specific model
cluster-admin                 =   "bedrock:*" on "*"
```

The principle is identical: **give each identity only the permissions it needs, nothing more.**

Just as you would never give every pod `cluster-admin`, you should not give every service full Bedrock access. An on-call triage bot only needs to invoke one model. A cost-optimization script does not need guardrail management permissions. A junior analyst should not be able to call expensive models without oversight.

---

## The Three-Tier Access Model

For most SRE organizations, three tiers cover the common scenarios:

```
                    ┌─────────────────────┐
                    │   ADMIN             │
                    │   bedrock:*         │
                    │   (Platform team)   │
                    └─────────┬───────────┘
                              │
                    ┌─────────┴───────────┐
                    │   FULL SRE          │
                    │   Invoke any model  │
                    │   + List models     │
                    │   (SRE team)        │
                    └─────────┬───────────┘
                              │
                    ┌─────────┴───────────┐
                    │   READ-ONLY ANALYST │
                    │   Invoke one model  │
                    │   (Automated tools) │
                    └─────────────────────┘
```

---

## Policy 1: Read-Only Analyst

**Who uses this:** Automated triage bots, monitoring integrations, junior team members.

**What it allows:** Invoke a single, specific model — nothing else.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["bedrock:InvokeModel"],
    "Resource": ["arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-sonnet-4-20250514-v1:0"]
  }]
}
```

**Why this matters:** If this credential leaks, the attacker can only call one model in one region. They cannot list other models, enable new ones, modify guardrails, or access any other Bedrock feature.

**Kubernetes equivalent:** A ServiceAccount with a Role that only allows `get` on ConfigMaps in one namespace.

---

## Policy 2: Full SRE

**Who uses this:** On-call engineers, SRE automation platforms, incident response tooling.

**What it allows:** Invoke any model (for flexibility during incidents), stream responses, and list available models.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:ListFoundationModels"],
    "Resource": ["*"]
  }]
}
```

**Why this matters:** During an incident, you may need to switch models (e.g., use a faster model for triage, then a more capable model for deep analysis). This policy allows model flexibility without granting administrative control.

**Kubernetes equivalent:** A ClusterRole that allows `get`, `list`, `watch` on most resources but cannot `create` or `delete`.

---

## Policy 3: Admin

**Who uses this:** Platform engineering team, security team, Bedrock administrators.

**What it allows:** Full Bedrock access including guardrail management, model access configuration, and provisioned throughput.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["bedrock:*"],
    "Resource": ["*"]
  }]
}
```

**Why this matters:** Only a small number of people should be able to modify guardrails (content filters), enable new models, or manage provisioned throughput (which has cost implications). This is your `cluster-admin` equivalent.

**Kubernetes equivalent:** `cluster-admin` ClusterRoleBinding.

---

## Role Assumption for Cross-Account Access

In enterprise environments, your AI workloads often run in a different account than your identity account. The STS AssumeRole pattern handles this — the same way you might assume a role to access a production cluster.

```python
"""
Cross-Account Bedrock Access via STS AssumeRole
Demonstrates assuming a role in another account to call Bedrock.
"""

import boto3
import json

print("=" * 65)
print("CROSS-ACCOUNT BEDROCK ACCESS VIA STS ASSUME ROLE")
print("=" * 65)

# Step 1: Assume a role in the target account
sts_client = boto3.client("sts")

print("\nAssuming role in AI workloads account...")
print("-" * 65)

assumed_role = sts_client.assume_role(
    RoleArn="arn:aws:iam::987654321098:role/SRE-Bedrock-Access",
    RoleSessionName="incident-response-session",
    DurationSeconds=3600  # 1 hour — enough for an incident
)

credentials = assumed_role["Credentials"]
print(f"Role assumed successfully")
print(f"Session expires: {credentials['Expiration']}")
print("-" * 65)

# Step 2: Create a Bedrock client with the assumed role credentials
bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
    aws_access_key_id=credentials["AccessKeyId"],
    aws_secret_access_key=credentials["SecretAccessKey"],
    aws_session_token=credentials["SessionToken"]
)

# Step 3: Make the Bedrock call with assumed credentials
print("\nInvoking Claude with cross-account credentials...")

response = bedrock_client.invoke_model(
    modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-10-25",
        "max_tokens": 512,
        "messages": [{
            "role": "user",
            "content": "List 3 key metrics to monitor after a database failover."
        }]
    })
)

result = json.loads(response["body"].read())
print(f"\nResponse received:")
print("-" * 65)
print(result["content"][0]["text"])
print("=" * 65)
```

### Trust Policy (on the target role)

The role in the AI workloads account needs a trust policy that allows your identity account to assume it:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "AWS": "arn:aws:iam::123456789012:root"
    },
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "aws:PrincipalTag/team": "sre"
      }
    }
  }]
}
```

---

## Exercise: Create a Scoped Policy and Test Access

In this exercise, you will create the Read-Only Analyst policy, attach it to a test role, and verify it works — and verify it denies what it should deny.

```python
"""
Exercise: Create and Test a Scoped IAM Policy for Bedrock
Demonstrates creating a least-privilege policy and verifying access.
"""

import boto3
import json

print("=" * 65)
print("EXERCISE: SCOPED IAM POLICY FOR BEDROCK")
print("=" * 65)

iam = boto3.client("iam")

# Define the least-privilege policy
policy_document = {
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "AllowSingleModelInvoke",
        "Effect": "Allow",
        "Action": ["bedrock:InvokeModel"],
        "Resource": [
            "arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-sonnet-4-20250514-v1:0"
        ]
    }]
}

print("\nPolicy to create:")
print("-" * 65)
print(json.dumps(policy_document, indent=2))
print("-" * 65)

# Create the policy
try:
    response = iam.create_policy(
        PolicyName="BedrockReadOnlyAnalyst-Lab2",
        Description="Lab 2: Allows invoking only Claude Sonnet via Bedrock",
        PolicyDocument=json.dumps(policy_document)
    )
    policy_arn = response["Policy"]["Arn"]
    print(f"\n[PASS] Policy created: {policy_arn}")
except iam.exceptions.EntityAlreadyExistsException:
    account_id = boto3.client("sts").get_caller_identity()["Account"]
    policy_arn = f"arn:aws:iam::{account_id}:policy/BedrockReadOnlyAnalyst-Lab2"
    print(f"\n[INFO] Policy already exists: {policy_arn}")

print("-" * 65)

# Verify: What this policy ALLOWS
print("\nAccess verification matrix:")
print("-" * 65)
print(f"  {'Action':<45} {'Result'}")
print(f"  {'------':<45} {'------'}")
print(f"  {'bedrock:InvokeModel (Claude Sonnet)':<45} {'ALLOW'}")
print(f"  {'bedrock:InvokeModel (Llama)':<45} {'DENY'}")
print(f"  {'bedrock:ListFoundationModels':<45} {'DENY'}")
print(f"  {'bedrock:CreateGuardrail':<45} {'DENY'}")
print(f"  {'bedrock:InvokeModelWithResponseStream':<45} {'DENY'}")

print("\n" + "=" * 65)
print("POLICY COMPARISON SUMMARY")
print("=" * 65)
print(f"\n  {'Role':<20} {'Models':<15} {'Stream':<10} {'List':<10} {'Admin'}")
print(f"  {'-'*20} {'-'*15} {'-'*10} {'-'*10} {'-'*10}")
print(f"  {'Analyst':<20} {'1 model':<15} {'No':<10} {'No':<10} {'No'}")
print(f"  {'Full SRE':<20} {'All models':<15} {'Yes':<10} {'Yes':<10} {'No'}")
print(f"  {'Admin':<20} {'All models':<15} {'Yes':<10} {'Yes':<10} {'Yes'}")
print("=" * 65)
```

---

## Best Practices for Production

```python
print("=" * 65)
print("IAM BEST PRACTICES FOR AI WORKLOADS")
print("=" * 65)

best_practices = [
    ("Use resource-level ARNs", 
     "Scope to specific models, not wildcard (*)"),
    ("Add conditions",
     "Restrict by source IP, VPC, or time of day"),
    ("Tag-based access control",
     "Use aws:ResourceTag to limit by environment"),
    ("Session duration limits",
     "Short-lived sessions (1hr) for incident response"),
    ("Separate accounts",
     "AI workloads in dedicated account, assume role in"),
    ("Enable CloudTrail",
     "Every InvokeModel call is logged with full context"),
    ("Set budget alerts",
     "AI costs can spike during incidents — set thresholds"),
    ("Rotate credentials",
     "Use IAM roles (auto-rotate) over access keys"),
]

for i, (practice, detail) in enumerate(best_practices, 1):
    print(f"\n  {i}. {practice}")
    print(f"     {detail}")

print("\n" + "=" * 65)
```

---

## Condition Keys for Advanced Scoping

For organizations that need finer-grained control:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["bedrock:InvokeModel"],
    "Resource": ["arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-sonnet-4-20250514-v1:0"],
    "Condition": {
      "StringEquals": {
        "aws:RequestedRegion": "us-east-1"
      },
      "IpAddress": {
        "aws:SourceIp": "10.0.0.0/8"
      },
      "DateLessThan": {
        "aws:CurrentTime": "2026-12-31T23:59:59Z"
      }
    }
  }]
}
```

This policy allows model invocation ONLY when:
- The request targets `us-east-1`
- It comes from your internal network (`10.0.0.0/8`)
- It is before the policy expiration date (forcing periodic review)

---

## What Success Looks Like

After completing this lab:

1. You can articulate which IAM policy tier applies to each team role
2. You understand the mapping between Kubernetes RBAC concepts and IAM
3. You can create a scoped policy that limits access to a single model
4. You know how to use STS AssumeRole for cross-account Bedrock access
5. You can explain why `bedrock:*` on `*` is the equivalent of `cluster-admin`

---

## Key Takeaway

**Treat AI access like any other cloud resource — least privilege, audit trail, role-based access.** The same security principles you apply to databases, storage, and compute apply to AI models. The only difference is the action names (`bedrock:InvokeModel` instead of `s3:GetObject`). If you can write a Kubernetes RBAC policy, you can write a Bedrock IAM policy. The mental model is identical.
