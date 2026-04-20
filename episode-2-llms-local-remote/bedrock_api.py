#!/usr/bin/env python3
"""
Episode 2: AWS Bedrock with Claude — Enterprise Multi-Model
AI-Assisted DevOps Workshop | Sagar Utekar

Uses IAM auth (no API keys), compliance logging, and audit trails.

Prerequisites:
  aws configure (Access Key, Secret Key, Region: us-east-1)
  pip install boto3
"""
import boto3
import json

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

def ask_bedrock(prompt: str, model_id: str = "anthropic.claude-sonnet-4-20250514-v1:0") -> str:
    """Query Claude via AWS Bedrock — uses IAM auth, no API keys."""
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "system": "You are an AWS-certified SRE. Focus on AWS-native solutions.",
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]

# Test it
if __name__ == "__main__":
    print(ask_bedrock("""
Our EKS cluster in us-east-1 has 3 node groups:
- general: m5.xlarge x 5 (CPU: 40%, Memory: 65%)
- memory-optimized: r5.2xlarge x 3 (CPU: 15%, Memory: 30%)
- gpu: g4dn.xlarge x 2 (GPU: 5%, Memory: 10%)

Suggest cost optimizations with estimated monthly savings.
"""))
