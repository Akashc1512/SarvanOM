"""
Comprehensive Database Model Tests - MAANG Standards

This module provides comprehensive unit tests for all database models,
ensuring they follow MAANG-level standards with proper validation,
relationships, and functionality testing.

Test Coverage:
    - Model initialization and validation
    - Relationship integrity
    - Business logic methods
    - Soft delete functionality
    - Audit trail functionality
    - Performance optimizations
    - Security features

Authors:
    - Universal Knowledge Platform Engineering Team
    
Version:
    2.0.0 (2024-12-28)
"""

import pytest
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from unittest.mock import Mock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import models
from shared.models.models import (
    Base,
    User,
    Role,
    UserSession,
    APIKey,
    KnowledgeItem,
    Query,
    AuditLog,
    RecordStatus,
    AuditAction,
    EncryptionKey,
)


# Test database setup
@pytest.fixture
def engine():
    """Create in-memory test database."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create test session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_user_data():
    """Provide sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": "hashed_password_123",
        "full_name": "Test User",
        "bio": "Test user bio",
    }


@pytest.fixture
def sample_role_data():
    """Provide sample role data for testing."""
    return {
        "name": "test_role",
        "description": "Test role description",
        "permissions": {"read": True, "write": False},
        "is_system": False,
    }


class TestBaseModel:
    """Test base model functionality."""

    def test_base_model_initialization(self, session):
        """Test base model initialization."""
        # Create a simple model instance
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
        )
        session.add(user)
        session.commit()

        # Verify base fields
        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.status == RecordStatus.ACTIVE
        assert user.version == 1
        assert user.deleted_at is None

    def test_soft_delete_functionality(self, session, sample_user_data):
        """Test soft delete functionality."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Verify active status
        assert user.is_active is True
        assert user.status == RecordStatus.ACTIVE

        # Perform soft delete
        user.soft_delete()
        session.commit()

        # Verify deleted status
        assert user.is_active is False
        assert user.status == RecordStatus.DELETED
        assert user.deleted_at is not None

    def test_restore_functionality(self, session, sample_user_data):
        """Test restore functionality."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Soft delete
        user.soft_delete()
        session.commit()
        assert user.is_active is False

        # Restore
        user.restore()
        session.commit()

        # Verify restored status
        assert user.is_active is True
        assert user.status == RecordStatus.ACTIVE
        assert user.deleted_at is None

    def test_archive_functionality(self, session, sample_user_data):
        """Test archive functionality."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Archive
        user.archive()
        session.commit()

        # Verify archived status
        assert user.status == RecordStatus.ARCHIVED
        assert user.is_active is False

    def test_to_dict_method(self, session, sample_user_data):
        """Test to_dict method."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Test basic to_dict
        user_dict = user.to_dict()
        assert "id" in user_dict
        assert "username" in user_dict
        assert "email" in user_dict
        assert "created_at" in user_dict

        # Test with include
        user_dict = user.to_dict(include=["username", "email"])
        assert "username" in user_dict
        assert "email" in user_dict
        assert "id" not in user_dict

        # Test with exclude
        user_dict = user.to_dict(exclude=["password_hash"])
        assert "username" in user_dict
        assert "password_hash" not in user_dict

    def test_update_from_dict(self, session, sample_user_data):
        """Test update_from_dict method."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Update with new data
        update_data = {"full_name": "Updated Name", "bio": "Updated bio"}
        user.update_from_dict(update_data)
        session.commit()

        # Verify updates
        assert user.full_name == "Updated Name"
        assert user.bio == "Updated bio"

    def test_optimistic_locking(self, session, sample_user_data):
        """Test optimistic locking."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        initial_version = user.version

        # Update user
        user.full_name = "Updated Name"
        session.commit()

        # Verify version increment
        assert user.version == initial_version + 1


