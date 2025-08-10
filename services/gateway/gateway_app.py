"""
API Gateway Application

This module provides the main FastAPI application that serves as the API gateway
for routing requests to various microservices.
"""

# Load environment variables from .env file first
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if present
except ImportError:
    pass  # dotenv not installed, continue without it

import logging
from typing import Dict, Any

# Try to import FastAPI, but handle gracefully if not installed
try:
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from contextlib import asynccontextmanager

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for testing
    class FastAPI:
        def __init__(self, **kwargs):
            pass

        def add_middleware(self, *args, **kwargs):
            pass

        def include_router(self, *args, **kwargs):
            pass

        def middleware(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

    class Request:
        pass

    class CORSMiddleware:
        pass

    class TrustedHostMiddleware:
        pass

    from contextlib import asynccontextmanager

from .routes import (
    health_router,
    search_router,
    fact_check_router,
    synthesis_router,
    auth_router,
    crawler_router,
    vector_router,
    graph_router,
)

# Import unified logging
from shared.core.unified_logging import setup_logging, get_logger, setup_fastapi_logging

# Configure unified logging
logging_config = setup_logging(service_name="sarvanom-gateway")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 API Gateway starting up...")
    yield
    # Shutdown
    logger.info("🛑 API Gateway shutting down...")


def create_gateway_app() -> FastAPI:
    """Create and configure the FastAPI gateway application."""

    app = FastAPI(
        title="Sarvanom API Gateway",
        description="API Gateway for Sarvanom Universal Knowledge Hub",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    if FASTAPI_AVAILABLE:
        # Setup unified logging integration
        setup_fastapi_logging(app, service_name="sarvanom-gateway")

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add trusted host middleware
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure appropriately for production
        )

        # Include routers
        app.include_router(health_router, tags=["Health"])
        app.include_router(search_router, prefix="/search", tags=["Search"])
        app.include_router(fact_check_router, prefix="/fact-check", tags=["Fact Check"])
        app.include_router(synthesis_router, prefix="/synthesize", tags=["Synthesis"])
        app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
        app.include_router(crawler_router, prefix="/crawler", tags=["Crawler"])
        app.include_router(vector_router, prefix="/vector", tags=["Vector"])
        app.include_router(graph_router, prefix="/graph", tags=["Graph"])

        @app.middleware("http")
        async def log_requests(request: Request, call_next):
            """Log all incoming requests."""
            logger.info(f"📥 {request.method} {request.url}")
            response = await call_next(request)
            logger.info(f"📤 {response.status_code}")
            return response

    return app


class GatewayApp:
    """API Gateway application wrapper."""

    def __init__(self):
        self.app = create_gateway_app()
        logger.info("✅ API Gateway initialized successfully")

    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app

    async def startup(self):
        """Startup the gateway application."""
        logger.info("🚀 Starting API Gateway...")

    async def shutdown(self):
        """Shutdown the gateway application."""
        logger.info("🛑 Shutting down API Gateway...")


# Create the application instance
gateway_app = GatewayApp()
app = gateway_app.get_app()


if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        import uvicorn

        uvicorn.run(
            "services.gateway.gateway_app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
        )
    else:
        print("⚠️  FastAPI not available. Install with: pip install fastapi uvicorn")
        print("✅ Gateway structure is ready for deployment")
