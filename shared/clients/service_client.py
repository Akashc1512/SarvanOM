"""
Service Client for Inter-Service Communication

This module provides a client for communicating between microservices
following MAANG/OpenAI/Perplexity standards.
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from pydantic import BaseModel

from shared.models.crud_models import CRUDResponse, PaginationParams, FilterParams
from shared.contracts.service_contracts import ServiceType, ServiceStatus, ServiceHealth

logger = logging.getLogger(__name__)


class ServiceClientConfig(BaseModel):
    """Configuration for service client"""
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    service_name: str
    service_type: ServiceType


class ServiceClient:
    """Client for inter-service communication"""
    
    def __init__(self, config: ServiceClientConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={
                "User-Agent": f"SarvanOM-ServiceClient/{config.service_name}",
                "Content-Type": "application/json"
            }
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def _make_request(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retries: int = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        if retries is None:
            retries = self.config.max_retries
        
        for attempt in range(retries + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if attempt == retries:
                    logger.error(f"HTTP error after {retries} retries: {e}")
                    raise
                logger.warning(f"HTTP error (attempt {attempt + 1}/{retries + 1}): {e}")
            except httpx.RequestError as e:
                if attempt == retries:
                    logger.error(f"Request error after {retries} retries: {e}")
                    raise
                logger.warning(f"Request error (attempt {attempt + 1}/{retries + 1}): {e}")
            
            if attempt < retries:
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
        
        raise Exception(f"Failed to make request after {retries} retries")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return await self._make_request("GET", "/health")
    
    async def detailed_health_check(self) -> Dict[str, Any]:
        """Get detailed health information"""
        return await self._make_request("GET", "/health/detailed")


class CRUDServiceClient(ServiceClient):
    """Client for CRUD service communication"""
    
    async def create_resource(self, resource_type: str, data: Dict[str, Any]) -> CRUDResponse:
        """Create a new resource"""
        response_data = await self._make_request("POST", f"/{resource_type}", data=data)
        return CRUDResponse(**response_data)
    
    async def get_resource(self, resource_type: str, resource_id: str) -> CRUDResponse:
        """Get a resource by ID"""
        response_data = await self._make_request("GET", f"/{resource_type}/{resource_id}")
        return CRUDResponse(**response_data)
    
    async def update_resource(self, resource_type: str, resource_id: str, data: Dict[str, Any]) -> CRUDResponse:
        """Update a resource by ID"""
        response_data = await self._make_request("PUT", f"/{resource_type}/{resource_id}", data=data)
        return CRUDResponse(**response_data)
    
    async def delete_resource(self, resource_type: str, resource_id: str) -> CRUDResponse:
        """Delete a resource by ID"""
        response_data = await self._make_request("DELETE", f"/{resource_type}/{resource_id}")
        return CRUDResponse(**response_data)
    
    async def list_resources(
        self,
        resource_type: str,
        pagination: Optional[PaginationParams] = None,
        filters: Optional[FilterParams] = None
    ) -> CRUDResponse:
        """List resources with pagination and filtering"""
        params = {}
        if pagination:
            params.update(pagination.dict())
        if filters:
            params.update(filters.dict())
        
        response_data = await self._make_request("GET", f"/{resource_type}", params=params)
        return CRUDResponse(**response_data)


class ServiceDiscoveryClient(ServiceClient):
    """Client for service discovery"""
    
    async def register_service(self, service_name: str, service_type: ServiceType, endpoint: str) -> bool:
        """Register a service"""
        data = {
            "service_name": service_name,
            "service_type": service_type.value,
            "endpoint": endpoint
        }
        response_data = await self._make_request("POST", "/register", data=data)
        return response_data.get("success", False)
    
    async def unregister_service(self, service_name: str) -> bool:
        """Unregister a service"""
        response_data = await self._make_request("DELETE", f"/services/{service_name}")
        return response_data.get("success", False)
    
    async def get_service_endpoint(self, service_name: str) -> Optional[str]:
        """Get service endpoint"""
        try:
            response_data = await self._make_request("GET", f"/services/{service_name}")
            return response_data.get("endpoint")
        except Exception:
            return None
    
    async def get_services_by_type(self, service_type: ServiceType) -> List[str]:
        """Get all services of a specific type"""
        response_data = await self._make_request("GET", f"/services/type/{service_type.value}")
        return response_data.get("services", [])
    
    async def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Get service health information"""
        try:
            response_data = await self._make_request("GET", f"/services/{service_name}/health")
            return ServiceHealth(**response_data)
        except Exception:
            return None


# Service client factory
class ServiceClientFactory:
    """Factory for creating service clients"""
    
    @staticmethod
    def create_crud_client(base_url: str = "http://localhost:8001") -> CRUDServiceClient:
        """Create a CRUD service client"""
        config = ServiceClientConfig(
            base_url=base_url,
            service_name="gateway",
            service_type=ServiceType.GATEWAY
        )
        return CRUDServiceClient(config)
    
    @staticmethod
    def create_service_discovery_client(base_url: str = "http://localhost:8002") -> ServiceDiscoveryClient:
        """Create a service discovery client"""
        config = ServiceClientConfig(
            base_url=base_url,
            service_name="gateway",
            service_type=ServiceType.GATEWAY
        )
        return ServiceDiscoveryClient(config)