class TestUserModel:
    """Test User model functionality."""

    def test_user_creation(self, session, sample_user_data):
        """Test user creation with valid data."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Verify user creation
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password_123"
        assert user.full_name == "Test User"
        assert user.bio == "Test user bio"
        assert user.email_verified is False
        assert user.two_factor_enabled is False
        assert user.login_count == 0
        assert user.failed_login_count == 0

    def test_user_validation(self, session):
        """Test user validation rules."""
        # Test valid email
        user = User(
            username="testuser",
            email="valid@example.com",
            password_hash="hashed_password",
        )
        session.add(user)
        session.commit()
        assert user.email == "valid@example.com"

        # Test invalid email (should raise validation error)
        with pytest.raises(ValueError):
            user.email = "invalid-email"
            session.commit()

    def test_username_validation(self, session, sample_user_data):
        """Test username validation."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Test valid username
        user.username = "validuser"
        session.commit()
        assert user.username == "validuser"

        # Test invalid username (too short)
        with pytest.raises(ValueError):
            user.username = "ab"  # Too short
            session.commit()

    def test_display_name_property(self, session, sample_user_data):
        """Test display_name property."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Test with full_name
        assert user.display_name == "Test User"

        # Test without full_name
        user.full_name = None
        session.commit()
        assert user.display_name == "testuser"

    def test_account_locking(self, session, sample_user_data):
        """Test account locking functionality."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Initially not locked
        assert user.is_locked is False

        # Lock account
        user.locked_until = datetime.now(timezone.utc) + timedelta(hours=1)
        session.commit()
        assert user.is_locked is True

        # Unlock account
        user.locked_until = None
        session.commit()
        assert user.is_locked is False

    def test_login_tracking(self, session, sample_user_data):
        """Test login tracking functionality."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Record successful login
        user.record_login("192.168.1.1")
        session.commit()

        assert user.last_login_at is not None
        assert user.last_login_ip == "192.168.1.1"
        assert user.login_count == 1

        # Record failed login
        user.record_failed_login()
        session.commit()

        assert user.failed_login_count == 1

    def test_role_management(self, session, sample_user_data, sample_role_data):
        """Test role management functionality."""
        user = User(**sample_user_data)
        role = Role(**sample_role_data)
        session.add_all([user, role])
        session.commit()

        # Add role to user
        user.add_role(role)
        session.commit()

        assert user.has_role("test_role")
        assert user.has_permission("read")
        assert not user.has_permission("write")

        # Remove role
        user.remove_role(role)
        session.commit()

        assert not user.has_role("test_role")


class TestRoleModel:
    """Test Role model functionality."""

    def test_role_creation(self, session, sample_role_data):
        """Test role creation with valid data."""
        role = Role(**sample_role_data)
        session.add(role)
        session.commit()

        # Verify role creation
        assert role.name == "test_role"
        assert role.description == "Test role description"
        assert role.permissions == {"read": True, "write": False}
        assert role.is_system is False

    def test_role_validation(self, session):
        """Test role validation rules."""
        # Test valid role name
        role = Role(name="valid_role", description="Valid role", permissions={})
        session.add(role)
        session.commit()
        assert role.name == "valid_role"

        # Test invalid role name (too short)
        with pytest.raises(ValueError):
            role.name = "ab"  # Too short
            session.commit()

    def test_permission_checking(self, session, sample_role_data):
        """Test permission checking functionality."""
        role = Role(**sample_role_data)
        session.add(role)
        session.commit()

        # Test permission checking
        assert role.has_permission("read") is True
        assert role.has_permission("write") is False
        assert role.has_permission("delete") is False


class TestUserSessionModel:
    """Test UserSession model functionality."""

    def test_session_creation(self, session, sample_user_data):
        """Test session creation."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        user_session = UserSession(
            user_id=user.id,
            token="session_token_123",
            refresh_token="refresh_token_123",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            refresh_expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0...",
            device_info={"device": "desktop", "browser": "chrome"},
        )
        session.add(user_session)
        session.commit()

        # Verify session creation
        assert user_session.user_id == user.id
        assert user_session.token == "session_token_123"
        assert user_session.ip_address == "192.168.1.1"
        assert user_session.device_info["device"] == "desktop"

    def test_session_expiration(self, session, sample_user_data):
        """Test session expiration functionality."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Create expired session
        expired_session = UserSession(
            user_id=user.id,
            token="expired_token",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        session.add(expired_session)
        session.commit()

        # Verify expiration
        assert expired_session.is_expired is True

        # Create valid session
        valid_session = UserSession(
            user_id=user.id,
            token="valid_token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        session.add(valid_session)
        session.commit()

        # Verify valid session
        assert valid_session.is_expired is False

    def test_session_extension(self, session, sample_user_data):
        """Test session extension functionality."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        user_session = UserSession(
            user_id=user.id,
            token="test_token",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
        session.add(user_session)
        session.commit()

        original_expires_at = user_session.expires_at

        # Extend session
        user_session.extend(minutes=60)
        session.commit()

        # Verify extension
        assert user_session.expires_at > original_expires_at


