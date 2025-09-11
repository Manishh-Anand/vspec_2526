"""
MCP Discovery Scanner Implementation
Uses optimized scanner for better performance
"""

import asyncio
import json
import logging
import os
import psutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import httpx

from src.core.protocol import MCPProtocol
from src.transport.stdio import StdioTransport
from src.transport.http import HTTPTransport
from src.transport.base import TransportConfig, TransportType
from src.core.models import MatchResult
from .optimized_scanner import OptimizedMCPDiscoveryScanner, DiscoveryConfig


@dataclass
class ServerCapabilities:
    """Complete server capability structure"""
    tools: List[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    prompts: List[Dict[str, Any]]
    server_info: Dict[str, Any]


@dataclass
class DiscoveredServer:
    """Discovered server information"""
    server_id: str
    transport_type: str
    endpoint: Optional[str] = None
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None
    pid: Optional[int] = None
    capabilities: Optional[ServerCapabilities] = None


class MCPDiscoveryScanner:
    """Complete MCP discovery engine that handles all three primitives"""
    
    def __init__(self, use_optimized: bool = True):
        self.logger = logging.getLogger(__name__)
        self.discovered_servers: Dict[str, DiscoveredServer] = {}
        self.protocol = MCPProtocol()
        self.use_optimized = use_optimized
        
        # Initialize optimized scanner if requested
        if self.use_optimized:
            self.optimized_scanner = OptimizedMCPDiscoveryScanner()
        else:
            self.optimized_scanner = None
        
    async def discover_all_servers(self) -> Dict[str, ServerCapabilities]:
        """Discover servers and ALL their capabilities"""
        self.logger.info("Starting comprehensive MCP server discovery")
        
        # Use optimized scanner if available
        if self.use_optimized and self.optimized_scanner:
            return await self._discover_with_optimized_scanner()
        else:
            return await self._discover_with_legacy_scanner()
    
    async def _discover_with_optimized_scanner(self) -> Dict[str, ServerCapabilities]:
        """Use optimized scanner for discovery"""
        try:
            async with self.optimized_scanner:
                discovered = await self.optimized_scanner.discover_all_servers()
                
                # Convert to legacy format
                result = {}
                for server_id, capabilities in discovered.items():
                    # Handle dict format from optimized scanner
                    if isinstance(capabilities, dict):
                        result[server_id] = ServerCapabilities(
                            tools=capabilities.get('tools', []),
                            resources=capabilities.get('resources', []),
                            prompts=capabilities.get('prompts', []),
                            server_info={
                                'name': capabilities.get('server_name', 'unknown'),
                                'version': capabilities.get('version', '1.0.0'),
                                'endpoint': capabilities.get('endpoint', ''),
                                'transport_type': capabilities.get('transport_type', 'http'),
                                'metadata': capabilities.get('metadata', {})
                            }
                        )
                    else:
                        # Handle object format (legacy)
                        result[server_id] = ServerCapabilities(
                            tools=[tool.__dict__ for tool in capabilities.tools],
                            resources=[resource.__dict__ for resource in capabilities.resources],
                            prompts=[prompt.__dict__ for prompt in capabilities.prompts],
                            server_info={
                                'name': capabilities.server_name,
                                'version': capabilities.version,
                                'endpoint': capabilities.endpoint,
                                'transport_type': capabilities.transport_type.value,
                                'metadata': capabilities.metadata
                            }
                    )
                
                self.logger.info(f"Optimized discovery found {len(result)} servers")
                return result
                
        except Exception as e:
            self.logger.error(f"Optimized discovery failed: {e}")
            # Fallback to legacy scanner
            return await self._discover_with_legacy_scanner()
    
    async def _discover_with_legacy_scanner(self) -> Dict[str, ServerCapabilities]:
        """Use legacy scanner for discovery"""
        self.logger.info("Using legacy discovery scanner")
        
        # Multi-tier discovery as per specification
        await self._discover_from_environment()
        await self._discover_from_network()
        await self._discover_from_processes()
        await self._discover_from_config_files()
        
        # Query each discovered server for complete capabilities
        for server_id, server in self.discovered_servers.items():
            # Debug: Check if server is the right type
            if not isinstance(server, DiscoveredServer):
                self.logger.error(f"Server {server_id} is not a DiscoveredServer object: {type(server)}")
                continue
            capabilities = await self._get_complete_capabilities(server)
            if capabilities:
                server.capabilities = capabilities
                self.logger.info(f"Server {server_id}: {len(capabilities.tools)} tools, {len(capabilities.resources)} resources, {len(capabilities.prompts)} prompts")
        
        # Return only servers with capabilities
        return {
            server_id: server.capabilities 
            for server_id, server in self.discovered_servers.items() 
            if server.capabilities
        }
    
    async def _discover_from_environment(self):
        """Discover servers from environment variables"""
        self.logger.info("Discovering servers from environment variables")
        
        # Check MCP_SERVERS environment variable
        mcp_servers = os.environ.get('MCP_SERVERS', '')
        if mcp_servers:
            for server_def in mcp_servers.split(','):
                if ':' in server_def:
                    host, port = server_def.split(':')
                    server_id = f"env_{host}_{port}"
                    self.discovered_servers[server_id] = DiscoveredServer(
                        server_id=server_id,
                        transport_type="http",
                        endpoint=f"http://{host}:{port}/mcp"
                    )
        
        # Check MCP_SERVER_PATHS for stdio servers
        mcp_paths = os.environ.get('MCP_SERVER_PATHS', '')
        if mcp_paths:
            for path in mcp_paths.split(','):
                if os.path.exists(path):
                    server_id = f"env_stdio_{Path(path).stem}"
                    self.discovered_servers[server_id] = DiscoveredServer(
                        server_id=server_id,
                        transport_type="stdio",
                        command="python",
                        args=[path]
                    )
    
    async def _discover_from_network(self):
        """Scan network for MCP servers"""
        self.logger.info("Scanning network for MCP servers")
        
        # Common MCP ports to scan
        ports_to_scan = [3000, 3001, 3002, 3003, 3004, 3005, 8080, 8081, 8082, 9000, 9001]
        
        for port in ports_to_scan:
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    # Try MCP protocol endpoint
                    endpoint = f"http://localhost:{port}/mcp"
                    try:
                        # Use proper MCP protocol initialization
                        mcp_init_request = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "initialize",
                            "params": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {},
                                "clientInfo": {"name": "mcp-discovery", "version": "1.0.0"}
                            }
                        }
                        
                        response = await client.post(
                            endpoint,
                            json=mcp_init_request,
                            headers={
                                "Accept": "application/json, text/event-stream",
                                "Content-Type": "application/json"
                            }
                        )
                        
                        if response.status_code == 200:
                            server_id = f"network_localhost_{port}"
                            self.discovered_servers[server_id] = DiscoveredServer(
                                server_id=server_id,
                                transport_type="http",
                                endpoint=endpoint
                            )
                            self.logger.info(f"Discovered MCP server at {endpoint}")
                    except:
                        continue
            except Exception as e:
                self.logger.debug(f"Port {port} scan failed: {e}")
                continue
    
    async def _discover_from_processes(self):
        """Discover MCP servers from running processes"""
        self.logger.info("Discovering MCP servers from running processes")
        
        # List of known MCP server patterns to look for
        mcp_server_patterns = [
            'mcp_server',
            'model_context',
            'mcp',
            'server.py',
            'finance_server',
            'productivity_server',
            'education_server',
            'sports_server',
            'software_dev_server'
        ]
        
        # List of processes to skip (system processes)
        skip_processes = [
            'conhost.exe',
            'Dashboard/Widgets.exe',
            'ArmouryCrate.exe',
            'svchost.exe',
            'explorer.exe',
            'taskmgr.exe',
            'cmd.exe',
            'powershell.exe',
            'python.exe',  # Skip generic Python processes
            'node.exe',
            'java.exe'
        ]
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if not cmdline:
                        continue
                    
                    # Skip system processes
                    process_name = proc.info.get('name', '').lower()
                    if any(skip_name.lower() in process_name for skip_name in skip_processes):
                        continue
                    
                    # Look for MCP-related processes
                    cmdline_str = ' '.join(cmdline).lower()
                    
                    # Only consider processes that match MCP patterns
                    is_mcp_server = any(pattern in cmdline_str for pattern in mcp_server_patterns)
                    
                    if is_mcp_server:
                        server_id = f"process_{proc.info['pid']}"
                        self.discovered_servers[server_id] = DiscoveredServer(
                            server_id=server_id,
                            transport_type="stdio",
                            command=cmdline[0] if cmdline else None,
                            args=cmdline[1:] if len(cmdline) > 1 else None,
                            pid=proc.info['pid']
                        )
                        self.logger.info(f"Discovered MCP process server: {server_id} - {cmdline[0]}")
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Process discovery error: {e}")
    
    async def _discover_from_config_files(self):
        """Discover servers from configuration files"""
        self.logger.info("Discovering servers from configuration files")
        
        # Check common config locations
        config_paths = [
            Path.home() / '.mcp' / 'servers.json',
            Path.home() / '.config' / 'mcp' / 'servers.json',
            Path.cwd() / 'mcp_servers.json',
            Path.cwd() / '.mcp' / 'servers.json'
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config_data = json.load(f)
                    
                    # Handle both list and dict formats
                    if isinstance(config_data, list):
                        servers_config = config_data
                    else:
                        servers_config = config_data.get('servers', [])
                    
                    for server_config in servers_config:
                        # Skip if server_config is not a dict
                        if not isinstance(server_config, dict):
                            continue
                            
                        server_id = server_config.get('name', f"config_{len(self.discovered_servers)}")
                        
                        if server_config.get('transport') == 'stdio':
                            command = server_config.get('command', 'python')
                            if isinstance(command, list):
                                command = command[0] if command else 'python'
                            self.discovered_servers[server_id] = DiscoveredServer(
                                server_id=server_id,
                                transport_type="stdio",
                                command=command,
                                args=server_config.get('args', [])
                            )
                        elif server_config.get('transport') == 'http':
                            endpoint = server_config.get('endpoint')
                            if endpoint:  # Only add if endpoint is provided
                                self.discovered_servers[server_id] = DiscoveredServer(
                                    server_id=server_id,
                                    transport_type="http",
                                    endpoint=endpoint
                                )
                    
                    self.logger.info(f"Loaded {len(servers_config)} servers from {config_path}")
                    break
                    
                except Exception as e:
                    self.logger.error(f"Error reading config file {config_path}: {e}")
    
    async def _get_complete_capabilities(self, server: DiscoveredServer) -> Optional[ServerCapabilities]:
        """Query server for ALL three primitive types"""
        transport = None
        
        try:
            # Create appropriate transport
            if server.transport_type == 'stdio':
                if not server.command:
                    return None
                
                # Start the server process
                process = await self._start_stdio_server(server.command, server.args or [])
                if not process:
                    return None
                
                config = TransportConfig(type=TransportType.STDIO)
                transport = StdioTransport(config, process)
                
            elif server.transport_type == 'http':
                if not server.endpoint:
                    return None
                
                config = TransportConfig(type=TransportType.HTTP, endpoint=server.endpoint)
                transport = HTTPTransport(config)
            
            if not transport:
                return None
            
            # Initialize connection
            await transport.connect()
            
            # Initialize MCP session
            init_request = self.protocol.create_initialize_request(
                protocol_version="2024-11-05",
                capabilities={
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                client_info={
                    "name": "mcp-discovery",
                    "version": "1.0.0"
                }
            )
            
            # Convert MCPRequest to dict
            init_request_dict = {
                "jsonrpc": init_request.jsonrpc,
                "id": init_request.id,
                "method": init_request.method,
                "params": init_request.params
            }
            
            init_response = await transport.send_request(init_request_dict)
            if 'error' in init_response:
                self.logger.warning(f"Failed to initialize server {server.server_id}: {init_response['error']}")
                return None
            
            # Query ALL three primitive types
            tools_response = await self._query_tools(transport)
            resources_response = await self._query_resources(transport)
            prompts_response = await self._query_prompts(transport)
            
            # Extract capabilities
            tools = tools_response.get('result', {}).get('tools', [])
            resources = resources_response.get('result', {}).get('resources', [])
            prompts = prompts_response.get('result', {}).get('prompts', [])
            
            return ServerCapabilities(
                tools=tools,
                resources=resources,
                prompts=prompts,
                server_info=init_response.get('result', {}).get('serverInfo', {})
            )
                    
        except Exception as e:
            self.logger.error(f"Error querying server {server.server_id} capabilities: {e}")
            return None
        finally:
            if transport:
                await transport.close()
    
    async def _start_stdio_server(self, command: str, args: List[str]) -> Optional[Any]:
        """Start a stdio server process"""
        try:
            full_command = [command] + args
            process = await asyncio.create_subprocess_exec(
                *full_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Give it a moment to start
            await asyncio.sleep(0.5)
            
            if process.returncode is None:  # Still running
                return process
            else:
                self.logger.warning(f"Server process failed to start: {full_command}")
                return None
                    
        except Exception as e:
            self.logger.error(f"Error starting stdio server: {e}")
            return None
    
    async def _query_tools(self, transport) -> Dict[str, Any]:
        """Query server for tools"""
        try:
            tools_request = self.protocol.create_tools_list_request()
            tools_request_dict = {
                "jsonrpc": tools_request.jsonrpc,
                "id": tools_request.id,
                "method": tools_request.method,
                "params": tools_request.params
            }
            return await transport.send_request(tools_request_dict)
        except Exception as e:
            self.logger.error(f"Error querying tools: {e}")
            return {"error": str(e)}
    
    async def _query_resources(self, transport) -> Dict[str, Any]:
        """Query server for resources"""
        try:
            resources_request = self.protocol.create_resources_list_request()
            resources_request_dict = {
                "jsonrpc": resources_request.jsonrpc,
                "id": resources_request.id,
                "method": resources_request.method,
                "params": resources_request.params
            }
            return await transport.send_request(resources_request_dict)
        except Exception as e:
            self.logger.error(f"Error querying resources: {e}")
            return {"error": str(e)}
    
    async def _query_prompts(self, transport) -> Dict[str, Any]:
        """Query server for prompts"""
        try:
            prompts_request = self.protocol.create_prompts_list_request()
            prompts_request_dict = {
                "jsonrpc": prompts_request.jsonrpc,
                "id": prompts_request.id,
                "method": prompts_request.method,
                "params": prompts_request.params
            }
            return await transport.send_request(prompts_request_dict)
        except Exception as e:
            self.logger.error(f"Error querying prompts: {e}")
            return {"error": str(e)}
    
    async def match_all_primitives(self, requirements: Dict, discovered_servers: Dict) -> Dict:
        """Match all three primitive types semantically"""
        matches = {
            'tools': [],
            'resources': [],
            'prompts': []
        }
        
        # Match tools
        for tool_req in requirements.get('tools', []):
            match = await self._match_tool_semantically(tool_req, discovered_servers)
            if match:
                matches['tools'].append(match)
        
        # Match resources
        for resource_req in requirements.get('resources', []):
            match = await self._match_resource_semantically(resource_req, discovered_servers)
            if match:
                matches['resources'].append(match)
        
        # Match prompts
        for prompt_req in requirements.get('prompts', []):
            match = await self._match_prompt_semantically(prompt_req, discovered_servers)
            if match:
                matches['prompts'].append(match)
        
        return matches
    
    async def _match_tool_semantically(self, tool_req: Dict, servers: Dict) -> Optional[MatchResult]:
        """Use semantic matching for tools"""
        # Collect all available tools from all servers
        available_tools = []
        for server_id, capabilities in servers.items():
            for tool in capabilities.tools:
                available_tools.append({
                    'server_id': server_id,
                    'tool': tool
                })
        
        # Simple name-based matching for now
        # In a full implementation, this would use LLM semantic matching
        for available in available_tools:
            if available['tool'].get('name') == tool_req['name']:
                # Convert tool dict to Tool object
                from ..core.protocol import Tool
                tool_obj = Tool(
                    name=available['tool']['name'],
                    description=available['tool'].get('description', ''),
                    inputSchema=available['tool'].get('inputSchema', {})
                )
                return MatchResult(
                    tool=tool_obj,
                    score=1.0,
                    confidence=1.0,
                    reasoning='Exact name match',
                    server=available['server_id']
                )
        
        return None
    
    async def _match_resource_semantically(self, resource_req: Dict, servers: Dict) -> Optional[MatchResult]:
        """Match resource requirements to available resources"""
        # Simple URI pattern matching for now
        for server_id, capabilities in servers.items():
            for resource in capabilities.resources:
                if resource.get('uri') == resource_req.get('uri'):
                    # Convert resource dict to Resource object
                    from ..core.protocol import Resource
                    resource_obj = Resource(
                        uri=resource['uri'],
                        name=resource.get('name', resource['uri']),
                        description=resource.get('description', ''),
                        mimeType=resource.get('mimeType', 'text/plain')
                    )
                    return MatchResult(
                        tool=resource_obj,  # Using tool field for resource
                        score=1.0,
                        confidence=1.0,
                        reasoning='Exact URI match',
                        server=server_id
                    )
        
        return None
    
    async def _match_prompt_semantically(self, prompt_req: Dict, servers: Dict) -> Optional[MatchResult]:
        """Match prompt requirements to available prompts"""
        # Simple name-based matching for now
        for server_id, capabilities in servers.items():
            for prompt in capabilities.prompts:
                if prompt.get('name') == prompt_req['name']:
                    # Convert prompt dict to Prompt object
                    from ..core.protocol import Prompt
                    prompt_obj = Prompt(
                        name=prompt['name'],
                        description=prompt.get('description', ''),
                        arguments=prompt.get('arguments', {})
                    )
                    return MatchResult(
                        tool=prompt_obj,  # Using tool field for prompt
                        score=1.0,
                        confidence=1.0,
                        reasoning='Exact name match',
                        server=server_id
                    )
        
        return None
