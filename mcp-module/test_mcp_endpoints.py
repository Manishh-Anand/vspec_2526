#!/usr/bin/env python3
"""
Test MCP endpoints directly
"""

import asyncio
import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def test_mcp_endpoint(port: int, server_name: str):
    """Test MCP endpoint on a server"""
    print(f"\nTesting {server_name} on port {port}...")
    
    # Test 1: Initialize
    print("1. Testing initialize...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        response = requests.post(
            f"http://localhost:{port}/mcp",
            headers={"Content-Type": "application/json"},
            json=init_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Initialize successful: {result.get('result', {}).get('serverInfo', {}).get('name', 'unknown')}")
        else:
            print(f"   ✗ Initialize failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ✗ Initialize error: {e}")
        return False
    
    # Test 2: Tools list
    print("2. Testing tools/list...")
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        response = requests.post(
            f"http://localhost:{port}/mcp",
            headers={"Content-Type": "application/json"},
            json=tools_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            tools = result.get('result', {}).get('tools', [])
            print(f"   ✓ Tools list successful: {len(tools)} tools found")
        else:
            print(f"   ✗ Tools list failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ✗ Tools list error: {e}")
        return False
    
    # Test 3: Resources list
    print("3. Testing resources/list...")
    resources_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "resources/list",
        "params": {}
    }
    
    try:
        response = requests.post(
            f"http://localhost:{port}/mcp",
            headers={"Content-Type": "application/json"},
            json=resources_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            resources = result.get('result', {}).get('resources', [])
            print(f"   ✓ Resources list successful: {len(resources)} resources found")
        else:
            print(f"   ✗ Resources list failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ✗ Resources list error: {e}")
        return False
    
    # Test 4: Prompts list
    print("4. Testing prompts/list...")
    prompts_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "prompts/list",
        "params": {}
    }
    
    try:
        response = requests.post(
            f"http://localhost:{port}/mcp",
            headers={"Content-Type": "application/json"},
            json=prompts_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            prompts = result.get('result', {}).get('prompts', [])
            print(f"   ✓ Prompts list successful: {len(prompts)} prompts found")
        else:
            print(f"   ✗ Prompts list failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ✗ Prompts list error: {e}")
        return False
    
    print(f"   ✓ All MCP endpoints working for {server_name}")
    return True

def main():
    """Main test function"""
    print("MCP Endpoint Test")
    print("=" * 50)
    
    # Test finance server
    finance_ok = test_mcp_endpoint(3001, "Finance MCP Server")
    
    # Test productivity server
    productivity_ok = test_mcp_endpoint(3002, "Productivity MCP Server")
    
    if finance_ok and productivity_ok:
        print("\n[SUCCESS] All MCP endpoints working correctly!")
        return 0
    else:
        print("\n[ERROR] Some MCP endpoints failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
