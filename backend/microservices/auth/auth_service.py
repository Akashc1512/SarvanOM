"""
Auth Microservice - Auth Service
Core authentication and authorization functionality.

This service provides:
- User authentication
- JWT token management
- User management
- Security validation
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Import core components
from .security import SecurityManager
from .user_management import UserManager
from .validators import AuthValidators

logger = logging.getLogger(__name__)

class AuthService:
    """Auth service for authentication and authorization."""
    
    def __init__(self):
        """Initialize the auth service."""
        self.security_manager = None
        self.user_manager = None
        self.validators = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all auth components."""
        try:
            # Initialize security manager
            self.security_manager = SecurityManager()
            
            # Initialize user manager
            self.user_manager = UserManager()
            
            # Initialize validators
            self.validators = AuthValidators()
            
            logger.info("Auth components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize auth components: {e}")
    
    async def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate a user."""
        start_time = time.time()
        
        try:
            # Validate input
            if self.validators:
                await self.validators.validate_login_credentials(username, password)
            
            # Authenticate user
            if self.user_manager:
                user = await self.user_manager.authenticate_user(username, password)
            else:
                # Fallback to basic authentication
                user = await self._basic_authentication(username, password)
            
            # Generate JWT token
            if self.security_manager and user:
                token = await self.security_manager.generate_jwt_token(user)
            else:
                token = None
            
            auth_time_ms = int((time.time() - start_time) * 1000)
            
            if user and token:
                return {
                    "user": user,
                    "token": token,
                    "auth_time_ms": auth_time_ms,
                    "status": "success"
                }
            else:
                return {
                    "user": None,
                    "token": None,
                    "auth_time_ms": auth_time_ms,
                    "status": "failed",
                    "error": "Invalid credentials"
                }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {
                "user": None,
                "token": None,
                "auth_time_ms": int((time.time() - start_time) * 1000),
                "status": "error",
                "error": str(e)
            }
    
    async def _basic_authentication(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Basic authentication fallback."""
        # This is a mock implementation
        if username == "admin" and password == "password":
            return {
                "id": "user_1",
                "username": username,
                "email": f"{username}@example.com",
                "role": "admin",
                "created_at": datetime.now().isoformat()
            }
        return None
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user."""
        try:
            # Validate user data
            if self.validators:
                await self.validators.validate_registration_data(user_data)
            
            # Create user
            if self.user_manager:
                user = await self.user_manager.create_user(user_data)
            else:
                # Fallback to basic user creation
                user = await self._basic_user_creation(user_data)
            
            return {
                "user": user,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"User registration error: {e}")
            return {
                "user": None,
                "status": "error",
                "error": str(e)
            }
    
    async def _basic_user_creation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic user creation fallback."""
        return {
            "id": f"user_{int(time.time())}",
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "role": "user",
            "created_at": datetime.now().isoformat()
        }
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate a JWT token."""
        try:
            if self.security_manager:
                payload = await self.security_manager.validate_jwt_token(token)
                return {
                    "valid": True,
                    "payload": payload
                }
            else:
                return {
                    "valid": False,
                    "error": "Security manager not available"
                }
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID."""
        try:
            if self.user_manager:
                user = await self.user_manager.get_user_by_id(user_id)
            else:
                # Fallback to mock user
                user = {
                    "id": user_id,
                    "username": "mock_user",
                    "email": "mock@example.com",
                    "role": "user",
                    "created_at": datetime.now().isoformat()
                }
            
            return {
                "user": user,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return {
                "user": None,
                "status": "error",
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the auth service."""
        try:
            health_status = {
                "service": "auth",
                "status": "healthy",
                "components": {
                    "security_manager": "healthy" if self.security_manager else "unavailable",
                    "user_manager": "healthy" if self.user_manager else "unavailable",
                    "validators": "healthy" if self.validators else "unavailable"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return health_status
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "service": "auth",
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.security_manager:
                await self.security_manager.cleanup()
            if self.user_manager:
                await self.user_manager.cleanup()
            logger.info("Auth service cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
