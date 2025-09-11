#!/usr/bin/env python3
"""
Simple MCP Test Server
A minimal server that responds to basic MCP requests for testing
"""
import json
import sys
import asyncio
from typing import Dict, Any

class SimpleMCPServer:
    """Simple MCP server for testing"""
    
    def __init__(self):
        self.request_id = 1
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        method = request.get("method")
        request_id = request.get("id", self.request_id)
        self.request_id += 1
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "simple-test-server",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "test_tool",
                            "description": "A test tool",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string"}
                                }
                            }
                        }
                    ]
                }
            }
        elif method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "resources": [
                        {
                            "name": "test_resource",
                            "description": "A test resource",
                            "uri": "test://resource/*",
                            "mimeType": "application/json"
                        }
                    ]
                }
            }
        elif method == "prompts/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "prompts": [
                        {
                            "name": "test_prompt",
                            "description": "A test prompt",
                            "arguments": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"}
                                }
                            }
                        }
                    ]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

async def stdio_server():
    """Run stdio server"""
    server = SimpleMCPServer()
    
    while True:
        try:
            # Read request from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request_data = json.loads(line.strip())
            response = server.handle_request(request_data)
            
            # Write response to stdout
            response_line = json.dumps(response) + "\n"
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.write, response_line)
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            error_line = json.dumps(error_response) + "\n"
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.write, error_line)
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)

if __name__ == "__main__":
    asyncio.run(stdio_server())
