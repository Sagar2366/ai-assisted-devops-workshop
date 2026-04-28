#!/usr/bin/env python3
"""
Demo: Same alert, all providers — side-by-side comparison
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Runs the same OOM alert through Google Gemini, Anthropic Claude, OpenAI GPT,
and AWS Bedrock. Skips any provider that is not configured.

Prerequisites:
  pip install google-generativeai anthropic openai boto3
  export GOOGLE_API_KEY="your-key-here"      # Free from aistudio.google.com
  export ANTHROPIC_API_KEY="your-key-here"
  export OPENAI_API_KEY="your-key-here"
  aws configure  (for Bedrock)
"""
import os
import json

alert = """Analyze this alert and give me a 3-step remediation plan:

ALERT: PodCrashLooping
Namespace: production
Pod: api-server-7d4f8b6c5-x2k9m
Restarts: 15 in last 30 minutes
Last Log: "fatal error: runtime: out of memory"
Current Memory Limit: 256Mi
Current Memory Usage: 255Mi (99.6%)"""

system = "You are a senior SRE with 10 years of Kubernetes experience. Be concise and actionable."


def try_google():
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system)
    response = model.generate_content(alert)
    return response.text


def try_anthropic():
    import anthropic
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": alert}]
    )
    return message.content[0].text


def try_openai():
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": alert}
        ]
    )
    return response.choices[0].message.content


def try_bedrock():
    import boto3
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
    response = bedrock.invoke_model(
        modelId="anthropic.claude-sonnet-4-6",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "system": system,
            "messages": [{"role": "user", "content": alert}]
        })
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


all_providers = [
    ("Google Gemini 2.5 Flash (FREE)", try_google),
    ("Anthropic Claude (Direct API)", try_anthropic),
    ("OpenAI GPT-4o", try_openai),
    ("AWS Bedrock (Claude via IAM)", try_bedrock),
]

for name, func in all_providers:
    print("=" * 60)
    print(f"PROVIDER: {name}")
    print("=" * 60)
    try:
        print(func())
    except Exception as e:
        print(f"SKIPPED — {type(e).__name__}: {e}")
    print()
