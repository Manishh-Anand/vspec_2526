"""
Productivity MCP Server Implementation
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
from .tools import ProductivityTools


@dataclass
class ProductivityServerConfig:
    """Productivity server configuration"""
    name: str = "productivity-server"
    version: str = "1.0.0"
    description: str = "Productivity tools and resources server"
    domain: str = "productivity"


class ProductivityMCPServer:
    """Productivity MCP Server"""
    
    def __init__(self, config: Optional[ProductivityServerConfig] = None):
        self.config = config or ProductivityServerConfig()
        self.logger = logging.getLogger(__name__)
        self.protocol = MCPProtocol()
        self.transport = StdioTransport()
        self.tools = ProductivityTools()
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self):
        """Register available tools"""
        self.available_tools = [
            Tool(
                name="email_summarizer",
                description="Summarize lengthy emails and suggest quick responses",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_content": {"type": "string", "description": "Email content to summarize"},
                        "context": {"type": "string", "description": "Additional context"}
                    },
                    "required": ["email_content"]
                }
            ),
            Tool(
                name="meeting_assistant",
                description="Automate scheduling, rescheduling, and meeting notes generation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "meeting_data": {"type": "object", "description": "Meeting information"},
                        "action": {"type": "string", "enum": ["schedule", "reschedule", "notes"]}
                    },
                    "required": ["meeting_data", "action"]
                }
            ),
            Tool(
                name="task_converter",
                description="Convert spoken ideas to actionable tasks with deadlines",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "audio_text": {"type": "string", "description": "Transcribed audio text"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                    },
                    "required": ["audio_text"]
                }
            ),
            Tool(
                name="calendar_optimizer",
                description="Optimize calendar scheduling and time management",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "calendar_data": {"type": "object", "description": "Calendar events and preferences"},
                        "optimization_goal": {"type": "string", "enum": ["productivity", "work_life_balance", "focus_time"]}
                    },
                    "required": ["calendar_data"]
                }
            ),
            Tool(
                name="smart_reply_generator",
                description="Generate context-aware email and message replies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message_content": {"type": "string", "description": "Original message content"},
                        "tone": {"type": "string", "enum": ["formal", "casual", "professional"]},
                        "length": {"type": "string", "enum": ["short", "medium", "long"]}
                    },
                    "required": ["message_content"]
                }
            ),
            Tool(
                name="focus_time_scheduler",
                description="Schedule focused work sessions and breaks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workload": {"type": "object", "description": "Tasks and priorities"},
                        "preferences": {"type": "object", "description": "Work preferences and constraints"}
                    },
                    "required": ["workload"]
                }
            ),
            Tool(
                name="collaboration_enhancer",
                description="Enhance team collaboration and communication",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "team_data": {"type": "object", "description": "Team information and dynamics"},
                        "collaboration_goals": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["team_data"]
                }
            ),
            Tool(
                name="workflow_automator",
                description="Automate repetitive workflows and processes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_steps": {"type": "array", "items": {"type": "object"}},
                        "automation_level": {"type": "string", "enum": ["partial", "full"]}
                    },
                    "required": ["workflow_steps"]
                }
            ),
            Tool(
                name="productivity_analyzer",
                description="Analyze productivity patterns and suggest improvements",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "productivity_data": {"type": "object", "description": "Productivity metrics and patterns"},
                        "analysis_period": {"type": "string", "enum": ["daily", "weekly", "monthly"]}
                    },
                    "required": ["productivity_data"]
                }
            ),
            Tool(
                name="goal_tracker",
                description="Track progress towards productivity goals",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "goals": {"type": "array", "items": {"type": "object"}},
                        "progress_data": {"type": "object", "description": "Current progress information"}
                    },
                    "required": ["goals"]
                }
            )
        ]
        
        # Register resources
        self.available_resources = [
            Resource(
                uri="productivity://templates/email_responses",
                name="Email Response Templates",
                description="Templates for common email responses",
                mimeType="application/json"
            ),
            Resource(
                uri="productivity://guides/time_management",
                name="Time Management Guide",
                description="Best practices for time management",
                mimeType="text/markdown"
            ),
            Resource(
                uri="productivity://templates/meeting_agendas",
                name="Meeting Agenda Templates",
                description="Templates for effective meeting agendas",
                mimeType="application/json"
            )
        ]
        
        # Register prompts
        self.available_prompts = [
            Prompt(
                name="email_composer",
                description="Compose professional emails",
                arguments=[
                    PromptArgument(name="recipient", description="Email recipient", type="string", required=True),
                    PromptArgument(name="subject", description="Email subject", type="string", required=True),
                    PromptArgument(name="context", description="Email context", type="string", required=True),
                    PromptArgument(name="tone", description="Email tone", type="string", required=False)
                ]
            ),
            Prompt(
                name="meeting_planner",
                description="Plan effective meetings",
                arguments=[
                    PromptArgument(name="purpose", description="Meeting purpose", type="string", required=True),
                    PromptArgument(name="participants", description="Meeting participants", type="array", required=True),
                    PromptArgument(name="duration", description="Meeting duration", type="string", required=True)
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
    server = ProductivityMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
