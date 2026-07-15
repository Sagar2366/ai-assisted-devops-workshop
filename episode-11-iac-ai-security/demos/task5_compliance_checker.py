#!/usr/bin/env python3
"""
Task 5: CIS Kubernetes Benchmark Compliance Checker

Uses Claude AI to validate Kubernetes manifests against CIS Kubernetes
Benchmark v1.8 controls, producing audit-ready reports with pass/fail
status, evidence, and remediation guidance.

Episode 11 - AI-Assisted DevOps Workshop
Author: Sagar Utekar | CNCF Ambassador | Kubestronaut
"""

import os
import yaml
import anthropic


def print_header():
    print("=" * 65)
    print("   TASK 5: CIS Kubernetes Benchmark Compliance Checker")
    print("=" * 65)
    print()


CIS_COMPLIANCE_PROMPT = """You are a Kubernetes compliance auditor performing a formal
assessment against the CIS Kubernetes Benchmark v1.8. You produce audit-ready reports
that can be presented to compliance teams, auditors, and security leadership.

You evaluate manifests against Section 5 (Policies) of the CIS Benchmark:

5.1 - RBAC and Service Accounts:
  5.1.1: Ensure cluster-admin role is only used where required (Level 1, Scored)
  5.1.2: Minimize access to secrets (Level 1, Scored)
  5.1.3: Minimize wildcard use in Roles/ClusterRoles (Level 1, Scored)
  5.1.5: Ensure default service accounts are not actively used (Level 1, Scored)
  5.1.6: Ensure Service Account Tokens are only mounted where necessary (Level 1, Scored)
  5.1.8: Limit use of the Bind/Escalate/Impersonate verbs (Level 1, Scored)

5.2 - Pod Security Standards:
  5.2.1: Ensure Privileged Pods are minimized (Level 1, Scored)
  5.2.2: Ensure Pods with host namespace sharing are minimized (Level 1, Scored)
  5.2.3: Ensure containers with added capabilities are minimized (Level 1, Scored)
  5.2.4: Ensure readOnlyRootFilesystem is set to true (Level 2, Scored)
  5.2.5: Ensure allowPrivilegeEscalation is set to false (Level 1, Scored)
  5.2.6: Ensure root containers are minimized (Level 2, Scored)
  5.2.7: Ensure NET_RAW capability is not admitted (Level 1, Scored)
  5.2.8: Ensure Seccomp profile is set to RuntimeDefault (Level 2, Scored)

5.3 - Network Policies:
  5.3.1: Ensure CNI supports NetworkPolicies (Level 1, Not Scored)
  5.3.2: Ensure a default deny NetworkPolicy exists (Level 1, Scored)

5.4 - Secrets Management:
  5.4.1: Prefer using secrets as files over secrets as env vars (Level 2, Scored)
  5.4.2: Consider external secret storage (Level 2, Not Scored)

5.7 - General Policies:
  5.7.1: Create administrative boundaries with namespaces (Level 1, Scored)
  5.7.2: Ensure Seccomp profile is set to RuntimeDefault (Level 2, Scored)
  5.7.3: Apply Security Context to pods and containers (Level 2, Scored)
  5.7.4: Ensure default namespace is not used (Level 2, Scored)

For each control, output:
- Control ID and Title
- Level (1 or 2) and Scored status
- Status: PASS / FAIL / N/A (with justification for N/A)
- Evidence: The specific configuration that passes or fails
- Remediation: If FAIL, provide the fix

End with a compliance summary table and overall score.
"""


def load_manifest(filepath: str) -> tuple:
    """Load and parse a Kubernetes YAML manifest."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)

    with open(full_path, "r") as f:
        raw_content = f.read()

    documents = list(yaml.safe_load_all(raw_content))
    return raw_content, documents


def check_compliance(manifest_content: str, parsed_docs: list) -> str:
    """Check manifest compliance against CIS Kubernetes Benchmark."""
    client = anthropic.Anthropic()

    # Identify resources for context
    resources = []
    for doc in parsed_docs:
        if doc:
            kind = doc.get("kind", "Unknown")
            name = doc.get("metadata", {}).get("name", "unnamed")
            namespace = doc.get("metadata", {}).get("namespace", "default")
            resources.append(f"{kind}/{name} (namespace: {namespace})")

    compliance_prompt = f"""Perform a formal CIS Kubernetes Benchmark v1.8 compliance
assessment on this manifest.

Resources being assessed:
{chr(10).join(f'  - {r}' for r in resources)}

For EACH applicable CIS control from Section 5:
1. State the control ID, title, level, and scored status
2. Evaluate: PASS, FAIL, or N/A
3. Provide evidence (the exact field/value or absence thereof)
4. If FAIL: provide specific remediation with YAML

