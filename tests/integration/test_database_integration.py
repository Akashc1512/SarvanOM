"""
Database Integration Tests - MAANG Standards

This module provides comprehensive integration tests for database models,
testing real-world scenarios, data integrity, and complex relationships.

Test Coverage:
    - Complex queries and joins
    - Data integrity constraints
    - Transaction handling
    - Concurrent access
    - Migration scenarios
    - Performance under load
    - Error handling and recovery

Authors:
    - Universal Knowledge Platform Engineering Team
    
Version:
    2.0.0 (2024-12-28)
"""

import pytest
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import IntegrityError, ConstraintViolation

# Import models
from shared.models.models import (
    Base, User, Role, UserSession, APIKey, KnowledgeItem, 
    Query, AuditLog, RecordStatus, AuditAction
)

# Test database setup
@pytest.fixture
def engine():
    """Create in-memory test database with proper constraints."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(engine):
    """Create test session with transaction support."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def sample_data(session):
    """Create sample data for integration tests."""
    # Create roles
    admin_role = Role(
        name="admin",
        description="Administrator role",
        permissions={"read": True, "write": True, "delete": True},
        is_system=True
    )
    
    user_role = Role(
        name="user",
        description="Regular user role",
        permissions={"read": True, "write": False},
        is_system=True
    )
    
    session.add_all([admin_role, user_role])
    session.commit()
    
    # Create users
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash="admin_hash",
        full_name="Admin User",
        email_verified=True
    )
    
    regular_user = User(
        username="user1",
        email="user1@example.com",
        password_hash="user_hash",
        full_name="Regular User",
        email_verified=True
    )
    
    session.add_all([admin_user, regular_user])
    session.commit()
    
    # Add roles to users
    admin_user.add_role(admin_role)
    regular_user.add_role(user_role)
    session.commit()
    
    return {
        "admin_user": admin_user,
        "regular_user": regular_user,
        "admin_role": admin_role,
        "user_role": user_role
    }

