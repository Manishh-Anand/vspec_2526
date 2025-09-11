"""
Sports MCP Server Implementation
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
from .tools import SportsTools


@dataclass
class SportsServerConfig:
    """Sports server configuration"""
    name: str = "sports-server"
    version: str = "1.0.0"
    description: str = "Sports tools and resources server"
    domain: str = "sports"


class SportsMCPServer:
    """Sports MCP Server"""
    
    def __init__(self, config: Optional[SportsServerConfig] = None):
        self.config = config or SportsServerConfig()
        self.logger = logging.getLogger(__name__)
        self.protocol = MCPProtocol()
        self.transport = StdioTransport()
        self.tools = SportsTools()
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self):
        """Register available tools"""
        self.available_tools = [
            Tool(
                name="performance_analyzer",
                description="Analyze athlete performance using movement and biomechanics data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "performance_data": {"type": "object", "description": "Athlete performance metrics"},
                        "analysis_type": {"type": "string", "enum": ["movement", "biomechanics", "training"]}
                    },
                    "required": ["performance_data"]
                }
            ),
            Tool(
                name="match_predictor",
                description="Predict match outcomes based on historical data and analytics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "team_data": {"type": "object", "description": "Team performance data"},
                        "match_conditions": {"type": "object", "description": "Match-specific conditions"}
                    },
                    "required": ["team_data"]
                }
            ),
            Tool(
                name="training_optimizer",
                description="Optimize training programs based on performance data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "athlete_profile": {"type": "object", "description": "Athlete information and goals"},
                        "current_performance": {"type": "object", "description": "Current performance metrics"}
                    },
                    "required": ["athlete_profile"]
                }
            ),
            Tool(
                name="injury_prevention",
                description="Analyze injury risk and recommend prevention strategies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "athlete_data": {"type": "object", "description": "Athlete health and performance data"},
                        "sport_type": {"type": "string", "description": "Type of sport"}
                    },
                    "required": ["athlete_data"]
                }
            ),
            Tool(
                name="nutrition_planner",
                description="Create personalized nutrition plans for athletes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "athlete_info": {"type": "object", "description": "Athlete information and dietary preferences"},
                        "training_schedule": {"type": "object", "description": "Training and competition schedule"}
                    },
                    "required": ["athlete_info"]
                }
            ),
            Tool(
                name="recovery_monitor",
                description="Monitor recovery progress and recommend recovery strategies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "recovery_data": {"type": "object", "description": "Recovery metrics and indicators"},
                        "training_load": {"type": "object", "description": "Recent training load and intensity"}
                    },
                    "required": ["recovery_data"]
                }
            ),
            Tool(
                name="tactical_analyzer",
                description="Analyze game tactics and strategies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "game_data": {"type": "object", "description": "Game footage and statistics"},
                        "analysis_focus": {"type": "string", "enum": ["offense", "defense", "transition"]}
                    },
                    "required": ["game_data"]
                }
            ),
            Tool(
                name="scout_reporter",
                description="Generate scouting reports for players and teams",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scouting_data": {"type": "object", "description": "Player or team scouting information"},
                        "report_type": {"type": "string", "enum": ["player", "team", "opponent"]}
                    },
                    "required": ["scouting_data"]
                }
            ),
            Tool(
                name="fitness_tracker",
                description="Track fitness metrics and progress over time",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "fitness_data": {"type": "object", "description": "Fitness metrics and measurements"},
                        "tracking_period": {"type": "string", "enum": ["daily", "weekly", "monthly"]}
                    },
                    "required": ["fitness_data"]
                }
            ),
            Tool(
                name="competition_planner",
                description="Plan and optimize competition schedules",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "team_schedule": {"type": "object", "description": "Current team schedule and constraints"},
                        "optimization_goals": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["team_schedule"]
                }
            )
        ]
        
        # Register resources
        self.available_resources = [
            Resource(
                uri="sports://data/performance_metrics",
                name="Performance Metrics Database",
                description="Comprehensive database of sports performance metrics",
                mimeType="application/json"
            ),
            Resource(
                uri="sports://guides/training_methods",
                name="Training Methods Guide",
                description="Best practices for sports training and conditioning",
                mimeType="text/markdown"
            ),
            Resource(
                uri="sports://analytics/match_statistics",
                name="Match Statistics Analytics",
                description="Historical match statistics and analytics",
                mimeType="application/json"
            )
        ]
        
        # Register prompts
        self.available_prompts = [
            Prompt(
                name="performance_coach",
                description="Get personalized performance coaching advice",
                arguments=[
                    PromptArgument(name="sport", description="Sport type", type="string", required=True),
                    PromptArgument(name="level", description="Performance level", type="string", required=True),
                    PromptArgument(name="goals", description="Performance goals", type="string", required=True)
                ]
            ),
            Prompt(
                name="training_motivator",
                description="Generate motivational content for training",
                arguments=[
                    PromptArgument(name="athlete_type", description="Type of athlete", type="string", required=True),
                    PromptArgument(name="training_phase", description="Current training phase", type="string", required=True),
                    PromptArgument(name="motivation_focus", description="Motivation focus area", type="string", required=False)
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
    server = SportsMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
