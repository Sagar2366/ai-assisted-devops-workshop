# Lab 0: API Setup and Environment Verification

## Mission

Get Claude API access configured and verified so you can interact with Claude programmatically — the foundation for every lab that follows.

---

## Concept: API Keys Are Production Secrets

Think of your API key like a Kubernetes service account token. It grants access to a powerful system, costs real money when used, and should never appear in source code, logs, or Slack messages. Treat it exactly like you would treat a database credential or cloud provider secret.

---

## Step 1: Get Your API Key

1. Navigate to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in to your account
3. Go to **Settings** > **API Keys**
4. Click **Create Key**
5. Give it a descriptive name (e.g., `devops-workshop-lab`)
6. Copy the key immediately — you will not be able to see it again

> **SRE Pro Tip:** This is like generating a new service account key in GCP or creating an IAM access key in AWS. The moment you close that dialog, the secret is gone. Store it in a password manager or vault right away.

---

## Step 2: Install the Anthropic Python SDK

```bash
pip install anthropic
```

Verify the installation:

```bash
python -c "import anthropic; print(f'SDK version: {anthropic.__version__}')"
```

---

## Step 3: Set Your API Key

### Option A: Environment Variable (recommended for development)

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

Then reload your shell:

```bash
source ~/.zshrc  # or ~/.bashrc
```

### Option B: .env File (recommended for projects)

Create a `.env` file in your project directory:

```bash
echo 'ANTHROPIC_API_KEY=sk-ant-api03-your-key-here' > .env
```

Then load it in Python:

```python
from dotenv import load_dotenv
load_dotenv()
```

> **IMPORTANT:** Add `.env` to your `.gitignore` immediately. Never commit API keys.

```bash
echo '.env' >> .gitignore
```

---

## Step 4: Verify Your Setup

Create a file called `verify_setup.py`:

```python
import anthropic

print("=" * 65)
print("Claude API Setup Verification")
print("=" * 65)

# Initialize the client (uses ANTHROPIC_API_KEY env var automatically)
client = anthropic.Anthropic()

# Make a simple test call
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Respond with exactly: 'API connection verified. Ready for DevOps.' Nothing else."
        }
    ]
)

print(f"\nModel: {message.model}")
print(f"Response: {message.content[0].text}")
print(f"Input tokens: {message.usage.input_tokens}")
print(f"Output tokens: {message.usage.output_tokens}")
print(f"\nStop reason: {message.stop_reason}")
print("=" * 65)
print("Setup complete! You are ready for the workshop.")
print("=" * 65)
```

Run it:

```bash
python verify_setup.py
```

---

## Pricing Reference

Understand what each API call costs — just like monitoring your cloud spend:

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Context Window |
|-------|----------------------|------------------------|----------------|
| Haiku 3.5 | $0.80 | $4.00 | 200K |
| Sonnet 4 | $3.00 | $15.00 | 200K |
| Opus 4 | $15.00 | $75.00 | 200K |

> **Cost Analogy:** Think of tokens like compute units. Haiku is a spot instance — cheap and fast. Sonnet is an on-demand instance — reliable and balanced. Opus is a dedicated host — expensive but maximum capability. Choose wisely based on the task, just like you choose instance types for workloads.

---

## What Success Looks Like

```
=================================================================
Claude API Setup Verification
=================================================================

Model: claude-sonnet-4-20250514
Response: API connection verified. Ready for DevOps.
Input tokens: 28
Output tokens: 11

Stop reason: end_turn
=================================================================
Setup complete! You are ready for the workshop.
=================================================================
```

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `AuthenticationError` | Invalid or missing API key | Check your `ANTHROPIC_API_KEY` env var |
| `ModuleNotFoundError` | SDK not installed | Run `pip install anthropic` |
| `RateLimitError` | Too many requests | Wait and retry, or check your plan limits |
| `APIConnectionError` | Network issue | Check firewall, proxy, or VPN settings |

---

## Key Takeaway

The API key is your gateway to cloud AI — treat it like a production secret. Rotate it if exposed, scope it to the minimum needed access, and never hardcode it. Everything in this workshop builds on this foundation.
