# Lab 5: Full Deployment Pipeline

> **Mission:** Orchestrate the complete AI deployment automation pipeline — from source code analysis through all artifact generation — in a single end-to-end flow.

## Concept: Pipeline Orchestration

The full pipeline combines all previous labs into a single automated workflow. One command analyzes your application and produces every deployment artifact needed to run it in development, staging, and production.

**Analogy**: This is like an architect who visits a building site, surveys the land, then produces all the blueprints, permits, and contractor instructions in one visit. No back-and-forth, no missed details — a complete package ready for construction.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Full Deployment Pipeline                      │
│                                                                 │
│  ┌────────┐   ┌──────────┐   ┌────────────────────────────┐    │
│  │ Source │──▶│ Analyze  │──▶│ Generate All Artifacts     │    │
│  │ Code   │   │ App      │   │                            │    │
│  └────────┘   └──────────┘   │  ├── Dockerfile            │    │
│                               │  ├── k8s/deployment.yaml   │    │
│                               │  ├── k8s/service.yaml      │    │
│                               │  ├── k8s/hpa.yaml          │    │
│                               │  ├── k8s/ingress.yaml      │    │
│                               │  ├── docker-compose.yaml   │    │
│                               │  └── .dockerignore         │    │
│                               └────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Step 1: Pipeline Configuration

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class PipelineConfig:
    """Configuration for the deployment pipeline."""
    app_dir: str
    app_name: str
    namespace: str = "default"
    output_dir: str = "./deploy"
    registry: str = "ghcr.io"
    domain: str = "example.com"
    replicas_min: int = 2
    replicas_max: int = 10
    cpu_target: int = 70
```

## Step 2: The Pipeline Orchestrator

```python
import os
import json
import anthropic

class DeploymentPipeline:
    """Orchestrates the full AI deployment automation pipeline."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.client = anthropic.Anthropic()
        self.profile = None
    
    def run(self):
        """Execute the full pipeline."""
        print(f"{'=' * 65}")
        print(f"  AI Deployment Pipeline: {self.config.app_name}")
        print(f"{'=' * 65}")
        
        # Phase 1: Analyze
        print("\n[1/4] Analyzing application...")
        self.profile = self.analyze()
        print(f"       Runtime: {self.profile['runtime']}")
        print(f"       Framework: {self.profile['framework']}")
        print(f"       Port: {self.profile['port']}")
        
        # Phase 2: Dockerfile
        print("\n[2/4] Generating Dockerfile...")
        dockerfile = self.generate_dockerfile()
        self.save("Dockerfile", dockerfile)
        
        # Phase 3: K8s manifests
        print("\n[3/4] Generating Kubernetes manifests...")
        manifests = self.generate_k8s()
        self.save("k8s/manifests.yaml", manifests)
        
        # Phase 4: Compose
        print("\n[4/4] Generating docker-compose.yaml...")
        compose = self.generate_compose()
        self.save("docker-compose.yaml", compose)
        
        # Summary
        self.print_summary()
    
    def analyze(self):
        """Phase 1: Analyze the application."""
        # (Implementation from Lab 1)
        ...
    
    def generate_dockerfile(self):
        """Phase 2: Generate Dockerfile."""
        # (Implementation from Lab 2)
        ...
    
    def generate_k8s(self):
        """Phase 3: Generate K8s manifests."""
        # (Implementation from Lab 3)
        ...
    
    def generate_compose(self):
        """Phase 4: Generate compose file."""
        # (Implementation from Lab 4)
        ...
    
    def save(self, filename, content):
        """Save an artifact to the output directory."""
        path = os.path.join(self.config.output_dir, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        print(f"       Saved: {path}")
    
    def print_summary(self):
        """Print a summary of generated artifacts."""
        print(f"\n{'=' * 65}")
        print(f"  Pipeline Complete!")
        print(f"{'=' * 65}")
        print(f"\n  Generated artifacts in: {self.config.output_dir}/")
        print(f"  ├── Dockerfile")
        print(f"  ├── k8s/manifests.yaml")
        print(f"  ├── docker-compose.yaml")
        print(f"  └── profile.json")
        print(f"\n  Next steps:")
        print(f"  1. docker compose up        (local development)")
        print(f"  2. docker build -t app .    (build image)")
        print(f"  3. kubectl apply -f k8s/    (deploy to cluster)")
```

## Step 3: Run the Pipeline

```python
config = PipelineConfig(
    app_dir="./sample-apps/python-app",
    app_name="my-flask-app",
    namespace="production",
    output_dir="./output/python-app",
    domain="mycompany.com"
)

pipeline = DeploymentPipeline(config)
pipeline.run()
```

## Step 4: Inspect Generated Output

```bash
tree output/python-app/
# output/python-app/
# ├── Dockerfile
# ├── docker-compose.yaml
# ├── k8s/
# │   └── manifests.yaml
# └── profile.json
```

## Step 5: Test the Artifacts

```bash
# Test Docker build
cd output/python-app
docker build -t my-flask-app .

# Test compose
docker compose up -d
docker compose ps
docker compose down

# Validate K8s manifests
kubectl apply --dry-run=client -f k8s/manifests.yaml
```

## Running the Demo Script

```bash
cd demos
python task5_full_deployment.py
```

The script runs the full pipeline against both sample applications and shows all generated artifacts.

## What Success Looks Like

- [x] A single command produces all deployment artifacts
- [x] The pipeline correctly chains analysis into generation
- [x] Output directory has a clean, organized structure
- [x] All generated files are syntactically valid
- [x] The Dockerfile builds successfully
- [x] The compose file starts the application with its dependencies
- [x] K8s manifests pass dry-run validation
- [x] The same pipeline works for both Python and Node applications

## Key Takeaway

> The full deployment pipeline demonstrates the power of AI-driven automation: a single analysis pass produces a complete, consistent set of deployment artifacts. Every artifact derives from the same source of truth — the deployment profile — ensuring alignment between local development, CI/CD, and production environments. This eliminates the drift that occurs when these files are maintained independently.

**Congratulations!** You have built a complete AI-powered deployment automation system. From analyzing source code to generating production-ready infrastructure, Claude acts as your deployment engineer — one that never forgets best practices.
