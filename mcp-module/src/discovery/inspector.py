"""
Capability Inspector
Introspects MCP server capabilities
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from ..session.client import MCPClient
from ..core.protocol import MCPProtocol


class CapabilityInspector:
    """MCP Capability Inspector"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.protocol = MCPProtocol()
    
    async def inspect_server(self, client: MCPClient) -> Dict[str, Any]:
        """Inspect server capabilities"""
        try:
            self.logger.info(f"Inspecting server: {client.server_name}")
            
            capabilities = {
                "server_name": client.server_name,
                "tools": [],
                "resources": [],
                "prompts": []
            }
            
            # Get tools
            tools = await client.list_tools()
            capabilities["tools"] = tools
            
            # Get resources
            resources = await client.list_resources()
            capabilities["resources"] = resources
            
            # Get prompts
            prompts = await client.list_prompts()
            capabilities["prompts"] = prompts
            
            self.logger.info(f"Server {client.server_name} has {len(tools)} tools, {len(resources)} resources, {len(prompts)} prompts")
            
            return capabilities
            
        except Exception as e:
            self.logger.error(f"Error inspecting server {client.server_name}: {e}")
            return {"server_name": client.server_name, "error": str(e)}
    
    async def get_tool_details(self, client: MCPClient, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific tool"""
        try:
            tools = await client.list_tools()
            for tool in tools:
                if tool.get('name') == tool_name:
                    return tool
            return None
        except Exception as e:
            self.logger.error(f"Error getting tool details for {tool_name}: {e}")
            return None
    
    async def get_resource_details(self, client: MCPClient, uri: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific resource"""
        try:
            resources = await client.list_resources()
            for resource in resources:
                if resource.get('uri') == uri:
                    return resource
            return None
        except Exception as e:
            self.logger.error(f"Error getting resource details for {uri}: {e}")
            return None
    
    async def get_prompt_details(self, client: MCPClient, prompt_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific prompt"""
        try:
            prompts = await client.list_prompts()
            for prompt in prompts:
                if prompt.get('name') == prompt_name:
                    return prompt
            return None
        except Exception as e:
            self.logger.error(f"Error getting prompt details for {prompt_name}: {e}")
            return None
