#!/usr/bin/env python3
"""
Unit tests for hybrid retrieval fusion logic.
Tests the score-weighted late fusion implementation with various scenarios.
"""

import asyncio
import pytest
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.search_service.core.hybrid_retrieval import (
    HybridRetrievalEngine,
    FusionStrategy,
    RetrievalSource,
    RetrievalResult,
    EnhancedRetrievalResult,
    HybridRetrievalResultV2
)


class TestHybridRetrievalFusion:
    """Test cases for hybrid retrieval fusion logic."""
    
    @pytest.fixture
    def mock_engines(self):
        """Create mock search engines for testing."""
        with patch('services.search_service.core.hybrid_retrieval.VectorSearchEngine') as mock_vector, \
             patch('services.search_service.core.hybrid_retrieval.MeilisearchEngine') as mock_meilisearch, \
             patch('services.search_service.core.hybrid_retrieval.KnowledgeGraphEngine') as mock_kg, \
             patch('services.search_service.core.hybrid_retrieval.WikipediaEngine') as mock_wikipedia, \
             patch('services.search_service.core.hybrid_retrieval.WikidataEngine') as mock_wikidata, \
             patch('services.search_service.core.hybrid_retrieval.ResultFusionEngine') as mock_fusion:
            
            # Mock vector search results
            mock_vector_instance = AsyncMock()
            mock_vector_instance.search.return_value = [
                RetrievalResult(
                    content="Vector result 1 for AI",
                    source=RetrievalSource.VECTOR_DB,
                    score=0.9,
                    metadata={
                        "vector_id": "vec_1",
                        "source_document": "doc_1",
                        "document_title": "AI Document 1",
                        "semantic_score": 0.9
                    }
                ),
                RetrievalResult(
                    content="Vector result 2 for AI",
                    source=RetrievalSource.VECTOR_DB,
                    score=0.8,
                    metadata={
                        "vector_id": "vec_2",
                        "source_document": "doc_2",
                        "document_title": "AI Document 2",
                        "semantic_score": 0.8
                    }
                ),
                RetrievalResult(
                    content="Vector result 3 for AI",
                    source=RetrievalSource.VECTOR_DB,
                    score=0.7,
                    metadata={
                        "vector_id": "vec_3",
                        "source_document": "doc_3",
                        "document_title": "AI Document 3",
                        "semantic_score": 0.7
                    }
                )
            ]
            mock_vector.return_value = mock_vector_instance
            
            # Mock Meilisearch results
            mock_meilisearch_instance = AsyncMock()
            mock_meilisearch_instance.search.return_value = [
                RetrievalResult(
                    content="Meilisearch result 1 for AI",
                    source=RetrievalSource.MEILISEARCH,
                    score=0.88,
                    metadata={
                        "meilisearch_id": "ms_1",
                        "source_document": "doc_1",
                        "document_title": "AI Document 1",
                        "search_engine": "meilisearch",
                        "keyword_matches": ["AI", "artificial", "intelligence"]
                    }
                ),
                RetrievalResult(
                    content="Meilisearch result 2 for AI",
                    source=RetrievalSource.MEILISEARCH,
                    score=0.8,
                    metadata={
                        "meilisearch_id": "ms_2",
                        "source_document": "doc_2",
                        "document_title": "AI Document 2",
                        "search_engine": "meilisearch",
                        "keyword_matches": ["AI", "artificial", "intelligence"]
                    }
                ),
                RetrievalResult(
                    content="Meilisearch result 4 for AI",
                    source=RetrievalSource.MEILISEARCH,
                    score=0.64,
                    metadata={
                        "meilisearch_id": "ms_4",
                        "source_document": "doc_4",
                        "document_title": "AI Document 4",
                        "search_engine": "meilisearch",
                        "keyword_matches": ["AI", "artificial", "intelligence"]
                    }
                )
            ]
            mock_meilisearch.return_value = mock_meilisearch_instance
            
            # Mock other engines with empty results
            mock_kg_instance = AsyncMock()
            mock_kg_instance.query.return_value = []
            mock_kg.return_value = mock_kg_instance
            
            mock_wikipedia_instance = AsyncMock()
            mock_wikipedia_instance.search.return_value = []
            mock_wikipedia.return_value = mock_wikipedia_instance
            
            mock_wikidata_instance = AsyncMock()
            mock_wikidata_instance.query.return_value = []
            mock_wikidata.return_value = mock_wikidata_instance
            
            # Mock fusion engine
            mock_fusion_instance = MagicMock()
            mock_fusion.return_value = mock_fusion_instance
            
            yield {
                'vector': mock_vector_instance,
                'meilisearch': mock_meilisearch_instance,
                'kg': mock_kg_instance,
                'wikipedia': mock_wikipedia_instance,
                'wikidata': mock_wikidata_instance,
                'fusion': mock_fusion_instance
            }
    
    @pytest.fixture
    def engine(self, mock_engines):
        """Create a HybridRetrievalEngine instance with mocked dependencies."""
        with patch('services.search_service.core.hybrid_retrieval.redis.Redis') as mock_redis:
            mock_redis_instance = MagicMock()
            mock_redis.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True
            
            engine = HybridRetrievalEngine()
            return engine
    
    @pytest.mark.asyncio
    async def test_basic_fusion_scenario(self, engine):
        """Test basic fusion scenario with both Meilisearch and vector results."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        # Assert result structure
        assert isinstance(result, HybridRetrievalResultV2)
        assert result.query == query
        assert len(result.enhanced_results) > 0
        
        # Assert all results are present and sorted by score
        scores = [r.combined_score for r in result.enhanced_results]
        assert scores == sorted(scores, reverse=True)
        
        # Assert metadata is present
        for enhanced_result in result.enhanced_results:
            assert enhanced_result.document_id is not None
            assert enhanced_result.title is not None
            assert enhanced_result.snippet is not None
            assert enhanced_result.combined_score >= 0
            assert len(enhanced_result.source_scores) > 0
            assert len(enhanced_result.source_types) > 0
            assert enhanced_result.metadata is not None
    
    @pytest.mark.asyncio
    async def test_multi_source_boost(self, engine):
        """Test that documents found in multiple sources get score boost."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=10,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        # Find documents that appear in both sources
        multi_source_results = [
            r for r in result.enhanced_results 
            if len(r.source_types) > 1
        ]
        
        # Find documents that appear in only one source
        single_source_results = [
            r for r in result.enhanced_results 
            if len(r.source_types) == 1
        ]
        
        # Assert multi-source documents have higher scores
        if multi_source_results and single_source_results:
            avg_multi_score = sum(r.combined_score for r in multi_source_results) / len(multi_source_results)
            avg_single_score = sum(r.combined_score for r in single_source_results) / len(single_source_results)
            
            # Multi-source documents should generally have higher scores
            assert avg_multi_score >= avg_single_score
    
    @pytest.mark.asyncio
    async def test_score_normalization(self, engine):
        """Test that scores from different sources are properly normalized."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=10,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        for enhanced_result in result.enhanced_results:
            # Check that normalized scores are in 0-1 range
            for source, score in enhanced_result.source_scores.items():
                assert 0 <= score <= 1, f"Score {score} for source {source} not in [0,1] range"
            
            # Check that combined score is in 0-1 range
            assert 0 <= enhanced_result.combined_score <= 1
    
    @pytest.mark.asyncio
    async def test_empty_meilisearch_results(self, engine, mock_engines):
        """Test scenario where Meilisearch returns no results."""
        # Mock Meilisearch to return empty results
        mock_engines['meilisearch'].search.return_value = []
        
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        # Should still get results from vector search
        assert len(result.enhanced_results) > 0
        
        # All results should come from vector search only
        for enhanced_result in result.enhanced_results:
            assert 'vector_db' in enhanced_result.source_types
            assert 'meilisearch' not in enhanced_result.source_types
    
    @pytest.mark.asyncio
    async def test_empty_vector_results(self, engine, mock_engines):
        """Test scenario where vector search returns no results."""
        # Mock vector search to return empty results
        mock_engines['vector'].search.return_value = []
        
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        # Should still get results from Elasticsearch
        assert len(result.enhanced_results) > 0
        
        # All results should come from Elasticsearch only
        for enhanced_result in result.enhanced_results:
            assert 'elasticsearch' in enhanced_result.source_types
            assert 'vector_db' not in enhanced_result.source_types
    
    @pytest.mark.asyncio
    async def test_all_empty_results(self, engine, mock_engines):
        """Test scenario where all sources return empty results."""
        # Mock all engines to return empty results
        mock_engines['vector'].search.return_value = []
        mock_engines['elasticsearch'].search.return_value = []
        
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        # Should return empty results
        assert len(result.enhanced_results) == 0
        assert result.confidence_score == 0.0
    
    @pytest.mark.asyncio
    async def test_engine_failure_handling(self, engine, mock_engines):
        """Test handling of engine failures."""
        # Mock vector search to raise an exception
        mock_engines['vector'].search.side_effect = Exception("Vector search failed")
        
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        # Should still get results from Elasticsearch
        assert len(result.enhanced_results) > 0
        
        # All results should come from Elasticsearch only
        for enhanced_result in result.enhanced_results:
            assert 'elasticsearch' in enhanced_result.source_types
            assert 'vector_db' not in enhanced_result.source_types
    
    @pytest.mark.asyncio
    async def test_document_deduplication(self, engine):
        """Test that duplicate documents are properly deduplicated."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=10,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        # Check that documents with same ID are deduplicated
        doc_ids = [r.document_id for r in result.enhanced_results]
        assert len(doc_ids) == len(set(doc_ids)), "Duplicate document IDs found"
        
        # Check that documents found in multiple sources are properly merged
        for enhanced_result in result.enhanced_results:
            if len(enhanced_result.source_types) > 1:
                # Should have scores from both sources
                assert len(enhanced_result.source_scores) > 1
    
    @pytest.mark.asyncio
    async def test_fusion_strategies(self, engine):
        """Test different fusion strategies."""
        query = "artificial intelligence"
        strategies = [
            FusionStrategy.WEIGHTED_SUM,
            FusionStrategy.RECIPROCAL_RANK,
            FusionStrategy.BORDA_COUNT
        ]
        
        for strategy in strategies:
            result = await engine.retrieve(
                query=query,
                fusion_strategy=strategy,
                max_results=5,
                sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
            )
            
            assert result.fusion_strategy == strategy
            assert len(result.enhanced_results) > 0
            assert result.confidence_score >= 0
    
    @pytest.mark.asyncio
    async def test_snippet_generation(self, engine):
        """Test that snippets are properly generated."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        for enhanced_result in result.enhanced_results:
            # Snippet should not be empty
            assert enhanced_result.snippet is not None
            assert len(enhanced_result.snippet) > 0
            
            # Snippet should be shorter than full content
            assert len(enhanced_result.snippet) <= len(enhanced_result.content)
    
    @pytest.mark.asyncio
    async def test_metadata_preservation(self, engine):
        """Test that metadata from different sources is properly preserved."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        for enhanced_result in result.enhanced_results:
            # Check that metadata contains expected fields
            assert 'source_document' in enhanced_result.metadata
            assert 'document_title' in enhanced_result.metadata
            
            # Check source-specific metadata
            if 'vector_db' in enhanced_result.source_types:
                assert 'vector_id' in enhanced_result.metadata
                assert 'semantic_score' in enhanced_result.metadata
            
            if 'elasticsearch' in enhanced_result.source_types:
                assert 'elasticsearch_id' in enhanced_result.metadata
                assert 'bm25_score' in enhanced_result.metadata
                assert 'keyword_matches' in enhanced_result.metadata
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, engine):
        """Test that confidence scores are calculated correctly."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        # Confidence should be between 0 and 1
        assert 0 <= result.confidence_score <= 1
        
        # Confidence should be higher when we have more diverse sources
        if len(result.enhanced_results) > 0:
            multi_source_count = sum(
                1 for r in result.enhanced_results 
                if len(r.source_types) > 1
            )
            if multi_source_count > 0:
                # Should have reasonable confidence with multi-source results
                assert result.confidence_score > 0.3
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, engine):
        """Test that performance metrics are properly recorded."""
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        # Processing time should be recorded
        assert result.processing_time_ms > 0
        
        # Metadata should contain performance info
        assert 'parallel_execution' in result.metadata
        assert 'late_fusion_applied' in result.metadata
        assert result.metadata['parallel_execution'] is True
        assert result.metadata['late_fusion_applied'] is True
    
    @pytest.mark.asyncio
    async def test_edge_case_single_result(self, engine, mock_engines):
        """Test edge case with only one result from one source."""
        # Mock to return only one result
        mock_engines['vector'].search.return_value = [
            RetrievalResult(
                content="Single vector result",
                source=RetrievalSource.VECTOR_DB,
                score=0.9,
                metadata={
                    "vector_id": "vec_1",
                    "source_document": "doc_1",
                    "document_title": "Single Document",
                    "semantic_score": 0.9
                }
            )
        ]
        mock_engines['elasticsearch'].search.return_value = []
        
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        assert len(result.enhanced_results) == 1
        assert result.enhanced_results[0].source_types == ['vector_db']
        assert result.enhanced_results[0].combined_score > 0
    
    @pytest.mark.asyncio
    async def test_edge_case_very_large_scores(self, engine, mock_engines):
        """Test edge case with very large scores that need normalization."""
        # Mock to return results with very large scores
        mock_engines['vector'].search.return_value = [
            RetrievalResult(
                content="High score vector result",
                source=RetrievalSource.VECTOR_DB,
                score=1.5,  # Above 1.0
                metadata={
                    "vector_id": "vec_1",
                    "source_document": "doc_1",
                    "document_title": "High Score Document",
                    "semantic_score": 1.5
                }
            )
        ]
        mock_engines['elasticsearch'].search.return_value = [
            RetrievalResult(
                content="High score elastic result",
                source=RetrievalSource.ELASTICSEARCH,
                score=50.0,  # Very high BM25 score
                metadata={
                    "elasticsearch_id": "es_1",
                    "source_document": "doc_1",
                    "document_title": "High Score Document",
                    "bm25_score": 50.0,
                    "keyword_matches": ["test"]
                }
            )
        ]
        
        query = "artificial intelligence"
        
        result = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.ELASTICSEARCH, RetrievalSource.VECTOR_DB]
        )
        
        # Scores should be normalized to 0-1 range
        for enhanced_result in result.enhanced_results:
            assert 0 <= enhanced_result.combined_score <= 1
            for source, score in enhanced_result.source_scores.items():
                assert 0 <= score <= 1


class TestScoreNormalization:
    """Test cases for score normalization logic."""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance for testing."""
        with patch('services.search_service.core.hybrid_retrieval.redis.Redis') as mock_redis:
            mock_redis_instance = MagicMock()
            mock_redis.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True
            
            return HybridRetrievalEngine()
    
    def test_vector_score_normalization(self, engine):
        """Test normalization of vector similarity scores."""
        # Vector scores are typically 0-1, should remain as is
        assert engine._normalize_score(0.9, RetrievalSource.VECTOR_DB) == 0.9
        assert engine._normalize_score(0.5, RetrievalSource.VECTOR_DB) == 0.5
        assert engine._normalize_score(0.0, RetrievalSource.VECTOR_DB) == 0.0
        assert engine._normalize_score(1.0, RetrievalSource.VECTOR_DB) == 1.0
        
        # Values outside 0-1 should be clamped
        assert engine._normalize_score(1.5, RetrievalSource.VECTOR_DB) == 1.0
        assert engine._normalize_score(-0.5, RetrievalSource.VECTOR_DB) == 0.0
    
    def test_meilisearch_score_normalization(self, engine):
        """Test normalization of Meilisearch scores."""
        # BM25 scores are normalized by dividing by 20
        assert engine._normalize_score(1.0, RetrievalSource.MEILISEARCH) == 1.0
        assert engine._normalize_score(0.5, RetrievalSource.MEILISEARCH) == 0.5
        assert engine._normalize_score(0.0, RetrievalSource.MEILISEARCH) == 0.0
        
        # Very high scores should be clamped
        assert engine._normalize_score(2.0, RetrievalSource.MEILISEARCH) == 1.0
        assert engine._normalize_score(-0.5, RetrievalSource.MEILISEARCH) == 0.0
    
    def test_other_source_normalization(self, engine):
        """Test normalization for other source types."""
        # Other sources should use default normalization (clamp to 0-1)
        assert engine._normalize_score(0.8, RetrievalSource.KNOWLEDGE_GRAPH) == 0.8
        assert engine._normalize_score(1.2, RetrievalSource.WIKIPEDIA) == 1.0
        assert engine._normalize_score(-0.3, RetrievalSource.WIKIDATA) == 0.0


