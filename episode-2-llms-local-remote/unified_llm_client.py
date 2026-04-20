#!/usr/bin/env python3
"""
Episode 2: Unified LLM Client — One Interface, Three Backends
AI-Assisted DevOps Workshop | Sagar Utekar

Switch between Ollama (local/free), Claude API (cloud), and
Bedrock (enterprise) with a single parameter change. Use this
throughout the workshop.

Prerequisites:
  pip install anthropic requests boto3
  ollama serve & (for local backend)
"""
import os
import json
import requests


class UnifiedLLM:
    """One interface, three backends."""

    def __init__(self, backend: str = "claude"):
        """
        backend: "ollama" | "claude" | "bedrock"
        """
        self.backend = backend

    def ask(self, prompt: str, system: str = "You are a senior SRE.",
            temperature: float = 0.1, max_tokens: int = 1024) -> str:
        if self.backend == "ollama":
            return self._ask_ollama(prompt, system, temperature)
        elif self.backend == "claude":
            return self._ask_claude(prompt, system, temperature, max_tokens)
        elif self.backend == "bedrock":
            return self._ask_bedrock(prompt, system, temperature, max_tokens)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def _ask_ollama(self, prompt, system, temperature):
        resp = requests.post("http://localhost:11434/api/generate", json={
            "model": "qwen2.5-coder:7b",
            "prompt": f"{system}\n\n{prompt}",
            "stream": False,
            "options": {"temperature": temperature}
        })
        return resp.json()["response"]

    def _ask_claude(self, prompt, system, temperature, max_tokens):
        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text

    def _ask_bedrock(self, prompt, system, temperature, max_tokens):
        import boto3
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        resp = bedrock.invoke_model(
            modelId="anthropic.claude-sonnet-4-20250514-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "system": system,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        return json.loads(resp["body"].read())["content"][0]["text"]


# Usage — same code, different backends
if __name__ == "__main__":
    prompt = "Write a one-liner kubectl command to find all pods using more than 500Mi memory"

    for backend in ["ollama", "claude"]:
        print(f"\n--- {backend.upper()} ---")
        try:
            llm = UnifiedLLM(backend=backend)
            print(llm.ask(prompt))
        except Exception as e:
            print(f"Skipped ({e})")
