#!/usr/bin/env python3
"""
Task 6: Full AI-Powered CI/CD Pipeline
========================================
Orchestrates the complete pipeline: diff review, risk scoring, deploy decision,
and release notes generation. Demonstrates end-to-end AI gates in CI/CD.

Usage:
    export ANTHROPIC_API_KEY="your-key"
    python3 task6_full_pipeline.py
"""

import anthropic
import json
import re
import time


class AIPipeline:
    """Orchestrates AI-powered CI/CD pipeline stages."""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.stages = []
        self.blocked = False
        self.audit_trail = []

    def run_stage(self, name, func):
        """Run a pipeline stage with timing and logging."""
        print(f"\n{'=' * 65}")
        print(f"  STAGE: {name}")
        print(f"{'=' * 65}")

        start = time.time()
        result = func()
        elapsed = time.time() - start

        status = result.get("status", "UNKNOWN")
        self.stages.append({"name": name, "result": result, "time": elapsed})
        self.audit_trail.append(f"[{name}] {status} ({elapsed:.1f}s)")

        status_icon = {"PASS": "[OK]", "BLOCKED": "[XX]", "SKIP": "[--]"}.get(status, "[??]")
        print(f"\n  Result: {status_icon} {status}")

        if status == "BLOCKED":
            self.blocked = True
            print(f"  >>> PIPELINE BLOCKED at stage: {name}")

        return result

    def print_summary(self):
        """Print final pipeline summary."""
        print("\n" + "=" * 65)
        print("  PIPELINE SUMMARY")
        print("=" * 65)
        final = "BLOCKED" if self.blocked else "DEPLOYED"
        print(f"\n  Final Result: {final}")
        print(f"\n  Audit Trail:")
        for entry in self.audit_trail:
            print(f"    {entry}")
        total_time = sum(s["time"] for s in self.stages)
        print(f"\n  Total pipeline time: {total_time:.1f}s")
        print("=" * 65)


