#!/usr/bin/env python3
"""
Environment Verification Script
Confirms your AI Foundations lab environment is properly configured.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar
"""

import os
import sys
import subprocess


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"  [OK] Python {version.major}.{version.minor}.{version.micro}")
    return version.major >= 3 and version.minor >= 9


def check_package(name):
    """Check if a Python package is installed"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", name],
            capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if line.startswith("Version:"):
                    version = line.split(":")[1].strip()
                    print(f"  [OK] {name} installed (version {version})")
                    return True
        print(f"  [MISSING] {name} not installed — run: pip install {name}")
        return False
    except Exception as e:
        print(f"  [ERROR] Could not check {name}: {e}")
        return False


def check_api_key(name, env_var):
    """Check if an API key is set"""
    key = os.getenv(env_var)
    if key:
        print(f"  [OK] {env_var} is set ({len(key)} chars)")
        return True
    else:
        print(f"  [SKIP] {env_var} not set — {name} demos will be skipped")
        return False


def test_anthropic():
    """Test Anthropic API connection"""
    try:
        import anthropic
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say OK"}]
        )
        print(f"  [OK] Anthropic API works")
        return True
    except Exception as e:
        print(f"  [FAIL] Anthropic API: {e}")
        return False


def test_openai():
    """Test OpenAI API connection"""
    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say OK"}]
        )
        print(f"  [OK] OpenAI API works")
        return True
    except Exception as e:
        print(f"  [FAIL] OpenAI API: {e}")
        return False


def test_bedrock():
    """Test AWS Bedrock connection"""
    try:
        import boto3
        import json
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        response = bedrock.invoke_model(
            modelId="anthropic.claude-sonnet-4-6",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Say OK"}]
            })
        )
        print(f"  [OK] AWS Bedrock works")
        return True
    except Exception as e:
        print(f"  [FAIL] AWS Bedrock: {e}")
        return False


def test_google():
    """Test Google Gemini API connection"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say OK")
        print(f"  [OK] Google Gemini API works")
        return True
    except Exception as e:
        print(f"  [FAIL] Google Gemini API: {e}")
        return False


def main():
    print("=" * 60)
    print("AI Foundations Lab — Environment Verification")
    print("AI-Assisted DevOps Workshop | Episode 1")
    print("=" * 60)

    # Python version
    print("\nPython Version:")
    check_python_version()

    # Required packages
    print("\nRequired Packages:")
    check_package("anthropic")

    print("\nOptional Packages (for multi-provider labs):")
    check_package("openai")
    check_package("boto3")
    check_package("google-generativeai")

    # API keys
    print("\nAPI Keys:")
    has_anthropic = check_api_key("Anthropic", "ANTHROPIC_API_KEY")
    has_openai = check_api_key("OpenAI", "OPENAI_API_KEY")
    has_google = check_api_key("Google Gemini", "GOOGLE_API_KEY")

    print("\nAWS Credentials:")
    has_aws = bool(os.getenv("AWS_ACCESS_KEY_ID"))
    if has_aws:
        print(f"  [OK] AWS credentials configured")
    else:
        print(f"  [SKIP] AWS not configured — Bedrock labs will be skipped")

    # Live API tests
    print("\nAPI Connection Tests:")
    providers = 0

    if has_anthropic:
        if test_anthropic():
            providers += 1
    else:
        print("  [SKIP] Anthropic — no API key")

    if has_openai:
        if test_openai():
            providers += 1
    else:
        print("  [SKIP] OpenAI — no API key")

    if has_google:
        if test_google():
            providers += 1
    else:
        print("  [SKIP] Google Gemini — no API key (free at aistudio.google.com)")

    if has_aws:
        if test_bedrock():
            providers += 1
    else:
        print("  [SKIP] Bedrock — no AWS credentials")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    if providers == 0:
        print("\n  [ERROR] No providers working!")
        print("  You need at least one API key to run the labs.")
        print("\n  Quick start (free):")
        print('    export GOOGLE_API_KEY="your-key-here"')
        print("    Get one free at: aistudio.google.com")
        print("\n  Or use Anthropic:")
        print('    export ANTHROPIC_API_KEY="your-key-here"')
        print("    Get one at: console.anthropic.com")
        sys.exit(1)
    else:
        print(f"\n  [OK] {providers} provider(s) working")
        print("\n  Start here:")
        if has_google:
            print("    python3 demos/google/task1_first_api_call.py   (free!)")
        if has_anthropic:
            print("    python3 demos/anthropic/task1_first_api_call.py")
        if has_openai:
            print("    python3 demos/openai/task1_first_api_call.py")
        if has_aws:
            print("    python3 demos/bedrock/task1_first_api_call.py")

    print("=" * 60)


if __name__ == "__main__":
    main()
