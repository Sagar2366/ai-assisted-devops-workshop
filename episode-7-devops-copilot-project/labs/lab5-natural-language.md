# Lab 5: Natural Language Interface

> Episode 7: Build a DevOps Copilot | **Sagar Utekar** | CNCF Ambassador | Kubestronaut

---

## Mission

Convert natural language requests into kubectl/docker commands — so users don't need to memorize flags, but ALWAYS see and approve the actual command before execution.

---

## Concepts

### Natural Language Interface (NLI)

The NLI is the "translator" layer between what humans say and what machines understand:

```
Human: "Show me pods that keep crashing"
   │
   ▼
┌─────────────────────────┐
│  Natural Language        │ ← THIS LAB
│  Interface (Claude API)  │
└─────────────────────────┘
   │
   ▼
Command: kubectl get pods --field-selector=status.phase=Failed -A
```

### The Golden Rule: Show Before Run

**NEVER** execute an AI-generated command without showing it to the user first:

```
✗ BAD:  "Restarting auth service..." (runs silently)
✓ GOOD: "I'll run: kubectl rollout restart deployment/auth-service — OK? [y/N]"
```

Why? Because the AI might:
- Misunderstand the request ("delete" vs "describe")
- Target the wrong resource ("production" vs "staging")
- Use a more aggressive approach than needed

### The Analogy

> Like a translator at a foreign embassy — you say what you want in plain English, they translate it to the official language (kubectl), and you approve before they submit the document.

You wouldn't sign a document in a language you don't read. Don't let AI run commands you haven't reviewed.

---

## Step-by-Step Code

### The System Prompt for Translation

```python
NL_SYSTEM_PROMPT = """You are a DevOps command translator. Convert natural language requests into the appropriate kubectl, docker, or system command.

## Rules:
1. Generate the EXACT command — ready to copy-paste into a terminal
2. Prefer the simplest command that achieves the goal
3. Include common flags that improve output (--output=wide, --no-trunc, etc.)
4. If the request is ambiguous, generate the SAFEST interpretation
5. Never generate destructive commands from ambiguous requests

## Context:
- Kubernetes cluster is available (kubectl configured)
- Docker daemon is running
- Standard Linux tools available
- User is an SRE with production access

## Response Format:
Respond with ONLY valid JSON:
{
    "command": "the exact command to run",
    "explanation": "brief explanation of what this does",
    "risk_level": "SAFE|RESTRICTED|BLOCKED",
    "alternatives": ["optional alternative command 1", "optional alternative 2"]
}

## Examples of good translations:
- "show me crashing pods" → kubectl get pods --field-selector=status.phase=Failed -A
- "how much disk are containers using" → docker system df
- "check memory on nodes" → kubectl top nodes
- "restart the auth service" → kubectl rollout restart deployment/auth-service
- "show me recent events" → kubectl get events --sort-by=.lastTimestamp -A | tail -20
"""
```

---

### The Natural Language Engine

```python
#!/usr/bin/env python3
"""Task 5: Natural Language → DevOps Commands."""

import json
import anthropic
from dataclasses import dataclass
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()
client = anthropic.Anthropic()


@dataclass
class NLResult:
    """Result of natural language translation."""
    original_request: str
    command: str
    explanation: str
    risk_level: str
    alternatives: list[str]


def translate_natural_language(request: str) -> NLResult:
    """Convert a natural language request into a DevOps command.
    
    Args:
        request: Natural language description of what the user wants
        
    Returns:
        NLResult with the translated command and metadata
    """
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=NL_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Translate this request: {request}"}
        ]
    )
    
    result_text = response.content[0].text.strip()
    
    # Handle markdown code blocks in response
    if result_text.startswith("```"):
        result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    
    try:
        data = json.loads(result_text)
    except json.JSONDecodeError:
        return NLResult(
            original_request=request,
            command="# Could not parse AI response",
            explanation="The AI response was not valid JSON — retry or rephrase",
            risk_level="BLOCKED",
            alternatives=[]
        )
    
    return NLResult(
        original_request=request,
        command=data.get("command", "# No command generated"),
        explanation=data.get("explanation", "No explanation provided"),
        risk_level=data.get("risk_level", "RESTRICTED"),
        alternatives=data.get("alternatives", [])
    )


def display_translation(result: NLResult):
    """Display the translated command with explanation and risk level."""
    risk_colors = {"SAFE": "green", "RESTRICTED": "yellow", "BLOCKED": "red"}
    color = risk_colors.get(result.risk_level, "white")
    
    # Show what the user said
    console.print(f"\n[bold]You said:[/bold] {result.original_request}")
    
    # Show the translated command with syntax highlighting
    console.print(f"\n[bold]Translated command:[/bold]")
    console.print(Syntax(result.command, "bash", theme="monokai", padding=1))
    
    # Show metadata
    console.print(f"  [bold]Explanation:[/bold] {result.explanation}")
    console.print(f"  [bold]Risk Level:[/bold] [{color}]{result.risk_level}[/{color}]")
    
    # Show alternatives if any
    if result.alternatives:
        console.print(f"  [bold]Alternatives:[/bold]")
        for alt in result.alternatives:
            console.print(f"    - {alt}")


def is_natural_language(user_input: str) -> bool:
    """Detect whether input is natural language vs an actual command.
    
    Heuristic: if it starts with a known command prefix, it's a command.
    Otherwise, treat it as natural language.
    """
    command_prefixes = [
        "kubectl", "docker", "helm", "terraform", "ansible",
        "cat", "grep", "find", "ls", "ps", "top", "curl",
        "git", "make", "npm", "pip", "cd", "rm", "mv", "cp"
    ]
    
    first_word = user_input.strip().split()[0].lower() if user_input.strip() else ""
    return first_word not in command_prefixes