def main():
    print("=" * 65)
    print("  TASK 6: FULL AI-POWERED CI/CD PIPELINE")
    print("  End-to-end: commit -> review -> test -> risk-gate -> deploy")
    print("=" * 65)

    pipeline = AIPipeline()

    # ─── Test Data ───────────────────────────────────────────────────
    code_diff = """diff --git a/api/handlers/payment.go b/api/handlers/payment.go
--- a/api/handlers/payment.go
+++ b/api/handlers/payment.go
@@ -42,8 +42,14 @@ func ProcessPayment(w http.ResponseWriter, r *http.Request) {
     amount := r.FormValue("amount")
-    // Process payment
-    result, err := paymentGateway.Charge(userID, amount)
+    // Add retry logic for payment processing
+    var result *PaymentResult
+    var err error
+    for i := 0; i < 3; i++ {
+        result, err = paymentGateway.Charge(userID, amount)
+        if err == nil {
+            break
+        }
+        time.Sleep(time.Second * time.Duration(i+1))
+    }
     if err != nil {
-        http.Error(w, "Payment failed", 500)
+        log.Printf("Payment failed after retries: %v", err)
+        http.Error(w, "Payment processing error", 503)
         return
     }
"""

    deployment_manifest = {
        "old": {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "payment-api", "namespace": "production"},
            "spec": {
                "replicas": 3,
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "payment-api",
                            "image": "registry.internal/payment-api:1.8.3",
                            "resources": {
                                "limits": {"memory": "512Mi", "cpu": "500m"}
                            }
                        }]
                    }
                }
            }
        },
        "new": {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "payment-api", "namespace": "production"},
            "spec": {
                "replicas": 3,
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "payment-api",
                            "image": "registry.internal/payment-api:1.9.0",
                            "resources": {
                                "limits": {"memory": "512Mi", "cpu": "500m"}
                            }
                        }]
                    }
                }
            }
        }
    }

    commit_log = """f8a1b2c3|Alice Chen|Add retry logic for payment processing|2024-03-15
a4b5c6d7|Alice Chen|Fix error message for failed payments|2024-03-15
b8c9d0e1|Bob Kumar|Update payment gateway SDK to 1.9.0|2024-03-14"""

    # ─── Stage 1: AI Code Review ─────────────────────────────────────
    def stage_code_review():
        print("  Sending diff to Claude for code review...")
        message = pipeline.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system="""You are a senior code reviewer. Review this diff and respond with:
1. A brief assessment (1-2 sentences)
2. Any CRITICAL issues (must fix before merge)
3. Any suggestions (nice to have)

End with a verdict: PASS (safe to merge) or FAIL (has critical issues).
Be concise.""",
            messages=[
                {"role": "user", "content": f"Review this diff:\n\n```diff\n{code_diff}\n```"}
            ]
        )
        review = message.content[0].text
        print(f"\n{review}")

        # Determine pass/fail from response
        status = "PASS" if "PASS" in review.upper() or "FAIL" not in review.upper() else "BLOCKED"
        return {"status": status, "review": review}

    pipeline.run_stage("Code Review", stage_code_review)

    # ─── Stage 2: CI Tests (Simulated) ──────────────────────────────
    if not pipeline.blocked:
        def stage_tests():
            print("  Running test suite...")
            print("    Unit tests:        87 passed, 0 failed")
            print("    Integration tests: 23 passed, 0 failed")
            print("    Payment tests:     12 passed, 0 failed")
            print("    Total: 122 passed")
            return {"status": "PASS", "tests_passed": 122, "tests_failed": 0}

        pipeline.run_stage("CI Tests", stage_tests)

    # ─── Stage 3: AI Risk Gate ───────────────────────────────────────
    if not pipeline.blocked:
        def stage_risk_gate():
            old = deployment_manifest["old"]
            new = deployment_manifest["new"]
            risk_score = 0
            findings = []

            # Check replicas
            old_replicas = old["spec"]["replicas"]
            new_replicas = new["spec"]["replicas"]
            if new_replicas < old_replicas:
                risk_score += 5
                findings.append(f"Scale down: {old_replicas} -> {new_replicas}")

            # Check image
            old_image = old["spec"]["template"]["spec"]["containers"][0]["image"]
            new_image = new["spec"]["template"]["spec"]["containers"][0]["image"]
            if old_image != new_image:
                old_tag = old_image.split(":")[-1]
                new_tag = new_image.split(":")[-1]
                # Check if major version changed
                old_major = old_tag.split(".")[0]
                new_major = new_tag.split(".")[0]
                if old_major != new_major:
                    risk_score += 4
                    findings.append(f"Major version bump: {old_image} -> {new_image}")
                else:
                    risk_score += 1
                    findings.append(f"Image update: {old_image} -> {new_image}")

            # Check namespace
            ns = new["metadata"].get("namespace", "default")
            if ns in ("production", "prod"):
                risk_score += 2
                findings.append(f"Target namespace: {ns}")

            # Check resource limits
            old_limits = old["spec"]["template"]["spec"]["containers"][0].get("resources", {}).get("limits")
            new_limits = new["spec"]["template"]["spec"]["containers"][0].get("resources", {}).get("limits")
            if old_limits and not new_limits:
                risk_score += 7
                findings.append("Resource limits REMOVED")

            print(f"  Static risk score: {risk_score}/10")
            for f in findings:
                print(f"    - {f}")

            # AI assessment
            print("\n  Requesting AI risk assessment...")
            message = pipeline.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system="You are an SRE assessing deployment risk. Given the score and findings, provide a 2-sentence assessment and recommend APPROVE or BLOCK.",
                messages=[
                    {"role": "user", "content": f"Risk score: {risk_score}/10\nFindings: {json.dumps(findings)}\nManifest change: image {old_image} -> {new_image}, replicas unchanged at {new_replicas}"}
                ]
            )
            ai_review = message.content[0].text
            print(f"\n  AI Assessment: {ai_review}")

            threshold = 7
            if risk_score >= threshold:
                return {"status": "BLOCKED", "score": risk_score, "findings": findings}
            return {"status": "PASS", "score": risk_score, "findings": findings}

        pipeline.run_stage("Risk Gate", stage_risk_gate)

    # ─── Stage 4: Deploy (Simulated) ────────────────────────────────
    if not pipeline.blocked:
        def stage_deploy():
            new_image = deployment_manifest["new"]["spec"]["template"]["spec"]["containers"][0]["image"]
            ns = deployment_manifest["new"]["metadata"]["namespace"]
            print(f"  Deploying {new_image} to {ns}...")
            print("  ArgoCD sync initiated")
            print("  Rollout status: 3/3 pods ready")
            print("  Health check: PASSED")
            return {"status": "PASS", "image": new_image, "namespace": ns}

        pipeline.run_stage("Deploy", stage_deploy)

    # ─── Stage 5: Release Notes ──────────────────────────────────────
    if not pipeline.blocked:
        def stage_release_notes():
            print("  Generating release notes from commits...")
            message = pipeline.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system="Generate brief release notes (5 lines max) from these commits. Format: version header, then bullet points.",
                messages=[
                    {"role": "user", "content": f"Generate release notes for v1.9.0:\n\n{commit_log}"}
                ]
            )
            notes = message.content[0].text
            print(f"\n{notes}")
            return {"status": "PASS", "notes": notes}

        pipeline.run_stage("Release Notes", stage_release_notes)

    # ─── Final Summary ───────────────────────────────────────────────
    pipeline.print_summary()

    # ─── Key Learning ────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Key Learning:")
    print("  The full pipeline is more than the sum of its parts. Each AI gate")
    print("  catches different risk classes: code review finds bugs, risk gate")
    print("  catches deployment dangers, release notes ensure documentation.")
    print("  The audit trail gives full traceability for post-mortems.")
    print("-" * 65)
    print("  Next: Explore the github-action.yml for production deployment")
    print("-" * 65)


if __name__ == "__main__":
    main()
