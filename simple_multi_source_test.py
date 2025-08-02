#!/usr/bin/env python3
"""
Simple test for multi-source retrieval integration.
"""

import asyncio
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.search_service.retrieval_agent import RetrievalAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_basic_integration():
    """Test basic multi-source retrieval integration."""
    
    print("🧪 Testing Multi-Source Retrieval Integration")
    print("=" * 50)
    
    try:
        # Initialize the retrieval agent
        print("📦 Initializing RetrievalAgent...")
        agent = RetrievalAgent()
        print("✅ RetrievalAgent initialized successfully")
        
        # Test query
        query = "What is machine learning?"
        print(f"\n🔍 Testing query: {query}")
        
        # Perform hybrid retrieval
        print("🔄 Performing hybrid retrieval...")
        result = await agent.hybrid_retrieve(query)
        
        print(f"✅ Search completed in {result.query_time_ms}ms")
        print(f"📊 Total hits: {result.total_hits}")
        print(f"🎯 Search type: {result.search_type}")
        
        # Show metadata
        if result.metadata:
            print(f"📋 Strategies used: {result.metadata.get('strategies_used', [])}")
            print(f"📋 Intent: {result.metadata.get('intent', 'unknown')}")
            print(f"📋 Complexity: {result.metadata.get('complexity', 'unknown')}")
        
        # Show top results
        print(f"\n📄 Top {min(3, len(result.documents))} results:")
        for i, doc in enumerate(result.documents[:3], 1):
            print(f"  {i}. [{doc.source}] Score: {doc.score:.3f}")
            print(f"     Content: {doc.content[:100]}...")
            print()
        
        print("🎉 Multi-source retrieval test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error("Test failed", exc_info=True)
        return False


async def test_individual_sources():
    """Test individual retrieval sources."""
    
    print("\n🧪 Testing Individual Retrieval Sources")
    print("=" * 50)
    
    try:
        agent = RetrievalAgent()
        query = "machine learning artificial intelligence"
        
        # Test Meilisearch
        print("\n🔍 Testing Meilisearch Search:")
        try:
            meili_result = await agent.meilisearch_search(query, top_k=5)
            print(f"✅ Meilisearch: {len(meili_result.documents)} results")
            if meili_result.documents:
                doc = meili_result.documents[0]
                print(f"  - [{doc.source}] {doc.content[:80]}...")
        except Exception as e:
            print(f"❌ Meilisearch test failed: {e}")
        
        # Test ArangoDB Graph Search
        print("\n🔍 Testing ArangoDB Graph Search:")
        try:
            arango_result = await agent.arangodb_graph_search(query, top_k=5)
            print(f"✅ ArangoDB: {len(arango_result.documents)} results")
            if arango_result.documents:
                doc = arango_result.documents[0]
                print(f"  - [{doc.source}] {doc.content[:80]}...")
        except Exception as e:
            print(f"❌ ArangoDB test failed: {e}")
        
        print("✅ Individual source tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Individual source tests failed: {e}")
        return False


async def main():
    """Run the tests."""
    print("🚀 Starting Multi-Source Retrieval Tests")
    print("=" * 60)
    
    # Test basic integration
    success1 = await test_basic_integration()
    
    # Test individual sources
    success2 = await test_individual_sources()
    
    if success1 and success2:
        print("\n✅ All tests passed! Multi-source retrieval integration is working.")
    else:
        print("\n❌ Some tests failed. Check the logs for details.")
    
    return success1 and success2


if __name__ == "__main__":
    asyncio.run(main()) 