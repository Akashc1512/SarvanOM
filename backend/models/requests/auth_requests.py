"""
Auth Request Models

This module contains Pydantic models for authentication-related API requests.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request model."""

    username: str = Field(..., min_length=1, max_length=100, description="Username")
    password: str = Field(..., min_length=1, max_length=100, description="Password")
    remember_me: bool = Field(False, description="Remember login session")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username."""
        if not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip()


class RegisterRequest(BaseModel):
    """Registration request model."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password")
    confirm_password: str = Field(..., description="Password confirmation")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username."""
        if not v.strip():
            raise ValueError("Username cannot be empty")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Validate email."""
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("confirm_password")
    @classmethod
    def validate_password_match(cls, v, info):
        """Validate password confirmation."""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class PasswordResetRequest(BaseModel):
    """Password reset request model."""

    email: str = Field(..., description="Email address")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Validate email."""
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip()


class PasswordChangeRequest(BaseModel):
    """Password change request model."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, max_length=100, description="New password"
    )
    confirm_new_password: str = Field(..., description="New password confirmation")

    @field_validator("confirm_new_password")
    @classmethod
    def validate_password_match(cls, v, info):
        """Validate password confirmation."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class TokenRefreshRequest(BaseModel):
    """Token refresh request model."""

    refresh_token: str = Field(..., description="Refresh token")
