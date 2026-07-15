# Lab 4: Audit Logging

> Episode 7: Build a DevOps Copilot | **Sagar Utekar** | CNCF Ambassador | Kubestronaut

---

## Mission

Log every AI copilot action to a structured JSON audit file — because in production, "what did the AI do?" must always have an answer.

---

## Concepts

### Why Audit Logs Matter

| Stakeholder | What They Need |
|-------------|---------------|
| **Security team** | Proof that AI actions are controlled and traceable |
| **Incident responders** | "What changed at 3:47 AM?" — exact commands + who approved |
| **Compliance (SOC2, ISO)** | Evidence of access control and action logging |
| **You (the SRE)** | "Wait, did I run that?" — review your own AI-assisted actions |

### What to Log

Every audit entry captures:

| Field | Purpose | Example |
|-------|---------|---------|
| `timestamp` | When it happened | `2024-01-15T03:47:22Z` |
| `user` | Who initiated it | `sagar@laptop` |
| `command` | What was requested | `kubectl scale deploy/web --replicas=10` |
| `risk_level` | How dangerous | `RESTRICTED` |
| `action_taken` | What the copilot did | `confirmed` / `denied` / `executed` |
| `ai_reasoning` | Why the AI classified it this way | `"Scaling changes resource allocation"` |
| `session_id` | Group actions by session | `sess_abc123` |

### The Analogy

> Like a flight recorder (black box) — you hope you never need it, but when an incident happens, it tells you exactly what the AI did and why.

Airlines don't fly without black boxes. Production copilots shouldn't run without audit logs.

---

## Step-by-Step Code

### The AuditLogger Class

```python
#!/usr/bin/env python3
"""Task 4: Audit Logging — every AI action gets recorded."""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class AuditEntry:
    """A single audit log entry."""
    timestamp: str
    session_id: str
    user: str
    command: str
    risk_level: str
    action_taken: str
    ai_reasoning: str
    output_preview: Optional[str] = None
    override_active: bool = False
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class AuditLogger:
    """JSON Lines audit logger for copilot actions.
    
    Writes one JSON object per line (JSON Lines format) — easy to
    parse, grep, and ship to log aggregation systems.
    """
    
    def __init__(self, log_dir: str = "~/.copilot/audit"):
        """
        Args:
            log_dir: Directory to store audit logs
        """
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = f"sess_{uuid.uuid4().hex[:8]}"
        self.user = os.environ.get("USER", "unknown")
        self._current_log_file = self._get_log_filename()
    
    def _get_log_filename(self) -> Path:
        """Generate log filename based on date (daily rotation)."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.log_dir / f"copilot-audit-{date_str}.jsonl"
    
    def log(
        self,
        command: str,
        risk_level: str,
        action_taken: str,
        ai_reasoning: str,
        output_preview: Optional[str] = None,
        override_active: bool = False
    ) -> AuditEntry:
        """Write an audit entry.
        
        Args:
            command: The command that was processed
            risk_level: SAFE, RESTRICTED, or BLOCKED
            action_taken: executed, confirmed, denied, cancelled
            ai_reasoning: Why the AI classified it this way
            output_preview: First 200 chars of command output
            override_active: Whether emergency override was on
            
        Returns:
            The AuditEntry that was written
        """
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=self.session_id,
            user=self.user,
            command=command,
            risk_level=risk_level,
            action_taken=action_taken,
            ai_reasoning=ai_reasoning,
            output_preview=output_preview[:200] if output_preview else None,
            override_active=override_active
        )
        
        # Rotate file if date changed
        self._current_log_file = self._get_log_filename()
        
        # Append to log file (JSON Lines format)
        with open(self._current_log_file, "a") as f:
            f.write(entry.to_json() + "\n")
        
        return entry
    
    def get_recent(self, n: int = 10) -> list[AuditEntry]:
        """Get the N most recent audit entries.
        
        Args:
            n: Number of entries to return
            
        Returns:
            List of recent AuditEntry objects
        """
        entries = []
        
        if self._current_log_file.exists():
            with open(self._current_log_file) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        entries.append(AuditEntry(**data))
        
        return entries[-n:]
    
    def display_recent(self, n: int = 10):
        """Display recent audit entries in a rich table."""
        entries = self.get_recent(n)
        
        if not entries:
            console.print("[dim]No audit entries found.[/dim]")
            return
        
        table = Table(title=f"Recent Audit Log (last {n})", border_style="blue")
        table.add_column("Time", style="dim", width=10)
        table.add_column("Command", max_width=40)
        table.add_column("Risk", width=12)
        table.add_column("Action", width=12)
        
        risk_colors = {"SAFE": "green", "RESTRICTED": "yellow", "BLOCKED": "red"}
        
        for entry in entries:
            time_str = entry.timestamp.split("T")[1][:8]  # HH:MM:SS
            risk_color = risk_colors.get(entry.risk_level, "white")
            
            table.add_row(
                time_str,
                entry.command[:40],
                f"[{risk_color}]{entry.risk_level}[/{risk_color}]",
                entry.action_taken
            )
        
        console.print(table)
    
    def get_stats(self) -> dict:
        """Get summary statistics for current session."""
        entries = self.get_recent(1000)  # Get all from today
        session_entries = [e for e in entries if e.session_id == self.session_id]
        
        stats = {
            "total_commands": len(session_entries),
            "safe_executed": sum(1 for e in session_entries if e.risk_level == "SAFE"),
            "restricted_confirmed": sum(1 for e in session_entries if e.action_taken == "confirmed"),
            "restricted_cancelled": sum(1 for e in session_entries if e.action_taken == "cancelled"),
            "blocked_denied": sum(1 for e in session_entries if e.action_taken == "denied"),
            "override_used": sum(1 for e in session_entries if e.override_active),
        }
        
        return stats


# --- Demo ---

if __name__ == "__main__":
    console.print("[bold]Audit Logging Demo[/bold]\n")
    
    # Create logger
    logger = AuditLogger(log_dir="/tmp/copilot-audit-demo")
    console.print(f"[dim]Session ID: {logger.session_id}[/dim]")
    console.print(f"[dim]Log file: {logger._current_log_file}[/dim]\n")
    
    # Simulate some copilot actions
    logger.log(
        command="kubectl get pods -n production",
        risk_level="SAFE",
        action_taken="executed",
        ai_reasoning="Read-only pod listing, no side effects",
        output_preview="NAME                    READY   STATUS    RESTARTS\nweb-abc123   1/1     Running   0"
    )
    
    logger.log(
        command="kubectl scale deployment/web --replicas=5",
        risk_level="RESTRICTED",
        action_taken="confirmed",
        ai_reasoning="Scaling changes resource allocation, recoverable"
    )
    
    logger.log(
        command="kubectl delete namespace production",
        risk_level="BLOCKED",
        action_taken="denied",
        ai_reasoning="Namespace deletion destroys all resources irreversibly"
    )
    
    logger.log(
        command="docker restart auth-service",
        risk_level="RESTRICTED",
        action_taken="cancelled",
        ai_reasoning="Container restart causes brief downtime"
    )
    
    # Display the audit log
    console.print()
    logger.display_recent()
    
    # Show stats
    stats = logger.get_stats()
    console.print(f"\n[bold]Session Stats:[/bold]")
    console.print(f"  Total commands: {stats['total_commands']}")
    console.print(f"  Safe (auto-executed): {stats['safe_executed']}")
    console.print(f"  Restricted (confirmed): {stats['restricted_confirmed']}")
    console.print(f"  Restricted (cancelled): {stats['restricted_cancelled']}")
    console.print(f"  Blocked (denied): {stats['blocked_denied']}")
    
    # Show raw log file
    console.print(f"\n[bold]Raw log file:[/bold]")
    console.print(f"[dim]{logger._current_log_file}[/dim]\n")
    
    with open(logger._current_log_file) as f:
        for line in f:
            data = json.loads(line)
            console.print(f"[dim]{json.dumps(data, indent=2)}[/dim]")
            console.print()
```

