#!/usr/bin/env python3
"""
Prompt Testing Framework for DevOps
====================================

Building automated tests for prompts to catch regressions when
prompts are modified or models are updated. This framework enables
SRE teams to validate that prompt changes don't break expected
behavior in production workflows.

Prerequisites:
    - anthropic SDK: pip install anthropic
    - ANTHROPIC_API_KEY environment variable set

Usage:
    python task5_testing_framework.py
"""

import anthropic
import time
from dataclasses import dataclass, field
from typing import List, Callable


# ============================================================
# Data Models
# ============================================================

@dataclass
class PromptTestCase:
    name: str
    prompt: str
    expected_keywords: List[str]
    format_checks: List[Callable[[str], bool]] = field(default_factory=list)


@dataclass
class TestResult:
    test_name: str
    passed: bool
    keyword_score: float
    format_score: float
    missing_keywords: List[str]
    failed_format_checks: int
    response_snippet: str


# ============================================================
# Prompt Test Runner
# ============================================================

class PromptTestRunner:
    """Automated test runner for prompt regression testing."""

    def __init__(self, client: anthropic.Anthropic):
        self.client = client
        self.results: List[TestResult] = []

    def run_test(self, test_case: PromptTestCase) -> TestResult:
        """Run a single test case and return the result with scores."""
        print(f"\n  Running: {test_case.name}...")

        # Send prompt to Claude
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": test_case.prompt}]
        )
        result = message.content[0].text

        # Check for expected keywords (case-insensitive)
        result_lower = result.lower()
        found_keywords = []
        missing_keywords = []

        for keyword in test_case.expected_keywords:
            if keyword.lower() in result_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        keyword_score = len(found_keywords) / len(test_case.expected_keywords) if test_case.expected_keywords else 1.0

        # Run format checks
        format_passed = 0
        format_total = len(test_case.format_checks)

        for check in test_case.format_checks:
            if check(result):
                format_passed += 1

        format_score = format_passed / format_total if format_total > 0 else 1.0
        failed_format_checks = format_total - format_passed

        # Determine pass/fail (threshold: 80% keywords, 100% format)
        passed = keyword_score >= 0.8 and format_score == 1.0

        # Create snippet for display
        snippet = result[:120].replace("\n", " ") + "..." if len(result) > 120 else result.replace("\n", " ")

        test_result = TestResult(
            test_name=test_case.name,
            passed=passed,
            keyword_score=keyword_score,
            format_score=format_score,
            missing_keywords=missing_keywords,
            failed_format_checks=failed_format_checks,
            response_snippet=snippet
        )

        return test_result

    def run_suite(self, test_cases: List[PromptTestCase]) -> List[TestResult]:
        """Run all test cases and print results."""
        print("\n  Starting test suite execution...")
        print(f"  Total tests: {len(test_cases)}")
        self.results = []

        for test_case in test_cases:
            result = self.run_test(test_case)
            self.results.append(result)
            time.sleep(1)  # Rate limiting

        # Print results summary
        print("\n" + "-" * 65)
        print("  TEST RESULTS SUMMARY")
        print("-" * 65)

        passed_count = 0
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            if r.passed:
                passed_count += 1
            print(f"\n  [{status}] {r.test_name}")
            print(f"    Keyword Score: {r.keyword_score * 100:.1f}%")
            print(f"    Format Score:  {r.format_score * 100:.1f}%")
            if r.missing_keywords:
                print(f"    Missing Keywords: {', '.join(r.missing_keywords)}")
            if r.failed_format_checks > 0:
                print(f"    Failed Format Checks: {r.failed_format_checks}")
            print(f"    Response: {r.response_snippet}")

        print("\n" + "-" * 65)
        print(f"  Overall: {passed_count}/{len(self.results)} tests passed")
        print(f"  Suite Score: {(passed_count / len(self.results)) * 100:.1f}%")
        print("-" * 65)

        return self.results


# ============================================================
# Format Check Helper Functions
# ============================================================

def has_numbered_list(text: str) -> bool:
    """Check if response contains a numbered list."""
    import re
    return bool(re.search(r'\d+[\.\)]\s', text))


def has_bullet_points(text: str) -> bool:
    """Check if response contains bullet points."""
    return any(line.strip().startswith(('-', '*', '•')) for line in text.split('\n'))


def has_sections(text: str) -> bool:
    """Check if response contains section headers (markdown or uppercase)."""
    import re
    has_markdown_headers = bool(re.search(r'^#{1,3}\s', text, re.MULTILINE))
    has_uppercase_headers = bool(re.search(r'^[A-Z][A-Z\s]{3,}:', text, re.MULTILINE))
    return has_markdown_headers or has_uppercase_headers


def min_length(min_chars: int) -> Callable[[str], bool]:
    """Return a check function that verifies minimum response length."""
    def check(text: str) -> bool:
        return len(text) >= min_chars
    return check


def max_length(max_chars: int) -> Callable[[str], bool]:
    """Return a check function that verifies maximum response length."""
    def check(text: str) -> bool:
        return len(text) <= max_chars
    return check


# ============================================================
# Main Execution
# ============================================================

def main():
    print("=" * 65)
    print("  PROMPT TESTING FRAMEWORK FOR DEVOPS")
    print("  Automated Regression Testing for SRE Prompts")
    print("=" * 65)

    # Initialize client and runner
    client = anthropic.Anthropic()
    runner = PromptTestRunner(client)

    # ----------------------------------------------------------
    # Define Test Cases
    # ----------------------------------------------------------
    print("\n" + "=" * 65)
    print("  SECTION 1: Defining Test Cases")
    print("=" * 65)

    test_cases = [
        # Test 1: Incident Severity Classification
        PromptTestCase(
            name="Incident Severity Classification",
            prompt=(
                "You are an SRE incident commander. Classify the following incident "
                "by severity level (P1, P2, P3, or P4). Provide the classification "
                "and brief justification.\n\n"
                "Incident: The primary database cluster is experiencing 95% packet loss "
                "affecting all customer-facing services. Revenue-generating transactions "
                "are failing. Estimated impact: 100% of users."
            ),
            expected_keywords=["P1", "critical", "impact", "database", "users"],
            format_checks=[min_length(100), has_bullet_points]
        ),

        # Test 2: Kubernetes Troubleshooting
        PromptTestCase(
            name="Kubernetes Troubleshooting Commands",
            prompt=(
                "A Kubernetes pod named 'payment-service' in namespace 'production' "
                "is in CrashLoopBackOff. Provide the exact kubectl commands to "
                "diagnose this issue, in order of execution."
            ),
            expected_keywords=[
                "kubectl", "describe", "logs", "get pods",
                "namespace", "events"
            ],
            format_checks=[has_numbered_list, min_length(200)]
        ),

        # Test 3: Alert Runbook Generation
        PromptTestCase(
            name="Alert Runbook Generation",
            prompt=(
                "Generate a runbook for the alert 'HighMemoryUsage' that fires when "
                "a service exceeds 90% memory utilization for more than 5 minutes. "
                "Include sections for Symptoms, Diagnostic Steps, Remediation Steps, "
                "and Escalation procedures."
            ),
            expected_keywords=[
                "Symptoms", "Steps", "Escalation",
                "memory", "threshold", "restart"
            ],
            format_checks=[has_sections, min_length(300)]
        ),

        # Test 4: Root Cause Analysis
        PromptTestCase(
            name="Root Cause Analysis Template",
            prompt=(
                "Perform a root cause analysis for the following incident: "
                "An API gateway experienced a cascading failure after a deployment "
                "introduced a memory leak. The failure propagated to downstream "
                "services over 45 minutes before detection. Identify the root cause "
                "and contributing factors."
            ),
            expected_keywords=[
                "root cause", "contributing factors", "memory leak",
                "deployment", "detection", "cascading"
            ],
            format_checks=[has_sections, min_length(250)]
        ),

        # Test 5: Change Risk Assessment
        PromptTestCase(
            name="Change Risk Assessment",
            prompt=(
                "Assess the risk of the following change: Migrating the authentication "
                "service from a monolithic architecture to microservices during business "
                "hours. The service handles 50,000 requests per minute. Include risk level, "
                "potential impact, and rollback plan."
            ),
            expected_keywords=[
                "risk", "rollback", "impact", "authentication",
                "downtime", "mitigation"
            ],
            format_checks=[has_sections, has_bullet_points, min_length(200)]
        ),

        # Test 6: SLO Definition
        PromptTestCase(
            name="SLO Definition Generation",
            prompt=(
                "Define appropriate SLOs for a payment processing API that currently "
                "has 99.95% availability and p99 latency of 200ms. Include the SLI "
                "definitions, SLO targets, and error budget calculations."
            ),
            expected_keywords=[
                "SLO", "SLI", "error budget", "availability",
                "latency", "99"
            ],
            format_checks=[min_length(200), has_numbered_list]
        ),
    ]

    print(f"\n  Defined {len(test_cases)} test cases:")
    for i, tc in enumerate(test_cases, 1):
        print(f"    {i}. {tc.name}")
        print(f"       Keywords to check: {', '.join(tc.expected_keywords[:4])}...")
        print(f"       Format checks: {len(tc.format_checks)}")

    # ----------------------------------------------------------
    # Run Test Suite
    # ----------------------------------------------------------
    print("\n" + "=" * 65)
    print("  SECTION 2: Running Test Suite")
    print("=" * 65)

    results = runner.run_suite(test_cases)

    # ----------------------------------------------------------
    # Regression Detection Demo
    # ----------------------------------------------------------
    print("\n" + "=" * 65)
    print("  SECTION 3: Catching Regressions When Prompts Change")
    print("=" * 65)

    print("\n  Demonstrating how prompt changes can introduce regressions...")
    print("\n  Original prompt (Incident Severity Classification):")
    print("  -> Includes clear instruction to classify by P1/P2/P3/P4")

    # Original test case (already run above)
    original_result = results[0]
    print(f"\n  Original Result: {'PASS' if original_result.passed else 'FAIL'}")
    print(f"  Keyword Score: {original_result.keyword_score * 100:.1f}%")

    print("\n" + "-" * 65)
    print("  Running modified prompt (simulating a regression)...")
    print("-" * 65)

    # Modified prompt that might cause a regression
    regression_test = PromptTestCase(
        name="Incident Classification (MODIFIED - potential regression)",
        prompt=(
            "Briefly describe what happened with the database. "
            "Keep it to one sentence."
        ),
        expected_keywords=["P1", "critical", "impact", "database", "users"],
        format_checks=[min_length(100), has_bullet_points]
    )

    regression_result = runner.run_test(regression_test)

    print(f"\n  Modified Result: {'PASS' if regression_result.passed else 'FAIL'}")
    print(f"  Keyword Score: {regression_result.keyword_score * 100:.1f}%")
    print(f"  Format Score: {regression_result.format_score * 100:.1f}%")

    if not regression_result.passed and original_result.passed:
        print("\n  ** REGRESSION DETECTED! **")
        print("  The modified prompt no longer meets the test criteria.")
        print(f"  Missing keywords: {', '.join(regression_result.missing_keywords)}")
        print(f"  Failed format checks: {regression_result.failed_format_checks}")
    elif regression_result.passed:
        print("\n  No regression detected - modified prompt still passes.")
    else:
        print("\n  Both versions have issues - review test thresholds.")

    print("\n" + "-" * 65)
    print("  Regression Testing Best Practices:")
    print("-" * 65)
    print("""
  1. Version Control Prompts: Store prompts in version control alongside
     their test cases so changes are tracked together.

  2. CI/CD Integration: Run prompt tests in your deployment pipeline
     to catch regressions before they reach production.

  3. Baseline Snapshots: Keep baseline responses to compare against
     when models are updated or prompts are modified.

  4. Threshold Tuning: Set keyword thresholds based on historical
     pass rates (80% is a good starting point).

  5. Format Stability: Format checks catch structural regressions
     that keyword matching alone might miss.
    """)

    # ----------------------------------------------------------
    # Key Learning
    # ----------------------------------------------------------
    print("=" * 65)
    print("  Key Learning:")
    print("=" * 65)
    print("""
  Prompt testing is essential for production SRE workflows:

  - Define WHAT you expect (keywords, structure, format) before testing
  - Use automated suites to catch regressions when prompts change
  - Score responses quantitatively (keyword %, format checks)
  - Set pass/fail thresholds appropriate for your use case
  - Run tests in CI/CD to prevent broken prompts from deploying
  - Test both content accuracy AND response format consistency
  - Compare results across model versions to plan migrations
  - Treat prompts as code: version, review, test, and monitor them
    """)

    print("=" * 65)
    print("  Next: task6_anti_patterns.py")
    print("         Common prompt anti-patterns in DevOps and how to fix them")
    print("=" * 65)


if __name__ == "__main__":
    main()
