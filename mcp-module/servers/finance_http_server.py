#!/usr/bin/env python3
"""
Simple HTTP-based Finance MCP Server
Runs on port 3001 for testing
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Finance MCP Server", version="1.0.0")

# Mock data for finance tools, resources, and prompts
FINANCE_TOOLS = [
    {
        "name": "file_reader",
        "description": "Read and parse financial files",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to file"},
                "file_type": {"type": "string", "enum": ["csv", "pdf", "json"]}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "bank_statement_parser",
        "description": "Parse bank statements and extract transaction data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "statement_data": {"type": "string", "description": "Bank statement data"},
                "format": {"type": "string", "enum": ["csv", "pdf", "json"]}
            },
            "required": ["statement_data"]
        }
    },
    {
        "name": "subscription_detector",
        "description": "Detect recurring subscriptions and payments",
        "inputSchema": {
            "type": "object",
            "properties": {
                "transactions": {"type": "array", "items": {"type": "object"}},
                "threshold": {"type": "number", "default": 0.9}
            },
            "required": ["transactions"]
        }
    },
    {
        "name": "income_expense_tracker",
        "description": "Track income and expenses",
        "inputSchema": {
            "type": "object",
            "properties": {
                "transactions": {"type": "array", "items": {"type": "object"}},
                "categories": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["transactions"]
        }
    },
    {
        "name": "budget_planner_tool",
        "description": "Create and manage budget plans",
        "inputSchema": {
            "type": "object",
            "properties": {
                "income": {"type": "number"},
                "expenses": {"type": "array", "items": {"type": "object"}},
                "goals": {"type": "array", "items": {"type": "object"}}
            },
            "required": ["income", "expenses"]
        }
    },
    {
        "name": "financial_advice_generator",
        "description": "Generate personalized financial advice",
        "inputSchema": {
            "type": "object",
            "properties": {
                "financial_profile": {"type": "object"},
                "goals": {"type": "array", "items": {"type": "string"}},
                "risk_tolerance": {"type": "string", "enum": ["low", "medium", "high"]}
            },
            "required": ["financial_profile"]
        }
    }
]

FINANCE_RESOURCES = [
    {
        "uri": "finance://reports/monthly_summary",
        "name": "Monthly Financial Summary",
        "description": "Monthly financial summary reports",
        "mimeType": "application/json"
    },
    {
        "uri": "finance://reports/budget_analysis",
        "name": "Budget Analysis Report",
        "description": "Detailed budget analysis and recommendations",
        "mimeType": "application/json"
    },
    {
        "uri": "finance://data/market_trends",
        "name": "Market Trends Data",
        "description": "Current market trends and analysis",
        "mimeType": "application/json"
    },
    {
        "uri": "finance://transactions/*",
        "name": "Transaction History",
        "description": "Historical transaction data",
        "mimeType": "application/json"
    },
    {
        "uri": "finance://market/*",
        "name": "Market Data",
        "description": "Real-time market information",
        "mimeType": "application/json"
    }
]

FINANCE_PROMPTS = [
    {
        "name": "budget_advice",
        "description": "Generate personalized budget advice",
        "arguments": [
            {"name": "income", "description": "Monthly income", "type": "number", "required": True},
            {"name": "expenses", "description": "Monthly expenses", "type": "object", "required": True},
            {"name": "goals", "description": "Financial goals", "type": "array", "required": False}
        ]
    },
    {
        "name": "investment_advice",
        "description": "Provide investment recommendations",
        "arguments": [
            {"name": "risk_tolerance", "description": "Risk tolerance level", "type": "string", "required": True},
            {"name": "investment_amount", "description": "Amount to invest", "type": "number", "required": True},
            {"name": "time_horizon", "description": "Investment time horizon", "type": "string", "required": True}
        ]
    },
    {
        "name": "financial_advice",
        "description": "Generate financial advice",
        "arguments": [
            {"name": "user_goal", "description": "User's financial goal", "type": "string", "required": True}
        ]
    },
    {
        "name": "budget_guidance",
        "description": "Budget consultation",
        "arguments": [
            {"name": "income_level", "description": "User's income level", "type": "string", "required": True}
        ]
    }
]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "server": "finance-mcp-server"}

@app.post("/mcp")
async def mcp_endpoint(request: Dict[str, Any]):
    """Main MCP JSON-RPC endpoint"""
    try:
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"MCP request: {method}")
        
        if method == "initialize":
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
                    "serverInfo": {
                        "name": "finance-core-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": FINANCE_TOOLS
                }
            }
        
        elif method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "resources": FINANCE_RESOURCES
                }
            }
        
        elif method == "prompts/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "prompts": FINANCE_PROMPTS
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Mock tool execution
            result = await execute_finance_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
        
        elif method == "resources/read":
            uri = params.get("uri")
            
            # Mock resource reading
            content = await read_finance_resource(uri)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "text/plain",
                            "text": content
                        }
                    ]
                }
            }
        
        elif method == "prompts/list":
            prompt_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Mock prompt execution
            result = await execute_finance_prompt(prompt_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    except Exception as e:
        logger.error(f"Error in MCP endpoint: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


async def execute_finance_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Execute a finance tool"""
    logger.info(f"Executing finance tool: {tool_name}")
    
    if tool_name == "file_reader":
        file_path = arguments.get("file_path", "unknown")
        return f"Successfully read file: {file_path}"
    
    elif tool_name == "bank_statement_parser":
        return "Bank statement parsed successfully. Found 25 transactions."
    
    elif tool_name == "subscription_detector":
        return "Detected 3 recurring subscriptions: Netflix, Spotify, Gym membership"
    
    elif tool_name == "income_expense_tracker":
        return "Income and expenses tracked. Monthly summary generated."
    
    elif tool_name == "budget_planner_tool":
        return "Budget plan created successfully. Monthly budget: $5000"
    
    elif tool_name == "financial_advice_generator":
        return "Financial advice generated: Consider increasing emergency fund to 6 months of expenses."
    
    else:
        return f"Tool {tool_name} executed successfully"


async def read_finance_resource(uri: str) -> str:
    """Read a finance resource"""
    logger.info(f"Reading finance resource: {uri}")
    
    if "monthly_summary" in uri:
        return "Monthly Financial Summary:\n- Income: $8000\n- Expenses: $6000\n- Savings: $2000"
    
    elif "budget_analysis" in uri:
        return "Budget Analysis:\n- Housing: 30%\n- Transportation: 15%\n- Food: 10%\n- Entertainment: 5%"
    
    elif "market_trends" in uri:
        return "Market Trends:\n- S&P 500: +2.5%\n- NASDAQ: +3.1%\n- Bond yields: 4.2%"
    
    else:
        return f"Resource content for {uri}"


async def execute_finance_prompt(prompt_name: str, arguments: Dict[str, Any]) -> str:
    """Execute a finance prompt"""
    logger.info(f"Executing finance prompt: {prompt_name}")
    
    if prompt_name == "budget_advice":
        return "Based on your financial profile, I recommend creating a 50/30/20 budget: 50% needs, 30% wants, 20% savings."
    
    elif prompt_name == "investment_advice":
        return "Consider diversifying your portfolio with index funds and maintaining a long-term investment strategy."
    
    else:
        return f"Prompt {prompt_name} executed successfully"


if __name__ == "__main__":
    logger.info("Starting Finance MCP Server on port 3001...")
    uvicorn.run(app, host="localhost", port=3001, log_level="info")
