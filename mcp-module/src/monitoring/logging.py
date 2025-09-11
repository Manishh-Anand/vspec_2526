"""
Logging Configuration
Structured logging setup for MCP module
"""

import logging
import logging.config
import sys
from typing import Optional, Dict, Any
import json
from datetime import datetime


def setup_logging(level: str = "INFO", 
                 log_file: Optional[str] = None,
                 log_format: str = "json") -> None:
    """
    Setup structured logging for the MCP module
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        log_format: Log format (json, text)
    """
    
    # Define log format
    if log_format == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


class StructuredLogger:
    """Structured logger with extra fields support"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.extra_fields = {}
    
    def bind(self, **kwargs) -> 'StructuredLogger':
        """Bind extra fields to logger"""
        new_logger = StructuredLogger(self.logger.name)
        new_logger.extra_fields = {**self.extra_fields, **kwargs}
        return new_logger
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method"""
        extra_fields = {**self.extra_fields, **kwargs}
        
        # Create a custom log record
        record = self.logger.makeRecord(
            self.logger.name, level, '', 0, message, (), None
        )
        record.extra_fields = extra_fields
        
        self.logger.handle(record)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log(logging.CRITICAL, message, **kwargs)


def get_logger(name: str) -> StructuredLogger:
    """Get structured logger"""
    return StructuredLogger(name)


# Performance monitoring
class PerformanceLogger:
    """Performance monitoring logger"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.metrics = {}
    
    def start_timer(self, operation: str) -> str:
        """Start timing an operation"""
        timer_id = f"{operation}_{datetime.utcnow().timestamp()}"
        self.metrics[timer_id] = {
            'operation': operation,
            'start_time': datetime.utcnow(),
            'status': 'running'
        }
        return timer_id
    
    def end_timer(self, timer_id: str, success: bool = True, **kwargs):
        """End timing an operation"""
        if timer_id in self.metrics:
            metric = self.metrics[timer_id]
            end_time = datetime.utcnow()
            duration = (end_time - metric['start_time']).total_seconds()
            
            metric.update({
                'end_time': end_time,
                'duration': duration,
                'success': success,
                'status': 'completed',
                **kwargs
            })
            
            self.logger.info(
                f"Operation completed: {metric['operation']}",
                operation=metric['operation'],
                duration=duration,
                success=success,
                **kwargs
            )
            
            del self.metrics[timer_id]
    
    def log_metric(self, name: str, value: float, unit: str = "", **kwargs):
        """Log a metric"""
        self.logger.info(
            f"Metric: {name} = {value}{unit}",
            metric_name=name,
            metric_value=value,
            metric_unit=unit,
            **kwargs
        )


# Error tracking
class ErrorTracker:
    """Error tracking and reporting"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.error_counts = {}
    
    def track_error(self, error_type: str, error_message: str, **kwargs):
        """Track an error occurrence"""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        self.logger.error(
            f"Error occurred: {error_type}",
            error_type=error_type,
            error_message=error_message,
            error_count=self.error_counts[error_type],
            **kwargs
        )
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get error summary"""
        return self.error_counts.copy()
    
    def reset_errors(self):
        """Reset error counts"""
        self.error_counts.clear()
