# Lab 5: Building a Prompt Testing Framework

## Mission

Build a prompt testing framework — regression tests for your prompts. When you change a prompt, old behaviors should not break.

## Why This Matters

**Prompts are code. They need tests.**

Think about it: you would never ship a function without unit tests. You would never refactor a module without running the test suite. Yet most teams change prompts based on vibes — "this seems better" — with no systematic validation that existing behaviors still work.

The analogy is direct:

| Software Engineering | Prompt Engineering |
|---------------------|-------------------|
| Function | Prompt template |
| Unit test | Test case (input + expected output characteristics) |
| Test runner | Prompt test runner |
| CI pipeline | Automated prompt regression suite |
| Code coverage | Scenario coverage |

When you modify a severity classification prompt to handle a new edge case, you need confidence that the 15 existing cases still classify correctly. This lab builds that confidence systematically.

---

## Prerequisites

- Python 3.9+
- An LLM API key (OpenAI or similar) set as environment variable
- Basic understanding of prompt templates from previous labs

```bash
# Install dependencies
pip install openai dataclasses-json rich
```

---

## Step 1: Define the Test Case Structure

Every test case needs three things: an input, what you expect from the output, and how to score it.

Create a file called `prompt_test_framework.py`:

```python
"""
Prompt Testing Framework
Regression tests for prompts — because prompts are code.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from enum import Enum
import re
import json
import time


class TestResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


@dataclass
class PromptTestCase:
    """A single test case for a prompt.
    
    Attributes:
        name: Human-readable test name
        description: What this test validates
        prompt_template: The prompt template with {placeholders}
        input_variables: Variables to fill into the template
        validators: List of scoring functions that return (bool, str)
        tags: Optional tags for filtering (e.g., 'severity', 'runbook')
        timeout: Max seconds to wait for response
    """
    name: str
    description: str
    prompt_template: str
    input_variables: dict
    validators: list  # List of Callable[[str], tuple[bool, str]]
    tags: list = field(default_factory=list)
    timeout: int = 30

    def render_prompt(self) -> str:
        """Render the prompt template with input variables."""
        return self.prompt_template.format(**self.input_variables)


@dataclass
class TestCaseResult:
    """Result of running a single test case."""
    test_case: PromptTestCase
    result: TestResult
    llm_output: str
    validator_results: list  # List of (bool, str) tuples
    duration_seconds: float
    error_message: Optional[str] = None

    @property
    def passed_validators(self) -> int:
        return sum(1 for passed, _ in self.validator_results if passed)

    @property
    def total_validators(self) -> int:
        return len(self.validator_results)

    @property
    def score(self) -> float:
        if self.total_validators == 0:
            return 0.0
        return self.passed_validators / self.total_validators
```

---

## Step 2: Build Scoring Functions

Scoring functions are the assertions of prompt testing. Each one checks a specific characteristic of the output.

