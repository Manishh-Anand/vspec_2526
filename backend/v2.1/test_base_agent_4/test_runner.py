#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaFlow Automated Test Runner
Runs comprehensive test suite and aggregates results
"""

import subprocess
import time
from pathlib import Path
from datetime import datetime

# Test prompts covering different scenarios and complexities
TEST_PROMPTS = [
    # Simple (1-2 agents expected)
    "Search for the latest iPhone 15 price in India and email me",
    "Find today's weather forecast in Bangalore",
    "Look up the current Bitcoin price and send notification",

    # Medium (3-5 agents expected)
    "Research electric vehicles in India, summarize key findings, and email me the report",
    "Find AI news from the past week, analyze trends, and create a summary document",
    "Search for Python developer jobs in Bangalore with salary >15L and send top 5",
    "Get stock prices for top 5 tech companies, compare performance, and email analysis",

    # Complex (6+ agents expected)
    "Research AI automation tools, compare features and pricing, create comparison table, and present findings",
    "Search for machine learning research papers, summarize abstracts, categorize by topic, and email digest",
    "Find competitor analysis for AI startups, extract key metrics, create comprehensive report, and share via email"
]

def run_single_test(prompt: str, index: int, total: int) -> tuple:
    """
    Run a single test scenario
    Returns: (success: bool, duration: float, error_msg: str)
    """
    print(f"\n{'='*75}")
    print(f"TEST {index + 1}/{total}")
    print(f"{'='*75}")
    print(f"Prompt: {prompt}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 75)

    start_time = time.time()

    try:
        # Run the batch file with prompt as argument
        result = subprocess.run(
            ['run_metaflow.bat', prompt],
            cwd=str(Path(__file__).parent),
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            encoding='utf-8',
            errors='ignore'
        )

        duration = time.time() - start_time

        if result.returncode == 0:
            print(f"✓ PASSED ({duration:.1f}s)")
            print(f"{'='*75}\n")
            return (True, duration, "")
        else:
            error_msg = result.stderr[:200] if result.stderr else "Unknown error"
            print(f"✗ FAILED ({duration:.1f}s)")
            print(f"Error: {error_msg}")
            print(f"{'='*75}\n")
            return (False, duration, error_msg)

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"✗ TIMEOUT (>{duration:.0f}s)")
        print(f"{'='*75}\n")
        return (False, duration, "Timeout after 300 seconds")

    except Exception as e:
        duration = time.time() - start_time
        print(f"✗ ERROR ({duration:.1f}s)")
        print(f"Exception: {str(e)}")
        print(f"{'='*75}\n")
        return (False, duration, str(e))

def print_test_summary(results: list, total_time: float):
    """Print comprehensive test summary"""

    passed = sum(1 for r in results if r[0])
    failed = len(results) - passed
    success_rate = (passed / len(results) * 100) if results else 0
    avg_time = total_time / len(results) if results else 0

    print("\n" + "=" * 75)
    print(" " * 28 + "TEST SUITE SUMMARY")
    print("=" * 75)
    print(f"Total Tests:          {len(results)}")
    print(f"Passed:               {passed}")
    print(f"Failed:               {failed}")
    print(f"Success Rate:         {success_rate:.1f}%")
    print("-" * 75)
    print(f"Total Time:           {total_time:.1f}s ({total_time/60:.1f} minutes)")
    print(f"Avg Time per Test:    {avg_time:.1f}s")
    print(f"Fastest Test:         {min(r[1] for r in results):.1f}s")
    print(f"Slowest Test:         {max(r[1] for r in results):.1f}s")
    print("=" * 75)

    # Print failures if any
    if failed > 0:
        print("\nFailed Tests:")
        print("-" * 75)
        for i, (success, duration, error) in enumerate(results):
            if not success:
                print(f"  {i+1}. {TEST_PROMPTS[i][:60]}...")
                print(f"     Error: {error[:100]}")
        print("=" * 75)

    print()

def main():
    """Main test runner function"""

    print("\n" + "=" * 75)
    print(" " * 23 + "METAFLOW AUTOMATED TEST SUITE")
    print("=" * 75)
    print(f"Total test scenarios: {len(TEST_PROMPTS)}")
    print(f"Estimated time: {len(TEST_PROMPTS) * 2} minutes (avg 2 min/test)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 75 + "\n")

    results = []
    start_time = time.time()

    # Run all tests
    for i, prompt in enumerate(TEST_PROMPTS):
        result = run_single_test(prompt, i, len(TEST_PROMPTS))
        results.append(result)

        # Brief pause between tests
        if i < len(TEST_PROMPTS) - 1:
            time.sleep(2)

    total_time = time.time() - start_time

    # Print summary
    print_test_summary(results, total_time)

    # Run aggregation
    print("Running results aggregation...")
    print("-" * 75 + "\n")

    try:
        subprocess.run(
            ['python', 'aggregate_results.py'],
            cwd=str(Path(__file__).parent),
            timeout=30
        )
    except Exception as e:
        print(f"Warning: Could not run aggregation: {e}\n")

    print("\n" + "=" * 75)
    print(" " * 25 + "TEST SUITE COMPLETE")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    print("Starting MetaFlow test suite...")
    print("This will run 10 automated tests and may take 15-30 minutes.")
    print("Press Ctrl+C to cancel.\n")

    try:
        time.sleep(2)  # Give user time to read
        main()
    except KeyboardInterrupt:
        print("\n\nTest suite cancelled by user.\n")
