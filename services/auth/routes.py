"""
Authentication Service Routes

This module provides authentication endpoints for user registration, login,
token refresh, logout, and user management.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer
from typing import Dict, Any, Optional
import structlog

from shared.core.secure_auth import (
    AuthManager, AuthConfig, UserRole, get_current_user, require_role
)
from shared.core.api.api_models import LoginRequest, RegisterRequest
from shared.core.config.central_config import initialize_config
from shared.core.database import get_db_manager
from backend.repositories.database.user_repository import UserRepository
from shared.core.auth.password_hasher import PasswordHasher

logger = structlog.get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Initialize dependencies
config = initialize_config()
security = HTTPBearer()

# Initialize auth manager with configuration
auth_config = AuthConfig(
    jwt_secret_key=config.jwt_secret_key.get_secret_value(),
    jwt_algorithm=config.jwt_algorithm,
    jwt_access_token_expire_minutes=config.jwt_access_token_expire_minutes,
    jwt_refresh_token_expire_days=config.jwt_refresh_token_expire_days,
    min_password_length=12,
    require_uppercase=True,
    require_lowercase=True,
    require_numbers=True,
    require_special_chars=True,
    max_login_attempts=5,
    lockout_duration_minutes=15,
    session_timeout_minutes=30,
    mfa_required=False,
    max_auth_requests_per_minute=10,
    max_auth_requests_per_hour=100,
    log_auth_events=True,
    log_failed_attempts=True,
)

auth_manager = AuthManager(auth_config)
user_repository = UserRepository()
password_hasher = PasswordHasher()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest) -> Dict[str, Any]:
    """
    Register a new user.
    
    Args:
        request: Registration request containing username, email, password, etc.
        
    Returns:
        User registration response with user details
    """
    try:
        # Check if username already exists
        existing_user = await user_repository.get_user_by_username(request.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        
        # Check if email already exists
        existing_email = await user_repository.get_user_by_email(request.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        
        # Validate password strength
        is_valid, message = password_hasher._validate_password_strength(request.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {message}"
            )
        
        # Create user
        user = await user_repository.create_user(
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=request.role
        )
        
        logger.info("user_registered", user_id=user.id, username=user.username)
        
        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("registration_failed", error=str(e), username=request.username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login")
async def login_user(request: LoginRequest, client_request: Request) -> Dict[str, Any]:
    """
    Authenticate user and return access tokens.
    
    Args:
        request: Login request containing username and password
        client_request: FastAPI request object for IP address
        
    Returns:
        Authentication response with access and refresh tokens
    """
    try:
        # Get client IP address
        ip_address = client_request.client.host if client_request.client else "unknown"
        
        # Authenticate user using the auth manager
        auth_result = await auth_manager.authenticate_user(
            username=request.username,
            password=request.password,
            ip_address=ip_address
        )
        
        logger.info("user_logged_in", username=request.username, ip_address=ip_address)
        
        return auth_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("login_failed", error=str(e), username=request.username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    client_request: Request
) -> Dict[str, Any]:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: The refresh token
        client_request: FastAPI request object for IP address
        
    Returns:
        New access token
    """
    try:
        # Get client IP address
        ip_address = client_request.client.host if client_request.client else "unknown"
        
        # Refresh token using auth manager
        auth_result = await auth_manager.refresh_token(refresh_token, ip_address)
        
        logger.info("token_refreshed", ip_address=ip_address)
        
        return auth_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("token_refresh_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
    client_request: Request = None
) -> Dict[str, str]:
    """
    Logout user and invalidate tokens.
    
    Args:
        current_user: Current authenticated user (from token)
        client_request: FastAPI request object
        
    Returns:
        Logout confirmation message
    """
    try:
        # Get token from request
        auth_header = client_request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            await auth_manager.logout(token, current_user["user_id"])
        
        logger.info("user_logged_out", user_id=current_user["user_id"])
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error("logout_failed", error=str(e), user_id=current_user["user_id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me")
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user (from token)
        
    Returns:
        Current user information
    """
    try:
        # Get full user details from database
        user = await user_repository.get_by_id(current_user["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_user_info_failed", error=str(e), user_id=current_user["user_id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.put("/me")
async def update_user_info(
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update current user information.
    
    Args:
        full_name: New full name (optional)
        email: New email (optional)
        current_user: Current authenticated user (from token)
        
    Returns:
        Updated user information
    """
    try:
        # Get current user
        user = await user_repository.get_by_id(current_user["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields if provided
        update_data = {}
        if full_name is not None:
            update_data["full_name"] = full_name
        if email is not None:
            # Check if email is already taken by another user
            existing_user = await user_repository.get_user_by_email(email)
            if existing_user and existing_user.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists"
                )
            update_data["email"] = email
        
        if update_data:
            updated_user = await user_repository.update(user.id, update_data)
            logger.info("user_updated", user_id=user.id, updated_fields=list(update_data.keys()))
            
            return {
                "message": "User updated successfully",
                "user": {
                    "id": updated_user.id,
                    "username": updated_user.username,
                    "email": updated_user.email,
                    "full_name": updated_user.full_name,
                    "role": updated_user.role,
                    "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
                }
            }
        else:
            return {"message": "No updates provided"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_user_failed", error=str(e), user_id=current_user["user_id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Change user password.
    
    Args:
        current_password: Current password
        new_password: New password
        current_user: Current authenticated user (from token)
        
    Returns:
        Password change confirmation
    """
    try:
        # Get current user
        user = await user_repository.get_by_id(current_user["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not await user_repository.authenticate_user(user.username, current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        is_valid, message = password_hasher._validate_password_strength(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {message}"
            )
        
        # Update password
        await user_repository.change_password(user.id, new_password)
        
        logger.info("password_changed", user_id=user.id)
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("change_password_failed", error=str(e), user_id=current_user["user_id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


# Admin endpoints (require admin role)
@router.get("/users", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def list_users(
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all users (admin only).
    
    Args:
        page: Page number
        page_size: Number of users per page
        search: Search term for username or email
        
    Returns:
        Paginated list of users
    """
    try:
        users, total = await user_repository.list_users(
            page=page,
            page_size=page_size,
            search=search
        )
        
        return {
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "is_active": user.is_active
                }
                for user in users
            ],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        logger.error("list_users_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "auth"}
