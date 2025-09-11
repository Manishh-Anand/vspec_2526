#!/usr/bin/env python3
"""
Start MCP Development Servers
Starts both finance-core-mcp (port 3001) and productivity-gmail-mcp (port 3002)
"""

import asyncio
import subprocess
import sys
import time
import os
from pathlib import Path

def start_server(server_path: str, port: int, server_name: str):
    """Start a server in a subprocess"""
    try:
        # Change to the server directory
        server_dir = Path(server_path).parent
        os.chdir(server_dir)
        
        # Start the server with HTTP mode
        cmd = [sys.executable, Path(server_path).name, "--http"]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"Started {server_name} on port {port} (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"Error starting {server_name}: {e}")
        return None

def check_server_health(port: int, server_name: str, max_retries: int = 10):
    """Check if server is healthy"""
    import httpx
    
    for i in range(max_retries):
        try:
            response = httpx.get(f"http://localhost:{port}/health", timeout=2.0)
            if response.status_code == 200:
                print(f"✅ {server_name} is healthy on port {port}")
                return True
        except Exception:
            pass
        
        print(f"⏳ Waiting for {server_name} to start... (attempt {i+1}/{max_retries})")
        time.sleep(1)
    
    print(f"❌ {server_name} failed to start on port {port}")
    return False

def main():
    """Main function to start both servers"""
    print("🚀 Starting MCP Development Servers...")
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    servers_dir = project_root / "servers"
    
    # Server configurations
    servers = [
        {
            "path": servers_dir / "finance" / "finance_core_mcp.py",
            "port": 3001,
            "name": "Finance Core MCP"
        },
        {
            "path": servers_dir / "productivity" / "productivity_gmail_mcp.py", 
            "port": 3002,
            "name": "Productivity Gmail MCP"
        }
    ]
    
    processes = []
    
    try:
        # Start all servers
        for server in servers:
            if server["path"].exists():
                process = start_server(
                    str(server["path"]), 
                    server["port"], 
                    server["name"]
                )
                if process:
                    processes.append((process, server))
            else:
                print(f"❌ Server file not found: {server['path']}")
        
        # Wait a moment for servers to start
        time.sleep(3)
        
        # Check server health
        all_healthy = True
        for _, server in processes:
            if not check_server_health(server["port"], server["name"]):
                all_healthy = False
        
        if all_healthy:
            print("\n🎉 All MCP servers are running successfully!")
            print("📋 Server Status:")
            print("   • Finance Core MCP: http://localhost:3001")
            print("   • Productivity Gmail MCP: http://localhost:3002")
            print("\n💡 You can now run the MCP module tests.")
            print("   Press Ctrl+C to stop all servers.")
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping servers...")
        else:
            print("\n❌ Some servers failed to start properly.")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        # Clean up processes
        for process, server in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {server['name']}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️  Force killed {server['name']}")
            except Exception as e:
                print(f"❌ Error stopping {server['name']}: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
