#!/usr/bin/env python3
"""
Task 4: ArgoCD AI Risk Gate
============================
Risk-scores ArgoCD deployment manifests by analyzing replicas, images,
resources, and namespaces. Uses Claude for nuanced risk analysis beyond
what static checks can catch.

Usage:
    export ANTHROPIC_API_KEY="your-key"
    python3 task4_argocd_risk_gate.py
"""

import anthropic
import json
import re


def get_container_image(manifest):
    """Extract the first container image from a manifest."""
    containers = (
        manifest.get("spec", {})
        .get("template", {})
        .get("spec", {})
        .get("containers", [])
    )
    if containers:
        return containers[0].get("image", "unknown:latest")
    return "unknown:latest"


def get_registry(image):
    """Extract registry from an image string."""
    if "/" in image and ("." in image.split("/")[0] or ":" in image.split("/")[0]):
        return image.split("/")[0]
    return "docker.io"


def get_major_version(image):
    """Extract major version from image tag."""
    tag = image.split(":")[-1] if ":" in image else "latest"
    match = re.match(r"(\d+)", tag)
    return match.group(1) if match else tag


def get_resource_limits(manifest):
    """Extract resource limits from first container."""
    containers = (
        manifest.get("spec", {})
        .get("template", {})
        .get("spec", {})
        .get("containers", [])
    )
    if containers:
        return containers[0].get("resources", {}).get("limits")
    return None


def score_manifest_changes(old_manifest, new_manifest):
    """Score changes between two K8s manifests."""
    risk_score = 0
    findings = []

    # ─── Replica Changes ─────────────────────────────────────────────
    old_replicas = old_manifest.get("spec", {}).get("replicas", 1)
    new_replicas = new_manifest.get("spec", {}).get("replicas", 1)

    if new_replicas < old_replicas:
        risk_score += 5
        findings.append(f"SCALE DOWN: {old_replicas} -> {new_replicas} replicas")
    elif new_replicas > old_replicas * 3:
        risk_score += 4
        findings.append(f"LARGE SCALE UP: {old_replicas} -> {new_replicas} replicas")
    elif new_replicas != old_replicas:
        risk_score += 1
        findings.append(f"Replica change: {old_replicas} -> {new_replicas}")

    # ─── Image Changes ───────────────────────────────────────────────
    old_image = get_container_image(old_manifest)
    new_image = get_container_image(new_manifest)

    if old_image != new_image:
        if get_registry(old_image) != get_registry(new_image):
            risk_score += 6
            findings.append(f"REGISTRY CHANGE: {old_image} -> {new_image}")
        elif get_major_version(old_image) != get_major_version(new_image):
            risk_score += 4
            findings.append(f"MAJOR VERSION BUMP: {old_image} -> {new_image}")
        elif "latest" in new_image:
            risk_score += 3
            findings.append(f"USING :latest TAG: {new_image}")
        else:
            risk_score += 1
            findings.append(f"Image update: {old_image} -> {new_image}")

    # ─── Resource Limit Changes ──────────────────────────────────────
    old_limits = get_resource_limits(old_manifest)
    new_limits = get_resource_limits(new_manifest)

    if old_limits and not new_limits:
        risk_score += 7
        findings.append("RESOURCE LIMITS REMOVED — unbounded resource usage possible")
    elif old_limits and new_limits:
        # Check if limits decreased significantly
        old_mem = old_limits.get("memory", "0Mi")
        new_mem = new_limits.get("memory", "0Mi")
        if old_mem != new_mem:
            risk_score += 1
            findings.append(f"Memory limit changed: {old_mem} -> {new_mem}")

    # ─── Namespace Risk ──────────────────────────────────────────────
    new_ns = new_manifest.get("metadata", {}).get("namespace", "default")
    if new_ns in ("production", "prod", "kube-system"):
        risk_score += 3
        findings.append(f"Deploying to sensitive namespace: {new_ns}")

    # ─── Privileged Container ────────────────────────────────────────
    containers = (
        new_manifest.get("spec", {})
        .get("template", {})
        .get("spec", {})
        .get("containers", [])
    )
    for container in containers:
        security_context = container.get("securityContext", {})
        if security_context.get("privileged", False):
            risk_score += 8
            findings.append("PRIVILEGED CONTAINER — full host access granted")
        if security_context.get("runAsUser") == 0:
            risk_score += 4
            findings.append("RUNNING AS ROOT — container runs as uid 0")

    return risk_score, findings


