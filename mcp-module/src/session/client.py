"""
MCP Client
Handles communication with MCP servers
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass

from ..core.protocol import MCPProtocol, MCPRequest, MCPResponse, MCPErrorResponse


@dataclass
class ClientConfig:
    """MCP Client Configuration"""
    server_name: str
    transport: str = "stdio"
    endpoint: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3


class MCPClient:
    """MCP Client for server communication"""
    
    def __init__(self, server_name: str, config: Optional[ClientConfig] = None):
        self.server_name = server_name
        self.config = config or ClientConfig(server_name=server_name)
        self.logger = logging.getLogger(__name__)
        self.protocol = MCPProtocol()
        self.connected = False
        self._request_id = 1
        
    async def connect(self) -> bool:
        """Connect to MCP server"""
        try:
            self.logger.info(f"Connecting to MCP server: {self.server_name}")
            
            # For now, we'll simulate a successful connection
            # In a real implementation, this would establish the actual connection
            await asyncio.sleep(0.1)  # Simulate connection time
            
            self.connected = True
            self.logger.info(f"Successfully connected to {self.server_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.server_name}: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        try:
            self.logger.info(f"Disconnecting from MCP server: {self.server_name}")
            self.connected = False
        except Exception as e:
            self.logger.error(f"Error disconnecting from {self.server_name}: {e}")
    
    async def send_request(self, request: MCPRequest) -> Union[MCPResponse, MCPErrorResponse]:
        """Send request to MCP server"""
        try:
            if not self.connected:
                await self.connect()
            
            self.logger.debug(f"Sending request to {self.server_name}: {request.method}")
            
            # For now, we'll simulate the response
            # In a real implementation, this would send the actual request
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Simulate successful response
            response = MCPResponse(
                id=request.id,
                result={
                    "status": "success",
                    "data": f"Mock response for {request.method}",
                    "server": self.server_name
                }
            )
            
            self.logger.debug(f"Received response from {self.server_name}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error sending request to {self.server_name}: {e}")
            return MCPErrorResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Internal error: {e}",
                    "data": None
                }
            )
    
    async def initialize(self, protocol_version: str = "2024-11-05",
                        capabilities: Optional[Dict[str, Any]] = None,
                        client_info: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize MCP connection"""
        try:
            request = self.protocol.create_initialize_request(
                protocol_version=protocol_version,
                capabilities=capabilities,
                client_info=client_info
            )
            
            response = await self.send_request(request)
            
            if isinstance(response, MCPErrorResponse):
                self.logger.error(f"Initialize failed: {response.error}")
                return False
            
            self.logger.info(f"Successfully initialized connection to {self.server_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during initialization: {e}")
            return False
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        try:
            request = self.protocol.create_tools_list_request()
            response = await self.send_request(request)
            
            if isinstance(response, MCPErrorResponse):
                self.logger.error(f"List tools failed: {response.error}")
                return []
            
            return response.result.get('tools', [])
            
        except Exception as e:
            self.logger.error(f"Error listing tools: {e}")
            return []
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool"""
        try:
            request = self.protocol.create_tools_call_request(name, arguments)
            response = await self.send_request(request)
            
            if isinstance(response, MCPErrorResponse):
                self.logger.error(f"Tool call failed: {response.error}")
                raise Exception(f"Tool call failed: {response.error.message}")
            
            return response.result
            
        except Exception as e:
            self.logger.error(f"Error calling tool {name}: {e}")
            raise
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        try:
            request = self.protocol.create_resources_list_request()
            response = await self.send_request(request)
            
            if isinstance(response, MCPErrorResponse):
                self.logger.error(f"List resources failed: {response.error}")
                return []
            
            return response.result.get('resources', [])
            
        except Exception as e:
            self.logger.error(f"Error listing resources: {e}")
            return []
    
    async def read_resource(self, uri: str) -> Any:
        """Read a resource"""
        try:
            request = self.protocol.create_resources_read_request(uri)
            response = await self.send_request(request)
            
            if isinstance(response, MCPErrorResponse):
                self.logger.error(f"Resource read failed: {response.error}")
                raise Exception(f"Resource read failed: {response.error.message}")
            
            return response.result
            
        except Exception as e:
            self.logger.error(f"Error reading resource {uri}: {e}")
            raise
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List available prompts"""
        try:
            request = self.protocol.create_prompts_list_request()
            response = await self.send_request(request)
            
            if isinstance(response, MCPErrorResponse):
                self.logger.error(f"List prompts failed: {response.error}")
                return []
            
            return response.result.get('prompts', [])
            
        except Exception as e:
            self.logger.error(f"Error listing prompts: {e}")
            return []
    
    async def get_prompt(self, name: str) -> Any:
        """Get a prompt"""
        try:
            request = self.protocol.create_prompts_get_request(name)
            response = await self.send_request(request)
            
            if isinstance(response, MCPErrorResponse):
                self.logger.error(f"Get prompt failed: {response.error}")
                raise Exception(f"Get prompt failed: {response.error.message}")
            
            return response.result
            
        except Exception as e:
            self.logger.error(f"Error getting prompt {name}: {e}")
            raise
    
    async def close(self):
        """Close the client connection"""
        await self.disconnect()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        asyncio.create_task(self.close())
