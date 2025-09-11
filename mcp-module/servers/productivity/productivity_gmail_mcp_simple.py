#!/usr/bin/env python3
"""
Simplified Productivity Gmail MCP Server
Port: 3002
Domain: Productivity (Gmail)
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
    }
]

MOCK_CONTACTS = [
    {"name": "John Manager", "email": "manager@company.com", "category": "work"},
    {"name": "Sarah Colleague", "email": "sarah@company.com", "category": "work"},
    {"name": "Tech Newsletter", "email": "newsletter@tech.com", "category": "newsletter"}
]

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
                        "body": {"type": "string", "description": "Email body content"}
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
                        "max_results": {"type": "integer", "description": "Maximum number of emails to retrieve"}
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
                        "action": {"type": "string", "enum": ["mark_read", "mark_unread", "archive"], "description": "Action to perform"}
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
                        "action": {"type": "string", "enum": ["add", "list"], "description": "Contact action"},
                        "name": {"type": "string", "description": "Contact name"},
                        "email": {"type": "string", "description": "Contact email"}
                    },
                    "required": ["action"]
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
                        "tone": {"type": "string", "enum": ["formal", "casual", "professional"], "description": "Email tone"}
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
                        "response_type": {"type": "string", "enum": ["acknowledge", "clarify", "decline"], "description": "Response type"}
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
                        "summary_length": {"type": "string", "enum": ["brief", "detailed"], "description": "Summary length"}
                    },
                    "required": ["email_thread"]
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
        logger.info("Initializing productivity Gmail MCP server")
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
        if tool_name == "email_sender":
            return self._execute_email_sender(arguments)
        elif tool_name == "email_reader":
            return self._execute_email_reader(arguments)
        elif tool_name == "email_organizer":
            return self._execute_email_organizer(arguments)
        elif tool_name == "contact_manager":
            return self._execute_contact_manager(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _execute_email_sender(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email sender tool"""
        to_email = arguments.get("to")
        subject = arguments.get("subject")
        body = arguments.get("body")
        
        return {
            "status": "success",
            "message_id": f"msg_{random.randint(1000, 9999)}",
            "to": to_email,
            "subject": subject,
            "sent_at": datetime.now().isoformat(),
            "delivery_status": "delivered"
        }
    
    def _execute_email_reader(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email reader tool"""
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 10)
        
        # Filter emails based on query
        filtered_emails = MOCK_EMAILS
        if query:
            filtered_emails = [email for email in MOCK_EMAILS if query.lower() in email["subject"].lower()]
        
        return {
            "status": "success",
            "emails": filtered_emails[:max_results],
            "total_found": len(filtered_emails),
            "query": query
        }
    
    def _execute_email_organizer(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email organizer tool"""
        email_ids = arguments.get("email_ids", [])
        action = arguments.get("action")
        
        return {
            "status": "success",
            "action": action,
            "processed_emails": len(email_ids),
            "email_ids": email_ids,
            "timestamp": datetime.now().isoformat()
        }
    
    def _execute_contact_manager(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute contact manager tool"""
        action = arguments.get("action")
        name = arguments.get("name")
        email = arguments.get("email")
        
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
                "contact": {"name": name, "email": email},
                "message": f"Contact {name} added successfully"
            }
        else:
            return {
                "status": "success",
                "action": action,
                "message": f"Contact {action} operation completed"
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
        elif "labels" in uri:
            return {
                "labels": [
                    {"name": "work", "count": 2},
                    {"name": "important", "count": 1},
                    {"name": "newsletter", "count": 1}
                ]
            }
        elif "contacts" in uri:
            return {
                "contacts": MOCK_CONTACTS,
                "total_contacts": len(MOCK_CONTACTS),
                "categories": ["work", "newsletter"]
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
        self.mcp_server = ProductivityGmailMCPServer()
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
            response = {"status": "healthy", "server": "productivity-gmail-mcp"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def run_server(port=3002):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MCPRequestHandler)
    logger.info(f"Starting Productivity Gmail MCP server on port {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        httpd.shutdown()

if __name__ == "__main__":
    run_server(3002)
