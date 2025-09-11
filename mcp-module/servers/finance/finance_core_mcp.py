#!/usr/bin/env python3
"""
Finance Core MCP Server
Port: 3001
Domain: Finance
Implements: Tools, Resources, Prompts
Transport: HTTP and stdio
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import random
from dataclasses import dataclass

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('finance_core_mcp.log')
    ]
)
logger = logging.getLogger(__name__)

# Mock data for finance operations
MOCK_TRANSACTIONS = [
    {"id": "txn_001", "amount": 1250.50, "type": "credit", "description": "Salary deposit", "date": "2024-01-15"},
    {"id": "txn_002", "amount": -89.99, "type": "debit", "description": "Grocery store", "date": "2024-01-16"},
    {"id": "txn_003", "amount": -250.00, "type": "debit", "description": "Rent payment", "date": "2024-01-17"},
    {"id": "txn_004", "amount": 500.00, "type": "credit", "description": "Freelance payment", "date": "2024-01-18"},
    {"id": "txn_005", "amount": -45.00, "type": "debit", "description": "Gas station", "date": "2024-01-19"}
]

MOCK_MARKET_DATA = {
    "AAPL": {"price": 185.50, "change": 2.5, "volume": 50000000},
    "GOOGL": {"price": 142.30, "change": -1.2, "volume": 30000000},
    "MSFT": {"price": 378.90, "change": 3.1, "volume": 40000000},
    "TSLA": {"price": 245.20, "change": -0.8, "volume": 60000000}
}

@dataclass
class MCPRequest:
    """MCP JSON-RPC 2.0 Request"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

