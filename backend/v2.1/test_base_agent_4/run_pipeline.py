#!/usr/bin/env python3
"""
MetaFlow Complete Pipeline Runner
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run command and handle errors"""
    print(f"\n{'='*70}")
    print(f"[STEP] {description}")
    print(f"{'='*70}")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"\n[ERROR] {description} failed!")
        sys.exit(1)
    
    print(f"[SUCCESS] {description} completed")
    return result

def main():
    print("\n" + "="*70)
    print(" "*20 + "METAFLOW COMPLETE PIPELINE")
    print("="*70 + "\n")
    
    # Step 1: STAR Conversion
    run_command(
        "python system_2_starMethod.py",
        "Step 1/4: STAR Conversion"
    )
    
    # Step 2: Workflow Generation
    run_command(
        "python base_agent_4.py",
        "Step 2/4: Workflow Generation"
    )
    
    # Step 3: Tool Mapping
    run_command(
        "python tool_mapper.py BA_op.json",
        "Step 3/4: Tool Mapping"
    )
    
    # Step 4: Workflow Execution
    run_command(
        "python langgraph_workflow_builder.py BA_enhanced.json",
        "Step 4/4: Workflow Execution"
    )
    
    print("\n" + "="*70)
    print(" "*20 + "PIPELINE COMPLETE!")
    print("="*70)
    print("\n[INFO] Check workflow_result_*.json for results\n")

if __name__ == "__main__":
    main()