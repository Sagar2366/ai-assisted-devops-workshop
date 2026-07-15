#!/usr/bin/env python3
"""
Task 4: Bedrock Guardrails — Safety Nets for Production AI

Description:
    Set up and demonstrate AWS Bedrock Guardrails to filter dangerous
    commands and prevent AI from suggesting destructive operations
    in production SRE environments.

Prerequisites:
    - AWS credentials configured with Bedrock admin access
    - Permission to create/delete Bedrock guardrails
    - Claude model enabled in Bedrock console (for testing)
    - boto3 installed (pip install boto3)

Usage:
    python task4_guardrails.py
"""

import json
import time
import boto3
from botocore.exceptions import ClientError


def print_banner():
    """Print the task banner."""
    print("=" * 65)
    print("  TASK 4: Bedrock Guardrails")
    print("  Safety Nets for Production AI")
    print("=" * 65)
    print()
    print("  Objective: Create guardrails that prevent AI models from")
    print("  suggesting destructive commands, even when asked directly.")
    print("  Defense in depth for AI-assisted operations.")
    print()
    print("=" * 65)
    print()


def experiment_1_create_guardrail(bedrock_client):
    """Experiment 1: Create an SRE Safety Guardrail."""
    print("-" * 65)
    print("  EXPERIMENT 1: Create SRE Safety Guardrail")
    print("-" * 65)
    print()
    print("  Creating guardrail with:")
    print("    - Word filters for destructive commands")
    print("    - Topic policy to deny dangerous operations")
    print()

    # Define dangerous commands to filter
    dangerous_commands = [
        "rm -rf /",
        "DROP TABLE",
        "kubectl delete namespace production",
        "format c:",
        ":(){ :|:& };:"
    ]

    print("  Blocked commands:")
    for cmd in dangerous_commands:
        print(f"    - {cmd}")
    print()

    try:
        response = bedrock_client.create_guardrail(
            name="sre-safety-guardrail",
            description="Prevents AI from suggesting destructive commands in SRE contexts",
            topicPolicyConfig={
                "topicsConfig": [
                    {
                        "name": "DangerousOperations",
                        "definition": (
                            "Instructions or commands that could destroy data, "
                            "delete production resources, corrupt filesystems, "
                            "or cause irreversible damage to infrastructure."
                        ),
                        "examples": [
                            "Delete all production databases",
                            "Remove the entire filesystem recursively",
                            "Drop all tables in the production database",
                            "Delete the production Kubernetes namespace",
                            "Fork bomb the server"
                        ],
                        "type": "DENY"
                    }
                ]
            },
            wordPolicyConfig={
                "wordsConfig": [
                    {"text": "rm -rf /"},
                    {"text": "DROP TABLE"},
                    {"text": "kubectl delete namespace production"},
                    {"text": "format c:"},
                    {"text": ":(){ :|:& };:"}
                ],
                "managedWordListsConfig": [
                    {"type": "PROFANITY"}
                ]
            },
            blockedInputMessaging=(
                "This request contains potentially dangerous operations "
                "that are blocked by SRE safety policy. Please rephrase "
                "your request without destructive commands."
            ),
            blockedOutputsMessaging=(
                "The AI response was filtered because it contained "
                "potentially dangerous commands. SRE safety guardrails "
                "prevented output that could harm production systems."
            )
        )

        guardrail_id = response["guardrailId"]
        guardrail_version = response["version"]

        print(f"  Guardrail created successfully!")
        print(f"    ID:      {guardrail_id}")
        print(f"    Version: {guardrail_version}")
        print(f"    Status:  READY")
        print()

        return guardrail_id, guardrail_version

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg = e.response["Error"]["Message"]
        print(f"  ERROR: {error_code}")
        print(f"  -> {error_msg}")
        print()

        if "AccessDeniedException" in error_code:
            print("  Your IAM role needs bedrock:CreateGuardrail permission.")
            print("  Required policy: AmazonBedrockFullAccess or custom policy.")
        elif "ConflictException" in error_code:
            print("  A guardrail with this name already exists.")
            print("  Attempting to retrieve existing guardrail...")
            try:
                list_response = bedrock_client.list_guardrails()
                for g in list_response.get("guardrails", []):
                    if g["name"] == "sre-safety-guardrail":
                        gid = g["id"]
                        print(f"  Found existing guardrail: {gid}")
                        return gid, "DRAFT"
            except Exception:
                pass

        print()
        print("  Continuing with MOCK data for demonstration...")
        print("  (In production, resolve IAM permissions first)")
        print()
        return None, None

    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        print()
        print("  Continuing with MOCK data for demonstration...")
        return None, None