@dataclass
class MCPResponse:
    """MCP JSON-RPC 2.0 Response"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class FinanceMCPServer:
    """Finance Core MCP Server implementing all three primitives"""
    
    def __init__(self):
        self.server_info = {
            "name": "finance-core-mcp",
            "version": "1.0.0",
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": True
            }
        }
        self.tools = self._initialize_tools()
        self.resources = self._initialize_resources()
        self.prompts = self._initialize_prompts()
        
    def _initialize_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available tools"""
        return {
            "file_reader": {
                "name": "file_reader",
                "description": "Read and parse financial documents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the file to read"},
                        "file_type": {"type": "string", "enum": ["pdf", "csv", "json"], "description": "Type of file"}
                    },
                    "required": ["file_path"]
                }
            },
            "bank_statement_parser": {
                "name": "bank_statement_parser",
                "description": "Parse bank statements and extract transaction data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "statement_path": {"type": "string", "description": "Path to bank statement file"},
                        "bank_type": {"type": "string", "description": "Type of bank (optional)"}
                    },
                    "required": ["statement_path"]
                }
            },
            "transaction_analyzer": {
                "name": "transaction_analyzer",
                "description": "Analyze transaction patterns and generate insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "account_id": {"type": "string", "description": "Account identifier"},
                        "date_range": {"type": "object", "properties": {
                            "start": {"type": "string", "format": "date"},
                            "end": {"type": "string", "format": "date"}
                        }}
                    },
                    "required": ["account_id"]
                }
            },
            "budget_calculator": {
                "name": "budget_calculator",
                "description": "Calculate budget based on income and expenses",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "income": {"type": "number", "description": "Monthly income"},
                        "expenses": {"type": "array", "items": {"type": "object"}},
                        "savings_goal": {"type": "number", "description": "Monthly savings goal"}
                    },
                    "required": ["income"]
                }
            }
        }
    
    def _initialize_resources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available resources"""
        return {
            "transaction_history": {
                "name": "transaction_history",
                "description": "Historical transaction data",
                "uri": "finance://transactions/*",
                "mimeType": "application/json"
            },
            "market_data": {
                "name": "market_data",
                "description": "Real-time market information",
                "uri": "finance://market/*",
                "mimeType": "application/json"
            },
            "account_balance": {
                "name": "account_balance",
                "description": "Current account balances",
                "uri": "finance://accounts/*/balance",
                "mimeType": "application/json"
            },
            "investment_portfolio": {
                "name": "investment_portfolio",
                "description": "Investment portfolio data",
                "uri": "finance://portfolio/*",
                "mimeType": "application/json"
            }
        }
    
    def _initialize_prompts(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available prompts"""
        return {
            "financial_advice": {
                "name": "financial_advice",
                "description": "Generate personalized financial advice",
                "arguments": {
                    "type": "object",
                    "properties": {
                        "income": {"type": "number", "description": "Monthly income"},
                        "expenses": {"type": "number", "description": "Monthly expenses"},
                        "goals": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "budget_guidance": {
                "name": "budget_guidance",
                "description": "Provide budget planning guidance",
                "arguments": {
                    "type": "object",
                    "properties": {
                        "current_budget": {"type": "object"},
                        "financial_goals": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "investment_recommendation": {
                "name": "investment_recommendation",
                "description": "Generate investment recommendations",
                "arguments": {
                    "type": "object",
                    "properties": {
                        "risk_tolerance": {"type": "string", "enum": ["low", "medium", "high"]},
                        "investment_amount": {"type": "number"},
                        "time_horizon": {"type": "string"}
                    }
                }
            },
            "expense_analysis": {
                "name": "expense_analysis",
                "description": "Analyze spending patterns and provide insights",
                "arguments": {
                    "type": "object",
                    "properties": {
                        "transactions": {"type": "array", "items": {"type": "object"}},
                        "categories": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        }
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP JSON-RPC 2.0 requests"""
        try:
            request = MCPRequest(**request_data)
            logger.info(f"Handling request: {request.method}")
            
            if request.method == "initialize":
                return self._handle_initialize(request)
            elif request.method == "tools/list":
                return self._handle_list_tools(request)
            elif request.method == "tools/call":
                return await self._handle_call_tool(request)
            elif request.method == "resources/list":
                return self._handle_list_resources(request)
            elif request.method == "resources/read":
                return await self._handle_read_resource(request)
            elif request.method == "prompts/list":
                return self._handle_list_prompts(request)
            elif request.method == "prompts/describe":
                return self._handle_describe_prompt(request)
            else:
                return self._create_error_response(request.id, -32601, f"Method not found: {request.method}")
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return self._create_error_response(
                request_data.get("id"), 
                -32603, 
                f"Internal error: {str(e)}"
            )
    
    def _handle_initialize(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle initialization request"""
        logger.info("Initializing finance MCP server")
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": self.server_info
            }
        }
    
    def _handle_list_tools(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle tools listing request"""
        logger.info("Listing available tools")
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "tools": list(self.tools.values())
            }
        }
    
    async def _handle_call_tool(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle tool execution request"""
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        if tool_name not in self.tools:
            return self._create_error_response(request.id, -32601, f"Tool not found: {tool_name}")
        
        try:
            result = await self._execute_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return self._create_error_response(request.id, -32603, f"Tool execution failed: {str(e)}")
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool"""
        if tool_name == "file_reader":
            return await self._execute_file_reader(arguments)
        elif tool_name == "bank_statement_parser":
            return await self._execute_bank_statement_parser(arguments)
        elif tool_name == "transaction_analyzer":
            return await self._execute_transaction_analyzer(arguments)
        elif tool_name == "budget_calculator":
            return await self._execute_budget_calculator(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _execute_file_reader(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file reader tool"""
        file_path = arguments.get("file_path")
        file_type = arguments.get("file_type", "unknown")
        
        # Simulate file reading
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "status": "success",
            "file_path": file_path,
            "file_type": file_type,
            "content": f"Mock content from {file_path}",
            "metadata": {
                "size": random.randint(1000, 10000),
                "last_modified": datetime.now().isoformat(),
                "encoding": "utf-8"
            }
        }
    
    async def _execute_bank_statement_parser(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute bank statement parser tool"""
        statement_path = arguments.get("statement_path")
        bank_type = arguments.get("bank_type", "generic")
        
        await asyncio.sleep(0.2)  # Simulate processing time
        
        return {
            "status": "success",
            "statement_path": statement_path,
            "bank_type": bank_type,
            "transactions": MOCK_TRANSACTIONS[:3],  # Return first 3 transactions
            "summary": {
                "total_transactions": len(MOCK_TRANSACTIONS),
                "total_credits": sum(t["amount"] for t in MOCK_TRANSACTIONS if t["amount"] > 0),
                "total_debits": abs(sum(t["amount"] for t in MOCK_TRANSACTIONS if t["amount"] < 0))
            }
        }
    
    async def _execute_transaction_analyzer(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute transaction analyzer tool"""
        account_id = arguments.get("account_id")
        
        await asyncio.sleep(0.3)  # Simulate processing time
        
        return {
            "status": "success",
            "account_id": account_id,
            "analysis": {
                "spending_patterns": {
                    "highest_category": "groceries",
                    "average_daily_spend": 45.50,
                    "peak_spending_day": "Monday"
                },
                "savings_rate": 0.25,
                "risk_score": "low",
                "recommendations": [
                    "Consider increasing emergency fund",
                    "Review subscription services",
                    "Set up automatic savings"
                ]
            }
        }
    
    async def _execute_budget_calculator(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute budget calculator tool"""
        income = arguments.get("income", 0)
        expenses = arguments.get("expenses", [])
        savings_goal = arguments.get("savings_goal", 0)
        
        await asyncio.sleep(0.1)  # Simulate processing time
        
        total_expenses = sum(exp.get("amount", 0) for exp in expenses)
        available_for_savings = income - total_expenses
        
        return {
            "status": "success",
            "budget_summary": {
                "income": income,
                "total_expenses": total_expenses,
                "available_for_savings": available_for_savings,
                "savings_goal": savings_goal,
                "goal_achievement": (available_for_savings / savings_goal * 100) if savings_goal > 0 else 0
            },
            "recommendations": [
                "Track all expenses for better visibility",
                "Set up automatic transfers to savings",
                "Review discretionary spending"
            ]
        }
    
    def _handle_list_resources(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle resources listing request"""
        logger.info("Listing available resources")
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "resources": list(self.resources.values())
            }
        }
    
    async def _handle_read_resource(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle resource reading request"""
        uri = request.params.get("uri")
        
        logger.info(f"Reading resource: {uri}")
        
        try:
            content = await self._read_resource(uri)
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(content, indent=2)
                        }
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Resource reading error: {e}")
            return self._create_error_response(request.id, -32603, f"Resource reading failed: {str(e)}")
    
    async def _read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a specific resource"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        if "transactions" in uri:
            return {
                "transactions": MOCK_TRANSACTIONS,
                "total_count": len(MOCK_TRANSACTIONS),
                "last_updated": datetime.now().isoformat()
            }
        elif "market" in uri:
            return {
                "market_data": MOCK_MARKET_DATA,
                "timestamp": datetime.now().isoformat(),
                "source": "finance-core-mcp"
            }
        elif "balance" in uri:
            return {
                "account_balances": {
                    "checking": 5420.75,
                    "savings": 12500.00,
                    "investment": 45000.00
                },
                "last_updated": datetime.now().isoformat()
            }
        elif "portfolio" in uri:
            return {
                "portfolio": {
                    "total_value": 45000.00,
                    "holdings": [
                        {"symbol": "AAPL", "shares": 10, "value": 1855.00},
                        {"symbol": "GOOGL", "shares": 5, "value": 711.50},
                        {"symbol": "MSFT", "shares": 8, "value": 3031.20}
                    ],
                    "performance": {
                        "daily_change": 2.5,
                        "monthly_change": 8.3,
                        "yearly_change": 15.7
                    }
                }
            }
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    
    def _handle_list_prompts(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle prompts listing request"""
        logger.info("Listing available prompts")
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "prompts": list(self.prompts.values())
            }
        }
    
    def _handle_describe_prompt(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle prompt description request"""
        name = request.params.get("name")
        
        logger.info(f"Describing prompt: {name}")
        
        if name not in self.prompts:
            return self._create_error_response(request.id, -32601, f"Prompt not found: {name}")
        
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": self.prompts[name]
        }
    
    def _create_error_response(self, request_id: Optional[str], code: int, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }

# HTTP Server Implementation
def http_server():
    """Run HTTP server on port 3001"""
    import uvicorn
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="Finance Core MCP Server", version="1.0.0")
    server = FinanceMCPServer()
    
    @app.post("/mcp")
    async def handle_mcp_request(request: Request):
        """Handle MCP requests via HTTP"""
        try:
            body = await request.json()
            response = await server.handle_request(body)
            return JSONResponse(content=response)
        except Exception as e:
            logger.error(f"HTTP server error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": str(e)}
            )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "server": "finance-core-mcp"}
    
    logger.info("Starting Finance Core MCP HTTP server on port 3001")
    uvicorn.run(app, host="0.0.0.0", port=3001)

# Stdio Server Implementation
async def stdio_server():
    """Run stdio server for process communication"""
    server = FinanceMCPServer()
    
    logger.info("Starting Finance Core MCP stdio server")
    
    while True:
        try:
            # Read request from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request_data = json.loads(line.strip())
            response = await server.handle_request(request_data)
            
            # Write response to stdout
            response_line = json.dumps(response) + "\n"
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.write, response_line)
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)
            
        except Exception as e:
            logger.error(f"Stdio server error: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            error_line = json.dumps(error_response) + "\n"
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.write, error_line)
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Run HTTP server
        http_server()
    else:
        # Run stdio server
        asyncio.run(stdio_server())
