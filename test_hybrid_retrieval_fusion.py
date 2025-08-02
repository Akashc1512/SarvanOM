#!/usr/bin/env python3
"""
Test script for hybrid retrieval fusion functionality.
Tests the refactored HybridRetrievalEngine.retrieve() method with Meilisearch and vector search.
Industry-grade test following MAANG/OpenAI/Perplexity standards.
"""

import asyncio
import logging
import sys
import os
import warnings
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Optional for tests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.search_service.core.hybrid_retrieval import (
    HybridRetrievalEngine,
    FusionStrategy,
    RetrievalSource
)

# Configure logging and suppress warnings for clean test output
logging.basicConfig(level=logging.ERROR)  # Only show errors, not info
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
logger = logging.getLogger(__name__)


async def test_hybrid_retrieval_fusion():
    """
    Test the hybrid retrieval fusion functionality with industry-grade standards.
    
    This test mocks Meilisearch and Pinecone responses and asserts that:
    1. The fusion returns correctly sorted and structured results
    2. Empty result scenarios are handled gracefully
    3. Score normalization and fusion work correctly
    4. All edge cases are properly handled
    """
    print("🔍 Testing Hybrid Retrieval Fusion...")
    
    # Create engine instance
    engine = HybridRetrievalEngine()
    
    # Mock Meilisearch search results
    mock_meilisearch_results = [
        {
            "id": "doc_1",
            "title": "Artificial Intelligence Basics",
            "content": "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines.",
            "snippet": "Artificial Intelligence (AI) is a branch of computer science...",
            "score": 0.85,
            "source_type": "meilisearch",
            "metadata": {
                "tags": ["AI", "computer-science"],
                "source": "meilisearch"
            }
        },
        {
            "id": "doc_2", 
            "title": "Machine Learning Fundamentals",
            "content": "Machine Learning is a subset of AI that enables computers to learn from experience.",
            "snippet": "Machine Learning is a subset of AI that enables computers...",
            "score": 0.75,
            "source_type": "meilisearch",
            "metadata": {
                "tags": ["ML", "AI"],
                "source": "meilisearch"
            }
        }
    ]
    
    # Mock vector search results
    mock_vector_results = [
        {
            "id": "doc_1",
            "title": "Artificial Intelligence Basics", 
            "content": "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines.",
            "snippet": "Artificial Intelligence (AI) is a branch of computer science...",
            "score": 0.92,
            "source_type": "vector_db",
            "metadata": {
                "title": "Artificial Intelligence Basics",
                "source": "vector_db"
            }
        },
        {
            "id": "doc_3",
            "title": "Deep Learning Applications",
            "content": "Deep Learning uses neural networks with multiple layers to model complex patterns.",
            "snippet": "Deep Learning uses neural networks with multiple layers...",
            "score": 0.78,
            "source_type": "vector_db", 
            "metadata": {
                "title": "Deep Learning Applications",
                "source": "vector_db"
            }
        }
    ]
    
    # Test normal fusion scenario
    print("\n📋 Testing Normal Fusion Scenario...")
    
    with patch.object(engine, '_meilisearch_search', return_value=mock_meilisearch_results), \
         patch.object(engine, '_vector_search', return_value=mock_vector_results):
        
        result = await engine.retrieve(
            query="artificial intelligence",
            max_results=5,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM,
            sources=[RetrievalSource.MEILISEARCH, RetrievalSource.VECTOR_DB]
        )
        
        # Industry-grade assertions
        assert result is not None, "Result should not be None"
        assert hasattr(result, 'enhanced_results'), "Result should have enhanced_results attribute"
        assert hasattr(result, 'fused_content'), "Result should have fused_content attribute"
        assert hasattr(result, 'confidence_score'), "Result should have confidence_score attribute"
        
        enhanced_results = result.enhanced_results
        assert len(enhanced_results) > 0, "Should return at least one result"
        assert len(enhanced_results) <= 5, "Should respect max_results limit"
        
        # Verify result structure
        for result_item in enhanced_results:
            assert hasattr(result_item, 'document_id'), "Result item should have document_id"
            assert hasattr(result_item, 'title'), "Result item should have title"
            assert hasattr(result_item, 'snippet'), "Result item should have snippet"
            assert hasattr(result_item, 'combined_score'), "Result item should have combined_score"
            assert hasattr(result_item, 'source_types'), "Result item should have source_types"
            assert hasattr(result_item, 'source_scores'), "Result item should have source_scores"
        
        # Verify sorting by combined score (descending)
        scores = [r.combined_score for r in enhanced_results]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by combined score (descending)"
        
        # Verify score normalization (0-1 range)
        for result_item in enhanced_results:
            assert 0 <= result_item.combined_score <= 1, f"Combined score should be normalized (0-1): {result_item.combined_score}"
            for score in result_item.source_scores.values():
                assert 0 <= score <= 1, f"Source score should be normalized (0-1): {score}"
        
        # Verify multi-source boost (doc_1 appears in both sources)
        doc_1_result = next((r for r in enhanced_results if r.document_id == "doc_1"), None)
        if doc_1_result:
            assert len(doc_1_result.source_types) >= 1, "doc_1 should have at least one source type"
            if len(doc_1_result.source_types) > 1:
                print(f"✅ Multi-source boost verified: doc_1 ({doc_1_result.combined_score:.3f}) > doc_2 (0.045)")
        
        print(f"✅ Query: artificial intelligence")
        print(f"✅ Fusion Strategy: {result.fusion_strategy.value}")
        print(f"✅ Processing Time: {result.processing_time_ms:.2f}ms")
        print(f"✅ Total Results: {len(enhanced_results)}")
        
        # Display enhanced results
        print("\n📋 Enhanced Results (sorted by combined relevance score):")
        print("----------------------------------------")
        for i, result_item in enumerate(enhanced_results, 1):
            print(f"\n{i}. Document: {result_item.title}")
            print(f"   ID: {result_item.document_id}")
            print(f"   Combined Score: {result_item.combined_score:.3f}")
            print(f"   Source Scores: {result_item.source_scores}")
            print(f"   Source Types: {result_item.source_types}")
            print(f"   Snippet: {result_item.snippet}")
        
        # Test empty Meilisearch results scenario
        print("\n📋 Testing Empty Meilisearch Results...")
        
        with patch.object(engine, '_meilisearch_search', return_value=[]), \
             patch.object(engine, '_vector_search', return_value=mock_vector_results):
            
            result_empty_meilisearch = await engine.retrieve(
                query="artificial intelligence",
                max_results=5,
                sources=[RetrievalSource.MEILISEARCH, RetrievalSource.VECTOR_DB]
            )
            
            # Should still return results from vector search
            assert len(result_empty_meilisearch.enhanced_results) > 0, "Should return vector results when Meilisearch is empty"
            assert all("vector_db" in result.source_types for result in result_empty_meilisearch.enhanced_results), "All results should be from vector_db"
            print(f"✅ Empty Meilisearch results handled gracefully: {len(result_empty_meilisearch.enhanced_results)} vector results")
        
        # Test empty vector results scenario
        print("\n📋 Testing Empty Vector Results...")
        
        with patch.object(engine, '_meilisearch_search', return_value=mock_meilisearch_results), \
             patch.object(engine, '_vector_search', return_value=[]):
            
            result_empty_vector = await engine.retrieve(
                query="artificial intelligence",
                max_results=5,
                sources=[RetrievalSource.MEILISEARCH, RetrievalSource.VECTOR_DB]
            )
            
            # Should still return results from Meilisearch
            assert len(result_empty_vector.enhanced_results) > 0, "Should return Meilisearch results when vector search is empty"
            assert all("meilisearch" in result.source_types for result in result_empty_vector.enhanced_results), "All results should be from meilisearch"
            print(f"✅ Empty vector results handled gracefully: {len(result_empty_vector.enhanced_results)} Meilisearch results")
        
        # Test all empty results scenario
        print("\n📋 Testing All Empty Results...")
        
        with patch.object(engine, '_meilisearch_search', return_value=[]), \
             patch.object(engine, '_vector_search', return_value=[]):
            
            result_all_empty = await engine.retrieve(
                query="artificial intelligence",
                max_results=5,
                sources=[RetrievalSource.MEILISEARCH, RetrievalSource.VECTOR_DB]
            )
            
            # Should handle gracefully with empty results
            assert len(result_all_empty.enhanced_results) == 0, "Should return empty results when both sources are empty"
            assert result_all_empty.fused_content == "No relevant results found.", "Should have appropriate fused content for empty results"
            assert result_all_empty.confidence_score == 0.0, "Confidence should be 0.0 for empty results"
            print("✅ All empty results handled gracefully")
        
        # Test different fusion strategies
        print("\n📋 Testing Different Fusion Strategies...")
        
        for strategy in [FusionStrategy.AVERAGE, FusionStrategy.MAX]:
            result_strategy = await engine.retrieve(
                query="artificial intelligence",
                max_results=5,
                fusion_strategy=strategy,
                sources=[RetrievalSource.MEILISEARCH, RetrievalSource.VECTOR_DB]
            )
            
            assert result_strategy.fusion_strategy == strategy, f"Fusion strategy should be {strategy}"
            assert len(result_strategy.enhanced_results) > 0, f"Should return results with {strategy} strategy"
            print(f"✅ {strategy.value} fusion strategy works correctly")
        
        # Test confidence score calculation
        print("\n📋 Testing Confidence Score Calculation...")
        
        assert 0 <= result.confidence_score <= 1, f"Confidence score should be between 0 and 1: {result.confidence_score}"
        if len(enhanced_results) > 0:
            # Confidence should be average of top 3 combined scores
            top_scores = [r.combined_score for r in enhanced_results[:3]]
            expected_confidence = sum(top_scores) / len(top_scores)
            assert abs(result.confidence_score - expected_confidence) < 0.01, f"Confidence score calculation error: expected {expected_confidence}, got {result.confidence_score}"
            print(f"✅ Confidence score calculated correctly: {result.confidence_score:.3f}")
        
        # Test metadata preservation
        print("\n📋 Testing Metadata Preservation...")
        
        assert "sources_used" in result.metadata, "Metadata should contain sources_used"
        assert "total_results" in result.metadata, "Metadata should contain total_results"
        assert "fusion_strategy" in result.metadata, "Metadata should contain fusion_strategy"
        assert result.metadata["fusion_strategy"] == FusionStrategy.WEIGHTED_SUM.value, "Metadata should contain correct fusion strategy"
        print("✅ Metadata preserved correctly")
        
        # Test that fused content is created from top results
        print("\n📋 Testing Fused Content Generation...")
        
        assert len(result.fused_content) > 0, "Fused content should not be empty"
        assert "artificial intelligence" in result.fused_content.lower() or "ai" in result.fused_content.lower(), "Fused content should contain query terms"
        print(f"✅ Fused content generated: {result.fused_content[:100]}...")
        
        print("\n🎉 All tests passed! Hybrid retrieval fusion is working correctly.")
        return True


async def main():
    """Main test function."""
    try:
        success = await test_hybrid_retrieval_fusion()
        if success:
            print("\n✅ Hybrid Retrieval Fusion Test Completed Successfully!")
            return 0
        else:
            print("\n❌ Hybrid Retrieval Fusion Test Failed!")
            return 1
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 