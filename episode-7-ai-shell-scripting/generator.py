"""
Episode 7: AI-Assisted Shell Scripting & Automation
AI Shell Script Generator

Describe what you want in English -> Get a production-ready bash script.
Uses Claude tool use for structured output.

Author: Sagar Utekar
Prerequisites:
    - Claude API key set as ANTHROPIC_API_KEY environment variable
    - Python anthropic package installed (pip install anthropic)
"""
import anthropic
import json
import os
import stat

client = anthropic.Anthropic()

# Define the generate_script tool
TOOLS = [
    {
        "name": "generate_script",
        "description": "Generate a production-ready bash script from a description. The script must include: shebang, set -euo pipefail, argument parsing with usage function, logging, error handling with traps, and inline comments.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Name for the script file, e.g. check_disk.sh"
                },
                "description": {
                    "type": "string",
                    "description": "One-line description of what the script does"
                },
                "script_content": {
                    "type": "string",
                    "description": "The complete bash script content"
                },
                "usage_examples": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Example commands showing how to run the script"
                }
            },
            "required": ["filename", "description", "script_content", "usage_examples"]
        }
    }
]

SYSTEM_PROMPT = """You are an expert shell script engineer. When asked to create a script, use the generate_script tool.

## Script Standards (non-negotiable):
1. Shebang: #!/usr/bin/env bash
2. Safety: set -euo pipefail
3. Argument parsing: getopts or positional with a usage() function
4. Logging: log() function with timestamps, write to both stdout and log file
5. Error handling: trap for cleanup on EXIT/ERR/INT
6. Variables: ALL_CAPS for constants, lower_case for locals
7. Quoting: Always quote variables ("$var" not $var)
8. Exit codes: 0=success, 1=general error, 2=usage error
9. Comments: explain WHY, not WHAT
10. Portability: use /usr/bin/env, avoid bashisms when possible

## Security:
- Never hardcode credentials
- Use environment variables or config files for secrets
- Validate all user input
- Use mktemp for temporary files"""


def generate_script(description: str, output_dir: str = "generated") -> dict:
    """Generate a bash script from natural language description."""

    messages = [{"role": "user", "content": f"Generate a bash script that: {description}"}]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages
    )

    # Extract tool use result
    for block in response.content:
        if block.type == "tool_use" and block.name == "generate_script":
            result = block.input

            # Save the script
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, result["filename"])
            with open(filepath, "w") as f:
                f.write(result["script_content"])

            # Make executable
            os.chmod(filepath, os.stat(filepath).st_mode | stat.S_IEXEC)

            print(f"Script: {filepath}")
            print(f"Description: {result['description']}")
            print(f"\nUsage examples:")
            for ex in result["usage_examples"]:
                print(f"  {ex}")
            print(f"\n{'='*60}")
            print(result["script_content"])
            print(f"{'='*60}")

            return result

    # Fallback if tool wasn't used
    for block in response.content:
        if hasattr(block, "text"):
            print(block.text)
    return {"error": "Tool was not called"}


if __name__ == "__main__":
    # Demo: Generate a disk usage monitoring script
    print("Generating disk usage monitoring script...\n")
    generate_script(
        "Checks disk usage on all mounted filesystems, "
        "alerts if any filesystem is above a configurable threshold (default 80%), "
        "and sends a Slack notification via webhook URL. "
        "Should accept --threshold, --webhook-url, and --log-file as arguments. "
        "Include a dry-run mode that shows what alerts WOULD fire without sending them."
    )
