#!/usr/bin/env python3
"""
Script to start test MCP servers
"""

import asyncio
import subprocess
import sys
import time
import requests
from pathlib import Path

def check_port(port: int) -> bool:
    """Check if a port is available"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server(script_path: str, port: int, server_name: str):
    """Start a server in a subprocess"""
    print(f"Starting {server_name} on port {port}...")
    
    # Check if port is already in use
    if check_port(port):
        print(f"Port {port} is already in use. Server may already be running.")
        return None
    
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for the server to start
        time.sleep(3)
        
        # Check if server started successfully
        if check_port(port):
            print(f"✓ {server_name} started successfully on port {port}")
            return process
        else:
            print(f"✗ Failed to start {server_name} on port {port}")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"✗ Error starting {server_name}: {e}")
        return None

def main():
    """Main function to start all test servers"""
    print("Starting MCP Test Servers...")
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
                print(f"✗ Server script not found: {server['script']}")
        
        if processes:
            print(f"\n✓ Started {len(processes)} servers successfully!")
            print("\nServers are running:")
            print("  - Finance MCP Server: http://localhost:3001")
            print("  - Productivity MCP Server: http://localhost:3002")
            print("\nPress Ctrl+C to stop all servers...")
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping servers...")
                
        else:
            print("✗ No servers were started successfully.")
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
        
        print("✓ All servers stopped.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
