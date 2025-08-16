"""
FastAPI Application Factory - Standardized Service Initialization.

This module provides a factory function to create FastAPI applications with
standardized middleware, common routes, and configuration across all microservices.

Features:
    - Standardized CORS configuration
    - TrustedHost middleware for security
    - Common health and metrics endpoints
    - Prometheus metrics integration
    - Structured logging
    - Environment-based configuration

Security:
    - CORS protection
    - TrustedHost validation
    - Secure defaults
    - Environment-specific settings

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import time
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any, Callable
from functools import wraps

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from shared.core.config.central_config import initialize_config
from shared.core.logging import get_logger
from shared.core.middleware import create_rate_limit_middleware

logger = get_logger(__name__)


def create_app_factory(
    service_name: str,
    description: str,
    version: Optional[str] = None,
    lifespan: Optional[Callable] = None,
    additional_middleware: Optional[List[Callable]] = None,
    additional_routes: Optional[List[Callable]] = None,
    enable_metrics: bool = True,
    enable_health: bool = True,
    enable_root: bool = True,
    enable_rate_limiting: bool = True,
    health_prefix: Optional[str] = None,
    metrics_prefix: Optional[str] = None,
    root_prefix: Optional[str] = None,
) -> Callable[[], FastAPI]:
    """
    Create a FastAPI application factory with standardized configuration.
    
    Args:
        service_name: Name of the service (e.g., "auth", "retrieval")
        description: Service description
        version: Service version (defaults to config.app_version)
        lifespan: Custom lifespan function
        additional_middleware: List of additional middleware functions
        additional_routes: List of additional route functions
        enable_metrics: Whether to include metrics endpoint
        enable_health: Whether to include health endpoint
        enable_root: Whether to include root endpoint
        enable_rate_limiting: Whether to include rate limiting middleware
        health_prefix: Prefix for health endpoint (e.g., "auth" for "/auth/health")
        metrics_prefix: Prefix for metrics endpoint (e.g., "internal" for "/internal/metrics")
        root_prefix: Prefix for root endpoint (e.g., "auth" for "/auth/")
        
    Returns:
        Function that creates and configures a FastAPI app
    """
    
    def create_app() -> FastAPI:
        # Initialize configuration
        config = initialize_config()
        
        # Use provided version or default to config version
        app_version = version or config.app_version
        
        # Default lifespan if not provided
        if lifespan is None:
            @asynccontextmanager
            async def default_lifespan(app: FastAPI):
                logger.info(f"Starting {service_name} service", version=app_version)
                yield
                logger.info(f"Shutting down {service_name} service")
            
            app_lifespan = default_lifespan
        else:
            app_lifespan = lifespan
        
        # Create FastAPI app
        app = FastAPI(
            title=f"{config.service_name}-{service_name}",
            version=app_version,
            description=description,
            lifespan=app_lifespan,
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origins,
            allow_credentials=bool(config.cors_credentials),
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add TrustedHost middleware for security
        if hasattr(config, 'allowed_hosts') and config.allowed_hosts:
            app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=config.allowed_hosts,
            )
        
        # Add rate limiting middleware if enabled
        if enable_rate_limiting and config.rate_limit_enabled:
            rate_limit_middleware = create_rate_limit_middleware(
                requests_per_minute=config.rate_limit_per_minute,
                burst_allowance=config.rate_limit_burst,
                key_prefix=f"rate_limit:{service_name}",
                exclude_paths=["/health", "/metrics", "/docs", "/openapi.json"],
                exclude_methods=["OPTIONS"],
            )
            app.middleware("http")(rate_limit_middleware)
            logger.info(
                f"Rate limiting enabled for {service_name}",
                requests_per_minute=config.rate_limit_per_minute,
                burst_allowance=config.rate_limit_burst,
            )
        
        # Add additional middleware if provided
        if additional_middleware:
            for middleware_func in additional_middleware:
                middleware_func(app)
        
        # Service start time for metrics
        service_start_time = time.time()
        
        # Add health endpoint
        if enable_health:
            health_path = f"/{health_prefix}/health" if health_prefix else "/health"
            @app.get(health_path)
            async def health() -> Dict[str, Any]:
                return {
                    "service": service_name,
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "version": app_version,
                }
        
        # Add metrics endpoint
        if enable_metrics:
            metrics_path = f"/{metrics_prefix}/metrics" if metrics_prefix else "/metrics"
            @app.get(metrics_path)
            async def metrics() -> Response:
                return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
        
        # Add root endpoint
        if enable_root:
            root_path = f"/{root_prefix}" if root_prefix else "/"
            @app.get(root_path)
            async def root() -> Dict[str, Any]:
                return {
                    "service": service_name,
                    "version": app_version,
                    "status": "ok",
                    "description": description,
                    "docs": "/docs",
                    "health": health_path if health_prefix else "/health",
                    "metrics": metrics_path if metrics_prefix else "/metrics",
                }
        
        # Add additional routes if provided
        if additional_routes:
            for route_func in additional_routes:
                route_func(app)
        
        logger.info(
            f"Created FastAPI app for {service_name}",
            version=app_version,
            description=description,
        )
        
        return app
    
    return create_app


def with_request_metrics(service_name: str) -> Callable:
    """
    Decorator to add request metrics to endpoints.
    
    Args:
        service_name: Name of the service for metric labels
        
    Returns:
        Decorator function
    """
    # Create metrics with safe registration
    try:
        request_counter = Counter(
            f"{service_name}_requests_total",
            f"Total {service_name} requests",
            ["endpoint", "method"]
        )
        request_latency = Histogram(
            f"{service_name}_request_latency_seconds",
            f"{service_name} request latency",
            ["endpoint"]
        )
    except ValueError:
        # Metrics already registered, get existing ones
        from prometheus_client import REGISTRY
        request_counter = REGISTRY.get_sample_value(f"{service_name}_requests_total")
        request_latency = REGISTRY.get_sample_value(f"{service_name}_request_latency_seconds")
        # If we can't get them, create dummy metrics for testing
        if request_counter is None:
            class DummyMetric:
                def labels(self, **kwargs): return self
                def inc(self): pass
                def time(self): return DummyContext()
            class DummyContext:
                def __enter__(self): return self
                def __exit__(self, *args): pass
            request_counter = DummyMetric()
            request_latency = DummyMetric()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            endpoint = func.__name__
            method = "POST" if "payload" in kwargs else "GET"
            
            request_counter.labels(endpoint=endpoint, method=method).inc()
            
            with request_latency.labels(endpoint=endpoint).time():
                return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def create_simple_app(
    service_name: str,
    description: str,
    port: int,
    version: Optional[str] = None,
) -> FastAPI:
    """
    Create a simple FastAPI app with basic configuration.
    
    This is a convenience function for services that only need basic setup.
    
    Args:
        service_name: Name of the service
        description: Service description
        port: Port number for the service
        version: Service version
        
    Returns:
        Configured FastAPI app
    """
    app_factory = create_app_factory(
        service_name=service_name,
        description=description,
        version=version,
    )
    
    app = app_factory()
    
    # Add uvicorn run configuration
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(
            f"services.{service_name}.main:app",
            host="0.0.0.0",
            port=port,
            reload=True
        )
    
    return app