class TestCombinedScoreCalculation:
    """Test cases for combined score calculation."""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance for testing."""
        with patch('services.search_service.core.hybrid_retrieval.redis.Redis') as mock_redis:
            mock_redis_instance = MagicMock()
            mock_redis.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True
            
            return HybridRetrievalEngine()
    
    def test_single_source_score(self, engine):
        """Test combined score calculation for single source."""
        source_scores = {'vector_db': 0.8}
        combined_score = engine._calculate_combined_score(source_scores)
        
        assert 0 <= combined_score <= 1
        
        # Calculate expected value based on actual implementation:
        # 1. Weighted sum = 0.8 * 0.4 = 0.32
        # 2. Total weight = 0.4
        # 3. Base score = 0.32 / 0.4 = 0.8
        # 4. Source count boost = 1 * 0.2 = 0.2
        # 5. Boosted score = 0.8 * (1 + 0.2) = 0.8 * 1.2 = 0.96
        expected_score = 0.96
        
        assert abs(combined_score - expected_score) < 0.01
    
    def test_multi_source_score(self, engine):
        """Test combined score calculation for multiple sources."""
        source_scores = {
            'vector_db': 0.8,
            'meilisearch': 0.6
        }
        combined_score = engine._calculate_combined_score(source_scores)
        
        assert 0 <= combined_score <= 1
        # Should be higher than single source due to boost
        assert combined_score > 0.6
    
    def test_empty_source_scores(self, engine):
        """Test combined score calculation with empty source scores."""
        source_scores = {}
        combined_score = engine._calculate_combined_score(source_scores)
        
        assert combined_score == 0.0
    
    def test_very_high_scores(self, engine):
        """Test combined score calculation with very high scores."""
        source_scores = {
            'vector_db': 1.0,
            'meilisearch': 1.0,
            'knowledge_graph': 1.0
        }
        combined_score = engine._calculate_combined_score(source_scores)
        
        # Should be clamped to 1.0
        assert combined_score == 1.0
    
    def test_multi_source_boost(self, engine):
        """Test that multi-source documents get score boost."""
        single_source = {'vector_db': 0.8}
        multi_source = {'vector_db': 0.8, 'meilisearch': 0.6}
        
        single_score = engine._calculate_combined_score(single_source)
        multi_score = engine._calculate_combined_score(multi_source)
        
        # Multi-source should have higher score due to boost
        assert multi_score > single_score


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 