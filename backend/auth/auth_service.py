"""
Auth Service

This service provides authentication and authorization functionality by wrapping the existing
auth modules and providing a clean interface for the API gateway.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Import the existing auth modules
from .auth import AuthManager
from .user_management import UserManagementService

logger = logging.getLogger(__name__)


class AuthService:
    """
    Auth Service that provides authentication and authorization functionality.
    Wraps the existing auth modules to provide a clean API interface.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.auth_manager = AuthManager(config)
        self.user_manager = UserManagementService(config)
        logger.info("AuthService initialized")
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return token."""
        try:
            # Authenticate user
            auth_result = await self.auth_manager.authenticate(
                username=username,
                password=password
            )
            
            if auth_result.get("success"):
                return {
                    "status": "success",
                    "token": auth_result.get("token"),
                    "user": auth_result.get("user"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": auth_result.get("error", "Authentication failed"),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def register(self, username: str, email: str, password: str, role: str = "user") -> Dict[str, Any]:
        """Register a new user."""
        try:
            # Create user
            user_result = await self.user_manager.create_user(
                username=username,
                email=email,
                password=password,
                role=role
            )
            
            if user_result.get("success"):
                return {
                    "status": "success",
                    "user": user_result.get("user"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": user_result.get("error", "Registration failed"),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user information."""
        try:
            user_info = await self.auth_manager.verify_token(token)
            return user_info
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    async def logout(self, user_id: str) -> Dict[str, Any]:
        """Logout user and invalidate token."""
        try:
            await self.auth_manager.logout(user_id)
            return {
                "status": "success",
                "message": "Logged out successfully",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information."""
        try:
            profile = await self.user_manager.get_user_profile(user_id)
            return {
                "status": "success",
                "profile": profile,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile information."""
        try:
            updated_profile = await self.user_manager.update_user_profile(
                user_id=user_id,
                profile_data=profile_data
            )
            
            return {
                "status": "success",
                "profile": updated_profile,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password."""
        try:
            result = await self.auth_manager.change_password(
                user_id=user_id,
                old_password=old_password,
                new_password=new_password
            )
            
            if result.get("success"):
                return {
                    "status": "success",
                    "message": "Password changed successfully",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("error", "Password change failed"),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def reset_password(self, email: str) -> Dict[str, Any]:
        """Reset user password."""
        try:
            result = await self.auth_manager.reset_password(email)
            
            if result.get("success"):
                return {
                    "status": "success",
                    "message": "Password reset email sent",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("error", "Password reset failed"),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def list_users(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List users (admin only)."""
        try:
            users = await self.user_manager.list_users(limit=limit, offset=offset)
            
            return {
                "status": "success",
                "users": users,
                "limit": limit,
                "offset": offset,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status and configuration."""
        return {
            "service": "auth",
            "status": "healthy",
            "auth_manager_available": hasattr(self, 'auth_manager'),
            "user_manager_available": hasattr(self, 'user_manager'),
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the auth service."""
        logger.info("Shutting down AuthService")
        # Cleanup if needed
        pass 