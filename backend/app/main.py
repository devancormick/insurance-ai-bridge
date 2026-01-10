"""FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.api.v1.router import api_router
from app.core.rate_limiter import rate_limit_middleware, get_rate_limit_config
from app.core.cache import cache
from app.utils.logging import logger
import time

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url] if settings.frontend_url else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """Apply rate limiting based on path."""
    max_requests, window_seconds = get_rate_limit_config(str(request.url.path))
    return await rate_limit_middleware(
        request, call_next, max_requests=max_requests, window_seconds=window_seconds
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": str(request.url.path)
        }
    )

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Insurance AI Bridge API",
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint with detailed status.
    
    Returns:
        Health status of all services
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "api": "healthy",
            "database": "unknown",
            "cache": "unknown",
            "llm": "unknown"
        }
    }
    
    # Check cache
    try:
        await cache.set("health_check", "ok", ttl=10)
        result = await cache.get("health_check")
        if result == "ok":
            health_status["services"]["cache"] = "healthy"
        else:
            health_status["services"]["cache"] = "unhealthy"
    except Exception as e:
        logger.warning(f"Cache health check failed: {e}")
        health_status["services"]["cache"] = "unhealthy"
    
    # Check database (would need actual DB connection)
    # For now, just mark as unknown
    
    # Check LLM availability
    if settings.openai_api_key or settings.anthropic_api_key:
        health_status["services"]["llm"] = "configured"
    else:
        health_status["services"]["llm"] = "not_configured"
    
    # Overall status
    if any(status == "unhealthy" for status in health_status["services"].values()):
        health_status["status"] = "degraded"
    
    return health_status


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info("Initializing cache...")
    await cache.get("startup_check")  # Initialize cache connection
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application...")
    await cache.close()
    logger.info("Application shutdown complete")

