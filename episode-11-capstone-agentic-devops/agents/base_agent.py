#!/usr/bin/env python3
"""
Episode 11: Capstone — End-to-End Agentic DevOps Platform
Base Agent Class — All SRE agents inherit from this.

Author: Sagar Utekar
Series: AI-Assisted DevOps Workshop

Prerequisites:
    - Python 3.10+
    - anthropic Python SDK (pip install anthropic)
    - ANTHROPIC_API_KEY environment variable set
"""
import anthropic
import json
from tools.unified_tools import toolkit

client = anthropic.Anthropic()


class SREAgent:
    """Base class for all SRE agents."""

    def __init__(self, name: str, system_prompt: str, tools: list, max_steps: int = 10):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self.max_steps = max_steps
        self.tool_handlers = {}

    def register_tool(self, name: str, handler: callable):
        self.tool_handlers[name] = handler

    def run(self, task: str, verbose: bool = True) -> dict:
        messages = [{"role": "user", "content": task}]
        step = 0

        if verbose:
            print(f"\n[{self.name}] Started: {task[:80]}")

        while step < self.max_steps:
            step += 1

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=self.system_prompt,
                tools=self.tools,
                messages=messages
            )

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "text" and block.text and verbose:
                        print(f"  [{self.name}] Think: {block.text[:100]}")
                    if block.type == "tool_use":
                        if verbose:
                            print(f"  [{self.name}] Action: {block.name}")
                        handler = self.tool_handlers.get(block.name)
                        if handler:
                            result = handler(**block.input)
                        else:
                            result = f"No handler for tool: {block.name}"
                        toolkit._log(self.name, block.name, json.dumps(block.input)[:100], str(result)[:200])
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result)
                        })
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
            else:
                conclusion = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        conclusion += block.text
                if verbose:
                    print(f"  [{self.name}] Done in {step} steps")
                return {"agent": self.name, "conclusion": conclusion, "steps": step}

        return {"agent": self.name, "conclusion": "Max steps reached", "steps": step}
