"""
MCP Protocol Implementation
JSON-RPC 2.0 compliant Model Context Protocol
"""

import json
import logging
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, asdict
from enum import Enum


class MCPErrorCode(Enum):
    """MCP Error Codes"""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_START = -32000
    SERVER_ERROR_END = -32099


@dataclass
class MCPError:
    """MCP Error Object"""
    code: int
    message: str
    data: Optional[Any] = None


@dataclass
class MCPRequest:
    """MCP Request Message"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: str = ""
    params: Optional[Dict[str, Any]] = None


@dataclass
class MCPResponse:
    """MCP Response Message"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Any = None


@dataclass
class MCPNotification:
    """MCP Notification Message"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Optional[Dict[str, Any]] = None


@dataclass
class MCPErrorResponse:
    """MCP Error Response Message"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    error: MCPError = None


@dataclass
class Tool:
    """MCP Tool Definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class Resource:
    """MCP Resource Definition"""
    uri: str
    name: str
    description: str
    mimeType: Optional[str] = None


@dataclass
class PromptArgument:
    """MCP Prompt Argument"""
    name: str
    description: str
    type: str
    required: bool = False


@dataclass
class Prompt:
    """MCP Prompt Definition"""
    name: str
    description: str
    arguments: List[PromptArgument]


class MCPProtocol:
    """MCP Protocol Handler"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._next_id = 1
        
    def _generate_id(self) -> Union[str, int]:
        """Generate next message ID"""
        id_val = self._next_id
        self._next_id += 1
        return id_val
    
    def create_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> MCPRequest:
        """Create an MCP request"""
        return MCPRequest(
            id=self._generate_id(),
            method=method,
            params=params or {}
        )
    
    def create_response(self, request_id: Union[str, int], result: Any) -> MCPResponse:
        """Create an MCP response"""
        return MCPResponse(
            id=request_id,
            result=result
        )
    
    def create_error_response(self, request_id: Union[str, int], 
                            error_code: MCPErrorCode, 
                            message: str, 
                            data: Optional[Any] = None) -> MCPErrorResponse:
        """Create an MCP error response"""
        error = MCPError(
            code=error_code.value,
            message=message,
            data=data
        )
        return MCPErrorResponse(
            id=request_id,
            error=error
        )
    
    def create_notification(self, method: str, params: Optional[Dict[str, Any]] = None) -> MCPNotification:
        """Create an MCP notification"""
        return MCPNotification(
            method=method,
            params=params or {}
        )
    
    def serialize_message(self, message: Union[MCPRequest, MCPResponse, MCPNotification, MCPErrorResponse]) -> str:
        """Serialize MCP message to JSON"""
        try:
            return json.dumps(asdict(message), default=str)
        except Exception as e:
            self.logger.error(f"Failed to serialize message: {e}")
            raise
    
    def deserialize_message(self, data: str) -> Union[MCPRequest, MCPResponse, MCPNotification, MCPErrorResponse]:
        """Deserialize JSON to MCP message"""
        try:
            parsed = json.loads(data)
            
            if "error" in parsed:
                return MCPErrorResponse(**parsed)
            elif "result" in parsed:
                return MCPResponse(**parsed)
            elif "method" in parsed and "id" not in parsed:
                return MCPNotification(**parsed)
            elif "method" in parsed and "id" in parsed:
                return MCPRequest(**parsed)
            else:
                raise ValueError("Invalid MCP message format")
                
        except Exception as e:
            self.logger.error(f"Failed to deserialize message: {e}")
            raise
    
    # MCP Protocol Methods
    
    def create_initialize_request(self, protocol_version: str = "2024-11-05",
                                capabilities: Optional[Dict[str, Any]] = None,
                                client_info: Optional[Dict[str, Any]] = None) -> MCPRequest:
        """Create initialize request"""
        params = {
            "protocolVersion": protocol_version,
            "capabilities": capabilities or {},
            "clientInfo": client_info or {}
        }
        return self.create_request("initialize", params)
    
    def create_tools_list_request(self) -> MCPRequest:
        """Create tools/list request"""
        return self.create_request("tools/list")
    
    def create_tools_call_request(self, name: str, arguments: Dict[str, Any]) -> MCPRequest:
        """Create tools/call request"""
        params = {
            "name": name,
            "arguments": arguments
        }
        return self.create_request("tools/call", params)
    
    def create_resources_list_request(self) -> MCPRequest:
        """Create resources/list request"""
        return self.create_request("resources/list")
    
    def create_resources_read_request(self, uri: str) -> MCPRequest:
        """Create resources/read request"""
        params = {"uri": uri}
        return self.create_request("resources/read", params)
    
    def create_prompts_list_request(self) -> MCPRequest:
        """Create prompts/list request"""
        return self.create_request("prompts/list")
    
    def create_prompts_get_request(self, name: str) -> MCPRequest:
        """Create prompts/get request"""
        params = {"name": name}
        return self.create_request("prompts/get", params)
    
    def create_initialized_notification(self) -> MCPNotification:
        """Create initialized notification"""
        return self.create_notification("initialized")
    
    def create_exit_notification(self) -> MCPNotification:
        """Create exit notification"""
        return self.create_notification("exit")
    
    def create_log_message_notification(self, message: str, level: str = "info") -> MCPNotification:
        """Create logMessage notification"""
        params = {
            "body": {
                "level": level,
                "message": message
            }
        }
        return self.create_notification("notifications/logMessage", params)
