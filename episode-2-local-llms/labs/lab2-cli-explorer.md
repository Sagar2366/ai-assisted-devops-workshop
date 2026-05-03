# Lab 2: CLI Explorer — Manage Models Like Containers

> **Mission:** Learn Ollama's CLI by mapping every command to its Docker equivalent — you already know this.

---

## The Concept

Ollama's CLI is modeled after Docker. If you've used `docker pull`, `docker images`, `docker ps`, you already know Ollama.

| Docker | Ollama | What It Does |
|--------|--------|--------------|
| `docker pull nginx` | `ollama pull llama3.1:8b` | Download to local storage |
| `docker images` | `ollama list` | Show what's on disk |
| `docker ps` | `ollama ps` | Show what's running in memory |
| `docker rmi nginx` | `ollama rm llama3.1:8b` | Delete from local storage |
| `docker inspect nginx` | `ollama show llama3.1:8b` | Show metadata/config |
| `docker run -it nginx sh` | `ollama run llama3.1:8b` | Interactive session |

Models are like container images — pull once, run many times. They live on disk until you delete them.

---

## What You'll Build

A Python script that wraps Ollama CLI commands via `subprocess.run()` and prints their output in a clean format.

---

## Step 1: Run the CLI Commands

```python
import subprocess

def run_cmd(cmd, description):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
    print(result.stdout.strip())
```

---

## Step 2: The Key Commands

```bash
# What's on disk?
ollama list

# What's loaded in RAM right now?
ollama ps

# Inspect a model's metadata
ollama show qwen2.5-coder:7b

# What version of Ollama am I running?
ollama --version
```

---

## Step 3: Run It

```bash
python3 demos/ollama/task2_cli_explorer.py
```

---

## What Success Looks Like

You see your locally available models, their sizes, and which ones are currently loaded in memory. `ollama show` reveals the model's architecture, parameters, and template.

---

## Key Takeaway

If you know Docker, you know Ollama. `pull` = download, `list` = local inventory, `ps` = running models, `show` = inspect, `rm` = delete. Models are container images for AI.

---

## Bonus: Interactive Session Commands

When you're inside an `ollama run` session, you have a second set of commands for inspecting and tweaking the model live. Useful for experimentation before writing code.

```bash
ollama run qwen2.5-coder:7b

# Inside the session:
/show info          # Architecture, parameter count, quantization, context length
/show parameters    # Current parameter values (temperature, top_p, etc.)
/show system        # System prompt baked into the model (if any)

/set parameter temperature 0.2    # Override a parameter for this session
/set system "You are a senior SRE. Be concise."   # Set a system prompt live

/clear              # Wipe conversation context — fresh start
/bye                # Exit the session
```

This is the fastest way to test different temperatures, system prompts, and model behaviors without writing a script. Try it before you code.

---

Next: [Lab 3: Model Parameters](lab3-model-parameters.md)
