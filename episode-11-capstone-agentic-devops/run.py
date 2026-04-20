#!/usr/bin/env python3
"""
Episode 11: Capstone — End-to-End Agentic DevOps Platform
Entry point — Starts the Agentic SRE Platform server.

Author: Sagar Utekar
Series: AI-Assisted DevOps Workshop

Prerequisites:
    - Python 3.10+
    - pip install fastapi uvicorn anthropic
    - ANTHROPIC_API_KEY environment variable set
    - kubectl configured with cluster access

Usage:
    python3 run.py
"""
import uvicorn

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║            AGENTIC SRE PLATFORM v1.0                         ║
║            by Sagar Utekar                                   ║
║            CNCF Ambassador | Kubestronaut                    ║
║                                                              ║
║  Endpoints:                                                  ║
║    GET  /health              - Platform health               ║
║    POST /diagnose            - Cluster diagnosis             ║
║    POST /incident            - Handle incident               ║
║    POST /scan                - Security scan                 ║
║    POST /webhook/alertmanager - Alertmanager webhook         ║
║    GET  /audit               - Full audit trail              ║
║    POST /ask                 - Ask anything                  ║
║                                                              ║
║  Docs: http://localhost:8000/docs                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
