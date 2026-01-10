"""
Distributed Tracing and Telemetry
OpenTelemetry integration for observability
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TelemetryManager:
    """Manages distributed tracing and telemetry"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.service_name = config.get("service_name", "insurance-ai-bridge")
        self.tracer = None
        self.metrics = None
        self._initialize_telemetry()
    
    def _initialize_telemetry(self):
        """Initialize OpenTelemetry"""
        if not self.enabled:
            logger.info("Telemetry is disabled")
            return
        
        try:
            from opentelemetry import trace
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.sdk.resources import Resource
            
            # Initialize tracer
            resource = Resource.create({"service.name": self.service_name})
            trace.set_tracer_provider(TracerProvider(resource=resource))
            
            # Configure Jaeger exporter
            jaeger_endpoint = self.config.get("jaeger_endpoint", "http://jaeger:14268/api/traces")
            jaeger_exporter = JaegerExporter(
                agent_host_name=jaeger_endpoint.split("://")[1].split(":")[0],
                agent_port=int(jaeger_endpoint.split(":")[-1].split("/")[0]) if ":" in jaeger_endpoint else 14268
            )
            
            # Add span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            self.tracer = trace.get_tracer(__name__)
            logger.info("Telemetry initialized with OpenTelemetry")
        
        except ImportError:
            logger.warning("OpenTelemetry packages not installed, telemetry disabled")
            self.enabled = False
        except Exception as e:
            logger.error(f"Error initializing telemetry: {e}", exc_info=True)
            self.enabled = False
    
    def get_tracer(self):
        """Get OpenTelemetry tracer"""
        return self.tracer
    
    def start_span(self, name: str, **kwargs):
        """Start a tracing span"""
        if not self.enabled or not self.tracer:
            return None
        
        return self.tracer.start_span(name, **kwargs)


# Global telemetry manager
telemetry_manager: Optional[TelemetryManager] = None


def get_telemetry_manager() -> TelemetryManager:
    """Get the global telemetry manager"""
    global telemetry_manager
    if telemetry_manager is None:
        from app.config import settings
        telemetry_manager = TelemetryManager(settings.telemetry_config)
    return telemetry_manager

