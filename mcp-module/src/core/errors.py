"""
MCP Error Definitions
Comprehensive error handling for MCP operations
"""

from enum import Enum
from typing import Optional, Any, Dict


class MCPErrorCode(Enum):
    """MCP Error Codes as per specification"""
    # JSON-RPC 2.0 Standard Errors
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # MCP-Specific Errors
    SERVER_ERROR_START = -32000
    SERVER_ERROR_END = -32099
    
    # Custom MCP Errors
    INITIALIZATION_FAILED = -32001
    CAPABILITY_NOT_FOUND = -32002
    TOOL_EXECUTION_FAILED = -32003
    RESOURCE_NOT_FOUND = -32004
    PROMPT_NOT_FOUND = -32005
    AUTHENTICATION_FAILED = -32006
    AUTHORIZATION_FAILED = -32007
    RATE_LIMIT_EXCEEDED = -32008
    SERVER_OVERLOADED = -32009
    NETWORK_ERROR = -32010
    TIMEOUT_ERROR = -32011
    VALIDATION_ERROR = -32012
    CONFIGURATION_ERROR = -32013


class MCPError(Exception):
    """Base MCP Error"""
    
    def __init__(self, 
                 code: MCPErrorCode,
                 message: str,
                 data: Optional[Any] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.data = data
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format"""
        return {
            "code": self.code.value,
            "message": self.message,
            "data": self.data,
            "details": self.details
        }
    
    def __str__(self) -> str:
        return f"MCPError({self.code.name}: {self.message})"


class MCPParseError(MCPError):
    """Parse Error - Invalid JSON received"""
    
    def __init__(self, message: str = "Parse error", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.PARSE_ERROR, message, data)


class MCPInvalidRequestError(MCPError):
    """Invalid Request - JSON-RPC request is invalid"""
    
    def __init__(self, message: str = "Invalid Request", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.INVALID_REQUEST, message, data)


class MCPMethodNotFoundError(MCPError):
    """Method Not Found - Method doesn't exist"""
    
    def __init__(self, method: str, data: Optional[Any] = None):
        message = f"Method not found: {method}"
        super().__init__(MCPErrorCode.METHOD_NOT_FOUND, message, data)


class MCPInvalidParamsError(MCPError):
    """Invalid Params - Invalid method parameters"""
    
    def __init__(self, message: str = "Invalid params", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.INVALID_PARAMS, message, data)


class MCPInternalError(MCPError):
    """Internal Error - Internal JSON-RPC error"""
    
    def __init__(self, message: str = "Internal error", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.INTERNAL_ERROR, message, data)


class MCPInitializationError(MCPError):
    """Initialization Failed - Server initialization failed"""
    
    def __init__(self, message: str = "Initialization failed", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.INITIALIZATION_FAILED, message, data)


class MCPCapabilityNotFoundError(MCPError):
    """Capability Not Found - Requested capability doesn't exist"""
    
    def __init__(self, capability: str, data: Optional[Any] = None):
        message = f"Capability not found: {capability}"
        super().__init__(MCPErrorCode.CAPABILITY_NOT_FOUND, message, data)


class MCPToolExecutionError(MCPError):
    """Tool Execution Failed - Tool execution failed"""
    
    def __init__(self, tool: str, message: str = "Tool execution failed", data: Optional[Any] = None):
        full_message = f"Tool '{tool}' execution failed: {message}"
        super().__init__(MCPErrorCode.TOOL_EXECUTION_FAILED, full_message, data)


class MCPResourceNotFoundError(MCPError):
    """Resource Not Found - Requested resource doesn't exist"""
    
    def __init__(self, uri: str, data: Optional[Any] = None):
        message = f"Resource not found: {uri}"
        super().__init__(MCPErrorCode.RESOURCE_NOT_FOUND, message, data)


class MCPPromptNotFoundError(MCPError):
    """Prompt Not Found - Requested prompt doesn't exist"""
    
    def __init__(self, prompt: str, data: Optional[Any] = None):
        message = f"Prompt not found: {prompt}"
        super().__init__(MCPErrorCode.PROMPT_NOT_FOUND, message, data)


class MCPAuthenticationError(MCPError):
    """Authentication Failed - Authentication failed"""
    
    def __init__(self, message: str = "Authentication failed", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.AUTHENTICATION_FAILED, message, data)


class MCPAuthorizationError(MCPError):
    """Authorization Failed - Authorization failed"""
    
    def __init__(self, message: str = "Authorization failed", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.AUTHORIZATION_FAILED, message, data)


class MCPRateLimitError(MCPError):
    """Rate Limit Exceeded - Rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.RATE_LIMIT_EXCEEDED, message, data)


class MCPServerOverloadedError(MCPError):
    """Server Overloaded - Server is overloaded"""
    
    def __init__(self, message: str = "Server overloaded", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.SERVER_OVERLOADED, message, data)


class MCPNetworkError(MCPError):
    """Network Error - Network communication error"""
    
    def __init__(self, message: str = "Network error", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.NETWORK_ERROR, message, data)


class MCPTimeoutError(MCPError):
    """Timeout Error - Operation timed out"""
    
    def __init__(self, message: str = "Operation timed out", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.TIMEOUT_ERROR, message, data)


class MCPValidationError(MCPError):
    """Validation Error - Data validation failed"""
    
    def __init__(self, message: str = "Validation failed", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.VALIDATION_ERROR, message, data)


class MCPConfigurationError(MCPError):
    """Configuration Error - Configuration error"""
    
    def __init__(self, message: str = "Configuration error", data: Optional[Any] = None):
        super().__init__(MCPErrorCode.CONFIGURATION_ERROR, message, data)


class MCPErrorHandler:
    """Error handler for MCP operations"""
    
    @staticmethod
    def handle_error(error: Exception) -> MCPError:
        """Convert any exception to MCPError"""
        if isinstance(error, MCPError):
            return error
        
        # Convert common exceptions to MCP errors
        if isinstance(error, ValueError):
            return MCPValidationError(str(error))
        elif isinstance(error, TimeoutError):
            return MCPTimeoutError(str(error))
        elif isinstance(error, ConnectionError):
            return MCPNetworkError(str(error))
        elif isinstance(error, PermissionError):
            return MCPAuthorizationError(str(error))
        elif isinstance(error, FileNotFoundError):
            return MCPResourceNotFoundError(str(error))
        else:
            return MCPInternalError(str(error))
    
    @staticmethod
    def create_error_response(error: MCPError) -> Dict[str, Any]:
        """Create error response dictionary"""
        return {
            "jsonrpc": "2.0",
            "error": error.to_dict(),
            "id": None
        }
    
    @staticmethod
    def is_retryable(error: MCPError) -> bool:
        """Check if error is retryable"""
        retryable_codes = [
            MCPErrorCode.NETWORK_ERROR,
            MCPErrorCode.TIMEOUT_ERROR,
            MCPErrorCode.SERVER_OVERLOADED,
            MCPErrorCode.RATE_LIMIT_EXCEEDED
        ]
        return error.code in retryable_codes
    
    @staticmethod
    def get_retry_delay(error: MCPError, attempt: int) -> float:
        """Get retry delay for error"""
        base_delay = 1.0
        
        if error.code == MCPErrorCode.RATE_LIMIT_EXCEEDED:
            base_delay = 5.0
        elif error.code == MCPErrorCode.SERVER_OVERLOADED:
            base_delay = 2.0
        
        # Exponential backoff
        return base_delay * (2 ** (attempt - 1))
