#!/usr/bin/env python3
"""
Productivity Gmail MCP Server
Port: 3002
Domain: Productivity (Gmail)
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
        logging.FileHandler('productivity_gmail_mcp.log')
    ]
)
logger = logging.getLogger(__name__)

# Mock data for Gmail operations
MOCK_EMAILS = [
    {
        "id": "email_001",
        "subject": "Project Update - Q1 Results",
        "sender": "manager@company.com",
        "recipient": "user@company.com",
        "body": "Please review the Q1 results and provide feedback.",
        "date": "2024-01-15T10:30:00Z",
        "labels": ["work", "important"],
        "read": False
    },
    {
        "id": "email_002", 
        "subject": "Meeting Reminder - Team Sync",
        "sender": "calendar@company.com",
        "recipient": "user@company.com",
        "body": "Reminder: Team sync meeting in 30 minutes.",
        "date": "2024-01-16T14:00:00Z",
        "labels": ["work", "meeting"],
        "read": True
    },
    {
        "id": "email_003",
        "subject": "Newsletter - Tech Updates",
        "sender": "newsletter@tech.com",
        "recipient": "user@company.com", 
        "body": "Latest tech updates and industry news.",
        "date": "2024-01-17T09:15:00Z",
        "labels": ["newsletter"],
        "read": False
    },
    {
        "id": "email_004",
        "subject": "Invoice #12345",
        "sender": "billing@service.com",
        "recipient": "user@company.com",
        "body": "Your invoice for January services is ready.",
        "date": "2024-01-18T16:45:00Z",
        "labels": ["billing", "important"],
        "read": False
    },
    {
        "id": "email_005",
        "subject": "Social Media Update",
        "sender": "social@platform.com",
        "recipient": "user@company.com",
        "body": "New activity on your social media accounts.",
        "date": "2024-01-19T11:20:00Z",
        "labels": ["social"],
        "read": True
    }
]

MOCK_CONTACTS = [
    {"name": "John Manager", "email": "manager@company.com", "category": "work"},
    {"name": "Sarah Colleague", "email": "sarah@company.com", "category": "work"},
    {"name": "Tech Newsletter", "email": "newsletter@tech.com", "category": "newsletter"},
    {"name": "Billing Service", "email": "billing@service.com", "category": "billing"}
]

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

class ProductivityGmailMCPServer:
    """Productivity Gmail MCP Server implementing all three primitives"""
    
    def __init__(self):
        self.server_info = {
            "name": "productivity-gmail-mcp",
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
            "email_sender": {
                "name": "email_sender",
                "description": "Send emails via Gmail",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body content"},
                        "cc": {"type": "array", "items": {"type": "string"}, "description": "CC recipients"},
                        "bcc": {"type": "array", "items": {"type": "string"}, "description": "BCC recipients"}
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            "email_reader": {
                "name": "email_reader",
                "description": "Read and parse emails from Gmail",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Gmail search query"},
                        "max_results": {"type": "integer", "description": "Maximum number of emails to retrieve"},
                        "label": {"type": "string", "description": "Gmail label filter"}
                    },
                    "required": ["query"]
                }
            },
            "email_organizer": {
                "name": "email_organizer",
                "description": "Organize emails with labels and filters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email_ids": {"type": "array", "items": {"type": "string"}, "description": "Email IDs to organize"},
                        "labels": {"type": "array", "items": {"type": "string"}, "description": "Labels to apply"},
                        "action": {"type": "string", "enum": ["mark_read", "mark_unread", "archive", "delete"], "description": "Action to perform"}
                    },
                    "required": ["email_ids", "action"]
                }
            },
            "contact_manager": {
                "name": "contact_manager",
                "description": "Manage Gmail contacts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["add", "update", "delete", "list"], "description": "Contact action"},
                        "name": {"type": "string", "description": "Contact name"},
                        "email": {"type": "string", "description": "Contact email"},
                        "category": {"type": "string", "description": "Contact category"}
                    },
                    "required": ["action"]
                }
            },
            "calendar_integration": {
                "name": "calendar_integration",
                "description": "Integrate with Google Calendar for email scheduling",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email_id": {"type": "string", "description": "Email ID to schedule"},
                        "calendar_date": {"type": "string", "format": "date", "description": "Calendar date"},
                        "reminder_time": {"type": "string", "description": "Reminder time"}
                    },
                    "required": ["email_id", "calendar_date"]
                }
            },
            "email_analytics": {
                "name": "email_analytics",
                "description": "Analyze email patterns and provide insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "date_range": {"type": "object", "properties": {
                            "start": {"type": "string", "format": "date"},
                            "end": {"type": "string", "format": "date"}
                        }},
                        "metrics": {"type": "array", "items": {"type": "string"}, "description": "Metrics to analyze"}
                    }
                }
            }
        }
    
    def _initialize_resources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available resources"""
        return {
            "email_inbox": {
                "name": "email_inbox",
                "description": "Gmail inbox emails",
                "uri": "gmail://inbox/*",
                "mimeType": "application/json"
            },
            "email_sent": {
                "name": "email_sent",
                "description": "Sent emails",
                "uri": "gmail://sent/*",
                "mimeType": "application/json"
            },
            "email_drafts": {
                "name": "email_drafts",
                "description": "Draft emails",
                "uri": "gmail://drafts/*",
                "mimeType": "application/json"
            },
            "email_labels": {
                "name": "email_labels",
                "description": "Gmail labels",
                "uri": "gmail://labels/*",
                "mimeType": "application/json"
            },
            "contacts": {
                "name": "contacts",
                "description": "Gmail contacts",
                "uri": "gmail://contacts/*",
                "mimeType": "application/json"
            },
            "calendar_events": {
                "name": "calendar_events",
                "description": "Google Calendar events",
                "uri": "gmail://calendar/*",
                "mimeType": "application/json"
            }
        }
    
    def _initialize_prompts(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available prompts"""
        return {
            "email_composer": {
                "name": "email_composer",
                "description": "Compose professional emails with AI assistance",
                "arguments": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string", "description": "Email recipient"},
                        "purpose": {"type": "string", "description": "Email purpose"},
                        "tone": {"type": "string", "enum": ["formal", "casual", "professional"], "description": "Email tone"},
                        "key_points": {"type": "array", "items": {"type": "string"}, "description": "Key points to include"}
                    },
                    "required": ["recipient", "purpose"]
                }
            },
            "email_responder": {
                "name": "email_responder",
                "description": "Generate appropriate email responses",
                "arguments": {
                    "type": "object",
                    "properties": {
                        "original_email": {"type": "object", "description": "Original email content"},
                        "response_type": {"type": "string", "enum": ["acknowledge", "clarify", "decline", "accept"], "description": "Response type"},
                        "urgency": {"type": "string", "enum": ["low", "medium", "high"], "description": "Response urgency"}
                    },
                    "required": ["original_email", "response_type"]
                }
            },
            "email_summarizer": {
                "name": "email_summarizer",
                "description": "Summarize email threads and conversations",
                "arguments": {
                    "type": "object",
                    "properties": {
                        "email_thread": {"type": "array", "items": {"type": "object"}, "description": "Email thread to summarize"},
                        "summary_length": {"type": "string", "enum": ["brief", "detailed"], "description": "Summary length"},
                        "focus_areas": {"type": "array", "items": {"type": "string"}, "description": "Areas to focus on"}
                    },
                    "required": ["email_thread"]
                }
            },
            "meeting_scheduler": {
                "name": "meeting_scheduler",
                "description": "Schedule meetings based on email content",
                "arguments": {
                    "type": "object",
                    "properties": {
                        "email_content": {"type": "string", "description": "Email content to analyze"},
                        "participants": {"type": "array", "items": {"type": "string"}, "description": "Meeting participants"},
                        "duration": {"type": "string", "description": "Meeting duration"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Meeting priority"}
                    },
                    "required": ["email_content"]
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
        logger.info("Initializing productivity Gmail MCP server")
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
        if tool_name == "email_sender":
            return await self._execute_email_sender(arguments)
        elif tool_name == "email_reader":
            return await self._execute_email_reader(arguments)
        elif tool_name == "email_organizer":
            return await self._execute_email_organizer(arguments)
        elif tool_name == "contact_manager":
            return await self._execute_contact_manager(arguments)
        elif tool_name == "calendar_integration":
            return await self._execute_calendar_integration(arguments)
        elif tool_name == "email_analytics":
            return await self._execute_email_analytics(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _execute_email_sender(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email sender tool"""
        to_email = arguments.get("to")
        subject = arguments.get("subject")
        body = arguments.get("body")
        cc = arguments.get("cc", [])
        bcc = arguments.get("bcc", [])
        
        await asyncio.sleep(0.2)  # Simulate sending time
        
        return {
            "status": "success",
            "message_id": f"msg_{random.randint(1000, 9999)}",
            "to": to_email,
            "subject": subject,
            "cc": cc,
            "bcc": bcc,
            "sent_at": datetime.now().isoformat(),
            "delivery_status": "delivered"
        }
    
    async def _execute_email_reader(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email reader tool"""
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 10)
        label = arguments.get("label")
        
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Filter emails based on query and label
        filtered_emails = MOCK_EMAILS
        if label:
            filtered_emails = [email for email in MOCK_EMAILS if label in email.get("labels", [])]
        
        if query:
            filtered_emails = [email for email in filtered_emails if query.lower() in email["subject"].lower()]
        
        return {
            "status": "success",
            "emails": filtered_emails[:max_results],
            "total_found": len(filtered_emails),
            "query": query,
            "label": label
        }
    
    async def _execute_email_organizer(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email organizer tool"""
        email_ids = arguments.get("email_ids", [])
        labels = arguments.get("labels", [])
        action = arguments.get("action")
        
        await asyncio.sleep(0.15)  # Simulate processing time
        
        return {
            "status": "success",
            "action": action,
            "processed_emails": len(email_ids),
            "applied_labels": labels,
            "email_ids": email_ids,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _execute_contact_manager(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute contact manager tool"""
        action = arguments.get("action")
        name = arguments.get("name")
        email = arguments.get("email")
        category = arguments.get("category")
        
        await asyncio.sleep(0.1)  # Simulate processing time
        
        if action == "list":
            return {
                "status": "success",
                "action": action,
                "contacts": MOCK_CONTACTS,
                "total_contacts": len(MOCK_CONTACTS)
            }
        elif action == "add":
            return {
                "status": "success",
                "action": action,
                "contact": {"name": name, "email": email, "category": category},
                "message": f"Contact {name} added successfully"
            }
        else:
            return {
                "status": "success",
                "action": action,
                "message": f"Contact {action} operation completed"
            }
    
    async def _execute_calendar_integration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calendar integration tool"""
        email_id = arguments.get("email_id")
        calendar_date = arguments.get("calendar_date")
        reminder_time = arguments.get("reminder_time")
        
        await asyncio.sleep(0.2)  # Simulate processing time
        
        return {
            "status": "success",
            "email_id": email_id,
            "calendar_date": calendar_date,
            "reminder_time": reminder_time,
            "event_id": f"event_{random.randint(1000, 9999)}",
            "scheduled_at": datetime.now().isoformat()
        }
    
    async def _execute_email_analytics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email analytics tool"""
        date_range = arguments.get("date_range", {})
        metrics = arguments.get("metrics", ["volume", "response_time"])
        
        await asyncio.sleep(0.3)  # Simulate processing time
        
        return {
            "status": "success",
            "date_range": date_range,
            "metrics": metrics,
            "analytics": {
                "total_emails": len(MOCK_EMAILS),
                "unread_count": len([e for e in MOCK_EMAILS if not e["read"]]),
                "average_response_time": "2.5 hours",
                "top_senders": ["manager@company.com", "newsletter@tech.com"],
                "most_active_day": "Monday",
                "label_distribution": {
                    "work": 3,
                    "important": 2,
                    "newsletter": 1,
                    "billing": 1,
                    "social": 1
                }
            }
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
        
        if "inbox" in uri:
            return {
                "emails": MOCK_EMAILS,
                "total_count": len(MOCK_EMAILS),
                "unread_count": len([e for e in MOCK_EMAILS if not e["read"]]),
                "last_updated": datetime.now().isoformat()
            }
        elif "sent" in uri:
            return {
                "sent_emails": [
                    {
                        "id": "sent_001",
                        "subject": "Project Status Update",
                        "recipient": "team@company.com",
                        "sent_at": "2024-01-15T14:30:00Z"
                    }
                ],
                "total_sent": 1
            }
        elif "drafts" in uri:
            return {
                "draft_emails": [
                    {
                        "id": "draft_001",
                        "subject": "Draft: Meeting Agenda",
                        "recipient": "colleague@company.com",
                        "last_modified": "2024-01-16T09:00:00Z"
                    }
                ],
                "total_drafts": 1
            }
        elif "labels" in uri:
            return {
                "labels": [
                    {"name": "work", "count": 3},
                    {"name": "important", "count": 2},
                    {"name": "newsletter", "count": 1},
                    {"name": "billing", "count": 1},
                    {"name": "social", "count": 1}
                ]
            }
        elif "contacts" in uri:
            return {
                "contacts": MOCK_CONTACTS,
                "total_contacts": len(MOCK_CONTACTS),
                "categories": ["work", "newsletter", "billing"]
            }
        elif "calendar" in uri:
            return {
                "calendar_events": [
                    {
                        "id": "event_001",
                        "title": "Team Meeting",
                        "start": "2024-01-20T10:00:00Z",
                        "end": "2024-01-20T11:00:00Z",
                        "attendees": ["user@company.com", "manager@company.com"]
                    }
                ],
                "total_events": 1
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
    """Run HTTP server on port 3002"""
    import uvicorn
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="Productivity Gmail MCP Server", version="1.0.0")
    server = ProductivityGmailMCPServer()
    
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
        return {"status": "healthy", "server": "productivity-gmail-mcp"}
    
    logger.info("Starting Productivity Gmail MCP HTTP server on port 3002")
    uvicorn.run(app, host="0.0.0.0", port=3002)

# Stdio Server Implementation
async def stdio_server():
    """Run stdio server for process communication"""
    server = ProductivityGmailMCPServer()
    
    logger.info("Starting Productivity Gmail MCP stdio server")
    
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
