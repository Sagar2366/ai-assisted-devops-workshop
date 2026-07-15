# Lab 0: Environment Setup

## Mission

Get your environment ready for prompt engineering experiments. By the end of this lab, you will have a working Python environment with the Anthropic SDK and a verified API connection.

---

## What is Prompt Engineering?

Prompt engineering is the practice of designing and refining inputs to AI models to get reliable, useful outputs. For DevOps and SRE teams, this means crafting prompts that consistently produce:

- Accurate incident triage decisions
- Reliable troubleshooting steps
- Well-structured runbooks and postmortems
- Safe change review assessments

Think of it like writing good runbooks for humans — the clearer and more structured your instructions, the better the output. The difference is that with AI, you can iterate on your "instructions" in seconds rather than weeks.

---

## Step 1: Verify Python Version

```bash
python3 --version
# Required: Python 3.10 or higher
```

If you need to install Python 3.10+, use your package manager:

```bash
# macOS
brew install python@3.12

# Ubuntu/Debian
sudo apt install python3.12
```

---

## Step 2: Create a Virtual Environment

```bash
# Create a project directory for your experiments
mkdir -p ~/prompt-engineering-lab
cd ~/prompt-engineering-lab

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate
```

---

## Step 3: Install the Anthropic SDK

```bash
pip install anthropic
```

Verify the installation:

```bash
python3 -c "import anthropic; print(f'Anthropic SDK version: {anthropic.__version__}')"
```

---

## Step 4: Set Your API Key

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Verify it's set
echo $ANTHROPIC_API_KEY | head -c 10
# Should show: sk-ant-api
```

To make this permanent, add it to your shell profile:

```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

---

## Step 5: Test Your Connection

Create a file called `test_connection.py`:

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Respond with exactly: CONNECTION_OK"
        }
    ]
)

response_text = message.content[0].text
print(f"Response: {response_text}")

if "CONNECTION_OK" in response_text:
    print("API connection verified successfully!")
else:
    print("Unexpected response - check your setup")
```

Run the test:

```bash
python3 test_connection.py
```

---

## Step 6: Create a Helper Module

We will reuse this helper throughout the labs. Create `sre_prompt.py`:

```python
import anthropic


def call_claude(prompt: str, model: str = "claude-sonnet-4-20250514", max_tokens: int = 1024) -> str:
    """Send a prompt to Claude and return the response text."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text


def call_claude_with_system(system: str, prompt: str, model: str = "claude-sonnet-4-20250514", max_tokens: int = 1024) -> str:
    """Send a prompt with a system message to Claude."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text


if __name__ == "__main__":
    result = call_claude("Say 'helper module working' in exactly those words.")
    print(f"Test result: {result}")
```

Test it:

```bash
python3 sre_prompt.py
```

---

## What Success Looks Like

After completing this lab, you should see:

```
$ python3 test_connection.py
Response: CONNECTION_OK
API connection verified successfully!

$ python3 sre_prompt.py
Test result: helper module working
```

---

## Key Takeaway

A reliable prompt engineering workflow starts with a solid foundation: a working SDK, verified API access, and reusable helper functions. Everything we build in the next 6 labs depends on this setup working correctly.

---

## Next

[Lab 1: Zero-Shot Prompting](lab1-zero-shot.md) — Direct prompting without examples for quick SRE tasks
