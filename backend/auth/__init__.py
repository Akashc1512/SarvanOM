"""
Auth Service
Handles authentication and authorization functionality.

This service provides:
- User authentication and registration
- JWT token management
- Role-based access control
- Security validation
"""

from .auth_service import AuthService

__all__ = [
    "AuthService"
] 