"""
Dependency Injection Module

This module provides dependency injection capabilities for the API gateway.
It includes the DI container, service providers, and configuration management.
"""

from .container import DIContainer, ServiceLifetime, get_container, set_container

from .providers import (
    ServiceProvider,
    ServiceFactory,
    get_service_provider,
    set_service_provider,
    get_service_factory,
    set_service_factory,
    # FastAPI dependency functions
    get_browser_service,
    get_pdf_service,
    get_knowledge_service,
    get_code_service,
    get_database_service,
    get_crawler_service,
)

from .config import (
    ConfigManager,
    ServiceConfig,
    BrowserServiceConfig,
    PDFServiceConfig,
    KnowledgeServiceConfig,
    CodeServiceConfig,
    DatabaseServiceConfig,
    CrawlerServiceConfig,
    get_config_manager,
    set_config_manager,
)

__all__ = [
    # Container
    "DIContainer",
    "ServiceLifetime",
    "get_container",
    "set_container",
    # Service Providers
    "ServiceProvider",
    "ServiceFactory",
    "get_service_provider",
    "set_service_provider",
    "get_service_factory",
    "set_service_factory",
    # FastAPI Dependencies
    "get_browser_service",
    "get_pdf_service",
    "get_knowledge_service",
    "get_code_service",
    "get_database_service",
    "get_crawler_service",
    # Configuration
    "ConfigManager",
    "ServiceConfig",
    "BrowserServiceConfig",
    "PDFServiceConfig",
    "KnowledgeServiceConfig",
    "CodeServiceConfig",
    "DatabaseServiceConfig",
    "CrawlerServiceConfig",
    "get_config_manager",
    "set_config_manager",
]
