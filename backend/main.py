"""
Main FastAPI Application

This is the main entry point for the SarvanOM backend application.
It sets up the FastAPI app with all routers and middleware.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .api.routers import routers
from .api.dependencies import get_cache_service, get_metrics_service
from shared.core.config.central_config import (
    initialize_config,
    get_central_config,
)
from .api.middleware.error_handling import (
    ErrorHandlingMiddleware, 
    SecurityHeadersMiddleware, 
    RequestLoggingMiddleware
)
from .api.middleware.monitoring import (
    PerformanceMonitoringMiddleware, 
    HealthCheckMiddleware, 
    RateLimitingMiddleware
)
from .services.core.cache_service import CacheService
from .services.core.metrics_service import MetricsService
from shared.core.logging.structured_logger import get_logger, set_request_id
from shared.core.metrics.metrics_service import get_metrics_service
from backend.api.middleware.logging_middleware import (
    LoggingMiddleware, 
    PerformanceMonitoringMiddleware, 
    ErrorLoggingMiddleware
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 SarvanOM Backend starting up...")
    
    # Initialize core services
    cache_service = get_cache_service()
    metrics_service = get_metrics_service()
    
    logger.info("✅ Core services initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 SarvanOM Backend shutting down...")
    
    # Cleanup
    await cache_service.clear()
    logger.info("✅ Cleanup completed")


# Initialize configuration
config = initialize_config()

# Create FastAPI application
app = FastAPI(
    title="SarvanOM API Gateway",
    description="Multi-agent orchestration platform for intelligent query processing",
    version="1.0.0"
)

# Get configuration
config = get_central_config()
metrics_service = get_metrics_service()

# Setup Middleware (order matters - last added is first executed)
# Error handling middleware (should be last/innermost)
app.add_middleware(ErrorLoggingMiddleware)
# Performance monitoring
app.add_middleware(PerformanceMonitoringMiddleware, metrics_service=metrics_service)
# Request logging
app.add_middleware(LoggingMiddleware, include_headers=False, include_body=False)
# CORS (should be outer/first middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=config.cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    request_id = set_request_id()
    logger.error(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "timestamp": time.time()
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import Response
    metrics_data = metrics_service.get_metrics()
    return Response(
        content=metrics_data,
        media_type=metrics_service.get_metrics_content_type()
    )

# Include routers
from backend.api.routers import query_router, health_router

app.include_router(query_router.router, prefix="/api/v1")
app.include_router(health_router.router, prefix="/api/v1")

logger.info("API Gateway started successfully", 
           cors_origins=config.cors_origins,
           log_level=logging.getLevelName(logging.getLogger().level))


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "SarvanOM Backend",
        "version": "1.0.0",
        "architecture": "Clean Architecture",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "queries": "/query",
            "health": "/health",
            "agents": "/agents",
            "admin": "/admin",
            "auth": "/auth",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 