Controls that cannot be evaluated from the manifest alone (e.g., cluster-level
configurations) should be marked N/A with explanation.

After individual controls, provide:

COMPLIANCE SUMMARY:
- Total Controls Assessed: X
- Passed: X
- Failed: X
- Not Applicable: X
- Compliance Score: X% (Passed / (Passed + Failed) * 100)
- Level 1 Score: X% (scored Level 1 controls only)
- Level 2 Score: X% (scored Level 2 controls only)

TOP PRIORITY REMEDIATIONS:
List the top 3 failed controls that should be fixed first, ordered by
security impact.

Manifest to assess:
```yaml
{manifest_content}
```"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=CIS_COMPLIANCE_PROMPT,
        messages=[
            {"role": "user", "content": compliance_prompt}
        ]
    )

    return message.content[0].text


def run_experiments():
    """Run CIS compliance checking experiments."""

    # Experiment 1: Full CIS assessment of insecure deployment
    print("Experiment 1: CIS Benchmark Assessment — Insecure Deployment")
    print("-" * 65)

    try:
        raw_content, parsed_docs = load_manifest(
            "sample-manifests/insecure-deployment.yaml"
        )
        print(f"Target: insecure-deployment.yaml")
        print(f"Documents: {len(parsed_docs)}")
        for doc in parsed_docs:
            if doc:
                kind = doc.get("kind", "Unknown")
                name = doc.get("metadata", {}).get("name", "unnamed")
                print(f"  - {kind}/{name}")
        print()
        print("Running CIS Kubernetes Benchmark v1.8 assessment...")
        print()

        result = check_compliance(raw_content, parsed_docs)
        print(result)

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except anthropic.APIError as e:
        print(f"API Error: {e}")

    print()
    print()

    # Experiment 2: Partially compliant workload
    print("Experiment 2: CIS Assessment — Partially Compliant Workload")
    print("-" * 65)

    partial_manifest = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-frontend
  namespace: production
  labels:
    app: web-frontend
    tier: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-frontend
  template:
    metadata:
      labels:
        app: web-frontend
    spec:
      serviceAccountName: web-frontend-sa
      automountServiceAccountToken: false
      containers:
      - name: nginx
        image: nginx:1.25.3
        ports:
        - containerPort: 80
        securityContext:
          runAsNonRoot: true
          runAsUser: 101
          allowPrivilegeEscalation: false
          capabilities:
            drop: ["ALL"]
            add: ["NET_BIND_SERVICE"]
        resources:
          limits:
            memory: "128Mi"
            cpu: "500m"
          requests:
            memory: "64Mi"
            cpu: "250m"
        readinessProbe:
          httpGet:
            path: /healthz
            port: 80
          initialDelaySeconds: 5
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: web-frontend-sa
  namespace: production
automountServiceAccountToken: false
"""

    try:
        parsed = list(yaml.safe_load_all(partial_manifest))
        print("Assessing a partially hardened deployment...")
        print()
        result = check_compliance(partial_manifest, parsed)
        print(result)
    except anthropic.APIError as e:
        print(f"API Error: {e}")

    print()
    print()

    # Experiment 3: Network Policy compliance check
    print("Experiment 3: Network Policy Compliance Gap Analysis")
    print("-" * 65)

    netpol_manifest = """apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: frontend
    ports:
    - protocol: TCP
      port: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-api
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend-api
      tier: backend
  template:
    metadata:
      labels:
        app: backend-api
        tier: backend
    spec:
      containers:
      - name: api
        image: company/backend:2.3.1
        ports:
        - containerPort: 8080
"""

    try:
        parsed = list(yaml.safe_load_all(netpol_manifest))
        print("Checking NetworkPolicy coverage for CIS 5.3.x compliance...")
        print()
        result = check_compliance(netpol_manifest, parsed)
        print(result)
    except anthropic.APIError as e:
        print(f"API Error: {e}")


def main():
    print_header()

    print("This demo validates Kubernetes manifests against the CIS Kubernetes")
    print("Benchmark v1.8, producing audit-ready compliance reports with")
    print("pass/fail status, evidence, and prioritized remediation guidance.")
    print()

    run_experiments()

    print()
    print("=" * 65)
    print()
    print("Key Learning: CIS benchmarks provide a standardized, auditable")
    print("framework for Kubernetes security. AI maps manifest configurations")
    print("to specific controls, producing evidence-based compliance reports")
    print("that satisfy both technical teams and compliance officers.")
    print()
    print("Next: Run task6_remediation.py to auto-generate secure, fixed")
    print("      versions of all insecure manifests.")


if __name__ == "__main__":
    main()
