"""
Episode 7: AI-Assisted Shell Scripting & Automation
AI Command-to-Script Converter

Turn one-off commands into reusable, parameterized scripts with error handling.

Author: Sagar Utekar
Prerequisites:
    - Claude API key set as ANTHROPIC_API_KEY environment variable
    - Python anthropic package installed (pip install anthropic)
"""
import anthropic

client = anthropic.Anthropic()

# Example one-off commands that SREs type regularly
ONELINER_EXAMPLES = [
    {
        "name": "Find large log files",
        "command": "find /var/log -name '*.log' -size +100M -exec ls -lh {} \\; | sort -k5 -rh | head -20"
    },
    {
        "name": "Kill zombie processes",
        "command": "ps aux | awk '{if ($8 == \"Z\") print $2}' | xargs -r kill -9"
    },
    {
        "name": "Check SSL cert expiry",
        "command": "echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates"
    }
]


def convert_to_script(command: str, purpose: str) -> str:
    """Convert a one-liner into a production-ready script."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="""You convert ad-hoc shell commands into production-ready scripts.

The script MUST have:
1. #!/usr/bin/env bash and set -euo pipefail
2. Every hardcoded value becomes a parameter with a default
3. A usage() function showing all parameters
4. Input validation for all parameters
5. A log() function with timestamps
6. Error handling with meaningful messages
7. A --dry-run flag that shows what WOULD happen
8. Comments explaining the WHY, not the WHAT

Output the complete script. No explanations outside the script.""",
        messages=[{
            "role": "user",
            "content": f"Convert this one-liner into a production script.\n\nPurpose: {purpose}\nCommand: {command}"
        }]
    )

    return response.content[0].text


if __name__ == "__main__":
    # Demo: Convert the large log finder into a reusable script
    print("Converting one-liner to production script...\n")

    result = convert_to_script(
        command="find /var/log -name '*.log' -size +100M -exec ls -lh {} \\; | sort -k5 -rh | head -20",
        purpose="Find large log files across servers, report sizes, optionally compress or delete old ones"
    )
    print(result)

    print("\n" + "=" * 60)
    print("Converting SSL cert checker...\n")

    result = convert_to_script(
        command="echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates",
        purpose="Check SSL certificate expiry for a list of domains, alert if any expire within N days"
    )
    print(result)