class TestAPIKeyModel:
    """Test APIKey model functionality."""

    def test_api_key_creation(self, session, sample_user_data):
        """Test API key creation."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        api_key = APIKey(
            user_id=user.id,
            name="Test API Key",
            key_hash="hashed_key_123",
            key_prefix="test_",
            scopes=["read", "write"],
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            rate_limit=1000,
            allowed_ips=["192.168.1.1", "10.0.0.1"],
        )
        session.add(api_key)
        session.commit()

        # Verify API key creation
        assert api_key.user_id == user.id
        assert api_key.name == "Test API Key"
        assert api_key.key_hash == "hashed_key_123"
        assert api_key.scopes == ["read", "write"]
        assert api_key.rate_limit == 1000
        assert api_key.allowed_ips == ["192.168.1.1", "10.0.0.1"]

    def test_api_key_expiration(self, session, sample_user_data):
        """Test API key expiration functionality."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Create expired API key
        expired_key = APIKey(
            user_id=user.id,
            name="Expired Key",
            key_hash="expired_hash",
            key_prefix="exp_",
            scopes=["read"],
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        session.add(expired_key)
        session.commit()

        # Verify expiration
        assert expired_key.is_expired is True

        # Create valid API key
        valid_key = APIKey(
            user_id=user.id,
            name="Valid Key",
            key_hash="valid_hash",
            key_prefix="val_",
            scopes=["read"],
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        session.add(valid_key)
        session.commit()

        # Verify valid key
        assert valid_key.is_expired is False

    def test_api_key_usage_tracking(self, session, sample_user_data):
        """Test API key usage tracking."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        api_key = APIKey(
            user_id=user.id,
            name="Test Key",
            key_hash="test_hash",
            key_prefix="test_",
            scopes=["read"],
        )
        session.add(api_key)
        session.commit()

        # Record usage
        api_key.record_usage("192.168.1.1")
        session.commit()

        assert api_key.last_used_at is not None
        assert api_key.usage_count == 1

    def test_api_key_scope_checking(self, session, sample_user_data):
        """Test API key scope checking."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        api_key = APIKey(
            user_id=user.id,
            name="Test Key",
            key_hash="test_hash",
            key_prefix="test_",
            scopes=["read", "write"],
        )
        session.add(api_key)
        session.commit()

        # Test scope checking
        assert api_key.has_scope("read") is True
        assert api_key.has_scope("write") is True
        assert api_key.has_scope("delete") is False


class TestKnowledgeItemModel:
    """Test KnowledgeItem model functionality."""

    def test_knowledge_item_creation(self, session, sample_user_data):
        """Test knowledge item creation."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        knowledge_item = KnowledgeItem(
            title="Test Knowledge Item",
            content="This is test content for the knowledge item.",
            summary="Test summary",
            type="document",
            source="Test Source",
            source_url="https://example.com",
            confidence=0.95,
            tags=["test", "knowledge"],
            embedding=[0.1, 0.2, 0.3],
            created_by=user.id,
        )
        session.add(knowledge_item)
        session.commit()

        # Verify knowledge item creation
        assert knowledge_item.title == "Test Knowledge Item"
        assert knowledge_item.content == "This is test content for the knowledge item."
        assert knowledge_item.summary == "Test summary"
        assert knowledge_item.type == "document"
        assert knowledge_item.confidence == 0.95
        assert knowledge_item.tags == ["test", "knowledge"]
        assert knowledge_item.embedding == [0.1, 0.2, 0.3]
        assert knowledge_item.created_by == user.id

    def test_confidence_validation(self, session, sample_user_data):
        """Test confidence validation."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Test valid confidence
        knowledge_item = KnowledgeItem(
            title="Test Item",
            content="Test content",
            confidence=0.8,
            created_by=user.id,
        )
        session.add(knowledge_item)
        session.commit()
        assert knowledge_item.confidence == 0.8

        # Test invalid confidence (too high)
        with pytest.raises(ValueError):
            knowledge_item.confidence = 1.5
            session.commit()

        # Test invalid confidence (too low)
        with pytest.raises(ValueError):
            knowledge_item.confidence = -0.1
            session.commit()

    def test_tag_management(self, session, sample_user_data):
        """Test tag management functionality."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        knowledge_item = KnowledgeItem(
            title="Test Item",
            content="Test content",
            tags=["tag1", "tag2"],
            created_by=user.id,
        )
        session.add(knowledge_item)
        session.commit()

        # Add tag
        knowledge_item.add_tag("tag3")
        session.commit()
        assert "tag3" in knowledge_item.tags

        # Remove tag
        knowledge_item.remove_tag("tag1")
        session.commit()
        assert "tag1" not in knowledge_item.tags
        assert "tag2" in knowledge_item.tags
        assert "tag3" in knowledge_item.tags


class TestQueryModel:
    """Test Query model functionality."""

    def test_query_creation(self, session, sample_user_data):
        """Test query creation."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        query = Query(
            user_id=user.id,
            query_text="What is Python?",
            query_embedding=[0.1, 0.2, 0.3],
            response_text="Python is a programming language.",
            response_time_ms=150,
            tokens_used=100,
            cost=Decimal("0.0025"),
            feedback_rating=5,
            feedback_text="Great response!",
        )
        session.add(query)
        session.commit()

        # Verify query creation
        assert query.user_id == user.id
        assert query.query_text == "What is Python?"
        assert query.response_text == "Python is a programming language."
        assert query.response_time_ms == 150
        assert query.tokens_used == 100
        assert query.cost == Decimal("0.0025")
        assert query.feedback_rating == 5
        assert query.feedback_text == "Great response!"


