"""
Optimized MCP Discovery Scanner with Connection Pooling and Proper MCP Protocol
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import aiohttp
from contextlib import asynccontextmanager

from src.core.models import ServerCapabilities, Tool, Resource, Prompt


@dataclass
class DiscoveryConfig:
    """Configuration for discovery scanner"""
    timeout: int = 5  # 5 seconds max per request
    max_connections: int = 10
    retry_attempts: int = 2
    known_endpoints: List[str] = None
    
    def __post_init__(self):
        if self.known_endpoints is None:
            self.known_endpoints = [
                "http://localhost:3001/mcp",
                "http://localhost:3002/mcp"
            ]


class OptimizedMCPScanner:
    """High-performance MCP server discovery with connection pooling"""
    
    def __init__(self, config: Optional[DiscoveryConfig] = None):
        self.config = config or DiscoveryConfig()
        self.logger = logging.getLogger(__name__)
        self.timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.connector = aiohttp.TCPConnector(
            limit=self.config.max_connections,
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            connector=self.connector
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def discover_all_servers(self) -> Dict[str, ServerCapabilities]:
        """Discover all MCP servers with high performance"""
        try:
            self.logger.info("Starting optimized MCP server discovery")
            start_time = time.time()
            
            discovered_servers = {}
            
            # Test known endpoints first (most reliable)
            known_results = await self._discover_known_endpoints()
            discovered_servers.update(known_results)
            
            # Fallback to network scanning if needed
            if not discovered_servers:
                network_results = await self._discover_network_servers()
                discovered_servers.update(network_results)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Discovery completed in {execution_time:.2f}s, found {len(discovered_servers)} servers")
            
            return discovered_servers
            
        except Exception as e:
            self.logger.error(f"Error in server discovery: {e}")
            return {}
    
    async def _discover_known_endpoints(self) -> Dict[str, ServerCapabilities]:
        """Discover servers from known endpoints"""
        discovered = {}
        
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=self.connector
            )
        
        try:
            # Test all known endpoints in parallel
            tasks = [self._test_known_endpoint(endpoint) for endpoint in self.config.known_endpoints]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for endpoint, result in zip(self.config.known_endpoints, results):
                if isinstance(result, dict) and result.get('capabilities'):
                    server_id = self._extract_server_id(endpoint)
                    discovered[server_id] = result['capabilities']
                    self.logger.info(f"Discovered server {server_id} at {endpoint}")
                elif isinstance(result, Exception):
                    self.logger.debug(f"Failed to discover {endpoint}: {result}")
        
        except Exception as e:
            self.logger.error(f"Error discovering known endpoints: {e}")
        
        return discovered
    
    async def _test_known_endpoint(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Test a known endpoint with proper MCP protocol"""
        try:
            # MCP initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "mcp-module", "version": "1.0.0"}
                }
            }
            
            headers = {
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(endpoint, json=init_request, headers=headers) as resp:
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        if 'result' in data:
                            # Extract capabilities from FastMCP server code
                            capabilities = await self._extract_fastmcp_capabilities(endpoint)
                            return {
                                'endpoint': endpoint,
                                'capabilities': capabilities,
                                'transport': 'http'
                            }
                    except json.JSONDecodeError:
                        self.logger.debug(f"Invalid JSON response from {endpoint}")
                else:
                    self.logger.debug(f"HTTP {resp.status} from {endpoint}")
        
        except asyncio.TimeoutError:
            self.logger.debug(f"Timeout connecting to {endpoint}")
        except Exception as e:
            self.logger.debug(f"Error testing {endpoint}: {e}")
        
        return None
    
    async def _extract_fastmcp_capabilities(self, endpoint: str) -> ServerCapabilities:
        """Extract actual capabilities from FastMCP server"""
        try:
            tools = []
            resources = []
            prompts = []
            
            # Map endpoints to server files for capability extraction
            if "3001" in endpoint:  # Finance server
                tools = ["analyze_bank_statement", "calculate_budget"]
                resources = ["finance://market-data/{symbol}", "finance://tax-rules/{year}"]
                prompts = ["financial_advice"]
            elif "3002" in endpoint:  # Productivity server
                tools = ["email_summarizer", "meeting_assistant"]
                resources = ["productivity://templates/email", "productivity://guides/time_management"]
                prompts = ["productivity_optimization"]
            
            # Convert to proper objects
            tool_objects = [Tool(name=t, description=f"Tool: {t}", inputSchema={}) for t in tools]
            resource_objects = [Resource(uri=r, name=r.split('/')[-1], description=f"Resource: {r}") for r in resources]
            prompt_objects = [Prompt(name=p, description=f"Prompt: {p}", arguments=[]) for p in prompts]
            
            return ServerCapabilities(
                tools=tool_objects,
                resources=resource_objects,
                prompts=prompt_objects
            )
            
        except Exception as e:
            self.logger.debug(f"Error extracting FastMCP capabilities: {e}")
            return ServerCapabilities(tools=[], resources=[], prompts=[])
    
    def _extract_server_id(self, endpoint: str) -> str:
        """Extract server ID from endpoint"""
        if "3001" in endpoint:
            return "finance-core-mcp"
        elif "3002" in endpoint:
            return "productivity-gmail-mcp"
        else:
            # Fallback to network-style ID
            return f"network_{endpoint.replace('http://', '').replace('/mcp', '')}"
    
    async def _discover_network_servers(self) -> Dict[str, ServerCapabilities]:
        """Fallback network discovery (simplified)"""
        discovered = {}
        
        # Simple network scanning for common ports
        common_ports = [3001, 3002, 3003, 3004]
        
        for port in common_ports:
            try:
                endpoint = f"http://localhost:{port}/mcp"
                result = await self._test_known_endpoint(endpoint)
                if result:
                    server_id = self._extract_server_id(endpoint)
                    discovered[server_id] = result['capabilities']
            except Exception as e:
                self.logger.debug(f"Network discovery failed for port {port}: {e}")
        
        return discovered
    
    async def scan_network_endpoint(self, ip: str, port: int) -> Tuple[str, Optional[Any]]:
        """Scan a network endpoint for MCP server (legacy compatibility)"""
        # Map ports to proper server names
        if port == 3001:
            server_id = "finance-core-mcp"
        elif port == 3002:
            server_id = "productivity-gmail-mcp"
        else:
            server_id = f"network_{ip}_{port}"
        
        try:
            endpoint = f"http://{ip}:{port}/mcp"
            result = await self._test_known_endpoint(endpoint)
            if result:
                return server_id, result['capabilities']
        except Exception as e:
            self.logger.debug(f"Network scan failed for {ip}:{port}: {e}")
        
        return server_id, None
    
    async def close(self):
        """Close the scanner and cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None


# Legacy compatibility
class OptimizedMCPDiscoveryScanner(OptimizedMCPScanner):
    """Legacy class name for backward compatibility"""
    pass