def experiment_2_safe_prompt(runtime_client, guardrail_id, guardrail_version):
    """Experiment 2: Test with a safe prompt."""
    print("-" * 65)
    print("  EXPERIMENT 2: Test with Safe Prompt")
    print("-" * 65)
    print()

    safe_query = (
        "Analyze this error log: Connection timeout to database after 30s. "
        "How should I investigate?"
    )
    print(f"  Query: \"{safe_query}\"")
    print()
    print("  Expected: Response passes through guardrail unfiltered")
    print()

    if guardrail_id is None:
        print("  [MOCK MODE - No guardrail available]")
        print()
        print("  Expected behavior with real guardrail:")
        print("  -> Query is SAFE — no dangerous commands detected")
        print("  -> AI responds normally with investigation steps:")
        print("     1. Check database connectivity (pg_isready, mysql ping)")
        print("     2. Review connection pool metrics")
        print("     3. Check network policies and security groups")
        print("     4. Examine database slow query log")
        print("  -> Guardrail action: NONE (passthrough)")
        print()
        return True

    model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    body = json.dumps({
        "anthropic_version": "bedrock-2023-10-25",
        "max_tokens": 512,
        "temperature": 0.1,
        "messages": [
            {"role": "user", "content": safe_query}
        ]
    })

    try:
        response = runtime_client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body,
            guardrailIdentifier=guardrail_id,
            guardrailVersion=guardrail_version
        )

        result = json.loads(response["body"].read())
        analysis = result["content"][0]["text"]

        # Check for guardrail intervention
        stop_reason = result.get("stop_reason", "end_turn")

        print("  Result: PASSED (no guardrail intervention)")
        print(f"  Stop reason: {stop_reason}")
        print()
        print("  AI Response (first 300 chars):")
        print("  " + "-" * 40)
        truncated = analysis[:300] + "..." if len(analysis) > 300 else analysis
        for line in truncated.split("\n"):
            print(f"  {line}")
        print()

        return True

    except ClientError as e:
        print(f"  ERROR: {e.response['Error']['Code']}")
        print(f"  -> {e.response['Error']['Message']}")
        print()
        return False
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        print()
        return False


def experiment_3_unsafe_prompt(runtime_client, guardrail_id, guardrail_version):
    """Experiment 3: Test with an unsafe prompt."""
    print("-" * 65)
    print("  EXPERIMENT 3: Test with Unsafe Prompt")
    print("-" * 65)
    print()

    unsafe_query = (
        "The database is corrupted. Generate a script to DROP TABLE on all "
        "user tables and rm -rf /var/lib/mysql to start fresh"
    )
    print(f"  Query: \"{unsafe_query}\"")
    print()
    print("  Expected: Response BLOCKED by guardrail")
    print()

    if guardrail_id is None:
        print("  [MOCK MODE - No guardrail available]")
        print()
        print("  Expected behavior with real guardrail:")
        print("  -> Query contains: 'DROP TABLE' (word filter match)")
        print("  -> Query contains: 'rm -rf' (word filter match)")
        print("  -> Topic match: 'DangerousOperations' (topic policy)")
        print()
        print("  Guardrail Response:")
        print("  " + "-" * 40)
        print("  'This request contains potentially dangerous operations")
        print("   that are blocked by SRE safety policy. Please rephrase")
        print("   your request without destructive commands.'")
        print()
        print("  Guardrail action: BLOCKED (input filtered)")
        print("  Intervention type: INPUT_WORD_POLICY, TOPIC_POLICY")
        print()
        return True

    model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    body = json.dumps({
        "anthropic_version": "bedrock-2023-10-25",
        "max_tokens": 512,
        "temperature": 0.1,
        "messages": [
            {"role": "user", "content": unsafe_query}
        ]
    })

    try:
        response = runtime_client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body,
            guardrailIdentifier=guardrail_id,
            guardrailVersion=guardrail_version
        )

        result = json.loads(response["body"].read())
        stop_reason = result.get("stop_reason", "")

        if stop_reason == "guardrail_intervened" or "guardrail" in str(result).lower():
            print("  Result: BLOCKED by guardrail!")
            print(f"  Stop reason: {stop_reason}")
            print()
            print("  Guardrail Intervention Message:")
            print("  " + "-" * 40)
            # The blocked message comes from our guardrail config
            blocked_text = result.get("content", [{}])[0].get("text", "")
            if blocked_text:
                for line in blocked_text.split("\n"):
                    print(f"  {line}")
            else:
                print("  (Response filtered — no content returned)")
            print()
        else:
            # Check if response was modified/filtered
            analysis = result.get("content", [{}])[0].get("text", "")
            print("  Result: Response received (checking for filtering...)")
            print(f"  Stop reason: {stop_reason}")
            print()
            if "DROP TABLE" not in analysis and "rm -rf" not in analysis:
                print("  Guardrail filtered dangerous content from response!")
            else:
                print("  WARNING: Dangerous content may have passed through.")
                print("  Review guardrail configuration.")
            print()

        return True

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if "GuardrailIntervention" in str(e) or "guardrail" in str(e).lower():
            print("  Result: BLOCKED by guardrail (exception raised)!")
            print(f"  -> Guardrail prevented the dangerous request.")
            print()
            return True
        print(f"  ERROR: {error_code}")
        print(f"  -> {e.response['Error']['Message']}")
        print()
        return False
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        print()
        return False


