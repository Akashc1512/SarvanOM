"""
Auth Response Models

This module contains Pydantic models for authentication-related API responses.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class LoginResponse(BaseModel):
    """Login response model."""

    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: Dict[str, Any] = Field(..., description="User information")


class RegisterResponse(BaseModel):
    """Registration response model."""

    user_id: str = Field(..., description="User identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    message: str = Field(..., description="Registration message")
    created_at: datetime = Field(..., description="Account creation timestamp")


class UserResponse(BaseModel):
    """User response model."""

    user_id: str = Field(..., description="User identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    role: str = Field(..., description="User role")
    status: str = Field(..., description="User status")
    is_authenticated: bool = Field(..., description="Authentication status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class PasswordResetResponse(BaseModel):
    """Password reset response model."""

    message: str = Field(..., description="Reset message")
    email: str = Field(..., description="Email address")
    reset_sent: bool = Field(..., description="Whether reset email was sent")
    timestamp: datetime = Field(..., description="Reset request timestamp")


class PasswordChangeResponse(BaseModel):
    """Password change response model."""

    message: str = Field(..., description="Change message")
    changed_at: datetime = Field(..., description="Password change timestamp")
    success: bool = Field(..., description="Whether password was changed successfully")


class LogoutResponse(BaseModel):
    """Logout response model."""

    message: str = Field(..., description="Logout message")
    logged_out_at: datetime = Field(..., description="Logout timestamp")
    success: bool = Field(..., description="Whether logout was successful")


class AuthErrorResponse(BaseModel):
    """Authentication error response model."""

    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type")
    timestamp: datetime = Field(..., description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
