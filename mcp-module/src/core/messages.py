"""
MCP Message Types
Message definitions for MCP protocol
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from enum import Enum


class MessageType(Enum):
    """MCP Message Types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


@dataclass
class MCPMessage:
    """Base MCP Message"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    message_type: MessageType = MessageType.REQUEST


@dataclass
class MCPRequestMessage(MCPMessage):
    """MCP Request Message"""
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    message_type: MessageType = MessageType.REQUEST


@dataclass
class MCPResponseMessage(MCPMessage):
    """MCP Response Message"""
    result: Any = None
    message_type: MessageType = MessageType.RESPONSE


@dataclass
class MCPNotificationMessage(MCPMessage):
    """MCP Notification Message"""
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    message_type: MessageType = MessageType.NOTIFICATION


@dataclass
class MCPErrorMessage(MCPMessage):
    """MCP Error Message"""
    error: Dict[str, Any] = field(default_factory=dict)
    message_type: MessageType = MessageType.ERROR


@dataclass
class BatchMessage:
    """Batch MCP Messages"""
    messages: List[Union[MCPRequestMessage, MCPResponseMessage, MCPNotificationMessage, MCPErrorMessage]]


class MessageFactory:
    """Factory for creating MCP messages"""
    
    @staticmethod
    def create_request(method: str, params: Optional[Dict[str, Any]] = None, 
                      message_id: Optional[Union[str, int]] = None) -> MCPRequestMessage:
        """Create a request message"""
        return MCPRequestMessage(
            id=message_id,
            method=method,
            params=params or {}
        )
    
    @staticmethod
    def create_response(result: Any, request_id: Union[str, int]) -> MCPResponseMessage:
        """Create a response message"""
        return MCPResponseMessage(
            id=request_id,
            result=result
        )
    
    @staticmethod
    def create_notification(method: str, params: Optional[Dict[str, Any]] = None) -> MCPNotificationMessage:
        """Create a notification message"""
        return MCPNotificationMessage(
            method=method,
            params=params or {}
        )
    
    @staticmethod
    def create_error(error_code: int, error_message: str, 
                    request_id: Optional[Union[str, int]] = None,
                    error_data: Optional[Any] = None) -> MCPErrorMessage:
        """Create an error message"""
        error = {
            "code": error_code,
            "message": error_message
        }
        if error_data is not None:
            error["data"] = error_data
        
        return MCPErrorMessage(
            id=request_id,
            error=error
        )
    
    @staticmethod
    def create_batch(messages: List[Union[MCPRequestMessage, MCPResponseMessage, 
                                        MCPNotificationMessage, MCPErrorMessage]]) -> BatchMessage:
        """Create a batch message"""
        return BatchMessage(messages=messages)


class MessageValidator:
    """Validator for MCP messages"""
    
    @staticmethod
    def validate_request(message: MCPRequestMessage) -> List[str]:
        """Validate a request message"""
        errors = []
        
        if not message.method:
            errors.append("Request method is required")
        
        if message.id is None:
            errors.append("Request ID is required")
        
        return errors
    
    @staticmethod
    def validate_response(message: MCPResponseMessage) -> List[str]:
        """Validate a response message"""
        errors = []
        
        if message.id is None:
            errors.append("Response ID is required")
        
        return errors
    
    @staticmethod
    def validate_notification(message: MCPNotificationMessage) -> List[str]:
        """Validate a notification message"""
        errors = []
        
        if not message.method:
            errors.append("Notification method is required")
        
        if message.id is not None:
            errors.append("Notification should not have an ID")
        
        return errors
    
    @staticmethod
    def validate_error(message: MCPErrorMessage) -> List[str]:
        """Validate an error message"""
        errors = []
        
        if not message.error:
            errors.append("Error object is required")
        else:
            if "code" not in message.error:
                errors.append("Error code is required")
            if "message" not in message.error:
                errors.append("Error message is required")
        
        return errors
