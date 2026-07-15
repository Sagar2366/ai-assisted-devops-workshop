# Lab 1: AI Application Analyzer

> **Mission:** Use Claude to analyze application source code and dependency files, producing a structured deployment profile that drives all downstream artifact generation.

## Concept: Why Analyze Before Deploying?

Think of this like a doctor's examination before prescribing treatment. Before generating any deployment artifacts, we need to understand:

- **Runtime**: What language and version does the app need?
- **Framework**: Is it Flask, Express, Gin — each has different serving patterns
- **Dependencies**: What packages need to be installed at build time?
- **Ports**: What port does the application listen on?
- **Environment Variables**: What configuration does it expect?
- **Health Checks**: Does it expose health endpoints?

**Analogy**: A deployment profile is like an architectural blueprint. You would not start construction without understanding the building's requirements — similarly, AI analyzes the "blueprints" (source code) before generating infrastructure.

## The Analysis Pipeline

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ requirements.txt│     │                  │     │ Deployment      │
│ package.json    │────▶│  Claude Analysis │────▶│ Profile (JSON)  │
│ go.mod          │     │                  │     │                 │
│ app source      │     └──────────────────┘     └─────────────────┘
└─────────────────┘
```

## Step 1: Read Application Files

First, we gather the relevant files from the application:

```python
import os
import json

def read_app_files(app_dir):
    """Read dependency and source files from an application directory."""
    files = {}
    target_files = [
        'requirements.txt', 'package.json', 'go.mod',
        'app.py', 'main.py', 'app.js', 'index.js', 'main.go',
        'Procfile', '.env.example'
    ]
    
    for filename in target_files:
        filepath = os.path.join(app_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                files[filename] = f.read()
    
    return files
```

## Step 2: Build the Analysis Prompt

The prompt instructs Claude to produce a structured JSON profile:

```python
def build_analysis_prompt(files):
    """Construct a prompt that asks Claude to analyze the application."""
    file_contents = ""
    for name, content in files.items():
        file_contents += f"\n--- {name} ---\n{content}\n"
    
    return f"""Analyze the following application files and produce a deployment profile as JSON.

{file_contents}

Return a JSON object with these fields:
- runtime: the language (python, node, go)
- runtime_version: recommended version
- framework: the web framework used
- port: the port the app listens on
- dependencies: list of key dependencies
- env_vars: list of environment variables needed
- health_endpoint: health check path if available
- build_command: command to build/install dependencies
- start_command: command to start the application
- needs_database: boolean
- database_type: if applicable (postgres, redis, mongodb, etc.)
"""
```

## Step 3: Call Claude for Analysis

```python
import anthropic

def analyze_application(app_dir):
    """Use Claude to analyze an application and return a deployment profile."""
    client = anthropic.Anthropic()
    files = read_app_files(app_dir)
    
    if not files:
        raise ValueError(f"No recognizable application files found in {app_dir}")
    
    prompt = build_analysis_prompt(files)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Extract JSON from the response
    response_text = message.content[0].text
    # Find JSON block in the response
    import re
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        profile = json.loads(json_match.group())
        return profile
    
    raise ValueError("Could not extract JSON profile from response")
```

## Step 4: Test with the Sample Python App

```python
profile = analyze_application("demos/sample-apps/python-app")
print(json.dumps(profile, indent=2))
```

Expected output:

```json
{
  "runtime": "python",
  "runtime_version": "3.11",
  "framework": "flask",
  "port": 5000,
  "dependencies": ["flask", "gunicorn", "redis"],
  "env_vars": ["FLASK_ENV", "REDIS_URL"],
  "health_endpoint": "/health",
  "build_command": "pip install -r requirements.txt",
  "start_command": "gunicorn app:app --bind 0.0.0.0:5000",
  "needs_database": true,
  "database_type": "redis"
}
```

## Step 5: Test with the Sample Node App

```python
profile = analyze_application("demos/sample-apps/node-app")
print(json.dumps(profile, indent=2))
```

Expected output:

```json
{
  "runtime": "node",
  "runtime_version": "20",
  "framework": "express",
  "port": 3000,
  "dependencies": ["express", "mongoose", "dotenv"],
  "env_vars": ["NODE_ENV", "MONGODB_URI", "PORT"],
  "health_endpoint": "/health",
  "build_command": "npm ci --production",
  "start_command": "node app.js",
  "needs_database": true,
  "database_type": "mongodb"
}
```

## Running the Demo Script

```bash
cd demos
python task1_app_analyzer.py
```

## What Success Looks Like

- [x] The analyzer reads `requirements.txt` or `package.json` and source files
- [x] Claude returns a structured JSON deployment profile
- [x] The profile correctly identifies runtime, framework, port, and dependencies
- [x] The profile flags database requirements and environment variables
- [x] Both Python and Node sample apps are analyzed successfully

## Key Takeaway

> AI application analysis transforms unstructured source code into a structured deployment profile. This profile becomes the single source of truth that drives all downstream automation — Dockerfiles, K8s manifests, and compose files all derive from this analysis.

**Next:** Lab 2 — Dockerfile Generator
