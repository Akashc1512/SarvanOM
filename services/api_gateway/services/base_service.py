"""
Base service interface for all agent services.

This module defines the common interface that all agent services must implement.
It provides standard methods for health checks, status reporting, and configuration validation.
"""

import logging
from shared.core.unified_logging import get_logger
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = get_logger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ServiceType(Enum):
    """Service type enumeration."""
    BROWSER = "browser"
    PDF = "pdf"
    KNOWLEDGE = "knowledge"
    CODE = "code"
    DATABASE = "database"
    CRAWLER = "crawler"


class BaseAgentService(ABC):
    """
    Base interface for all agent services.
    
    This abstract base class defines the common interface that all agent services
    must implement. It provides standard methods for health checks, status reporting,
    and configuration validation.
    """
    
    def __init__(self, service_type: ServiceType, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base service.
        
        Args:
            service_type: The type of service
            config: Service configuration dictionary
        """
        self.service_type = service_type
        self.config = config or {}
        self.start_time = datetime.now()
        self.status = ServiceStatus.UNKNOWN
        self.error_count = 0
        self.request_count = 0
        
        logger.info(f"Initialized {service_type.value} service")
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health.
        
        Returns:
            Dictionary containing health status and metrics
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get detailed service status.
        
        Returns:
            Dictionary containing service status information
        """
        pass
    
    @abstractmethod
    async def validate_config(self) -> bool:
        """
        Validate service configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get service performance metrics.
        
        Returns:
            Dictionary containing performance metrics
        """
        pass
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get basic service information.
        
        Returns:
            Dictionary containing service information
        """
        return {
            "service_type": self.service_type.value,
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "status": self.status.value,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1)
        }
    
    def increment_request_count(self) -> None:
        """Increment the request counter."""
        self.request_count += 1
    
    def increment_error_count(self) -> None:
        """Increment the error counter."""
        self.error_count += 1
        self.status = ServiceStatus.DEGRADED if self.error_count > 0 else ServiceStatus.HEALTHY
    
    def update_status(self, status: ServiceStatus) -> None:
        """
        Update service status.
        
        Args:
            status: New service status
        """
        self.status = status
        logger.info(f"{self.service_type.value} service status updated to {status.value}")
    
    async def pre_request(self) -> None:
        """
        Pre-request processing.
        
        Called before each service request to perform any necessary setup.
        """
        self.increment_request_count()
    
    async def post_request(self, success: bool = True) -> None:
        """
        Post-request processing.
        
        Args:
            success: Whether the request was successful
        """
        if not success:
            self.increment_error_count()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        logger.info(f"Updated {self.service_type.value} service config: {key} = {value}")
    
    async def reload_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Reload service configuration.
        
        Args:
            new_config: New configuration dictionary
            
        Returns:
            True if configuration was successfully reloaded
        """
        try:
            old_config = self.config.copy()
            self.config = new_config
            
            # Validate new configuration
            if not await self.validate_config():
                self.config = old_config
                logger.error(f"Failed to reload {self.service_type.value} service config: validation failed")
                return False
            
            logger.info(f"Successfully reloaded {self.service_type.value} service config")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reload {self.service_type.value} service config: {e}")
            return False
    
    async def shutdown(self) -> None:
        """
        Shutdown the service.
        
        Called when the service is being shut down to perform cleanup.
        """
        logger.info(f"Shutting down {self.service_type.value} service")
        self.status = ServiceStatus.UNKNOWN


class ServiceHealthChecker:
    """Utility class for checking service health."""
    
    @staticmethod
    def check_service_health(service: BaseAgentService) -> Dict[str, Any]:
        """
        Check the health of a service.
        
        Args:
            service: The service to check
            
        Returns:
            Health check result dictionary
        """
        try:
            health_info = service.get_service_info()
            health_info["healthy"] = service.status == ServiceStatus.HEALTHY
            health_info["last_check"] = datetime.now().isoformat()
            
            return health_info
            
        except Exception as e:
            logger.error(f"Health check failed for {service.service_type.value} service: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "service_type": service.service_type.value,
                "last_check": datetime.now().isoformat()
            }


class ServiceMetricsCollector:
    """Utility class for collecting service metrics."""
    
    @staticmethod
    def collect_service_metrics(service: BaseAgentService) -> Dict[str, Any]:
        """
        Collect metrics from a service.
        
        Args:
            service: The service to collect metrics from
            
        Returns:
            Metrics dictionary
        """
        try:
            metrics = service.get_service_info()
            metrics["timestamp"] = datetime.now().isoformat()
            metrics["memory_usage"] = "N/A"  # TODO: Implement actual memory usage
            metrics["cpu_usage"] = "N/A"      # TODO: Implement actual CPU usage
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics collection failed for {service.service_type.value} service: {e}")
            return {
                "error": str(e),
                "service_type": service.service_type.value,
                "timestamp": datetime.now().isoformat()
            } 