```python
# --- Scoring Functions (Validators) ---

def contains_keywords(keywords: list[str], case_sensitive: bool = False) -> Callable[[str], tuple[bool, str]]:
    """Check that output contains all specified keywords."""
    def validator(output: str) -> tuple[bool, str]:
        check_output = output if case_sensitive else output.lower()
        missing = []
        for kw in keywords:
            check_kw = kw if case_sensitive else kw.lower()
            if check_kw not in check_output:
                missing.append(kw)
        if missing:
            return (False, f"Missing keywords: {missing}")
        return (True, f"All keywords found: {keywords}")
    return validator


def excludes_keywords(keywords: list[str], case_sensitive: bool = False) -> Callable[[str], tuple[bool, str]]:
    """Check that output does NOT contain any of the specified keywords."""
    def validator(output: str) -> tuple[bool, str]:
        check_output = output if case_sensitive else output.lower()
        found = []
        for kw in keywords:
            check_kw = kw if case_sensitive else kw.lower()
            if check_kw in check_output:
                found.append(kw)
        if found:
            return (False, f"Unwanted keywords found: {found}")
        return (True, f"No unwanted keywords present")
    return validator


def matches_format(pattern: str) -> Callable[[str], tuple[bool, str]]:
    """Check that output matches a regex pattern."""
    def validator(output: str) -> tuple[bool, str]:
        if re.search(pattern, output, re.MULTILINE | re.DOTALL):
            return (True, f"Output matches pattern: {pattern}")
        return (False, f"Output does not match pattern: {pattern}")
    return validator


def has_sections(section_headers: list[str]) -> Callable[[str], tuple[bool, str]]:
    """Check that output contains expected section headers (markdown)."""
    def validator(output: str) -> tuple[bool, str]:
        missing = []
        for header in section_headers:
            # Check for markdown headers (##, ###) or bold text
            pattern = rf"(#{1,4}\s*{re.escape(header)}|\*\*{re.escape(header)}\*\*)"
            if not re.search(pattern, output, re.IGNORECASE):
                missing.append(header)
        if missing:
            return (False, f"Missing sections: {missing}")
        return (True, f"All sections present: {section_headers}")
    return validator


def length_between(min_chars: int, max_chars: int) -> Callable[[str], tuple[bool, str]]:
    """Check that output length is within expected range."""
    def validator(output: str) -> tuple[bool, str]:
        length = len(output)
        if length < min_chars:
            return (False, f"Output too short: {length} chars (min: {min_chars})")
        if length > max_chars:
            return (False, f"Output too long: {length} chars (max: {max_chars})")
        return (True, f"Length OK: {length} chars (range: {min_chars}-{max_chars})")
    return validator


def is_valid_json() -> Callable[[str], tuple[bool, str]]:
    """Check that output is valid JSON."""
    def validator(output: str) -> tuple[bool, str]:
        try:
            # Try to extract JSON from markdown code blocks first
            json_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", output, re.DOTALL)
            if json_match:
                json.loads(json_match.group(1))
            else:
                json.loads(output)
            return (True, "Valid JSON output")
        except json.JSONDecodeError as e:
            return (False, f"Invalid JSON: {e}")
    return validator


def json_has_keys(required_keys: list[str]) -> Callable[[str], tuple[bool, str]]:
    """Check that JSON output contains required keys."""
    def validator(output: str) -> tuple[bool, str]:
        try:
            json_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", output, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                data = json.loads(output)
            
            missing = [k for k in required_keys if k not in data]
            if missing:
                return (False, f"Missing JSON keys: {missing}")
            return (True, f"All required keys present: {required_keys}")
        except json.JSONDecodeError:
            return (False, "Cannot check keys — invalid JSON")
    return validator


def severity_is_valid() -> Callable[[str], tuple[bool, str]]:
    """Check that a severity classification is one of the valid levels."""
    valid_severities = ["critical", "high", "medium", "low", "info"]
    def validator(output: str) -> tuple[bool, str]:
        output_lower = output.lower()
        for sev in valid_severities:
            if sev in output_lower:
                return (True, f"Valid severity found: {sev}")
        return (False, f"No valid severity level found. Expected one of: {valid_severities}")
    return validator
```

---

## Step 3: Build the Test Runner

The test runner orchestrates execution, handles errors, and collects results.

