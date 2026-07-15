#!/usr/bin/env python3
"""
Task 3: Multi-Model Comparison — Same Alert, Different Brains

Description:
    Send the same SRE alert to Claude, Llama, and Titan on AWS Bedrock
    and compare their responses for incident analysis quality, speed,
    and suitability for different operational scenarios.

Prerequisites:
    - AWS credentials configured (aws configure or environment variables)
    - Claude Sonnet, Llama 3.1, and Titan Text Express enabled in Bedrock console
    - boto3 installed (pip install boto3)
    - Region set to one supporting all three models (e.g., us-east-1)

Usage:
    python task3_multi_model.py
"""

import json
import time
import boto3
from botocore.exceptions import ClientError


def print_banner():
    """Print the task banner."""
    print("=" * 65)
    print("  TASK 3: Multi-Model Comparison")
    print("  Same Alert, Different Brains")
    print("=" * 65)
    print()
    print("  Objective: Send an identical SRE alert to Claude, Llama,")
    print("  and Titan on Bedrock, then compare their incident analysis")
    print("  capabilities across speed, depth, and actionability.")
    print()
    print("=" * 65)
    print()


def get_alert_scenario():
    """Return the SRE alert scenario for multi-model analysis."""
    return (
        "CRITICAL: Production API gateway reporting 503 errors. "
        "Rate: 45% of requests failing. Duration: 8 minutes. "
        "Affected services: payment-service, order-service. "
        "Last deployment: 12 minutes ago (payment-service v2.3.1). "
        "Redis cluster showing 98% memory utilization. "
        "3 of 5 payment-service pods in CrashLoopBackOff with OOMKilled."
    )


def get_sre_prompt(alert):
    """Build the SRE analysis prompt."""
    return (
        f"You are a Senior SRE responding to a production incident. "
        f"Analyze the following alert and provide:\n"
        f"1. Root cause hypothesis\n"
        f"2. Immediate mitigation steps (ordered by priority)\n"
        f"3. Commands to run for diagnosis\n"
        f"4. Rollback decision (yes/no with reasoning)\n\n"
        f"ALERT: {alert}"
    )


