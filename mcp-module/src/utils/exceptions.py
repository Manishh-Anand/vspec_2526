"""
Custom Exceptions
MCP module specific exceptions
"""


class MCPModuleError(Exception):
    """Base exception for MCP module errors"""
    pass


class ParsingError(MCPModuleError):
    """Error during BA_op.json parsing"""
    pass


class ValidationError(MCPModuleError):
    """Error during data validation"""
    pass


class MatchingError(MCPModuleError):
    """Error during semantic matching"""
    pass


class ExecutionError(MCPModuleError):
    """Error during MCP operation execution"""
    pass


class ConfigurationError(MCPModuleError):
    """Error in configuration setup"""
    pass


class TransportError(MCPModuleError):
    """Error in transport layer"""
    pass


class ProtocolError(MCPModuleError):
    """Error in MCP protocol handling"""
    pass


class ServerConnectionError(MCPModuleError):
    """Error connecting to MCP server"""
    pass


class LLMError(MCPModuleError):
    """Error with LLM operations"""
    pass


class CacheError(MCPModuleError):
    """Error in caching operations"""
    pass


class DiscoveryError(MCPModuleError):
    """Error during server discovery"""
    pass


class SessionError(MCPModuleError):
    """Error in session management"""
    pass
