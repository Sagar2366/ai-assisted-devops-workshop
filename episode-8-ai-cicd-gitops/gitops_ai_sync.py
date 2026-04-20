"""
Episode 8: AI-Powered CI/CD & GitOps
Smart GitOps Sync Check -- AI analyzes what ArgoCD is about to sync
and rates the risk before allowing it.

Author: Sagar Utekar
Prerequisites:
    - Claude API key set as ANTHROPIC_API_KEY environment variable
    - Python anthropic package installed (pip install anthropic)
    - argocd CLI installed and configured (optional; uses simulated diff if unavailable)
"""
import anthropic
import subprocess
import json

client = anthropic.Anthropic()

def get_argocd_diff(app_name: str) -> str:
    """Get the diff ArgoCD would apply."""
    result = subprocess.run(
        f"argocd app diff {app_name} 2>/dev/null || echo 'ArgoCD not available - using simulated diff'",
        shell=True, capture_output=True, text=True
    )
    return result.stdout


def assess_sync_risk(app_name: str, diff: str) -> dict:
    """AI assessment of sync risk."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="""You assess Kubernetes deployment risk. Output JSON only:
{
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "score": 1-10,
  "auto_sync_safe": true|false,
  "reasons": ["reason1", "reason2"],
  "recommendations": ["rec1", "rec2"]
}""",
        messages=[{
            "role": "user",
            "content": f"App: {app_name}\n\nDiff to be synced:\n```\n{diff}\n```"
        }]
    )

    try:
        # Strip markdown code blocks if present
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except (json.JSONDecodeError, IndexError):
        return {"risk_level": "UNKNOWN", "auto_sync_safe": False, "reasons": ["Could not parse risk assessment"]}


def smart_sync(app_name: str):
    """Sync with AI risk assessment."""
    print(f"Checking sync risk for: {app_name}")

    diff = get_argocd_diff(app_name)
    assessment = assess_sync_risk(app_name, diff)

    print(f"\nRisk Level: {assessment.get('risk_level', 'UNKNOWN')}")
    print(f"Score: {assessment.get('score', 'N/A')}/10")
    print(f"Auto-sync safe: {assessment.get('auto_sync_safe', False)}")
    print(f"\nReasons:")
    for r in assessment.get("reasons", []):
        print(f"  - {r}")
    print(f"\nRecommendations:")
    for r in assessment.get("recommendations", []):
        print(f"  - {r}")

    if assessment.get("auto_sync_safe"):
        print(f"\n[AUTO-SYNC] Safe to sync automatically.")
        # subprocess.run(f"argocd app sync {app_name}", shell=True)
    else:
        print(f"\n[MANUAL REVIEW REQUIRED] Sync blocked -- needs human approval.")


if __name__ == "__main__":
    smart_sync("my-api")
