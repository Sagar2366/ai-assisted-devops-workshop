# Lab 2: AI Pipeline Optimizer

> **Mission:** Feed your GitHub Actions workflow to AI — get specific optimizations for speed, cost, caching, and parallelization.

---

## The Concept

### Why Optimize CI/CD Pipelines?

Slow pipelines kill developer productivity. A 20-minute pipeline means 20 minutes of context-switching on every push. AI can analyze your workflow YAML and suggest specific optimizations — caching strategies, job parallelization, conditional execution — that would take hours of manual research.

> **Analogy:** Like a CI/CD consultant who has optimized 10,000 pipelines — they instantly spot that your npm install runs uncached, your tests could run in parallel, and half your jobs don't need to run on PRs to docs-only changes.

---

### Optimization Categories

| Category | Example Optimization | Typical Savings |
|----------|---------------------|----------------|
| Caching | Cache node_modules, Go modules, Docker layers | 30-70% time reduction |
| Parallelization | Run tests, lint, security scan in parallel | 40-60% time reduction |
| Conditional execution | Skip deploy on docs-only changes | Eliminates unnecessary runs |
| Resource right-sizing | Use smaller runners for lint, larger for builds | 20-40% cost reduction |
| Early termination | Fail fast on lint before running full test suite | Faster feedback |

---

## What You'll Build

A Python script that analyzes a GitHub Actions YAML and returns specific, actionable optimizations with estimated time/cost savings.

---

## Step 1: The Optimizer Prompt

```python
SYSTEM_PROMPT = """You are a CI/CD pipeline optimization expert specializing in GitHub Actions.

Analyze the provided workflow YAML and suggest optimizations in these categories:
1. **Caching**: What can be cached? Provide exact cache key patterns.
2. **Parallelization**: Which jobs can run in parallel? Show the dependency graph.
3. **Conditional Execution**: Which jobs can be skipped based on changed files?
4. **Resource Optimization**: Right-size runners for each job.
5. **Early Termination**: Reorder to fail fast on cheap checks.

For each optimization:
- **Category**: which category
- **Current**: what the workflow does now
- **Optimized**: exact YAML snippet showing the fix
- **Estimated savings**: time or cost reduction

Return a complete optimized workflow at the end."""
```

---

## Step 2: Analyze a Workflow

```python
workflow_yaml = '''
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm install
      - run: npm run lint
      - run: npm run test
      - run: npm run build
      - run: docker build -t myapp .
      - run: docker push myapp:latest
'''

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": f"Optimize this GitHub Actions workflow:\n\n```yaml\n{workflow_yaml}\n```"}
    ]
)
print(message.content[0].text)
```

---

## Run It

```bash
python3 demos/task2_pipeline_optimizer.py
```

---

## What Success Looks Like

The AI suggests:
1. Add npm cache with `actions/setup-node` cache option
2. Split lint/test/build into parallel jobs
3. Add path filter: skip Docker build on docs-only changes
4. Add Docker layer caching
5. Move lint first — cheapest check fails fastest

And provides a complete rewritten workflow YAML.

---

## Key Takeaway

Pipeline optimization is pattern matching across hundreds of best practices. AI knows all of them and applies them to YOUR specific workflow — not generic advice, but exact YAML snippets you can copy-paste.

---

Next: [Lab 3: GitHub Actions](lab3-github-actions.md)
