"""
Dependency Injection Container

This module provides a simple DI container for managing service dependencies
and lifecycle. It supports singleton and factory patterns for service creation.
"""

import logging
from shared.core.unified_logging import get_logger
from typing import Dict, Any, Optional, Callable, Type, Union
from datetime import datetime
from enum import Enum

logger = get_logger(__name__)


class ServiceLifetime(Enum):
    """Service lifetime enumeration."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class DIContainer:
    """
    Simple dependency injection container.

    This container manages service registration, instantiation, and lifecycle.
    It supports singleton, transient, and scoped service lifetimes.
    """

    def __init__(self):
        """Initialize the DI container."""
        self._services: Dict[str, Dict[str, Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._scoped_instances: Dict[str, Dict[str, Any]] = {}
        self._factories: Dict[str, Callable] = {}

        logger.info("Initialized DI container")

    def register_singleton(
        self,
        service_type: str,
        implementation: Union[Type, Callable],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a singleton service.

        Args:
            service_type: The service type identifier
            implementation: The service implementation class or factory
            config: Optional configuration for the service
        """
        self._services[service_type] = {
            "lifetime": ServiceLifetime.SINGLETON,
            "implementation": implementation,
            "config": config or {},
            "registered_at": datetime.now(),
        }

        logger.info(f"Registered singleton service: {service_type}")

    def register_transient(
        self,
        service_type: str,
        implementation: Union[Type, Callable],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a transient service.

        Args:
            service_type: The service type identifier
            implementation: The service implementation class or factory
            config: Optional configuration for the service
        """
        self._services[service_type] = {
            "lifetime": ServiceLifetime.TRANSIENT,
            "implementation": implementation,
            "config": config or {},
            "registered_at": datetime.now(),
        }

        logger.info(f"Registered transient service: {service_type}")

    def register_scoped(
        self,
        service_type: str,
        implementation: Union[Type, Callable],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a scoped service.

        Args:
            service_type: The service type identifier
            implementation: The service implementation class or factory
            config: Optional configuration for the service
        """
        self._services[service_type] = {
            "lifetime": ServiceLifetime.SCOPED,
            "implementation": implementation,
            "config": config or {},
            "registered_at": datetime.now(),
        }

        logger.info(f"Registered scoped service: {service_type}")

    def register_factory(
        self,
        service_type: str,
        factory: Callable,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a service factory.

        Args:
            service_type: The service type identifier
            factory: Factory function to create service instances
            config: Optional configuration for the factory
        """
        self._factories[service_type] = factory
        self._services[service_type] = {
            "lifetime": ServiceLifetime.TRANSIENT,
            "implementation": factory,
            "config": config or {},
            "registered_at": datetime.now(),
            "is_factory": True,
        }

        logger.info(f"Registered factory service: {service_type}")

    def resolve(self, service_type: str, scope_id: Optional[str] = None) -> Any:
        """
        Resolve a service instance.

        Args:
            service_type: The service type to resolve
            scope_id: Optional scope identifier for scoped services

        Returns:
            The resolved service instance

        Raises:
            KeyError: If service is not registered
        """
        if service_type not in self._services:
            raise KeyError(f"Service '{service_type}' is not registered")

        service_info = self._services[service_type]
        lifetime = service_info["lifetime"]
        implementation = service_info["implementation"]
        config = service_info.get("config", {})

        try:
            if lifetime == ServiceLifetime.SINGLETON:
                return self._resolve_singleton(service_type, implementation, config)
            elif lifetime == ServiceLifetime.TRANSIENT:
                return self._resolve_transient(service_type, implementation, config)
            elif lifetime == ServiceLifetime.SCOPED:
                return self._resolve_scoped(
                    service_type, implementation, config, scope_id
                )
            else:
                raise ValueError(f"Unknown service lifetime: {lifetime}")

        except Exception as e:
            logger.error(f"Failed to resolve service '{service_type}': {e}")
            raise

    def _resolve_singleton(
        self,
        service_type: str,
        implementation: Union[Type, Callable],
        config: Dict[str, Any],
    ) -> Any:
        """Resolve a singleton service."""
        if service_type in self._singletons:
            return self._singletons[service_type]

        instance = self._create_instance(implementation, config)
        self._singletons[service_type] = instance

        logger.debug(f"Created singleton instance for service: {service_type}")
        return instance

    def _resolve_transient(
        self,
        service_type: str,
        implementation: Union[Type, Callable],
        config: Dict[str, Any],
    ) -> Any:
        """Resolve a transient service."""
        instance = self._create_instance(implementation, config)

        logger.debug(f"Created transient instance for service: {service_type}")
        return instance

    def _resolve_scoped(
        self,
        service_type: str,
        implementation: Union[Type, Callable],
        config: Dict[str, Any],
        scope_id: str,
    ) -> Any:
        """Resolve a scoped service."""
        if not scope_id:
            raise ValueError(f"Scope ID required for scoped service: {service_type}")

        if scope_id not in self._scoped_instances:
            self._scoped_instances[scope_id] = {}

        if service_type in self._scoped_instances[scope_id]:
            return self._scoped_instances[scope_id][service_type]

        instance = self._create_instance(implementation, config)
        self._scoped_instances[scope_id][service_type] = instance

        logger.debug(
            f"Created scoped instance for service: {service_type} in scope: {scope_id}"
        )
        return instance

    def _create_instance(
        self, implementation: Union[Type, Callable], config: Dict[str, Any]
    ) -> Any:
        """Create a service instance."""
        if callable(implementation) and not isinstance(implementation, type):
            # Factory function
            return implementation(config)
        elif isinstance(implementation, type):
            # Class constructor
            return implementation(config)
        else:
            raise ValueError(f"Invalid implementation type: {type(implementation)}")

    def get_service_info(self, service_type: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered service.

        Args:
            service_type: The service type to get info for

        Returns:
            Service information dictionary or None if not found
        """
        if service_type not in self._services:
            return None

        service_info = self._services[service_type].copy()
        service_info["is_singleton_created"] = service_type in self._singletons

        return service_info

    def get_all_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all registered services.

        Returns:
            Dictionary of all registered services
        """
        return {
            service_type: self.get_service_info(service_type)
            for service_type in self._services.keys()
        }

    def is_registered(self, service_type: str) -> bool:
        """
        Check if a service is registered.

        Args:
            service_type: The service type to check

        Returns:
            True if service is registered, False otherwise
        """
        return service_type in self._services

    def unregister(self, service_type: str) -> bool:
        """
        Unregister a service.

        Args:
            service_type: The service type to unregister

        Returns:
            True if service was unregistered, False if not found
        """
        if service_type not in self._services:
            return False

        # Remove from services
        del self._services[service_type]

        # Remove singleton instance if exists
        if service_type in self._singletons:
            del self._singletons[service_type]

        # Remove from factories if exists
        if service_type in self._factories:
            del self._factories[service_type]

        # Remove from all scoped instances
        for scope_instances in self._scoped_instances.values():
            if service_type in scope_instances:
                del scope_instances[service_type]

        logger.info(f"Unregistered service: {service_type}")
        return True

    def clear_scope(self, scope_id: str) -> None:
        """
        Clear all instances for a specific scope.

        Args:
            scope_id: The scope ID to clear
        """
        if scope_id in self._scoped_instances:
            del self._scoped_instances[scope_id]
            logger.info(f"Cleared scope: {scope_id}")

    def clear_all_scopes(self) -> None:
        """Clear all scoped instances."""
        self._scoped_instances.clear()
        logger.info("Cleared all scoped instances")

    def shutdown(self) -> None:
        """Shutdown the container and cleanup resources."""
        # Shutdown all singleton services
        for service_type, instance in self._singletons.items():
            if hasattr(instance, "shutdown"):
                try:
                    instance.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down service '{service_type}': {e}")

        # Clear all collections
        self._services.clear()
        self._singletons.clear()
        self._scoped_instances.clear()
        self._factories.clear()

        logger.info("DI container shutdown complete")


# Global container instance
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """
    Get the global DI container instance.

    Returns:
        The global DI container
    """
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def set_container(container: DIContainer) -> None:
    """
    Set the global DI container instance.

    Args:
        container: The DI container to set as global
    """
    global _container
    _container = container