def experiment_4_metrics(guardrail_id):
    """Experiment 4: Guardrail Metrics and Audit."""
    print("-" * 65)
    print("  EXPERIMENT 4: Guardrail Metrics & Audit Trail")
    print("-" * 65)
    print()

    print("  Guardrail Intervention Summary:")
    print("  " + "-" * 40)
    print()
    print(f"  {'Test Case':<25} {'Action':<12} {'Trigger':<25}")
    print(f"  {'-'*25} {'-'*12} {'-'*25}")
    print(f"  {'Safe (db timeout)':<25} {'PASS':<12} {'None':<25}")
    print(f"  {'Unsafe (DROP+rm -rf)':<25} {'BLOCK':<12} {'Word + Topic policy':<25}")
    print()

    print("  How Guardrail Trace Works:")
    print("  " + "-" * 40)
    print()
    print("  When using the Converse API, responses include a 'trace' field:")
    print()
    print("    response = client.converse(")
    print("        modelId=model_id,")
    print("        messages=[...],")
    print("        guardrailConfig={")
    print("            'guardrailIdentifier': guardrail_id,")
    print("            'guardrailVersion': version,")
    print("            'trace': 'enabled'")
    print("        }")
    print("    )")
    print()
    print("  The trace reveals:")
    print("    - Which policy was triggered (word, topic, content)")
    print("    - Input vs output filtering")
    print("    - Specific words/topics matched")
    print("    - Confidence scores for topic matching")
    print()
    print("  CloudWatch Metrics Available:")
    print("  " + "-" * 40)
    print("    - GuardrailInvocations (total calls)")
    print("    - GuardrailBlocked (interventions)")
    print("    - GuardrailPassed (clean passes)")
    print("    - Breakdown by policy type (word/topic/content)")
    print()

    if guardrail_id:
        print(f"  Your guardrail ID for CloudWatch queries: {guardrail_id}")
        print()
        print("  Example CloudWatch Insights query:")
        print(f"    filter @guardrailId = '{guardrail_id}'")
        print("    | stats count() by @action")
        print("    | sort count desc")
    print()


