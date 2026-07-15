# Lab 6: Full Copilot

> Episode 7: Build a DevOps Copilot | **Sagar Utekar** | CNCF Ambassador | Kubestronaut

---

> **Mission:** Wire together the CLI interface, command classification, safety guardrails, audit logging, and natural language translation into a single, production-ready DevOps copilot.

---

## Concepts

### The Integration Challenge

Building individual components is the easy part. Making them work together as a cohesive system — with proper error handling, fallback behavior, and consistent UX — is where real engineering happens.

### The Full Pipeline

Every user input flows through this pipeline:

```
User Input
    │
    ▼
┌────────────────────┐
│  Is it a command   │──── Yes ──→ Skip translation
│  or natural lang?  │
└────────────────────┘
    │ No (natural language)
    ▼
┌────────────────────┐
│  NL Translation    │  ← Lab 5: "show crashing pods" → kubectl get pods ...
│  (Claude API)      │
└────────────────────┘
    │
    ▼
┌────────────────────┐
│  Classification    │  ← Lab 2: SAFE / RESTRICTED / BLOCKED
│  (Claude API)      │
└────────────────────┘
    │
    ▼
┌────────────────────┐
│  Safety Guardrails │  ← Lab 3: auto-run / confirm / deny
└────────────────────┘
    │
    ▼
┌────────────────────┐
│  Execution         │  ← Run command (or simulate)
└────────────────────┘
    │
    ▼
┌────────────────────┐
│  Audit Logger      │  ← Lab 4: Record everything to JSON
└────────────────────┘
```

### The Analogy

> Building the copilot is like assembling a car. You have built the engine (classification), brakes (guardrails), dashboard (CLI), GPS (natural language), and black box (audit). Now you bolt them together and take it for a drive.

---

## Step-by-Step Code

### Step 1: The Copilot Class Structure

```python
class DevOpsCopilot:
    """Full DevOps Copilot — all features integrated."""
    
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.logger = AuditLogger()
        self.session_id = str(uuid.uuid4())[:8]
        self.commands_executed = 0
        self.commands_blocked = 0
    
    def handle_input(self, user_input: str) -> bool:
        """Process user input through the full pipeline."""
        
        # Step 1: Detect input type
        if self.is_direct_command(user_input):
            command = user_input
        else:
            command = self.translate_to_command(user_input)
        
        # Step 2: Classify
        classification = self.classify_command(command)
        
        # Step 3: Apply guardrails
        result = self.apply_guardrail(command, classification)
        
        # Step 4: Log everything
        self.logger.log(command, classification, result)
        
        return True  # Continue running
```

### Step 2: Input Detection

```python
def is_direct_command(self, text: str) -> bool:
    """Detect if input is a direct command vs natural language."""
    command_prefixes = [
        "kubectl", "docker", "helm", "terraform", "ansible",
        "git", "curl", "cat", "ls", "grep", "rm", "find"
    ]
    first_word = text.strip().split()[0].lower()
    return first_word in command_prefixes
```

### Step 3: The Main Loop

```python
def run(self):
    """Main interaction loop."""
    self.print_banner()
    
    while True:
        try:
            user_input = input("copilot> ")
            if not user_input.strip():
                continue
            
            # Handle special commands
            if user_input.startswith("/"):
                if not self.handle_special(user_input):
                    break
                continue
            
            # Process through the pipeline
            self.handle_input(user_input)
            
        except KeyboardInterrupt:
            print("\n  Use /exit to quit")
        except EOFError:
            break
    
    self.print_session_summary()
```

### Step 4: Special Commands

```python
def handle_special(self, command: str) -> bool:
    """Handle /slash commands."""
    if command == "/exit":
        return False
    elif command == "/help":
        self.print_help()
    elif command == "/audit":
        self.logger.display_recent()
    elif command == "/stats":
        self.print_stats()
    return True
```

### Step 5: Session Summary