```python
import os
from openai import OpenAI


class PromptTestRunner:
    """Runs prompt test cases against an LLM and reports results."""

    def __init__(self, model: str = "gpt-4", temperature: float = 0.0):
        """Initialize the test runner.
        
        Args:
            model: The LLM model to use
            temperature: LLM temperature (0.0 for deterministic testing)
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.temperature = temperature
        self.results: list[TestCaseResult] = []

    def _call_llm(self, prompt: str, timeout: int) -> str:
        """Call the LLM with the rendered prompt."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=2000,
            timeout=timeout,
        )
        return response.choices[0].message.content

    def run_test(self, test_case: PromptTestCase) -> TestCaseResult:
        """Run a single test case and return the result."""
        start_time = time.time()
        
        try:
            # Render and send the prompt
            rendered_prompt = test_case.render_prompt()
            llm_output = self._call_llm(rendered_prompt, test_case.timeout)
            
            # Run all validators
            validator_results = []
            for validator in test_case.validators:
                try:
                    result = validator(llm_output)
                    validator_results.append(result)
                except Exception as e:
                    validator_results.append((False, f"Validator error: {e}"))
            
            # Determine overall result
            all_passed = all(passed for passed, _ in validator_results)
            duration = time.time() - start_time
            
            return TestCaseResult(
                test_case=test_case,
                result=TestResult.PASS if all_passed else TestResult.FAIL,
                llm_output=llm_output,
                validator_results=validator_results,
                duration_seconds=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestCaseResult(
                test_case=test_case,
                result=TestResult.ERROR,
                llm_output="",
                validator_results=[],
                duration_seconds=duration,
                error_message=str(e),
            )

    def run_suite(self, test_cases: list[PromptTestCase], tags: Optional[list[str]] = None) -> list[TestCaseResult]:
        """Run a suite of test cases, optionally filtered by tags.
        
        Args:
            test_cases: List of test cases to run
            tags: If provided, only run tests matching these tags
        """
        self.results = []
        
        # Filter by tags if specified
        if tags:
            filtered = [tc for tc in test_cases if any(t in tc.tags for t in tags)]
        else:
            filtered = test_cases

        print(f"\n{'='*60}")
        print(f"  PROMPT TEST SUITE")
        print(f"  Running {len(filtered)} test(s) | Model: {self.model}")
        print(f"{'='*60}\n")

        for i, test_case in enumerate(filtered, 1):
            print(f"  [{i}/{len(filtered)}] {test_case.name}...", end=" ", flush=True)
            result = self.run_test(test_case)
            self.results.append(result)
            
            # Print result indicator
            if result.result == TestResult.PASS:
                print(f"PASS ({result.duration_seconds:.1f}s)")
            elif result.result == TestResult.FAIL:
                print(f"FAIL ({result.duration_seconds:.1f}s)")
                for passed, msg in result.validator_results:
                    if not passed:
                        print(f"         -> {msg}")
            else:
                print(f"ERROR ({result.duration_seconds:.1f}s)")
                print(f"         -> {result.error_message}")

        self._print_summary()
        return self.results

    def _print_summary(self):
        """Print a summary of all test results."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.result == TestResult.PASS)
        failed = sum(1 for r in self.results if r.result == TestResult.FAIL)
        errors = sum(1 for r in self.results if r.result == TestResult.ERROR)
        
        print(f"\n{'='*60}")
        print(f"  RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"  Total:  {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Errors: {errors}")
        print(f"  Score:  {passed}/{total} ({(passed/total*100):.1f}%)" if total > 0 else "  Score:  N/A")
        print(f"{'='*60}")
        
        if failed > 0 or errors > 0:
            print(f"\n  FAILED TESTS:")
            for r in self.results:
                if r.result in (TestResult.FAIL, TestResult.ERROR):
                    print(f"    - {r.test_case.name}: {r.result.value}")
            print()
```

---

## Step 4: Define Test Cases for SRE Prompts

Now we define actual test cases for the prompts we use in production.

