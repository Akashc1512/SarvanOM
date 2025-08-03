"""
Service Factory

This module provides a factory for creating and configuring agent services.
It manages service instantiation, configuration, and dependency injection.
"""

import logging
from typing import Dict, Any, Optional, Type
from datetime import datetime

from .base_service import BaseAgentService, ServiceType, ServiceStatus
from ..di.container import get_container, DIContainer

logger = logging.getLogger(__name__)


class ServiceFactory:
    """
    Factory for creating and managing agent services.
    
    This factory handles service instantiation, configuration, and dependency
    injection. It provides a centralized way to create and manage all agent services.
    """
    
    def __init__(self, container: Optional[DIContainer] = None):
        """
        Initialize the service factory.
        
        Args:
            container: DI container instance (uses global if not provided)
        """
        self.container = container or get_container()
        self._services: Dict[str, BaseAgentService] = {}
        self._service_classes: Dict[str, Type[BaseAgentService]] = {}
        
        logger.info("Initialized service factory")
    
    def register_service_class(
        self, 
        service_type: ServiceType, 
        service_class: Type[BaseAgentService]
    ) -> None:
        """
        Register a service class.
        
        Args:
            service_type: The type of service
            service_class: The service class to register
        """
        self._service_classes[service_type.value] = service_class
        logger.info(f"Registered service class: {service_type.value}")
    
    def create_service(
        self, 
        service_type: ServiceType, 
        config: Optional[Dict[str, Any]] = None
    ) -> BaseAgentService:
        """
        Create a service instance.
        
        Args:
            service_type: The type of service to create
            config: Service configuration
            
        Returns:
            The created service instance
            
        Raises:
            ValueError: If service class is not registered
        """
        if service_type.value not in self._service_classes:
            raise ValueError(f"Service class not registered for type: {service_type.value}")
        
        service_class = self._service_classes[service_type.value]
        service = service_class(service_type, config or {})
        
        # Register with DI container as singleton
        self.container.register_singleton(service_type.value, lambda _: service)
        
        # Store in local registry
        self._services[service_type.value] = service
        
        logger.info(f"Created service instance: {service_type.value}")
        return service
    
    def get_service(self, service_type: ServiceType) -> Optional[BaseAgentService]:
        """
        Get a service instance.
        
        Args:
            service_type: The type of service to get
            
        Returns:
            The service instance or None if not found
        """
        # Try to get from DI container first
        try:
            return self.container.resolve(service_type.value)
        except KeyError:
            # Try local registry
            return self._services.get(service_type.value)
    
    def get_or_create_service(
        self, 
        service_type: ServiceType, 
        config: Optional[Dict[str, Any]] = None
    ) -> BaseAgentService:
        """
        Get an existing service or create a new one.
        
        Args:
            service_type: The type of service
            config: Service configuration (used only if creating new service)
            
        Returns:
            The service instance
        """
        service = self.get_service(service_type)
        if service is None:
            service = self.create_service(service_type, config)
        return service
    
    def get_all_services(self) -> Dict[str, BaseAgentService]:
        """
        Get all registered services.
        
        Returns:
            Dictionary of all service instances
        """
        return self._services.copy()
    
    def get_service_status(self, service_type: ServiceType) -> Dict[str, Any]:
        """
        Get status of a specific service.
        
        Args:
            service_type: The type of service
            
        Returns:
            Service status information
        """
        service = self.get_service(service_type)
        if service is None:
            return {
                "service_type": service_type.value,
                "status": "not_created",
                "created": False
            }
        
        return {
            "service_type": service_type.value,
            "status": service.status.value,
            "created": True,
            "uptime_seconds": (datetime.now() - service.start_time).total_seconds(),
            "request_count": service.request_count,
            "error_count": service.error_count
        }
    
    def get_all_service_statuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all services.
        
        Returns:
            Dictionary of all service statuses
        """
        return {
            service_type.value: self.get_service_status(service_type)
            for service_type in ServiceType
        }
    
    def health_check_all_services(self) -> Dict[str, Any]:
        """
        Perform health check on all services.
        
        Returns:
            Health check results for all services
        """
        results = {}
        overall_healthy = True
        
        for service_type in ServiceType:
            service = self.get_service(service_type)
            if service is None:
                results[service_type.value] = {
                    "healthy": False,
                    "error": "Service not created",
                    "status": "not_created"
                }
                overall_healthy = False
            else:
                try:
                    health_info = service.get_service_info()
                    health_info["healthy"] = service.status == ServiceStatus.HEALTHY
                    results[service_type.value] = health_info
                    
                    if service.status != ServiceStatus.HEALTHY:
                        overall_healthy = False
                        
                except Exception as e:
                    results[service_type.value] = {
                        "healthy": False,
                        "error": str(e),
                        "status": "error"
                    }
                    overall_healthy = False
        
        return {
            "overall_healthy": overall_healthy,
            "services": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def shutdown_all_services(self) -> None:
        """Shutdown all services."""
        for service in self._services.values():
            try:
                if hasattr(service, 'shutdown'):
                    service.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down service {service.service_type.value}: {e}")
        
        self._services.clear()
        logger.info("Shutdown all services")
    
    def reload_service_config(
        self, 
        service_type: ServiceType, 
        new_config: Dict[str, Any]
    ) -> bool:
        """
        Reload configuration for a specific service.
        
        Args:
            service_type: The type of service
            new_config: New configuration
            
        Returns:
            True if configuration was reloaded successfully
        """
        service = self.get_service(service_type)
        if service is None:
            logger.warning(f"Cannot reload config for non-existent service: {service_type.value}")
            return False
        
        try:
            success = service.reload_config(new_config)
            if success:
                logger.info(f"Successfully reloaded config for service: {service_type.value}")
            else:
                logger.error(f"Failed to reload config for service: {service_type.value}")
            return success
            
        except Exception as e:
            logger.error(f"Error reloading config for service {service_type.value}: {e}")
            return False
    
    def get_service_metrics(self, service_type: ServiceType) -> Dict[str, Any]:
        """
        Get metrics for a specific service.
        
        Args:
            service_type: The type of service
            
        Returns:
            Service metrics
        """
        service = self.get_service(service_type)
        if service is None:
            return {
                "service_type": service_type.value,
                "error": "Service not found"
            }
        
        try:
            return service.get_metrics()
        except Exception as e:
            return {
                "service_type": service_type.value,
                "error": str(e)
            }
    
    def get_all_service_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all services.
        
        Returns:
            Dictionary of all service metrics
        """
        return {
            service_type.value: self.get_service_metrics(service_type)
            for service_type in ServiceType
        }


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