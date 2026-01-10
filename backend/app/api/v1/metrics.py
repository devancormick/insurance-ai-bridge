"""Metrics API endpoints."""
from fastapi import APIRouter
from fastapi.responses import Response
from app.core.monitoring import get_metrics, get_health_metrics

router = APIRouter()


@router.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint.
    
    Returns:
        Prometheus metrics format
    """
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        
        # Generate Prometheus metrics
        metrics_output = generate_latest()
        return Response(
            content=metrics_output,
            media_type=CONTENT_TYPE_LATEST
        )
    except ImportError:
        # Fallback to JSON metrics if Prometheus not available
        from app.core.monitoring import get_metrics
        metrics = get_metrics()
        
        # Convert to Prometheus-like format
        prometheus_format = ""
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                prometheus_format += f"# TYPE {key} gauge\n"
                prometheus_format += f"{key} {value}\n"
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, (int, float)):
                        prometheus_format += f"{key}{{{subkey}}} {subvalue}\n"
        
        return Response(
            content=prometheus_format,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )


@router.get("/health/metrics")
async def health_metrics():
    """
    Get health-related metrics.
    
    Returns:
        Health metrics dictionary
    """
    return get_health_metrics()

