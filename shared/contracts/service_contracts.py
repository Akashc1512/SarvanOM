"""
Service Contracts for Microservices Architecture

This module defines contracts and interfaces for inter-service communication
following MAANG/OpenAI/Perplexity standards.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from shared.models.crud_models import (
    CacheEntry, UserProfile, ModelConfiguration, Dataset, SystemSetting,
    CRUDResponse, PaginationParams, FilterParams
)


class ServiceType(str, Enum):
    """Service types in the microservices architecture"""
    GATEWAY = "gateway"
    AUTH = "auth"
    SEARCH = "search"
    SYNTHESIS = "synthesis"
    FACT_CHECK = "fact_check"
    RETRIEVAL = "retrieval"
    ANALYTICS = "analytics"
    MONITORING = "monitoring"


class ServiceStatus(str, Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"


class ServiceHealth(BaseModel):
    """Service health information"""
    service_name: str = Field(..., description="Service name")
    service_type: ServiceType = Field(..., description="Service type")
    status: ServiceStatus = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    uptime: float = Field(..., description="Service uptime in seconds")
    last_check: datetime = Field(default_factory=datetime.utcnow, description="Last health check")
    dependencies: List[str] = Field(default=[], description="Service dependencies")
    metrics: Dict[str, Any] = Field(default={}, description="Service metrics")


class ServiceRequest(BaseModel):
    """Base service request model"""
    request_id: str = Field(..., description="Unique request identifier")
    service_name: str = Field(..., description="Requesting service name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for tracing")


class ServiceResponse(BaseModel):
    """Base service response model"""
    request_id: str = Field(..., description="Request identifier")
    service_name: str = Field(..., description="Responding service name")
    status: str = Field(..., description="Response status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if any")


# CRUD Service Contracts
class CRUDServiceContract(ABC):
    """Abstract base class for CRUD service contracts"""
    
    @abstractmethod
    async def create(self, resource_type: str, data: Dict[str, Any]) -> CRUDResponse:
        """Create a new resource"""
        pass
    
    @abstractmethod
    async def read(self, resource_type: str, resource_id: str) -> CRUDResponse:
        """Read a resource by ID"""
        pass
    
    @abstractmethod
    async def update(self, resource_type: str, resource_id: str, data: Dict[str, Any]) -> CRUDResponse:
        """Update a resource by ID"""
        pass
    
    @abstractmethod
    async def delete(self, resource_type: str, resource_id: str) -> CRUDResponse:
        """Delete a resource by ID"""
        pass
    
    @abstractmethod
    async def list(self, resource_type: str, pagination: PaginationParams, filters: Optional[FilterParams] = None) -> CRUDResponse:
        """List resources with pagination and filtering"""
        pass


# Cache Service Contract
class CacheServiceContract(ABC):
    """Abstract base class for cache service contracts"""
    
    @abstractmethod
    async def get(self, key: str, service: str) -> Optional[Any]:
        """Get a value from cache"""
        pass
    
    @abstractmethod
    async def set(self, entry: CacheEntry) -> bool:
        """Set a value in cache"""
        pass
    
    @abstractmethod
    async def update(self, key: str, entry: CacheEntry) -> bool:
        """Update a value in cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str, service: str) -> bool:
        """Delete a value from cache"""
        pass
    
    @abstractmethod
    async def clear(self, service: str) -> bool:
        """Clear all cache entries for a service"""
        pass
    
    @abstractmethod
    async def get_stats(self, service: str) -> Dict[str, Any]:
        """Get cache statistics for a service"""
        pass


# User Service Contract
class UserServiceContract(ABC):
    """Abstract base class for user service contracts"""
    
    @abstractmethod
    async def create_user(self, user: UserProfile) -> CRUDResponse:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_user(self, user_id: str) -> CRUDResponse:
        """Get a user by ID"""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, user: UserProfile) -> CRUDResponse:
        """Update a user"""
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: str) -> CRUDResponse:
        """Delete a user"""
        pass
    
    @abstractmethod
    async def list_users(self, pagination: PaginationParams, filters: Optional[FilterParams] = None) -> CRUDResponse:
        """List users with pagination and filtering"""
        pass


