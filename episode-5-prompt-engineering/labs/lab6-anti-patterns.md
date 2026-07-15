# Lab 6: Prompt Engineering Anti-Patterns for DevOps

## Mission

Learn to identify and fix common prompt mistakes in a DevOps context. Bad prompts produce bad results, even when you are using the most capable model available. This lab walks through six critical anti-patterns, demonstrates why each one fails, and shows you how to fix it.

---

## Why This Matters

As an SRE or DevOps engineer, you will interact with AI assistants during incident response, infrastructure automation, capacity planning, and more. The quality of the output you receive is directly proportional to the quality of the prompt you provide. A poorly constructed prompt can waste precious minutes during an outage or generate dangerous infrastructure changes that could cause further damage.

**The core principle:** Garbage in, garbage out -- even with the best model.

---

## Anti-Pattern 1: Vague Asks

### The Bad Prompt

```python
import anthropic

client = anthropic.Anthropic()

# BAD: Vague ask with no specifics
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Fix my pod"
        }
    ]
)

print(message.content[0].text)
```

### Why It Fails

This prompt gives the model almost nothing to work with:

- **Which pod?** There could be hundreds of pods across multiple namespaces.
- **What is wrong?** Is it crashing, pending, evicted, OOMKilled, in a CrashLoopBackOff?
- **What cluster?** Production, staging, development?
- **What has been tried?** Has the pod been restarted? Have logs been checked?

The model is forced to guess or ask a series of follow-up questions, wasting time that could be critical during an incident.

### The Fixed Prompt

```python
import anthropic

client = anthropic.Anthropic()

# GOOD: Specific, actionable, context-rich
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": """My pod 'payment-service-7b4d8f6c9-x2vnl' in the 'production' namespace
is in CrashLoopBackOff. It started failing 10 minutes ago after we deployed
image tag v2.3.1 (previous working tag was v2.3.0).

The container exit code is 137 (OOMKilled). The pod resource limits are set
to 512Mi memory. Our monitoring shows the pod memory usage was climbing
steadily before the kill.

What are the most likely causes and what steps should I take to resolve this?"""
        }
    ]
)

print(message.content[0].text)
```

### Key Difference

The fixed prompt provides the pod name, namespace, symptom, timeline, what changed, exit code, resource limits, and observed behavior. The model can now give a targeted, actionable response instead of a generic troubleshooting guide.

---

## Anti-Pattern 2: Missing Context (No Logs, No Error)

### The Bad Prompt

```python
import anthropic

client = anthropic.Anthropic()

# BAD: Reporting a problem with zero supporting evidence
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "My Terraform apply is failing. How do I fix it?"
        }
    ]
)

print(message.content[0].text)
```

### Why It Fails

This is like calling a doctor and saying "I feel bad" without describing any symptoms:

- **No error message** -- Terraform produces specific error codes and messages that pinpoint the problem.
- **No resource context** -- Is it an AWS, GCP, or Azure resource? What type?
- **No state information** -- Is the state locked? Is there a drift?
- **No version info** -- Terraform behavior varies significantly between versions.

The model must respond with a generic checklist that may not even apply to your situation.

### The Fixed Prompt