```python
def print_session_summary(self):
    """Display end-of-session summary."""
    stats = self.logger.get_stats()
    print(f"\n{'=' * 65}")
    print(f"  Session Summary: {self.session_id}")
    print(f"{'=' * 65}")
    print(f"  Commands executed:  {self.commands_executed}")
    print(f"  Commands blocked:   {self.commands_blocked}")
    print(f"  Audit entries:      {stats['total']}")
    print(f"  Audit log file:     {self.logger.log_file}")
    print(f"{'=' * 65}")
```

---

## Running the Full Copilot

```bash
# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Run it
python3 demos/task6_full_copilot.py
```

### Example Session

```
═══════════════════════════════════════════════════════════════════
  DevOps Copilot v1.0.0 | Session: f7a2b9c1
═══════════════════════════════════════════════════════════════════

copilot> kubectl get pods -n production
─────────────────────────────────────────────────────────────────
  Mode: Direct command
  Risk: [SAFE]
  [AUTO-RUN] kubectl get pods -n production
  >>> Executed successfully (simulated)
─────────────────────────────────────────────────────────────────

copilot> show me what's crashing
─────────────────────────────────────────────────────────────────
  Mode: Natural language translation
  Translated: kubectl get pods --field-selector=status.phase=Failed -A
  Lists all pods in Failed state across namespaces
  Risk: [SAFE]
  [AUTO-RUN] kubectl get pods --field-selector=status.phase=Failed -A
  >>> Executed successfully (simulated)
─────────────────────────────────────────────────────────────────

copilot> scale web to 5 replicas
─────────────────────────────────────────────────────────────────
  Mode: Natural language translation
  Translated: kubectl scale deployment/web --replicas=5
  Scales the web deployment to 5 pods
  Risk: [RESTRICTED]
  [CONFIRM] kubectl scale deployment/web --replicas=5
  Reason: Modifies replica count, affects resource allocation
  Execute? (y/n): y
  >>> Confirmed and executed (simulated)
─────────────────────────────────────────────────────────────────

copilot> delete the production namespace
─────────────────────────────────────────────────────────────────
  Mode: Natural language translation
  Translated: kubectl delete namespace production
  Deletes the production namespace and all its resources
  Risk: [BLOCKED]
  [BLOCKED] kubectl delete namespace production
  Reason: Namespace deletion is irreversible and destroys all resources
  This command has been denied.
─────────────────────────────────────────────────────────────────

copilot> /audit
─────────────────────────────────────────────────────────────────
  Recent Audit Log:
─────────────────────────────────────────────────────────────────
  14:23:01 | SAFE        | executed   | kubectl get pods -n production
  14:23:05 | SAFE        | executed   | kubectl get pods --field-sele...
  14:23:12 | RESTRICTED  | confirmed  | kubectl scale deployment/web...
  14:23:18 | BLOCKED     | denied     | kubectl delete namespace prod...
─────────────────────────────────────────────────────────────────

copilot> /exit

═══════════════════════════════════════════════════════════════════
  Session Summary: f7a2b9c1
═══════════════════════════════════════════════════════════════════
  Commands executed:  3
  Commands blocked:   1
  Audit entries:      4
  Audit log:          /tmp/devops-copilot-audit/audit.log
═══════════════════════════════════════════════════════════════════
```

---

## What Success Looks Like

A fully working copilot that:
1. Accepts both direct commands and natural language
2. Classifies every command by risk level
3. Auto-runs SAFE commands instantly
4. Asks confirmation for RESTRICTED commands
5. Blocks BLOCKED commands completely
6. Logs every single action to a JSON audit file
7. Provides session statistics on demand

---

## Key Takeaway

The full copilot demonstrates that AI safety is not a single feature — it is an architecture. Each layer (translation, classification, guardrails, logging) handles one concern cleanly, and together they create a system where AI amplifies human capability without bypassing human judgment on destructive operations. This is how you build AI that operations teams can trust.

---

**Previous: [Lab 5: Natural Language](lab5-natural-language.md)** | **Back to [README](../README.md)**
