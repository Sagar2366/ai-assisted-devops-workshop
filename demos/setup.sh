#!/bin/bash
# ============================================================
# Agentic AI for DevOps Workshop — Setup Script
# Run this BEFORE the workshop to prepare your environment.
# ============================================================

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Agentic AI for DevOps — Workshop Setup              ║"
echo "║     by Sagar Utekar | CNCF Ambassador                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check() {
    if command -v "$1" &> /dev/null; then
        echo -e "  ${GREEN}[OK]${NC} $1 $(command -v "$1")"
        return 0
    else
        echo -e "  ${RED}[MISSING]${NC} $1 — $2"
        return 1
    fi
}

echo "=== Checking Prerequisites ==="
echo ""

MISSING=0

echo "Core Tools:"
check "docker" "Install: brew install --cask docker" || MISSING=$((MISSING+1))
check "kubectl" "Install: brew install kubectl" || MISSING=$((MISSING+1))
check "kind" "Install: brew install kind" || MISSING=$((MISSING+1))
check "helm" "Install: brew install helm" || MISSING=$((MISSING+1))
check "python3" "Install: brew install python3" || MISSING=$((MISSING+1))
check "pip3" "Comes with python3" || MISSING=$((MISSING+1))
check "node" "Install: brew install node" || MISSING=$((MISSING+1))
check "npm" "Comes with node" || MISSING=$((MISSING+1))

echo ""
echo "AI Tools:"
check "ollama" "Install: brew install ollama" || MISSING=$((MISSING+1))
check "claude" "Install: npm install -g @anthropic-ai/claude-code" || echo -e "  ${YELLOW}[OPTIONAL]${NC} Claude Code CLI"

echo ""
echo "Optional Tools:"
check "terraform" "Install: brew install terraform" || echo -e "  ${YELLOW}[OPTIONAL]${NC} Needed for Episode 9"
check "gh" "Install: brew install gh" || echo -e "  ${YELLOW}[OPTIONAL]${NC} GitHub CLI for CI/CD demos"
check "k9s" "Install: brew install k9s" || echo -e "  ${YELLOW}[OPTIONAL]${NC} Nice K8s TUI"

echo ""

if [ $MISSING -gt 0 ]; then
    echo -e "${RED}Missing $MISSING required tools. Install them and re-run this script.${NC}"
    exit 1
fi

echo -e "${GREEN}All required tools found!${NC}"
echo ""

# ── Python dependencies ──
echo "=== Installing Python Dependencies ==="
pip3 install --quiet anthropic fastapi uvicorn pydantic requests PyGithub boto3 openai pyyaml 2>/dev/null
pip3 install --quiet "mcp[cli]" 2>/dev/null || echo -e "  ${YELLOW}MCP SDK install failed — may need Python 3.10+${NC}"
echo -e "  ${GREEN}[OK]${NC} Python dependencies installed"
echo ""

# ── Ollama models ──
echo "=== Pulling Ollama Models ==="
echo "Starting Ollama..."
ollama serve &>/dev/null &
sleep 2

echo "Pulling qwen2.5-coder:7b (this may take a few minutes on first run)..."
ollama pull qwen2.5-coder:7b 2>/dev/null && echo -e "  ${GREEN}[OK]${NC} qwen2.5-coder:7b" || echo -e "  ${YELLOW}[SKIP]${NC} Pull manually: ollama pull qwen2.5-coder:7b"

echo ""

# ── Kind cluster ──
echo "=== Setting Up Kubernetes Cluster ==="
if kind get clusters 2>/dev/null | grep -q "workshop"; then
    echo -e "  ${GREEN}[OK]${NC} Kind cluster 'workshop' already exists"
else
    echo "Creating kind cluster 'workshop'..."
    kind create cluster --name workshop
    echo -e "  ${GREEN}[OK]${NC} Kind cluster 'workshop' created"
fi
echo ""

# ── Test workloads ──
echo "=== Deploying Test Workloads ==="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cat << 'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-frontend
  namespace: default
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
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
          limits:
            cpu: 100m
            memory: 128Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  namespace: default
  labels:
    app: api-server
    tier: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
      - name: api
        image: nginx:nonexistent-v999
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: default
  labels:
    app: payment-service
    tier: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: payment-service
  template:
    metadata:
      labels:
        app: payment-service
    spec:
      containers:
      - name: payment
        image: busybox
        command: ["/bin/sh", "-c", "echo 'Starting payment service...' && sleep 5 && echo 'OOM simulated' && exit 137"]
        resources:
          requests:
            cpu: 50m
            memory: 32Mi
          limits:
            cpu: 100m
            memory: 64Mi
EOF

echo -e "  ${GREEN}[OK]${NC} Test workloads deployed"
echo ""
echo "Waiting 30 seconds for pods to start..."
sleep 30

echo ""
echo "=== Cluster Status ==="
kubectl get pods -o wide
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Setup Complete!                                         ║"
echo "║                                                          ║"
echo "║  You should see:                                         ║"
echo "║  - web-frontend pods: Running (healthy)                  ║"
echo "║  - api-server pods: ImagePullBackOff (intentional)       ║"
echo "║  - payment-service pods: CrashLoopBackOff (intentional)  ║"
echo "║                                                          ║"
echo "║  Environment check:                                      ║"
echo "║  - ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+SET}${ANTHROPIC_API_KEY:-NOT SET — export it!}  ║"
echo "║                                                          ║"
echo "║  Ready for the workshop!                                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
