#!/usr/bin/env python3
"""
Simple HTTP-based Productivity MCP Server
Runs on port 3002 for testing
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

app = FastAPI(title="Productivity MCP Server", version="1.0.0")

# Mock data for productivity tools, resources, and prompts
PRODUCTIVITY_TOOLS = [
    {
        "name": "data_cleaner",
        "description": "Clean and validate data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "items": {"type": "object"}},
                "validation_rules": {"type": "object"}
            },
            "required": ["data"]
        }
    },
    {
        "name": "data_transformer",
        "description": "Transform data formats",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "items": {"type": "object"}},
                "target_format": {"type": "string", "enum": ["json", "csv", "xml"]}
            },
            "required": ["data", "target_format"]
        }
    },
    {
        "name": "report_builder",
        "description": "Build productivity reports",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "items": {"type": "object"}},
                "report_type": {"type": "string", "enum": ["summary", "detailed", "analytics"]}
            },
            "required": ["data", "report_type"]
        }
    },
    {
        "name": "chart_generator",
        "description": "Generate charts and graphs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "items": {"type": "object"}},
                "chart_type": {"type": "string", "enum": ["bar", "line", "pie", "scatter"]}
            },
            "required": ["data", "chart_type"]
        }
    },
    {
        "name": "email_analyzer",
        "description": "Analyze email patterns and productivity",
        "inputSchema": {
            "type": "object",
            "properties": {
                "emails": {"type": "array", "items": {"type": "object"}},
                "analysis_type": {"type": "string", "enum": ["sentiment", "frequency", "response_time"]}
            },
            "required": ["emails"]
        }
    },
    {
        "name": "task_scheduler",
        "description": "Schedule and manage tasks",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tasks": {"type": "array", "items": {"type": "object"}},
                "priority_levels": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["tasks"]
        }
    }
]

PRODUCTIVITY_RESOURCES = [
    {
        "uri": "productivity://reports/performance_summary",
        "name": "Performance Summary",
        "description": "Productivity performance reports",
        "mimeType": "application/json"
    },
    {
        "uri": "productivity://data/email_metrics",
        "name": "Email Metrics",
        "description": "Email productivity metrics",
        "mimeType": "application/json"
    },
    {
        "uri": "productivity://templates/reports/*",
        "name": "Report Templates",
        "description": "Productivity report templates",
        "mimeType": "application/json"
    },
    {
        "uri": "productivity://raw-data/*",
        "name": "Raw Data Store",
        "description": "Raw productivity data storage",
        "mimeType": "application/json"
    }
]

PRODUCTIVITY_PROMPTS = [
    {
        "name": "data_validation",
        "description": "Validate data quality",
        "arguments": [
            {"name": "data_type", "description": "Type of data to validate", "type": "string", "required": True}
        ]
    },
    {
        "name": "report_summary",
        "description": "Generate report summary",
        "arguments": [
            {"name": "report_type", "description": "Type of report", "type": "string", "required": True},
            {"name": "time_period", "description": "Time period for report", "type": "string", "required": True}
        ]
    },
    {
        "name": "productivity_analysis",
        "description": "Analyze productivity patterns",
        "arguments": [
            {"name": "metrics", "description": "Productivity metrics to analyze", "type": "array", "required": True},
            {"name": "timeframe", "description": "Analysis timeframe", "type": "string", "required": True}
        ]
    }
]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "server": "productivity-mcp-server"}

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
                        "name": "productivity-gmail-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": PRODUCTIVITY_TOOLS
                }
            }
        
        elif method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "resources": PRODUCTIVITY_RESOURCES
                }
            }
        
        elif method == "prompts/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "prompts": PRODUCTIVITY_PROMPTS
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Mock tool execution
            result = await execute_productivity_tool(tool_name, arguments)
            
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
            content = await read_productivity_resource(uri)
            
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
            result = await execute_productivity_prompt(prompt_name, arguments)
            
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


async def execute_productivity_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Execute a productivity tool"""
    logger.info(f"Executing productivity tool: {tool_name}")
    
    if tool_name == "gmail_summarize":
        return "Email summary generated: 15 unread emails, 3 urgent, 2 from clients"
    
    elif tool_name == "smart_reply":
        return "Smart reply generated: 'Thank you for your email. I'll get back to you soon.'"
    
    elif tool_name == "email_categorize":
        return "Emails categorized: 5 work, 3 personal, 2 newsletters, 1 urgent"
    
    elif tool_name == "meeting_assistant":
        return "Meeting assistant ready. Agenda created and participants notified."
    
    elif tool_name == "task_converter":
        return "Email converted to task: 'Follow up with client about project proposal'"
    
    elif tool_name == "calendar_optimizer":
        return "Calendar optimized. Found 3 time slots for focused work."
    
    else:
        return f"Tool {tool_name} executed successfully"


async def read_productivity_resource(uri: str) -> str:
    """Read a productivity resource"""
    logger.info(f"Reading productivity resource: {uri}")
    
    if "email_templates" in uri:
        return "Email Templates:\n- Professional greeting\n- Meeting request\n- Follow-up reminder\n- Thank you note"
    
    elif "time_management" in uri:
        return "Time Management Guide:\n- Pomodoro Technique\n- Time blocking\n- Priority matrix\n- Delegation strategies"
    
    elif "productivity_tools" in uri:
        return "Productivity Tools Reference:\n- Gmail filters\n- Calendar shortcuts\n- Task automation\n- Focus apps"
    
    else:
        return f"Resource content for {uri}"


async def execute_productivity_prompt(prompt_name: str, arguments: Dict[str, Any]) -> str:
    """Execute a productivity prompt"""
    logger.info(f"Executing productivity prompt: {prompt_name}")
    
    if prompt_name == "email_composition":
        return "Professional email composed: Clear subject line, concise content, and call to action included."
    
    elif prompt_name == "meeting_summary":
        return "Meeting summary generated: Key points, action items, and next steps documented."
    
    else:
        return f"Prompt {prompt_name} executed successfully"

if __name__ == "__main__":
    logger.info("Starting Productivity MCP Server on port 3002...")
    uvicorn.run(app, host="localhost", port=3002, log_level="info")