---

## Log Format: JSON Lines

Each line in the audit file is a complete JSON object:

```json
{"timestamp": "2024-01-15T03:47:22.123456+00:00", "session_id": "sess_a1b2c3d4", "user": "sagar", "command": "kubectl get pods -n production", "risk_level": "SAFE", "action_taken": "executed", "ai_reasoning": "Read-only pod listing", "output_preview": "NAME  READY  STATUS...", "override_active": false}
{"timestamp": "2024-01-15T03:47:45.789012+00:00", "session_id": "sess_a1b2c3d4", "user": "sagar", "command": "kubectl delete namespace production", "risk_level": "BLOCKED", "action_taken": "denied", "ai_reasoning": "Namespace deletion is irreversible", "output_preview": null, "override_active": false}
```

Why JSON Lines (`.jsonl`)?
- One entry per line — easy to `grep`, `wc -l`, `tail -f`
- Each line is valid JSON — parseable by any tool
- Append-only — safe for concurrent writes
- Ships directly to ELK/Splunk/Datadog

---

## Querying Audit Logs

```bash
# What did the copilot do today?
cat ~/.copilot/audit/copilot-audit-2024-01-15.jsonl | jq .

# How many commands were blocked?
grep '"action_taken": "denied"' ~/.copilot/audit/*.jsonl | wc -l

# What commands ran during the P1 incident (3:00-4:00 AM)?
cat ~/.copilot/audit/copilot-audit-2024-01-15.jsonl | \
  jq 'select(.timestamp > "2024-01-15T03:00" and .timestamp < "2024-01-15T04:00")'

# Was emergency override used?
grep '"override_active": true' ~/.copilot/audit/*.jsonl | jq .
```

---

## What Success Looks Like

```
Audit Logging Demo

Session ID: sess_f7a2b9c1
Log file: /tmp/copilot-audit-demo/copilot-audit-2024-01-15.jsonl

         Recent Audit Log (last 10)
┌──────────┬──────────────────────┬────────────┬──────────┐
│ Time     │ Command              │ Risk       │ Action   │
├──────────┼──────────────────────┼────────────┼──────────┤
│ 03:47:22 │ kubectl get pods ... │ SAFE       │ executed │
│ 03:47:23 │ kubectl scale dep... │ RESTRICTED │ confirmed│
│ 03:47:24 │ kubectl delete na... │ BLOCKED    │ denied   │
│ 03:47:25 │ docker restart au... │ RESTRICTED │ cancelled│
└──────────┴──────────────────────┴────────────┴──────────┘

Session Stats:
  Total commands: 4
  Safe (auto-executed): 1
  Restricted (confirmed): 1
  Restricted (cancelled): 1
  Blocked (denied): 1
```

---

## Key Takeaway

Audit logging is what turns an AI experiment into a production tool your security team will approve. Without logs, your copilot is a liability. With logs, it's an accountable team member whose every action is traceable, reviewable, and auditable.

---

**Previous → [Lab 3: Safety Guardrails](lab3-safety-guardrails.md)** | **Next → [Lab 5: Natural Language](lab5-natural-language.md)**
