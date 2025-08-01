#!/usr/bin/env python3
"""
Test Meilisearch Integration - Zero-budget Elasticsearch alternative
Tests the Meilisearch integration with the existing hybrid retrieval system.
"""
import asyncio
import logging
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.search_service.core.meilisearch_engine import MeilisearchEngine, MeilisearchDocument
from services.search_service.core.hybrid_retrieval import HybridRetrievalEngine, RetrievalSource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_meilisearch_basic():
    """Test basic Meilisearch functionality."""
    print("🔍 Testing Meilisearch Basic Functionality...")
    
    # Initialize Meilisearch engine
    meilisearch_url = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
    engine = MeilisearchEngine(meilisearch_url)
    
    # Test health check
    is_healthy = await engine.health_check()
    if not is_healthy:
        print("❌ Meilisearch is not running. Please start it first:")
        print("   docker run -p 7700:7700 getmeili/meilisearch:latest")
        return False
    
    print("✅ Meilisearch is running")
    
    # Test index creation
    index_created = await engine.create_index()
    if not index_created:
        print("❌ Failed to create index")
        return False
    
    print("✅ Index created successfully")
    
    # Test document addition
    test_documents = [
        MeilisearchDocument(
            id="1",
            title="Artificial Intelligence Basics",
            content="Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that work and react like humans.",
            tags=["AI", "computer-science", "technology"]
        ),
        MeilisearchDocument(
            id="2", 
            title="Machine Learning Fundamentals",
            content="Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed.",
            tags=["ML", "AI", "algorithms"]
        ),
        MeilisearchDocument(
            id="3",
            title="Deep Learning Applications",
            content="Deep Learning uses neural networks with multiple layers to model and understand complex patterns in data.",
            tags=["deep-learning", "neural-networks", "AI"]
        )
    ]
    
    docs_added = await engine.add_documents(test_documents)
    if not docs_added:
        print("❌ Failed to add documents")
        return False
    
    print("✅ Documents added successfully")
    
    # Test search functionality
    search_results = await engine.search("artificial intelligence", top_k=5)
    if not search_results:
        print("❌ Search returned no results")
        return False
    
    print(f"✅ Search successful - found {len(search_results)} results")
    for i, result in enumerate(search_results[:3]):
        print(f"   {i+1}. Score: {result.score:.3f} - {result.content[:100]}...")
    
    return True


async def test_hybrid_retrieval_integration():
    """Test Meilisearch integration with hybrid retrieval system."""
    print("\n🔍 Testing Hybrid Retrieval Integration...")
    
    # Initialize hybrid retrieval engine
    hybrid_engine = HybridRetrievalEngine()
    
    # Test retrieval with Meilisearch and Vector search
    query = "artificial intelligence machine learning"
    
    try:
        result = await hybrid_engine.retrieve(
            query=query,
            sources=[RetrievalSource.MEILISEARCH, RetrievalSource.VECTOR_DB],
            max_results=10
        )
        
        print(f"✅ Hybrid retrieval successful")
        print(f"   Query: {result.query}")
        print(f"   Processing time: {result.processing_time_ms:.2f}ms")
        print(f"   Confidence: {result.confidence_score:.3f}")
        print(f"   Results found: {len(result.enhanced_results)}")
        
        # Show top results
        for i, enhanced_result in enumerate(result.enhanced_results[:3]):
            print(f"   {i+1}. Combined Score: {enhanced_result.combined_score:.3f}")
            print(f"      Title: {enhanced_result.title}")
            print(f"      Snippet: {enhanced_result.snippet[:100]}...")
            print(f"      Sources: {enhanced_result.source_types}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hybrid retrieval failed: {e}")
        return False


async def test_performance_comparison():
    """Compare Meilisearch performance with expected Elasticsearch performance."""
    print("\n🔍 Testing Performance Comparison...")
    
    engine = MeilisearchEngine()
    
    # Test search performance
    queries = [
        "artificial intelligence",
        "machine learning algorithms", 
        "deep learning neural networks",
        "computer science technology",
        "data science analytics"
    ]
    
    total_time = 0
    successful_searches = 0
    
    for query in queries:
        start_time = datetime.now()
        results = await engine.search(query, top_k=10)
        end_time = datetime.now()
        
        search_time = (end_time - start_time).total_seconds() * 1000
        
        if results:
            successful_searches += 1
            total_time += search_time
            print(f"   ✅ '{query}' - {len(results)} results in {search_time:.2f}ms")
        else:
            print(f"   ❌ '{query}' - No results")
    
    if successful_searches > 0:
        avg_time = total_time / successful_searches
        print(f"\n📊 Performance Summary:")
        print(f"   Average search time: {avg_time:.2f}ms")
        print(f"   Successful searches: {successful_searches}/{len(queries)}")
        
        # Meilisearch should be faster than Elasticsearch
        if avg_time < 100:  # Less than 100ms is excellent
            print("   🚀 Performance: Excellent (faster than Elasticsearch)")
        elif avg_time < 200:
            print("   ⚡ Performance: Good (comparable to Elasticsearch)")
        else:
            print("   ⚠️ Performance: Slow (may need optimization)")
    
    return successful_searches > 0


async def main():
    """Run all Meilisearch integration tests."""
    print("🚀 Meilisearch Integration Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    basic_ok = await test_meilisearch_basic()
    
    if basic_ok:
        # Test hybrid retrieval integration
        hybrid_ok = await test_hybrid_retrieval_integration()
        
        # Test performance
        performance_ok = await test_performance_comparison()
        
        print("\n" + "=" * 50)
        print("📋 Test Results Summary:")
        print(f"   Basic Functionality: {'✅ PASS' if basic_ok else '❌ FAIL'}")
        print(f"   Hybrid Integration: {'✅ PASS' if hybrid_ok else '❌ FAIL'}")
        print(f"   Performance: {'✅ PASS' if performance_ok else '❌ FAIL'}")
        
        if basic_ok and hybrid_ok and performance_ok:
            print("\n🎉 All tests passed! Meilisearch is ready to replace Elasticsearch.")
            print("\n💡 Next steps:")
            print("   1. Update your .env file with MEILISEARCH_URL=http://localhost:7700")
            print("   2. Remove Elasticsearch from docker-compose.yml")
            print("   3. Add Meilisearch to your deployment scripts")
        else:
            print("\n⚠️ Some tests failed. Please check the logs above.")
    else:
        print("\n❌ Basic functionality test failed. Please ensure Meilisearch is running.")


if __name__ == "__main__":
    asyncio.run(main()) 