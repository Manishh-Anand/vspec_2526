"""
Education MCP Server Implementation
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
from .tools import EducationTools


@dataclass
class EducationServerConfig:
    """Education server configuration"""
    name: str = "education-server"
    version: str = "1.0.0"
    description: str = "Education tools and resources server"
    domain: str = "education"


class EducationMCPServer:
    """Education MCP Server"""
    
    def __init__(self, config: Optional[EducationServerConfig] = None):
        self.config = config or EducationServerConfig()
        self.logger = logging.getLogger(__name__)
        self.protocol = MCPProtocol()
        self.transport = StdioTransport()
        self.tools = EducationTools()
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self):
        """Register available tools"""
        self.available_tools = [
            Tool(
                name="research_assistant",
                description="Extract key insights from academic papers and research documents",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_content": {"type": "string", "description": "Academic paper or research document"},
                        "focus_areas": {"type": "array", "items": {"type": "string"}, "description": "Specific areas to focus on"}
                    },
                    "required": ["document_content"]
                }
            ),
            Tool(
                name="paper_summarizer",
                description="Generate comprehensive summaries of academic papers",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "paper_content": {"type": "string", "description": "Academic paper content"},
                        "summary_length": {"type": "string", "enum": ["brief", "detailed", "comprehensive"]}
                    },
                    "required": ["paper_content"]
                }
            ),
            Tool(
                name="career_guidance",
                description="Suggest career paths and learning resources based on user skills",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "skills": {"type": "array", "items": {"type": "string"}, "description": "User skills and competencies"},
                        "interests": {"type": "array", "items": {"type": "string"}, "description": "User interests and preferences"},
                        "experience_level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]}
                    },
                    "required": ["skills"]
                }
            ),
            Tool(
                name="skill_recommender",
                description="Recommend skills and learning paths based on career goals",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "career_goal": {"type": "string", "description": "Target career or role"},
                        "current_skills": {"type": "array", "items": {"type": "string"}},
                        "timeframe": {"type": "string", "enum": ["3_months", "6_months", "1_year", "2_years"]}
                    },
                    "required": ["career_goal"]
                }
            ),
            Tool(
                name="study_planner",
                description="Create personalized study schedules based on learning habits",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "subjects": {"type": "array", "items": {"type": "object"}, "description": "Subjects and topics to study"},
                        "available_time": {"type": "object", "description": "Available study time per day/week"},
                        "learning_preferences": {"type": "object", "description": "Preferred learning methods and times"}
                    },
                    "required": ["subjects", "available_time"]
                }
            ),
            Tool(
                name="adaptive_learning",
                description="Adapt learning content based on progress and performance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "learning_data": {"type": "object", "description": "Learning progress and performance data"},
                        "content_difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                        "learning_style": {"type": "string", "enum": ["visual", "auditory", "kinesthetic"]}
                    },
                    "required": ["learning_data"]
                }
            ),
            Tool(
                name="knowledge_assessor",
                description="Assess knowledge gaps and recommend learning materials",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "subject_area": {"type": "string", "description": "Subject or topic area"},
                        "assessment_results": {"type": "object", "description": "Previous assessment results"},
                        "learning_objectives": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["subject_area"]
                }
            ),
            Tool(
                name="learning_path_generator",
                description="Generate personalized learning paths for specific goals",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "learning_goal": {"type": "string", "description": "Specific learning objective"},
                        "current_level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]},
                        "preferred_format": {"type": "array", "items": {"type": "string"}, "enum": ["video", "text", "interactive", "practice"]}
                    },
                    "required": ["learning_goal"]
                }
            ),
            Tool(
                name="progress_tracker",
                description="Track learning progress and provide insights",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "learning_activities": {"type": "array", "items": {"type": "object"}, "description": "Completed learning activities"},
                        "assessment_scores": {"type": "array", "items": {"type": "object"}, "description": "Assessment and quiz scores"},
                        "time_spent": {"type": "object", "description": "Time spent on different topics"}
                    },
                    "required": ["learning_activities"]
                }
            ),
            Tool(
                name="collaborative_learning",
                description="Facilitate group learning and peer collaboration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "group_members": {"type": "array", "items": {"type": "object"}, "description": "Group member information"},
                        "learning_topic": {"type": "string", "description": "Topic for collaborative learning"},
                        "collaboration_type": {"type": "string", "enum": ["discussion", "project", "study_group"]}
                    },
                    "required": ["group_members", "learning_topic"]
                }
            )
        ]
        
        # Register resources
        self.available_resources = [
            Resource(
                uri="education://resources/learning_materials",
                name="Learning Materials Library",
                description="Comprehensive library of educational resources",
                mimeType="application/json"
            ),
            Resource(
                uri="education://guides/study_techniques",
                name="Study Techniques Guide",
                description="Effective study methods and techniques",
                mimeType="text/markdown"
            ),
            Resource(
                uri="education://careers/industry_insights",
                name="Industry Career Insights",
                description="Career insights and industry trends",
                mimeType="application/json"
            )
        ]
        
        # Register prompts
        self.available_prompts = [
            Prompt(
                name="learning_advisor",
                description="Get personalized learning advice",
                arguments=[
                    PromptArgument(name="goal", description="Learning goal", type="string", required=True),
                    PromptArgument(name="background", description="Educational background", type="string", required=True),
                    PromptArgument(name="constraints", description="Time or resource constraints", type="string", required=False)
                ]
            ),
            Prompt(
                name="study_motivator",
                description="Generate motivational content for studying",
                arguments=[
                    PromptArgument(name="subject", description="Subject being studied", type="string", required=True),
                    PromptArgument(name="difficulty", description="Current difficulty level", type="string", required=True),
                    PromptArgument(name="motivation_type", description="Type of motivation needed", type="string", required=False)
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
    server = EducationMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
