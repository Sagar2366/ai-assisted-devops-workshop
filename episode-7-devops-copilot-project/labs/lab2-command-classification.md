# Lab 2: Command Classification

> Episode 7: Build a DevOps Copilot | **Sagar Utekar** | CNCF Ambassador | Kubestronaut

---

> **Mission:** Use Claude to classify DevOps commands into three risk tiers (SAFE / RESTRICTED / BLOCKED) so the copilot knows how to handle each one.

---

## Concepts

### Why Classify Commands?

Not all commands are equal. `kubectl get pods` is harmless — it reads data. `kubectl delete namespace production` can take down your entire platform. An AI copilot must know the difference before it does anything.

### The Three Tiers

| Tier | Meaning | Action | Examples |
|------|---------|--------|----------|
| **SAFE** | Read-only, no state change | Auto-execute | `kubectl get`, `docker ps`, `helm list` |
| **RESTRICTED** | Modifies state, recoverable | Ask for confirmation | `kubectl scale`, `docker stop`, `helm upgrade` |
| **BLOCKED** | Destructive, irreversible | Always deny | `kubectl delete ns`, `rm -rf /`, `docker system prune --all` |

### The Analogy

> Think of it like airport security. SAFE commands are carry-on bags — they go through without stopping. RESTRICTED commands are flagged items — a human reviews them. BLOCKED commands are prohibited items — they never get through, period.

### How Claude Classifies

We give Claude a **system prompt** that defines the three tiers with examples, then ask it to return a structured JSON response for each command. The AI understands context — it knows that `kubectl delete pod` (single pod) is different from `kubectl delete namespace` (everything in the namespace).

---

## Step-by-Step Code

### Step 1: Define the Classification Prompt

The system prompt is the brain of the classifier. It must be precise:

```python
CLASSIFICATION_SYSTEM_PROMPT = """You are a DevOps command safety classifier.
Classify each command into exactly one of three tiers:

## SAFE
Commands that only READ data and cannot modify system state.
Examples: kubectl get, docker ps, cat, ls, helm status, kubectl describe

## RESTRICTED
Commands that MODIFY state but can be recovered from or are scoped.
Examples: kubectl scale, docker stop, kubectl rollout restart, helm upgrade

## BLOCKED
Commands that DESTROY data, affect production globally, or are irreversible.
Examples: kubectl delete namespace, rm -rf, docker system prune --all,
kubectl delete pv, helm uninstall (production)

Respond ONLY with valid JSON:
{"risk_level": "SAFE|RESTRICTED|BLOCKED", "category": "brief category", "reason": "one-sentence explanation"}
"""
```

### Step 2: Send a Command to Claude

```python
import anthropic
import json

client = anthropic.Anthropic()

def classify_command(command: str) -> dict:
    """Classify a single command using Claude."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        system=CLASSIFICATION_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Classify this command: {command}"}
        ]
    )
    
    text = response.content[0].text
    
    # Parse JSON from response
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Extract JSON if surrounded by extra text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        return {"risk_level": "BLOCKED", "reason": "Parse failure — blocking for safety"}
```

### Step 3: Test with Real Commands

```python
TEST_COMMANDS = [
    "kubectl get pods -n production",         # Should be SAFE
    "kubectl delete namespace prod",          # Should be BLOCKED
    "docker ps --format 'table {{.Names}}'",  # Should be SAFE
    "docker system prune --all -f",           # Should be BLOCKED
    "kubectl scale deployment/api --replicas=3",  # Should be RESTRICTED
    "kubectl rollout restart deployment/web",     # Should be RESTRICTED
    "helm status my-release",                 # Should be SAFE
    "rm -rf /tmp/old-logs",                   # Should be BLOCKED
]

for command in TEST_COMMANDS:
    result = classify_command(command)
    print(f"[{result['risk_level']:10}] {command}")
    print(f"           Reason: {result['reason']}")
```

### Step 4: Handle Edge Cases

The classifier should default to BLOCKED when uncertain — this is the safe default:

```python
def classify_command_safe(command: str) -> dict:
    """Classify with safe fallback on any error."""
    try:
        result = classify_command(command)
        # Validate the response has required fields
        if result.get("risk_level") not in ("SAFE", "RESTRICTED", "BLOCKED"):
            return {"risk_level": "BLOCKED", "reason": "Invalid classification — blocking"}
        return result
    except Exception as e:
        # Any error = BLOCKED (fail-safe principle)
        return {"risk_level": "BLOCKED", "reason": f"Classification error: {str(e)}"}
```

---

## What Success Looks Like

```
=================================================================
  TASK 2: AI Command Classification
=================================================================

  Classifying: kubectl get pods -n production
  Result:  [SAFE]
  Reason:  Read-only command that lists pods without modification

  Classifying: kubectl delete namespace prod
  Result:  [BLOCKED]
  Reason:  Deletes entire namespace including all resources — irreversible

  Classifying: kubectl scale deployment/api --replicas=3
  Result:  [RESTRICTED]
  Reason:  Modifies replica count but can be reverted

  Classification Summary:
  SAFE:       3 commands
  RESTRICTED: 2 commands
  BLOCKED:    3 commands
```

---

## Key Takeaway

AI classification gives us a programmatic way to assess risk without maintaining a static whitelist. Claude understands DevOps context — it knows that `rm -rf /tmp/logs` is less dangerous than `rm -rf /`, and that `kubectl delete pod` (one pod) is less destructive than `kubectl delete namespace` (everything). But always default to BLOCKED when in doubt. In safety-critical systems, false positives (blocking something safe) are far better than false negatives (allowing something dangerous).

---

**Previous: [Lab 1: CLI Interface](lab1-cli-interface.md)** | **Next: [Lab 3: Safety Guardrails](lab3-safety-guardrails.md)**
