"""
Multi-Tenant Service for API Gateway

This module provides multi-tenant functionality with:
- Tenant isolation and resource management
- Tenant-specific configurations
- Data segregation
- Usage tracking and billing
- Tenant administration
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


class TenantStatus(Enum):
    """Tenant status enumeration."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"
    PENDING = "pending"


class TenantTier(Enum):
    """Tenant subscription tiers."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class TenantConfig:
    """Tenant configuration data."""
    max_users: int = 10
    max_storage_gb: int = 1
    max_api_calls_per_month: int = 1000
    features_enabled: List[str] = field(default_factory=lambda: ["basic"])
    custom_domain: Optional[str] = None
    branding: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantUsage:
    """Tenant usage statistics."""
    api_calls_this_month: int = 0
    storage_used_gb: float = 0.0
    active_users: int = 0
    last_activity: Optional[datetime] = None
    monthly_cost: float = 0.0


@dataclass
class Tenant:
    """Tenant data model."""
    tenant_id: str
    name: str
    domain: str
    status: TenantStatus
    tier: TenantTier
    config: TenantConfig
    usage: TenantUsage
    created_at: datetime
    owner_id: str
    admin_emails: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultiTenantService:
    """Service for handling multi-tenant operations."""
    
    def __init__(self):
        self.tenants = {}  # In-memory tenant store (should be database)
        self.tenant_resources = {}  # Resource tracking per tenant
        self.tenant_limits = {
            TenantTier.FREE: {
                "max_users": 5,
                "max_storage_gb": 1,
                "max_api_calls_per_month": 1000,
                "features": ["basic_search", "basic_analytics"]
            },
            TenantTier.BASIC: {
                "max_users": 25,
                "max_storage_gb": 10,
                "max_api_calls_per_month": 10000,
                "features": ["basic_search", "basic_analytics", "advanced_search"]
            },
            TenantTier.PROFESSIONAL: {
                "max_users": 100,
                "max_storage_gb": 100,
                "max_api_calls_per_month": 100000,
                "features": ["basic_search", "basic_analytics", "advanced_search", "custom_models"]
            },
            TenantTier.ENTERPRISE: {
                "max_users": -1,  # Unlimited
                "max_storage_gb": -1,  # Unlimited
                "max_api_calls_per_month": -1,  # Unlimited
                "features": ["all"]
            }
        }
        self._initialize_default_tenants()
    
    def _initialize_default_tenants(self):
        """Initialize default tenants for development."""
        default_tenant = Tenant(
            tenant_id="default",
            name="Default Tenant",
            domain="default.sarvanom.com",
            status=TenantStatus.ACTIVE,
            tier=TenantTier.ENTERPRISE,
            config=TenantConfig(
                max_users=1000,
                max_storage_gb=1000,
                max_api_calls_per_month=1000000,
                features_enabled=["all"]
            ),
            usage=TenantUsage(),
            created_at=datetime.now(),
            owner_id="admin-001",
            admin_emails=["admin@sarvanom.com"]
        )
        
        self.tenants[default_tenant.tenant_id] = default_tenant
        self.tenant_resources[default_tenant.tenant_id] = {
            "api_calls": 0,
            "storage_gb": 0.0,
            "active_users": 0
        }
    
    async def create_tenant(
        self,
        name: str,
        domain: str,
        owner_id: str,
        tier: TenantTier = TenantTier.FREE,
        admin_emails: Optional[List[str]] = None
    ) -> Tenant:
        """Create a new tenant."""
        tenant_id = str(uuid.uuid4())
        
        # Get limits for the tier
        limits = self.tenant_limits[tier]
        
        config = TenantConfig(
            max_users=limits["max_users"],
            max_storage_gb=limits["max_storage_gb"],
            max_api_calls_per_month=limits["max_api_calls_per_month"],
            features_enabled=limits["features"]
        )
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            domain=domain,
            status=TenantStatus.ACTIVE,
            tier=tier,
            config=config,
            usage=TenantUsage(),
            created_at=datetime.now(),
            owner_id=owner_id,
            admin_emails=admin_emails or []
        )
        
        self.tenants[tenant_id] = tenant
        self.tenant_resources[tenant_id] = {
            "api_calls": 0,
            "storage_gb": 0.0,
            "active_users": 0
        }
        
        logger.info(f"Created new tenant: {tenant_id} ({name})")
        return tenant
    
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenants.get(tenant_id)
    
    async def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain."""
        for tenant in self.tenants.values():
            if tenant.domain == domain:
                return tenant
        return None
    
    async def update_tenant_status(self, tenant_id: str, status: TenantStatus) -> bool:
        """Update tenant status."""
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        tenant.status = status
        logger.info(f"Updated tenant {tenant_id} status to {status.value}")
        return True
    
    async def upgrade_tenant_tier(self, tenant_id: str, new_tier: TenantTier) -> bool:
        """Upgrade tenant to a higher tier."""
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        # Check if upgrade is valid
        current_tier_order = list(TenantTier)
        current_index = current_tier_order.index(tenant.tier)
        new_index = current_tier_order.index(new_tier)
        
        if new_index <= current_index:
            logger.warning(f"Invalid tier upgrade: {tenant.tier} -> {new_tier}")
            return False
        
        # Update tenant configuration
        limits = self.tenant_limits[new_tier]
        tenant.tier = new_tier
        tenant.config.max_users = limits["max_users"]
        tenant.config.max_storage_gb = limits["max_storage_gb"]
        tenant.config.max_api_calls_per_month = limits["max_api_calls_per_month"]
        tenant.config.features_enabled = limits["features"]
        
        logger.info(f"Upgraded tenant {tenant_id} to {new_tier.value}")
        return True
    
    async def track_api_call(self, tenant_id: str) -> bool:
        """Track an API call for a tenant."""
        tenant = await self.get_tenant(tenant_id)
        if not tenant or tenant.status != TenantStatus.ACTIVE:
            return False
        
        # Check limits
        if (tenant.config.max_api_calls_per_month != -1 and 
            tenant.usage.api_calls_this_month >= tenant.config.max_api_calls_per_month):
            logger.warning(f"Tenant {tenant_id} has exceeded API call limit")
            return False
        
        # Update usage
        tenant.usage.api_calls_this_month += 1
        tenant.usage.last_activity = datetime.now()
        
        # Update resource tracking
        if tenant_id in self.tenant_resources:
            self.tenant_resources[tenant_id]["api_calls"] += 1
        
        return True
    
    async def track_storage_usage(self, tenant_id: str, storage_gb: float) -> bool:
        """Track storage usage for a tenant."""
        tenant = await self.get_tenant(tenant_id)
        if not tenant or tenant.status != TenantStatus.ACTIVE:
            return False
        
        # Check limits
        if (tenant.config.max_storage_gb != -1 and 
            tenant.usage.storage_used_gb + storage_gb > tenant.config.max_storage_gb):
            logger.warning(f"Tenant {tenant_id} would exceed storage limit")
            return False
        
        # Update usage
        tenant.usage.storage_used_gb += storage_gb
        tenant.usage.last_activity = datetime.now()
        
        # Update resource tracking
        if tenant_id in self.tenant_resources:
            self.tenant_resources[tenant_id]["storage_gb"] += storage_gb
        
        return True
    
    async def track_user_activity(self, tenant_id: str, user_id: str) -> bool:
        """Track user activity for a tenant."""
        tenant = await self.get_tenant(tenant_id)
        if not tenant or tenant.status != TenantStatus.ACTIVE:
            return False
        
        # Check user limits
        if (tenant.config.max_users != -1 and 
            tenant.usage.active_users >= tenant.config.max_users):
            logger.warning(f"Tenant {tenant_id} has reached user limit")
            return False
        
        # Update usage
        tenant.usage.active_users = max(tenant.usage.active_users, 1)
        tenant.usage.last_activity = datetime.now()
        
        # Update resource tracking
        if tenant_id in self.tenant_resources:
            self.tenant_resources[tenant_id]["active_users"] = max(
                self.tenant_resources[tenant_id]["active_users"], 1
            )
        
        return True
    
    async def get_tenant_usage(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed usage statistics for a tenant."""
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            return None
        
        resources = self.tenant_resources.get(tenant_id, {})
        
        return {
            "tenant_id": tenant_id,
            "tenant_name": tenant.name,
            "tier": tenant.tier.value,
            "status": tenant.status.value,
            "usage": {
                "api_calls_this_month": tenant.usage.api_calls_this_month,
                "storage_used_gb": tenant.usage.storage_used_gb,
                "active_users": tenant.usage.active_users,
                "last_activity": tenant.usage.last_activity.isoformat() if tenant.usage.last_activity else None
            },
            "limits": {
                "max_api_calls_per_month": tenant.config.max_api_calls_per_month,
                "max_storage_gb": tenant.config.max_storage_gb,
                "max_users": tenant.config.max_users
            },
            "features_enabled": tenant.config.features_enabled,
            "created_at": tenant.created_at.isoformat()
        }
    
    async def get_all_tenants(self) -> List[Tenant]:
        """Get all tenants."""
        return list(self.tenants.values())
    
    async def get_active_tenants(self) -> List[Tenant]:
        """Get all active tenants."""
        return [t for t in self.tenants.values() if t.status == TenantStatus.ACTIVE]
    
    async def get_tenant_stats(self) -> Dict[str, Any]:
        """Get overall tenant statistics."""
        total_tenants = len(self.tenants)
        active_tenants = len([t for t in self.tenants.values() if t.status == TenantStatus.ACTIVE])
        
        tier_counts = {}
        for tenant in self.tenants.values():
            tier = tenant.tier.value
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        total_api_calls = sum(t.usage.api_calls_this_month for t in self.tenants.values())
        total_storage = sum(t.usage.storage_used_gb for t in self.tenants.values())
        total_users = sum(t.usage.active_users for t in self.tenants.values())
        
        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "tier_distribution": tier_counts,
            "total_api_calls": total_api_calls,
            "total_storage_gb": total_storage,
            "total_active_users": total_users,
            "last_updated": datetime.now().isoformat()
        }
    
    async def reset_monthly_usage(self, tenant_id: str) -> bool:
        """Reset monthly usage for a tenant."""
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        tenant.usage.api_calls_this_month = 0
        tenant.usage.last_activity = datetime.now()
        
        if tenant_id in self.tenant_resources:
            self.tenant_resources[tenant_id]["api_calls"] = 0
        
        logger.info(f"Reset monthly usage for tenant {tenant_id}")
        return True
    
    async def is_feature_enabled(self, tenant_id: str, feature: str) -> bool:
        """Check if a feature is enabled for a tenant."""
        tenant = await self.get_tenant(tenant_id)
        if not tenant or tenant.status != TenantStatus.ACTIVE:
            return False
        
        return feature in tenant.config.features_enabled or "all" in tenant.config.features_enabled
    
    async def get_tenant_config(self, tenant_id: str) -> Optional[TenantConfig]:
        """Get tenant configuration."""
        tenant = await self.get_tenant(tenant_id)
        return tenant.config if tenant else None
    
    async def update_tenant_config(self, tenant_id: str, config: TenantConfig) -> bool:
        """Update tenant configuration."""
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        tenant.config = config
        logger.info(f"Updated configuration for tenant {tenant_id}")
        return True


# Create global multi-tenant service instance
multi_tenant_service = MultiTenantService()
