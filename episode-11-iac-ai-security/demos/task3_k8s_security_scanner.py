#!/usr/bin/env python3
"""
Task 3: Kubernetes Manifest Security Scanner

Uses Claude AI to scan Kubernetes YAML manifests for security issues
including privileged containers, RBAC over-permissions, missing network
policies, and Pod Security Standards violations.

Episode 11 - AI-Assisted DevOps Workshop
Author: Sagar Utekar | CNCF Ambassador | Kubestronaut
"""

import os
import yaml
import anthropic


def print_header():
    print("=" * 65)
    print("   TASK 3: Kubernetes Manifest Security Scanner")
    print("=" * 65)
    print()


K8S_SECURITY_SYSTEM_PROMPT = """You are a Kubernetes security expert performing
manifest security analysis. You have deep knowledge of:

- Kubernetes Pod Security Standards (Privileged, Baseline, Restricted)
- CIS Kubernetes Benchmark v1.8
- RBAC best practices and privilege escalation paths
- Network Policy design patterns
- Container runtime security
- Supply chain security for container images

When scanning Kubernetes manifests, evaluate against these categories:

1. POD SECURITY (CIS 5.2.x):
   - Privileged containers (5.2.1)
   - Host namespace sharing (5.2.2) — hostPID, hostIPC, hostNetwork
   - Capabilities (5.2.3) — especially NET_RAW, SYS_ADMIN, ALL
   - Privilege escalation (5.2.5)
   - Root containers (5.2.6) — runAsNonRoot, runAsUser
   - Seccomp profiles
   - ReadOnlyRootFilesystem

2. RBAC (CIS 5.1.x):
   - Wildcard permissions (5.1.1)
   - cluster-admin binding to pods/service accounts (5.1.2)
   - Default service account usage (5.1.5)
   - Privilege escalation via bind/escalate/impersonate verbs

3. NETWORK SECURITY (CIS 5.3.x):
   - Missing NetworkPolicies (5.3.2)
   - Overly broad ingress/egress rules
   - LoadBalancer services without restrictions

4. RESOURCE MANAGEMENT (CIS 5.4.x):
   - Missing resource limits (5.4.1)
   - Missing resource requests
   - No LimitRange or ResourceQuota

5. SECRETS AND DATA:
   - Secrets in environment variables vs. volume mounts
   - Hardcoded sensitive values
   - Missing encryption at rest

6. SUPPLY CHAIN:
   - Use of :latest tag
   - No image pull policy set
   - Missing image digest pinning
   - Untrusted registries

Format findings as:
[SEVERITY] Title (CIS Reference)
Resource: <kind>/<name>
Evidence: <specific field and value>
Attack Path: <how an attacker exploits this>
Remediation: <YAML fix>
"""


def load_manifest(filepath: str) -> tuple:
    """Load and parse a Kubernetes YAML manifest."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)

    with open(full_path, "r") as f:
        raw_content = f.read()

    # Parse all documents in the YAML file
    documents = list(yaml.safe_load_all(raw_content))
    return raw_content, documents


def scan_manifest(manifest_content: str, parsed_docs: list) -> str:
    """Scan a Kubernetes manifest for security issues."""
    client = anthropic.Anthropic()

    # Build context about what resources are in the manifest
    resource_summary = []
    for doc in parsed_docs:
        if doc:
            kind = doc.get("kind", "Unknown")
            name = doc.get("metadata", {}).get("name", "unnamed")
            resource_summary.append(f"  - {kind}/{name}")

    context = "Resources in this manifest:\n" + "\n".join(resource_summary)

    scan_prompt = f"""Perform a comprehensive security scan of this Kubernetes manifest.

{context}

Evaluate against:
1. Pod Security Standards (Restricted level as target)
2. CIS Kubernetes Benchmark v1.8 Section 5
3. RBAC least-privilege principles
4. Network segmentation requirements
5. Supply chain security
6. Secrets management best practices

For each finding:
- Assign severity (CRITICAL, HIGH, MEDIUM, LOW)
- Reference specific CIS control numbers
- Show the exact field/value that is insecure
- Describe the attack path an adversary would use
- Provide the corrected YAML snippet

After findings, provide:
- Pod Security Standard level this manifest would pass (Privileged/Baseline/Restricted)
- Overall risk score (1-10, where 10 is most risky)
- Top 3 priority fixes