class TestAuditLogModel:
    """Test AuditLog model functionality."""

    def test_audit_log_creation(self, session, sample_user_data):
        """Test audit log creation."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        audit_log = AuditLog(
            user_id=user.id,
            action=AuditAction.CREATE,
            entity_type="User",
            entity_id=user.id,
            old_values=None,
            new_values={"username": "testuser", "email": "test@example.com"},
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0...",
        )
        session.add(audit_log)
        session.commit()

        # Verify audit log creation
        assert audit_log.user_id == user.id
        assert audit_log.action == AuditAction.CREATE
        assert audit_log.entity_type == "User"
        assert audit_log.entity_id == user.id
        assert audit_log.new_values["username"] == "testuser"
        assert audit_log.ip_address == "192.168.1.1"


class TestModelRelationships:
    """Test model relationships and integrity."""

    def test_user_role_relationship(self, session, sample_user_data, sample_role_data):
        """Test user-role relationship."""
        user = User(**sample_user_data)
        role = Role(**sample_role_data)
        session.add_all([user, role])
        session.commit()

        # Add role to user
        user.add_role(role)
        session.commit()

        # Verify relationship
        assert role in user.roles
        assert user in role.users

    def test_user_session_relationship(self, session, sample_user_data):
        """Test user-session relationship."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        user_session = UserSession(
            user_id=user.id,
            token="test_token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        session.add(user_session)
        session.commit()

        # Verify relationship
        assert user_session.user == user
        assert user_session in user.sessions

    def test_user_api_key_relationship(self, session, sample_user_data):
        """Test user-API key relationship."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        api_key = APIKey(
            user_id=user.id,
            name="Test Key",
            key_hash="test_hash",
            key_prefix="test_",
            scopes=["read"],
        )
        session.add(api_key)
        session.commit()

        # Verify relationship
        assert api_key.user == user
        assert api_key in user.api_keys

    def test_knowledge_item_creator_relationship(self, session, sample_user_data):
        """Test knowledge item-creator relationship."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        knowledge_item = KnowledgeItem(
            title="Test Item", content="Test content", created_by=user.id
        )
        session.add(knowledge_item)
        session.commit()

        # Verify relationship
        assert knowledge_item.creator == user


class TestModelPerformance:
    """Test model performance optimizations."""

    def test_index_usage(self, session):
        """Test that indexes are properly used."""
        # This would require database-specific testing
        # For now, we'll verify that indexes are defined
        user_table = User.__table__
        assert any(idx.name == "idx_users_email" for idx in user_table.indexes)
        assert any(idx.name == "idx_users_username" for idx in user_table.indexes)

    def test_lazy_loading(self, session, sample_user_data):
        """Test lazy loading behavior."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Test that relationships are lazy loaded by default
        # (except those marked as 'joined')
        assert user.sessions.lazy == "dynamic"
        assert user.api_keys.lazy == "dynamic"


class TestModelSecurity:
    """Test model security features."""

    @patch("shared.models.models.EncryptionKey.get_key")
    def test_encrypted_fields(self, mock_get_key, session, sample_user_data):
        """Test encrypted field functionality."""
        mock_get_key.return_value = b"test_key_32_bytes_long_key"

        user = User(**sample_user_data)
        user.two_factor_secret = "secret_value"
        session.add(user)
        session.commit()

        # Verify encrypted field is stored
        assert user.two_factor_secret == "secret_value"

    def test_soft_delete_security(self, session, sample_user_data):
        """Test soft delete security."""
        user = User(**sample_user_data)
        session.add(user)
        session.commit()

        # Soft delete user
        user.soft_delete()
        session.commit()

        # Verify user is not active
        assert user.is_active is False
        assert user.status == RecordStatus.DELETED


# Performance benchmarks
class TestModelPerformanceBenchmarks:
    """Performance benchmarks for database models."""

    def test_bulk_insert_performance(self, session):
        """Test bulk insert performance."""
        import time

        # Create multiple users
        users = []
        for i in range(100):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=f"hash{i}",
            )
            users.append(user)

        # Measure insert time
        start_time = time.time()
        session.add_all(users)
        session.commit()
        end_time = time.time()

        # Verify performance (should complete in reasonable time)
        assert end_time - start_time < 5.0  # 5 seconds max

        # Verify all users were created
        assert session.query(User).count() == 100

    def test_query_performance(self, session):
        """Test query performance."""
        import time

        # Create test data
        users = []
        for i in range(100):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=f"hash{i}",
            )
            users.append(user)
        session.add_all(users)
        session.commit()

        # Measure query time
        start_time = time.time()
        result = session.query(User).filter(User.username.like("user%")).all()
        end_time = time.time()

        # Verify performance
        assert end_time - start_time < 1.0  # 1 second max
        assert len(result) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
