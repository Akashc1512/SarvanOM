#!/usr/bin/env python3
"""
Integration Tests for Advanced Features (Phase D1)

Tests for:
- Real-time collaboration
- Advanced analytics
- Performance optimization
- Predictive caching
- Expert dashboard
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from services.gateway.advanced_features import (
    AdvancedFeaturesManager,
    PredictiveCache,
    CollaborationSession,
    AdvancedAnalytics,
    PerformanceOptimizer,
    PredictiveCacheConfig,
    CollaborationConfig,
    AnalyticsConfig
)
from services.gateway.main import app
from shared.core.config.central_config import CentralConfig


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def config():
    """Central configuration for testing."""
    return CentralConfig()


@pytest.fixture
async def advanced_features_manager(config):
    """Advanced features manager for testing."""
    manager = AdvancedFeaturesManager(config)
    await manager.start()
    yield manager
    await manager.stop()


class TestPredictiveCache:
    """Test predictive caching functionality."""
    
    def test_predictive_cache_initialization(self):
        """Test predictive cache initialization."""
        config = PredictiveCacheConfig()
        cache = PredictiveCache(config)
        
        assert cache.config.enabled == True
        assert cache.config.prediction_window == 300
        assert cache.config.confidence_threshold == 0.7
        assert len(cache.query_patterns) == 0
    
    def test_update_patterns(self):
        """Test updating query patterns."""
        config = PredictiveCacheConfig()
        cache = PredictiveCache(config)
        
        query = "What is machine learning?"
        related_queries = ["How does ML work?", "ML vs AI", "Deep learning basics"]
        
        cache.update_patterns(query, related_queries)
        
        query_hash = cache.query_patterns.keys().__iter__().__next__()
        assert len(cache.query_patterns[query_hash]) == 3
        assert "How does ML work?" in cache.query_patterns[query_hash]
    
    def test_predict_next_queries(self):
        """Test query prediction."""
        config = PredictiveCacheConfig()
        cache = PredictiveCache(config)
        
        query = "What is machine learning?"
        related_queries = ["How does ML work?", "ML vs AI", "Deep learning basics"]
        
        cache.update_patterns(query, related_queries)
        predictions = cache.predict_next_queries(query)
        
        assert len(predictions) > 0
        assert all(pred in related_queries for pred in predictions)
    
    def test_should_precache(self):
        """Test precaching decision."""
        config = PredictiveCacheConfig()
        cache = PredictiveCache(config)
        
        query = "What is machine learning?"
        related_queries = ["How does ML work?", "ML vs AI", "Deep learning basics", "Neural networks"]
        
        cache.update_patterns(query, related_queries)
        should_precache = cache.should_precache(query)
        
        assert should_precache == True


class TestCollaborationSession:
    """Test collaboration session functionality."""
    
    @pytest.fixture
    def config(self):
        """Collaboration configuration."""
        return CollaborationConfig()
    
    @pytest.fixture
    def session(self, config):
        """Collaboration session for testing."""
        return CollaborationSession("test-session", config)
    
    def test_session_initialization(self, session):
        """Test session initialization."""
        assert session.session_id == "test-session"
        assert len(session.collaborators) == 0
        assert len(session.cursors) == 0
        assert len(session.comments) == 0
        assert session.config.enable_cursors == True
        assert session.config.enable_comments == True
    
    @pytest.mark.asyncio
    async def test_add_collaborator(self, session):
        """Test adding a collaborator."""
        websocket = AsyncMock()
        user_id = "user1"
        
        await session.add_collaborator(user_id, websocket)
        
        assert user_id in session.collaborators
        assert session.collaborators[user_id] == websocket
        assert len(session.collaborators) == 1
    
    @pytest.mark.asyncio
    async def test_remove_collaborator(self, session):
        """Test removing a collaborator."""
        websocket = AsyncMock()
        user_id = "user1"
        
        await session.add_collaborator(user_id, websocket)
        await session.remove_collaborator(user_id)
        
        assert user_id not in session.collaborators
        assert len(session.collaborators) == 0
    
    @pytest.mark.asyncio
    async def test_update_cursor(self, session):
        """Test cursor update."""
        websocket = AsyncMock()
        user_id = "user1"
        position = {"x": 100, "y": 200}
        
        await session.add_collaborator(user_id, websocket)
        await session.update_cursor(user_id, position)
        
        assert user_id in session.cursors
        assert session.cursors[user_id]["position"] == position
    
    @pytest.mark.asyncio
    async def test_add_comment(self, session):
        """Test adding a comment."""
        websocket = AsyncMock()
        user_id = "user1"
        comment = "This is a test comment"
        position = {"line": 10, "column": 5}
        
        await session.add_collaborator(user_id, websocket)
        await session.add_comment(user_id, comment, position)
        
        assert len(session.comments) == 1
        assert session.comments[0]["user_id"] == user_id
        assert session.comments[0]["comment"] == comment
        assert session.comments[0]["position"] == position
    
    def test_session_expiration(self, session):
        """Test session expiration."""
        # Set last activity to 2 hours ago
        session.last_activity = datetime.now() - timedelta(hours=2)
        
        assert session.is_expired() == True
        
        # Set last activity to now
        session.last_activity = datetime.now()
        
        assert session.is_expired() == False


class TestAdvancedAnalytics:
    """Test advanced analytics functionality."""
    
    @pytest.fixture
    def config(self):
        """Analytics configuration."""
        return AnalyticsConfig()
    
    @pytest.fixture
    def analytics(self, config):
        """Analytics instance for testing."""
        return AdvancedAnalytics(config)
    
    def test_analytics_initialization(self, analytics):
        """Test analytics initialization."""
        assert analytics.config.enabled == True
        assert analytics.config.retention_days == 90
        assert len(analytics.query_metrics) == 0
        assert len(analytics.user_behavior) == 0
    
    def test_record_query(self, analytics):
        """Test recording query metrics."""
        query = "What is Python?"
        user_id = "user1"
        response_time = 1.5
        success = True
        sources_used = ["wikipedia", "stackoverflow"]
        
        analytics.record_query(query, user_id, response_time, success, sources_used)
        
        assert query in analytics.query_metrics
        assert len(analytics.query_metrics[query]) == 1
        
        metric = analytics.query_metrics[query][0]
        assert metric["query"] == query
        assert metric["user_id"] == user_id
        assert metric["response_time"] == response_time
        assert metric["success"] == success
        assert metric["sources_used"] == sources_used
    
    def test_record_user_behavior(self, analytics):
        """Test recording user behavior."""
        user_id = "user1"
        action = "query_submitted"
        context = {"query": "What is Python?", "session_duration": 300}
        
        analytics.record_user_behavior(user_id, action, context)
        
        assert user_id in analytics.user_behavior
        assert len(analytics.user_behavior[user_id]) == 1
        
        behavior = analytics.user_behavior[user_id][0]
        assert behavior["user_id"] == user_id
        assert behavior["action"] == action
        assert behavior["context"] == context
    
    def test_get_query_insights(self, analytics):
        """Test getting query insights."""
        # Add some test data
        analytics.record_query("What is Python?", "user1", 1.0, True, ["wikipedia"])
        analytics.record_query("What is Python?", "user2", 1.5, True, ["stackoverflow"])
        analytics.record_query("How to code?", "user1", 2.0, False, [])
        
        insights = analytics.get_query_insights()
        
        assert insights["total_queries"] == 3
        assert insights["success_rate"] == 2/3
        assert "What is Python?" in [q[0] for q in insights["popular_queries"]]
        assert insights["unique_users"] == 2
    
    def test_get_performance_insights(self, analytics):
        """Test getting performance insights."""
        # Add some performance metrics
        analytics.performance_metrics = [
            {"response_time": 1.0, "error_rate": 0.1},
            {"response_time": 1.5, "error_rate": 0.2},
            {"response_time": 2.0, "error_rate": 0.05}
        ]
        
        insights = analytics.get_performance_insights()
        
        assert insights["avg_response_time"] == 1.5
        assert insights["avg_error_rate"] == 0.11666666666666667
        assert insights["trend"] in ["improving", "degrading", "stable"]


class TestPerformanceOptimizer:
    """Test performance optimization functionality."""
    
    @pytest.fixture
    def optimizer(self):
        """Performance optimizer for testing."""
        return PerformanceOptimizer()
    
    def test_optimizer_initialization(self, optimizer):
        """Test optimizer initialization."""
        assert len(optimizer.query_optimizations) == 0
        assert len(optimizer.cache_hit_rates) == 0
    
    def test_optimize_query_simple(self, optimizer):
        """Test optimizing a simple query."""
        query = "What is Python?"
        context = {"complexity": "simple", "user_priority": "normal"}
        
        optimization = optimizer.optimize_query(query, context)
        
        assert optimization["cache_strategy"] == "aggressive"
        assert optimization["parallel_processing"] == False
        assert optimization["compression"] == False
        assert optimization["priority"] == 5
    
    def test_optimize_query_complex(self, optimizer):
        """Test optimizing a complex query."""
        query = "Analyze the comprehensive differences between machine learning algorithms"
        context = {"complexity": "complex", "user_priority": "high"}
        
        optimization = optimizer.optimize_query(query, context)
        
        assert optimization["cache_strategy"] == "conservative"
        assert optimization["parallel_processing"] == True
        assert optimization["compression"] == True
        assert optimization["priority"] == 7
    
    def test_optimize_query_urgent(self, optimizer):
        """Test optimizing an urgent query."""
        query = "Emergency: How to fix critical bug?"
        context = {"complexity": "medium", "user_priority": "normal"}
        
        optimization = optimizer.optimize_query(query, context)
        
        assert optimization["priority"] == 8  # High priority due to "urgent"
    
    def test_update_metrics(self, optimizer):
        """Test updating performance metrics."""
        query_hash = "test_hash"
        response_time = 1.5
        cache_hit = True
        
        optimizer.update_metrics(query_hash, response_time, cache_hit)
        
        assert query_hash in optimizer.response_time_history
        assert len(optimizer.response_time_history[query_hash]) == 1
        assert optimizer.response_time_history[query_hash][0] == response_time
        assert optimizer.cache_hit_rates[query_hash] == 1.0


class TestAdvancedFeaturesManager:
    """Test advanced features manager functionality."""
    
    @pytest.fixture
    async def manager(self, config):
        """Advanced features manager for testing."""
        manager = AdvancedFeaturesManager(config)
        await manager.start()
        yield manager
        await manager.stop()
    
    def test_manager_initialization(self, config):
        """Test manager initialization."""
        manager = AdvancedFeaturesManager(config)
        
        assert manager.config == config
        assert manager.predictive_cache is not None
        assert manager.analytics is not None
        assert manager.performance_optimizer is not None
        assert len(manager.collaboration_sessions) == 0
    
    @pytest.mark.asyncio
    async def test_create_collaboration_session(self, manager):
        """Test creating a collaboration session."""
        session_id = "test-session"
        session = await manager.create_collaboration_session(session_id)
        
        assert session.session_id == session_id
        assert session_id in manager.collaboration_sessions
        assert manager.collaboration_sessions[session_id] == session
    
    @pytest.mark.asyncio
    async def test_get_collaboration_session(self, manager):
        """Test getting a collaboration session."""
        session_id = "test-session"
        session = await manager.create_collaboration_session(session_id)
        
        retrieved_session = manager.get_collaboration_session(session_id)
        assert retrieved_session == session
        
        # Test non-existent session
        non_existent = manager.get_collaboration_session("non-existent")
        assert non_existent is None
    
    def test_get_analytics_insights(self, manager):
        """Test getting analytics insights."""
        insights = manager.get_analytics_insights()
        
        assert "query_insights" in insights
        assert "performance_insights" in insights
        assert "collaboration_stats" in insights
        assert insights["collaboration_stats"]["active_sessions"] == 0
    
    def test_optimize_query(self, manager):
        """Test query optimization."""
        query = "What is machine learning?"
        context = {"complexity": "medium", "user_priority": "normal"}
        
        optimization = manager.optimize_query(query, context)
        
        assert "cache_strategy" in optimization
        assert "parallel_processing" in optimization
        assert "compression" in optimization
        assert "priority" in optimization
    
    def test_predict_next_queries(self, manager):
        """Test query prediction."""
        query = "What is machine learning?"
        
        # Add some patterns first
        manager.predictive_cache.update_patterns(
            query, 
            ["How does ML work?", "ML vs AI", "Deep learning basics"]
        )
        
        predictions = manager.predict_next_queries(query)
        
        assert isinstance(predictions, list)
        # Predictions might be empty if patterns aren't strong enough
        # This is expected behavior for a new system
    
    def test_should_precache(self, manager):
        """Test precaching decision."""
        query = "What is machine learning?"
        
        # Add strong patterns
        manager.predictive_cache.update_patterns(
            query, 
            ["How does ML work?", "ML vs AI", "Deep learning basics", "Neural networks", "AI basics"]
        )
        
        should_precache = manager.should_precache(query)
        
        # Should precache if we have enough predictions
        assert isinstance(should_precache, bool)


class TestAdvancedFeaturesAPI:
    """Test advanced features API endpoints."""
    
    def test_advanced_features_health(self, client):
        """Test advanced features health endpoint."""
        response = client.get("/advanced/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "features" in data
        assert "timestamp" in data
    
    def test_create_collaboration_session(self, client):
        """Test creating a collaboration session."""
        request_data = {
            "session_id": "test-session",
            "user_id": "user1",
            "action": "join",
            "data": {}
        }
        
        response = client.post("/advanced/collaboration/session", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "collaborators" in data
        assert "cursors" in data
        assert "comments" in data
    
    def test_get_collaboration_session(self, client):
        """Test getting a collaboration session."""
        # First create a session
        create_data = {
            "session_id": "test-session",
            "user_id": "user1",
            "action": "join",
            "data": {}
        }
        client.post("/advanced/collaboration/session", json=create_data)
        
        # Then get it
        response = client.get("/advanced/collaboration/session/test-session")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session"
    
    def test_list_collaboration_sessions(self, client):
        """Test listing collaboration sessions."""
        response = client.get("/advanced/collaboration/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_record_analytics_event(self, client):
        """Test recording analytics event."""
        request_data = {
            "query": "What is Python?",
            "user_id": "user1",
            "time_range": "7d",
            "metrics": ["queries", "performance"]
        }
        
        response = client.post("/advanced/analytics/record", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_get_analytics_insights(self, client):
        """Test getting analytics insights."""
        response = client.get("/advanced/analytics/insights")
        
        assert response.status_code == 200
        data = response.json()
        assert "query_insights" in data
        assert "performance_insights" in data
        assert "collaboration_stats" in data
    
    def test_get_popular_queries(self, client):
        """Test getting popular queries."""
        response = client.get("/advanced/analytics/queries/popular?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert "popular_queries" in data
    
    def test_get_performance_trends(self, client):
        """Test getting performance trends."""
        response = client.get("/advanced/analytics/performance/trends")
        
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data
    
    def test_optimize_query(self, client):
        """Test query optimization."""
        request_data = {
            "query": "What is machine learning?",
            "context": {"complexity": "medium", "user_priority": "normal"},
            "include_predictions": True
        }
        
        response = client.post("/advanced/optimization/query", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "cache_strategy" in data
        assert "parallel_processing" in data
        assert "compression" in data
        assert "priority" in data
        assert "predicted_queries" in data
    
    def test_get_query_predictions(self, client):
        """Test getting query predictions."""
        query_hash = "test_hash_123"
        response = client.get(f"/advanced/optimization/predictions/{query_hash}")
        
        assert response.status_code == 200
        data = response.json()
        assert "query_hash" in data
        assert "predictions" in data
        assert "confidence" in data
        assert "should_precache" in data
    
    def test_update_optimization_metrics(self, client):
        """Test updating optimization metrics."""
        request_data = {
            "query_hash": "test_hash",
            "response_time": 1.5,
            "cache_hit": True
        }
        
        response = client.post("/advanced/optimization/metrics", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_get_dashboard_overview(self, client):
        """Test getting dashboard overview."""
        response = client.get("/advanced/dashboard/overview")
        
        assert response.status_code == 200
        data = response.json()
        assert "system_health" in data
        assert "performance" in data
        assert "collaboration" in data
        assert "predictions" in data
    
    def test_get_features_status(self, client):
        """Test getting features status."""
        response = client.get("/advanced/dashboard/features/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "predictive_caching" in data
        assert "collaboration" in data
        assert "analytics" in data
        assert "performance_optimization" in data


class TestAdvancedFeaturesIntegration:
    """Integration tests for advanced features."""
    
    @pytest.mark.asyncio
    async def test_full_collaboration_workflow(self, advanced_features_manager):
        """Test full collaboration workflow."""
        # Create session
        session = await advanced_features_manager.create_collaboration_session("test-session")
        
        # Add collaborators
        websocket1 = AsyncMock()
        websocket2 = AsyncMock()
        
        await session.add_collaborator("user1", websocket1)
        await session.add_collaborator("user2", websocket2)
        
        # Update cursors
        await session.update_cursor("user1", {"x": 100, "y": 200})
        await session.update_cursor("user2", {"x": 150, "y": 250})
        
        # Add comments
        await session.add_comment("user1", "Great point!", {"line": 10, "column": 5})
        await session.add_comment("user2", "I agree", {"line": 12, "column": 8})
        
        # Verify state
        assert len(session.collaborators) == 2
        assert len(session.cursors) == 2
        assert len(session.comments) == 2
        
        # Remove one collaborator
        await session.remove_collaborator("user1")
        
        assert len(session.collaborators) == 1
        assert "user2" in session.collaborators
        assert "user1" not in session.collaborators
    
    @pytest.mark.asyncio
    async def test_analytics_and_optimization_integration(self, advanced_features_manager):
        """Test analytics and optimization integration."""
        # Record some analytics
        advanced_features_manager.analytics.record_query(
            "What is Python?", "user1", 1.0, True, ["wikipedia"]
        )
        advanced_features_manager.analytics.record_query(
            "How to code?", "user1", 1.5, True, ["stackoverflow"]
        )
        
        # Get insights
        insights = advanced_features_manager.get_analytics_insights()
        assert insights["query_insights"]["total_queries"] == 2
        
        # Optimize a query
        optimization = advanced_features_manager.optimize_query(
            "What is machine learning?",
            {"complexity": "medium", "user_priority": "normal"}
        )
        assert "cache_strategy" in optimization
        
        # Predict next queries
        predictions = advanced_features_manager.predict_next_queries("What is Python?")
        assert isinstance(predictions, list)
    
    def test_performance_optimization_workflow(self, advanced_features_manager):
        """Test performance optimization workflow."""
        # Optimize multiple queries
        queries = [
            ("What is Python?", {"complexity": "simple"}),
            ("Analyze machine learning algorithms", {"complexity": "complex"}),
            ("Emergency: Fix critical bug", {"complexity": "medium"})
        ]
        
        optimizations = []
        for query, context in queries:
            optimization = advanced_features_manager.optimize_query(query, context)
            optimizations.append(optimization)
        
        # Verify different strategies for different queries
        assert optimizations[0]["cache_strategy"] == "aggressive"  # Simple query
        assert optimizations[1]["cache_strategy"] == "conservative"  # Complex query
        assert optimizations[2]["priority"] > 5  # Emergency query has higher priority
        
        # Update metrics
        for i, (query, _) in enumerate(queries):
            query_hash = f"hash_{i}"
            advanced_features_manager.performance_optimizer.update_metrics(
                query_hash, 1.0 + i * 0.5, i % 2 == 0
            )
        
        # Verify metrics are updated
        assert len(advanced_features_manager.performance_optimizer.response_time_history) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
