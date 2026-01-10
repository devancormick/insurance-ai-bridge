"""Monitoring and metrics collection."""
from typing import Dict, Any
from datetime import datetime
from app.utils.logging import logger
from app.config import settings

# In-memory metrics (use Prometheus in production)
metrics = {
    "requests_total": 0,
    "requests_by_status": {},
    "requests_by_endpoint": {},
    "llm_calls_total": 0,
    "llm_tokens_used": 0,
    "llm_errors": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "pii_tokens_created": 0,
    "pii_tokens_cleared": 0,
    "average_response_time_ms": 0,
    "start_time": datetime.utcnow().isoformat()
}


def increment_counter(metric_name: str, labels: Dict[str, str] = None):
    """
    Increment a counter metric.
    
    Args:
        metric_name: Name of the metric
        labels: Optional labels for the metric
    """
    if metric_name in metrics:
        if isinstance(metrics[metric_name], dict) and labels:
            key = ",".join(f"{k}={v}" for k, v in labels.items())
            metrics[metric_name][key] = metrics[metric_name].get(key, 0) + 1
        else:
            metrics[metric_name] += 1


def record_gauge(metric_name: str, value: float):
    """
    Record a gauge metric value.
    
    Args:
        metric_name: Name of the metric
        value: Value to record
    """
    if metric_name in metrics:
        metrics[metric_name] = value


def get_metrics() -> Dict[str, Any]:
    """
    Get all current metrics.
    
    Returns:
        Dictionary of all metrics
    """
    return metrics.copy()


def get_health_metrics() -> Dict[str, Any]:
    """
    Get health-related metrics.
    
    Returns:
        Dictionary of health metrics
    """
    uptime = (datetime.utcnow() - datetime.fromisoformat(metrics["start_time"])).total_seconds()
    
    return {
        "uptime_seconds": int(uptime),
        "requests_total": metrics["requests_total"],
        "llm_calls_total": metrics["llm_calls_total"],
        "cache_hit_rate": (
            metrics["cache_hits"] / (metrics["cache_hits"] + metrics["cache_misses"])
            if (metrics["cache_hits"] + metrics["cache_misses"]) > 0
            else 0
        ),
        "average_response_time_ms": metrics["average_response_time_ms"],
        "error_rate": (
            sum(metrics["requests_by_status"].values())
            - metrics["requests_by_status"].get("200", 0)
        ) / metrics["requests_total"] if metrics["requests_total"] > 0 else 0
    }

