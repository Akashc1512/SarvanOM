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


# Create FastAPI application
app = FastAPI(
    title="SarvanOM Backend",
    description="Clean Architecture Backend for SarvanOM Universal Knowledge Hub",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
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


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    
    # Log request
    logger.info(f"📥 {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(f"📤 {response.status_code} - {process_time:.3f}s")
    
    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Middleware for request ID
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to request state."""
    import uuid
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 