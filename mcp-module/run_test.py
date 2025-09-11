#!/usr/bin/env python3
"""
Simple test script for the MCP Module
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def main():
    """Test the MCP module"""
    
    # Define paths
    current_dir = Path(__file__).parent
    ba_op_path = current_dir.parent / "backend" / "v2.1" / "test_base_agent_4" / "BA_op (1).json"
    output_path = current_dir / "mcp_configuration_output.json"
    
    print(f"Input BA_op.json path: {ba_op_path}")
    print(f"Output MCP configuration path: {output_path}")
    
    # Check if input file exists
    if not ba_op_path.exists():
        print(f"ERROR: Input file not found: {ba_op_path}")
        return
    
    try:
        # Import and run the module
        from src.main import MCPModule
        
        # Initialize MCP Module
        mcp_module = MCPModule()
        print("MCP Module initialized successfully")
        
        # Process the BA_op.json file
        print("Processing BA_op.json file...")
        mcp_config = await mcp_module.process_ba_output(str(ba_op_path))
        
        # Write output to JSON file
        print("Writing MCP configuration to output file...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mcp_config, f, indent=2, ensure_ascii=False)
        
        print(f"MCP configuration written to: {output_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("MCP MODULE TEST COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Input file: {ba_op_path}")
        print(f"Output file: {output_path}")
        print(f"Output file size: {output_path.stat().st_size} bytes")
        
        # Print configuration summary
        if isinstance(mcp_config, dict):
            print(f"\nConfiguration Summary:")
            print(f"- Servers configured: {len(mcp_config.get('servers', []))}")
            print(f"- Bindings created: {len(mcp_config.get('bindings', []))}")
            print(f"- Execution plan steps: {len(mcp_config.get('execution_plan', []))}")
            
            # List configured servers
            servers = mcp_config.get('servers', [])
            if servers:
                print(f"\nConfigured Servers:")
                for server in servers:
                    print(f"  - {server.get('name', 'Unknown')} ({server.get('domain', 'Unknown')})")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    asyncio.run(main())
