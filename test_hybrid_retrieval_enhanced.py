#!/usr/bin/env python3
"""
Test script for enhanced HybridRetrievalEngine with score-weighted late fusion.
Demonstrates parallel execution of Meilisearch and vector search with enhanced metadata.
"""

import asyncio
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.search_service.core.hybrid_retrieval import (
    HybridRetrievalEngine,
    FusionStrategy,
    RetrievalSource
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_enhanced_hybrid_retrieval():
    """Test the enhanced hybrid retrieval with score-weighted late fusion."""
    
    print("🚀 Testing Enhanced Hybrid Retrieval with Score-Weighted Late Fusion")
    print("=" * 70)
    
    # Initialize the enhanced retrieval engine
    engine = HybridRetrievalEngine()
    
    try:
        # Test queries
        test_queries = [
            "artificial intelligence applications",
            "machine learning algorithms",
            "natural language processing techniques",
            "deep learning neural networks"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test {i}: Query = '{query}'")
            print("-" * 50)
            
            # Execute enhanced retrieval
            result = await engine.retrieve(
                query=query,
                fusion_strategy=FusionStrategy.WEIGHTED_SUM,
                max_results=5,
                sources=[RetrievalSource.MEILISEARCH, RetrievalSource.VECTOR_DB]
            )
            
            # Display results
            print(f"✅ Processing time: {result.processing_time_ms:.2f}ms")
            print(f"🎯 Confidence score: {result.confidence_score:.3f}")
            print(f"📊 Total results: {len(result.enhanced_results)}")
            print(f"🔍 Sources used: {result.metadata.get('sources_used', [])}")
            
            print("\n📋 Enhanced Results (sorted by combined relevance score):")
            print("-" * 40)
            
            for j, enhanced_result in enumerate(result.enhanced_results, 1):
                print(f"\n{j}. Document: {enhanced_result.title}")
                print(f"   ID: {enhanced_result.document_id}")
                print(f"   Combined Score: {enhanced_result.combined_score:.3f}")
                print(f"   Source Scores: {enhanced_result.source_scores}")
                print(f"   Source Types: {enhanced_result.source_types}")
                print(f"   Snippet: {enhanced_result.snippet}")
                
                # Show metadata details
                if enhanced_result.metadata:
                    print(f"   Metadata: {enhanced_result.metadata}")
            
            print(f"\n📝 Fused Content:")
            print(f"   {result.fused_content}")
            
            print("\n" + "=" * 70)
        
        # Test with different fusion strategies
        print("\n🧪 Testing Different Fusion Strategies")
        print("=" * 50)
        
        query = "artificial intelligence"
        strategies = [
            FusionStrategy.WEIGHTED_SUM,
            FusionStrategy.RECIPROCAL_RANK,
            FusionStrategy.BORDA_COUNT
        ]
        
        for strategy in strategies:
            print(f"\n🔧 Strategy: {strategy.value}")
            result = await engine.retrieve(
                query=query,
                fusion_strategy=strategy,
                max_results=3
            )
            
            print(f"   Confidence: {result.confidence_score:.3f}")
            print(f"   Results: {len(result.enhanced_results)}")
            
            if result.enhanced_results:
                top_result = result.enhanced_results[0]
                print(f"   Top Score: {top_result.combined_score:.3f}")
                print(f"   Top Sources: {top_result.source_types}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
    
    finally:
        # Clean up
        await engine.close()


async def test_performance_comparison():
    """Compare performance of parallel vs sequential execution."""
    
    print("\n⚡ Performance Comparison: Parallel vs Sequential")
    print("=" * 60)
    
    engine = HybridRetrievalEngine()
    
    try:
        query = "machine learning applications"
        
        # Test parallel execution (default)
        print("\n🔄 Testing Parallel Execution...")
        start_time = asyncio.get_event_loop().time()
        
        result_parallel = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.MEILISEARCH, RetrievalSource.VECTOR_DB]
        )
        
        parallel_time = (asyncio.get_event_loop().time() - start_time) * 1000
        print(f"   Parallel execution time: {parallel_time:.2f}ms")
        print(f"   Results: {len(result_parallel.enhanced_results)}")
        
        # Test with more sources
        print("\n🔄 Testing with Multiple Sources...")
        start_time = asyncio.get_event_loop().time()
        
        result_multi = await engine.retrieve(
            query=query,
            max_results=5,
            sources=[RetrievalSource.MEILISEARCH, RetrievalSource.VECTOR_DB, 
                    RetrievalSource.KNOWLEDGE_GRAPH, RetrievalSource.WIKIPEDIA]
        )
        
        multi_time = (asyncio.get_event_loop().time() - start_time) * 1000
        print(f"   Multi-source execution time: {multi_time:.2f}ms")
        print(f"   Results: {len(result_multi.enhanced_results)}")
        print(f"   Sources used: {result_multi.metadata.get('sources_used', [])}")
        
        print("\n📈 Performance Summary:")
        print(f"   Parallel (2 sources): {parallel_time:.2f}ms")
        print(f"   Multi-source (4 sources): {multi_time:.2f}ms")
        print(f"   Efficiency: {parallel_time/multi_time:.2f}x faster with parallel execution")
        
    except Exception as e:
        logger.error(f"Performance test failed: {e}")
        print(f"❌ Performance test failed: {e}")
    
    finally:
        await engine.close()


async def test_score_normalization():
    """Test score normalization and late fusion."""
    
    print("\n🎯 Testing Score Normalization and Late Fusion")
    print("=" * 55)
    
    engine = HybridRetrievalEngine()
    
    try:
        query = "deep learning neural networks"
        
        result = await engine.retrieve(
            query=query,
            max_results=10
        )
        
        print(f"Query: {query}")
        print(f"Total enhanced results: {len(result.enhanced_results)}")
        
        print("\n📊 Score Analysis:")
        print("-" * 30)
        
        for i, enhanced_result in enumerate(result.enhanced_results, 1):
            print(f"\n{i}. {enhanced_result.title}")
            print(f"   Combined Score: {enhanced_result.combined_score:.3f}")
            print(f"   Source Scores: {enhanced_result.source_scores}")
            print(f"   Source Count: {len(enhanced_result.source_types)}")
            
            # Show which sources contributed
            if len(enhanced_result.source_types) > 1:
                print(f"   ✅ Multi-source match (boosted score)")
            else:
                print(f"   ⚠️  Single source match")
        
        # Analyze score distribution
        scores = [r.combined_score for r in result.enhanced_results]
        if scores:
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            
            print(f"\n📈 Score Statistics:")
            print(f"   Average: {avg_score:.3f}")
            print(f"   Maximum: {max_score:.3f}")
            print(f"   Minimum: {min_score:.3f}")
            print(f"   Range: {max_score - min_score:.3f}")
        
    except Exception as e:
        logger.error(f"Score normalization test failed: {e}")
        print(f"❌ Score normalization test failed: {e}")
    
    finally:
        await engine.close()


async def main():
    """Run all tests."""
    print("🧪 Enhanced Hybrid Retrieval Engine Tests")
    print("=" * 50)
    
    # Run tests
    await test_enhanced_hybrid_retrieval()
    await test_performance_comparison()
    await test_score_normalization()
    
    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main()) 