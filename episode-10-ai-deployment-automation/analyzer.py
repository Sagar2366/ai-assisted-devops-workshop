"""
Episode 10: AI-Powered Deployment Automation
Tool: AI Application Analyzer

Reads a Python app and recommends the best deployment target.
Analyzes framework, dependencies, ports, and traffic patterns.

Author: Sagar Utekar
Prerequisites:
    - Anthropic API key (set ANTHROPIC_API_KEY env var)
    - pip install anthropic
    - An application directory to analyze (or use the built-in sample app)
"""
import anthropic
import os
import json

client = anthropic.Anthropic()

ANALYZER_SYSTEM = """You are a deployment architect. Analyze application code and recommend the best deployment target.

## Analysis Checklist:
1. Framework detection (Flask, FastAPI, Django, etc.)
2. Dependencies (requirements.txt, package.json, go.mod)
3. Port configuration
4. Database/cache requirements
5. Static file serving needs
6. Background job requirements
7. Expected traffic pattern (steady, bursty, event-driven)

## Deployment Targets:
- **Container (Docker)**: Good default. Stateless apps, microservices.
- **Kubernetes**: Multiple replicas needed, auto-scaling, service mesh, >1 service.
- **VM (Ansible)**: Legacy apps, stateful workloads, compliance requirements.
- **Serverless**: Event-driven, infrequent traffic, cost-sensitive.

## Output JSON:
{
  "app_name": "name",
  "framework": "detected framework",
  "language_version": "e.g. python 3.11+",
  "port": 8080,
  "dependencies": ["list", "of", "key", "deps"],
  "has_database": true/false,
  "has_background_jobs": true/false,
  "recommended_target": "container|kubernetes|vm|serverless",
  "reasoning": "why this target",
  "deployment_artifacts_needed": ["Dockerfile", "k8s manifests", "docker-compose.yml"]
}"""


def analyze_app(app_dir: str) -> dict:
    """Analyze an application directory and recommend deployment."""

    # Read key files
    app_files = {}
    important_files = [
        "app.py", "main.py", "server.py", "wsgi.py",
        "requirements.txt", "Pipfile", "pyproject.toml",
        "package.json", "go.mod", "Cargo.toml",
        "Dockerfile", "docker-compose.yml",
        ".env.example", "config.py", "settings.py"
    ]

    for fname in important_files:
        fpath = os.path.join(app_dir, fname)
        if os.path.exists(fpath):
            with open(fpath) as f:
                content = f.read()
                # Limit file size to avoid huge tokens
                app_files[fname] = content[:3000]

    # Also look for any .py files in root
    for fname in os.listdir(app_dir):
        if fname.endswith(".py") and fname not in app_files:
            fpath = os.path.join(app_dir, fname)
            with open(fpath) as f:
                app_files[fname] = f.read()[:2000]

    if not app_files:
        return {"error": "No recognizable application files found"}

    file_listing = ""
    for name, content in app_files.items():
        file_listing += f"\n### {name}\n```\n{content}\n```\n"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=ANALYZER_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"Analyze this application and recommend deployment:\n{file_listing}"
        }]
    )

    result_text = response.content[0].text

    # Parse JSON from response
    try:
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            json_str = result_text.split("```")[1].split("```")[0]
        else:
            json_str = result_text
        return json.loads(json_str)
    except (json.JSONDecodeError, IndexError):
        return {"raw_response": result_text}


if __name__ == "__main__":
    import sys
    app_dir = sys.argv[1] if len(sys.argv) > 1 else "sample_app"

    # Create a sample Flask app if none exists
    if not os.path.exists(app_dir):
        os.makedirs(app_dir, exist_ok=True)

        # Sample Flask app
        with open(os.path.join(app_dir, "app.py"), "w") as f:
            f.write('''from flask import Flask, jsonify, request
import redis
import os

app = Flask(__name__)
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379))
)

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/api/items", methods=["GET"])
def get_items():
    items = redis_client.lrange("items", 0, -1)
    return jsonify([i.decode() for i in items])

@app.route("/api/items", methods=["POST"])
def add_item():
    item = request.json.get("name")
    redis_client.rpush("items", item)
    return jsonify({"added": item}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
''')

        with open(os.path.join(app_dir, "requirements.txt"), "w") as f:
            f.write("flask==3.0.0\nredis==5.0.1\ngunicorn==21.2.0\n")

        print(f"Created sample Flask app in {app_dir}/\n")

    print("Analyzing application...\n")
    result = analyze_app(app_dir)
    print(json.dumps(result, indent=2))
