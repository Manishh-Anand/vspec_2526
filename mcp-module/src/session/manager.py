"""
Session Manager
Manages MCP session lifecycle
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from .client import MCPClient, ClientConfig


class SessionManager:
    """MCP Session Manager"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sessions: Dict[str, MCPClient] = {}
        self.session_configs: Dict[str, ClientConfig] = {}
    
    async def create_session(self, server_name: str, config: Optional[ClientConfig] = None) -> MCPClient:
        """Create a new session"""
        try:
            if server_name in self.sessions:
                self.logger.warning(f"Session for {server_name} already exists")
                return self.sessions[server_name]
            
            client_config = config or ClientConfig(server_name=server_name)
            client = MCPClient(server_name, client_config)
            
            # Connect to server
            if await client.connect():
                self.sessions[server_name] = client
                self.session_configs[server_name] = client_config
                self.logger.info(f"Created session for {server_name}")
                return client
            else:
                self.logger.error(f"Failed to connect to {server_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating session for {server_name}: {e}")
            return None
    
    async def get_session(self, server_name: str) -> Optional[MCPClient]:
        """Get existing session"""
        return self.sessions.get(server_name)
    
    async def close_session(self, server_name: str) -> bool:
        """Close a session"""
        try:
            if server_name in self.sessions:
                client = self.sessions[server_name]
                await client.disconnect()
                del self.sessions[server_name]
                del self.session_configs[server_name]
                self.logger.info(f"Closed session for {server_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error closing session for {server_name}: {e}")
            return False
    
    async def close_all_sessions(self) -> None:
        """Close all sessions"""
        for server_name in list(self.sessions.keys()):
            await self.close_session(server_name)
    
    async def list_sessions(self) -> List[str]:
        """List all active sessions"""
        return list(self.sessions.keys())
    
    async def is_session_active(self, server_name: str) -> bool:
        """Check if session is active"""
        if server_name in self.sessions:
            client = self.sessions[server_name]
            return client.is_connected()
        return False