class TestDataIntegrity:
    """Test data integrity constraints and relationships."""
    
    def test_user_email_uniqueness(self, session):
        """Test that user email uniqueness is enforced."""
        # Create first user
        user1 = User(
            username="user1",
            email="test@example.com",
            password_hash="hash1"
        )
        session.add(user1)
        session.commit()
        
        # Try to create second user with same email
        user2 = User(
            username="user2",
            email="test@example.com",  # Same email
            password_hash="hash2"
        )
        session.add(user2)
        
        # Should raise integrity error
        with pytest.raises(IntegrityError):
            session.commit()
    
    def test_username_uniqueness(self, session):
        """Test that username uniqueness is enforced."""
        # Create first user
        user1 = User(
            username="testuser",
            email="test1@example.com",
            password_hash="hash1"
        )
        session.add(user1)
        session.commit()
        
        # Try to create second user with same username
        user2 = User(
            username="testuser",  # Same username
            email="test2@example.com",
            password_hash="hash2"
        )
        session.add(user2)
        
        # Should raise integrity error
        with pytest.raises(IntegrityError):
            session.commit()
    
    def test_role_name_uniqueness(self, session):
        """Test that role name uniqueness is enforced."""
        # Create first role
        role1 = Role(
            name="testrole",
            description="Test role 1",
            permissions={}
        )
        session.add(role1)
        session.commit()
        
        # Try to create second role with same name
        role2 = Role(
            name="testrole",  # Same name
            description="Test role 2",
            permissions={}
        )
        session.add(role2)
        
        # Should raise integrity error
        with pytest.raises(IntegrityError):
            session.commit()
    
    def test_foreign_key_constraints(self, session):
        """Test foreign key constraints."""
        # Try to create session with non-existent user
        session_obj = UserSession(
            user_id=uuid.uuid4(),  # Non-existent user ID
            token="test_token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        session.add(session_obj)
        
        # Should raise integrity error
        with pytest.raises(IntegrityError):
            session.commit()
    
    def test_cascade_delete(self, session, sample_data):
        """Test cascade delete behavior."""
        admin_user = sample_data["admin_user"]
        
        # Create API key for admin user
        api_key = APIKey(
            user_id=admin_user.id,
            name="Test API Key",
            key_hash="test_hash",
            key_prefix="test_",
            scopes=["read"]
        )
        session.add(api_key)
        session.commit()
        
        # Verify API key exists
        assert session.query(APIKey).filter_by(user_id=admin_user.id).count() == 1
        
        # Delete user
        session.delete(admin_user)
        session.commit()
        
        # Verify API key is also deleted (cascade)
        assert session.query(APIKey).filter_by(user_id=admin_user.id).count() == 0

class TestComplexQueries:
    """Test complex queries and joins."""
    
    def test_user_with_roles_query(self, session, sample_data):
        """Test querying users with their roles."""
        # Query users with roles
        users_with_roles = session.query(User).join(User.roles).all()
        
        # Verify all users have roles
        for user in users_with_roles:
            assert len(user.roles) > 0
    
    def test_active_sessions_query(self, session, sample_data):
        """Test querying active sessions."""
        admin_user = sample_data["admin_user"]
        
        # Create multiple sessions
        active_session = UserSession(
            user_id=admin_user.id,
            token="active_token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        expired_session = UserSession(
            user_id=admin_user.id,
            token="expired_token",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        
        session.add_all([active_session, expired_session])
        session.commit()
        
        # Query active sessions only
        active_sessions = session.query(UserSession).filter(
            UserSession.expires_at > datetime.now(timezone.utc)
        ).all()
        
        # Verify only active sessions are returned
        assert len(active_sessions) == 1
        assert active_sessions[0].token == "active_token"
    
    def test_knowledge_items_by_creator(self, session, sample_data):
        """Test querying knowledge items by creator."""
        admin_user = sample_data["admin_user"]
        regular_user = sample_data["regular_user"]
        
        # Create knowledge items
        admin_item = KnowledgeItem(
            title="Admin Item",
            content="Admin content",
            created_by=admin_user.id
        )
        
        user_item = KnowledgeItem(
            title="User Item",
            content="User content",
            created_by=regular_user.id
        )
        
        session.add_all([admin_item, user_item])
        session.commit()
        
        # Query items by creator
        admin_items = session.query(KnowledgeItem).filter_by(created_by=admin_user.id).all()
        user_items = session.query(KnowledgeItem).filter_by(created_by=regular_user.id).all()
        
        # Verify correct items are returned
        assert len(admin_items) == 1
        assert admin_items[0].title == "Admin Item"
        
        assert len(user_items) == 1
        assert user_items[0].title == "User Item"
    
    def test_audit_log_by_entity(self, session, sample_data):
        """Test querying audit logs by entity."""
        admin_user = sample_data["admin_user"]
        
        # Create audit logs
        audit_log1 = AuditLog(
            user_id=admin_user.id,
            action=AuditAction.CREATE,
            entity_type="User",
            entity_id=admin_user.id,
            new_values={"username": "admin"}
        )
        
        audit_log2 = AuditLog(
            user_id=admin_user.id,
            action=AuditAction.UPDATE,
            entity_type="User",
            entity_id=admin_user.id,
            old_values={"username": "admin"},
            new_values={"username": "admin_updated"}
        )
        
        session.add_all([audit_log1, audit_log2])
        session.commit()
        
        # Query audit logs by entity
        entity_logs = session.query(AuditLog).filter_by(
            entity_type="User",
            entity_id=admin_user.id
        ).order_by(AuditLog.created_at).all()
        
        # Verify correct logs are returned
        assert len(entity_logs) == 2
        assert entity_logs[0].action == AuditAction.CREATE
        assert entity_logs[1].action == AuditAction.UPDATE

class TestTransactionHandling:
    """Test transaction handling and rollback scenarios."""
    
    def test_transaction_rollback(self, session):
        """Test transaction rollback on error."""
        # Start transaction
        user1 = User(
            username="user1",
            email="user1@example.com",
            password_hash="hash1"
        )
        session.add(user1)
        session.commit()
        
        # Try to add invalid data
        user2 = User(
            username="user2",
            email="user1@example.com",  # Duplicate email
            password_hash="hash2"
        )
        session.add(user2)
        
        # Should fail and rollback
        with pytest.raises(IntegrityError):
            session.commit()
        
        # Verify first user still exists
        assert session.query(User).filter_by(username="user1").count() == 1
        assert session.query(User).filter_by(username="user2").count() == 0
    
    def test_nested_transactions(self, session):
        """Test nested transaction handling."""
        # Outer transaction
        user1 = User(
            username="user1",
            email="user1@example.com",
            password_hash="hash1"
        )
        session.add(user1)
        
        # Inner transaction (nested)
        try:
            user2 = User(
                username="user2",
                email="user2@example.com",
                password_hash="hash2"
            )
            session.add(user2)
            session.commit()  # Commit inner transaction
            
            # Try to add invalid data
            user3 = User(
                username="user3",
                email="user1@example.com",  # Duplicate email
                password_hash="hash3"
            )
            session.add(user3)
            session.commit()  # Should fail
            
        except IntegrityError:
            session.rollback()
        
        # Verify only valid data is committed
        assert session.query(User).filter_by(username="user1").count() == 1
        assert session.query(User).filter_by(username="user2").count() == 1
        assert session.query(User).filter_by(username="user3").count() == 0

class TestConcurrentAccess:
    """Test concurrent access scenarios."""
    
    def test_concurrent_user_creation(self, session):
        """Test concurrent user creation."""
        def create_user(username, email):
            """Create user in separate session."""
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=session.bind)
            local_session = SessionLocal()
            try:
                user = User(
                    username=username,
                    email=email,
                    password_hash="hash"
                )
                local_session.add(user)
                local_session.commit()
                return True
            except IntegrityError:
                local_session.rollback()
                return False
            finally:
                local_session.close()
        
        # Create users concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(create_user, f"user{i}", f"user{i}@example.com")
                for i in range(3)
            ]
            
            results = [future.result() for future in futures]
        
        # Verify all users were created successfully
        assert all(results)
        assert session.query(User).count() == 3
    
    def test_concurrent_session_creation(self, session, sample_data):
        """Test concurrent session creation for same user."""
        admin_user = sample_data["admin_user"]
        
        def create_session(token):
            """Create session in separate session."""
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=session.bind)
            local_session = SessionLocal()
            try:
                user_session = UserSession(
                    user_id=admin_user.id,
                    token=token,
                    expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
                )
                local_session.add(user_session)
                local_session.commit()
                return True
            except IntegrityError:
                local_session.rollback()
                return False
            finally:
                local_session.close()
        
        # Create sessions concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(create_session, f"token{i}")
                for i in range(3)
            ]
            
            results = [future.result() for future in futures]
        
        # Verify all sessions were created successfully
        assert all(results)
        assert session.query(UserSession).filter_by(user_id=admin_user.id).count() == 3

