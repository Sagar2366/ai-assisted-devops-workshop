# Lab 4: AI Docker Compose Generator

> **Mission:** Use Claude to generate docker-compose.yaml files that replicate the production topology locally, including dependent services like databases and caches.

## Concept: Local Development Parity

The goal of a compose file is to give developers a one-command setup that mirrors production — same services, same networking, same environment variables.

**Analogy**: If Kubernetes manifests are the blueprints for a skyscraper, docker-compose is a scale model that fits on your desk. It has the same structure — the same rooms and hallways — but runs on your laptop instead of in the cloud.

```
┌─────────────────────────────────────────────────────┐
│  docker-compose.yaml                                │
│                                                     │
│  ┌───────────┐    ┌───────────┐    ┌────────────┐  │
│  │    App    │───▶│  Database │    │   Cache    │  │
│  │  Service  │    │  Service  │    │  Service   │  │
│  └─────┬─────┘    └───────────┘    └────────────┘  │
│        │                                            │
│  ┌─────▼─────┐                                     │
│  │  Volume   │    Network: app-network              │
│  │  Mounts   │                                     │
│  └───────────┘                                     │
└─────────────────────────────────────────────────────┘
```

## Step 1: Build the Compose Generation Prompt

```python
import json
import anthropic

def build_compose_prompt(profile, app_name):
    """Create a prompt for generating docker-compose.yaml."""
    return f"""Generate a docker-compose.yaml for local development of this application.

Application Name: {app_name}
Application Profile:
{json.dumps(profile, indent=2)}

Requirements:
1. Include the main application service with:
   - Build context pointing to current directory
   - Volume mounts for live code reloading
   - Port mapping to the host
   - Environment variables from the profile
   - Depends_on for any required services
2. Include dependent services based on the profile:
   - If needs_database is true, add the appropriate database service
   - Add Redis if the app uses caching
   - Include proper volume persistence for data services
3. Define a custom network for service communication
4. Add health checks for all services
5. Use named volumes for database persistence
6. Include comments explaining each section

Return ONLY the docker-compose.yaml content, no explanation.
Use docker compose v3.8+ format.
"""
```

## Step 2: Generate the Compose File

```python
def generate_compose(profile, app_name):
    """Use Claude to generate a docker-compose.yaml."""
    client = anthropic.Anthropic()
    prompt = build_compose_prompt(profile, app_name)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    compose_content = message.content[0].text
    # Strip markdown code fences if present
    if compose_content.startswith("```"):
        lines = compose_content.split('\n')
        compose_content = '\n'.join(lines[1:-1])
    
    return compose_content
```

## Step 3: Example Output for Python App (with Redis)

```yaml
version: "3.8"

services:
  # Main application service
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: python-flask-app
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./:/app
      - /app/__pycache__  # Exclude pycache from mount
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    restart: unless-stopped

  # Redis cache service
  redis:
    image: redis:7-alpine
    container_name: python-flask-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
    restart: unless-stopped

networks:
  app-network:
    driver: bridge

volumes:
  redis-data:
    driver: local
```

## Step 4: Example Output for Node App (with MongoDB)

```yaml
version: "3.8"

services:
  # Main application service
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: node-express-app
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - MONGODB_URI=mongodb://mongodb:27017/myapp
      - PORT=3000
    volumes:
      - ./:/app
      - /app/node_modules  # Exclude node_modules from mount
    depends_on:
      mongodb:
        condition: service_healthy
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    restart: unless-stopped

  # MongoDB database service
  mongodb:
    image: mongo:7
    container_name: node-express-mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongodb-data:/data/db
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 3
    restart: unless-stopped

networks:
  app-network:
    driver: bridge

volumes:
  mongodb-data:
    driver: local
```

## Step 5: Validate the Compose File

```python
import subprocess

def validate_compose(filepath):
    """Validate the generated compose file."""
    result = subprocess.run(
        ["docker", "compose", "-f", filepath, "config", "--quiet"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("Compose file is valid!")
    else:
        print(f"Validation error: {result.stderr}")
    return result.returncode == 0
```

## Running the Demo Script

```bash
cd demos
python task4_compose_generator.py
```

## What Success Looks Like

- [x] Claude generates a complete docker-compose.yaml with all necessary services
- [x] Database/cache services are included based on the deployment profile
- [x] Volume mounts enable live code reloading for development
- [x] Health checks are configured for all services
- [x] Named volumes persist database data across restarts
- [x] A custom network connects all services
- [x] The compose file passes `docker compose config` validation

## Key Takeaway

> AI-generated compose files bridge the gap between development and production. By deriving the local environment from the same deployment profile used for K8s manifests, developers get a consistent experience that catches integration issues early — before code ever reaches the cluster.

**Next:** Lab 5 — Full Deployment Pipeline
