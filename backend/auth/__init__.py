# DEAD CODE - Candidate for deletion: This backend directory is not used by the main application
"""
Authentication Service for Universal Knowledge Hub.

This service handles user authentication, authorization, and user management.
"""

__version__ = "1.0.0"

from .auth_service import AuthService
from .user_management import UserManagementService

__all__ = ["AuthService", "UserManagementService"]
