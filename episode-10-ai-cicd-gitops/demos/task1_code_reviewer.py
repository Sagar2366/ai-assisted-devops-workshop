#!/usr/bin/env python3
"""
Task 1: AI Code Reviewer
========================
AI reviews a git diff for bugs, security issues, and best practices.
Uses a realistic Kubernetes deployment change to demonstrate how AI catches
issues that humans miss under time pressure.

Usage:
    export ANTHROPIC_API_KEY="your-key"
    python3 task1_code_reviewer.py
"""

import anthropic


def main():
    print("=" * 65)
    print("  TASK 1: AI CODE REVIEWER")
    print("  AI reviews diffs for bugs, security issues, best practices")
    print("=" * 65)

    # ─── System Prompt ───────────────────────────────────────────────
    SYSTEM_PROMPT = """You are a senior code reviewer specializing in DevOps and cloud-native applications.

Review the provided diff and identify:
1. **CRITICAL**: Security vulnerabilities, data loss risks, production outage risks
2. **HIGH**: Logic bugs, race conditions, missing error handling
3. **MEDIUM**: Performance issues, code smells, missing tests
4. **LOW**: Style issues, naming conventions, documentation gaps

For each finding, provide:
- **Severity**: CRITICAL/HIGH/MEDIUM/LOW
- **File**: filename and line number
- **Issue**: what's wrong
- **Impact**: what could go wrong in production
- **Fix**: concrete code suggestion

Focus on issues that could cause incidents in production. Skip trivial style nits unless they indicate a pattern."""

    # ─── Realistic Diff: Kubernetes Deployment Change ────────────────
    diff = """diff --git a/k8s/deployment.yaml b/k8s/deployment.yaml
--- a/k8s/deployment.yaml
+++ b/k8s/deployment.yaml
@@ -1,6 +1,6 @@
 apiVersion: apps/v1
 kind: Deployment
 metadata:
-  name: payment-service
+  name: payment-service-v2
   namespace: production
 spec:
-  replicas: 5
+  replicas: 1
   selector:
     matchLabels:
       app: payment-service
@@ -18,15 +18,12 @@
       containers:
         - name: payment-service
-          image: registry.internal/payment-service:1.4.2
+          image: docker.io/randomuser/payment-service:latest
           ports:
             - containerPort: 8080
-          resources:
-            requests:
-              memory: "256Mi"
-              cpu: "250m"
-            limits:
-              memory: "512Mi"
-              cpu: "500m"
+          securityContext:
+            privileged: true
+            runAsUser: 0
           env:
             - name: DB_PASSWORD
-              valueFrom:
-                secretKeyRef:
-                  name: payment-secrets
-                  key: db-password
+              value: "SuperSecret123!"
+            - name: API_KEY
+              value: "sk-prod-abc123xyz789"
           readinessProbe:
             httpGet:
               path: /health
               port: 8080
-            initialDelaySeconds: 5
-            periodSeconds: 10
"""

    print("\n" + "-" * 65)
    print("  INPUT: Kubernetes Deployment Diff")
    print("-" * 65)
    print(diff)

    print("\n" + "-" * 65)
    print("  AI REVIEW IN PROGRESS...")
    print("-" * 65)

    # ─── Call Claude API ─────────────────────────────────────────────
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Review this Kubernetes deployment diff:\n\n```diff\n{diff}\n```"}
        ]
    )

    review = message.content[0].text

    print("\n" + "=" * 65)
    print("  AI REVIEW RESULTS")
    print("=" * 65)
    print(review)

    # ─── Summary ─────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Key Learning:")
    print("  AI code review catches security vulnerabilities, misconfigurations,")
    print("  and operational risks that humans routinely miss under time pressure.")
    print("  The structured prompt ensures consistent severity ratings and")
    print("  actionable fix suggestions.")
    print("-" * 65)
    print("  Next: python3 task2_pipeline_optimizer.py")
    print("-" * 65)


if __name__ == "__main__":
    main()
