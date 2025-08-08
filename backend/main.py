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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    title=config.app_name or "SarvanOM Backend",
    description="Clean Architecture Backend for SarvanOM Universal Knowledge Hub",
    version=config.app_version or "1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup Middleware (order matters - last added is first executed)

# Error handling middleware (should be last/innermost)
metrics_service = get_metrics_service()
app.add_middleware(ErrorHandlingMiddleware, metrics_service=metrics_service)

# Security headers
if config.security_headers_enabled:
    app.add_middleware(SecurityHeadersMiddleware)

# Performance monitoring
app.add_middleware(PerformanceMonitoringMiddleware, metrics_service=metrics_service)

# Health monitoring
app.add_middleware(HealthCheckMiddleware)

# Rate limiting
if config.rate_limit_enabled:
    app.add_middleware(
        RateLimitingMiddleware,
        max_requests=int(config.rate_limit_per_minute),
        time_window=60,
    )

# Request logging
app.add_middleware(RequestLoggingMiddleware, metrics_service=metrics_service)

# CORS (should be outer/first middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=bool(config.cors_credentials),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
for router in routers:
    app.include_router(router)

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


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check core services
        cache_service = get_cache_service()
        metrics_service = get_metrics_service()
        
        cache_stats = await cache_service.get_stats()
        metrics_summary = metrics_service.get_metrics_summary()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "cache": {
                    "status": "healthy",
                    "stats": cache_stats
                },
                "metrics": {
                    "status": "healthy",
                    "summary": metrics_summary
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    try:
        metrics_service = get_metrics_service()
        return metrics_service.export_metrics()
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving metrics")


# Note: Exception handlers and request middleware are now handled by dedicated middleware classes


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 