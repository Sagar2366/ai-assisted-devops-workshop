# Lab 1: CLI Interface

> Episode 7: Build a DevOps Copilot | **Sagar Utekar** | CNCF Ambassador | Kubestronaut

---

## Mission

Build an interactive command-line interface that accepts user input in a loop — the foundation every other component plugs into.

---

## Concepts

### The REPL Pattern

REPL stands for **Read-Eval-Print Loop** — the same pattern used by Python's interactive shell, bash, and every CLI tool you've ever used:

1. **Read** — accept user input
2. **Eval** — process the input (later: classify, guardrail, execute)
3. **Print** — show the result
4. **Loop** — go back to step 1

### Why CLI Over Web UI?

For SRE work, CLIs beat web dashboards every time:

| CLI | Web UI |
|-----|--------|
| Works over SSH to prod servers | Requires browser + network |
| Scriptable — pipe output anywhere | Click, click, click |
| Millisecond response time | Page loads, spinners, latency |
| Works in incident war rooms (tmux) | Tab switching during pages |
| Keyboard-only = faster | Mouse required |

### The Analogy

> A CLI copilot is like having a senior SRE sitting next to you in the terminal — you type what you want, they suggest the command.

You're building that senior SRE, one layer at a time. This lab builds their "ears" (input) and "mouth" (output).

---

## Step-by-Step Code

### Version 1: The Minimal REPL

```python
#!/usr/bin/env python3
"""Task 1: Basic CLI Interface — the foundation of our copilot."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def display_banner():
    """Show the copilot welcome banner."""
    banner = """
[bold cyan]DevOps Copilot[/bold cyan] v0.1
[dim]Episode 7 — AI-Assisted DevOps Workshop[/dim]

Type a command or question. Type [bold]exit[/bold] to quit.
    """
    console.print(Panel(banner.strip(), border_style="cyan"))

def main():
    """Main REPL loop."""
    display_banner()
    
    # Command history
    history = []
    
    while True:
        try:
            # Read
            user_input = Prompt.ask("\n[bold green]copilot[/bold green]")
            
            # Handle empty input
            if not user_input.strip():
                continue
            
            # Handle exit
            if user_input.strip().lower() in ("exit", "quit", "q"):
                console.print("\n[dim]Goodbye! Stay safe out there. 👋[/dim]")
                break
            
            # Handle history
            if user_input.strip().lower() == "history":
                if history:
                    console.print("\n[bold]Command History:[/bold]")
                    for i, cmd in enumerate(history, 1):
                        console.print(f"  {i}. {cmd}")
                else:
                    console.print("[dim]No commands yet.[/dim]")
                continue
            
            # Store in history
            history.append(user_input)
            
            # Eval + Print (placeholder — later labs add AI here)
            console.print(f"\n[dim]Received:[/dim] {user_input}")
            console.print("[yellow]⚡ Processing will be added in Lab 2+[/yellow]")
            
        except KeyboardInterrupt:
            console.print("\n[dim]Use 'exit' to quit gracefully.[/dim]")
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()
```

---

### Version 2: Adding Structure

```python
#!/usr/bin/env python3
"""Task 1 (Enhanced): CLI Interface with command routing."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from datetime import datetime

console = Console()

class DevOpsCLI:
    """Interactive CLI for the DevOps Copilot."""
    
    def __init__(self):
        self.history = []
        self.start_time = datetime.now()
        self.running = True
    
    def display_banner(self):
        """Show welcome banner."""
        banner = """[bold cyan]DevOps Copilot[/bold cyan] v0.1
[dim]Type 'help' for available commands | 'exit' to quit[/dim]"""
        console.print(Panel(banner, border_style="cyan", padding=(1, 2)))
    
    def show_help(self):
        """Display help table."""
        table = Table(title="Available Commands", border_style="cyan")
        table.add_column("Command", style="bold")
        table.add_column("Description")
        
        table.add_row("help", "Show this help message")
        table.add_row("history", "Show command history")
        table.add_row("status", "Show copilot status")
        table.add_row("clear", "Clear the screen")
        table.add_row("exit", "Exit the copilot")
        table.add_row("[italic]anything else[/italic]", "Sent to AI for processing")
        
        console.print(table)
    
    def show_status(self):
        """Show copilot status."""
        uptime = datetime.now() - self.start_time
        console.print(f"\n[bold]Copilot Status[/bold]")
        console.print(f"  Uptime: {uptime}")
        console.print(f"  Commands processed: {len(self.history)}")
        console.print(f"  AI Engine: [yellow]Not connected (Lab 2+)[/yellow]")
        console.print(f"  Safety: [yellow]Not active (Lab 3+)[/yellow]")
        console.print(f"  Audit Log: [yellow]Not active (Lab 4+)[/yellow]")
    
    def process_input(self, user_input: str):
        """Route user input to the appropriate handler."""
        command = user_input.strip().lower()
        
        if command in ("exit", "quit", "q"):
            self.running = False
            console.print("\n[dim]Goodbye! Stay safe out there.[/dim]")
        elif command == "help":
            self.show_help()
        elif command == "history":
            self.show_history()
        elif command == "status":
            self.show_status()
        elif command == "clear":
            console.clear()
            self.display_banner()
        else:
            # Future: send to AI classifier → guardrails → executor
            self.history.append(user_input)
            console.print(f"\n[dim]→ Would process:[/dim] {user_input}")
            console.print("[yellow]  (AI processing added in Lab 2)[/yellow]")
    
    def show_history(self):
        """Display command history."""
        if not self.history:
            console.print("[dim]No commands in history yet.[/dim]")
            return
        console.print("\n[bold]Command History:[/bold]")
        for i, cmd in enumerate(self.history, 1):
            console.print(f"  [cyan]{i:3d}[/cyan] │ {cmd}")
    
    def run(self):
        """Main loop."""
        self.display_banner()
        
        while self.running:
            try:
                user_input = Prompt.ask("\n[bold green]copilot[/bold green]")
                if not user_input.strip():
                    continue
                self.process_input(user_input)
            except KeyboardInterrupt:
                console.print("\n[dim]Ctrl+C — type 'exit' to quit.[/dim]")
            except EOFError:
                break

if __name__ == "__main__":
    cli = DevOpsCLI()
    cli.run()
```

---

## What Success Looks Like

```
╭────────────────────────────────────────╮
│ DevOps Copilot v0.1                    │
│ Type 'help' for available commands     │
╰────────────────────────────────────────╯

copilot: kubectl get pods
→ Would process: kubectl get pods
  (AI processing added in Lab 2)

copilot: help
┌─────────────────────────────┐
│ Available Commands           │
├──────────┬──────────────────┤
│ Command  │ Description      │
├──────────┼──────────────────┤
│ help     │ Show this help   │
│ history  │ Show history     │
│ status   │ Show status      │
│ exit     │ Exit copilot     │
└──────────┴──────────────────┘

copilot: exit
Goodbye! Stay safe out there.
```

---

## Key Takeaway

The CLI is the interface layer — it doesn't know about safety or AI yet. It only knows how to:
1. Accept input
2. Route to handlers
3. Display output

Every future component (classification, guardrails, audit, NL) plugs into this shell. Build the skeleton first, add intelligence later.

---

**Previous → [Lab 0: Setup](lab0-setup.md)** | **Next → [Lab 2: Command Classification](lab2-command-classification.md)**