```python
# --- SRE Prompt Templates ---

SEVERITY_CLASSIFICATION_PROMPT = """You are an SRE severity classifier. Given the following alert, classify its severity level.

Alert: {alert_description}
Service: {service_name}
Impact: {impact_description}

Respond with a JSON object containing:
- "severity": one of "critical", "high", "medium", "low", "info"
- "reasoning": brief explanation of your classification
- "recommended_action": immediate action to take

Respond ONLY with the JSON object, no additional text."""


RUNBOOK_GENERATION_PROMPT = """You are an SRE runbook generator. Create a concise runbook for the following incident type.

Incident Type: {incident_type}
Service: {service_name}
Environment: {environment}

The runbook must include these sections:
## Overview
## Detection
## Diagnosis Steps
## Remediation
## Verification
## Escalation

Keep each section focused and actionable. Use numbered steps where appropriate."""


INCIDENT_SUMMARY_PROMPT = """Summarize the following incident for a post-incident review.

Timeline:
{timeline}

Impact:
{impact}

Provide a structured summary with:
- **Incident Title**: A concise title
- **Duration**: Total time from detection to resolution
- **Root Cause**: One-sentence root cause
- **Impact Summary**: Who/what was affected
- **Key Lessons**: 2-3 bullet points

Keep the summary under 300 words."""


# --- Test Cases ---

severity_test_cases = [
    PromptTestCase(
        name="severity_critical_database_down",
        description="Production database completely down should be CRITICAL",
        prompt_template=SEVERITY_CLASSIFICATION_PROMPT,
        input_variables={
            "alert_description": "PostgreSQL primary node is unreachable. All connections failing.",
            "service_name": "payment-service",
            "impact_description": "All payment processing halted. Revenue impact: $50K/minute.",
        },
        validators=[
            is_valid_json(),
            json_has_keys(["severity", "reasoning", "recommended_action"]),
            contains_keywords(["critical"]),
            excludes_keywords(["low", "info"]),
            length_between(100, 1000),
        ],
        tags=["severity", "critical"],
    ),
    PromptTestCase(
        name="severity_high_latency_spike",
        description="Significant latency spike affecting users should be HIGH",
        prompt_template=SEVERITY_CLASSIFICATION_PROMPT,
        input_variables={
            "alert_description": "API response time p99 exceeded 5s for 10 minutes",
            "service_name": "api-gateway",
            "impact_description": "30% of requests timing out. User-facing degradation.",
        },
        validators=[
            is_valid_json(),
            json_has_keys(["severity", "reasoning", "recommended_action"]),
            contains_keywords(["high"]),
            excludes_keywords(["info"]),
            length_between(100, 1000),
        ],
        tags=["severity", "high"],
    ),
    PromptTestCase(
        name="severity_low_disk_warning",
        description="Non-critical disk space warning should be LOW",
        prompt_template=SEVERITY_CLASSIFICATION_PROMPT,
        input_variables={
            "alert_description": "Disk usage on log volume reached 70%",
            "service_name": "log-aggregator",
            "impact_description": "No immediate impact. Log rotation scheduled in 6 hours.",
        },
        validators=[
            is_valid_json(),
            json_has_keys(["severity", "reasoning", "recommended_action"]),
            contains_keywords(["low"]),
            excludes_keywords(["critical"]),
            length_between(100, 1000),
        ],
        tags=["severity", "low"],
    ),
    PromptTestCase(
        name="severity_medium_replica_lag",
        description="Database replica lag should be MEDIUM",
        prompt_template=SEVERITY_CLASSIFICATION_PROMPT,
        input_variables={
            "alert_description": "Read replica lag exceeded 30 seconds",
            "service_name": "user-service",
            "impact_description": "Read queries may return stale data. Write path unaffected.",
        },
        validators=[
            is_valid_json(),
            json_has_keys(["severity", "reasoning", "recommended_action"]),
            contains_keywords(["medium"]),
            excludes_keywords(["critical"]),
            length_between(100, 1000),
        ],
        tags=["severity", "medium"],
    ),
]

runbook_test_cases = [
    PromptTestCase(
        name="runbook_memory_leak",
        description="Memory leak runbook should have all required sections",
        prompt_template=RUNBOOK_GENERATION_PROMPT,
        input_variables={
            "incident_type": "Memory leak causing OOM kills",
            "service_name": "recommendation-engine",
            "environment": "production",
        },
        validators=[
            has_sections(["Overview", "Detection", "Diagnosis Steps", "Remediation", "Verification", "Escalation"]),
            contains_keywords(["memory", "OOM", "restart"]),
            length_between(500, 5000),
        ],
        tags=["runbook"],
    ),
    PromptTestCase(
        name="runbook_certificate_expiry",
        description="TLS certificate expiry runbook should include renewal steps",
        prompt_template=RUNBOOK_GENERATION_PROMPT,
        input_variables={
            "incident_type": "TLS certificate expiring within 24 hours",
            "service_name": "api-gateway",
            "environment": "production",
        },
        validators=[
            has_sections(["Overview", "Detection", "Diagnosis Steps", "Remediation", "Verification", "Escalation"]),
            contains_keywords(["certificate", "renew"]),
            length_between(500, 5000),
        ],
        tags=["runbook"],
    ),
    PromptTestCase(
        name="runbook_pod_crashloop",
        description="Kubernetes CrashLoopBackOff runbook should reference kubectl",
        prompt_template=RUNBOOK_GENERATION_PROMPT,
        input_variables={
            "incident_type": "Pods in CrashLoopBackOff state",
            "service_name": "checkout-service",
            "environment": "production",
        },
        validators=[
            has_sections(["Overview", "Detection", "Diagnosis Steps", "Remediation", "Verification", "Escalation"]),
            contains_keywords(["kubectl", "logs", "CrashLoopBackOff"]),
            length_between(500, 5000),
        ],
        tags=["runbook"],
    ),
]

incident_summary_test_cases = [
    PromptTestCase(
        name="incident_summary_format",
        description="Incident summary should have all required sections",
        prompt_template=INCIDENT_SUMMARY_PROMPT,
        input_variables={
            "timeline": "14:00 - Alert fired for high error rate\n14:05 - On-call acknowledged\n14:15 - Root cause identified: bad config deploy\n14:20 - Config rolled back\n14:25 - Services recovering\n14:35 - All clear",
            "impact": "Payment processing failed for 35 minutes. ~2000 transactions affected. Revenue impact estimated at $150K.",
        },
        validators=[
            contains_keywords(["Incident Title", "Duration", "Root Cause", "Impact Summary", "Key Lessons"]),
            contains_keywords(["config"]),
            length_between(200, 2000),
        ],
        tags=["incident", "summary"],
    ),
]
```

