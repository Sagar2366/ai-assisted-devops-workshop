#!/usr/bin/env python3
"""
Task 2: IAM Authentication Patterns — Secure AI Access
========================================================

Description:
    Demonstrate IAM-based authentication patterns for Bedrock access.
    This script explores the credential chain, explicit sessions, role
    assumption for cross-account access, and session-based temporary
    credentials — the building blocks of enterprise AI security.

Prerequisites:
    - AWS credentials configured (via env vars, ~/.aws/credentials, or instance profile)
    - boto3 installed: pip install boto3
    - (Optional) A cross-account IAM role ARN for the role assumption demo

Usage:
    python task2_iam_auth.py
"""

import json
import time
import sys
from datetime import datetime, timezone

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
except ImportError:
    print("ERROR: boto3 is not installed.")
    print("Install it with: pip install boto3")
    sys.exit(1)


def main():
    print("=" * 65)
    print("  TASK 2: IAM Authentication Patterns — Secure AI Access")
    print("=" * 65)
    print()
    print("  Exploring IAM-based authentication patterns that make Bedrock")
    print("  enterprise-ready: credential chains, role assumption, and")
    print("  session-based access control.")
    print()
    print("=" * 65)
    print()

    # ─────────────────────────────────────────────────────────────────
    # Experiment 1: Default Credential Chain
    # ─────────────────────────────────────────────────────────────────
    print("[Experiment 1] Default Credential Chain")
    print("-" * 65)
    print()
    print("  boto3 resolves credentials in this order:")
    print("  ┌─────────────────────────────────────────────────────────┐")
    print("  │ 1. Environment variables (AWS_ACCESS_KEY_ID, etc.)      │")
    print("  │ 2. Shared credentials file (~/.aws/credentials)         │")
    print("  │ 3. AWS config file (~/.aws/config)                      │")
    print("  │ 4. Assume Role provider (from config profiles)          │")
    print("  │ 5. ECS container credentials (AWS_CONTAINER_CREDENTIALS)│")
    print("  │ 6. EC2 instance metadata (Instance Profile / IMDS)      │")
    print("  └─────────────────────────────────────────────────────────┘")
    print()
    print("  Verifying current identity via STS get-caller-identity...")
    print()

    try:
        session = boto3.Session()
        sts_client = session.client("sts")
        identity = sts_client.get_caller_identity()

        print(f"  Account:  {identity['Account']}")
        print(f"  ARN:      {identity['Arn']}")
        print(f"  User ID:  {identity['UserId']}")
        print()

        # Determine credential source
        credentials = session.get_credentials()
        if credentials:
            resolved = credentials.get_frozen_credentials()
            source = getattr(credentials, '_credential_provider', 'default chain')
            print(f"  Credential source resolved successfully.")
            print(f"  Access Key (last 4): ...{resolved.access_key[-4:]}")
            token_status = "present (temporary credentials)" if resolved.token else "absent (long-term credentials)"
            print(f"  Session Token: {token_status}")
        print()
        print("  [OK] Identity verified — credentials are valid.")

    except NoCredentialsError:
        print("  [FAIL] No AWS credentials found.")
        print()
        print("  To configure credentials, use one of these methods:")
        print("    a) Run: aws configure")
        print("    b) Set environment variables:")
        print("       export AWS_ACCESS_KEY_ID=AKIA...")
        print("       export AWS_SECRET_ACCESS_KEY=...")
        print("    c) Use an EC2 instance profile or ECS task role")
        print()
        print("  Continuing with remaining experiments (some may fail)...")

    except ClientError as e:
        print(f"  [FAIL] STS call failed: {e.response['Error']['Message']}")
        print("  Continuing with remaining experiments...")

    print()

    # ─────────────────────────────────────────────────────────────────
    # Experiment 2: Explicit Session Configuration
    # ─────────────────────────────────────────────────────────────────
    print("[Experiment 2] Explicit Session Configuration")
    print("-" * 65)
    print()
    print("  In production, you often need explicit control over which")
    print("  profile and region your Bedrock client uses.")
    print()

    # Demonstrate region-specific session
    print("  --- Example: Region-Specific Session ---")
    print()
    print("  Creating session for us-east-1 (primary Bedrock region)...")

    try:
        explicit_session = boto3.Session(region_name="us-east-1")
        bedrock_client = explicit_session.client("bedrock-runtime")
        print(f"  [OK] Bedrock client created for region: us-east-1")
        print(f"  Endpoint: https://bedrock-runtime.us-east-1.amazonaws.com")
    except Exception as e:
        print(f"  [INFO] Session creation note: {e}")

    print()

    # Demonstrate profile-based session
    print("  --- Example: Profile-Based Session ---")
    print()
    print("  For multi-environment access, use named profiles:")
    print()
    print("  # ~/.aws/config")
    print("  [profile bedrock-dev]")
    print("  region = us-east-1")
    print("  role_arn = arn:aws:iam::111111111111:role/bedrock-dev-role")
    print("  source_profile = default")
    print()
    print("  [profile bedrock-prod]")
    print("  region = us-east-1")
    print("  role_arn = arn:aws:iam::222222222222:role/bedrock-prod-role")
    print("  source_profile = default")
    print()
    print("  Usage in code:")
    print("    session = boto3.Session(profile_name='bedrock-prod')")
    print("    client = session.client('bedrock-runtime')")
    print()

    # Attempt to show available profiles
    try:
        available_profiles = boto3.Session().available_profiles
        print(f"  Profiles available on this system: {available_profiles}")
    except Exception:
        print("  Profiles available on this system: ['default']")

    print()

    # ─────────────────────────────────────────────────────────────────
    # Experiment 3: Role Assumption with STS
    # ─────────────────────────────────────────────────────────────────
    print("[Experiment 3] Role Assumption with STS")
    print("-" * 65)
    print()
    print("  Cross-account role assumption enables centralized AI governance:")
    print("  - AI team manages Bedrock access in a dedicated account")
    print("  - Application accounts assume a role to invoke models")
    print("  - All access is auditable via CloudTrail")
    print()

    # Placeholder role ARN — users should customize this
    CROSS_ACCOUNT_ROLE_ARN = "arn:aws:iam::123456789012:role/BedrockCrossAccountRole"
    SESSION_NAME = "sre-bedrock-session"

    print(f"  Target Role: {CROSS_ACCOUNT_ROLE_ARN}")
    print(f"  Session Name: {SESSION_NAME}")
    print()
    print("  NOTE: Replace the role ARN above with your actual cross-account")
    print("        role to test this in your environment.")
    print()
    print("  Attempting role assumption...")
    print()

    try:
        sts_client = boto3.client("sts")

        assumed_role = sts_client.assume_role(
            RoleArn=CROSS_ACCOUNT_ROLE_ARN,
            RoleSessionName=SESSION_NAME,
            DurationSeconds=900  # 15 minutes — minimum for Bedrock calls
        )

        temp_credentials = assumed_role["Credentials"]

        print("  [OK] Role assumed successfully!")
        print(f"  Assumed Role ARN:  {assumed_role['AssumedRoleUser']['Arn']}")
        print(f"  Access Key:        ...{temp_credentials['AccessKeyId'][-4:]}")
        print(f"  Expiration:        {temp_credentials['Expiration']}")
        print()

        # Create a Bedrock client with the assumed role credentials
        print("  Creating Bedrock client with assumed role credentials...")

        assumed_bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
            aws_access_key_id=temp_credentials["AccessKeyId"],
            aws_secret_access_key=temp_credentials["SecretAccessKey"],
            aws_session_token=temp_credentials["SessionToken"]
        )

        print("  [OK] Bedrock client created with cross-account credentials.")
        print()
        print("  This client can now invoke models using the assumed role's")
        print("  permissions — perfect for multi-account enterprise setups.")

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        print(f"  [EXPECTED] Role assumption failed: {error_code}")
        print(f"  Message: {error_message}")
        print()

        if error_code == "AccessDenied":
            print("  This is expected if the placeholder role ARN is used.")
            print("  In a real setup, you would need:")
            print("    1. The target role to exist in the target account")
            print("    2. A trust policy allowing your account to assume it")
            print("    3. Your IAM user/role to have sts:AssumeRole permission")
            print()
            print("  Example trust policy on the target role:")
            print("  {")
            print('    "Effect": "Allow",')
            print('    "Principal": {')
            print('      "AWS": "arn:aws:iam::YOUR_ACCOUNT:root"')
            print("    },")
            print('    "Action": "sts:AssumeRole",')
            print('    "Condition": {')
            print('      "StringEquals": {')
            print('        "sts:ExternalId": "bedrock-access-2024"')
            print("      }")
            print("    }")
            print("  }")
        elif error_code == "MalformedPolicyDocument":
            print("  The role's trust policy may be misconfigured.")
            print("  Check the trust relationship in the IAM console.")
        else:
            print(f"  Review the error and adjust the role configuration.")

    except NoCredentialsError:
        print("  [SKIP] No credentials available to attempt role assumption.")

    print()

    # ─────────────────────────────────────────────────────────────────
    # Experiment 4: Session-Based Access
    # ─────────────────────────────────────────────────────────────────
    print("[Experiment 4] Session-Based Access (Temporary Credentials)")
    print("-" * 65)
    print()
    print("  Temporary credentials provide time-limited access — a security")
    print("  best practice for automated SRE tools and CI/CD pipelines.")
    print()

    try:
        sts_client = boto3.client("sts")

        print("  Requesting session token with limited duration...")
        print()

        # Get a session token (works with IAM user credentials)
        # Note: This won't work with credentials that are already temporary
        try:
            session_token_response = sts_client.get_session_token(
                DurationSeconds=900  # 15 minutes
            )

            temp_creds = session_token_response["Credentials"]
            expiration = temp_creds["Expiration"]

            # Calculate time until expiration
            if expiration.tzinfo:
                now = datetime.now(timezone.utc)
            else:
                now = datetime.utcnow()

            time_remaining = expiration - now

            print("  [OK] Temporary session credentials obtained!")
            print(f"  Access Key ID:   ...{temp_creds['AccessKeyId'][-4:]}")
            print(f"  Expiration:      {expiration.isoformat()}")
            print(f"  Time Remaining:  {time_remaining}")
            print()
            print("  These credentials will automatically expire — no cleanup needed.")
            print("  If an SRE tool is compromised, exposure is limited to the")
            print("  credential lifetime.")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                print("  [INFO] get_session_token not available with current credentials.")
                print("  This typically means you are already using temporary credentials")
                print("  (e.g., from an assumed role or SSO session).")
                print()
                print("  Key concept: Temporary credentials cannot create new session")
                print("  tokens — they are already time-bounded by design.")
            else:
                print(f"  [INFO] Session token request returned: {error_code}")
                print(f"  Message: {e.response['Error']['Message']}")

    except NoCredentialsError:
        print("  [SKIP] No credentials available for session token request.")

    print()
    print("  --- Credential Expiration Concept ---")
    print()
    print("  Temporary credentials provide defense-in-depth:")
    print("  - If credentials leak, damage is time-limited")
    print("  - Automated rotation eliminates stale access")
    print("  - CloudTrail logs tie actions to specific sessions")
    print("  - Revocation is immediate via IAM policy changes")
    print()

    # ─────────────────────────────────────────────────────────────────
    # Summary: Credential Sources and Use Cases
    # ─────────────────────────────────────────────────────────────────
    print("=" * 65)
    print("  CREDENTIAL SOURCES — SUMMARY TABLE")
    print("=" * 65)
    print()
    print("  ┌──────────────────────┬──────────────────────────────────┐")
    print("  │ Credential Source    │ Use Case                         │")
    print("  ├──────────────────────┼──────────────────────────────────┤")
    print("  │ Environment Vars     │ CI/CD pipelines, containers,     │")
    print("  │                      │ local development                │")
    print("  ├──────────────────────┼──────────────────────────────────┤")
    print("  │ Shared Credentials   │ Developer workstations,          │")
    print("  │ (~/.aws/credentials) │ multi-profile setups             │")
    print("  ├──────────────────────┼──────────────────────────────────┤")
    print("  │ IAM Instance Profile │ EC2-based SRE tools,             │")
    print("  │                      │ no credentials to manage         │")
    print("  ├──────────────────────┼──────────────────────────────────┤")
    print("  │ ECS Task Role        │ Containerized microservices,     │")
    print("  │                      │ per-service access control       │")
    print("  ├──────────────────────┼──────────────────────────────────┤")
    print("  │ IAM Role Assumption  │ Cross-account access,            │")
    print("  │ (STS AssumeRole)     │ centralized AI governance        │")
    print("  ├──────────────────────┼──────────────────────────────────┤")
    print("  │ SSO / Identity Center│ Enterprise user access,          │")
    print("  │                      │ federated identity               │")
    print("  ├──────────────────────┼──────────────────────────────────┤")
    print("  │ Session Token        │ Time-limited automated access,   │")
    print("  │ (GetSessionToken)    │ reduced blast radius             │")
    print("  └──────────────────────┴──────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────
    # Key Learning
    # ─────────────────────────────────────────────────────────────────
    print("=" * 65)
    print("  KEY LEARNING")
    print("=" * 65)
    print()
    print("  IAM is the enterprise advantage of AWS Bedrock over direct API access:")
    print()
    print("  1. No API keys to manage — authentication flows through IAM,")
    print("     the same system securing all your AWS infrastructure.")
    print()
    print("  2. Fine-grained access control — restrict which models, actions,")
    print("     and resources each team or service can access.")
    print()
    print("  3. Cross-account governance — centralize AI model access in a")
    print("     dedicated account while granting scoped access to workloads.")
    print()
    print("  4. Temporary credentials — time-bounded access reduces risk from")
    print("     credential exposure; no long-lived secrets to rotate.")
    print()
    print("  5. Full audit trail — every Bedrock invocation is logged in")
    print("     CloudTrail with the caller identity, enabling compliance")
    print("     and cost attribution.")
    print()
    print("=" * 65)
    print("  Next: task3 — Bedrock guardrails, model invocation logging,")
    print("        and enterprise governance patterns for production AI.")
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()
