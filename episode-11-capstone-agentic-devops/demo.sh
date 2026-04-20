#!/usr/bin/env bash
# Episode 11: Capstone — End-to-End Agentic DevOps Platform
# Demo Script — 8 curl commands to exercise all platform endpoints.
#
# Author: Sagar Utekar
# Series: AI-Assisted DevOps Workshop
#
# Prerequisites:
#   - Platform running: python3 run.py (in another terminal)
#   - jq installed for JSON formatting
#   - kubectl cluster with test workloads deployed
#
# Usage:
#   chmod +x demo.sh
#   ./demo.sh

set -euo pipefail

BASE_URL="http://localhost:8000"

echo "============================================"
echo "  Agentic SRE Platform — Demo Sequence"
echo "============================================"
echo ""

# 1. Health check
echo ">>> 1. Health check"
curl -s "$BASE_URL/health" | jq
echo ""

# 2. Cluster diagnosis
echo ">>> 2. Cluster diagnosis"
curl -s -X POST "$BASE_URL/diagnose" \
  -H "Content-Type: application/json" \
  -d '{"query": "Full cluster diagnosis — find all issues, prioritize by severity"}' | jq
echo ""

# 3. Incident response
echo ">>> 3. Incident response"
curl -s -X POST "$BASE_URL/incident" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_name": "PodCrashLooping",
    "severity": "critical",
    "service": "payment-service",
    "namespace": "default",
    "description": "Payment service has restarted 15 times"
  }' | jq
echo ""

# 4. Security scan
echo ">>> 4. Security scan"
curl -s -X POST "$BASE_URL/scan" \
  -H "Content-Type: application/json" \
  -d '{"namespace": "default"}' | jq
echo ""

# 5. Simulate Alertmanager webhook
echo ">>> 5. Simulate Alertmanager webhook"
curl -s -X POST "$BASE_URL/webhook/alertmanager" \
  -H "Content-Type: application/json" \
  -d '{
    "alerts": [{
      "labels": {"alertname": "HighErrorRate", "severity": "critical", "service": "api-server", "namespace": "default"},
      "annotations": {"description": "Error rate > 10%"},
      "status": "firing"
    }]
  }' | jq
echo ""

# 6. Free-form question
echo ">>> 6. Free-form question"
curl -s -X POST "$BASE_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Which deployments are healthy and which need attention?"}' | jq
echo ""

# 7. Check audit trail
echo ">>> 7. Check audit trail"
curl -s "$BASE_URL/audit" | jq
echo ""

# 8. Open Swagger docs
echo ">>> 8. Open Swagger docs"
echo "Open http://localhost:8000/docs in your browser!"