---

## Step 5: Create the Command-Line Interface

Make the framework runnable from the command line with tag filtering and output options.

```python
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Prompt Testing Framework - Regression tests for prompts"
    )
    parser.add_argument(
        "--tags",
        nargs="+",
        help="Only run tests matching these tags",
    )
    parser.add_argument(
        "--model",
        default="gpt-4",
        help="LLM model to use (default: gpt-4)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="LLM temperature (default: 0.0 for deterministic output)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show full LLM outputs for failed tests",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Combine all test cases
    all_test_cases = (
        severity_test_cases
        + runbook_test_cases
        + incident_summary_test_cases
    )

    # Initialize runner and execute
    runner = PromptTestRunner(model=args.model, temperature=args.temperature)
    results = runner.run_suite(all_test_cases, tags=args.tags)

    # Verbose output for failures
    if args.verbose:
        failed = [r for r in results if r.result != TestResult.PASS]
        if failed:
            print("\n" + "="*60)
            print("  DETAILED FAILURE OUTPUT")
            print("="*60)
            for r in failed:
                print(f"\n  Test: {r.test_case.name}")
                print(f"  Output (first 500 chars):")
                print(f"  {r.llm_output[:500]}")
                print(f"  ---")

    # JSON output for CI integration
    if args.output == "json":
        output_data = {
            "model": args.model,
            "total": len(results),
            "passed": sum(1 for r in results if r.result == TestResult.PASS),
            "failed": sum(1 for r in results if r.result == TestResult.FAIL),
            "errors": sum(1 for r in results if r.result == TestResult.ERROR),
            "results": [
                {
                    "name": r.test_case.name,
                    "result": r.result.value,
                    "score": r.score,
                    "duration": r.duration_seconds,
                }
                for r in results
            ],
        }
        print(json.dumps(output_data, indent=2))

    # Exit with non-zero code if any test failed (for CI)
    if any(r.result != TestResult.PASS for r in results):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## Step 6: Run the Test Suite

```bash
# Run all tests
python prompt_test_framework.py

