"""
Software Development MCP Server Implementation
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from ...src.core.protocol import (
    MCPProtocol, MCPRequest, MCPResponse, MCPErrorResponse,
    Tool, Resource, Prompt, PromptArgument
)
from ...src.transport.stdio import StdioTransport
from .tools import SoftwareDevTools


@dataclass
class SoftwareDevServerConfig:
    """Software development server configuration"""
    name: str = "software-dev-server"
    version: str = "1.0.0"
    description: str = "Software development tools and resources server"
    domain: str = "software_dev"


class SoftwareDevMCPServer:
    """Software Development MCP Server"""
    
    def __init__(self, config: Optional[SoftwareDevServerConfig] = None):
        self.config = config or SoftwareDevServerConfig()
        self.logger = logging.getLogger(__name__)
        self.protocol = MCPProtocol()
        self.transport = StdioTransport()
        self.tools = SoftwareDevTools()
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self):
        """Register available tools"""
        self.available_tools = [
            Tool(
                name="ci_cd_automator",
                description="Enhance build, test, and deployment automation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pipeline_config": {"type": "object", "description": "CI/CD pipeline configuration"},
                        "automation_goals": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["pipeline_config"]
                }
            ),
            Tool(
                name="code_optimizer",
                description="Suggest efficient alternatives for complex code snippets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code_snippet": {"type": "string", "description": "Code to optimize"},
                        "language": {"type": "string", "description": "Programming language"},
                        "optimization_focus": {"type": "string", "enum": ["performance", "readability", "security"]}
                    },
                    "required": ["code_snippet", "language"]
                }
            ),
            Tool(
                name="api_documentation_generator",
                description="Create API documentation and auto-generate test cases",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "api_spec": {"type": "object", "description": "API specification"},
                        "documentation_type": {"type": "string", "enum": ["swagger", "postman", "markdown"]}
                    },
                    "required": ["api_spec"]
                }
            ),
            Tool(
                name="code_reviewer",
                description="Automated code review and quality assessment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code_changes": {"type": "object", "description": "Code changes to review"},
                        "review_criteria": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["code_changes"]
                }
            ),
            Tool(
                name="security_scanner",
                description="Scan code for security vulnerabilities and best practices",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "codebase": {"type": "object", "description": "Codebase to scan"},
                        "scan_type": {"type": "string", "enum": ["static", "dynamic", "dependency"]}
                    },
                    "required": ["codebase"]
                }
            ),
            Tool(
                name="performance_analyzer",
                description="Analyze code performance and suggest optimizations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "performance_data": {"type": "object", "description": "Performance metrics"},
                        "analysis_scope": {"type": "string", "enum": ["function", "module", "system"]}
                    },
                    "required": ["performance_data"]
                }
            ),
            Tool(
                name="test_generator",
                description="Generate comprehensive test suites for code",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code_module": {"type": "object", "description": "Code module to test"},
                        "test_framework": {"type": "string", "enum": ["pytest", "junit", "jest"]},
                        "coverage_target": {"type": "number", "minimum": 0, "maximum": 100}
                    },
                    "required": ["code_module"]
                }
            ),
            Tool(
                name="dependency_manager",
                description="Manage and analyze project dependencies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dependency_file": {"type": "string", "description": "Dependency file path"},
                        "action": {"type": "string", "enum": ["audit", "update", "optimize"]}
                    },
                    "required": ["dependency_file"]
                }
            ),
            Tool(
                name="architecture_analyzer",
                description="Analyze software architecture and suggest improvements",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "architecture_data": {"type": "object", "description": "Architecture information"},
                        "analysis_focus": {"type": "string", "enum": ["scalability", "maintainability", "performance"]}
                    },
                    "required": ["architecture_data"]
                }
            ),
            Tool(
                name="deployment_optimizer",
                description="Optimize deployment strategies and configurations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "deployment_config": {"type": "object", "description": "Deployment configuration"},
                        "optimization_goals": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["deployment_config"]
                }
            )
        ]
        
        # Register resources
        self.available_resources = [
            Resource(
                uri="software_dev://guides/best_practices",
                name="Software Development Best Practices",
                description="Comprehensive guide to software development best practices",
                mimeType="text/markdown"
            ),
            Resource(
                uri="software_dev://templates/code_templates",
                name="Code Templates Library",
                description="Collection of reusable code templates and patterns",
                mimeType="application/json"
            ),
            Resource(
                uri="software_dev://tools/devops_tools",
                name="DevOps Tools Reference",
                description="Reference guide for DevOps tools and practices",
                mimeType="application/json"
            )
        ]
        
        # Register prompts
        self.available_prompts = [
            Prompt(
                name="code_assistant",
                description="Get coding assistance and best practices",
                arguments=[
                    PromptArgument(name="language", description="Programming language", type="string", required=True),
                    PromptArgument(name="task", description="Coding task", type="string", required=True),
                    PromptArgument(name="context", description="Additional context", type="string", required=False)
                ]
            ),
            Prompt(
                name="debugging_helper",
                description="Get debugging assistance and troubleshooting tips",
                arguments=[
                    PromptArgument(name="error_message", description="Error message", type="string", required=True),
                    PromptArgument(name="language", description="Programming language", type="string", required=True),
                    PromptArgument(name="code_context", description="Relevant code context", type="string", required=False)
                ]
            )
        ]
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle MCP request"""
        try:
            if request.method == "initialize":
                return await self._handle_initialize(request)
            elif request.method == "tools/list":
                return await self._handle_tools_list(request)
            elif request.method == "tools/call":
                return await self._handle_tools_call(request)
            elif request.method == "resources/list":
                return await self._handle_resources_list(request)
            elif request.method == "resources/read":
                return await self._handle_resources_read(request)
            elif request.method == "prompts/list":
                return await self._handle_prompts_list(request)
            elif request.method == "prompts/get":
                return await self._handle_prompts_get(request)
            else:
                return self.protocol.create_error_response(
                    request.id, 
                    self.protocol.MCPErrorCode.METHOD_NOT_FOUND,
                    f"Unknown method: {request.method}"
                )
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return self.protocol.create_error_response(
                request.id,
                self.protocol.MCPErrorCode.INTERNAL_ERROR,
                f"Internal server error: {str(e)}"
            )
    
    async def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """Handle initialize request"""
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            "serverInfo": {
                "name": self.config.name,
                "version": self.config.version,
                "description": self.config.description
            }
        }
        return self.protocol.create_response(request.id, result)
    
    async def _handle_tools_list(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/list request"""
        tools_data = [asdict(tool) for tool in self.available_tools]
        return self.protocol.create_response(request.id, {"tools": tools_data})
    
    async def _handle_tools_call(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/call request"""
        params = request.params or {}
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Find the tool
        tool = next((t for t in self.available_tools if t.name == tool_name), None)
        if not tool:
            return self.protocol.create_error_response(
                request.id,
                self.protocol.MCPErrorCode.INVALID_PARAMS,
                f"Tool not found: {tool_name}"
            )
        
        # Execute the tool
        try:
            result = await self.tools.execute_tool(tool_name, arguments)
            return self.protocol.create_response(request.id, result)
        except Exception as e:
            return self.protocol.create_error_response(
                request.id,
                self.protocol.MCPErrorCode.INTERNAL_ERROR,
                f"Tool execution failed: {str(e)}"
            )
    
    async def _handle_resources_list(self, request: MCPRequest) -> MCPResponse:
        """Handle resources/list request"""
        resources_data = [asdict(resource) for resource in self.available_resources]
        return self.protocol.create_response(request.id, {"resources": resources_data})
    
    async def _handle_resources_read(self, request: MCPRequest) -> MCPResponse:
        """Handle resources/read request"""
        params = request.params or {}
        uri = params.get("uri")
        
        # Find the resource
        resource = next((r for r in self.available_resources if r.uri == uri), None)
        if not resource:
            return self.protocol.create_error_response(
                request.id,
                self.protocol.MCPErrorCode.INVALID_PARAMS,
                f"Resource not found: {uri}"
            )
        
        # Read the resource
        try:
            content = await self.tools.read_resource(uri)
            result = {
                "contents": [{
                    "uri": uri,
                    "mimeType": resource.mimeType,
                    "text": content
                }]
            }
            return self.protocol.create_response(request.id, result)
        except Exception as e:
            return self.protocol.create_error_response(
                request.id,
                self.protocol.MCPErrorCode.INTERNAL_ERROR,
                f"Resource read failed: {str(e)}"
            )
    
    async def _handle_prompts_list(self, request: MCPRequest) -> MCPResponse:
        """Handle prompts/list request"""
        prompts_data = [asdict(prompt) for prompt in self.available_prompts]
        return self.protocol.create_response(request.id, {"prompts": prompts_data})
    
    async def _handle_prompts_get(self, request: MCPRequest) -> MCPResponse:
        """Handle prompts/get request"""
        params = request.params or {}
        prompt_name = params.get("name")
        
        # Find the prompt
        prompt = next((p for p in self.available_prompts if p.name == prompt_name), None)
        if not prompt:
            return self.protocol.create_error_response(
                request.id,
                self.protocol.MCPErrorCode.INVALID_PARAMS,
                f"Prompt not found: {prompt_name}"
            )
        
        return self.protocol.create_response(request.id, asdict(prompt))
    
    async def run(self):
        """Run the server"""
        self.logger.info(f"Starting {self.config.name} v{self.config.version}")
        
        try:
            await self.transport.start()
            
            while True:
                # Read message from stdin
                message_data = await self.transport.receive()
                if not message_data:
                    break
                
                # Parse request
                request = self.protocol.deserialize_message(message_data)
                if not isinstance(request, MCPRequest):
                    continue
                
                # Handle request
                response = await self.handle_request(request)
                
                # Send response
                response_data = self.protocol.serialize_message(response)
                await self.transport.send(response_data)
                
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")
        except Exception as e:
            self.logger.error(f"Server error: {e}")
        finally:
            await self.transport.stop()


async def main():
    """Main entry point"""
    server = SoftwareDevMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
