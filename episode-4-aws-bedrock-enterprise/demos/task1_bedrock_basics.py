#!/usr/bin/env python3
"""
Task 1: Your First Bedrock API Call — Enterprise AI for SRE
=============================================================

Description:
    Make your first AWS Bedrock call using Claude for Kubernetes incident
    analysis. This script demonstrates the fundamental pattern for invoking
    Claude models through the Bedrock runtime API using the Messages API format.

Prerequisites:
    - AWS credentials configured (via env vars, ~/.aws/credentials, or instance profile)
    - boto3 installed: pip install boto3
    - Claude model access enabled in AWS Bedrock console (us-east-1 region)

Usage:
    python task1_bedrock_basics.py
"""

import json
import time
import sys

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("ERROR: boto3 is not installed.")
    print("Install it with: pip install boto3")
    sys.exit(1)


def main():
    print("=" * 65)
    print("  TASK 1: Your First Bedrock API Call — Enterprise AI for SRE")
    print("=" * 65)
    print()
    print("  Making our first AWS Bedrock call using Claude to analyze")
    print("  a real Kubernetes incident scenario.")
    print()
    print("=" * 65)
    print()

    # ─────────────────────────────────────────────────────────────────
    # Step 1: Create the Bedrock Runtime Client
    # ─────────────────────────────────────────────────────────────────
    print("[Step 1] Creating Bedrock Runtime Client")
    print("-" * 65)
    print()
    print("  Region: us-east-1")
    print("  Service: bedrock-runtime")
    print()

    try:
        client = boto3.client("bedrock-runtime", region_name="us-east-1")
        print("  [OK] Bedrock runtime client created successfully.")
    except Exception as e:
        print(f"  [FAIL] Could not create Bedrock client: {e}")
        print()
        print("  Troubleshooting:")
        print("    - Ensure AWS credentials are configured")
        print("    - Run: aws configure")
        print("    - Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env vars")
        sys.exit(1)

    print()

    # ─────────────────────────────────────────────────────────────────
    # Step 2: Define the Kubernetes Incident Scenario
    # ─────────────────────────────────────────────────────────────────
    print("[Step 2] Defining Kubernetes Incident Scenario")
    print("-" * 65)
    print()

    k8s_incident = """
You are an expert SRE analyzing a Kubernetes incident. Provide a concise root cause analysis and remediation plan.

INCIDENT REPORT:
- Namespace: production
- Deployment: payment-service
- Pod Status: CrashLoopBackOff (3 of 5 pods affected)
- Last Termination Reason: OOMKilled
- Container Exit Code: 137
- Memory Limit: 512Mi
- Memory Usage Before Crash: 498Mi (97% of limit)
- Restart Count: 14 in the last hour
- Recent Change: Deployed v2.3.1 (added batch payment processing feature)
- Node Status: All nodes healthy, 40% cluster memory available

Provide:
1. Root cause analysis
2. Immediate remediation steps
3. Long-term prevention recommendations
"""

    print("  Scenario: Kubernetes Production Incident")
    print("  -----------------------------------------")
    print("  - Pod Status: CrashLoopBackOff (3/5 pods)")
    print("  - Termination Reason: OOMKilled (Exit Code 137)")
    print("  - Memory: 498Mi / 512Mi limit (97% utilization)")
    print("  - Restart Count: 14 in the last hour")
    print("  - Recent Change: v2.3.1 deployed (batch processing feature)")
    print()

    # ─────────────────────────────────────────────────────────────────
    # Step 3: Prepare and Send the Bedrock API Request
    # ─────────────────────────────────────────────────────────────────
    print("[Step 3] Calling AWS Bedrock (Claude) for Incident Analysis")
    print("-" * 65)
    print()
    print("  Model: us.anthropic.claude-sonnet-4-20250514-v1:0")
    print("  API Version: bedrock-2023-10-25 (Messages API)")
    print("  Max Tokens: 1024")
    print()
    print("  Sending request...")
    print()

    body = json.dumps({
        "anthropic_version": "bedrock-2023-10-25",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": k8s_incident}
        ]
    })

    start_time = time.time()

    try:
        response = client.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
            contentType="application/json",
            accept="application/json",
            body=body
        )

        latency = time.time() - start_time

        # ─────────────────────────────────────────────────────────────
        # Step 4: Parse and Display the Response
        # ─────────────────────────────────────────────────────────────
        print("[Step 4] Parsing Claude's Incident Analysis")
        print("-" * 65)
        print()

        result = json.loads(response["body"].read())

        # Extract the response text
        response_text = result["content"][0]["text"]
        print("  CLAUDE'S ANALYSIS:")
        print("  " + "~" * 61)
        for line in response_text.split("\n"):
            print(f"  {line}")
        print("  " + "~" * 61)
        print()

        # ─────────────────────────────────────────────────────────────
        # Step 5: Display Metadata and Usage Statistics
        # ─────────────────────────────────────────────────────────────
        print("[Step 5] Response Metadata")
        print("-" * 65)
        print()
        print(f"  Latency:        {latency:.2f} seconds")
        print(f"  Model:          {result.get('model', 'N/A')}")
        print(f"  Stop Reason:    {result.get('stop_reason', 'N/A')}")

        usage = result.get("usage", {})
        input_tokens = usage.get("input_tokens", "N/A")
        output_tokens = usage.get("output_tokens", "N/A")
        print(f"  Input Tokens:   {input_tokens}")
        print(f"  Output Tokens:  {output_tokens}")

        if isinstance(input_tokens, int) and isinstance(output_tokens, int):
            total_tokens = input_tokens + output_tokens
            print(f"  Total Tokens:   {total_tokens}")

        print()
        print("  HTTP Status:    " + str(response.get("ResponseMetadata", {}).get("HTTPStatusCode", "N/A")))
        print()

    except ClientError as e:
        latency = time.time() - start_time
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        print(f"  [FAIL] API call failed after {latency:.2f}s")
        print(f"  Error Code: {error_code}")
        print(f"  Message: {error_message}")
        print()

        if error_code == "AccessDeniedException":
            print("  TROUBLESHOOTING — AccessDeniedException:")
            print("  -----------------------------------------")
            print("  1. Ensure your IAM user/role has bedrock:InvokeModel permission")
            print("  2. Check that the Claude model is enabled in the Bedrock console:")
            print("     AWS Console -> Bedrock -> Model access -> Enable Claude models")
            print("  3. Verify you are using the correct region (us-east-1)")
            print("  4. Example IAM policy:")
            print('     {')
            print('       "Effect": "Allow",')
            print('       "Action": "bedrock:InvokeModel",')
            print('       "Resource": "arn:aws:bedrock:us-east-1::foundation-model/*"')
            print('     }')
        elif error_code == "ValidationException":
            print("  TROUBLESHOOTING — ValidationException:")
            print("  -----------------------------------------")
            print("  1. The model ID may be incorrect or not available in your region")
            print("  2. Check that the request body format matches the Messages API spec")
            print("  3. Ensure anthropic_version is set to 'bedrock-2023-10-25'")
        elif error_code == "ResourceNotFoundException":
            print("  TROUBLESHOOTING — Model Not Found:")
            print("  -----------------------------------------")
            print("  1. The model may not be enabled in your account")
            print("  2. Go to AWS Bedrock Console -> Model access")
            print("  3. Request access to Anthropic Claude models")
            print("  4. Wait for access to be granted (usually immediate)")
        elif error_code == "ThrottlingException":
            print("  TROUBLESHOOTING — Throttling:")
            print("  -----------------------------------------")
            print("  1. You have exceeded the API rate limit")
            print("  2. Implement exponential backoff in production")
            print("  3. Request a quota increase via AWS Support if needed")
        else:
            print(f"  TROUBLESHOOTING — {error_code}:")
            print("  -----------------------------------------")
            print("  1. Check AWS documentation for this error code")
            print("  2. Verify credentials and permissions")
            print("  3. Ensure the Bedrock service is available in your region")

        print()
        sys.exit(1)

    except Exception as e:
        print(f"  [FAIL] Unexpected error: {e}")
        print()
        print("  Troubleshooting:")
        print("    - Verify network connectivity to AWS")
        print("    - Check that boto3 is up to date: pip install --upgrade boto3")
        print("    - Ensure your system clock is synchronized (required for AWS auth)")
        print()
        sys.exit(1)

    # ─────────────────────────────────────────────────────────────────
    # Key Learning
    # ─────────────────────────────────────────────────────────────────
    print("=" * 65)
    print("  KEY LEARNING")
    print("=" * 65)
    print()
    print("  1. AWS Bedrock provides a managed API for Claude — no need to")
    print("     host or manage model infrastructure yourself.")
    print()
    print("  2. The Messages API format (anthropic_version: bedrock-2023-10-25)")
    print("     is the standard interface for Claude on Bedrock.")
    print()
    print("  3. Authentication is handled entirely through IAM — your AWS")
    print("     credentials are your API key. No separate AI service keys needed.")
    print()
    print("  4. Response metadata (tokens, latency) enables cost tracking and")
    print("     performance monitoring — essential for production SRE tooling.")
    print()
    print("  5. Claude can analyze complex K8s incidents and provide actionable")
    print("     remediation steps in seconds — accelerating MTTR.")
    print()
    print("=" * 65)
    print("  Next: task2_iam_auth.py — IAM Authentication Patterns for")
    print("        secure, enterprise-grade AI access control.")
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()
