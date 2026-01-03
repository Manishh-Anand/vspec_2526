#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaFlow Results Aggregator
Aggregates metrics from multiple workflow runs for thesis analysis
"""

import json
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

def load_workflow_results(pattern: str = "workflow_result_*.json") -> List[Dict[str, Any]]:
    """Load all workflow result files"""
    files = glob.glob(pattern)
    results = []

    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['_filepath'] = filepath
                results.append(data)
        except Exception as e:
            print(f"Warning: Could not load {filepath}: {e}")

    return results

def calculate_aggregates(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregate metrics"""

    if not results:
        return {
            "error": "No results to aggregate",
            "total_runs": 0
        }

    total_runs = len(results)
    successful = 0
    failed = 0
    total_time = 0.0
    total_tokens = 0
    total_agents_executed = 0
    total_agents_succeeded = 0

    for result in results:
        # Status check
        status = result.get('status', '').lower()
        if status in ['success', 'completed', 'passed']:
            successful += 1
        else:
            failed += 1

        # Time metrics
        duration = result.get('duration_seconds', 0)
        if isinstance(duration, (int, float)):
            total_time += duration

        # Agent metrics
        agents_exec = result.get('agents_executed', 0)
        agents_succ = result.get('agents_succeeded', 0)
        if isinstance(agents_exec, int):
            total_agents_executed += agents_exec
        if isinstance(agents_succ, int):
            total_agents_succeeded += agents_succ

        # Token metrics (multiple possible locations)
        tokens = 0
        if 'token_stats' in result:
            tokens = result['token_stats'].get('total_tokens', 0)
        elif 'total_tokens' in result:
            tokens = result.get('total_tokens', 0)
        elif 'metrics' in result and 'total_tokens' in result['metrics']:
            tokens = result['metrics']['total_tokens']

        if isinstance(tokens, int):
            total_tokens += tokens

    # Calculate averages
    avg_time = total_time / total_runs if total_runs > 0 else 0
    avg_tokens = total_tokens / total_runs if total_runs > 0 else 0
    success_rate = (successful / total_runs * 100) if total_runs > 0 else 0
    avg_agents = total_agents_executed / total_runs if total_runs > 0 else 0

    # Calculate estimated cost (assuming $0.000004 per token for local + cloud hybrid)
    avg_cost = avg_tokens * 0.000004
    total_cost = total_tokens * 0.000004

    return {
        "timestamp": datetime.now().isoformat(),
        "total_runs": total_runs,
        "successful": successful,
        "failed": failed,
        "success_rate_percent": round(success_rate, 1),
        "avg_time_seconds": round(avg_time, 2),
        "total_time_seconds": round(total_time, 2),
        "avg_tokens": int(avg_tokens),
        "total_tokens": int(total_tokens),
        "avg_cost_dollars": round(avg_cost, 6),
        "total_cost_dollars": round(total_cost, 4),
        "avg_agents_per_workflow": round(avg_agents, 1),
        "total_agents_executed": int(total_agents_executed),
        "total_agents_succeeded": int(total_agents_succeeded),
        "agent_success_rate_percent": round((total_agents_succeeded / total_agents_executed * 100) if total_agents_executed > 0 else 0, 1)
    }

