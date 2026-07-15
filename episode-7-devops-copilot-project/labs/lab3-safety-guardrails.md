# Lab 3: Safety Guardrails

> Episode 7: Build a DevOps Copilot | **Sagar Utekar** | CNCF Ambassador | Kubestronaut

---

## Mission

Implement the three-tier safety system that acts on classification results — auto-executing safe commands, requiring confirmation for restricted ones, and blocking dangerous operations entirely.

---

## Concepts

### Defense in Depth

Safety isn't a single check — it's **layers of protection**:

```
User Input
    │
    ▼
┌──────────────────┐
│  Classification  │ ← Lab 2: Decides risk level
└──────────────────┘
    │
    ▼
┌──────────────────┐
│   Guardrails     │ ← THIS LAB: Acts on the decision
└──────────────────┘
    │
    ├── SAFE ──────→ Auto-execute, show output
    ├── RESTRICTED ─→ Show command, ask confirmation
    └── BLOCKED ───→ Deny, explain why
```

### The Three Tiers in Action

| Tier | User Experience | Real-World Analog |
|------|----------------|-------------------|
| SAFE | Command runs immediately, output shown | Unlocked door — walk through |
| RESTRICTED | "Run `kubectl scale ...`? [y/N]" | Locked door — need badge swipe |
| BLOCKED | "DENIED: Cannot delete production namespace" | Vault door — no access |

### The Analogy

> Like a nuclear launch system — some buttons anyone can press (read gauges), some need two-key confirmation (adjust power), some are physically locked (SCRAM the reactor).

The copilot applies the same graduated response: the higher the risk, the more friction before execution.

---

## Step-by-Step Code

### The Guardrails Engine

```python
#!/usr/bin/env python3
"""Task 3: Safety Guardrails — three-tier execution control."""

import subprocess
import json
from enum import Enum
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()


class RiskLevel(Enum):
    SAFE = "SAFE"
    RESTRICTED = "RESTRICTED"
    BLOCKED = "BLOCKED"


@dataclass
class ClassificationResult:
    """Result from the command classifier (Lab 2)."""
    risk_level: RiskLevel
    reason: str
    command: str


@dataclass  
class GuardrailResult:
    """Result from the guardrail engine."""
    action: str          # "executed", "confirmed", "denied", "cancelled"
    command: str
    output: str | None
    risk_level: RiskLevel
    reason: str


class SafetyGuardrails:
    """Three-tier safety system for command execution."""
    
    def __init__(self, dry_run: bool = False):
        """
        Args:
            dry_run: If True, never actually execute commands (for testing)
        """
        self.dry_run = dry_run
        self.override_active = False
    
    def evaluate(self, classification: ClassificationResult) -> GuardrailResult:
        """Apply guardrails based on classification result.
        
        Args:
            classification: The risk assessment from the classifier
            
        Returns:
            GuardrailResult with action taken and any output
        """
        if classification.risk_level == RiskLevel.SAFE:
            return self._handle_safe(classification)
        elif classification.risk_level == RiskLevel.RESTRICTED:
            return self._handle_restricted(classification)
        else:  # BLOCKED
            return self._handle_blocked(classification)
    
    def _handle_safe(self, classification: ClassificationResult) -> GuardrailResult:
        """SAFE: Auto-execute without asking."""
        console.print(f"[green]✓ SAFE[/green] — executing: [bold]{classification.command}[/bold]")
        
        output = self._execute(classification.command)
        
        return GuardrailResult(
            action="executed",
            command=classification.command,
            output=output,
            risk_level=RiskLevel.SAFE,
            reason=classification.reason
        )
    
    def _handle_restricted(self, classification: ClassificationResult) -> GuardrailResult:
        """RESTRICTED: Show command and ask for confirmation."""
        console.print(Panel(
            f"[yellow]⚠ RESTRICTED[/yellow]\n\n"
            f"[bold]Command:[/bold] {classification.command}\n"
            f"[bold]Reason:[/bold]  {classification.reason}\n\n"
            f"[dim]This command modifies state but is recoverable.[/dim]",
            title="Confirmation Required",
            border_style="yellow"
        ))
        
        confirmed = Confirm.ask("Execute this command?", default=False)
        
        if confirmed:
            output = self._execute(classification.command)
            return GuardrailResult(
                action="confirmed",
                command=classification.command,
                output=output,
                risk_level=RiskLevel.RESTRICTED,
                reason=classification.reason
            )
        else:
            console.print("[dim]Command cancelled by user.[/dim]")
            return GuardrailResult(
                action="cancelled",
                command=classification.command,
                output=None,
                risk_level=RiskLevel.RESTRICTED,
                reason=classification.reason
            )
    
    def _handle_blocked(self, classification: ClassificationResult) -> GuardrailResult:
        """BLOCKED: Deny execution with explanation."""
        console.print(Panel(
            f"[red bold]✗ BLOCKED[/red bold]\n\n"
            f"[bold]Command:[/bold] {classification.command}\n"
            f"[bold]Reason:[/bold]  {classification.reason}\n\n"
            f"[dim]This command is too dangerous to execute.\n"
            f"If you need to run this, do it manually outside the copilot.[/dim]",
            title="Command Denied",
            border_style="red"
        ))
        
        return GuardrailResult(
            action="denied",
            command=classification.command,
            output=None,
            risk_level=RiskLevel.BLOCKED,
            reason=classification.reason
        )
    
    def _execute(self, command: str) -> str:
        """Execute a shell command and return output.
        
        Args:
            command: Shell command to execute
            
        Returns:
            Command output (stdout + stderr)
        """
        if self.dry_run:
            return f"[DRY RUN] Would execute: {command}"
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30-second timeout for safety
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]: {result.stderr}"
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            return output
        except subprocess.TimeoutExpired:
            return "[ERROR] Command timed out after 30 seconds"
        except Exception as e:
            return f"[ERROR] {str(e)}"


# --- Emergency Override ---

class EmergencyOverride:
    """Override mechanism for critical situations.
    
    Sometimes during an incident, you NEED to run a restricted command
    without confirmation. This provides a time-limited override.
    """
    
    def __init__(self, guardrails: SafetyGuardrails):
        self.guardrails = guardrails
        self.active = False
        self.override_reason = None
    
    def activate(self, reason: str):
        """Activate emergency override (RESTRICTED → auto-execute)."""
        console.print(Panel(
            f"[red bold]EMERGENCY OVERRIDE ACTIVATED[/red bold]\n\n"
            f"Reason: {reason}\n\n"
            f"RESTRICTED commands will auto-execute.\n"
            f"BLOCKED commands are STILL blocked.\n"
            f"[dim]Type 'override off' to deactivate.[/dim]",
            border_style="red"
        ))
        self.active = True
        self.override_reason = reason
    
    def deactivate(self):
        """Deactivate emergency override."""
        self.active = False
        self.override_reason = None
        console.print("[green]Override deactivated. Normal safety rules restored.[/green]")


# --- Demo ---

if __name__ == "__main__":
    console.print("[bold]Safety Guardrails Demo[/bold]\n")
    console.print("[dim]Running in dry-run mode (no commands actually execute)[/dim]\n")
    
    guardrails = SafetyGuardrails(dry_run=True)
    
    # Simulate classifications
    test_cases = [
        ClassificationResult(
            risk_level=RiskLevel.SAFE,
            reason="Read-only pod listing",
            command="kubectl get pods -n production"
        ),
        ClassificationResult(
            risk_level=RiskLevel.RESTRICTED,
            reason="Scaling changes resource allocation",
            command="kubectl scale deployment/web --replicas=5"
        ),
        ClassificationResult(
            risk_level=RiskLevel.BLOCKED,
            reason="Deleting namespace destroys all resources irreversibly",
            command="kubectl delete namespace production"
        ),
    ]
    
    for classification in test_cases:
        console.print(f"\n{'='*60}")
        result = guardrails.evaluate(classification)
        console.print(f"[dim]Action taken: {result.action}[/dim]")
        if result.output:
            console.print(f"[dim]Output: {result.output}[/dim]")
```

