# Lab 0: Environment Setup

> **Sagar Utekar** | CNCF Ambassador | Kubestronaut | Docker Captain

> **Mission:** Prepare your environment with the tools, dependencies, and sample files needed to run AI-powered IaC security scanning throughout this episode.

---

## Concepts

### The Security Scanning Toolkit

Think of our setup like assembling a detective's toolkit before investigating a crime scene:

| Component | Analogy | Purpose |
|-----------|---------|---------|
| Anthropic SDK | The detective's brain | AI reasoning about security |
| PyYAML | Evidence reader | Parse Kubernetes manifests |
| Sample manifests | Crime scene evidence | Intentionally insecure files to scan |
| Python 3.10+ | The lab equipment | Runtime for our tools |

### Why These Tools?

The Anthropic Python SDK gives us direct access to Claude's reasoning capabilities. Combined with structured prompting, we can build security tools that understand *intent* — not just pattern-match against regex rules.

---

## Step 1: Verify Python Installation

```bash
python3 --version
# Expected: Python 3.10 or higher
```

If you need to install Python 3.10+:
```bash
# macOS
brew install python@3.12

# Ubuntu/Debian
sudo apt update && sudo apt install python3.12 python3.12-venv

# Amazon Linux / RHEL
sudo dnf install python3.12
```

## Step 2: Create Virtual Environment

```bash
# Navigate to episode directory
cd episode-11-iac-ai-security

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

## Step 3: Install Dependencies

```bash
pip install anthropic pyyaml
```

Verify installation:
```python
python3 -c "import anthropic; print(f'Anthropic SDK: {anthropic.__version__}')"
python3 -c "import yaml; print(f'PyYAML: {yaml.__version__}')"
```

## Step 4: Configure API Key

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"

# Verify it's set
python3 -c "
import os
key = os.environ.get('ANTHROPIC_API_KEY', '')
if key and key != 'your-key-here':
    print(f'API key configured: {key[:8]}...{key[-4:]}')
else:
    print('WARNING: API key not set or is placeholder')
"
```

For persistence across sessions:
```bash
# Add to your shell profile
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## Step 5: Verify Sample Manifests

Check that the intentionally insecure sample files are present:

```bash
ls demos/sample-manifests/
# Expected:
# insecure-deployment.yaml
# insecure-dockerfile
# insecure-terraform.tf
```

Quick validation:
```bash
# Check Kubernetes manifest parses correctly
python3 -c "
import yaml
with open('demos/sample-manifests/insecure-deployment.yaml') as f:
    docs = list(yaml.safe_load_all(f))
    print(f'K8s manifest loaded: {len(docs)} document(s)')
    for doc in docs:
        print(f'  - Kind: {doc.get(\"kind\", \"unknown\")}')
"
```

## Step 6: Test API Connectivity

```bash
python3 -c "
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model='claude-sonnet-4-20250514',
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'Reply with: IaC Security Lab Ready'}]
)
print(response.content[0].text)
"
```

## Step 7: Directory Structure Verification

```bash
# Verify full structure
find . -type f | sort
```

Expected output:
```
./README.md
./demos/sample-manifests/insecure-deployment.yaml
./demos/sample-manifests/insecure-dockerfile
./demos/sample-manifests/insecure-terraform.tf
./demos/task1_terraform_generator.py
./demos/task2_terraform_reviewer.py
./demos/task3_k8s_security_scanner.py
./demos/task4_dockerfile_scanner.py
./demos/task5_compliance_checker.py
./demos/task6_remediation.py
./labs/lab0-setup.md
./labs/lab1-terraform-generator.md
./labs/lab2-terraform-reviewer.md
./labs/lab3-k8s-security-scanner.md
./labs/lab4-dockerfile-scanner.md
./labs/lab5-compliance-checker.md
./labs/lab6-remediation.md
```

---

## What Success Looks Like

After completing this lab, you should see:

```
✓ Python 3.10+ installed and verified
✓ Virtual environment created and activated
✓ anthropic and pyyaml packages installed
✓ ANTHROPIC_API_KEY configured and tested
✓ Sample manifests present and parseable
✓ API connectivity confirmed with test message
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: anthropic` | Run `pip install anthropic` in your venv |
| `AuthenticationError` | Check your API key is valid and exported |
| `yaml.scanner.ScannerError` | Ensure YAML files have no tab characters |
| `Connection timeout` | Check network/proxy settings |

---

## Key Takeaway

A properly configured environment is the foundation for all security scanning work. By using a virtual environment and validating each component, we ensure reproducible results across all six labs in this episode.

---

**Next:** [Lab 1 — Terraform Generator](lab1-terraform-generator.md) — Generate secure Terraform from natural language descriptions.
