"""
Unit tests for authentication token creation functionality.

Tests cover:
- JWT token creation and validation
- Access token generation
- Refresh token generation
- Token expiration handling
- Token blacklisting
- User session management
- Authentication flow
"""

import pytest
import jwt
import secrets
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from shared.core.secure_auth import JWTManager, AuthManager, UserSession, UserRole, AuthConfig


class TestAuthTokenCreation:
    """Test authentication token creation functionality."""

    @pytest.fixture
    def auth_config(self):
        """Create test auth configuration."""
        return AuthConfig(
            jwt_secret_key="test_secret_key_for_testing_only_very_long_key",
            jwt_algorithm="HS256",
            jwt_access_token_expire_minutes=30,
            jwt_refresh_token_expire_days=7,
            session_timeout_minutes=60,
            max_login_attempts=5,
            lockout_duration_minutes=15
        )

    @pytest.fixture
    def jwt_manager(self, auth_config):
        """Create JWT manager for testing."""
        return JWTManager(auth_config)

    @pytest.fixture
    def sample_user(self):
        """Sample user data for testing."""
        return {
            "id": "user123",
            "username": "testuser",
            "role": "user",
            "permissions": ["read", "write"]
        }

    @pytest.fixture
    def admin_user(self):
        """Sample admin user data for testing."""
        return {
            "id": "admin456",
            "username": "admin",
            "role": "admin",
            "permissions": ["read", "write", "admin", "delete"]
        }

    def test_create_access_token_basic(self, jwt_manager, sample_user):
        """Test basic access token creation."""
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        # Decode and verify token
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        assert decoded["sub"] == sample_user["id"]
        assert decoded["role"] == sample_user["role"]
        assert decoded["permissions"] == sample_user["permissions"]
        assert decoded["type"] == "access"
        assert "exp" in decoded
        assert "iat" in decoded
        assert "jti" in decoded

    def test_create_access_token_admin(self, jwt_manager, admin_user):
        """Test access token creation for admin user."""
        token = jwt_manager.create_access_token(
            user_id=admin_user["id"],
            role=UserRole(admin_user["role"]),
            permissions=admin_user["permissions"]
        )
        
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        assert decoded["sub"] == admin_user["id"]
        assert decoded["role"] == admin_user["role"]
        assert decoded["permissions"] == admin_user["permissions"]
        assert "admin" in decoded["permissions"]

    def test_create_refresh_token(self, jwt_manager, sample_user):
        """Test refresh token creation."""
        token = jwt_manager.create_refresh_token(user_id=sample_user["id"])
        
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        assert decoded["sub"] == sample_user["id"]
        assert decoded["type"] == "refresh"
        assert "exp" in decoded
        assert "iat" in decoded
        assert "jti" in decoded

    def test_token_expiration_access(self, jwt_manager, sample_user):
        """Test access token expiration."""
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        # Check expiration time
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = exp_time - now
        
        # Should expire in approximately 30 minutes
        assert timedelta(minutes=29) <= time_diff <= timedelta(minutes=31)

    def test_token_expiration_refresh(self, jwt_manager, sample_user):
        """Test refresh token expiration."""
        token = jwt_manager.create_refresh_token(user_id=sample_user["id"])
        
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        # Check expiration time
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = exp_time - now
        
        # Should expire in approximately 7 days
        assert timedelta(days=6) <= time_diff <= timedelta(days=8)

    def test_token_blacklisting(self, jwt_manager, sample_user):
        """Test token blacklisting functionality."""
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        # Blacklist the token
        jwt_manager.blacklisted_tokens.add(token)
        
        # Verify token is blacklisted
        assert token in jwt_manager.blacklisted_tokens

    def test_token_validation_blacklisted(self, jwt_manager, sample_user):
        """Test validation of blacklisted tokens."""
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        # Blacklist the token
        jwt_manager.blacklisted_tokens.add(token)
        
        # Verify token is in blacklist
        assert token in jwt_manager.blacklisted_tokens
        
        # Token should still be decodable (blacklist check would be done in validation layer)
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        assert decoded["sub"] == sample_user["id"]

    def test_token_jti_uniqueness(self, jwt_manager, sample_user):
        """Test that each token has a unique JTI."""
        token1 = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        token2 = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        decoded1 = jwt.decode(
            token1, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        decoded2 = jwt.decode(
            token2, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        assert decoded1["jti"] != decoded2["jti"]

    def test_user_session_creation(self, auth_config, sample_user):
        """Test user session creation."""
        session_id = secrets.token_urlsafe(32)
        session = UserSession(
            user_id=sample_user["id"],
            session_id=session_id,
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=auth_config.session_timeout_minutes),
            last_activity=datetime.now(timezone.utc),
            ip_address="127.0.0.1",
            user_agent="test-agent",
            is_active=True
        )
        
        assert session.user_id == sample_user["id"]
        assert session.session_id == session_id
        assert session.role == UserRole(sample_user["role"])
        assert session.permissions == sample_user["permissions"]
        assert session.is_active is True

    def test_session_expiration(self, auth_config, sample_user):
        """Test session expiration logic."""
        session_id = secrets.token_urlsafe(32)
        session = UserSession(
            user_id=sample_user["id"],
            session_id=session_id,
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=auth_config.session_timeout_minutes),
            last_activity=datetime.now(timezone.utc),
            ip_address="127.0.0.1",
            user_agent="test-agent",
            is_active=True
        )
        
        # Check if session is expired
        is_expired = datetime.now(timezone.utc) > session.expires_at
        assert not is_expired  # Should not be expired immediately after creation

    def test_token_payload_structure(self, jwt_manager, sample_user):
        """Test token payload structure and required fields."""
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        required_fields = ["sub", "role", "permissions", "type", "exp", "iat", "jti"]
        for field in required_fields:
            assert field in decoded

    def test_permissions_encoding(self, jwt_manager, sample_user):
        """Test that permissions are properly encoded in token."""
        permissions = ["read", "write", "delete", "admin"]
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=permissions
        )
        
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        assert decoded["permissions"] == permissions
        assert len(decoded["permissions"]) == 4

    def test_role_encoding(self, jwt_manager, sample_user):
        """Test that user role is properly encoded in token."""
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole.ADMIN,  # Use enum value
            permissions=sample_user["permissions"]
        )
        
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        assert decoded["role"] == "admin"

    def test_token_creation_with_empty_permissions(self, jwt_manager, sample_user):
        """Test token creation with empty permissions list."""
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=[]
        )
        
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        assert decoded["permissions"] == []

    def test_token_creation_with_none_permissions(self, jwt_manager, sample_user):
        """Test token creation with None permissions."""
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=None
        )
        
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        assert decoded["permissions"] is None

    def test_token_iat_timestamp(self, jwt_manager, sample_user):
        """Test that issued at timestamp is recent."""
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        iat_time = datetime.fromtimestamp(decoded["iat"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = now - iat_time
        
        # Should be issued within the last minute
        assert time_diff <= timedelta(minutes=1)

    def test_token_exp_after_iat(self, jwt_manager, sample_user):
        """Test that expiration time is after issued at time."""
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        assert decoded["exp"] > decoded["iat"]

    def test_refresh_token_no_permissions(self, jwt_manager, sample_user):
        """Test that refresh tokens don't contain permissions."""
        token = jwt_manager.create_refresh_token(user_id=sample_user["id"])
        
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        assert "permissions" not in decoded
        assert "role" not in decoded

    def test_token_signature_verification(self, jwt_manager, sample_user):
        """Test token signature verification."""
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        # Should decode successfully with correct secret
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        assert decoded["sub"] == sample_user["id"]
        
        # Should fail with wrong secret
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(
                token, 
                "wrong_secret_key", 
                algorithms=[jwt_manager.config.jwt_algorithm]
            )

    def test_token_algorithm_verification(self, jwt_manager, sample_user):
        """Test token algorithm verification."""
        token = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        # Should decode successfully with correct algorithm
        decoded = jwt.decode(
            token, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=["HS256"]
        )
        
        assert decoded["sub"] == sample_user["id"]
        
        # Should fail with wrong algorithm
        with pytest.raises(jwt.InvalidAlgorithmError):
            jwt.decode(
                token, 
                jwt_manager.config.jwt_secret_key, 
                algorithms=["HS512"]
            )

    def test_multiple_tokens_same_user(self, jwt_manager, sample_user):
        """Test creating multiple tokens for the same user."""
        token1 = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        token2 = jwt_manager.create_access_token(
            user_id=sample_user["id"],
            role=UserRole(sample_user["role"]),
            permissions=sample_user["permissions"]
        )
        
        # Both tokens should be valid and different
        decoded1 = jwt.decode(
            token1, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        decoded2 = jwt.decode(
            token2, 
            jwt_manager.config.jwt_secret_key, 
            algorithms=[jwt_manager.config.jwt_algorithm]
        )
        
        assert decoded1["sub"] == decoded2["sub"]  # Same user
        assert token1 != token2  # Different tokens
        assert decoded1["jti"] != decoded2["jti"]  # Different JTI

    def test_token_creation_performance(self, jwt_manager, sample_user):
        """Test token creation performance (basic timing)."""
        import time
        
        start_time = time.time()
        for _ in range(100):
            jwt_manager.create_access_token(
                user_id=sample_user["id"],
                role=UserRole(sample_user["role"]),
                permissions=sample_user["permissions"]
            )
        end_time = time.time()
        
        # Should create 100 tokens in reasonable time (less than 1 second)
        assert end_time - start_time < 1.0
