"""
Multi-Tenant Router for API Gateway.

Provides tenant management, usage tracking, and tier management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from ..services import multi_tenant_service
from ..models.requests import (
    CreateTenantRequest,
    UpdateTenantRequest,
    TenantConfigRequest,
    UsageTrackingRequest
)
from ..models.responses import (
    TenantResponse,
    TenantListResponse,
    TenantUsageResponse,
    TenantStatsResponse,
    TenantConfigResponse
)
from ..middleware import get_current_user
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tenants", tags=["Multi-Tenant Management"])

@router.post("/", response_model=TenantResponse)
async def create_tenant(request: CreateTenantRequest):
    """
    Create a new tenant.
    
    Creates a new tenant with the specified configuration and tier.
    """
    try:
        tenant = await multi_tenant_service.create_tenant(
            name=request.name,
            domain=request.domain,
            owner_id=request.owner_id,
            tier=request.tier,
            admin_emails=request.admin_emails
        )
        
        return TenantResponse(
            id=tenant.id,
            name=tenant.name,
            domain=tenant.domain,
            owner_id=tenant.owner_id,
            tier=tenant.tier.value,
            status=tenant.status.value,
            config=TenantConfigResponse(
                features_enabled=tenant.config.features_enabled,
                custom_settings=tenant.config.custom_settings,
                api_rate_limit=tenant.config.api_rate_limit,
                storage_limit_gb=tenant.config.storage_limit_gb
            ),
            usage=TenantUsageResponse(
                api_calls_this_month=tenant.usage.api_calls_this_month,
                storage_used_gb=tenant.usage.storage_used_gb,
                active_users=tenant.usage.active_users,
                last_activity=tenant.usage.last_activity.isoformat() if tenant.usage.last_activity else None
            ),
            created_at=tenant.created_at.isoformat(),
            updated_at=tenant.updated_at.isoformat()
        )
    except Exception as e:
        logger.error(f"Failed to create tenant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tenant"
        )

@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str):
    """
    Get tenant information by ID.
    """
    try:
        tenant = await multi_tenant_service.get_tenant(tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return TenantResponse(
            id=tenant.id,
            name=tenant.name,
            domain=tenant.domain,
            owner_id=tenant.owner_id,
            tier=tenant.tier.value,
            status=tenant.status.value,
            config=TenantConfigResponse(
                features_enabled=tenant.config.features_enabled,
                custom_settings=tenant.config.custom_settings,
                api_rate_limit=tenant.config.api_rate_limit,
                storage_limit_gb=tenant.config.storage_limit_gb
            ),
            usage=TenantUsageResponse(
                api_calls_this_month=tenant.usage.api_calls_this_month,
                storage_used_gb=tenant.usage.storage_used_gb,
                active_users=tenant.usage.active_users,
                last_activity=tenant.usage.last_activity.isoformat() if tenant.usage.last_activity else None
            ),
            created_at=tenant.created_at.isoformat(),
            updated_at=tenant.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tenant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tenant"
        )

@router.get("/domain/{domain}", response_model=TenantResponse)
async def get_tenant_by_domain(domain: str):
    """
    Get tenant information by domain.
    """
    try:
        tenant = await multi_tenant_service.get_tenant_by_domain(domain)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return TenantResponse(
            id=tenant.id,
            name=tenant.name,
            domain=tenant.domain,
            owner_id=tenant.owner_id,
            tier=tenant.tier.value,
            status=tenant.status.value,
            config=TenantConfigResponse(
                features_enabled=tenant.config.features_enabled,
                custom_settings=tenant.config.custom_settings,
                api_rate_limit=tenant.config.api_rate_limit,
                storage_limit_gb=tenant.config.storage_limit_gb
            ),
            usage=TenantUsageResponse(
                api_calls_this_month=tenant.usage.api_calls_this_month,
                storage_used_gb=tenant.usage.storage_used_gb,
                active_users=tenant.usage.active_users,
                last_activity=tenant.usage.last_activity.isoformat() if tenant.usage.last_activity else None
            ),
            created_at=tenant.created_at.isoformat(),
            updated_at=tenant.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tenant by domain: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tenant"
        )

@router.put("/{tenant_id}/status")
async def update_tenant_status(tenant_id: str, status: str):
    """
    Update tenant status (active, suspended, inactive).
    """
    try:
        from ..services.multi_tenant_service import TenantStatus
        
        # Convert string to enum
        try:
            tenant_status = TenantStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}. Valid values: {[s.value for s in TenantStatus]}"
            )
        
        success = await multi_tenant_service.update_tenant_status(tenant_id, tenant_status)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return {"message": f"Tenant status updated to {status}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update tenant status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tenant status"
        )

@router.put("/{tenant_id}/tier")
async def upgrade_tenant_tier(tenant_id: str, tier: str):
    """
    Upgrade tenant tier (free, basic, professional, enterprise).
    """
    try:
        from ..services.multi_tenant_service import TenantTier
        
        # Convert string to enum
        try:
            tenant_tier = TenantTier(tier)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {tier}. Valid values: {[t.value for t in TenantTier]}"
            )
        
        success = await multi_tenant_service.upgrade_tenant_tier(tenant_id, tenant_tier)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return {"message": f"Tenant tier upgraded to {tier}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upgrade tenant tier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade tenant tier"
        )

@router.post("/{tenant_id}/track/api-call")
async def track_api_call(tenant_id: str):
    """
    Track an API call for the tenant.
    """
    try:
        success = await multi_tenant_service.track_api_call(tenant_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return {"message": "API call tracked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to track API call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track API call"
        )

@router.post("/{tenant_id}/track/storage")
async def track_storage_usage(tenant_id: str, request: UsageTrackingRequest):
    """
    Track storage usage for the tenant.
    """
    try:
        success = await multi_tenant_service.track_storage_usage(tenant_id, request.storage_gb)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return {"message": "Storage usage tracked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to track storage usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track storage usage"
        )

@router.post("/{tenant_id}/track/user-activity")
async def track_user_activity(tenant_id: str, user_id: str):
    """
    Track user activity for the tenant.
    """
    try:
        success = await multi_tenant_service.track_user_activity(tenant_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return {"message": "User activity tracked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to track user activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track user activity"
        )

@router.get("/{tenant_id}/usage", response_model=TenantUsageResponse)
async def get_tenant_usage(tenant_id: str):
    """
    Get tenant usage statistics.
    """
    try:
        usage_data = await multi_tenant_service.get_tenant_usage(tenant_id)
        if not usage_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return TenantUsageResponse(**usage_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tenant usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tenant usage"
        )

@router.get("/", response_model=TenantListResponse)
async def get_all_tenants():
    """
    Get all tenants (admin only).
    """
    try:
        tenants = await multi_tenant_service.get_all_tenants()
        
        tenant_responses = []
        for tenant in tenants:
            tenant_responses.append(TenantResponse(
                id=tenant.id,
                name=tenant.name,
                domain=tenant.domain,
                owner_id=tenant.owner_id,
                tier=tenant.tier.value,
                status=tenant.status.value,
                config=TenantConfigResponse(
                    features_enabled=tenant.config.features_enabled,
                    custom_settings=tenant.config.custom_settings,
                    api_rate_limit=tenant.config.api_rate_limit,
                    storage_limit_gb=tenant.config.storage_limit_gb
                ),
                usage=TenantUsageResponse(
                    api_calls_this_month=tenant.usage.api_calls_this_month,
                    storage_used_gb=tenant.usage.storage_used_gb,
                    active_users=tenant.usage.active_users,
                    last_activity=tenant.usage.last_activity.isoformat() if tenant.usage.last_activity else None
                ),
                created_at=tenant.created_at.isoformat(),
                updated_at=tenant.updated_at.isoformat()
            ))
        
        return TenantListResponse(tenants=tenant_responses, total=len(tenant_responses))
    except Exception as e:
        logger.error(f"Failed to get all tenants: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tenants"
        )

@router.get("/active", response_model=TenantListResponse)
async def get_active_tenants():
    """
    Get all active tenants.
    """
    try:
        tenants = await multi_tenant_service.get_active_tenants()
        
        tenant_responses = []
        for tenant in tenants:
            tenant_responses.append(TenantResponse(
                id=tenant.id,
                name=tenant.name,
                domain=tenant.domain,
                owner_id=tenant.owner_id,
                tier=tenant.tier.value,
                status=tenant.status.value,
                config=TenantConfigResponse(
                    features_enabled=tenant.config.features_enabled,
                    custom_settings=tenant.config.custom_settings,
                    api_rate_limit=tenant.config.api_rate_limit,
                    storage_limit_gb=tenant.config.storage_limit_gb
                ),
                usage=TenantUsageResponse(
                    api_calls_this_month=tenant.usage.api_calls_this_month,
                    storage_used_gb=tenant.usage.storage_used_gb,
                    active_users=tenant.usage.active_users,
                    last_activity=tenant.usage.last_activity.isoformat() if tenant.usage.last_activity else None
                ),
                created_at=tenant.created_at.isoformat(),
                updated_at=tenant.updated_at.isoformat()
            ))
        
        return TenantListResponse(tenants=tenant_responses, total=len(tenant_responses))
    except Exception as e:
        logger.error(f"Failed to get active tenants: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get active tenants"
        )

@router.get("/stats", response_model=TenantStatsResponse)
async def get_tenant_stats():
    """
    Get tenant statistics (admin only).
    """
    try:
        stats = await multi_tenant_service.get_tenant_stats()
        return TenantStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Failed to get tenant stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tenant statistics"
        )

@router.post("/{tenant_id}/reset-usage")
async def reset_monthly_usage(tenant_id: str):
    """
    Reset monthly usage for the tenant.
    """
    try:
        success = await multi_tenant_service.reset_monthly_usage(tenant_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return {"message": "Monthly usage reset successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset monthly usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset monthly usage"
        )

@router.get("/{tenant_id}/feature/{feature}")
async def is_feature_enabled(tenant_id: str, feature: str):
    """
    Check if a feature is enabled for the tenant.
    """
    try:
        enabled = await multi_tenant_service.is_feature_enabled(tenant_id, feature)
        return {"feature": feature, "enabled": enabled}
    except Exception as e:
        logger.error(f"Failed to check feature: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check feature"
        )

@router.get("/{tenant_id}/config", response_model=TenantConfigResponse)
async def get_tenant_config(tenant_id: str):
    """
    Get tenant configuration.
    """
    try:
        config = await multi_tenant_service.get_tenant_config(tenant_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return TenantConfigResponse(
            features_enabled=config.features_enabled,
            custom_settings=config.custom_settings,
            api_rate_limit=config.api_rate_limit,
            storage_limit_gb=config.storage_limit_gb
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tenant config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tenant configuration"
        )

@router.put("/{tenant_id}/config")
async def update_tenant_config(tenant_id: str, request: TenantConfigRequest):
    """
    Update tenant configuration.
    """
    try:
        from ..services.multi_tenant_service import TenantConfig
        
        config = TenantConfig(
            features_enabled=request.features_enabled,
            custom_settings=request.custom_settings,
            api_rate_limit=request.api_rate_limit,
            storage_limit_gb=request.storage_limit_gb
        )
        
        success = await multi_tenant_service.update_tenant_config(tenant_id, config)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return {"message": "Tenant configuration updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update tenant config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tenant configuration"
        )
