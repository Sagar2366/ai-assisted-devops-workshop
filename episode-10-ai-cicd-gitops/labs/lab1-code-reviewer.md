# Lab 1: AI Code Reviewer

> **Mission:** Build an AI code reviewer that analyzes diffs for bugs, security vulnerabilities, and best practice violations — like a senior engineer reviewing every PR.

---

## The Concept

### Why AI Code Review?

Human reviewers miss things. They get fatigued after the 5th PR of the day. They have blind spots in areas outside their expertise. AI reviews every line with the same attention, catches patterns across the entire codebase, and never gets tired.

> **Analogy:** Like having a tireless senior engineer who has reviewed millions of PRs across every language and framework — and who checks security, performance, and correctness on every single review without fail.

---

### What AI Catches That Humans Often Miss

| Category | Example |
|----------|---------|
| Security | SQL injection, hardcoded secrets, SSRF |
| Logic bugs | Off-by-one errors, race conditions, null dereferences |
| Performance | N+1 queries, unnecessary allocations in loops |
| Best practices | Missing error handling, inconsistent naming |
| DevOps-specific | Privileged containers, missing resource limits, no health checks |

---

## What You'll Build

A Python script that:
1. Takes a unified diff as input
2. Sends it to Claude with a code review system prompt
3. Returns structured findings: severity, location, description, fix suggestion

---

## Step 1: The Code Review Prompt

```python
SYSTEM_PROMPT = """You are a senior code reviewer specializing in DevOps and cloud-native applications.

Review the provided diff and identify:
1. **CRITICAL**: Security vulnerabilities, data loss risks, production outage risks
2. **HIGH**: Logic bugs, race conditions, missing error handling
3. **MEDIUM**: Performance issues, code smells, missing tests
4. **LOW**: Style issues, naming conventions, documentation gaps

For each finding, provide:
- **Severity**: CRITICAL/HIGH/MEDIUM/LOW
- **File**: filename and line number
- **Issue**: what's wrong
- **Impact**: what could go wrong in production
- **Fix**: concrete code suggestion

Focus on issues that could cause incidents in production. Skip trivial style nits unless they indicate a pattern."""
```

---

## Step 2: Review a Diff

```python
import anthropic

client = anthropic.Anthropic()

diff = '''
diff --git a/app/api/users.py b/app/api/users.py
--- a/app/api/users.py
+++ b/app/api/users.py
@@ -15,6 +15,12 @@ def get_user(user_id):
 
+@app.route("/api/users/search")
+def search_users():
+    query = request.args.get("q")
+    results = db.execute(f"SELECT * FROM users WHERE name LIKE '%{query}%'")
+    return jsonify(results)
+
+@app.route("/api/users/<user_id>/delete", methods=["POST"])
+def delete_user(user_id):
+    db.execute(f"DELETE FROM users WHERE id = {user_id}")
+    return jsonify({"status": "deleted"})
'''

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": f"Review this diff:\n\n```diff\n{diff}\n```"}
    ]
)
print(message.content[0].text)
```

---

## Run It

```bash
python3 demos/task1_code_reviewer.py
```

---

## What Success Looks Like

The AI identifies:
1. CRITICAL: SQL injection in both endpoints (string interpolation in SQL)
2. HIGH: No authentication/authorization check on delete endpoint
3. HIGH: DELETE via POST instead of DELETE method
4. MEDIUM: No input validation or sanitization on search query
5. MEDIUM: No rate limiting on search endpoint

Each finding includes a concrete fix with parameterized queries.

---

## Key Takeaway

AI code review catches security vulnerabilities that humans routinely miss under time pressure. The structured system prompt ensures consistent severity ratings and actionable fix suggestions — not just "this looks wrong" but "here's the exact code to fix it."

---

Next: [Lab 2: Pipeline Optimizer](lab2-pipeline-optimizer.md)