# Run only severity classification tests
python prompt_test_framework.py --tags severity

# Run runbook tests with verbose output
python prompt_test_framework.py --tags runbook --verbose

# Run with a different model
python prompt_test_framework.py --model gpt-3.5-turbo

# Output JSON for CI pipeline integration
python prompt_test_framework.py --output json > test_results.json

# Run in CI (non-zero exit code on failure)
python prompt_test_framework.py || echo "Prompt tests failed!"
```

### Example Output

```
============================================================
  PROMPT TEST SUITE
  Running 8 test(s) | Model: gpt-4
============================================================

  [1/8] severity_critical_database_down... PASS (2.3s)
  [2/8] severity_high_latency_spike... PASS (1.8s)
  [3/8] severity_low_disk_warning... PASS (1.9s)
  [4/8] severity_medium_replica_lag... PASS (2.1s)
  [5/8] runbook_memory_leak... PASS (4.2s)
  [6/8] runbook_certificate_expiry... PASS (3.8s)
  [7/8] runbook_pod_crashloop... FAIL (3.5s)
         -> Missing keywords: ['CrashLoopBackOff']
  [8/8] incident_summary_format... PASS (2.4s)

============================================================
  RESULTS SUMMARY
============================================================
  Total:  8
  Passed: 7
  Failed: 1
  Errors: 0
  Score:  7/8 (87.5%)
============================================================

  FAILED TESTS:
    - runbook_pod_crashloop: FAIL
```

---

## Step 7: Integrate with CI/CD

Add prompt tests to your pipeline so prompt changes go through the same rigor as code changes.

```yaml
# .github/workflows/prompt-tests.yml
name: Prompt Regression Tests

on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'prompt_test_framework.py'

jobs:
  prompt-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install openai dataclasses-json rich

      - name: Run prompt test suite
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python prompt_test_framework.py --output json > results.json
          python prompt_test_framework.py

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: prompt-test-results
          path: results.json
```

---

## What Success Looks Like

After completing this lab, you should be able to:

1. **Define test cases declaratively** — Each test case specifies inputs, expected output characteristics, and scoring functions without hard-coding exact outputs.

2. **Run regression tests before deploying prompt changes** — A single command tells you whether your prompt modification broke existing behavior.

3. **Integrate prompt testing into CI** — Prompt changes trigger automated tests just like code changes trigger unit tests.

4. **Score outputs on multiple dimensions** — Format, content, length, and structure are all validated independently, giving you granular failure information.

5. **Filter and organize tests by tags** — Run only the tests relevant to the prompt you changed, or run the full suite before release.

6. **Get deterministic, reproducible results** — Temperature 0.0 and structured validators mean results are consistent across runs.

Your framework should catch regressions like:
- A severity prompt that starts classifying "critical" alerts as "high" after a template edit
- A runbook prompt that drops required sections when you add new context
- An incident summary that exceeds length limits after adding more instructions

---

## Key Takeaway

**If you cannot test a prompt change, you cannot safely deploy it.**

Prompt testing is not optional tooling for advanced teams — it is the baseline for operating LLM-powered systems in production. The framework you built in this lab is minimal by design. In production, you would extend it with:

- **Semantic similarity scoring** (embeddings-based comparison to reference outputs)
- **LLM-as-judge** (using a second model to evaluate the first model's output)
- **Statistical testing** (running each test N times and checking pass rates)
- **A/B comparison** (testing a new prompt against the current production prompt)
- **Cost tracking** (measuring token usage per test run)

But the core principle remains: prompts are code, and code needs tests. Start with keyword checks and format validation. Graduate to semantic scoring as your prompts mature. Never ship a prompt change without running the suite.

---

**Next:** [Lab 6: Prompt Anti-Patterns](lab6-anti-patterns.md) — Common mistakes that make prompts fragile, expensive, or dangerous in production systems.
