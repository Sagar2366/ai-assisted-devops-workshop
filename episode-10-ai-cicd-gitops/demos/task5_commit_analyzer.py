#!/usr/bin/env python3
"""
Task 5: AI Commit Analyzer
============================
Parses git log output, categorizes commits by type (feature/fix/refactor/docs),
generates structured release notes, and suggests semantic versioning.

Usage:
    export ANTHROPIC_API_KEY="your-key"
    python3 task5_commit_analyzer.py
"""

import anthropic
import json


def parse_git_log(raw_log):
    """Parse git log formatted output into structured commits."""
    commits = []
    for line in raw_log.strip().split("\n"):
        if "|" in line:
            parts = line.split("|", 3)
            commits.append({
                "hash": parts[0].strip()[:8],
                "author": parts[1].strip(),
                "message": parts[2].strip(),
                "date": parts[3].strip() if len(parts) > 3 else "unknown"
            })
    return commits


def categorize_commits(client, commits):
    """Use Claude to categorize commits by type."""
    commit_list = "\n".join(
        f"- {c['hash']}: {c['message']}" for c in commits
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="""You are a release engineer categorizing git commits.

For each commit, assign exactly ONE category:
- feature: New functionality added
- fix: Bug fix or crash fix
- refactor: Code restructuring without behavior change
- docs: Documentation only changes
- perf: Performance improvement
- breaking: Breaking change (API removal, schema migration)
- chore: Build system, CI, dependency updates

Return a valid JSON array:
[{"hash": "abc12345", "category": "feature", "description": "Clean one-line description for changelog"}]

Rules:
- "fix typo in README" is docs, not fix
- "update deps" or "bump version" is chore
- "Add retry logic" or "implement X" is feature
- "Remove deprecated endpoint" is breaking
- Infer intent from the message even if poorly written""",
        messages=[
            {"role": "user", "content": f"Categorize these commits:\n\n{commit_list}"}
        ]
    )
    return message.content[0].text


def suggest_version(current_version, categories):
    """Suggest next semantic version based on commit categories."""
    parts = current_version.lstrip("v").split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if "breaking" in categories:
        return f"v{major + 1}.0.0"
    elif "feature" in categories:
        return f"v{major}.{minor + 1}.0"
    else:
        return f"v{major}.{minor}.{patch + 1}"


def generate_release_notes(client, categorized_json, version):
    """Generate formatted release notes from categorized commits."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="""Generate professional release notes in Markdown format:

# Release vX.Y.Z

## Highlights
(2-3 sentence summary of the most important changes)

## Features
- Description (hash)

## Bug Fixes
- Description (hash)

## Breaking Changes
- Description with migration note (hash)

## Other Changes
- Refactors, docs, perf, chores grouped here (hash)

---
Contributors: list unique authors

Rules:
- Omit empty sections entirely
- Write descriptions for end users, not developers
- Breaking changes MUST include migration guidance
- Keep each item to one line""",
        messages=[
            {"role": "user", "content": f"Generate release notes for {version} from:\n\n{categorized_json}"}
        ]
    )
    return message.content[0].text


def main():
    print("=" * 65)
    print("  TASK 5: AI COMMIT ANALYZER")
    print("  Categorize commits and generate structured release notes")
    print("=" * 65)

    # ─── Simulated Git Log ───────────────────────────────────────────
    # Format: hash|author|message|date
    raw_git_log = """a1b2c3d4|Alice Chen|Add user search API endpoint with pagination|2024-03-15
d4e5f6a7|Bob Kumar|Fix null pointer when email field is empty during OAuth|2024-03-14
b7c8d9e0|Alice Chen|Refactor authentication middleware for clarity|2024-03-13
e0f1a2b3|Charlie Park|Update API documentation for v2 endpoints|2024-03-12
f3a4b5c6|Alice Chen|Remove deprecated /v1/users endpoint|2024-03-11
c6d7e8f9|Bob Kumar|Add request rate limiting to public APIs|2024-03-10
a9b0c1d2|Diana Lee|Optimize database queries for user listing|2024-03-09
b2c3d4e5|Charlie Park|Add retry logic with exponential backoff|2024-03-08
e5f6a7b8|Bob Kumar|Fix race condition in session cleanup|2024-03-07
f8a9b0c1|Diana Lee|Update Go dependencies to latest patch versions|2024-03-06"""

    commits = parse_git_log(raw_git_log)
    current_version = "v1.4.2"

    print(f"\n  Current version: {current_version}")
    print(f"  Commits since last release: {len(commits)}")

    print("\n" + "-" * 65)
    print("  RAW COMMITS")
    print("-" * 65)
    for c in commits:
        print(f"  {c['hash']} | {c['author']:<14} | {c['message']}")

    # ─── AI Categorization ───────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  CATEGORIZING COMMITS...")
    print("-" * 65)

    client = anthropic.Anthropic()
    categorized_raw = categorize_commits(client, commits)

    print(categorized_raw)

    # ─── Parse categories for version suggestion ─────────────────────
    try:
        # Try to extract JSON from the response
        json_match = categorized_raw
        if "```" in categorized_raw:
            json_match = categorized_raw.split("```")[1]
            if json_match.startswith("json"):
                json_match = json_match[4:]
        categorized = json.loads(json_match)
        all_categories = set(c.get("category", "chore") for c in categorized)
    except (json.JSONDecodeError, IndexError):
        # Fallback: infer from raw text
        all_categories = set()
        for keyword in ["feature", "fix", "breaking", "refactor", "docs", "perf", "chore"]:
            if keyword in categorized_raw.lower():
                all_categories.add(keyword)

    # ─── Version Suggestion ──────────────────────────────────────────
    suggested_version = suggest_version(current_version, all_categories)

    print("\n" + "-" * 65)
    print("  VERSION ANALYSIS")
    print("-" * 65)
    print(f"  Categories found: {', '.join(sorted(all_categories))}")
    print(f"  Current version:  {current_version}")
    print(f"  Suggested next:   {suggested_version}")

    if "breaking" in all_categories:
        print("  Reason: BREAKING CHANGE detected -> MAJOR bump")
    elif "feature" in all_categories:
        print("  Reason: New features detected -> MINOR bump")
    else:
        print("  Reason: Fixes/maintenance only -> PATCH bump")

    # ─── Generate Release Notes ──────────────────────────────────────
    print("\n" + "-" * 65)
    print("  GENERATING RELEASE NOTES...")
    print("-" * 65)

    release_notes = generate_release_notes(client, categorized_raw, suggested_version)

    print("\n" + "=" * 65)
    print("  RELEASE NOTES")
    print("=" * 65)
    print(release_notes)

    # ─── Summary ─────────────────────────────────────────────────────
    print("\n" + "-" * 65)
    print("  Key Learning:")
    print("  AI turns messy git history into professional release notes by")
    print("  understanding intent behind commit messages. Combined with")
    print("  semantic versioning rules, it automates the entire release")
    print("  documentation process — no more manual changelog writing.")
    print("-" * 65)
    print("  Next: python3 task6_full_pipeline.py")
    print("-" * 65)


if __name__ == "__main__":
    main()
