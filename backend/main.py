"""
Backend Main Entry Point for SarvanOM

This module provides the main FastAPI application for the backend services,
following clean architecture principles with clear separation of concerns.

Architecture:
- API Layer: FastAPI routers and middleware
- Service Layer: Business logic and orchestration
- Domain Layer: Core business models and rules
- Infrastructure Layer: Data access and external services
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Import shared components
from shared.core.unified_logging import setup_logging, get_logger, setup_fastapi_logging

# Import API routers
from .api.routers import (
    admin_router,
    agent_router,
    auth_router,
    database_router,
    health_router,
    query_router
)

# Import services
from .services.health.health_service import HealthService
from .services.core.database_service import DatabaseService
from .services.core.cache_service import CacheService
from .services.core.metrics_service import MetricsService

# Configure logging
logging_config = setup_logging(service_name="sarvanom-backend")
logger = get_logger(__name__)

# Initialize services
health_service = HealthService()
database_service = DatabaseService()
cache_service = CacheService()
metrics_service = MetricsService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting SarvanOM Backend Services...")
    
    try:
        # Initialize database connection
        await database_service.initialize()
        logger.info("✅ Database service initialized")
        
        # Initialize cache service
        await cache_service.initialize()
        logger.info("✅ Cache service initialized")
        
        # Initialize metrics service
        await metrics_service.initialize()
        logger.info("✅ Metrics service initialized")
        
        logger.info("🎉 All backend services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize backend services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down backend services...")
    
    try:
        await database_service.close()
        await cache_service.close()
        await metrics_service.close()
        logger.info("✅ All backend services shut down successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

# Create FastAPI app
app = FastAPI(
    title="SarvanOM Backend API",
    description="Clean architecture backend services for SarvanOM Universal Knowledge Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Security configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://sarvanom.com",
    "https://www.sarvanom.com"
]

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "sarvanom.com", "www.sarvanom.com"]
)

# Configure FastAPI logging
setup_fastapi_logging(app)

# Include routers
app.include_router(health_router.router, prefix="/health", tags=["health"])
app.include_router(auth_router.router, prefix="/auth", tags=["authentication"])
app.include_router(admin_router.router, prefix="/admin", tags=["administration"])
app.include_router(agent_router.router, prefix="/agents", tags=["agents"])
app.include_router(query_router.router, prefix="/queries", tags=["queries"])
app.include_router(database_router.router, prefix="/database", tags=["database"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SarvanOM Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/status")
async def status():
    """Service status endpoint"""
    try:
        health_status = await health_service.get_health_status()
        return {
            "status": "healthy",
            "timestamp": health_status.timestamp,
            "services": health_status.services
        }
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
