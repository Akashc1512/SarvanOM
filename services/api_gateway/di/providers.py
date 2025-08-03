"""
Service Providers

This module provides service providers for dependency injection of all agent services.
It manages service registration, instantiation, and lifecycle management.
"""

import logging
from typing import Dict, Any, Optional, Type
from functools import lru_cache

from .container import DIContainer, get_container
from ..services.base_service import BaseAgentService, ServiceType
from ..services.browser_service import BrowserService
from ..services.pdf_service import PDFService
from ..services.knowledge_service import KnowledgeService
from ..services.code_service import CodeService
from ..services.database_service import DatabaseService
from ..services.crawler_service import CrawlerService

logger = logging.getLogger(__name__)


class ServiceProvider:
    """
    Service provider for managing agent service dependencies.
    
    This class handles service registration, instantiation, and lifecycle
    management for all agent services through the DI container.
    """
    
    def __init__(self, container: Optional[DIContainer] = None):
        """
        Initialize the service provider.
        
        Args:
            container: DI container instance (uses global if not provided)
        """
        self.container = container or get_container()
        self._register_services()
        logger.info("Service provider initialized")
    
    def _register_services(self) -> None:
        """Register all agent services with the DI container."""
        try:
            # Register all services as singletons
            self.container.register_singleton("browser_service", BrowserService)
            self.container.register_singleton("pdf_service", PDFService)
            self.container.register_singleton("knowledge_service", KnowledgeService)
            self.container.register_singleton("code_service", CodeService)
            self.container.register_singleton("database_service", DatabaseService)
            self.container.register_singleton("crawler_service", CrawlerService)
            
            logger.info("All agent services registered with DI container")
            
        except Exception as e:
            logger.error(f"Failed to register services: {e}")
            raise
    
    def get_browser_service(self) -> BrowserService:
        """Get browser service instance."""
        return self.container.resolve("browser_service")
    
    def get_pdf_service(self) -> PDFService:
        """Get PDF service instance."""
        return self.container.resolve("pdf_service")
    
    def get_knowledge_service(self) -> KnowledgeService:
        """Get knowledge service instance."""
        return self.container.resolve("knowledge_service")
    
    def get_code_service(self) -> CodeService:
        """Get code service instance."""
        return self.container.resolve("code_service")
    
    def get_database_service(self) -> DatabaseService:
        """Get database service instance."""
        return self.container.resolve("database_service")
    
    def get_crawler_service(self) -> CrawlerService:
        """Get crawler service instance."""
        return self.container.resolve("crawler_service")
    
    def get_service_by_type(self, service_type: ServiceType) -> BaseAgentService:
        """
        Get service instance by service type.
        
        Args:
            service_type: The type of service to get
            
        Returns:
            Service instance
        """
        service_map = {
            ServiceType.BROWSER: self.get_browser_service,
            ServiceType.PDF: self.get_pdf_service,
            ServiceType.KNOWLEDGE: self.get_knowledge_service,
            ServiceType.CODE: self.get_code_service,
            ServiceType.DATABASE: self.get_database_service,
            ServiceType.CRAWLER: self.get_crawler_service
        }
        
        if service_type not in service_map:
            raise ValueError(f"Unknown service type: {service_type}")
        
        return service_map[service_type]()
    
    def get_all_services(self) -> Dict[str, BaseAgentService]:
        """
        Get all service instances.
        
        Returns:
            Dictionary of all service instances
        """
        return {
            "browser": self.get_browser_service(),
            "pdf": self.get_pdf_service(),
            "knowledge": self.get_knowledge_service(),
            "code": self.get_code_service(),
            "database": self.get_database_service(),
            "crawler": self.get_crawler_service()
        }
    
    async def health_check_all_services(self) -> Dict[str, Any]:
        """
        Perform health check on all services.
        
        Returns:
            Health check results for all services
        """
        results = {}
        overall_healthy = True
        
        try:
            services = self.get_all_services()
            
            for name, service in services.items():
                try:
                    health_info = await service.health_check()
                    results[name] = health_info
                    
                    if not health_info.get("healthy", False):
                        overall_healthy = False
                        
                except Exception as e:
                    logger.error(f"Health check failed for {name} service: {e}")
                    results[name] = {
                        "healthy": False,
                        "error": str(e)
                    }
                    overall_healthy = False
            
            return {
                "overall_healthy": overall_healthy,
                "services": results,
                "total_services": len(services)
            }
            
        except Exception as e:
            logger.error(f"Failed to perform health checks: {e}")
            return {
                "overall_healthy": False,
                "error": str(e),
                "services": {},
                "total_services": 0
            }
    
    async def shutdown_all_services(self) -> None:
        """Shutdown all services."""
        try:
            services = self.get_all_services()
            
            for name, service in services.items():
                try:
                    await service.shutdown()
                    logger.info(f"Shutdown {name} service")
                except Exception as e:
                    logger.error(f"Failed to shutdown {name} service: {e}")
            
            logger.info("All services shutdown complete")
            
        except Exception as e:
            logger.error(f"Failed to shutdown services: {e}")
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about all registered services.
        
        Returns:
            Service information
        """
        try:
            services = self.get_all_services()
            
            info = {
                "total_services": len(services),
                "services": {}
            }
            
            for name, service in services.items():
                info["services"][name] = {
                    "service_type": service.service_type.value,
                    "status": service.status.value,
                    "uptime_seconds": (service.start_time - service.start_time).total_seconds(),
                    "request_count": service.request_count,
                    "error_count": service.error_count
                }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get service info: {e}")
            return {
                "total_services": 0,
                "error": str(e),
                "services": {}
            }


# Global service provider instance
_service_provider: Optional[ServiceProvider] = None


def get_service_provider() -> ServiceProvider:
    """
    Get the global service provider instance.
    
    Returns:
        The global service provider
    """
    global _service_provider
    if _service_provider is None:
        _service_provider = ServiceProvider()
    return _service_provider


def set_service_provider(provider: ServiceProvider) -> None:
    """
    Set the global service provider instance.
    
    Args:
        provider: The service provider to set as global
    """
    global _service_provider
    _service_provider = provider


# FastAPI dependency functions for route handlers
@lru_cache()
def get_browser_service() -> BrowserService:
    """Get browser service for dependency injection."""
    return get_service_provider().get_browser_service()


@lru_cache()
def get_pdf_service() -> PDFService:
    """Get PDF service for dependency injection."""
    return get_service_provider().get_pdf_service()


@lru_cache()
def get_knowledge_service() -> KnowledgeService:
    """Get knowledge service for dependency injection."""
    return get_service_provider().get_knowledge_service()


@lru_cache()
def get_code_service() -> CodeService:
    """Get code service for dependency injection."""
    return get_service_provider().get_code_service()


@lru_cache()
def get_database_service() -> DatabaseService:
    """Get database service for dependency injection."""
    return get_service_provider().get_database_service()


@lru_cache()
def get_crawler_service() -> CrawlerService:
    """Get crawler service for dependency injection."""
    return get_service_provider().get_crawler_service()


# Service factory for advanced usage
class ServiceFactory:
    """
    Service factory for creating and managing service instances.
    
    This factory provides advanced service management capabilities
    including configuration, lifecycle management, and monitoring.
    """
    
    def __init__(self, provider: Optional[ServiceProvider] = None):
        """
        Initialize the service factory.
        
        Args:
            provider: Service provider instance
        """
        self.provider = provider or get_service_provider()
        logger.info("Service factory initialized")
    
    def create_service(self, service_type: ServiceType, config: Optional[Dict[str, Any]] = None) -> BaseAgentService:
        """
        Create a service instance with configuration.
        
        Args:
            service_type: Type of service to create
            config: Service configuration
            
        Returns:
            Service instance
        """
        service = self.provider.get_service_by_type(service_type)
        
        if config:
            # Update service configuration
            for key, value in config.items():
                service.set_config(key, value)
        
        return service
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all services."""
        return await self.provider.health_check_all_services()
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about all services."""
        return self.provider.get_service_info()
    
    async def shutdown_all(self) -> None:
        """Shutdown all services."""
        await self.provider.shutdown_all_services()


# Global service factory instance
_service_factory: Optional[ServiceFactory] = None


def get_service_factory() -> ServiceFactory:
    """
    Get the global service factory instance.
    
    Returns:
        The global service factory
    """
    global _service_factory
    if _service_factory is None:
        _service_factory = ServiceFactory()
    return _service_factory


def set_service_factory(factory: ServiceFactory) -> None:
    """
    Set the global service factory instance.
    
    Args:
        factory: The service factory to set as global
    """
    global _service_factory
    _service_factory = factory 