```

---

### Integrating into the Pipeline

```python
def handle_user_input(user_input: str):
    """Route input through the full copilot pipeline.
    
    If natural language → translate first, then classify + guardrail.
    If direct command → classify + guardrail immediately.
    """
    if is_natural_language(user_input):
        # Step 1: Translate NL → command
        console.print("[dim]Detected natural language — translating...[/dim]")
        nl_result = translate_natural_language(user_input)
        display_translation(nl_result)
        
        # Step 2: The translated command goes through safety pipeline
        command_to_evaluate = nl_result.command
    else:
        # Direct command — skip translation
        command_to_evaluate = user_input
    
    # Step 3: Classify (Lab 2)
    classification = classify_command(command_to_evaluate)
    
    # Step 4: Guardrails (Lab 3)
    result = guardrails.evaluate(classification)
    
    # Step 5: Audit (Lab 4)
    audit.log(
        command=command_to_evaluate,
        risk_level=classification.risk_level,
        action_taken=result.action,
        ai_reasoning=f"NL: '{user_input}' → {nl_result.explanation}"
            if is_natural_language(user_input) else classification.reason
    )
```

---

## Translation Examples

| What You Say | What Gets Generated | Risk |
|---|---|---|
| "Show me crashing pods" | `kubectl get pods --field-selector=status.phase=Failed -A` | SAFE |
| "How much disk are containers using?" | `docker system df` | SAFE |
| "Restart the auth service" | `kubectl rollout restart deployment/auth-service` | RESTRICTED |
| "Which nodes are low on memory?" | `kubectl top nodes --sort-by=memory` | SAFE |
| "What happened in the last 5 minutes?" | `kubectl get events --sort-by=.lastTimestamp -A \| tail -20` | SAFE |
| "Scale web to 10 pods" | `kubectl scale deployment/web --replicas=10` | RESTRICTED |
| "Delete the staging namespace" | `kubectl delete namespace staging` | BLOCKED |
| "Show me container logs for payments" | `kubectl logs deployment/payments --tail=100` | SAFE |

---

## Handling Ambiguity

What happens when the request is unclear?

```
User: "Clean up the cluster"

Could mean:
  a) kubectl delete pods --field-selector=status.phase=Succeeded  (mild cleanup)
  b) kubectl delete pods --all -A                                 (DANGEROUS)
  c) docker system prune --all                                    (DESTRUCTIVE)
```

The AI should:
1. Choose the **safest interpretation** (option a)
2. Explain what it chose and why
3. Offer alternatives so the user can pick

```json
{
    "command": "kubectl delete pods --field-selector=status.phase=Succeeded -A",
    "explanation": "Removes completed (Succeeded) pods only. This is the safest interpretation of cluster cleanup.",
    "risk_level": "RESTRICTED",
    "alternatives": [
        "docker system prune (remove unused containers/images)",
        "kubectl delete pods --field-selector=status.phase=Failed -A (remove failed pods)"
    ]
}
```

---

## Demo Script

```python
if __name__ == "__main__":
    console.print("[bold]Natural Language → Command Demo[/bold]\n")
    
    test_requests = [
        "Show me pods that keep crashing",
        "How much disk are my containers using?",
        "Restart the auth service",
        "Which nodes are running low on memory?",
        "Show me what happened in the last 5 minutes",
        "List all services in the production namespace",
        "Scale the web frontend to 10 replicas",
        "Show me container logs for the payment service",
    ]
    
    for request in test_requests:
        console.print(f"\n{'─' * 60}")
        result = translate_natural_language(request)
        display_translation(result)
```

---

## What Success Looks Like

```
Natural Language → Command Demo

────────────────────────────────────────────────────────────
You said: Show me pods that keep crashing

Translated command:
  ┌──────────────────────────────────────────────────────────┐
  │ kubectl get pods --field-selector=status.phase=Failed -A │
  └──────────────────────────────────────────────────────────┘
  Explanation: Lists all pods in Failed state across all namespaces
  Risk Level: SAFE

────────────────────────────────────────────────────────────
You said: Restart the auth service

Translated command:
  ┌──────────────────────────────────────────────────────────┐
  │ kubectl rollout restart deployment/auth-service           │
  └──────────────────────────────────────────────────────────┘
  Explanation: Performs a rolling restart of the auth-service deployment
  Risk Level: RESTRICTED
  Alternatives:
    - kubectl delete pod -l app=auth-service (delete pods, let them recreate)

────────────────────────────────────────────────────────────
You said: Scale the web frontend to 10 replicas

Translated command:
  ┌──────────────────────────────────────────────────────────┐
  │ kubectl scale deployment/web-frontend --replicas=10       │
  └──────────────────────────────────────────────────────────┘
  Explanation: Scales the web-frontend deployment to 10 pods
  Risk Level: RESTRICTED
```

---

## Key Takeaway

Natural language is the UX layer — users don't need to memorize kubectl flags, but they ALWAYS see the actual command before it runs. The AI translates intent to syntax, but the human remains in the approval loop. Trust but verify.

---

**Previous → [Lab 4: Audit Logging](lab4-audit-logging.md)** | **Next → [Lab 6: Full Copilot](lab6-full-copilot.md)**