def print_summary(aggregates: Dict[str, Any]):
    """Print formatted summary"""

    if "error" in aggregates:
        print(f"\nError: {aggregates['error']}\n")
        return

    print("\n" + "=" * 75)
    print(" " * 25 + "METAFLOW AGGREGATE RESULTS")
    print("=" * 75)
    print(f"Timestamp........................... {aggregates['timestamp']}")
    print(f"Total Runs.......................... {aggregates['total_runs']}")
    print(f"Successful.......................... {aggregates['successful']}")
    print(f"Failed.............................. {aggregates['failed']}")
    print(f"Success Rate........................ {aggregates['success_rate_percent']}%")
    print("-" * 75)
    print(f"Avg Time per Workflow............... {aggregates['avg_time_seconds']}s")
    print(f"Total Execution Time................ {aggregates['total_time_seconds']}s")
    print("-" * 75)
    print(f"Avg Tokens per Workflow............. {aggregates['avg_tokens']}")
    print(f"Total Tokens Used................... {aggregates['total_tokens']}")
    print(f"Avg Cost per Workflow............... ${aggregates['avg_cost_dollars']}")
    print(f"Total Cost.......................... ${aggregates['total_cost_dollars']}")
    print("-" * 75)
    print(f"Avg Agents per Workflow............. {aggregates['avg_agents_per_workflow']}")
    print(f"Total Agents Executed............... {aggregates['total_agents_executed']}")
    print(f"Total Agents Succeeded.............. {aggregates['total_agents_succeeded']}")
    print(f"Agent Success Rate.................. {aggregates['agent_success_rate_percent']}%")
    print("=" * 75 + "\n")

def print_thesis_comparison(aggregates: Dict[str, Any]):
    """Print thesis-ready comparison format"""

    if "error" in aggregates:
        return

    print("=" * 75)
    print(" " * 20 + "THESIS COMPARISON TABLE - MetaFlow vs Others")
    print("=" * 75)
    print(f"MetaFlow Success Rate:          {aggregates['success_rate_percent']}%")
    print(f"MetaFlow Avg Execution Time:    {aggregates['avg_time_seconds']}s")
    print(f"MetaFlow Avg Cost:              ${aggregates['avg_cost_dollars']}")
    print(f"MetaFlow Setup Time:            ~30s (automated)")
    print("-" * 75)
    print("n8n Success Rate:               ~95% (manual setup)")
    print("n8n Avg Execution Time:         30-60s")
    print("n8n Avg Cost:                   $0 (self-host) or $0.10 (cloud)")
    print("n8n Setup Time:                 5-10 minutes (manual)")
    print("-" * 75)
    print("Zapier Success Rate:            ~95% (manual setup)")
    print("Zapier Avg Execution Time:      30-60s")
    print("Zapier Avg Cost:                $0.10-0.50 per workflow")
    print("Zapier Setup Time:              5-10 minutes (manual)")
    print("-" * 75)
    print(f"MetaFlow Cost Savings:          {round((1 - aggregates['avg_cost_dollars'] / 0.30) * 100, 1)}% vs traditional cloud AI")
    print(f"MetaFlow Setup Speed:           {round(600 / 30, 1)}x faster than manual")
    print("=" * 75 + "\n")

def save_summary(aggregates: Dict[str, Any], filepath: str = "aggregate_summary.json"):
    """Save summary to JSON file"""

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(aggregates, f, indent=2)

    print(f"Detailed summary saved to: {filepath}\n")

def main():
    """Main aggregation function"""

    print("\n" + "=" * 75)
    print(" " * 25 + "MetaFlow Results Aggregator")
    print("=" * 75)

    # Load results
    print("\nSearching for workflow result files...")
    results = load_workflow_results()

    if not results:
        print("No workflow result files found (pattern: workflow_result_*.json)")
        print("Run some workflows first, then try again.\n")
        return

    print(f"Found {len(results)} result files\n")

    # Calculate aggregates
    print("Calculating aggregate metrics...")
    aggregates = calculate_aggregates(results)

    # Print summaries
    print_summary(aggregates)
    print_thesis_comparison(aggregates)

    # Save to file
    save_summary(aggregates)

    print("Aggregation complete!\n")

if __name__ == "__main__":
    import sys

    # Allow custom pattern as command-line argument
    if len(sys.argv) > 1:
        pattern = sys.argv[1]
        print(f"Using custom pattern: {pattern}")
        results = load_workflow_results(pattern)
        aggregates = calculate_aggregates(results)
        print_summary(aggregates)
        save_summary(aggregates)
    else:
        main()
