#!/usr/bin/env python3
"""
Task 2: AI Pipeline Optimizer
==============================
Analyzes a GitHub Actions YAML and suggests optimizations including
caching strategies, parallel jobs, matrix builds, and conditional execution.

Usage:
    export ANTHROPIC_API_KEY="your-key"
    python3 task2_pipeline_optimizer.py
"""

import anthropic


def main():
    print("=" * 65)
    print("  TASK 2: AI PIPELINE OPTIMIZER")
    print("  Analyze GitHub Actions YAML, suggest speed/cost optimizations")
    print("=" * 65)

    # ─── System Prompt ───────────────────────────────────────────────
    SYSTEM_PROMPT = """You are a CI/CD pipeline optimization expert specializing in GitHub Actions.

Analyze the provided workflow YAML and suggest optimizations in these categories:
1. **Caching**: What can be cached? Provide exact cache key patterns.
2. **Parallelization**: Which jobs can run in parallel? Show the dependency graph.
3. **Conditional Execution**: Which jobs can be skipped based on changed files?
4. **Matrix Builds**: Where can matrix strategy reduce duplication?
5. **Resource Optimization**: Right-size runners for each job.
6. **Early Termination**: Reorder to fail fast on cheap checks.

For each optimization:
- **Category**: which category
- **Current**: what the workflow does now
- **Optimized**: exact YAML snippet showing the fix
- **Estimated savings**: time or cost reduction

Return a complete optimized workflow at the end."""

    # ─── Sample Workflow YAML (intentionally unoptimized) ────────────
    workflow_yaml = """name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm install

      - name: Run linter
        run: npm run lint

      - name: Run unit tests
        run: npm run test

      - name: Run integration tests
        run: npm run test:integration

      - name: Build application
        run: npm run build

      - name: Run security scan
        run: npm audit

      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Push Docker image
        run: docker push myapp:${{ github.sha }}

      - name: Deploy to staging
        run: kubectl apply -f k8s/staging/

      - name: Run smoke tests
        run: npm run test:smoke -- --env staging

      - name: Deploy to production
        if: github.ref == 'refs/heads/main'
        run: kubectl apply -f k8s/production/
"""

    print("\n" + "-" * 65)
    print("  INPUT: Unoptimized GitHub Actions Workflow")
    print("-" * 65)
    print(workflow_yaml)

    print("\n" + "-" * 65)
    print("  ANALYZING PIPELINE...")
    print("-" * 65)

    # ─── Call Claude API ─────────────────────────────────────────────
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Optimize this GitHub Actions workflow:\n\n```yaml\n{workflow_yaml}\n```"}
        ]
    )

    optimizations = message.content[0].text

    print("\n" + "=" * 65)
    print("  OPTIMIZATION RESULTS")
    print("=" * 65)
    print(optimizations)

    # ─── Summary ─────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Key Learning:")
    print("  Pipeline optimization is pattern matching across hundreds of best")
    print("  practices. AI identifies caching opportunities, parallelization")
    print("  potential, and unnecessary steps — then generates exact YAML fixes")
    print("  you can copy-paste into your workflow.")
    print("-" * 65)
    print("  Next: python3 task3_github_action.py")
    print("-" * 65)


if __name__ == "__main__":
    main()
