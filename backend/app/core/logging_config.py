"""
Logging configuration for the AI Travel Planner API.
"""
import logging
import logging.config
import sys
from typing import Dict, Any
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log string
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from the record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                'thread', 'threadName', 'processName', 'process', 'getMessage'
            ]:
                extra_fields[key] = value
        
        if extra_fields:
            log_entry["extra"] = extra_fields
        
        return json.dumps(log_entry, default=str)

class ErrorTrackingFilter(logging.Filter):
    """
    Filter to track and enhance error logging.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter and enhance log records.
        
        Args:
            record: Log record to filter
            
        Returns:
            True to include the record
        """
        # Add request context if available
        if hasattr(record, 'request_id'):
            # Request ID is already set
            pass
        else:
            # Try to get request ID from context (if available)
            try:
                import contextvars
                request_id_var = contextvars.ContextVar('request_id', default=None)
                request_id = request_id_var.get()
                if request_id:
                    record.request_id = request_id
            except (ImportError, LookupError):
                pass
        
        # Add severity classification for errors
        if record.levelno >= logging.ERROR:
            record.severity = "high"
            record.alert_required = True
        elif record.levelno >= logging.WARNING:
            record.severity = "medium"
            record.alert_required = False
        else:
            record.severity = "low"
            record.alert_required = False
        
        # Enhance error messages with context
        if record.levelno >= logging.ERROR and hasattr(record, 'exc_info') and record.exc_info:
            record.error_type = record.exc_info[0].__name__ if record.exc_info[0] else "Unknown"
        
        return True

def get_logging_config(log_level: str = "INFO", use_json: bool = False) -> Dict[str, Any]:
    """
    Get logging configuration dictionary.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting
        
    Returns:
        Logging configuration dictionary
    """
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": JSONFormatter,
            }
        },
        "filters": {
            "error_tracking": {
                "()": ErrorTrackingFilter,
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "json" if use_json else "detailed",
                "filters": ["error_tracking"],
                "stream": sys.stdout
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json" if use_json else "detailed",
                "filters": ["error_tracking"],
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "app_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "json" if use_json else "standard",
                "filters": ["error_tracking"],
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "app": {
                "level": log_level,
                "handlers": ["console", "app_file", "error_file"],
                "propagate": False
            },
            "app.services": {
                "level": log_level,
                "handlers": ["console", "app_file", "error_file"],
                "propagate": False
            },
            "app.api": {
                "level": log_level,
                "handlers": ["console", "app_file", "error_file"],
                "propagate": False
            },
            "app.core": {
                "level": log_level,
                "handlers": ["console", "app_file", "error_file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "error_file"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"]
        }
    }
    
    return config

def setup_logging(log_level: str = "INFO", use_json: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level
        use_json: Whether to use JSON formatting
    """
    import os
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Get and apply logging configuration
    config = get_logging_config(log_level, use_json)
    logging.config.dictConfig(config)
    
    # Log startup message
    logger = logging.getLogger("app.core.logging")
    logger.info(f"Logging configured with level: {log_level}, JSON format: {use_json}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"app.{name}")

# Context manager for request-scoped logging
class RequestLoggingContext:
    """
    Context manager for request-scoped logging with request ID.
    """
    
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.logger = logging.getLogger("app.api")
    
    def __enter__(self):
        # Set request ID in context
        try:
            import contextvars
            request_id_var = contextvars.ContextVar('request_id')
            request_id_var.set(self.request_id)
        except ImportError:
            pass
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Log any unhandled exceptions
        if exc_type is not None:
            self.logger.error(
                f"Unhandled exception in request {self.request_id}",
                exc_info=(exc_type, exc_val, exc_tb),
                extra={"request_id": self.request_id}
            )
    
    def log_error(self, message: str, **kwargs):
        """Log an error with request context."""
        self.logger.error(message, extra={"request_id": self.request_id, **kwargs})
    
    def log_warning(self, message: str, **kwargs):
        """Log a warning with request context."""
        self.logger.warning(message, extra={"request_id": self.request_id, **kwargs})
    
    def log_info(self, message: str, **kwargs):
        """Log info with request context."""
        self.logger.info(message, extra={"request_id": self.request_id, **kwargs})

# Performance monitoring decorator
def log_performance(operation_name: str):
    """
    Decorator to log performance metrics for operations.
    
    Args:
        operation_name: Name of the operation being monitored
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            logger = logging.getLogger("app.performance")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"Operation completed: {operation_name}",
                    extra={
                        "operation": operation_name,
                        "duration_seconds": round(duration, 4),
                        "status": "success"
                    }
                )
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Operation failed: {operation_name}",
                    extra={
                        "operation": operation_name,
                        "duration_seconds": round(duration, 4),
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    },
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator

class StructuredLogger:
    """
    Structured logger for consistent log formatting.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with structured data."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with structured data."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with structured data."""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with structured data."""
        self.logger.debug(message, extra=kwargs)