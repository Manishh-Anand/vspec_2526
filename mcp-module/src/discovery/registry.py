"""
Server Registry Management
Manages MCP server registry
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from .scanner import ServerInfo


class ServerRegistry:
    """MCP Server Registry"""
    
    def __init__(self, registry_path: Optional[str] = None):
        self.registry_path = registry_path or str(Path.home() / ".mcp" / "registry.json")
        self.logger = logging.getLogger(__name__)
        self.servers: Dict[str, ServerInfo] = {}
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load server registry from file"""
        try:
            registry_file = Path(self.registry_path)
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    data = json.load(f)
                
                for server_data in data.get('servers', []):
                    server_info = ServerInfo(
                        name=server_data.get('name', ''),
                        domain=server_data.get('domain', ''),
                        transport=server_data.get('transport', 'stdio'),
                        endpoint=server_data.get('endpoint'),
                        command=server_data.get('command'),
                        args=server_data.get('args', []),
                        enabled=server_data.get('enabled', True),
                        capabilities=server_data.get('capabilities', {})
                    )
                    
                    if server_info.name:
                        self.servers[server_info.name] = server_info
                        
        except Exception as e:
            self.logger.error(f"Error loading server registry: {e}")
    
    def _save_registry(self) -> None:
        """Save server registry to file"""
        try:
            registry_file = Path(self.registry_path)
            registry_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "servers": [
                    {
                        "name": server.name,
                        "domain": server.domain,
                        "transport": server.transport,
                        "endpoint": server.endpoint,
                        "command": server.command,
                        "args": server.args or [],
                        "enabled": server.enabled,
                        "capabilities": server.capabilities or {}
                    }
                    for server in self.servers.values()
                ]
            }
            
            with open(registry_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving server registry: {e}")
    
    async def register_server(self, server_info: ServerInfo) -> bool:
        """Register a server in the registry"""
        try:
            self.servers[server_info.name] = server_info
            self._save_registry()
            self.logger.info(f"Registered server: {server_info.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error registering server {server_info.name}: {e}")
            return False
    
    async def unregister_server(self, server_name: str) -> bool:
        """Unregister a server from the registry"""
        try:
            if server_name in self.servers:
                del self.servers[server_name]
                self._save_registry()
                self.logger.info(f"Unregistered server: {server_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error unregistering server {server_name}: {e}")
            return False
    
    async def get_server(self, server_name: str) -> Optional[ServerInfo]:
        """Get server information from registry"""
        return self.servers.get(server_name)
    
    async def list_servers(self) -> List[ServerInfo]:
        """List all registered servers"""
        return list(self.servers.values())
    
    async def list_enabled_servers(self) -> List[ServerInfo]:
        """List all enabled servers"""
        return [server for server in self.servers.values() if server.enabled]
    
    async def filter_servers_by_domain(self, domain: str) -> List[ServerInfo]:
        """Filter servers by domain"""
        return [server for server in self.servers.values() if server.domain == domain]
    
    async def filter_servers_by_transport(self, transport: str) -> List[ServerInfo]:
        """Filter servers by transport type"""
        return [server for server in self.servers.values() if server.transport == transport]
    
    async def update_server_capabilities(self, server_name: str, capabilities: Dict[str, Any]) -> bool:
        """Update server capabilities"""
        try:
            if server_name in self.servers:
                self.servers[server_name].capabilities = capabilities
                self._save_registry()
                self.logger.info(f"Updated capabilities for server: {server_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error updating capabilities for server {server_name}: {e}")
            return False
    
    async def enable_server(self, server_name: str) -> bool:
        """Enable a server"""
        try:
            if server_name in self.servers:
                self.servers[server_name].enabled = True
                self._save_registry()
                self.logger.info(f"Enabled server: {server_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error enabling server {server_name}: {e}")
            return False
    
    async def disable_server(self, server_name: str) -> bool:
        """Disable a server"""
        try:
            if server_name in self.servers:
                self.servers[server_name].enabled = False
                self._save_registry()
                self.logger.info(f"Disabled server: {server_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error disabling server {server_name}: {e}")
            return False
    
    async def clear_registry(self) -> bool:
        """Clear the entire registry"""
        try:
            self.servers.clear()
            self._save_registry()
            self.logger.info("Cleared server registry")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing registry: {e}")
            return False