def experiment_1_claude(client, alert):
    """Experiment 1: Claude Analysis via Messages API."""
    print("-" * 65)
    print("  EXPERIMENT 1: Claude Sonnet Analysis")
    print("-" * 65)
    print()
    print("  Model: us.anthropic.claude-sonnet-4-20250514-v1:0")
    print("  API Format: Messages API (anthropic_version: bedrock-2023-10-25)")
    print()

    model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    prompt = get_sre_prompt(alert)

    body = json.dumps({
        "anthropic_version": "bedrock-2023-10-25",
        "max_tokens": 1024,
        "temperature": 0.1,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    try:
        print("  Sending alert to Claude...")
        start_time = time.time()

        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body
        )

        elapsed = time.time() - start_time
        result = json.loads(response["body"].read())
        analysis = result["content"][0]["text"]

        print(f"  Response time: {elapsed:.2f}s")
        print()
        print("  Claude's Analysis:")
        print("  " + "-" * 40)
        for line in analysis.split("\n"):
            print(f"  {line}")
        print()

        return {"time": elapsed, "analysis": analysis, "success": True}

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        print(f"  ERROR: {error_code}")
        if "AccessDeniedException" in error_code:
            print("  -> Claude Sonnet may not be enabled in your Bedrock console.")
            print("  -> Go to Bedrock > Model access > Enable Claude models.")
        else:
            print(f"  -> {e.response['Error']['Message']}")
        print()
        return {"time": 0, "analysis": None, "success": False}
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        print()
        return {"time": 0, "analysis": None, "success": False}


def experiment_2_llama(client, alert):
    """Experiment 2: Llama 3.1 Analysis."""
    print("-" * 65)
    print("  EXPERIMENT 2: Llama 3.1 Analysis")
    print("-" * 65)
    print()
    print("  Model: meta.llama3-1-8b-instruct-v1:0")
    print("  API Format: Llama prompt template with special tokens")
    print()

    model_id = "meta.llama3-1-8b-instruct-v1:0"
    prompt_text = get_sre_prompt(alert)

    # Llama 3.1 uses special token format
    formatted_prompt = (
        f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
        f"{prompt_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    )

    body = json.dumps({
        "prompt": formatted_prompt,
        "max_gen_len": 1024,
        "temperature": 0.1
    })

    try:
        print("  Sending alert to Llama 3.1...")
        start_time = time.time()

        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body
        )

        elapsed = time.time() - start_time
        result = json.loads(response["body"].read())
        analysis = result.get("generation", "")

        print(f"  Response time: {elapsed:.2f}s")
        print()
        print("  Llama's Analysis:")
        print("  " + "-" * 40)
        for line in analysis.split("\n"):
            print(f"  {line}")
        print()

        return {"time": elapsed, "analysis": analysis, "success": True}

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        print(f"  ERROR: {error_code}")
        if "AccessDeniedException" in error_code:
            print("  -> Llama 3.1 may not be enabled in your Bedrock console.")
            print("  -> Go to Bedrock > Model access > Enable Meta Llama models.")
        elif "ValidationException" in error_code:
            print("  -> Model may not be available in your region.")
            print("  -> Try us-east-1 or us-west-2.")
        else:
            print(f"  -> {e.response['Error']['Message']}")
        print()
        return {"time": 0, "analysis": None, "success": False}
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        print()
        return {"time": 0, "analysis": None, "success": False}


def experiment_3_titan(client, alert):
    """Experiment 3: Titan Text Express Analysis."""
    print("-" * 65)
    print("  EXPERIMENT 3: Amazon Titan Analysis")
    print("-" * 65)
    print()
    print("  Model: amazon.titan-text-express-v1")
    print("  API Format: inputText with textGenerationConfig")
    print()

    model_id = "amazon.titan-text-express-v1"
    prompt_text = get_sre_prompt(alert)

    body = json.dumps({
        "inputText": prompt_text,
        "textGenerationConfig": {
            "maxTokenCount": 1024,
            "temperature": 0.1
        }
    })

    try:
        print("  Sending alert to Titan...")
        start_time = time.time()

        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body
        )

        elapsed = time.time() - start_time
        result = json.loads(response["body"].read())
        analysis = result.get("results", [{}])[0].get("outputText", "")

        print(f"  Response time: {elapsed:.2f}s")
        print()
        print("  Titan's Analysis:")
        print("  " + "-" * 40)
        for line in analysis.split("\n"):
            print(f"  {line}")
        print()

        return {"time": elapsed, "analysis": analysis, "success": True}

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        print(f"  ERROR: {error_code}")
        if "AccessDeniedException" in error_code:
            print("  -> Titan Text Express may not be enabled in your Bedrock console.")
            print("  -> Go to Bedrock > Model access > Enable Amazon Titan models.")
        else:
            print(f"  -> {e.response['Error']['Message']}")
        print()
        return {"time": 0, "analysis": None, "success": False}
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        print()
        return {"time": 0, "analysis": None, "success": False}


