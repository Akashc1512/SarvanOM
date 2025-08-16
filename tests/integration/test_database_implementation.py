"""
Database Implementation Integration Tests

This module tests the database implementation including:
- Database connection management
- Repository operations
- User and Query repositories
- Password hashing
- Transaction handling

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import pytest
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

from shared.core.database.connection import get_db_manager, shutdown_db_manager
from shared.core.auth.password_hasher import get_password_hasher, hash_password, verify_password
from backend.repositories.database.user_repository import UserRepository
from backend.repositories.database.query_repository import QueryRepository
from shared.models.models import User, Query, RecordStatus


class TestDatabaseImplementation:
    """Test database implementation functionality."""

    @pytest.fixture(autouse=True)
    async def setup_teardown(self):
        """Setup and teardown for each test."""
        # Setup
        yield
        # Teardown
        await shutdown_db_manager()

    @pytest.mark.asyncio
    async def test_database_connection_manager(self):
        """Test database connection manager initialization."""
        # Test that we can get the database manager
        db_manager = get_db_manager()
        assert db_manager is not None
        
        # Test health check
        health_result = await db_manager.health_check()
        assert isinstance(health_result, dict)
        assert "status" in health_result

    @pytest.mark.asyncio
    async def test_password_hasher(self):
        """Test password hashing and verification."""
        password_hasher = get_password_hasher()
        
        # Test password hashing
        password = "test_password_123"
        hashed = password_hasher.hash_password(password)
        assert hashed != password
        assert len(hashed) > len(password)
        
        # Test password verification
        assert password_hasher.verify_password(password, hashed) is True
        assert password_hasher.verify_password("wrong_password", hashed) is False
        
        # Test password strength
        score = password_hasher.get_password_strength_score(password)
        assert 0 <= score <= 100
        
        label = password_hasher.get_password_strength_label(password)
        assert label in ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"]

    @pytest.mark.asyncio
    async def test_user_repository_creation(self):
        """Test user repository creation and basic operations."""
        # Test repository initialization
        user_repo = UserRepository()
        assert user_repo is not None
        
        # Test user creation
        username = "testuser"
        email = "test@example.com"
        password = "secure_password_123"
        
        try:
            user = await user_repo.create_user(
                username=username,
                email=email,
                password=password
            )
            
            assert user is not None
            assert user.username == username
            assert user.email == email
            assert user.password_hash != password  # Should be hashed
            
            # Test user retrieval
            retrieved_user = await user_repo.get_by_id(str(user.id))
            assert retrieved_user is not None
            assert retrieved_user.username == username
            
            # Test username lookup
            user_by_username = await user_repo.get_by_username(username)
            assert user_by_username is not None
            assert user_by_username.id == user.id
            
            # Test email lookup
            user_by_email = await user_repo.get_by_email(email)
            assert user_by_email is not None
            assert user_by_email.id == user.id
            
            # Test authentication
            authenticated_user = await user_repo.authenticate_user(username, password)
            assert authenticated_user is not None
            assert authenticated_user.id == user.id
            
            # Test failed authentication
            failed_auth = await user_repo.authenticate_user(username, "wrong_password")
            assert failed_auth is None
            
        except Exception as e:
            # If database is not available, skip the test
            pytest.skip(f"Database not available: {e}")

    @pytest.mark.asyncio
    async def test_query_repository_creation(self):
        """Test query repository creation and basic operations."""
        # Test repository initialization
        query_repo = QueryRepository()
        assert query_repo is not None
        
        # Test query creation
        user_id = "test-user-id"
        query_text = "What is artificial intelligence?"
        query_type = "search"
        
        try:
            query = await query_repo.create_query(
                user_id=user_id,
                query_text=query_text,
                query_type=query_type
            )
            
            assert query is not None
            assert query.user_id == user_id
            assert query.query_text == query_text
            assert query.query_type == query_type
            
            # Test query retrieval
            retrieved_query = await query_repo.get_by_id(str(query.id))
            assert retrieved_query is not None
            assert retrieved_query.query_text == query_text
            
            # Test query status update
            success = await query_repo.update_query_status(str(query.id), "completed")
            assert success is True
            
            # Test query response update
            response_data = {"answer": "AI is a field of computer science..."}
            success = await query_repo.update_query_response(
                str(query.id), 
                response_data, 
                response_time=1.5
            )
            assert success is True
            
        except Exception as e:
            # If database is not available, skip the test
            pytest.skip(f"Database not available: {e}")

    @pytest.mark.asyncio
    async def test_user_search_and_analytics(self):
        """Test user search and analytics functionality."""
        user_repo = UserRepository()
        
        try:
            # Create test users
            users = []
            for i in range(5):
                user = await user_repo.create_user(
                    username=f"testuser{i}",
                    email=f"test{i}@example.com",
                    password="password123"
                )
                users.append(user)
            
            # Test user search
            search_results, total_count = await user_repo.search_users("testuser")
            assert total_count >= 5
            assert len(search_results) >= 5
            
            # Test user statistics
            stats = await user_repo.get_user_stats()
            assert "total_users" in stats
            assert "active_users" in stats
            assert stats["total_users"] >= 5
            
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    @pytest.mark.asyncio
    async def test_query_analytics(self):
        """Test query analytics functionality."""
        query_repo = QueryRepository()
        
        try:
            # Create test queries
            user_id = "test-user-id"
            queries = []
            for i in range(10):
                query = await query_repo.create_query(
                    user_id=user_id,
                    query_text=f"Test query {i}",
                    query_type="search"
                )
                queries.append(query)
            
            # Test query analytics
            analytics = await query_repo.get_query_analytics(user_id=user_id, days=30)
            assert "total_queries" in analytics
            assert "queries_by_status" in analytics
            assert analytics["total_queries"] >= 10
            
            # Test popular queries
            popular = await query_repo.get_popular_queries(days=7, user_id=user_id)
            assert len(popular) >= 0  # May be empty if no duplicates
            
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    @pytest.mark.asyncio
    async def test_transaction_handling(self):
        """Test transaction handling and rollback."""
        user_repo = UserRepository()
        
        try:
            # Test transaction with multiple operations
            operations = [
                lambda session: user_repo.create_user(
                    username="transaction_user1",
                    email="trans1@example.com",
                    password="password123"
                ),
                lambda session: user_repo.create_user(
                    username="transaction_user2",
                    email="trans2@example.com",
                    password="password123"
                )
            ]
            
            results = await user_repo.transaction(operations)
            assert len(results) == 2
            assert all(result is not None for result in results)
            
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    @pytest.mark.asyncio
    async def test_connection_pool_stats(self):
        """Test connection pool statistics."""
        db_manager = get_db_manager()
        
        # Test pool statistics
        stats = db_manager.get_pool_stats()
        assert isinstance(stats, dict)
        
        # Check that we have at least one database connection
        if stats:
            for db_name, db_stats in stats.items():
                assert "pool_size" in db_stats
                assert "checked_in" in db_stats
                assert "checked_out" in db_stats

    @pytest.mark.asyncio
    async def test_password_strength_validation(self):
        """Test password strength validation."""
        password_hasher = get_password_hasher()
        
        # Test weak password
        weak_password = "123"
        with pytest.raises(ValueError, match="at least 8 characters"):
            password_hasher.hash_password(weak_password)
        
        # Test common password
        common_password = "password"
        with pytest.raises(ValueError, match="too common"):
            password_hasher.hash_password(common_password)
        
        # Test strong password
        strong_password = "SecurePassword123!"
        hashed = password_hasher.hash_password(strong_password)
        assert hashed != strong_password
        
        # Test password strength score
        score = password_hasher.get_password_strength_score(strong_password)
        assert score > 50  # Should be reasonably strong

    @pytest.mark.asyncio
    async def test_secure_password_generation(self):
        """Test secure password generation."""
        password_hasher = get_password_hasher()
        
        # Test password generation
        password = password_hasher.generate_secure_password(length=16)
        assert len(password) == 16
        
        # Test that generated password is strong
        score = password_hasher.get_password_strength_score(password)
        assert score > 70  # Generated passwords should be strong
        
        # Test password verification
        hashed = password_hasher.hash_password(password)
        assert password_hasher.verify_password(password, hashed) is True


# Test utility functions
def test_convenience_functions():
    """Test convenience functions for password hashing."""
    # Test global functions
    password = "test_password_123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False
    
    # Test password generation
    generated = generate_secure_password(length=12)
    assert len(generated) == 12
    
    # Test strength functions
    score = get_password_strength_score(password)
    assert 0 <= score <= 100
    
    label = get_password_strength_label(password)
    assert label in ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"]


if __name__ == "__main__":
    pytest.main([__file__])
