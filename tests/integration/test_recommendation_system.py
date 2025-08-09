"""
Integration tests for recommendation system.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch
from typing import List, Dict, Any

# Import the actual classes we're testing
from services.synthesis_service.recommendation_service import (
    RecommendationService,
    Recommendation,
)


class TestRecommendationService:
    """Test recommendation service functionality."""

    @pytest.fixture
    async def recommendation_service(self):
        """Create mock recommendation service."""
        service = RecommendationService()
        return service

    @pytest.fixture
    def mock_arangodb_client(self):
        """Create mock ArangoDB client."""
        client = Mock()
        client.connected = True
        return client

    @pytest.mark.asyncio
    async def test_get_recommendations(self, recommendation_service):
        """Test getting recommendations."""
        # Mock the knowledge graph query
        mock_entities = [
            {
                "id": "entity_1",
                "title": "Machine Learning",
                "content": "A subset of artificial intelligence",
                "confidence": 0.8,
                "source": "knowledge_graph",
                "metadata": {"type": "technology"},
            },
            {
                "id": "entity_2",
                "title": "Deep Learning",
                "content": "A subset of machine learning",
                "confidence": 0.7,
                "source": "knowledge_graph",
                "metadata": {"type": "technology"},
            },
        ]

        with patch.object(
            recommendation_service.knowledge_graph, "query_knowledge_graph"
        ) as mock_query:
            mock_query.return_value.entities = mock_entities

            recommendations = await recommendation_service.get_recommendations(
                query="machine learning", max_recommendations=5
            )

            assert len(recommendations) == 2
            assert recommendations[0].title == "Machine Learning"
            assert recommendations[0].confidence == 0.8
            assert recommendations[1].title == "Deep Learning"
            assert recommendations[1].confidence == 0.7

    @pytest.mark.asyncio
    async def test_get_related_concepts(self, recommendation_service):
        """Test getting related concepts."""
        mock_entities = [
            {
                "id": "related_1",
                "title": "Neural Networks",
                "content": "Computing systems inspired by biological neural networks",
                "confidence": 0.7,
                "source": "knowledge_graph",
                "metadata": {
                    "relationship_type": "enables",
                    "source_entity": "Deep Learning",
                    "target_entity": "Neural Networks",
                },
            }
        ]

        with patch.object(
            recommendation_service.knowledge_graph, "query_knowledge_graph"
        ) as mock_query:
            mock_query.return_value.entities = mock_entities

            related = await recommendation_service.get_related_concepts(
                concept_id="deep_learning", max_related=3
            )

            assert len(related) == 1
            assert related[0].title == "Neural Networks"
            assert related[0].metadata["relationship_type"] == "enables"

    @pytest.mark.asyncio
    async def test_get_trending_topics(self, recommendation_service):
        """Test getting trending topics."""
        mock_entities = [
            {
                "id": "trending_1",
                "title": "Artificial Intelligence",
                "content": "The simulation of human intelligence by machines",
                "confidence": 0.9,
                "source": "knowledge_graph",
                "metadata": {"popularity": 95, "type": "technology"},
            }
        ]

        with patch.object(
            recommendation_service.knowledge_graph, "query_knowledge_graph"
        ) as mock_query:
            mock_query.return_value.entities = mock_entities

            trending = await recommendation_service.get_trending_topics(max_topics=5)

            assert len(trending) == 1
            assert trending[0].title == "Artificial Intelligence"
            assert trending[0].confidence == 0.9
            assert trending[0].metadata["popularity"] == 95

    @pytest.mark.asyncio
    async def test_get_recommendations_empty_result(self, recommendation_service):
        """Test getting recommendations when no results are found."""
        with patch.object(
            recommendation_service.knowledge_graph, "query_knowledge_graph"
        ) as mock_query:
            mock_query.return_value.entities = []

            recommendations = await recommendation_service.get_recommendations(
                query="nonexistent query", max_recommendations=5
            )

            assert len(recommendations) == 0

    @pytest.mark.asyncio
    async def test_get_recommendations_exception_handling(self, recommendation_service):
        """Test exception handling in recommendation service."""
        with patch.object(
            recommendation_service.knowledge_graph, "query_knowledge_graph"
        ) as mock_query:
            mock_query.side_effect = Exception("Database connection failed")

            recommendations = await recommendation_service.get_recommendations(
                query="test query", max_recommendations=5
            )

            assert len(recommendations) == 0

    @pytest.mark.asyncio
    async def test_health_status(self, recommendation_service):
        """Test health status of recommendation service."""
        with patch.object(recommendation_service.knowledge_graph, "connected", True):
            with patch.object(
                recommendation_service.knowledge_graph, "get_health_status"
            ) as mock_health:
                mock_health.return_value = {
                    "status": "healthy",
                    "database_type": "arangodb",
                }

                health = await recommendation_service.get_health_status()

                assert health["status"] == "healthy"
                assert health["service_type"] == "recommendation"
                assert "knowledge_graph_status" in health


class TestRecommendation:
    """Test Recommendation dataclass."""

    def test_recommendation_creation(self):
        """Test creating a recommendation object."""
        recommendation = Recommendation(
            id="test_id",
            title="Test Title",
            content="Test content for recommendation",
            confidence=0.85,
            source="knowledge_graph",
            metadata={"type": "technology", "category": "AI"},
        )

        assert recommendation.id == "test_id"
        assert recommendation.title == "Test Title"
        assert recommendation.content == "Test content for recommendation"
        assert recommendation.confidence == 0.85
        assert recommendation.source == "knowledge_graph"
        assert recommendation.metadata["type"] == "technology"
        assert recommendation.metadata["category"] == "AI"

    def test_recommendation_defaults(self):
        """Test recommendation with minimal parameters."""
        recommendation = Recommendation(
            id="minimal_id",
            title="Minimal Title",
            content="Minimal content",
            confidence=0.5,
            source="test_source",
            metadata={},
        )

        assert recommendation.id == "minimal_id"
        assert recommendation.title == "Minimal Title"
        assert recommendation.content == "Minimal content"
        assert recommendation.confidence == 0.5
        assert recommendation.source == "test_source"
        assert recommendation.metadata == {}


@pytest.mark.asyncio
async def test_integration_recommendation_flow():
    """Test complete recommendation flow integration."""
    # This test would require a real ArangoDB instance
    # For now, we'll test with mocked components

    service = RecommendationService()

    # Mock the entire knowledge graph
    with patch.object(service.knowledge_graph, "connected", True):
        with patch.object(
            service.knowledge_graph, "query_knowledge_graph"
        ) as mock_query:
            # Mock successful query response
            mock_query.return_value.entities = [
                {
                    "id": "ai_1",
                    "title": "Artificial Intelligence",
                    "content": "The simulation of human intelligence by machines",
                    "confidence": 0.9,
                    "source": "knowledge_graph",
                    "metadata": {"type": "technology", "category": "AI"},
                }
            ]

            # Test the complete flow
            recommendations = await service.get_recommendations(
                query="artificial intelligence", max_recommendations=3
            )

            assert len(recommendations) == 1
            assert recommendations[0].title == "Artificial Intelligence"
            assert recommendations[0].confidence == 0.9
            assert recommendations[0].source == "knowledge_graph"


if __name__ == "__main__":
    pytest.main([__file__])
