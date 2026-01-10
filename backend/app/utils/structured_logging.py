"""Structured logging with correlation IDs."""
import logging
import uuid
from contextvars import ContextVar
from typing import Optional, Dict, Any
import json
from datetime import datetime

# Context variable for correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID."""
    return correlation_id_var.get()


def set_correlation_id(cid: Optional[str] = None) -> str:
    """
    Set correlation ID for current context.
    
    Args:
        cid: Correlation ID to set (generates new one if None)
        
    Returns:
        Correlation ID string
    """
    if cid is None:
        cid = str(uuid.uuid4())
    correlation_id_var.set(cid)
    return cid


def get_request_id() -> Optional[str]:
    """Get current request ID."""
    return request_id_var.get()


def set_request_id(rid: Optional[str] = None) -> str:
    """
    Set request ID for current context.
    
    Args:
        rid: Request ID to set (generates new one if None)
        
    Returns:
        Request ID string
    """
    if rid is None:
        rid = str(uuid.uuid4())
    request_id_var.set(rid)
    return rid


class StructuredFormatter(logging.Formatter):
    """Structured JSON log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add correlation ID if available
        cid = get_correlation_id()
        if cid:
            log_data["correlation_id"] = cid
        
        # Add request ID if available
        rid = get_request_id()
        if rid:
            log_data["request_id"] = rid
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


def setup_structured_logging(log_level: str = "INFO") -> None:
    """
    Set up structured logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler with structured formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredFormatter())
    logger.addHandler(console_handler)
    
    # Optionally add file handler for production
    # file_handler = logging.FileHandler('app.log')
    # file_handler.setFormatter(StructuredFormatter())
    # logger.addHandler(file_handler)

