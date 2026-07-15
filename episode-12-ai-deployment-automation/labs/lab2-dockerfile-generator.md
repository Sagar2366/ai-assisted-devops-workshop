# Lab 2: AI Dockerfile Generator

> **Mission:** Use Claude to generate optimized, multi-stage Dockerfiles based on the application deployment profile from Lab 1.

## Concept: Multi-Stage Builds

Multi-stage Docker builds separate the build environment from the runtime environment, producing smaller, more secure images.

**Analogy**: Think of a multi-stage build like a construction project. The construction site (build stage) has heavy equipment, raw materials, and tools. The finished building (runtime stage) only contains what occupants need — no scaffolding, no cement mixers. Similarly, your final Docker image should not ship compilers, build tools, or source code.

```
┌─────────────────────────────────────────────────┐
│  Build Stage                                    │
│  ┌───────────┐  ┌────────┐  ┌───────────────┐  │
│  │ Source    │─▶│ Build  │─▶│ Compiled App  │  │
│  │ Code      │  │ Tools  │  │ + Deps        │  │
│  └───────────┘  └────────┘  └───────┬───────┘  │
│                                      │          │
├──────────────────────────────────────┼──────────┤
│  Runtime Stage                       │          │
│  ┌───────────────────────────────────▼───────┐  │
│  │ Minimal Base + App Binary/Code + Deps     │  │
│  │ (No build tools, no source, no cache)     │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Step 1: Build the Dockerfile Generation Prompt

```python
import json
import anthropic

def build_dockerfile_prompt(profile):
    """Create a prompt asking Claude to generate an optimized Dockerfile."""
    return f"""Generate a production-ready, multi-stage Dockerfile for this application.

Application Profile:
{json.dumps(profile, indent=2)}

Requirements:
1. Use a multi-stage build (builder + runtime stages)
2. Use specific version tags for base images (no 'latest')
3. Run as non-root user in the runtime stage
4. Include a HEALTHCHECK instruction
5. Use .dockerignore best practices in comments
6. Minimize layers and leverage build cache
7. Include appropriate labels (maintainer, version, description)
8. Set proper EXPOSE and ENTRYPOINT/CMD

Return ONLY the Dockerfile content, no explanation.
"""
```

## Step 2: Generate the Dockerfile

```python
def generate_dockerfile(profile):
    """Use Claude to generate a multi-stage Dockerfile."""
    client = anthropic.Anthropic()
    prompt = build_dockerfile_prompt(profile)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    dockerfile_content = message.content[0].text
    # Strip markdown code fences if present
    if dockerfile_content.startswith("```"):
        lines = dockerfile_content.split('\n')
        dockerfile_content = '\n'.join(lines[1:-1])
    
    return dockerfile_content
```

## Step 3: Example Output for Python App

For a Flask application, Claude generates something like:

```dockerfile
# ============================================
# Build Stage
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# Runtime Stage
# ============================================
FROM python:3.11-slim AS runtime

LABEL maintainer="team@example.com"
LABEL description="Flask application"
LABEL version="1.0.0"

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

ENTRYPOINT ["gunicorn"]
CMD ["app:app", "--bind", "0.0.0.0:5000", "--workers", "4"]
```

## Step 4: Example Output for Node App

```dockerfile
# ============================================
# Build Stage
# ============================================
FROM node:20-alpine AS builder

WORKDIR /build

COPY package*.json ./
RUN npm ci --production

# ============================================
# Runtime Stage
# ============================================
FROM node:20-alpine AS runtime

LABEL maintainer="team@example.com"
LABEL description="Express application"
LABEL version="1.0.0"

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

COPY --from=builder /build/node_modules ./node_modules
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "app.js"]
```

## Step 5: Save and Validate

```python
def save_dockerfile(content, output_path="Dockerfile"):
    """Save the generated Dockerfile."""
    with open(output_path, 'w') as f:
        f.write(content)
    print(f"Dockerfile saved to: {output_path}")

# Optionally validate with docker
import subprocess

def validate_dockerfile(path):
    """Run a basic lint check on the Dockerfile."""
    result = subprocess.run(
        ["docker", "build", "--check", "-f", path, "."],
        capture_output=True, text=True
    )
    return result.returncode == 0
```

## Running the Demo Script

```bash
cd demos
python task2_dockerfile_generator.py
```

## What Success Looks Like

- [x] Claude generates a complete multi-stage Dockerfile
- [x] Build stage installs dependencies without including build tools in final image
- [x] Runtime stage uses a minimal base image
- [x] Non-root user is configured
- [x] HEALTHCHECK instruction is included
- [x] Proper EXPOSE and CMD/ENTRYPOINT are set
- [x] The generated Dockerfile builds successfully (if Docker is available)

## Key Takeaway

> AI-generated Dockerfiles follow production best practices by default — multi-stage builds, non-root users, health checks, and minimal images. Instead of copying boilerplate and forgetting security hardening, the AI produces optimized containers every time based on the specific application profile.

**Next:** Lab 3 — Kubernetes Manifest Generator