class TestPerformanceScenarios:
    """Test performance under various scenarios."""
    
    def test_bulk_insert_performance(self, session):
        """Test bulk insert performance."""
        import time
        
        # Create large dataset
        users = []
        for i in range(1000):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=f"hash{i}"
            )
            users.append(user)
        
        # Measure bulk insert time
        start_time = time.time()
        session.add_all(users)
        session.commit()
        end_time = time.time()
        
        # Verify performance (should complete in reasonable time)
        assert end_time - start_time < 10.0  # 10 seconds max
        assert session.query(User).count() == 1000
    
    def test_complex_query_performance(self, session, sample_data):
        """Test complex query performance."""
        import time
        
        admin_user = sample_data["admin_user"]
        
        # Create large dataset
        knowledge_items = []
        queries = []
        audit_logs = []
        
        for i in range(100):
            # Knowledge items
            item = KnowledgeItem(
                title=f"Item {i}",
                content=f"Content {i}",
                created_by=admin_user.id,
                tags=[f"tag{i}"]
            )
            knowledge_items.append(item)
            
            # Queries
            query = Query(
                user_id=admin_user.id,
                query_text=f"Query {i}",
                response_text=f"Response {i}",
                tokens_used=100 + i
            )
            queries.append(query)
            
            # Audit logs
            audit_log = AuditLog(
                user_id=admin_user.id,
                action=AuditAction.CREATE,
                entity_type="KnowledgeItem",
                entity_id=uuid.uuid4(),
                new_values={"title": f"Item {i}"}
            )
            audit_logs.append(audit_log)
        
        session.add_all(knowledge_items + queries + audit_logs)
        session.commit()
        
        # Measure complex query time
        start_time = time.time()
        
        # Complex query with joins
        result = session.query(
            User, KnowledgeItem, Query, AuditLog
        ).join(
            KnowledgeItem, User.id == KnowledgeItem.created_by
        ).join(
            Query, User.id == Query.user_id
        ).join(
            AuditLog, User.id == AuditLog.user_id
        ).filter(
            User.id == admin_user.id
        ).all()
        
        end_time = time.time()
        
        # Verify performance
        assert end_time - start_time < 5.0  # 5 seconds max
        assert len(result) > 0
    
    def test_index_usage_performance(self, session):
        """Test index usage performance."""
        import time
        
        # Create users with indexed fields
        users = []
        for i in range(1000):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=f"hash{i}",
                last_login_at=datetime.now(timezone.utc) - timedelta(days=i)
            )
            users.append(user)
        
        session.add_all(users)
        session.commit()
        
        # Measure indexed query performance
        start_time = time.time()
        
        # Query by indexed field
        result = session.query(User).filter(
            User.email.like("user%")
        ).order_by(User.last_login_at.desc()).limit(100).all()
        
        end_time = time.time()
        
        # Verify performance
        assert end_time - start_time < 2.0  # 2 seconds max
        assert len(result) == 100

