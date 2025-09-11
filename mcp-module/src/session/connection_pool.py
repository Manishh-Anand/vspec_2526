"""
Connection Pool
Manages multiple MCP connections
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from .client import MCPClient, ClientConfig


class ConnectionPool:
    """MCP Connection Pool"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.logger = logging.getLogger(__name__)
        self.connections: Dict[str, MCPClient] = {}
        self.connection_semaphore = asyncio.Semaphore(max_connections)
    
    async def get_connection(self, server_name: str, config: Optional[ClientConfig] = None) -> Optional[MCPClient]:
        """Get a connection from the pool"""
        async with self.connection_semaphore:
            if server_name in self.connections:
                client = self.connections[server_name]
                if client.is_connected():
                    return client
                else:
                    # Reconnect if disconnected
                    if await client.connect():
                        return client
                    else:
                        del self.connections[server_name]
            
            # Create new connection
            client_config = config or ClientConfig(server_name=server_name)
            client = MCPClient(server_name, client_config)
            
            if await client.connect():
                self.connections[server_name] = client
                self.logger.info(f"Created connection for {server_name}")
                return client
            else:
                self.logger.error(f"Failed to create connection for {server_name}")
                return None
    
    async def release_connection(self, server_name: str) -> None:
        """Release a connection back to the pool"""
        if server_name in self.connections:
            client = self.connections[server_name]
            if client.is_connected():
                # Keep connection in pool for reuse
                pass
            else:
                # Remove disconnected connection
                del self.connections[server_name]
    
    async def close_connection(self, server_name: str) -> bool:
        """Close and remove a connection"""
        try:
            if server_name in self.connections:
                client = self.connections[server_name]
                await client.disconnect()
                del self.connections[server_name]
                self.logger.info(f"Closed connection for {server_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error closing connection for {server_name}: {e}")
            return False
    
    async def close_all_connections(self) -> None:
        """Close all connections"""
        for server_name in list(self.connections.keys()):
            await self.close_connection(server_name)
    
    async def list_connections(self) -> List[str]:
        """List all active connections"""
        return list(self.connections.keys())
    
    async def get_connection_status(self) -> Dict[str, bool]:
        """Get status of all connections"""
        status = {}
        for server_name, client in self.connections.items():
            status[server_name] = client.is_connected()
        return status
