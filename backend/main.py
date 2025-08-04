"""
Main entry point for the backend application.

This module initializes the FastAPI application and starts the server.

# DEAD CODE - Candidate for deletion: This backend directory is not used by the main application
"""

import logging
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the gateway service
from backend.gateway.gateway_service import GatewayService

# Global gateway service instance
gateway_service: Optional[GatewayService] = None


@asynccontextmanager
async def lifespan(app):
    """Application lifespan manager."""
    global gateway_service
    
    # Startup
    logger.info("Starting backend application...")
    try:
        gateway_service = GatewayService()
        await gateway_service.startup()
        logger.info("Backend application started successfully")
    except Exception as e:
        logger.error(f"Failed to start backend application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down backend application...")
    try:
        if gateway_service:
            await gateway_service.shutdown()
        logger.info("Backend application shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Universal Knowledge Platform API",
        description="Backend API for the Universal Knowledge Platform",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include the API router
    app.include_router(gateway_service.router if gateway_service else app.router)
    
    return app


if __name__ == "__main__":
    # Create the application
    app = create_app()
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True  # Enable auto-reload for development
    ) 