class TestErrorHandling:
    """Test error handling and recovery scenarios."""
    
    def test_validation_error_handling(self, session):
        """Test validation error handling."""
        # Try to create user with invalid email
        user = User(
            username="testuser",
            email="invalid-email",  # Invalid email
            password_hash="hash"
        )
        session.add(user)
        
        # Should raise validation error
        with pytest.raises(ValueError):
            session.commit()
    
    def test_constraint_violation_handling(self, session):
        """Test constraint violation handling."""
        # Create user with valid data
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash"
        )
        session.add(user)
        session.commit()
        
        # Try to update with invalid data
        user.username = "ab"  # Too short
        
        # Should raise validation error
        with pytest.raises(ValueError):
            session.commit()
    
    def test_foreign_key_violation_handling(self, session):
        """Test foreign key violation handling."""
        # Try to create session with non-existent user
        user_session = UserSession(
            user_id=uuid.uuid4(),  # Non-existent user
            token="test_token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        session.add(user_session)
        
        # Should raise integrity error
        with pytest.raises(IntegrityError):
            session.commit()

class TestMigrationScenarios:
    """Test migration and schema change scenarios."""
    
    def test_data_migration_simulation(self, session):
        """Simulate data migration scenario."""
        # Create old format data
        users = []
        for i in range(100):
            user = User(
                username=f"olduser{i}",
                email=f"olduser{i}@example.com",
                password_hash=f"oldhash{i}",
                preferences={"old_format": True}
            )
            users.append(user)
        
        session.add_all(users)
        session.commit()
        
        # Simulate migration to new format
        for user in session.query(User).all():
            if user.preferences.get("old_format"):
                user.preferences = {
                    "new_format": True,
                    "migrated_at": datetime.now(timezone.utc).isoformat()
                }
        
        session.commit()
        
        # Verify migration
        migrated_users = session.query(User).filter(
            User.preferences.contains({"new_format": True})
        ).count()
        
        assert migrated_users == 100
    
    def test_schema_evolution_simulation(self, session):
        """Simulate schema evolution scenario."""
        # Create data with current schema
        users = []
        for i in range(50):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=f"hash{i}",
                metadata_json={"version": "1.0"}
            )
            users.append(user)
        
        session.add_all(users)
        session.commit()
        
        # Simulate schema evolution
        for user in session.query(User).all():
            metadata = user.metadata_json or {}
            metadata["schema_version"] = "2.0"
            metadata["upgraded_at"] = datetime.now(timezone.utc).isoformat()
            user.metadata_json = metadata
        
        session.commit()
        
        # Verify schema evolution
        upgraded_users = session.query(User).filter(
            User.metadata_json.contains({"schema_version": "2.0"})
        ).count()
        
        assert upgraded_users == 50

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 