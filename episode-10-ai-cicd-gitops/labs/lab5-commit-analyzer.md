# Lab 5: AI Commit Analyzer

> **Mission:** Use AI to categorize commits and generate structured release notes — turning messy git history into clean changelogs automatically.

---

## The Concept

### Why AI for Commit Analysis?

Git logs are messy. Developers write commits like "fix stuff", "WIP", "address review comments". Release notes need structure: features, fixes, refactors, breaking changes. AI reads intent from diffs and messages, categorizes properly, and generates human-readable changelogs.

> **Analogy:** Like a librarian who takes a pile of unsorted books (commits) dumped on a table and organizes them by genre, author, and publication date — then writes a catalog entry for each section that visitors can actually use.

---

### Commit Categories

| Category | Conventional Prefix | Example |
|----------|-------------------|---------|
| Feature | `feat:` | New API endpoint, new CLI flag |
| Fix | `fix:` | Bug fix, crash fix, data corruption fix |
| Refactor | `refactor:` | Code restructuring, no behavior change |
| Documentation | `docs:` | README updates, API docs, comments |
| Performance | `perf:` | Optimization, caching, query tuning |
| Breaking Change | `BREAKING:` | API removal, schema migration required |

---

### Semantic Versioning from Commits

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Breaking change | MAJOR (X.0.0) | Remove deprecated API endpoint |
| New feature | MINOR (0.X.0) | Add new search filter |
| Bug fix | PATCH (0.0.X) | Fix null pointer in auth |

---

## What You'll Build

A Python script that:
1. Parses git log output (commit hash, author, message, date)
2. Uses Claude to categorize each commit
3. Generates structured release notes grouped by category
4. Suggests the next semantic version

---

## Step 1: Parse Git Log

```python
import subprocess
import re

def get_git_log(since_tag="v1.0.0"):
    """Get git log since last release tag."""
    result = subprocess.run(
        ["git", "log", f"{since_tag}..HEAD", "--pretty=format:%H|%an|%s|%ai"],
        capture_output=True, text=True
    )
    commits = []
    for line in result.stdout.strip().split("\n"):
        if "|" in line:
            parts = line.split("|", 3)
            commits.append({
                "hash": parts[0][:8],
                "author": parts[1],
                "message": parts[2],
                "date": parts[3]
            })
    return commits
```

---

## Step 2: AI Categorization

```python
import anthropic

client = anthropic.Anthropic()

def categorize_commits(commits):
    """Use Claude to categorize a batch of commits."""

    commit_list = "\n".join(
        f"- {c['hash']}: {c['message']}" for c in commits
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="""You are a release engineer categorizing git commits.

For each commit, assign exactly ONE category:
- feature: New functionality
- fix: Bug fix
- refactor: Code restructuring without behavior change
- docs: Documentation only
- perf: Performance improvement
- breaking: Breaking change (API removal, schema change)
- chore: Build, CI, dependency updates

Return JSON array:
[{"hash": "abc123", "category": "feature", "description": "Clean one-line description"}]

Infer intent from the commit message. "fix typo in README" is docs, not fix.
"update deps" is chore. "Add retry logic" is feature.""",
        messages=[
            {"role": "user", "content": f"Categorize these commits:\n\n{commit_list}"}
        ]
    )
    return message.content[0].text
```

---

## Step 3: Generate Release Notes

```python
def generate_release_notes(categorized_commits, version):
    """Generate structured release notes from categorized commits."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="""Generate release notes in this exact format:

# Release vX.Y.Z

## Highlights
(2-3 sentence summary of the most important changes)

## Features
- Description of feature (hash)

## Bug Fixes
- Description of fix (hash)

## Breaking Changes
- Description with migration guide

## Other Changes
- Refactors, docs, chores grouped here

---
**Full Changelog**: link_placeholder

Omit empty sections. Write for end users, not developers.""",
        messages=[
            {"role": "user", "content": f"Generate release notes for version {version}:\n\n{categorized_commits}"}
        ]
    )
    return message.content[0].text
```

---

## Step 4: Version Suggestion

```python
def suggest_version(current_version, categories):
    """Suggest next version based on commit categories."""
    major, minor, patch = map(int, current_version.lstrip("v").split("."))

    if "breaking" in categories:
        return f"v{major + 1}.0.0"
    elif "feature" in categories:
        return f"v{major}.{minor + 1}.0"
    else:
        return f"v{major}.{minor}.{patch + 1}"
```

---

## Run It

```bash
python3 demos/task5_commit_analyzer.py
```

---

## What Success Looks Like

Given a git log like:
```
a1b2c3d: Add user search endpoint
d4e5f6a: Fix crash when email is null
b7c8d9e: Refactor auth middleware
e0f1a2b: Update API documentation
f3a4b5c: Remove deprecated /v1/users endpoint
```

The analyzer produces:
```markdown
# Release v2.0.0

## Highlights
This release adds user search, fixes a critical null pointer crash, and removes
the deprecated v1 users endpoint. Migration required for v1 API consumers.

## Features
- Add user search endpoint (a1b2c3d)

## Bug Fixes
- Fix crash when email field is null during auth (d4e5f6a)

## Breaking Changes
- Remove deprecated /v1/users endpoint — migrate to /v2/users (f3a4b5c)

## Other Changes
- Refactor auth middleware for clarity (b7c8d9e)
- Update API documentation (e0f1a2b)
```

Version suggestion: `v2.0.0` (breaking change detected).

---

## Key Takeaway

AI turns messy git history into professional release notes in seconds. The combination of categorization + generation means even teams with inconsistent commit messages get clean changelogs. The semantic version suggestion prevents the "is this a patch or minor?" debate on every release.

---

Next: [Lab 6: Full Pipeline](lab6-full-pipeline.md)
