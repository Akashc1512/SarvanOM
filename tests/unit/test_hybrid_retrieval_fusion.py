#!/usr/bin/env python3
"""
Unit tests for hybrid retrieval fusion logic.
Tests the score-weighted late fusion implementation with various scenarios.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime
import warnings

# Suppress warnings for cleaner test output
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Optional for tests

from services.search_service.core.hybrid_retrieval import (
    HybridRetrievalEngine,
    FusionStrategy,
    RetrievalSource,
    EnhancedRetrievalResult,
    HybridRetrievalResultV2
)


class TestHybridRetrievalFusion:
    """Test hybrid retrieval fusion functionality."""
    
    @pytest.fixture
    def mock_engines(self):
        """Create mock search engines for testing."""
        with patch('services.search_service.core.meilisearch_engine.MeilisearchEngine') as mock_meilisearch, \
             patch('shared.core.vector_database.PineconeVectorDB') as mock_vector_db:
            
            # Mock Meilisearch results
            mock_meilisearch_instance = AsyncMock()
            mock_meilisearch_instance.search.return_value = [
                MagicMock(
                    content="Meilisearch result 1 for AI",
                    source="meilisearch",
                    score=0.88,
                    metadata={
                        "meilisearch_id": "ms_1",
                        "title": "AI Document 1",
                        "search_engine": "meilisearch",
                        "keyword_matches": ["AI", "artificial", "intelligence"]
                    }
                ),
                MagicMock(
                    content="Meilisearch result 2 for AI",
                    source="meilisearch",
                    score=0.8,
                    metadata={
                        "meilisearch_id": "ms_2",
                        "title": "AI Document 2",
                        "search_engine": "meilisearch",
                        "keyword_matches": ["AI", "artificial", "intelligence"]
                    }
                ),
                MagicMock(
                    content="Meilisearch result 4 for AI",
                    source="meilisearch",
                    score=0.64,
                    metadata={
                        "meilisearch_id": "ms_4",
                        "title": "AI Document 4",
                        "search_engine": "meilisearch",
                        "keyword_matches": ["AI", "artificial", "intelligence"]
                    }
                )
            ]
            mock_meilisearch.return_value = mock_meilisearch_instance
            
            # Mock vector database results
            mock_vector_db_instance = AsyncMock()
            mock_vector_db_instance.search_vectors.return_value = [
                MagicMock(
                    id="vec_1",
                    content="Vector result 1 for AI",
                    score=0.9,
                    metadata={
                        "vector_id": "vec_1",
                        "title": "AI Document 1",
                        "semantic_score": 0.9
                    }
                ),
                MagicMock(
                    id="vec_2",
                    content="Vector result 2 for AI",
                    score=0.8,
                    metadata={
                        "vector_id": "vec_2",
                        "title": "AI Document 2",
                        "semantic_score": 0.8
                    }
                ),
                MagicMock(
                    id="vec_3",
                    content="Vector result 3 for AI",
                    score=0.7,
                    metadata={
                        "vector_id": "vec_3",
                        "title": "AI Document 3",
                        "semantic_score": 0.7
                    }
                )
            ]
            mock_vector_db.return_value = mock_vector_db_instance
            
            yield {
                'meilisearch': mock_meilisearch_instance,
                'vector_db': mock_vector_db_instance
            }
    
    @pytest.fixture
    def engine(self, mock_engines):
        """Create a test engine instance."""
        with patch('services.search_service.core.meilisearch_engine.MeilisearchEngine') as mock_meilisearch, \
             patch('shared.core.vector_database.PineconeVectorDB') as mock_vector_db:
            
            # Configure the mocks to return our test instances
            mock_meilisearch.return_value = mock_engines['meilisearch']
            mock_vector_db.return_value = mock_engines['vector_db']
            
            # Create the engine
            engine = HybridRetrievalEngine()
            engine.meilisearch_engine = mock_engines['meilisearch']
            engine.vector_db = mock_engines['vector_db']
            engine.vector_db_initialized = True
            
            return engine
    
    @pytest.mark.asyncio
    async def test_basic_fusion_scenario(self, engine):
        """Test basic fusion scenario with multiple sources."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Verify result structure
        assert isinstance(result, HybridRetrievalResultV2)
        assert result.query == query
        assert len(result.enhanced_results) > 0
        assert result.confidence_score > 0
        assert result.processing_time_ms > 0
        
        # Verify enhanced results
        for enhanced_result in result.enhanced_results:
            assert isinstance(enhanced_result, EnhancedRetrievalResult)
            assert enhanced_result.document_id is not None
            assert enhanced_result.title is not None
            assert enhanced_result.content is not None
            assert enhanced_result.combined_score >= 0
            assert len(enhanced_result.source_types) > 0
    
    @pytest.mark.asyncio
    async def test_multi_source_boost(self, engine):
        """Test that documents found in multiple sources get score boost."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Check that results are properly scored
        assert len(result.enhanced_results) > 0
        
        # Verify that documents with multiple sources have higher scores
        multi_source_results = [
            r for r in result.enhanced_results 
            if len(r.source_types) > 1
        ]
        
        if multi_source_results:
            # Multi-source results should generally have higher scores
            # (though this depends on the specific scoring algorithm)
            assert any(r.combined_score > 0.5 for r in multi_source_results)
    
    @pytest.mark.asyncio
    async def test_score_normalization(self, engine):
        """Test that scores are properly normalized."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Verify that all scores are in the expected range
        for enhanced_result in result.enhanced_results:
            assert 0 <= enhanced_result.combined_score <= 1.0
            for score in enhanced_result.source_scores.values():
                assert 0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_empty_meilisearch_results(self, engine, mock_engines):
        """Test scenario where Meilisearch returns no results."""
        # Mock Meilisearch to return empty results
        mock_engines['meilisearch'].search.return_value = []
        
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Should still work with only vector results
        assert isinstance(result, HybridRetrievalResultV2)
        assert result.query == query
    
    @pytest.mark.asyncio
    async def test_empty_vector_results(self, engine, mock_engines):
        """Test scenario where vector search returns no results."""
        # Mock vector search to return empty results
        mock_engines['vector_db'].search_vectors.return_value = []
        
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Should still work with only Meilisearch results
        assert isinstance(result, HybridRetrievalResultV2)
        assert result.query == query
    
    @pytest.mark.asyncio
    async def test_all_empty_results(self, engine, mock_engines):
        """Test scenario where all sources return empty results."""
        # Mock all engines to return empty results
        mock_engines['vector_db'].search_vectors.return_value = []
        mock_engines['meilisearch'].search.return_value = []
        
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Should handle empty results gracefully
        assert isinstance(result, HybridRetrievalResultV2)
        assert result.query == query
        assert len(result.enhanced_results) == 0
        assert result.confidence_score == 0.0
    
    @pytest.mark.asyncio
    async def test_engine_failure_handling(self, engine, mock_engines):
        """Test handling of engine failures."""
        # Mock vector search to raise an exception
        mock_engines['vector_db'].search_vectors.side_effect = Exception("Vector search failed")
        
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Should handle failures gracefully
        assert isinstance(result, HybridRetrievalResultV2)
        assert result.query == query
    
    @pytest.mark.asyncio
    async def test_document_deduplication(self, engine):
        """Test that duplicate documents are properly deduplicated."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=10,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Check that we don't have duplicate document IDs
        document_ids = [r.document_id for r in result.enhanced_results]
        assert len(document_ids) == len(set(document_ids))
    
    @pytest.mark.asyncio
    async def test_fusion_strategies(self, engine):
        """Test different fusion strategies."""
        query = "artificial intelligence"
        
        strategies = [FusionStrategy.WEIGHTED_SUM, FusionStrategy.AVERAGE, FusionStrategy.MAX]
        
        for strategy in strategies:
            result = await engine.retrieve(
                query=query,
                max_results=5,
                fusion_strategy=strategy
            )
            
            assert isinstance(result, HybridRetrievalResultV2)
            assert result.fusion_strategy == strategy
    
    @pytest.mark.asyncio
    async def test_snippet_generation(self, engine):
        """Test that snippets are properly generated."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Check that snippets are generated
        for enhanced_result in result.enhanced_results:
            assert enhanced_result.snippet is not None
            assert len(enhanced_result.snippet) > 0
    
    @pytest.mark.asyncio
    async def test_metadata_preservation(self, engine):
        """Test that metadata is properly preserved."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Check that metadata is preserved
        for enhanced_result in result.enhanced_results:
            assert enhanced_result.metadata is not None
            assert isinstance(enhanced_result.metadata, dict)
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, engine):
        """Test that confidence scores are properly calculated."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Check confidence score range
        assert 0 <= result.confidence_score <= 1.0
        
        # If we have results, confidence should be > 0
        if len(result.enhanced_results) > 0:
            assert result.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, engine):
        """Test that performance metrics are properly recorded."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Check performance metrics
        assert result.processing_time_ms > 0
        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_edge_case_single_result(self, engine, mock_engines):
        """Test edge case with only one result from one source."""
        # Mock to return only one result
        mock_engines['vector_db'].search_vectors.return_value = [
            MagicMock(
                id="vec_1",
                content="Single vector result",
                score=0.9,
                metadata={
                    "vector_id": "vec_1",
                    "title": "Single Document",
                    "semantic_score": 0.9
                }
            )
        ]
        mock_engines['meilisearch'].search.return_value = []
        
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Should handle single result gracefully
        assert isinstance(result, HybridRetrievalResultV2)
        assert result.query == query
    
    @pytest.mark.asyncio
    async def test_edge_case_very_large_scores(self, engine, mock_engines):
        """Test edge case with very large scores that need normalization."""
        # Mock to return results with very large scores
        mock_engines['vector_db'].search_vectors.return_value = [
            MagicMock(
                id="vec_1",
                content="High score vector result",
                score=1.5,  # Above 1.0
                metadata={
                    "vector_id": "vec_1",
                    "title": "High Score Document",
                    "semantic_score": 1.5
                }
            )
        ]
        mock_engines['meilisearch'].search.return_value = [
            MagicMock(
                content="High score elastic result",
                source="elasticsearch",
                score=50.0,  # Very high BM25 score
                metadata={
                    "elasticsearch_id": "es_1",
                    "title": "High Score Document",
                    "bm25_score": 50.0,
                    "keyword_matches": ["test"]
                }
            )
        ]
        
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM
        )
        
        # Should normalize large scores properly
        assert isinstance(result, HybridRetrievalResultV2)
        for enhanced_result in result.enhanced_results:
            assert 0 <= enhanced_result.combined_score <= 1.0


class TestScoreNormalization:
    """Test score normalization functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create a test engine instance."""
        return HybridRetrievalEngine()
    
    def test_vector_score_normalization(self, engine):
        """Test vector score normalization."""
        # Test various score values
        test_scores = [0.0, 0.5, 1.0, 1.5, 2.0]
        
        for score in test_scores:
            normalized = engine._normalize_score(score, RetrievalSource.VECTOR_DB)
            assert 0 <= normalized <= 1.0
    
    def test_meilisearch_score_normalization(self, engine):
        """Test Meilisearch score normalization."""
        # Test various score values
        test_scores = [0.0, 0.5, 1.0, 1.5, 2.0]
        
        for score in test_scores:
            normalized = engine._normalize_score(score, RetrievalSource.MEILISEARCH)
            assert 0 <= normalized <= 1.0
    
    def test_other_source_normalization(self, engine):
        """Test normalization for other sources."""
        # Test various score values
        test_scores = [0.0, 0.5, 1.0, 1.5, 2.0]
        
        for score in test_scores:
            normalized = engine._normalize_score(score, RetrievalSource.KNOWLEDGE_GRAPH)
            assert 0 <= normalized <= 1.0


class TestCombinedScoreCalculation:
    """Test combined score calculation functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create a test engine instance."""
        return HybridRetrievalEngine()
    
    def test_single_source_score(self, engine):
        """Test calculation with single source."""
        source_scores = {"meilisearch": 0.8}
        
        score = engine._calculate_combined_score(source_scores, FusionStrategy.WEIGHTED_SUM)
        assert 0 <= score <= 1.0
    
    def test_multi_source_score(self, engine):
        """Test calculation with multiple sources."""
        source_scores = {"meilisearch": 0.8, "vector_db": 0.9}
        
        score = engine._calculate_combined_score(source_scores, FusionStrategy.WEIGHTED_SUM)
        assert 0 <= score <= 1.0
    
    def test_empty_source_scores(self, engine):
        """Test calculation with empty source scores."""
        source_scores = {}
        
        score = engine._calculate_combined_score(source_scores, FusionStrategy.WEIGHTED_SUM)
        assert score == 0.0
    
    def test_very_high_scores(self, engine):
        """Test calculation with very high scores."""
        source_scores = {"meilisearch": 0.95, "vector_db": 0.98}
        
        score = engine._calculate_combined_score(source_scores, FusionStrategy.WEIGHTED_SUM)
        assert 0 <= score <= 1.0
    
    def test_multi_source_boost(self, engine):
        """Test that multi-source results get score boost."""
        single_source = {"meilisearch": 0.8}
        multi_source = {"meilisearch": 0.8, "vector_db": 0.8}
        
        single_score = engine._calculate_combined_score(single_source, FusionStrategy.WEIGHTED_SUM)
        multi_score = engine._calculate_combined_score(multi_source, FusionStrategy.WEIGHTED_SUM)
        
        # Multi-source should generally have higher score due to boost
        assert multi_score >= single_score


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 