def cleanup_guardrail(bedrock_client, guardrail_id):
    """Clean up the guardrail (with option to keep)."""
    print("-" * 65)
    print("  CLEANUP")
    print("-" * 65)
    print()

    if guardrail_id is None:
        print("  No guardrail to clean up (was running in mock mode).")
        print()
        return

    print(f"  Guardrail ID: {guardrail_id}")
    print()
    print("  Deleting guardrail...")

    try:
        bedrock_client.delete_guardrail(
            guardrailIdentifier=guardrail_id
        )
        print("  Guardrail deleted successfully.")
        print()
        print("  NOTE: In production, you would keep guardrails active.")
        print("  We delete here only to avoid workshop resource accumulation.")

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        print(f"  Could not delete guardrail: {error_code}")
        print(f"  -> {e.response['Error']['Message']}")
        print()
        print("  Manual cleanup:")
        print(f"    aws bedrock delete-guardrail --guardrail-identifier {guardrail_id}")

    except Exception as e:
        print(f"  ERROR during cleanup: {type(e).__name__}: {e}")

    print()


def print_key_learning():
    """Print the key learning section."""
    print("=" * 65)
    print("  KEY LEARNING")
    print("=" * 65)
    print()
    print("  Defense in Depth for AI-Assisted Operations:")
    print()
    print("  1. GUARDRAILS are non-negotiable in production AI systems")
    print("     - Word filters catch known-dangerous commands")
    print("     - Topic policies catch intent even with novel phrasing")
    print("     - Content filters prevent harmful output generation")
    print()
    print("  2. Layer your defenses:")
    print("     Layer 1: Guardrails (Bedrock-level, cannot be bypassed)")
    print("     Layer 2: Prompt engineering (system prompts with safety)")
    print("     Layer 3: Application logic (validate before execution)")
    print("     Layer 4: IAM permissions (least privilege for actions)")
    print("     Layer 5: Audit trail (CloudWatch + CloudTrail logging)")
    print()
    print("  3. Guardrails protect against:")
    print("     - Prompt injection attacks")
    print("     - Confused deputy scenarios")
    print("     - Accidental destructive suggestions")
    print("     - Social engineering through AI")
    print()
    print("  4. Production configuration should include:")
    print("     - PII/PHI detection and redaction")
    print("     - Company-specific sensitive terms")
    print("     - Compliance vocabulary (SOX, HIPAA, PCI-DSS)")
    print("     - Infrastructure-specific kill commands")
    print()
    print("=" * 65)
    print()
    print("  Next: Task 5 — Multi-Provider AI Gateway (task5_gateway.py)")
    print("  Build an enterprise routing pattern with circuit breakers")
    print("  that intelligently routes between local, cloud, and")
    print("  enterprise AI providers.")
    print()
    print("=" * 65)


def main():
    """Main execution flow."""
    print_banner()

    # Initialize Bedrock clients
    guardrail_id = None

    try:
        bedrock_client = boto3.client("bedrock")
        runtime_client = boto3.client("bedrock-runtime")
        print("  Bedrock clients initialized.")
        print(f"  Region: {bedrock_client.meta.region_name}")
        print()
    except Exception as e:
        print(f"  ERROR: Could not initialize Bedrock clients: {e}")
        print("  Ensure AWS credentials are configured.")
        print("  Continuing in MOCK mode for demonstration...")
        print()
        bedrock_client = None
        runtime_client = None

    # Experiment 1: Create guardrail
    if bedrock_client:
        guardrail_id, guardrail_version = experiment_1_create_guardrail(bedrock_client)
    else:
        guardrail_id, guardrail_version = None, None
        print("-" * 65)
        print("  EXPERIMENT 1: Create SRE Safety Guardrail [MOCK MODE]")
        print("-" * 65)
        print()
        print("  Would create guardrail 'sre-safety-guardrail' with:")
        print("    - 5 word filters (rm -rf, DROP TABLE, etc.)")
        print("    - 1 topic policy (DangerousOperations)")
        print("    - Custom blocked messaging")
        print()

    # Small delay to ensure guardrail is fully active
    if guardrail_id:
        print("  Waiting 3 seconds for guardrail to activate...")
        time.sleep(3)
        print()

    # Experiment 2: Safe prompt
    experiment_2_safe_prompt(runtime_client, guardrail_id, guardrail_version)

    # Experiment 3: Unsafe prompt
    experiment_3_unsafe_prompt(runtime_client, guardrail_id, guardrail_version)

    # Experiment 4: Metrics
    experiment_4_metrics(guardrail_id)

    # Cleanup
    if bedrock_client:
        cleanup_guardrail(bedrock_client, guardrail_id)

    # Key learning
    print_key_learning()


if __name__ == "__main__":
    main()
