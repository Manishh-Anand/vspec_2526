#!/usr/bin/env python3
"""
Debug script to test the agent tool function directly
"""

import asyncio
import sys
from pathlib import Path

# Add the agents_created directory to the path
sys.path.append(str(Path("agents_created").absolute()))

async def test_tool_directly():
    """Test the tool function directly to isolate the issue"""
    try:
        from agent_1 import UniversalAgent as Agent1
        
        print("Creating agent...")
        agent = Agent1()
        
        # Get the first tool
        if agent.tools:
            tool = agent.tools[0]
            print(f"Testing tool: {tool.name}")
            print(f"Tool description: {tool.description}")
            
            # Test the tool function directly
            print("Calling tool function directly...")
            result = tool.func("test input")
            print(f"Tool result: {result}")
        else:
            print("No tools found!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 Debug Agent Tool Function")
    print("=" * 40)
    asyncio.run(test_tool_directly())
