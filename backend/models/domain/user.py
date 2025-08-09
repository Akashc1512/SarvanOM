"""
User Domain Models

This module contains the core user domain models and business logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum


class UserRole(Enum):
    """User roles."""

    ANONYMOUS = "anonymous"
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(Enum):
    """User status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"


@dataclass
class UserPreferences:
    """User preferences and settings."""

    language: str = "en"
    timezone: str = "UTC"
    max_tokens: int = 1000
    confidence_threshold: float = 0.8
    enable_caching: bool = True
    enable_analytics: bool = True


@dataclass
class UserContext:
    """User context for request processing."""

    user_id: str
    session_id: str
    role: UserRole = UserRole.ANONYMOUS
    preferences: UserPreferences = field(default_factory=UserPreferences)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class User:
    """Core user domain model."""

    id: str
    username: str
    email: Optional[str] = None
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    preferences: UserPreferences = field(default_factory=UserPreferences)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

    def __post_init__(self):
        """Validate user after initialization."""
        if not self.username.strip():
            raise ValueError("Username cannot be empty")

        if self.email and "@" not in self.email:
            raise ValueError("Invalid email format")

    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE

    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN

    def can_access_feature(self, feature: str) -> bool:
        """Check if user can access specific feature."""
        if self.role == UserRole.ADMIN:
            return True

        # Add feature-specific access rules here
        feature_rules = {
            "admin_panel": self.role == UserRole.ADMIN,
            "analytics": self.role in [UserRole.ADMIN, UserRole.MODERATOR],
            "advanced_queries": self.is_active(),
        }

        return feature_rules.get(feature, self.is_active())

    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.now()
        self.updated_at = datetime.now()

    def suspend(self, reason: str = ""):
        """Suspend user account."""
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.now()

    def activate(self):
        """Activate user account."""
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.now()
