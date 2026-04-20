"""
Episode 8: AI-Powered CI/CD & GitOps
AI Code Review Agent

Reviews PRs with context-aware analysis.

Author: Sagar Utekar
Prerequisites:
    - Claude API key set as ANTHROPIC_API_KEY environment variable
    - GITHUB_TOKEN environment variable set
    - PR_NUMBER and REPO_NAME environment variables set (by GitHub Actions)
    - Python packages: anthropic, PyGithub (pip install anthropic PyGithub)
"""
import os
import subprocess
import anthropic
from github import Github

# Config
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
PR_NUMBER = int(os.environ["PR_NUMBER"])
REPO_NAME = os.environ["REPO_NAME"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
gh = Github(GITHUB_TOKEN)
repo = gh.get_repo(REPO_NAME)
pr = repo.get_pull(PR_NUMBER)

REVIEW_PROMPT = """You are a senior SRE reviewing a pull request for a Kubernetes-based production system.

## Review Checklist:
1. **Security** — Secrets exposed? Injection risks? Running as root? Excessive permissions?
2. **Reliability** — Error handling? Retries? Timeouts? Circuit breakers? Resource limits?
3. **Performance** — N+1 queries? Missing indexes? Unnecessary allocations? Cache misses?
4. **Kubernetes** — Health checks? Resource requests/limits? PDBs? Anti-affinity?
5. **Observability** — Logging? Metrics? Tracing? Alerting rules?
6. **IaC** — Terraform state safety? Blast radius? Cost impact?

## Output Format:
Start with a one-line summary verdict: APPROVE / REQUEST_CHANGES / COMMENT

Then for each finding:
### [CRITICAL/WARNING/INFO] — Brief title
**File:** `filename:line`
**Issue:** What's wrong
**Fix:** How to fix (with code if applicable)

Keep it concise. Only flag real issues, not style preferences."""

def get_diff():
    """Get the PR diff."""
    result = subprocess.run(
        ["git", "diff", f"origin/{pr.base.ref}...HEAD"],
        capture_output=True, text=True
    )
    return result.stdout

def get_changed_files():
    """Get list of changed files with their content."""
    files = []
    for f in pr.get_files():
        files.append({
            "filename": f.filename,
            "status": f.status,
            "additions": f.additions,
            "deletions": f.deletions,
            "patch": f.patch or ""
        })
    return files

def review_pr():
    diff = get_diff()
    files = get_changed_files()

    file_summary = "\n".join([
        f"  {f['status']:>10} {f['filename']} (+{f['additions']}/-{f['deletions']})"
        for f in files
    ])

    user_message = f"""## Pull Request: {pr.title}

**Description:** {pr.body or 'No description'}
**Author:** {pr.user.login}
**Base:** {pr.base.ref} <- {pr.head.ref}

### Changed Files:
{file_summary}

### Diff:
```diff
{diff[:50000]}
```

Review this PR following the checklist."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": REVIEW_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{"role": "user", "content": user_message}]
    )

    return response.content[0].text

def post_review(review_text: str):
    """Post the review as a PR comment."""
    # Determine review event
    first_line = review_text.strip().split('\n')[0].upper()
    if "APPROVE" in first_line and "REQUEST" not in first_line:
        event = "APPROVE"
    elif "REQUEST_CHANGES" in first_line:
        event = "REQUEST_CHANGES"
    else:
        event = "COMMENT"

    pr.create_review(
        body=f"## AI SRE Review\n\n{review_text}\n\n---\n*Reviewed by AI SRE Agent*",
        event=event
    )
    print(f"Review posted: {event}")

if __name__ == "__main__":
    print(f"Reviewing PR #{PR_NUMBER}: {pr.title}")
    review = review_pr()
    print(review)
    post_review(review)
