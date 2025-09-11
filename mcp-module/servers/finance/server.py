"""
Finance MCP Server Implementation
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ...src.core.protocol import (
    MCPProtocol, MCPRequest, MCPResponse, MCPErrorResponse,
    Tool, Resource, Prompt, PromptArgument
)
from ...src.transport.stdio import StdioTransport
from .tools import FinanceTools


@dataclass
class FinanceServerConfig:
    """Finance server configuration"""
    name: str = "finance-server"
    version: str = "1.0.0"
    description: str = "Financial tools and resources server"
    domain: str = "finance"


class FinanceMCPServer:
    """Finance MCP Server"""
    
    def __init__(self, config: Optional[FinanceServerConfig] = None):
        self.config = config or FinanceServerConfig()
        self.logger = logging.getLogger(__name__)
        self.protocol = MCPProtocol()
        self.transport = StdioTransport()
        self.tools = FinanceTools()
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self):
        """Register available tools"""
        self.available_tools = [
            Tool(
                name="file_reader",
                description="Read and parse financial files",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to file"},
                        "file_type": {"type": "string", "enum": ["csv", "pdf", "json"]}
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="bank_statement_parser",
                description="Parse bank statements and extract transaction data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "statement_data": {"type": "string", "description": "Bank statement data"},
                        "format": {"type": "string", "enum": ["csv", "pdf", "json"]}
                    },
                    "required": ["statement_data"]
                }
            ),
            Tool(
                name="subscription_detector",
                description="Detect recurring subscriptions and payments",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "transactions": {"type": "array", "items": {"type": "object"}},
                        "threshold": {"type": "number", "default": 0.9}
                    },
                    "required": ["transactions"]
                }
            ),
            Tool(
                name="recurring_charge_identifier",
                description="Identify recurring charges and patterns",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "transactions": {"type": "array", "items": {"type": "object"}},
                        "time_period": {"type": "string", "enum": ["monthly", "quarterly", "yearly"]}
                    },
                    "required": ["transactions"]
                }
            ),
            Tool(
                name="income_expense_tracker",
                description="Track income and expenses",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "transactions": {"type": "array", "items": {"type": "object"}},
                        "categories": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["transactions"]
                }
            ),
            Tool(
                name="budget_planner_tool",
                description="Create and manage budget plans",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "income": {"type": "number"},
                        "expenses": {"type": "array", "items": {"type": "object"}},
                        "goals": {"type": "array", "items": {"type": "object"}}
                    },
                    "required": ["income", "expenses"]
                }
            ),
            Tool(
                name="financial_advice_generator",
                description="Generate personalized financial advice",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "financial_profile": {"type": "object"},
                        "goals": {"type": "array", "items": {"type": "string"}},
                        "risk_tolerance": {"type": "string", "enum": ["low", "medium", "high"]}
                    },
                    "required": ["financial_profile"]
                }
            ),
            Tool(
                name="financial_management_tool",
                description="Manage financial portfolios and investments",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "portfolio": {"type": "object"},
                        "market_data": {"type": "object"},
                        "strategy": {"type": "string"}
                    },
                    "required": ["portfolio"]
                }
            ),
            Tool(
                name="spending_pattern_visualizer",
                description="Create visualizations of spending patterns",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "spending_data": {"type": "array", "items": {"type": "object"}},
                        "chart_type": {"type": "string", "enum": ["pie", "bar", "line"]},
                        "time_period": {"type": "string"}
                    },
                    "required": ["spending_data"]
                }
            ),
            Tool(
                name="graph_chart_creator",
                description="Create financial charts and graphs",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "array", "items": {"type": "object"}},
                        "chart_type": {"type": "string"},
                        "options": {"type": "object"}
                    },
                    "required": ["data", "chart_type"]
                }
            ),
            Tool(
                name="progress_monitor_tool",
                description="Monitor financial progress and goals",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "goals": {"type": "array", "items": {"type": "object"}},
                        "current_status": {"type": "object"},
                        "metrics": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["goals", "current_status"]
                }
            ),
            Tool(
                name="budget_plan_adjuster",
                description="Adjust budget plans based on progress",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "current_budget": {"type": "object"},
                        "performance_data": {"type": "object"},
                        "adjustment_rules": {"type": "array", "items": {"type": "object"}}
                    },
                    "required": ["current_budget", "performance_data"]
                }
            )
        ]
        
        # Register resources
        self.available_resources = [
            Resource(
                uri="finance://reports/monthly_summary",
                name="Monthly Financial Summary",
                description="Monthly financial summary reports",
                mimeType="application/json"
            ),
            Resource(
                uri="finance://reports/budget_analysis",
                name="Budget Analysis Report",
                description="Detailed budget analysis and recommendations",
                mimeType="application/json"
            ),
            Resource(
                uri="finance://data/market_trends",
                name="Market Trends Data",
                description="Current market trends and analysis",
                mimeType="application/json"
            )
        ]
        
        # Register prompts
        self.available_prompts = [
            Prompt(
                name="budget_advice",
                description="Generate personalized budget advice",
                arguments=[
                    PromptArgument(name="income", description="Monthly income", type="number", required=True),
                    PromptArgument(name="expenses", description="Monthly expenses", type="object", required=True),
                    PromptArgument(name="goals", description="Financial goals", type="array", required=False)
                ]
            ),
            Prompt(
                name="investment_advice",
                description="Provide investment recommendations",
                arguments=[
                    PromptArgument(name="risk_tolerance", description="Risk tolerance level", type="string", required=True),
                    PromptArgument(name="investment_amount", description="Amount to invest", type="number", required=True),
                    PromptArgument(name="time_horizon", description="Investment time horizon", type="string", required=True)
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
    server = FinanceMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
