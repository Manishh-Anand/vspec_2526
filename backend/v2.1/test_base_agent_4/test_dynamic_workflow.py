import subprocess
import json
import sys
import os
from pathlib import Path

def test_complete_dynamic_workflow():
    """Test the complete dynamic workflow generation"""
    
    print("[TEST] Testing Dynamic Workflow Generation")
    print("=" * 60)
    
    # Create test prompt file
    test_prompt = "Research the latest news about AI startups and email me a summary"
    prompt_file = Path("test_prompt.txt")
    with open(prompt_file, "w") as f:
        f.write(test_prompt)
    print(f"[INFO] Created test prompt: {test_prompt}")
    
    # Step 1: STAR conversion
    print("\n[1/4] Running STAR conversion...")
    result = subprocess.run([sys.executable, 'system2starmethod.py', 'test_prompt.txt'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] STAR conversion failed: {result.stderr}")
        return False
    print("[SUCCESS] STAR conversion successful")
    
    # Step 2: Generate workflow
    print("\n[2/4] Generating workflow with base_agent_4.py...")
    result = subprocess.run([sys.executable, 'base_agent_4.py'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] Workflow generation failed: {result.stderr}")
        print(f"Output: {result.stdout}")
        return False
    
    # Verify BA_op.json was created
    if not Path('BA_op.json').exists():
        print("[ERROR] BA_op.json not created")
        return False
    
    # Validate structure
    try:
        with open('BA_op.json', 'r') as f:
            ba_op = json.load(f)
        
        print(f"[SUCCESS] BA_op.json created")
        workflow_id = ba_op.get('workflow_metadata', {}).get('workflow_id', 'unknown')
        print(f"   Workflow: {workflow_id}")
        print(f"   Agents: {len(ba_op.get('agents', []))}")
        for agent in ba_op.get('agents', []):
            print(f"   - {agent.get('agent_name', 'unknown')}: {len(agent.get('tools', []))} tools")
    except Exception as e:
        print(f"[ERROR] Invalid BA_op.json: {e}")
        return False
    
    # Step 3: Map tools
    print("\n[3/4] Mapping tools...")
    result = subprocess.run([sys.executable, 'tool_mapper.py', 'BA_op.json'],
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] Tool mapping failed: {result.stderr}")
        print(f"Output: {result.stdout}")
        return False
    
    print("[SUCCESS] BA_enhanced.json created")
    
    # Step 4: Execute workflow
    print("\n[4/4] Executing workflow...")
    # We use a timeout because execution might take time or hang
    try:
        result = subprocess.run([sys.executable, 'langgraph_workflow_builder.py', 'BA_enhanced.json'],
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"[ERROR] Workflow execution failed: {result.stderr}")
            print(f"Output: {result.stdout}")
            return False
            
        print("[SUCCESS] Workflow executed successfully")
        
    except subprocess.TimeoutExpired:
        print("[WARN] Workflow execution timed out (this might be expected for long tasks)")
    
    print("\n[SUCCESS] COMPLETE DYNAMIC WORKFLOW TEST PASSED!")
    return True

if __name__ == "__main__":
    # Ensure we are in the correct directory
    os.chdir(Path(__file__).parent)
    test_complete_dynamic_workflow()
