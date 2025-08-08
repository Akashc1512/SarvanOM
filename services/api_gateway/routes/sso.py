"""
SSO (Single Sign-On) Router for API Gateway.

Provides authentication, user management, and session handling endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from ..services import sso_service
from ..models.requests import (
    LoginRequest,
    RegisterRequest,
    OAuthLoginRequest,
    PasswordChangeRequest,
    UserUpdateRequest
)
from ..models.responses import (
    AuthResponse,
    UserResponse,
    UserStatsResponse,
    OAuthUrlResponse
)
from ..middleware import get_current_user, get_current_user_optional
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["SSO Authentication"])

# Security
security = HTTPBearer(auto_error=False)

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with username/email and password.
    
    Returns JWT access token and user information.
    """
    try:
        user = await sso_service.authenticate_user(request.username, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create session
        auth_token = await sso_service.create_session(user)
        
        return AuthResponse(
            access_token=auth_token.token,
            token_type="bearer",
            expires_in=auth_token.expires_in,
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role.value,
                is_active=user.is_active,
                created_at=user.created_at.isoformat(),
                last_login=user.last_login.isoformat() if user.last_login else None
            )
        )
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    Register a new user account.
    
    Creates user account and returns authentication token.
    """
    try:
        # Check if user already exists
        existing_user = await sso_service.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user (this would typically be in the service)
        # For now, we'll simulate user creation
        from ..services.sso_service import User, UserRole
        from datetime import datetime
        
        new_user = User(
            id=f"user_{datetime.now().timestamp()}",
            username=request.username,
            email=request.email,
            role=UserRole.USER,
            is_active=True,
            created_at=datetime.now(),
            last_login=datetime.now()
        )
        
        # Add to service (in real implementation, this would be in the service)
        sso_service.users[new_user.id] = new_user
        
        # Create session
        auth_token = await sso_service.create_session(new_user)
        
        return AuthResponse(
            access_token=auth_token.token,
            token_type="bearer",
            expires_in=auth_token.expires_in,
            user=UserResponse(
                id=new_user.id,
                username=new_user.username,
                email=new_user.email,
                role=new_user.role.value,
                is_active=new_user.is_active,
                created_at=new_user.created_at.isoformat(),
                last_login=new_user.last_login.isoformat()
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/oauth/{provider}/login", response_model=AuthResponse)
async def oauth_login(provider: str, request: OAuthLoginRequest):
    """
    Authenticate user via OAuth provider.
    
    Supports Google, GitHub, Microsoft, and other OAuth providers.
    """
    try:
        user = await sso_service.authenticate_oauth(provider, request.code)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OAuth authentication failed"
            )
        
        # Create session
        auth_token = await sso_service.create_session(user)
        
        return AuthResponse(
            access_token=auth_token.token,
            token_type="bearer",
            expires_in=auth_token.expires_in,
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role.value,
                is_active=user.is_active,
                created_at=user.created_at.isoformat(),
                last_login=user.last_login.isoformat() if user.last_login else None
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed"
        )

@router.get("/oauth/{provider}/url", response_model=OAuthUrlResponse)
async def get_oauth_url(provider: str, redirect_uri: str):
    """
    Get OAuth authorization URL for the specified provider.
    """
    try:
        oauth_url = await sso_service.get_oauth_url(provider, redirect_uri)
        if not oauth_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth provider '{provider}' not supported"
            )
        
        return OAuthUrlResponse(
            provider=provider,
            authorization_url=oauth_url,
            redirect_uri=redirect_uri
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get OAuth URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get OAuth URL"
        )

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user = Depends(get_current_user)):
    """
    Get current user profile information.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: UserUpdateRequest,
    current_user = Depends(get_current_user)
):
    """
    Update current user profile information.
    """
    try:
        # Update user fields (in real implementation, this would be in the service)
        if request.username:
            current_user.username = request.username
        if request.email:
            current_user.email = request.email
        
        return UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            role=current_user.role.value,
            is_active=current_user.is_active,
            created_at=current_user.created_at.isoformat(),
            last_login=current_user.last_login.isoformat() if current_user.last_login else None
        )
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user = Depends(get_current_user)
):
    """
    Change user password.
    """
    try:
        # Verify current password
        if not sso_service.verify_password(request.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password (in real implementation, this would be in the service)
        current_user.hashed_password = sso_service.get_password_hash(request.new_password)
        
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """
    Logout current user and invalidate session.
    """
    try:
        await sso_service.revoke_session(current_user.id)
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/users/stats", response_model=UserStatsResponse)
async def get_user_stats(current_user = Depends(get_current_user)):
    """
    Get user statistics (admin only).
    """
    try:
        # Check if user has admin role
        if not sso_service.has_role(current_user, sso_service.UserRole.ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        stats = await sso_service.get_user_stats()
        return UserStatsResponse(**stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )

@router.get("/verify")
async def verify_token(current_user = Depends(get_current_user_optional)):
    """
    Verify JWT token and return user information.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )
