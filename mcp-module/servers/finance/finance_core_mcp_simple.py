#!/usr/bin/env python3
"""
Simplified Finance Core MCP Server
Port: 3001
Domain: Finance
Implements: Tools, Resources, Prompts
Transport: HTTP only
"""

import json
import logging
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
import random
from dataclasses import dataclass
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock data
MOCK_TRANSACTIONS = [
    {"id": "txn_001", "amount": 1250.50, "type": "credit", "description": "Salary deposit", "date": "2024-01-15"},
    {"id": "txn_002", "amount": -89.99, "type": "debit", "description": "Grocery store", "date": "2024-01-16"},
    {"id": "txn_003", "amount": -250.00, "type": "debit", "description": "Rent payment", "date": "2024-01-17"}
]

MOCK_MARKET_DATA = {
    "AAPL": {"price": 185.50, "change": 2.5, "volume": 50000000},
    "GOOGL": {"price": 142.30, "change": -1.2, "volume": 30000000},
    "MSFT": {"price": 378.90, "change": 3.1, "volume": 40000000}
}

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
                        "account_id": {"type": "string", "description": "Account identifier"}
                    },
                    "required": ["account_id"]
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
            }
        }
    
    def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP JSON-RPC 2.0 requests"""
        try:
            method = request_data.get("method")
            request_id = request_data.get("id")
            
            logger.info(f"Handling request: {method}")
            
            if method == "initialize":
                return self._handle_initialize(request_id)
            elif method == "tools/list":
                return self._handle_list_tools(request_id)
            elif method == "tools/call":
                return self._handle_call_tool(request_data)
            elif method == "resources/list":
                return self._handle_list_resources(request_id)
            elif method == "resources/read":
                return self._handle_read_resource(request_data)
            elif method == "prompts/list":
                return self._handle_list_prompts(request_id)
            elif method == "prompts/describe":
                return self._handle_describe_prompt(request_data)
            else:
                return self._create_error_response(request_id, -32601, f"Method not found: {method}")
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return self._create_error_response(
                request_data.get("id"), 
                -32603, 
                f"Internal error: {str(e)}"
            )
    
    def _handle_initialize(self, request_id: str) -> Dict[str, Any]:
        """Handle initialization request"""
        logger.info("Initializing finance MCP server")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
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
    
    def _handle_list_tools(self, request_id: str) -> Dict[str, Any]:
        """Handle tools listing request"""
        logger.info("Listing available tools")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": list(self.tools.values())
            }
        }
    
    def _handle_call_tool(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution request"""
        tool_name = request_data.get("params", {}).get("name")
        arguments = request_data.get("params", {}).get("arguments", {})
        request_id = request_data.get("id")
        
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        if tool_name not in self.tools:
            return self._create_error_response(request_id, -32601, f"Tool not found: {tool_name}")
        
        try:
            result = self._execute_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
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
            return self._create_error_response(request_id, -32603, f"Tool execution failed: {str(e)}")
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool"""
        if tool_name == "file_reader":
            return self._execute_file_reader(arguments)
        elif tool_name == "bank_statement_parser":
            return self._execute_bank_statement_parser(arguments)
        elif tool_name == "transaction_analyzer":
            return self._execute_transaction_analyzer(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _execute_file_reader(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file reader tool"""
        file_path = arguments.get("file_path")
        file_type = arguments.get("file_type", "unknown")
        
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
    
    def _execute_bank_statement_parser(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute bank statement parser tool"""
        statement_path = arguments.get("statement_path")
        bank_type = arguments.get("bank_type", "generic")
        
        return {
            "status": "success",
            "statement_path": statement_path,
            "bank_type": bank_type,
            "transactions": MOCK_TRANSACTIONS,
            "summary": {
                "total_transactions": len(MOCK_TRANSACTIONS),
                "total_credits": sum(t["amount"] for t in MOCK_TRANSACTIONS if t["amount"] > 0),
                "total_debits": abs(sum(t["amount"] for t in MOCK_TRANSACTIONS if t["amount"] < 0))
            }
        }
    
    def _execute_transaction_analyzer(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute transaction analyzer tool"""
        account_id = arguments.get("account_id")
        
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
    
    def _handle_list_resources(self, request_id: str) -> Dict[str, Any]:
        """Handle resources listing request"""
        logger.info("Listing available resources")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": list(self.resources.values())
            }
        }
    
    def _handle_read_resource(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource reading request"""
        uri = request_data.get("params", {}).get("uri")
        request_id = request_data.get("id")
        
        logger.info(f"Reading resource: {uri}")
        
        try:
            content = self._read_resource(uri)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
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
            return self._create_error_response(request_id, -32603, f"Resource reading failed: {str(e)}")
    
    def _read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a specific resource"""
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
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    
    def _handle_list_prompts(self, request_id: str) -> Dict[str, Any]:
        """Handle prompts listing request"""
        logger.info("Listing available prompts")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "prompts": list(self.prompts.values())
            }
        }
    
    def _handle_describe_prompt(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompt description request"""
        name = request_data.get("params", {}).get("name")
        request_id = request_data.get("id")
        
        logger.info(f"Describing prompt: {name}")
        
        if name not in self.prompts:
            return self._create_error_response(request_id, -32601, f"Prompt not found: {name}")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
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

# HTTP Server Handler
class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP server"""
    
    def __init__(self, *args, **kwargs):
        self.mcp_server = FinanceMCPServer()
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests (MCP protocol)"""
        if self.path == "/mcp":
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                # Handle MCP request
                response = self.mcp_server.handle_request(request_data)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                logger.error(f"Error handling POST request: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        """Handle GET requests (health check)"""
        if self.path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "server": "finance-core-mcp"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def run_server(port=3001):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MCPRequestHandler)
    logger.info(f"Starting Finance Core MCP server on port {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        httpd.shutdown()

if __name__ == "__main__":
    run_server(3001)
