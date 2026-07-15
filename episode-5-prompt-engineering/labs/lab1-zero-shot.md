# Lab 1: Zero-Shot Prompting

## Mission

Use zero-shot prompting to handle quick SRE tasks — no examples needed. You will learn how to write clear, direct instructions that produce useful outputs for Kubernetes troubleshooting, log analysis, and alert triage.

---

## Concept: What is Zero-Shot Prompting?

Zero-shot prompting means giving the model a task with instructions but **no examples**. You rely entirely on the model's training to produce the right output format and content.

### The Analogy

Imagine hiring a senior SRE who just joined your team. You ask them: "This pod is CrashLoopBackOff — what should I check?" They do not need to see your past incident reports. They draw on years of experience (their "training") to give you a solid answer.

That is zero-shot prompting — you provide the task and context, the model provides the expertise.

### When to Use Zero-Shot

- Quick troubleshooting questions
- Generating kubectl commands
- Explaining error messages
- One-off analysis tasks
- Situations where speed matters more than format consistency

---

## Step 1: Basic kubectl Generation

```python
from sre_prompt import call_claude

# Zero-shot: Generate kubectl commands
prompt = """You are a Kubernetes expert. Generate the exact kubectl command to:
List all pods in the 'production' namespace that are NOT in Running state.

Return ONLY the kubectl command, no explanation."""

response = call_claude(prompt)
print(f"Command: {response}")
```

Expected output:

```
Command: kubectl get pods -n production --field-selector=status.phase!=Running
```

---

## Step 2: Log Analysis

```python
from sre_prompt import call_claude

# Zero-shot: Analyze a log snippet
log_snippet = """
2024-03-15T08:23:41Z ERROR [payment-service] Connection refused to postgres-primary:5432
2024-03-15T08:23:42Z ERROR [payment-service] Connection refused to postgres-primary:5432
2024-03-15T08:23:43Z WARN  [payment-service] Circuit breaker OPEN for database connections
2024-03-15T08:23:44Z ERROR [payment-service] Failed to process transaction tx-9921: database unavailable
2024-03-15T08:23:45Z INFO  [payment-service] Retry attempt 1/3 for postgres-primary:5432
2024-03-15T08:23:48Z ERROR [payment-service] Retry failed: connection timeout after 3000ms
2024-03-15T08:23:49Z CRITICAL [payment-service] Payment processing halted - all retries exhausted
"""

prompt = f"""Analyze these application logs and provide:
1. Root cause (one sentence)
2. Affected service(s)
3. Impact level (LOW / MEDIUM / HIGH / CRITICAL)
4. Immediate action to take

Logs:
{log_snippet}"""

response = call_claude(prompt)
print(response)
```

---

## Step 3: Alert Triage

```python
from sre_prompt import call_claude

# Zero-shot: Triage a Prometheus alert
alert = """
Alert: HighMemoryUsage
Severity: warning
Service: api-gateway
Current Value: 89%
Threshold: 85%
Duration: 15 minutes
Labels:
  namespace: production
  pod: api-gateway-7d4f8b6c9-x2k1m
  node: worker-node-03
"""

prompt = f"""You are an SRE on-call. Triage this alert and provide:
1. Is this actionable right now? (YES/NO)
2. Urgency (respond within: 5min / 30min / next business day)
3. Likely cause (one sentence)
4. First three commands to run for investigation

Alert:
{alert}"""

response = call_claude(prompt)
print(response)
```

---

## Step 4: Kubernetes Troubleshooting

```python
from sre_prompt import call_claude

# Zero-shot: Troubleshoot a pod issue
pod_status = """
NAME                        READY   STATUS             RESTARTS   AGE
checkout-5f8d7c9b4-2nj8k   0/1     CrashLoopBackOff   7          12m
"""

pod_events = """
Events:
  Type     Reason     Age                 From               Message
  ----     ------     ----                ----               -------
  Normal   Scheduled  12m                 default-scheduler  Successfully assigned production/checkout-5f8d7c9b4-2nj8k to worker-node-02
  Normal   Pulled     10m (x5 over 12m)  kubelet            Container image "checkout:v2.3.1" successfully pulled
  Normal   Created    10m (x5 over 12m)  kubelet            Created container checkout
  Normal   Started    10m (x5 over 12m)  kubelet            Started container checkout
  Warning  BackOff    2m (x25 over 11m)  kubelet            Back-off restarting failed container
"""

prompt = f"""A pod is in CrashLoopBackOff. Based on the information below, provide:
1. Most likely root cause
2. Diagnostic commands to run (in order)
3. Common fixes for this pattern

Pod Status:
{pod_status}

Pod Events:
{pod_events}"""

response = call_claude(prompt)
print(response)
```

---

## Step 5: Comparing Prompt Specificity

Let us see how prompt quality affects output quality:

```python
from sre_prompt import call_claude

# Vague zero-shot prompt
vague_prompt = "My pod is crashing. Help."

# Specific zero-shot prompt
specific_prompt = """A pod named 'checkout-5f8d7c9b4-2nj8k' in the 'production' namespace
is in CrashLoopBackOff state with 7 restarts over 12 minutes.

The container image is checkout:v2.3.1 and it was recently deployed.
The pod is scheduled on worker-node-02.

Provide a structured troubleshooting plan with:
1. Most likely causes (ranked by probability)
2. Diagnostic commands to run
3. Quick fixes to try
4. Escalation criteria (when to page someone else)"""

print("=== VAGUE PROMPT ===")
print(call_claude(vague_prompt))
print("\n=== SPECIFIC PROMPT ===")
print(call_claude(specific_prompt))
```

Notice how the specific prompt produces actionable, structured output while the vague prompt produces generic advice.

---

## Experiment: Build Your Own Zero-Shot Prompts

Try building zero-shot prompts for these scenarios:

1. **Terraform Error**: A `terraform apply` failed with a "resource already exists" error
2. **Network Policy**: Generate a Kubernetes NetworkPolicy that allows traffic only from the `frontend` namespace
3. **Prometheus Query**: Write a PromQL query to find services with error rates above 1% in the last hour

```python
from sre_prompt import call_claude

# Your experiment here
your_prompt = """[Your zero-shot prompt for one of the scenarios above]"""

response = call_claude(your_prompt)
print(response)
```

---

## What Success Looks Like

After completing this lab, you can:

- Write zero-shot prompts that produce specific, actionable SRE outputs
- Understand when zero-shot is sufficient vs. when you need few-shot or chain-of-thought
- Structure prompts with clear role, context, and output format instructions
- Generate kubectl commands, analyze logs, and triage alerts using only instructions

---

## Key Takeaway

Zero-shot prompting works well for tasks where the model already has strong domain knowledge (like Kubernetes troubleshooting). The key is **specificity** — the more context and structure you provide in your prompt, the better the output. When you find zero-shot outputs are inconsistent or missing important details, that is your signal to move to few-shot prompting (next lab).

---

## Next

[Lab 2: Few-Shot Prompting](lab2-few-shot.md) — Using labeled examples to improve consistency and output format
