#!/usr/bin/env python3
"""
Test Transport Layer
Simple test to verify transport layer functionality
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from transport.base import TransportConfig, TransportType
from transport.stdio import StdioTransport
from core.protocol import MCPProtocol

async def test_stdio_transport():
    """Test stdio transport with simple server"""
    print("Testing stdio transport...")
    
    # Get the path to the test server
    server_path = Path(__file__).parent / "test_simple_server.py"
    
    try:
        # Create transport config
        config = TransportConfig(
            type=TransportType.STDIO
        )
        
        # Start the server process
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(server_path),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Give it a moment to start
        await asyncio.sleep(0.5)
        
        if process.returncode is not None:
            raise Exception("Server process failed to start")
        
        # Create transport with the process
        transport = StdioTransport(config, process)
        
        # Connect to server
        print("Connecting to server...")
        await transport.connect()
        print("Connected successfully!")
        
        # Create MCP protocol
        protocol = MCPProtocol()
        
        # Test initialize request
        print("Testing initialize request...")
        init_request = protocol.create_initialize_request(
            protocol_version="2024-11-05",
            capabilities={
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            client_info={
                "name": "test-client",
                "version": "1.0.0"
            }
        )
        
        # Convert to dict
        init_request_dict = {
            "jsonrpc": init_request.jsonrpc,
            "id": init_request.id,
            "method": init_request.method,
            "params": init_request.params
        }
        
        # Send request
        response = await transport.send_request(init_request_dict)
        print(f"Initialize response: {response}")
        
        # Test tools/list request
        print("Testing tools/list request...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        tools_response = await transport.send_request(tools_request)
        print(f"Tools response: {tools_response}")
        
        # Test resources/list request
        print("Testing resources/list request...")
        resources_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/list",
            "params": {}
        }
        
        resources_response = await transport.send_request(resources_request)
        print(f"Resources response: {resources_response}")
        
        # Test prompts/list request
        print("Testing prompts/list request...")
        prompts_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "prompts/list",
            "params": {}
        }
        
        prompts_response = await transport.send_request(prompts_request)
        print(f"Prompts response: {prompts_response}")
        
        # Disconnect
        await transport.disconnect()
        print("Disconnected successfully!")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("Starting transport layer test...")
    
    success = await test_stdio_transport()
    
    if success:
        print("✅ Transport layer test passed!")
    else:
        print("❌ Transport layer test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
