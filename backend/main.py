"""
Backend Main Entry Point

This is the main entry point for the new modular backend structure.
It initializes the API gateway and starts the FastAPI server.
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# FastAPI imports
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the gateway service
from gateway.gateway_service import GatewayService

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
    logger.info("Starting backend services...")
    
    # Initialize services
    try:
        # The gateway service will initialize all other services
        gateway = GatewayService()
        app.state.gateway = gateway
        logger.info("Backend services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize backend services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down backend services...")
    try:
        if hasattr(app.state, 'gateway'):
            await app.state.gateway.shutdown()
        logger.info("Backend services shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Create the gateway service
    gateway = GatewayService()
    
    # Get the FastAPI app from the gateway
    app = gateway.app
    
    # Add lifespan manager
    app.router.lifespan_context = lifespan
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


def main():
    """Main entry point for the backend application."""
    try:
        # Create the application
        app = create_app()
        
        # Get configuration from environment
        host = os.getenv("BACKEND_HOST", "0.0.0.0")
        port = int(os.getenv("BACKEND_PORT", "8000"))
        reload = os.getenv("BACKEND_RELOAD", "false").lower() == "true"
        
        logger.info(f"Starting backend server on {host}:{port}")
        logger.info(f"Reload mode: {reload}")
        
        # Start the server
        uvicorn.run(
            "backend.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("Backend server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start backend server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 