def experiment_4_comparison(results):
    """Experiment 4: Comparison Summary."""
    print("-" * 65)
    print("  EXPERIMENT 4: Comparison Summary")
    print("-" * 65)
    print()

    # Determine ratings based on results
    models = {
        "Claude Sonnet": {
            "result": results.get("claude"),
            "depth": "Deep (structured, actionable)",
            "best_for": "Complex incidents, runbooks"
        },
        "Llama 3.1 8B": {
            "result": results.get("llama"),
            "depth": "Moderate (concise, fast)",
            "best_for": "Quick triage, high volume alerts"
        },
        "Titan Express": {
            "result": results.get("titan"),
            "depth": "Basic (general guidance)",
            "best_for": "Cost-sensitive batch processing"
        }
    }

    # Print comparison table
    print(f"  {'Model':<16} {'Response Time':<15} {'Status':<12} {'Best For'}")
    print(f"  {'-'*16} {'-'*15} {'-'*12} {'-'*30}")

    for name, info in models.items():
        result = info["result"]
        if result and result["success"]:
            time_str = f"{result['time']:.2f}s"
            status = "SUCCESS"
        else:
            time_str = "N/A"
            status = "FAILED"
        print(f"  {name:<16} {time_str:<15} {status:<12} {info['best_for']}")

    print()
    print("  Analysis Depth Comparison:")
    print("  " + "-" * 40)
    for name, info in models.items():
        result = info["result"]
        status = "Available" if (result and result["success"]) else "Not tested"
        print(f"  {name:<16} -> {info['depth']:<35} [{status}]")

    print()
    print("  Recommended Model Selection Strategy:")
    print("  " + "-" * 40)
    print("  - P1/P2 Incidents   -> Claude (deepest analysis, best reasoning)")
    print("  - Alert Triage      -> Llama (fast, cost-effective for volume)")
    print("  - Batch Processing  -> Titan (AWS-native, predictable pricing)")
    print("  - Cost Optimization -> Llama for initial filter, Claude for escalation")
    print("  - Compliance/Audit  -> Bedrock (all models, unified logging)")
    print()

    # Count successes
    success_count = sum(
        1 for r in results.values() if r and r["success"]
    )
    print(f"  Models tested successfully: {success_count}/3")
    if success_count < 3:
        print("  (Enable remaining models in Bedrock console for full comparison)")
    print()


def print_key_learning():
    """Print the key learning section."""
    print("=" * 65)
    print("  KEY LEARNING")
    print("=" * 65)
    print()
    print("  Model Selection Strategy for SRE:")
    print()
    print("  1. No single model wins every scenario — build a portfolio")
    print("  2. Claude excels at complex reasoning and structured responses")
    print("  3. Llama offers speed and cost-efficiency for high-volume triage")
    print("  4. Titan provides AWS-native integration and predictable costs")
    print("  5. Bedrock unifies access — same auth, same logging, same guardrails")
    print()
    print("  Production Pattern: Route by incident severity")
    print("    - P1 (Critical)  -> Claude for deep analysis + runbook generation")
    print("    - P2 (High)      -> Claude or Llama based on complexity")
    print("    - P3 (Medium)    -> Llama for quick categorization")
    print("    - P4 (Low)       -> Titan for batch processing overnight")
    print()
    print("=" * 65)
    print()
    print("  Next: Task 4 — Bedrock Guardrails (task4_guardrails.py)")
    print("  Learn to add safety nets that prevent AI from suggesting")
    print("  dangerous operations in production environments.")
    print()
    print("=" * 65)


def main():
    """Main execution flow."""
    print_banner()

    # Display the alert scenario
    alert = get_alert_scenario()
    print("  ALERT SCENARIO (sent to all models):")
    print("  " + "-" * 40)
    print(f"  {alert}")
    print()
    print("=" * 65)
    print()

    # Initialize Bedrock runtime client
    try:
        client = boto3.client("bedrock-runtime")
        print("  Bedrock runtime client initialized.")
        print(f"  Region: {client.meta.region_name}")
        print()
    except Exception as e:
        print(f"  ERROR: Could not initialize Bedrock client: {e}")
        print("  Ensure AWS credentials are configured:")
        print("    aws configure")
        print("    # or set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION")
        return

    # Run experiments
    results = {}

    results["claude"] = experiment_1_claude(client, alert)
    results["llama"] = experiment_2_llama(client, alert)
    results["titan"] = experiment_3_titan(client, alert)

    # Comparison
    experiment_4_comparison(results)

    # Key learning
    print_key_learning()


if __name__ == "__main__":
    main()
