#!/usr/bin/env python3
"""
Complete MCP Module Test with Servers
"""

import asyncio
import subprocess
import sys
import time
import requests
from pathlib import Path

def check_server(port: int, server_name: str) -> bool:
    """Check if a server is running on the specified port"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            print(f"[OK] {server_name} is running on port {port}")
            return True
        else:
            print(f"[ERROR] {server_name} responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {server_name} not running on port {port}: {e}")
        return False

def start_server(script_path: str, port: int, server_name: str):
    """Start a server in a subprocess"""
    print(f"Starting {server_name} on port {port}...")
    
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        for attempt in range(10):
            time.sleep(2)
            if check_server(port, server_name):
                return process
        
        print(f"[ERROR] Failed to start {server_name} after 20 seconds")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"[ERROR] Error starting {server_name}: {e}")
        return None

async def run_complete_test():
    """Run the complete test with servers"""
    print("MCP Module Complete Test with Servers")
    print("=" * 50)
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Define servers to start
    servers = [
        {
            "script": current_dir / "servers" / "finance_http_server.py",
            "port": 3001,
            "name": "Finance MCP Server"
        },
        {
            "script": current_dir / "servers" / "productivity_http_server.py",
            "port": 3002,
            "name": "Productivity MCP Server"
        }
    ]
    
    processes = []
    
    try:
        # Start each server
        for server in servers:
            if server["script"].exists():
                process = start_server(
                    str(server["script"]),
                    server["port"],
                    server["name"]
                )
                if process:
                    processes.append(process)
            else:
                print(f"[ERROR] Server script not found: {server['script']}")
        
        if len(processes) == len(servers):
            print(f"\n[OK] All {len(processes)} servers started successfully!")
            print("\nServers are running:")
            print("  - Finance MCP Server: http://localhost:3001")
            print("  - Productivity MCP Server: http://localhost:3002")
            
            # Wait a moment for servers to fully initialize
            print("\nWaiting for servers to fully initialize...")
            time.sleep(5)
            
            # Run the complete test
            print("\nRunning complete MCP module test...")
            result = subprocess.run([sys.executable, "test_mcp_module.py"], 
                                  capture_output=True, text=True)
            
            print("\nTest Output:")
            print(result.stdout)
            
            if result.stderr:
                print("\nErrors:")
                print(result.stderr)
            
            if result.returncode == 0:
                print("\n🎉 Complete test passed! All components working with servers.")
            else:
                print(f"\n❌ Test failed with return code {result.returncode}")
                
        else:
            print(f"[ERROR] Only {len(processes)} out of {len(servers)} servers started.")
            return 1
            
    except KeyboardInterrupt:
        print("\nStopping servers...")
    finally:
        # Terminate all processes
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except:
                pass
        
        print("[OK] All servers stopped.")
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(run_complete_test()))
