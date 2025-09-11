import asyncio
import httpx
import json

async def test_mcp_servers():
    """Test if MCP servers are responding correctly"""
    
    # Test finance server (port 3001)
    print("Testing Finance MCP Server (port 3001)...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            response = await client.post(
                'http://localhost:3001/mcp',
                json=init_request,
                headers={
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"Finance server status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Finance server is responding!")
                print(f"Response: {response.text[:200]}...")
            else:
                print(f"❌ Finance server error: {response.text}")
                
    except Exception as e:
        print(f"❌ Finance server connection failed: {e}")
    
    # Test productivity server (port 3002)
    print("\nTesting Productivity MCP Server (port 3002)...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            response = await client.post(
                'http://localhost:3002/mcp',
                json=init_request,
                headers={
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"Productivity server status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Productivity server is responding!")
                print(f"Response: {response.text[:200]}...")
            else:
                print(f"❌ Productivity server error: {response.text}")
                
    except Exception as e:
        print(f"❌ Productivity server connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_servers())
