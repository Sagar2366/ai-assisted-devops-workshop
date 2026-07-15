# Lab 3: AI Kubernetes Manifest Generator

> **Mission:** Use Claude to generate production-ready Kubernetes manifests including Deployment, Service, HPA, and Ingress resources based on the application profile.

## Concept: The Kubernetes Resource Stack

Deploying an application to Kubernetes requires multiple coordinated resources. Each resource serves a specific purpose in making the app accessible and resilient.

**Analogy**: Think of a Kubernetes deployment like opening a restaurant. The Deployment is your kitchen staff (how many cooks, what they need). The Service is the front door (how customers reach you). The Ingress is your street address and signage. The HPA is your manager who hires more staff when it gets busy.

```
┌─────────────────────────────────────────────────────┐
│  Kubernetes Resource Stack                          │
│                                                     │
│  ┌─────────┐     ┌─────────┐     ┌──────────────┐  │
│  │ Ingress │────▶│ Service │────▶│  Deployment  │  │
│  │ (Route) │     │ (LB)    │     │  (Pods)      │  │
│  └─────────┘     └─────────┘     └──────┬───────┘  │
│                                          │          │
│                                   ┌──────▼───────┐  │
│                                   │     HPA      │  │
│                                   │ (Autoscaler) │  │
│                                   └──────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Step 1: Build the K8s Generation Prompt

```python
import json
import anthropic

def build_k8s_prompt(profile, app_name, namespace="default"):
    """Create a prompt for generating Kubernetes manifests."""
    return f"""Generate production-ready Kubernetes manifests for this application.

Application Name: {app_name}
Namespace: {namespace}
Application Profile:
{json.dumps(profile, indent=2)}

Generate the following resources as a single YAML file (separated by ---):

1. **Namespace** (if not 'default')
2. **Deployment** with:
   - 2 replicas minimum
   - Resource requests and limits
   - Liveness and readiness probes
   - Pod anti-affinity for spreading across nodes
   - Proper labels (app, version, managed-by)
   - Environment variables from profile
3. **Service** (ClusterIP type)
4. **HorizontalPodAutoscaler** with:
   - Min 2, Max 10 replicas
   - Target 70% CPU utilization
5. **Ingress** with:
   - Host-based routing
   - TLS placeholder
   - Annotations for nginx ingress controller

Use these conventions:
- Image: {app_name}:latest
- Label selector: app={app_name}
- All resources in the same namespace

Return ONLY the YAML content, no explanation.
"""
```

## Step 2: Generate the Manifests

```python
def generate_k8s_manifests(profile, app_name, namespace="default"):
    """Use Claude to generate Kubernetes manifests."""
    client = anthropic.Anthropic()
    prompt = build_k8s_prompt(profile, app_name, namespace)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    manifests = message.content[0].text
    # Strip markdown code fences if present
    if manifests.startswith("```"):
        lines = manifests.split('\n')
        manifests = '\n'.join(lines[1:-1])
    
    return manifests
```

## Step 3: Example Output

For a Flask application named `my-flask-app`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-flask-app
  namespace: production
  labels:
    app: my-flask-app
    version: "1.0.0"
    managed-by: ai-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-flask-app
  template:
    metadata:
      labels:
        app: my-flask-app
        version: "1.0.0"
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - my-flask-app
                topologyKey: kubernetes.io/hostname
      containers:
        - name: my-flask-app
          image: my-flask-app:latest
          ports:
            - containerPort: 5000
              protocol: TCP
          env:
            - name: FLASK_ENV
              value: "production"
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: my-flask-app-secrets
                  key: redis-url
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: my-flask-app
  namespace: production
  labels:
    app: my-flask-app
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 5000
      protocol: TCP
  selector:
    app: my-flask-app
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-flask-app
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-flask-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-flask-app
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - my-flask-app.example.com
      secretName: my-flask-app-tls
  rules:
    - host: my-flask-app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-flask-app
                port:
                  number: 80
```

## Step 4: Validate with kubectl

```python
import subprocess
import tempfile

def validate_manifests(yaml_content):
    """Validate generated manifests using kubectl dry-run."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        f.flush()
        
        result = subprocess.run(
            ["kubectl", "apply", "--dry-run=client", "-f", f.name],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("Validation passed!")
            print(result.stdout)
        else:
            print("Validation failed:")
            print(result.stderr)
        
        return result.returncode == 0
```

## Running the Demo Script

```bash
cd demos
python task3_k8s_generator.py
```

## What Success Looks Like

- [x] Claude generates a complete set of K8s resources (Deployment, Service, HPA, Ingress)
- [x] Resource requests and limits are appropriate for the application type
- [x] Liveness and readiness probes use the correct health endpoint
- [x] Pod anti-affinity is configured for high availability
- [x] HPA scales between 2-10 replicas based on CPU
- [x] Ingress includes TLS and proper annotations
- [x] Manifests pass `kubectl apply --dry-run=client` validation

## Key Takeaway

> AI-generated Kubernetes manifests encode production best practices — resource limits, health probes, autoscaling, and anti-affinity — that are often forgotten in manually-written YAML. The deployment profile ensures every manifest is tailored to the specific application rather than being generic boilerplate.

**Next:** Lab 4 — Docker Compose Generator
