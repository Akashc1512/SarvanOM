"""
CORS Middleware for API Gateway

This module handles Cross-Origin Resource Sharing (CORS) for the API gateway.
It provides configurable CORS settings for web application integration.
"""

from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class CORSConfig:
    """Configuration for CORS middleware."""
    
    def __init__(self):
        from shared.core.config import get_central_config
        config = get_central_config()
        self.allowed_origins: List[str] = config.cors_origins + [
            "https://sarvanom.com",
            "https://www.sarvanom.com"
        ]
        
        self.allowed_methods: List[str] = [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "OPTIONS"
        ]
        
        self.allowed_headers: List[str] = [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-API-Key",
            "X-Request-ID",
            "X-Response-Time"
        ]
        
        self.expose_headers: List[str] = [
            "X-Request-ID",
            "X-Response-Time",
            "X-Security-Check"
        ]
        
        self.allow_credentials: bool = True
        self.max_age: int = 86400  # 24 hours


def setup_cors(app: FastAPI, config: Optional[CORSConfig] = None):
    """
    Setup CORS middleware for FastAPI application.
    
    Args:
        app: FastAPI application instance
        config: CORS configuration (optional)
    """
    if config is None:
        config = CORSConfig()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins,
        allow_credentials=config.allow_credentials,
        allow_methods=config.allowed_methods,
        allow_headers=config.allowed_headers,
        expose_headers=config.expose_headers,
        max_age=config.max_age,
    )


def create_cors_config(
    allowed_origins: Optional[List[str]] = None,
    allowed_methods: Optional[List[str]] = None,
    allowed_headers: Optional[List[str]] = None,
    expose_headers: Optional[List[str]] = None,
    allow_credentials: bool = True,
    max_age: int = 86400
) -> CORSConfig:
    """
    Create a custom CORS configuration.
    
    Args:
        allowed_origins: List of allowed origins
        allowed_methods: List of allowed HTTP methods
        allowed_headers: List of allowed headers
        expose_headers: List of headers to expose
        allow_credentials: Whether to allow credentials
        max_age: Cache duration in seconds
        
    Returns:
        CORS configuration object
    """
    config = CORSConfig()
    
    if allowed_origins is not None:
        config.allowed_origins = allowed_origins
    
    if allowed_methods is not None:
        config.allowed_methods = allowed_methods
    
    if allowed_headers is not None:
        config.allowed_headers = allowed_headers
    
    if expose_headers is not None:
        config.expose_headers = expose_headers
    
    config.allow_credentials = allow_credentials
    config.max_age = max_age
    
    return config


def get_development_cors_config() -> CORSConfig:
    """Get CORS configuration for development environment."""
    config = CORSConfig()
    config.allowed_origins.extend([
        "http://localhost:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8000"
    ])
    return config


def get_production_cors_config() -> CORSConfig:
    """Get CORS configuration for production environment."""
    config = CORSConfig()
    # In production, you might want to restrict origins more strictly
    config.allowed_origins = [
        "https://sarvanom.com",
        "https://www.sarvanom.com",
        "https://app.sarvanom.com"
    ]
    return config 