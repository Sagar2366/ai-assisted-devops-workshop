"""
Episode 9: Infrastructure as Code + AI & Security Scanning
Tool: AI Security Scanner for Kubernetes Manifests

Finds misconfigurations that tools like Trivy/Kubesec miss.
Scans based on CIS Kubernetes Benchmark and NSA/CISA guidelines.

Author: Sagar Utekar
Prerequisites:
    - Anthropic API key (set ANTHROPIC_API_KEY env var)
    - pip install anthropic
    - kubectl configured (for live cluster scanning)
"""
import anthropic
import os
import glob
import json

client = anthropic.Anthropic()

SECURITY_SYSTEM = """You are a Kubernetes security expert. Scan manifests for security issues.

## Check for (based on CIS Kubernetes Benchmark & NSA/CISA guidelines):

### Critical
- Running as root (runAsUser: 0 or missing runAsNonRoot: true)
- Privileged containers
- Host network/PID/IPC namespace
- Writable root filesystem
- No resource limits (DoS risk)
- Secrets in env vars (should use volumes or external secrets)
- :latest tag (unpinnable, unreproducible)

### Warning
- No security context
- Missing network policies
- No pod security standards labels
- Overly permissive RBAC
- No liveness/readiness probes
- Missing PodDisruptionBudget
- No anti-affinity (single point of failure)

### Info
- Missing labels (app, version, team)
- No annotations for monitoring
- Suboptimal resource requests

## Output JSON:
{
  "scan_summary": {
    "total_resources": N,
    "critical": N,
    "warning": N,
    "info": N,
    "passed": N
  },
  "findings": [
    {
      "severity": "CRITICAL|WARNING|INFO",
      "resource": "kind/name",
      "file": "filename",
      "check": "what was checked",
      "issue": "what's wrong",
      "fix": "how to fix with example YAML"
    }
  ],
  "score": "A|B|C|D|F"
}"""


def scan_manifests(path: str) -> dict:
    """Scan K8s manifests in a directory or file."""

    manifests = []

    if os.path.isfile(path):
        files = [path]
    else:
        files = glob.glob(f"{path}/**/*.yaml", recursive=True) + \
                glob.glob(f"{path}/**/*.yml", recursive=True)

    for f in files:
        with open(f) as fh:
            content = fh.read()
            manifests.append({"file": f, "content": content})

    if not manifests:
        return {"error": "No YAML files found"}

    manifest_text = ""
    for m in manifests:
        manifest_text += f"\n### File: {m['file']}\n```yaml\n{m['content']}\n```\n"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": SECURITY_SYSTEM,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{
            "role": "user",
            "content": f"Scan these Kubernetes manifests for security issues:\n{manifest_text}"
        }]
    )

    result_text = response.content[0].text

    # Try to parse JSON from response
    try:
        # Strip markdown code blocks if present
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            json_str = result_text.split("```")[1].split("```")[0]
        else:
            json_str = result_text
        return json.loads(json_str)
    except (json.JSONDecodeError, IndexError):
        return {"raw_response": result_text}


def scan_live_cluster(namespace: str = "default") -> dict:
    """Scan running resources in the cluster."""
    import subprocess

    # Export current state
    result = subprocess.run(
        f"kubectl get deploy,svc,configmap,ingress -n {namespace} -o yaml",
        shell=True, capture_output=True, text=True, timeout=30
    )

    if result.returncode != 0:
        return {"error": result.stderr}

    # Save to temp file and scan
    temp_file = f"/tmp/k8s-scan-{namespace}.yaml"
    with open(temp_file, 'w') as f:
        f.write(result.stdout)

    return scan_manifests(temp_file)


def print_report(scan_result: dict):
    """Pretty print the scan report."""
    if "error" in scan_result:
        print(f"Error: {scan_result['error']}")
        return

    if "raw_response" in scan_result:
        print(scan_result["raw_response"])
        return

    summary = scan_result.get("scan_summary", {})
    findings = scan_result.get("findings", [])
    score = scan_result.get("score", "?")

    print(f"""
╔══════════════════════════════════════════════════╗
║            K8s SECURITY SCAN REPORT              ║
╠══════════════════════════════════════════════════╣
║  Score: {score}                                       ║
║  Resources scanned: {summary.get('total_resources', '?'):<27}║
║  Critical: {summary.get('critical', '?'):<36}║
║  Warning:  {summary.get('warning', '?'):<36}║
║  Info:     {summary.get('info', '?'):<36}║
║  Passed:   {summary.get('passed', '?'):<36}║
╚══════════════════════════════════════════════════╝
""")

    for f in findings:
        severity_icon = {"CRITICAL": "!!!", "WARNING": " ! ", "INFO": " i "}.get(f.get("severity", ""), " ? ")
        print(f"[{severity_icon}] {f.get('severity', 'UNKNOWN')}: {f.get('check', 'Unknown check')}")
        print(f"     Resource: {f.get('resource', 'unknown')}")
        print(f"     Issue: {f.get('issue', 'no details')}")
        print(f"     Fix: {f.get('fix', 'no fix provided')}")
        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(f"Scanning: {path}")
        result = scan_manifests(path)
    else:
        # Scan live cluster
        print("Scanning live cluster (default namespace)...")
        result = scan_live_cluster()

    print_report(result)
