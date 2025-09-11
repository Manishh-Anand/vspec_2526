"""
MCP Execution Engine with Proper Protocol Implementation
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import aiohttp
from contextlib import asynccontextmanager

from src.core.models import MatchResult
from src.transport.base import TransportConfig, TransportType
from src.transport.fixed_http import FixedHTTPTransport, HTTPTransportWithRetry
from src.transport.fixed_stdio import FixedStdioTransport


@dataclass
class ExecutionConfig:
    """Configuration for execution engine"""
    timeout: int = 10  # 10 seconds max per execution
    max_retries: int = 3
    retry_delay: float = 1.0
    connection_pool_size: int = 10


class ExecutionEngine:
    """MCP execution engine with proper protocol implementation"""
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()
        self.logger = logging.getLogger(__name__)
        self.connector = aiohttp.TCPConnector(
            limit=self.config.connection_pool_size,
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            connector=self.connector
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def execute_tool(self, tool_binding: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a tool using proper MCP protocol"""
        try:
            self.logger.info(f"Executing tool: {tool_binding.get('tool', {}).get('name', 'unknown')}")
            
            # Extract server information
            server_info = tool_binding.get('server', {})
            if isinstance(server_info, str):
                # Server is just a string ID, need to get endpoint
                server_endpoint = await self._get_server_endpoint(server_info)
            else:
                server_endpoint = server_info.get('endpoint')
            
            if not server_endpoint:
                raise Exception(f"No server endpoint found for tool {tool_binding.get('tool', {}).get('name', 'unknown')}")
            
            # Extract tool information
            tool_info = tool_binding.get('tool', {})
            tool_name = tool_info.get('name', 'unknown')
            
            # Execute using proper MCP tools/call method
            result = await self._execute_mcp_tool(server_endpoint, tool_name, params or {})
            
            self.logger.info(f"Tool execution successful: {tool_name}")
            return {
                'success': True,
                'result': result,
                'tool': tool_name,
                'server': server_info,
                'execution_time': 0.0  # TODO: Add timing
            }
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {tool_name if 'tool_name' in locals() else 'unknown'}: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool': tool_binding.get('tool', {}).get('name', 'unknown'),
                'server': tool_binding.get('server', 'unknown')
            }
    
    async def _execute_mcp_tool(self, server_endpoint: str, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute tool using MCP tools/call method"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                connector=self.connector
            )
        
        # MCP tools/call request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params or {}
            }
        }
        
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        
        for attempt in range(self.config.max_retries):
            try:
                async with self.session.post(f"{server_endpoint}/mcp", json=request, headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        if 'result' in result:
                            return result['result']
                        elif 'error' in result:
                            error_msg = result['error'].get('message', 'Unknown error')
                            raise Exception(f"MCP server error: {error_msg}")
                        else:
                            raise Exception("Invalid MCP response format")
                    else:
                        raise Exception(f"HTTP {resp.status}: {await resp.text()}")
                        
            except asyncio.TimeoutError:
                if attempt == self.config.max_retries - 1:
                    raise Exception(f"Tool execution timeout after {self.config.max_retries} attempts")
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
                
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
    
    async def _get_server_endpoint(self, server_id: str) -> Optional[str]:
        """Get server endpoint from server ID"""
        # Map server IDs to endpoints
        server_endpoints = {
            "finance-core-mcp": "http://localhost:3001/mcp",
            "productivity-gmail-mcp": "http://localhost:3002/mcp"
        }
        
        return server_endpoints.get(server_id)
    
    async def execute_all_tools(self, tool_bindings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute all tools in parallel"""
        if not tool_bindings:
            return []
        
        try:
            # Execute tools in parallel
            tasks = [self.execute_tool(binding) for binding in tool_bindings]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'success': False,
                        'error': str(result),
                        'tool': tool_bindings[i].get('tool', {}).get('name', 'unknown'),
                        'server': tool_bindings[i].get('server', 'unknown')
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Error executing tools in parallel: {e}")
            return []
    
    async def get_server_connection(self, server_config: Dict[str, Any]) -> Any:
        """Get server connection using proper transport"""
        try:
            transport_type = server_config.get('transport', {}).get('type', 'http')
            
            if transport_type == 'http':
                # Use connection pooling
                if not self.session:
                    self.session = aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                        connector=self.connector
                    )
                return self.session
                
            elif transport_type == 'stdio':
                # Create stdio transport
                command = server_config.get('transport', {}).get('command', [])
                if not command:
                    raise Exception("No command specified for stdio transport")
                
                config = TransportConfig(
                    type=TransportType.STDIO,
                    timeout=self.config.timeout
                )
                return FixedStdioTransport(config, command)
                
            else:
                raise Exception(f"Unsupported transport type: {transport_type}")
                
        except Exception as e:
            self.logger.error(f"Error getting server connection: {e}")
            raise
    
    async def _create_default_connection(self, server_id: str) -> Any:
        """Create default connection for development servers"""
        try:
            # Map server ID to endpoint
            endpoint = await self._get_server_endpoint(server_id)
            if endpoint:
                if not self.session:
                    self.session = aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                        connector=self.connector
                    )
                return self.session
            
            raise Exception(f"No default connection available for server: {server_id}")
            
        except Exception as e:
            self.logger.error(f"Error creating default connection: {e}")
            raise
    
    async def close(self):
        """Close the execution engine and cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None


# Legacy compatibility
class MCPExecutionEngine(ExecutionEngine):
    """Legacy class name for backward compatibility"""
    pass