def ai_risk_assessment(old_manifest, new_manifest, static_score, findings):
    """Use Claude for nuanced risk analysis beyond static checks."""
    client = anthropic.Anthropic()

    manifest_summary = json.dumps({
        "old": old_manifest,
        "new": new_manifest
    }, indent=2)

    findings_text = "\n".join(f"- {f}" for f in findings)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system="""You are an SRE risk assessor for Kubernetes deployments.
Given a manifest change, static risk score, and findings:
1. Assess whether the static score is appropriate (over/under)
2. Identify risks the static analysis might have missed
3. Consider blast radius, rollback difficulty, and cascading failures
4. Recommend: APPROVE, REQUIRE_REVIEW, or BLOCK
5. If blocking, explain what must change before deployment is safe

Be concise and decisive. Format as:
RECOMMENDATION: [APPROVE|REQUIRE_REVIEW|BLOCK]
ADJUSTED SCORE: X/10
REASONING: (2-3 sentences)
ADDITIONAL RISKS: (if any)
REQUIRED ACTIONS: (if blocking)""",
        messages=[
            {"role": "user", "content": f"""Manifest changes:
{manifest_summary}

Static risk score: {static_score}/10
Static findings:
{findings_text}

Provide your risk assessment."""}
        ]
    )
    return message.content[0].text


def gate_decision(risk_score, threshold=7):
    """Make the gate decision based on score."""
    if risk_score >= threshold:
        return "BLOCKED"
    elif risk_score >= 4:
        return "REQUIRES_REVIEW"
    else:
        return "APPROVED"


def main():
    print("=" * 65)
    print("  TASK 4: ARGOCD AI RISK GATE")
    print("  Risk-score deployments before ArgoCD syncs to production")
    print("=" * 65)

    # ─── Simulated ArgoCD Manifests (before and after) ───────────────
    old_manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "payment-service",
            "namespace": "production"
        },
        "spec": {
            "replicas": 5,
            "template": {
                "spec": {
                    "containers": [{
                        "name": "payment-service",
                        "image": "registry.internal/payment-service:1.4.2",
                        "resources": {
                            "requests": {"memory": "256Mi", "cpu": "250m"},
                            "limits": {"memory": "512Mi", "cpu": "500m"}
                        },
                        "securityContext": {
                            "runAsNonRoot": True,
                            "readOnlyRootFilesystem": True
                        }
                    }]
                }
            }
        }
    }

    new_manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "payment-service",
            "namespace": "production"
        },
        "spec": {
            "replicas": 2,
            "template": {
                "spec": {
                    "containers": [{
                        "name": "payment-service",
                        "image": "docker.io/thirdparty/payment-service:2.0.0",
                        "securityContext": {
                            "privileged": True,
                            "runAsUser": 0
                        }
                    }]
                }
            }
        }
    }

    print("\n" + "-" * 65)
    print("  CURRENT DEPLOYMENT (running in production)")
    print("-" * 65)
    print(f"  Image:    {get_container_image(old_manifest)}")
    print(f"  Replicas: {old_manifest['spec']['replicas']}")
    print(f"  Limits:   {get_resource_limits(old_manifest)}")
    print(f"  NS:       {old_manifest['metadata']['namespace']}")

    print("\n" + "-" * 65)
    print("  PROPOSED CHANGE (pending ArgoCD sync)")
    print("-" * 65)
    print(f"  Image:    {get_container_image(new_manifest)}")
    print(f"  Replicas: {new_manifest['spec']['replicas']}")
    print(f"  Limits:   {get_resource_limits(new_manifest)}")
    print(f"  NS:       {new_manifest['metadata']['namespace']}")

    # ─── Static Risk Scoring ─────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  STATIC RISK ANALYSIS")
    print("-" * 65)

    risk_score, findings = score_manifest_changes(old_manifest, new_manifest)

    for finding in findings:
        severity = "!!!" if any(w in finding for w in ["SCALE DOWN", "REGISTRY", "PRIVILEGED", "REMOVED", "ROOT"]) else " > "
        print(f"  {severity} {finding}")

    print(f"\n  Static Risk Score: {risk_score}/10")
    print(f"  Gate Decision: {gate_decision(risk_score)}")

    # ─── AI Risk Assessment ──────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  AI RISK ASSESSMENT (nuanced analysis)")
    print("-" * 65)

    ai_assessment = ai_risk_assessment(old_manifest, new_manifest, risk_score, findings)
    print(f"\n{ai_assessment}")

    # ─── Final Decision ──────────────────────────────────────────────
    decision = gate_decision(risk_score)
    print("\n" + "=" * 65)
    print(f"  FINAL DECISION: {decision}")
    if decision == "BLOCKED":
        print("  ArgoCD sync will be PREVENTED (PreSync hook exits non-zero)")
    elif decision == "REQUIRES_REVIEW":
        print("  ArgoCD sync allowed but team notified for review")
    else:
        print("  ArgoCD sync proceeds normally")
    print("=" * 65)

    # ─── Summary ─────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Key Learning:")
    print("  Static scoring catches obvious risks (scale-downs, removed limits).")
    print("  AI adds nuance: understanding context, blast radius, and whether")
    print("  a risky change might be intentional vs. accidental. The combination")
    print("  creates a gate that is both reliable and intelligent.")
    print("-" * 65)
    print("  Next: python3 task5_commit_analyzer.py")
    print("-" * 65)


if __name__ == "__main__":
    main()