Kubernetes manifest to scan:
```yaml
{manifest_content}
```"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=K8S_SECURITY_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": scan_prompt}
        ]
    )

    return message.content[0].text


def run_experiments():
    """Run Kubernetes security scanning experiments."""

    # Experiment 1: Scan the insecure deployment
    print("Experiment 1: Full Security Scan of Insecure Deployment")
    print("-" * 65)

    try:
        raw_content, parsed_docs = load_manifest(
            "sample-manifests/insecure-deployment.yaml"
        )
        print(f"Loaded manifest with {len(parsed_docs)} documents:")
        for doc in parsed_docs:
            if doc:
                kind = doc.get("kind", "Unknown")
                name = doc.get("metadata", {}).get("name", "unnamed")
                print(f"  - {kind}/{name}")
        print()
        print("Sending to AI for security analysis...")
        print()

        result = scan_manifest(raw_content, parsed_docs)
        print(result)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Ensure sample-manifests/insecure-deployment.yaml exists")
    except anthropic.APIError as e:
        print(f"API Error: {e}")

    print()
    print()

    # Experiment 2: Scan a minimal pod with subtle issues
    print("Experiment 2: Subtle Security Issues in Minimal Deployment")
    print("-" * 65)

    subtle_manifest = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-service
  template:
    metadata:
      labels:
        app: api-service
    spec:
      serviceAccountName: default
      containers:
      - name: api
        image: company/api-service:v2.1.0
        ports:
        - containerPort: 8080
        env:
        - name: DB_CONNECTION_STRING
          value: "postgresql://appuser:Pr0d_P@ss!@db.internal:5432/api"
        - name: REDIS_URL
          value: "redis://redis.internal:6379"
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
        securityContext:
          readOnlyRootFilesystem: false
      - name: sidecar
        image: company/log-agent:latest
        volumeMounts:
        - name: app-logs
          mountPath: /var/log/app
      volumes:
      - name: app-logs
        emptyDir: {}
"""

    try:
        parsed = list(yaml.safe_load_all(subtle_manifest))
        print("Scanning a seemingly reasonable deployment for subtle issues...")
        print()
        result = scan_manifest(subtle_manifest, parsed)
        print(result)
    except anthropic.APIError as e:
        print(f"API Error: {e}")

    print()
    print()

    # Experiment 3: RBAC-focused scan
    print("Experiment 3: RBAC Over-Permission Analysis")
    print("-" * 65)

    rbac_manifest = """apiVersion: v1
kind: ServiceAccount
metadata:
  name: monitoring-sa
  namespace: monitoring
automountServiceAccountToken: true
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-role
rules:
- apiGroups: [""]
  resources: ["pods", "nodes", "services", "endpoints", "secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets", "daemonsets"]
  verbs: ["get", "list", "watch", "update", "patch"]
- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["create"]
- apiGroups: ["rbac.authorization.k8s.io"]
  resources: ["clusterroles", "clusterrolebindings"]
  verbs: ["get", "list", "bind", "escalate"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: monitoring-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: monitoring-role
subjects:
- kind: ServiceAccount
  name: monitoring-sa
  namespace: monitoring
"""

    try:
        parsed = list(yaml.safe_load_all(rbac_manifest))
        print("Scanning RBAC configuration for privilege escalation paths...")
        print()
        result = scan_manifest(rbac_manifest, parsed)
        print(result)
    except anthropic.APIError as e:
        print(f"API Error: {e}")


def main():
    print_header()

    print("This demo scans Kubernetes manifests for security issues including")
    print("Pod Security Standards violations, RBAC over-permissions, missing")
    print("network policies, and supply chain risks.")
    print()

    run_experiments()

    print()
    print("=" * 65)
    print()
    print("Key Learning: Kubernetes security requires defense-in-depth. AI")
    print("scanning understands the relationships between security controls —")
    print("a privileged container with hostPath access is far more dangerous")
    print("than either alone. Mapping findings to attack paths helps developers")
    print("understand WHY each control matters.")
    print()
    print("Next: Run task4_dockerfile_scanner.py to audit Dockerfiles for")
    print("      vulnerabilities and best practice violations.")


if __name__ == "__main__":
    main()
