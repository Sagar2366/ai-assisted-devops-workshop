# Lab 0: Installing and Configuring Claude Code CLI

> **Mission:** Install Claude Code, authenticate, and verify your environment is ready for advanced DevOps workflows.

## Concept: What Is Claude Code?

Think of Claude Code as a **senior engineer who lives in your terminal**. Unlike chat interfaces, Claude Code:

- Has direct access to your filesystem, shell, and git history
- Reads your project context automatically via CLAUDE.md files
- Executes commands with your permission (or autonomously with trust settings)
- Maintains conversation context across your entire codebase

**Analogy:** If Claude Desktop is like pair programming over screen share, Claude Code is like having a teammate sitting at the next desk with full access to the same development environment.

## Prerequisites

- Node.js 18+ installed
- An Anthropic API key OR Claude Max/Team/Enterprise subscription
- Terminal access (bash, zsh, or fish)

## Step 1: Install Claude Code

```bash
# Install globally via npm
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version

# Alternative: use npx without global install
npx @anthropic-ai/claude-code --version
```

## Step 2: Authenticate

### Option A: API Key Authentication

```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Add to your shell profile for persistence
echo 'export ANTHROPIC_API_KEY="sk-ant-YOUR_KEY_HERE"' >> ~/.zshrc
source ~/.zshrc
```

### Option B: Claude Max / Team / Enterprise (OAuth)

```bash
# Launch Claude Code — it will open a browser for OAuth
claude

# Follow the browser prompts to authenticate
# Your session token is stored securely in ~/.claude/
```

## Step 3: First Launch

```bash
# Navigate to any project directory
cd ~/your-devops-repo

# Launch Claude Code
claude

# You should see the interactive prompt:
# Claude Code v1.x.x
# ╭──────────────────────╮
# │ How can I help you?   │
# ╰──────────────────────╯
```

## Step 4: Verify Core Capabilities

Inside the Claude Code session, test these commands:

```
# Check Claude can read your project
> What files are in this directory?

# Check Claude can execute commands
> Run `git status` and summarize the result

# Check Claude understands your project
> Describe the architecture of this repository
```

## Step 5: Understand the Settings Hierarchy

```bash
# User-level settings (your personal preferences)
cat ~/.claude/settings.json

# Project-level settings (shared with team via git)
cat .claude/settings.json

# Example: View your current configuration
claude config list
```

## Step 6: Configure Trust Settings for DevOps

For DevOps workflows, you often need Claude Code to run infrastructure commands. Configure permissions appropriately:

```bash
# In your project's .claude/settings.json
cat > .claude/settings.json << 'EOF'
{
  "permissions": {
    "allow": [
      "Bash(kubectl get *)",
      "Bash(terraform plan *)",
      "Bash(helm list *)",
      "Bash(docker ps *)",
      "Bash(git *)"
    ],
    "deny": [
      "Bash(kubectl delete *)",
      "Bash(terraform destroy *)",
      "Bash(rm -rf *)"
    ]
  }
}
EOF
```

## Step 7: Test the DevOps Setup

```bash
# Start Claude Code in your infrastructure repo
cd ~/infrastructure-repo
claude

# Ask it to analyze your infrastructure
> Analyze the Terraform modules in this repo and list all AWS resources

# Ask it to check cluster health (if kubectl is configured)
> Run kubectl get pods --all-namespaces and flag any pods not in Running state
```

## What Success Looks Like

After completing this lab, you should be able to:

- [x] Launch Claude Code from any directory
- [x] Authenticate successfully (API key or OAuth)
- [x] Have Claude Code read and understand your project files
- [x] Execute shell commands through Claude Code
- [x] See the settings hierarchy (user, project, CLAUDE.md)
- [x] Have basic permissions configured for DevOps tools

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `command not found: claude` | Ensure npm global bin is in your PATH |
| Authentication fails | Check API key format starts with `sk-ant-` |
| Permission denied on commands | Check `.claude/settings.json` allow list |
| Slow responses | Verify network connectivity to api.anthropic.com |
| Context too large | Add `.claudeignore` file (works like `.gitignore`) |

## Key Takeaway

Claude Code is most powerful when it understands your project context. The next lab shows you how to give it that context through CLAUDE.md files — turning it from a generic assistant into a team member who knows your infrastructure inside out.

## Next

Proceed to [Lab 1: Writing CLAUDE.md Files](lab1-claude-md.md) to encode your DevOps knowledge into project context.
