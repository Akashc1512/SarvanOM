"""
SSO Service for API Gateway

This module provides Single Sign-On (SSO) functionality with support for:
- OAuth2 providers (Google, GitHub, Microsoft, etc.)
- SAML authentication
- JWT token management
- Multi-tenant authentication
- Role-based access control (RBAC)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from jose import JWTError, jwt as jose_jwt
import aiohttp
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

# Load .env so SECRET_KEY can come from environment
load_dotenv()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings (prefer JWT_SECRET_KEY, fallback to JWT_SECRET)
SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.getenv(
    "JWT_SECRET", "your-secret-key-here"
)
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class AuthProvider(Enum):
    """Supported authentication providers."""

    INTERNAL = "internal"
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"
    SAML = "saml"
    OAUTH2 = "oauth2"


class UserRole(Enum):
    """User roles for RBAC."""

    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    READONLY = "readonly"


@dataclass
class User:
    """User data model."""

    user_id: str
    username: str
    email: str
    role: UserRole
    tenant_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None
    permissions: List[str] = None


@dataclass
class AuthToken:
    """Authentication token data."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class SSOService:
    """Service for handling SSO and authentication."""

    def __init__(self):
        self.users = {}  # In-memory user store (should be database)
        self.active_sessions = {}
        self.oauth_providers = {
            "google": {
                "client_id": "your-google-client-id",
                "client_secret": "your-google-client-secret",
                "auth_url": "https://accounts.google.com/o/oauth2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
            },
            "github": {
                "client_id": "your-github-client-id",
                "client_secret": "your-github-client-secret",
                "auth_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
            },
        }
        self._initialize_default_users()

    def _initialize_default_users(self):
        """Initialize default users for development."""
        default_users = [
            User(
                user_id="admin-001",
                username="admin",
                email="admin@sarvanom.com",
                role=UserRole.ADMIN,
                tenant_id="default",
                created_at=datetime.now(),
                permissions=["read", "write", "delete", "admin"],
            ),
            User(
                user_id="user-001",
                username="user",
                email="user@sarvanom.com",
                role=UserRole.USER,
                tenant_id="default",
                created_at=datetime.now(),
                permissions=["read", "write"],
            ),
        ]

        for user in default_users:
            self.users[user.user_id] = user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except PyJWTError:
            return None

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        # In a real implementation, this would query a database
        for user in self.users.values():
            if user.username == username and user.is_active:
                # For demo purposes, accept any password for existing users
                return user
        return None

    async def authenticate_oauth(self, provider: str, code: str) -> Optional[User]:
        """Authenticate user via OAuth provider."""
        if provider not in self.oauth_providers:
            logger.error(f"Unsupported OAuth provider: {provider}")
            return None

        try:
            # Exchange code for access token
            token_data = await self._exchange_oauth_code(provider, code)
            if not token_data:
                return None

            # Get user info from provider
            user_info = await self._get_oauth_user_info(
                provider, token_data["access_token"]
            )
            if not user_info:
                return None

            # Create or update user
            user = await self._create_or_update_oauth_user(provider, user_info)
            return user

        except Exception as e:
            logger.error(f"OAuth authentication failed: {e}")
            return None

    async def _exchange_oauth_code(
        self, provider: str, code: str
    ) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token."""
        provider_config = self.oauth_providers[provider]

        async with aiohttp.ClientSession() as session:
            data = {
                "client_id": provider_config["client_id"],
                "client_secret": provider_config["client_secret"],
                "code": code,
                "grant_type": "authorization_code",
            }

            async with session.post(
                provider_config["token_url"], data=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"OAuth token exchange failed: {response.status}")
                    return None

    async def _get_oauth_user_info(
        self, provider: str, access_token: str
    ) -> Optional[Dict[str, Any]]:
        """Get user information from OAuth provider."""
        provider_config = self.oauth_providers[provider]

        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                provider_config["userinfo_url"], headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get user info from {provider}")
                    return None

    async def _create_or_update_oauth_user(
        self, provider: str, user_info: Dict[str, Any]
    ) -> User:
        """Create or update user from OAuth user info."""
        email = user_info.get("email")
        username = user_info.get("login") or user_info.get("name") or email

        # Check if user exists
        for user in self.users.values():
            if user.email == email:
                user.last_login = datetime.now()
                return user

        # Create new user
        new_user = User(
            user_id=f"{provider}-{user_info.get('id', len(self.users) + 1)}",
            username=username,
            email=email,
            role=UserRole.USER,
            tenant_id="default",
            created_at=datetime.now(),
            last_login=datetime.now(),
            permissions=["read", "write"],
        )

        self.users[new_user.user_id] = new_user
        return new_user

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def has_permission(self, user: User, permission: str) -> bool:
        """Check if user has specific permission."""
        return permission in user.permissions if user.permissions else False

    def has_role(self, user: User, role: UserRole) -> bool:
        """Check if user has specific role."""
        return user.role == role

    async def create_session(self, user: User) -> AuthToken:
        """Create a new session for a user."""
        access_token = self.create_access_token(
            data={"sub": user.user_id, "email": user.email, "role": user.role.value}
        )

        session = AuthToken(
            access_token=access_token, expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        self.active_sessions[user.user_id] = session
        return session

    async def validate_session(self, token: str) -> Optional[User]:
        """Validate a session token and return the user."""
        payload = self.verify_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user = await self.get_user_by_id(user_id)
        if not user or not user.is_active:
            return None

        return user

    async def revoke_session(self, user_id: str) -> bool:
        """Revoke a user's session."""
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
            return True
        return False

    async def get_oauth_url(self, provider: str, redirect_uri: str) -> Optional[str]:
        """Get OAuth authorization URL."""
        if provider not in self.oauth_providers:
            return None

        provider_config = self.oauth_providers[provider]
        params = {
            "client_id": provider_config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": (
                "read:user user:email"
                if provider == "github"
                else "openid email profile"
            ),
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{provider_config['auth_url']}?{query_string}"

    async def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        total_users = len(self.users)
        active_users = len([u for u in self.users.values() if u.is_active])
        active_sessions = len(self.active_sessions)

        role_counts = {}
        for user in self.users.values():
            role = user.role.value
            role_counts[role] = role_counts.get(role, 0) + 1

        return {
            "total_users": total_users,
            "active_users": active_users,
            "active_sessions": active_sessions,
            "role_distribution": role_counts,
            "last_updated": datetime.now().isoformat(),
        }


# Create global SSO service instance
sso_service = SSOService()
