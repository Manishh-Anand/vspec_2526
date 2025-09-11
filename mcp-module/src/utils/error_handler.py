"""
Centralized error handling and structured logging for MCP module
"""

import logging
import traceback
import asyncio
from typing import Any, Dict, Optional, Union
from datetime import datetime
from enum import Enum
import json

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for better organization"""
    CONNECTION = "connection"
    DISCOVERY = "discovery"
    MATCHING = "matching"
    EXECUTION = "execution"
    TRANSPORT = "transport"
    PROTOCOL = "protocol"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

class MCPError(Exception):
    """Base exception for MCP module errors"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.original_error = original_error
        self.timestamp = datetime.utcnow()
        self.traceback = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "traceback": self.traceback
        }

class ConnectionError(MCPError):
    """Connection-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorCategory.CONNECTION, ErrorSeverity.HIGH, details, original_error)

class DiscoveryError(MCPError):
    """Discovery-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorCategory.DISCOVERY, ErrorSeverity.MEDIUM, details, original_error)

class MatchingError(MCPError):
    """Matching-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorCategory.MATCHING, ErrorSeverity.MEDIUM, details, original_error)

class ExecutionError(MCPError):
    """Execution-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorCategory.EXECUTION, ErrorSeverity.HIGH, details, original_error)

class TransportError(MCPError):
    """Transport-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorCategory.TRANSPORT, ErrorSeverity.HIGH, details, original_error)

class ProtocolError(MCPError):
    """Protocol-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorCategory.PROTOCOL, ErrorSeverity.MEDIUM, details, original_error)

class ConfigurationError(MCPError):
    """Configuration-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorCategory.CONFIGURATION, ErrorSeverity.MEDIUM, details, original_error)

class ValidationError(MCPError):
    """Validation-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorCategory.VALIDATION, ErrorSeverity.LOW, details, original_error)

class TimeoutError(MCPError):
    """Timeout-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM, details, original_error)

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, logger_name: str = "mcp_error_handler"):
        self.logger = logging.getLogger(logger_name)
        self.error_count = 0
        self.error_history: list = []
        self.max_history = 1000
        
        # Setup structured logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup structured logging configuration"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def handle_error(
        self,
        error: Union[Exception, MCPError],
        context: Optional[Dict[str, Any]] = None,
        reraise: bool = False
    ) -> MCPError:
        """Handle and log an error"""
        # Convert to MCPError if needed
        if not isinstance(error, MCPError):
            mcp_error = MCPError(
                message=str(error),
                original_error=error,
                details=context or {}
            )
        else:
            mcp_error = error
            if context:
                mcp_error.details.update(context)
        
        # Log the error
        self._log_error(mcp_error)
        
        # Store in history
        self._store_error(mcp_error)
        
        # Reraise if requested
        if reraise:
            raise mcp_error
        
        return mcp_error
    
    def _log_error(self, error: MCPError):
        """Log error with appropriate level"""
        error_dict = error.to_dict()
        
        # Choose log level based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {error.message}", extra=error_dict)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(f"HIGH SEVERITY: {error.message}", extra=error_dict)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"MEDIUM SEVERITY: {error.message}", extra=error_dict)
        else:
            self.logger.info(f"LOW SEVERITY: {error.message}", extra=error_dict)
    
    def _store_error(self, error: MCPError):
        """Store error in history"""
        self.error_count += 1
        self.error_history.append(error.to_dict())
        
        # Maintain history size
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors"""
        if not self.error_history:
            return {"total_errors": 0, "categories": {}, "severities": {}}
        
        categories = {}
        severities = {}
        
        for error in self.error_history:
            category = error.get("category", "unknown")
            severity = error.get("severity", "unknown")
            
            categories[category] = categories.get(category, 0) + 1
            severities[severity] = severities.get(severity, 0) + 1
        
        return {
            "total_errors": self.error_count,
            "categories": categories,
            "severities": severities,
            "recent_errors": self.error_history[-10:] if self.error_history else []
        }
    
    def clear_history(self):
        """Clear error history"""
        self.error_history.clear()
        self.error_count = 0

class AsyncErrorHandler(ErrorHandler):
    """Async-compatible error handler"""
    
    async def handle_async_error(
        self,
        error: Union[Exception, MCPError],
        context: Optional[Dict[str, Any]] = None,
        reraise: bool = False
    ) -> MCPError:
        """Handle async errors"""
        return self.handle_error(error, context, reraise)
    
    async def safe_execute(
        self,
        coro,
        context: Optional[Dict[str, Any]] = None,
        default_return: Any = None
    ) -> Any:
        """Safely execute async function with error handling"""
        try:
            return await coro
        except Exception as e:
            self.handle_error(e, context)
            return default_return

def create_error_handler(logger_name: str = "mcp_error_handler") -> ErrorHandler:
    """Factory function to create error handler"""
    return ErrorHandler(logger_name)

def create_async_error_handler(logger_name: str = "mcp_error_handler") -> AsyncErrorHandler:
    """Factory function to create async error handler"""
    return AsyncErrorHandler(logger_name)

# Global error handler instance
_global_error_handler = None

def get_global_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = create_error_handler()
    return _global_error_handler

def get_global_async_error_handler() -> AsyncErrorHandler:
    """Get global async error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = create_async_error_handler()
    return _global_error_handler