# Model Service Contract
class ModelServiceContract(ABC):
    """Abstract base class for model service contracts"""
    
    @abstractmethod
    async def create_model(self, model: ModelConfiguration) -> CRUDResponse:
        """Create a new model configuration"""
        pass
    
    @abstractmethod
    async def get_model(self, model_name: str) -> CRUDResponse:
        """Get a model configuration by name"""
        pass
    
    @abstractmethod
    async def update_model(self, model_name: str, model: ModelConfiguration) -> CRUDResponse:
        """Update a model configuration"""
        pass
    
    @abstractmethod
    async def delete_model(self, model_name: str) -> CRUDResponse:
        """Delete a model configuration"""
        pass
    
    @abstractmethod
    async def list_models(self, pagination: PaginationParams, filters: Optional[FilterParams] = None) -> CRUDResponse:
        """List model configurations with pagination and filtering"""
        pass


# Dataset Service Contract
class DatasetServiceContract(ABC):
    """Abstract base class for dataset service contracts"""
    
    @abstractmethod
    async def create_dataset(self, dataset: Dataset) -> CRUDResponse:
        """Create a new dataset"""
        pass
    
    @abstractmethod
    async def get_dataset(self, dataset_id: str) -> CRUDResponse:
        """Get a dataset by ID"""
        pass
    
    @abstractmethod
    async def update_dataset(self, dataset_id: str, dataset: Dataset) -> CRUDResponse:
        """Update a dataset"""
        pass
    
    @abstractmethod
    async def delete_dataset(self, dataset_id: str) -> CRUDResponse:
        """Delete a dataset"""
        pass
    
    @abstractmethod
    async def list_datasets(self, pagination: PaginationParams, filters: Optional[FilterParams] = None) -> CRUDResponse:
        """List datasets with pagination and filtering"""
        pass


# Settings Service Contract
class SettingsServiceContract(ABC):
    """Abstract base class for settings service contracts"""
    
    @abstractmethod
    async def create_setting(self, setting: SystemSetting) -> CRUDResponse:
        """Create a new system setting"""
        pass
    
    @abstractmethod
    async def get_setting(self, setting_key: str) -> CRUDResponse:
        """Get a system setting by key"""
        pass
    
    @abstractmethod
    async def update_setting(self, setting_key: str, setting: SystemSetting) -> CRUDResponse:
        """Update a system setting"""
        pass
    
    @abstractmethod
    async def delete_setting(self, setting_key: str) -> CRUDResponse:
        """Delete a system setting"""
        pass
    
    @abstractmethod
    async def list_settings(self, pagination: PaginationParams, filters: Optional[FilterParams] = None) -> CRUDResponse:
        """List system settings with pagination and filtering"""
        pass


# Service Discovery Contract
class ServiceDiscoveryContract(ABC):
    """Abstract base class for service discovery contracts"""
    
    @abstractmethod
    async def register_service(self, service_name: str, service_type: ServiceType, endpoint: str) -> bool:
        """Register a service with the discovery service"""
        pass
    
    @abstractmethod
    async def unregister_service(self, service_name: str) -> bool:
        """Unregister a service from the discovery service"""
        pass
    
    @abstractmethod
    async def get_service_endpoint(self, service_name: str) -> Optional[str]:
        """Get the endpoint for a service"""
        pass
    
    @abstractmethod
    async def get_services_by_type(self, service_type: ServiceType) -> List[str]:
        """Get all services of a specific type"""
        pass
    
    @abstractmethod
    async def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Get health information for a service"""
        pass


# Event Bus Contract
class EventBusContract(ABC):
    """Abstract base class for event bus contracts"""
    
    @abstractmethod
    async def publish_event(self, event_type: str, event_data: Dict[str, Any], service_name: str) -> bool:
        """Publish an event to the event bus"""
        pass
    
    @abstractmethod
    async def subscribe_to_events(self, event_types: List[str], service_name: str, callback) -> bool:
        """Subscribe to events of specific types"""
        pass
    
    @abstractmethod
    async def unsubscribe_from_events(self, event_types: List[str], service_name: str) -> bool:
        """Unsubscribe from events of specific types"""
        pass
