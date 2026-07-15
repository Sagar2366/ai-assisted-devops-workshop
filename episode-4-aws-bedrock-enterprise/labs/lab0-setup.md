# Lab 0: AWS Bedrock Setup — Credentials, SDK, and Model Access

> **Mission:** Get AWS Bedrock configured with proper IAM permissions and verify connectivity. By the end of this lab, you will have a working Bedrock environment ready for the remaining exercises.

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] An AWS account with permissions to manage IAM and Bedrock
- [ ] AWS CLI v2 installed (`aws --version` should show 2.x)
- [ ] Python 3.9 or higher (`python3 --version`)
- [ ] A terminal with network access to AWS endpoints
- [ ] Access to the AWS Management Console (for enabling models)

---

## Concept: Why Bedrock?

Think of AWS Bedrock like a **managed vending machine for AI models**. Instead of running your own inference servers (buying the vending machine, stocking it, maintaining it), you walk up, swipe your AWS badge (IAM credentials), select a model, and get your response. AWS handles the infrastructure, scaling, and availability — you just pay per use.

For SRE teams, this means:
- No GPU clusters to manage
- No model deployment pipelines to maintain
- Same IAM controls you already use for every other AWS service
- CloudTrail logging for every AI call (audit-ready from day one)

---

## Step 1: Verify AWS CLI Configuration

First, confirm your AWS CLI is configured with valid credentials.

```bash
# Check CLI version (must be 2.x)
aws --version

# Configure credentials if not already set
aws configure
# You will be prompted for:
#   AWS Access Key ID
#   AWS Secret Access Key
#   Default region name (use us-east-1 for broadest model availability)
#   Default output format (json recommended)

# Verify your identity
aws sts get-caller-identity
```

Expected output:

```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

```python
# Quick verification script
print("=" * 65)
print("AWS CREDENTIAL VERIFICATION")
print("=" * 65)

import subprocess
import json

result = subprocess.run(
    ["aws", "sts", "get-caller-identity"],
    capture_output=True, text=True
)

if result.returncode == 0:
    identity = json.loads(result.stdout)
    print(f"Account:  {identity['Account']}")
    print(f"User ARN: {identity['Arn']}")
    print("-" * 65)
    print("[PASS] AWS credentials are valid")
else:
    print("[FAIL] AWS credentials not configured")
    print(f"Error: {result.stderr}")

print("=" * 65)
```

---

## Step 2: Install boto3

Install the AWS SDK for Python:

```bash
# Install boto3 (AWS SDK for Python)
pip install boto3

# Verify installation
python3 -c "import boto3; print(f'boto3 version: {boto3.__version__}')"
```

If you are using a virtual environment (recommended):

```bash
python3 -m venv bedrock-lab
source bedrock-lab/bin/activate
pip install boto3
```

---

## Step 3: Enable Model Access in Bedrock Console

Models are not enabled by default. You must explicitly request access through the AWS Console.

### Console Navigation

1. Sign in to the **AWS Management Console**
2. Navigate to **Amazon Bedrock** (search "Bedrock" in the service search bar)
3. In the left sidebar, click **Model access**
4. Click **Modify model access** (orange button, top right)
5. Check the boxes next to the models you want to enable:
   - Anthropic > Claude (all available versions)
   - Meta > Llama 3.1
   - Amazon > Titan Text
6. Click **Next**
7. Review your selections and click **Submit**
8. Wait for status to change from "In Progress" to **"Access granted"** (usually 1-2 minutes)

### Supported Models for This Workshop

| Provider | Model ID | Use Case |
|----------|----------|----------|
| Anthropic | us.anthropic.claude-sonnet-4-20250514-v1:0 | Complex analysis, incident response |
| Meta | meta.llama3-1-8b-instruct-v1:0 | Fast triage, simple queries |
| Amazon | amazon.titan-text-express-v1 | Summarization, general tasks |

> **Note:** Model availability varies by region. `us-east-1` (N. Virginia) typically has the broadest selection. If a model is not listed, try switching regions.

---

## Step 4: Verify Connectivity

Run this script to confirm Bedrock is accessible and your models are enabled:

```python
"""
Bedrock Connectivity Test
Verifies that your AWS credentials can reach Bedrock
and that the required models are accessible.
"""

import boto3
import json

print("=" * 65)
print("AWS BEDROCK CONNECTIVITY TEST")
print("=" * 65)

# Create Bedrock client (management plane — for listing models)
bedrock = boto3.client("bedrock", region_name="us-east-1")

# List available foundation models
print("\nQuerying available foundation models...")
print("-" * 65)

try:
    response = bedrock.list_foundation_models()
    models = response["modelSummaries"]

    # Filter for models we care about
    target_providers = ["Anthropic", "Meta", "Amazon"]
    workshop_models = [
        m for m in models
        if m.get("providerName") in target_providers
    ]

    print(f"\nFound {len(models)} total models")
    print(f"Workshop-relevant models: {len(workshop_models)}")
    print("-" * 65)

    for model in workshop_models[:10]:
        print(f"  {model['modelId']}")
        print(f"    Provider: {model['providerName']}")
        print(f"    Status:   {model.get('modelLifecycle', {}).get('status', 'ACTIVE')}")
        print()

    print("=" * 65)
    print("[PASS] Bedrock connectivity verified successfully")
    print("=" * 65)

except Exception as e:
    print(f"\n[FAIL] Could not connect to Bedrock")
    print(f"Error: {e}")
    print("-" * 65)
    print("Troubleshooting steps:")
    print("  1. Check your AWS credentials (aws sts get-caller-identity)")
    print("  2. Verify region (us-east-1 recommended)")
    print("  3. Ensure IAM policy allows bedrock:ListFoundationModels")
    print("=" * 65)
```

---

## Troubleshooting

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `AccessDeniedException` | IAM policy missing Bedrock permissions | Add `bedrock:*` to your user/role policy |
| `Could not connect to the endpoint URL` | Wrong region or network issue | Verify region in `aws configure`; check VPN/proxy |
| `ModelNotReadyException` | Model not yet enabled | Complete Step 3; wait for "Access granted" status |
| `ValidationException: model not found` | Model ID typo or model not available in region | Double-check model ID; try `us-east-1` |
| `ExpiredTokenException` | Temporary credentials (SSO/role) expired | Run `aws sso login` or refresh your session |

### Quick Diagnostic

```bash
# Check if Bedrock is reachable in your region
aws bedrock list-foundation-models \
    --region us-east-1 \
    --query "modelSummaries[?providerName=='Anthropic'].modelId" \
    --output table
```

---

## What Success Looks Like

After completing this lab, you should see:

1. `aws sts get-caller-identity` returns your account details without errors
2. `python3 -c "import boto3"` runs without import errors
3. The connectivity test script lists available models with `[PASS]` status
4. At least the Anthropic Claude model shows as available

---

## Key Takeaway

**Bedrock uses your existing AWS IAM — no separate API keys needed.** If you can authenticate to AWS, you can use Bedrock. This means all your existing security controls (MFA, SCPs, CloudTrail, VPC endpoints) apply automatically to AI workloads. No new credential management system to learn or maintain.
