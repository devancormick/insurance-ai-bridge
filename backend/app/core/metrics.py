"""Prometheus metrics integration."""
from typing import Dict, Any
from app.utils.logging import logger

# In production, use prometheus_client
try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("prometheus_client not installed, metrics will be in-memory only")


if PROMETHEUS_AVAILABLE:
    # Prometheus metrics
    http_requests_total = Counter(
        'http_requests_total',
        'Total HTTP requests',
        ['method', 'endpoint', 'status']
    )
    
    http_request_duration_seconds = Histogram(
        'http_request_duration_seconds',
        'HTTP request duration in seconds',
        ['method', 'endpoint']
    )
    
    llm_calls_total = Counter(
        'llm_calls_total',
        'Total LLM API calls',
        ['provider', 'status']
    )
    
    llm_tokens_total = Counter(
        'llm_tokens_total',
        'Total LLM tokens used',
        ['provider']
    )
    
    cache_operations_total = Counter(
        'cache_operations_total',
        'Total cache operations',
        ['operation', 'result']
    )
    
    active_connections = Gauge(
        'active_connections',
        'Number of active connections'
    )
else:
    # Fallback when Prometheus not available
    http_requests_total = None
    http_request_duration_seconds = None
    llm_calls_total = None
    llm_tokens_total = None
    cache_operations_total = None
    active_connections = None


def record_http_request(method: str, endpoint: str, status: int, duration: float):
    """Record HTTP request metric."""
    if PROMETHEUS_AVAILABLE and http_requests_total:
        http_requests_total.labels(method=method, endpoint=endpoint, status=str(status)).inc()
        if http_request_duration_seconds:
            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def record_llm_call(provider: str, status: str, tokens: int = 0):
    """Record LLM call metric."""
    if PROMETHEUS_AVAILABLE:
        if llm_calls_total:
            llm_calls_total.labels(provider=provider, status=status).inc()
        if llm_tokens_total and tokens > 0:
            llm_tokens_total.labels(provider=provider).inc(tokens)


def record_cache_operation(operation: str, result: str):
    """Record cache operation metric."""
    if PROMETHEUS_AVAILABLE and cache_operations_total:
        cache_operations_total.labels(operation=operation, result=result).inc()


def set_active_connections(value: int):
    """Set active connections gauge."""
    if PROMETHEUS_AVAILABLE and active_connections:
        active_connections.set(value)