---

## The Override Mechanism

During a real incident, sometimes you need to move fast:

```python
# Activate during a P1 incident
override = EmergencyOverride(guardrails)
override.activate("P1 incident — auth service down, need rapid scaling")

# Now RESTRICTED commands auto-execute (no confirmation prompt)
# BLOCKED commands are STILL blocked — override doesn't bypass everything

# When incident is resolved:
override.deactivate()
```

The override:
- Upgrades RESTRICTED → auto-execute (skips confirmation)
- Does NOT unlock BLOCKED commands (those always require manual execution)
- Gets logged to the audit trail (Lab 4)
- Should be time-limited in production (auto-expire after 30 minutes)

---

## Design Decisions

### Why not just block everything dangerous?

Because SREs need to **actually do their jobs**:
- Scaling a deployment is state-changing but necessary during incidents
- Restarting a pod is disruptive but sometimes the only fix
- The goal is **appropriate oversight**, not maximum restriction

### Why keep BLOCKED truly blocked?

Because some commands have no undo:
- `kubectl delete namespace` — gone, including PVCs
- `rm -rf /var/lib/etcd` — cluster state destroyed
- `docker system prune --all` — all images/containers removed

These should NEVER be one-click operations. The copilot makes you go run them manually — which adds just enough friction to prevent accidents.

---

## What Success Looks Like

```
Safety Guardrails Demo

============================================================
✓ SAFE — executing: kubectl get pods -n production
Action taken: executed
Output: [DRY RUN] Would execute: kubectl get pods -n production

============================================================
╭─── Confirmation Required ───╮
│ ⚠ RESTRICTED                 │
│ Command: kubectl scale ...   │
│ Reason: Scaling changes...   │
╰──────────────────────────────╯
Execute this command? [y/N]: y
Action taken: confirmed

============================================================
╭─── Command Denied ───╮
│ ✗ BLOCKED             │
│ Command: kubectl ...  │
│ Reason: Destroys...   │
╰───────────────────────╯
Action taken: denied
```

---

## Key Takeaway

Safety isn't about blocking everything — it's about matching the oversight level to the risk level. SAFE commands flow freely. RESTRICTED commands pause for a human check. BLOCKED commands refuse entirely. This graduated response keeps SREs productive while preventing catastrophic mistakes.

---

**Previous → [Lab 2: Command Classification](lab2-command-classification.md)** | **Next → [Lab 4: Audit Logging](lab4-audit-logging.md)**