```python
import anthropic

client = anthropic.Anthropic()

# GOOD: Includes the actual error, versions, and relevant config
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    messages=[
        {
            "role": "user",
            "content": """My Terraform apply is failing with the following error:

```
Error: error creating IAM Role (eks-node-role): EntityAlreadyExists:
Role with name eks-node-role already exists.
status code: 409, request id: a1b2c3d4-5678-90ab-cdef-ghijklmnop

  on modules/eks/iam.tf line 12, in resource "aws_iam_role" "node_role":
  12: resource "aws_iam_role" "node_role" {
```

Environment details:
- Terraform v1.6.4
- AWS provider v5.31.0
- Region: us-east-1
- This is a fresh apply after importing a previously manually-created cluster

The role exists in AWS but is not in my Terraform state. What is the correct
way to resolve this without deleting the existing role (it has pods using it)?"""
        }
    ]
)

print(message.content[0].text)
```

### Key Difference

The fixed prompt includes the exact error message, the file and line where it occurs, version information, the cloud provider and region, the backstory (import scenario), and a critical constraint (cannot delete the role). The model can now suggest `terraform import` with the exact syntax needed.

---

## Anti-Pattern 3: Too Much Context (Dumping 10K Lines of Logs)

### The Bad Prompt

```python
import anthropic

client = anthropic.Anthropic()

# BAD: Dumping an entire log file without filtering
# Imagine 'massive_log' contains 10,000+ lines of log output
massive_log = open("/var/log/application/service.log").read()  # 10K+ lines

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": f"Something is wrong with my service. Here are the logs:\n\n{massive_log}\n\nFix it."
        }
    ]
)

print(message.content[0].text)
```

### Why It Fails

Overwhelming the model with irrelevant information causes several problems:

- **Signal-to-noise ratio** -- The actual error is buried in thousands of INFO-level lines about successful requests.
- **Token limits** -- You may hit context window limits, causing the logs to be truncated and potentially losing the critical error.
- **Increased cost** -- You are paying for tokens on all that irrelevant log data.
- **Reduced accuracy** -- The model may fixate on irrelevant patterns in the noise rather than the actual problem.
- **Slower response** -- More input tokens means longer processing time during an incident when seconds count.

### The Fixed Prompt

```python
import anthropic

client = anthropic.Anthropic()

# GOOD: Pre-filtered, relevant context with clear structure
# Pre-filter logs before sending:
# grep -E "ERROR|FATAL|panic|exception" /var/log/application/service.log | tail -50

filtered_errors = """
2024-01-15T14:32:01Z ERROR [payment-processor] Connection refused to postgres-primary:5432 - retry 1/3
2024-01-15T14:32:04Z ERROR [payment-processor] Connection refused to postgres-primary:5432 - retry 2/3
2024-01-15T14:32:07Z ERROR [payment-processor] Connection refused to postgres-primary:5432 - retry 3/3
2024-01-15T14:32:07Z FATAL [payment-processor] All database connection retries exhausted. Shutting down.
2024-01-15T14:32:07Z ERROR [health-check] Liveness probe failed: database connection unavailable
"""

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": f"""My payment-processor service started failing at 14:32 UTC.
Here are the relevant error logs (filtered from full output):

```
{filtered_errors}
```

Additional context:
- The postgres-primary pod was rescheduled to a new node at 14:31 UTC
- The service uses a connection pool with max 20 connections
- There is a PgBouncer sidecar in the pod
- The postgres Service endpoint has been verified as correct via `kubectl get endpoints`

What is causing the connection failures after the postgres pod rescheduled,
and how do I make the service resilient to this scenario?"""
        }
    ]
)

print(message.content[0].text)
```

### Key Difference

The fixed prompt pre-filters logs to show only relevant error lines, provides a timeline, includes architectural context (connection pool, PgBouncer sidecar), mentions what has already been verified, and asks a specific question. The model can focus on the actual problem: likely stale DNS or connection pool not refreshing after pod reschedule.

---

## Anti-Pattern 4: No Output Format Specified

### The Bad Prompt

```python
import anthropic

client = anthropic.Anthropic()

# BAD: No guidance on desired output format
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    messages=[
        {
            "role": "user",
            "content": "Give me a Prometheus alerting rule for high CPU usage."
        }
    ]
)

print(message.content[0].text)
```

### Why It Fails

Without format specification, you might receive:

- A paragraph explaining what the rule should do instead of the actual YAML
- A rule in the old Prometheus 1.x format when you need the 2.x format
- Missing fields like `for`, `labels`, or `annotations` that your alerting pipeline requires
- No explanation of threshold choices, making it hard to tune later
- Output mixed with prose that requires manual extraction

In DevOps, output format matters because configs go directly into version-controlled files, CI/CD pipelines, or automation scripts.

### The Fixed Prompt

```python
import anthropic

client = anthropic.Anthropic()

# GOOD: Explicit format, structure, and integration requirements
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    messages=[
        {
            "role": "user",
            "content": """Generate a Prometheus alerting rule for high CPU usage with these requirements:

Criteria:
- Alert when CPU usage exceeds 80% for 5 minutes sustained
- Must work with kube-state-metrics and node-exporter
- Exclude short-lived batch jobs (pods with label `job-type: batch`)

Output format:
- Valid YAML for a PrometheusRule CRD (apiVersion: monitoring.coreos.com/v1)
- Include the full metadata section with name, namespace (monitoring), and labels
- Include these annotation fields: summary, description (with template variables), runbook_url
- Include severity label with value 'warning'
- Add a comment above the PromQL expression explaining the query logic

After the YAML block, provide:
1. A one-paragraph explanation of why the 5-minute `for` duration avoids false positives
2. The kubectl command to apply this rule
3. A PromQL query I can use in Grafana to verify the rule is working"""
        }
    ]
)

print(message.content[0].text)
```

### Key Difference

The fixed prompt specifies the exact CRD format, required fields, namespace, exclusion criteria, and what supplementary information to include. The output can be directly committed to a Git repository without manual reformatting.

---

## Anti-Pattern 5: Asking for Multiple Unrelated Things

### The Bad Prompt

```python
import anthropic

client = anthropic.Anthropic()

# BAD: Multiple unrelated requests crammed into one prompt
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": """Can you help me with:
1. Write a Dockerfile for my Python Flask app
2. Also explain how Kubernetes network policies work
3. And debug why my Jenkins pipeline is failing
4. Oh and what's the best way to set up GitOps with ArgoCD?
5. Also write a bash script to rotate my AWS access keys"""
        }
    ]
)

print(message.content[0].text)
```

### Why It Fails

Combining unrelated tasks into a single prompt causes:

- **Shallow answers** -- The model allocates attention across five topics, giving each a surface-level treatment instead of a thorough one.
- **Context confusion** -- Details from one topic can bleed into another (e.g., the Flask app context influencing the Jenkins debugging).
- **No iterative refinement** -- You cannot ask follow-up questions about the Dockerfile without re-establishing context for all five items.
- **Harder to validate** -- You cannot verify correctness of five unrelated outputs as easily as one focused output.
- **Token budget exhaustion** -- `max_tokens` gets divided across all topics, potentially truncating the last items.

### The Fixed Prompt

```python
import anthropic

client = anthropic.Anthropic()

# GOOD: One focused task with full context
# Task 1: Dockerfile (send as its own request)
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    messages=[
        {
            "role": "user",
            "content": """Write a production-ready Dockerfile for my Python Flask application with these specs:

Application details:
- Python 3.11, Flask 3.0, uses gunicorn as WSGI server
- Dependencies are in requirements.txt (includes psycopg2, redis, celery)
- Application entry point: app/main.py
- Needs to connect to PostgreSQL and Redis at runtime
- Static assets are served by nginx (separate container), not Flask

Requirements:
- Multi-stage build to minimize image size
- Run as non-root user (UID 1000)
- Use a distroless or slim base for the final stage
- Include a HEALTHCHECK instruction hitting /health endpoint
- Pin the base image digest for reproducibility
- Set appropriate labels (maintainer, version, description)
- Order layers for optimal cache utilization (dependencies before app code)

Output: Only the Dockerfile with inline comments explaining each decision."""
        }
    ]
)

print(message.content[0].text)

# Task 2: Jenkins debugging (separate request with its own context)
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    messages=[
        {
            "role": "user",
            "content": """My Jenkins declarative pipeline is failing at the 'Deploy' stage.

Pipeline snippet:
```groovy
stage('Deploy') {
    steps {
        withCredentials([usernamePassword(credentialsId: 'k8s-deploy-creds',
                        usernameVariable: 'USER', passwordVariable: 'TOKEN')]) {
            sh '''
                kubectl set image deployment/api-server \
                    api-server=${DOCKER_REGISTRY}/api-server:${BUILD_NUMBER} \
                    --namespace=production
            '''
        }
    }
}
```

Error:
```
error: You must be logged in to the server (Unauthorized)
```

Context:
- Jenkins agent runs in Kubernetes (same cluster as target deployment)
- The credentials were rotated last week
- Other pipelines using different credentials still work
- `kubectl get pods` from the Jenkins agent shell works fine manually

What are the possible causes and how do I debug this systematically?"""
        }
    ]
)

print(message.content[0].text)
```

### Key Difference

Each task gets its own request with full, dedicated context. The model can provide thorough, detailed answers that you can iterate on independently. If the Dockerfile needs tweaking, you do not need to re-send the Jenkins context.

---

## Anti-Pattern 6: Not Specifying the Environment or Constraints

### The Bad Prompt

```python
import anthropic

client = anthropic.Anthropic()

# BAD: No environment details, no constraints
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    messages=[
        {
            "role": "user",
            "content": "Write a script to back up my database."
        }
    ]
)

print(message.content[0].text)
```

### Why It Fails

This prompt is dangerously ambiguous in a production environment:

- **Which database?** PostgreSQL, MySQL, MongoDB, Redis, DynamoDB? Each has completely different backup mechanisms.
- **What environment?** Is this running in Kubernetes, on bare metal, in RDS, or Cloud SQL?
- **What constraints?** Is there a maintenance window? How much storage is available? Is the database size 1GB or 1TB?
- **What compliance requirements?** Does the backup need encryption? How long must it be retained? Does it need to be cross-region?
- **What is the recovery objective?** RPO of 5 minutes vs. daily backups are vastly different solutions.

A generic backup script generated without these constraints could cause data loss, compliance violations, or production outages.

### The Fixed Prompt

```python
import anthropic

client = anthropic.Anthropic()

# GOOD: Full environment specification and constraints
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": """Write a bash script to back up our PostgreSQL database with these specifications:

Environment:
- PostgreSQL 15.4 running in Kubernetes (StatefulSet, 1 primary + 2 replicas)
- Database size: approximately 200GB
- Cluster: EKS on AWS in us-west-2
- Backup storage: S3 bucket 's3://company-db-backups/production/postgres/'
- The script runs as a CronJob in the same Kubernetes cluster

Constraints:
- Must back up from a read replica (not primary) to avoid performance impact
- Maximum acceptable backup duration: 2 hours
- Network bandwidth to S3: 1 Gbps available
- Retention policy: daily backups kept for 30 days, weekly for 90 days
- Backups must be encrypted with AES-256 (KMS key alias: 'alias/db-backup-key')
- Must not consume more than 50GB of local ephemeral storage during the process

Requirements:
- Use pg_dump with custom format (-Fc) for selective restore capability
- Implement parallel dump (--jobs=4) for the large tables
- Compress with zstd before uploading to S3
- Include pre-backup validation (check replica lag < 10 seconds)
- Include post-backup validation (verify S3 object integrity with checksum)
- Send success/failure notifications to PagerDuty service key via their Events API
- Exit codes: 0=success, 1=backup failed, 2=validation failed, 3=upload failed
- Log to stdout in JSON format for Fluentd ingestion

The script should handle these failure scenarios:
- Replica lag exceeds threshold (skip backup, alert, exit 2)
- Disk space runs low during dump (cleanup partial files, exit 1)
- S3 upload fails (retry 3 times with exponential backoff, then exit 3)

Output the script with inline comments. After the script, provide the Kubernetes
CronJob YAML manifest to run it at 02:00 UTC daily."""
        }
    ]
)

print(message.content[0].text)
```

### Key Difference

The fixed prompt specifies the exact database engine and version, deployment topology, storage target, performance constraints, compliance requirements, error handling expectations, and output format. The resulting script will be production-ready and safe to deploy, not a toy example that could cause an outage.

---

## What Success Looks Like

After completing this lab, you should be able to construct prompts that consistently produce high-quality, actionable results. Here is a checklist for evaluating your prompts before sending them:

| Criterion | Question to Ask Yourself |
|-----------|--------------------------|
| **Specificity** | Would two different engineers interpret this prompt the same way? |
| **Context** | Have I included the error message, version numbers, and relevant config? |
| **Signal-to-noise** | Have I filtered the input to only what is relevant? |
| **Format** | Have I specified exactly what the output should look like? |
| **Focus** | Am I asking for one thing or multiple unrelated things? |
| **Environment** | Have I stated the platform, constraints, and requirements? |

### Quick Self-Test

Before sending any prompt to an AI assistant during DevOps work, run through this mental framework:

```bash
# The CLEVER framework for DevOps prompts:
# C - Context: What system, version, environment?
# L - Logs/Evidence: What error or symptom (filtered)?
# E - Expected behavior: What should happen vs. what does happen?
# V - Versions/Variants: What versions, what changed recently?
# E - Environment: Cloud provider, cluster, region, constraints?
# R - Result format: How should the answer be structured?
```

---

## Key Takeaway

The difference between a useful AI response and a useless one almost always comes down to the prompt, not the model. In DevOps and SRE work, where precision matters and mistakes have real consequences, investing 60 extra seconds to write a well-structured prompt can save hours of debugging, prevent misconfigurations, and produce outputs that are safe to deploy directly.

**Remember these rules:**

1. **Be specific** -- Name the thing that is broken, not the category it belongs to.
2. **Show evidence** -- Include the error, but only the relevant portion.
3. **Filter ruthlessly** -- 20 lines of relevant logs beats 10,000 lines of noise.
4. **Declare the format** -- Tell the model exactly what the output should look like.
5. **One task per prompt** -- Focused questions get thorough answers.
6. **State your environment** -- The same question has different answers on different platforms.

---

## Congratulations

You have completed Lab 6 and all labs in Episode 5: Prompt Engineering for DevOps.

Throughout this episode, you have learned:

- How to structure effective prompts for infrastructure and operational tasks
- Techniques for providing the right amount of context to AI assistants
- How to specify output formats that integrate directly into your workflows
- The critical anti-patterns that lead to wasted time, incorrect outputs, and potential production issues

These prompt engineering skills are foundational to everything that follows in the AI-Assisted DevOps Workshop. As AI tools become increasingly integrated into incident response, infrastructure-as-code workflows, CI/CD pipelines, and observability systems, the engineers who can communicate precisely with these tools will be the ones who extract the most value from them.

**Next steps:**
- Practice rewriting your recent AI prompts using the patterns from this episode
- Create a prompt template library for your team's most common operational tasks
- Share the CLEVER framework with your team during your next retrospective

Well done on completing Episode 5. See you in the next episode.
