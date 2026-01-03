import subprocess
import sys
import os
from pathlib import Path

def run_step(command, step_name):
    print(f"\n{'='*60}")
    print(f"STEP: {step_name}")
    print(f"COMMAND: {' '.join(command)}")
    print(f"{'='*60}\n")
    
    try:
        # Use shell=True for windows command compatibility if needed, but list format is safer generally.
        # However, for python scripts, direct execution is better.
        result = subprocess.run(command, check=True, text=True)
        print(f"\n[SUCCESS] {step_name} completed.")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] {step_name} failed with exit code {e.returncode}")
        sys.exit(e.returncode)

def main():
    base_dir = Path(__file__).parent.resolve()
    v2_1_dir = base_dir.parent.resolve()
    
    print(f"Base Directory: {base_dir}")
    print(f"v2.1 Directory: {v2_1_dir}")
    
    # Step 1: Process System Prompt (system_2_starMethod.py)
    # This script is in the parent directory (v2.1)
    # It reads System_prompt.py and writes star_m.py (both in v2.1)
    step1_script = v2_1_dir / "system_2_starMethod.py"
    run_step([sys.executable, str(step1_script)], "Process System Prompt -> STAR Format")
    
    # Step 2: Generate Workflow (base_agent_4.py)
    # This script is in the current directory (test_base_agent_4)
    # It reads from v2.1/System_prompt.py and v2.1/star_m.py
    # Outputs BA_op.json in current directory
    step2_script = base_dir / "base_agent_4.py"
    run_step([sys.executable, str(step2_script)], "Generate IO Operation (base_agent_4)")
    
    # Step 3: Map Tools (tool_mapper.py)
    # Maps tools in BA_op.json to BA_enhanced.json using Bright Data / MCP
    step3_script = base_dir / "tool_mapper.py"
    input_json = "BA_op.json"
    run_step([sys.executable, str(step3_script), input_json], "Map Tools (tool_mapper)")
    
    # Step 4: Execute Workflow (langgraph_workflow_builder.py)
    # Runs the agents
    step4_script = base_dir / "langgraph_workflow_builder.py"
    enhanced_json = "BA_enhanced.json"
    run_step([sys.executable, str(step4_script), enhanced_json], "Execute Workflow")
    
    print(f"\n{'='*60}")
    print("PROJECT PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
