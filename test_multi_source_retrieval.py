#!/usr/bin/env python3
"""
Test script for multi-source retrieval integration.
Tests the enhanced RetrievalAgent with Meilisearch and ArangoDB integration.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.search_service.retrieval_agent import RetrievalAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_multi_source_retrieval():
    """Test the multi-source retrieval functionality."""
    
    print("🧪 Testing Multi-Source Retrieval Integration")
    print("=" * 50)
    
    # Initialize the retrieval agent
    agent = RetrievalAgent()
    
    # Test queries
    test_queries = [
        "What is machine learning?",
        "How does deep learning relate to neural networks?",
        "Explain the relationship between Python and AI development",
        "What are the differences between Docker and Kubernetes?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 40)
        
        try:
            # Perform hybrid retrieval
            result = await agent.hybrid_retrieve(query)
            
            print(f"✅ Search completed in {result.query_time_ms}ms")
            print(f"📊 Total hits: {result.total_hits}")
            print(f"🎯 Search type: {result.search_type}")
            
            # Show metadata
            if result.metadata:
                print(f"📋 Metadata: {result.metadata}")
            
            # Show top results
            print(f"\n📄 Top {min(3, len(result.documents))} results:")
            for j, doc in enumerate(result.documents[:3], 1):
                print(f"  {j}. [{doc.source}] Score: {doc.score:.3f}")
                print(f"     Content: {doc.content[:100]}...")
                if doc.metadata:
                    print(f"     Metadata: {doc.metadata}")
                print()
                
        except Exception as e:
            print(f"❌ Error testing query '{query}': {e}")
            logger.error(f"Test failed for query: {query}", exc_info=True)
    
    print("\n🎉 Multi-source retrieval test completed!")


async def test_individual_sources():
    """Test individual retrieval sources."""
    
    print("\n🧪 Testing Individual Retrieval Sources")
    print("=" * 50)
    
    agent = RetrievalAgent()
    query = "machine learning artificial intelligence"
    
    # Test Meilisearch
    print("\n🔍 Testing Meilisearch Search:")
    try:
        meili_result = await agent.meilisearch_search(query, top_k=5)
        print(f"✅ Meilisearch: {len(meili_result.documents)} results")
        for doc in meili_result.documents[:2]:
            print(f"  - [{doc.source}] {doc.content[:80]}...")
    except Exception as e:
        print(f"❌ Meilisearch test failed: {e}")
    
    # Test ArangoDB Graph Search
    print("\n🔍 Testing ArangoDB Graph Search:")
    try:
        arango_result = await agent.arangodb_graph_search(query, top_k=5)
        print(f"✅ ArangoDB: {len(arango_result.documents)} results")
        for doc in arango_result.documents[:2]:
            print(f"  - [{doc.source}] {doc.content[:80]}...")
    except Exception as e:
        print(f"❌ ArangoDB test failed: {e}")
    
    # Test Vector Search
    print("\n🔍 Testing Vector Search:")
    try:
        vector_result = await agent.vector_search(query, top_k=5)
        print(f"✅ Vector: {len(vector_result.documents)} results")
        for doc in vector_result.documents[:2]:
            print(f"  - [{doc.source}] {doc.content[:80]}...")
    except Exception as e:
        print(f"❌ Vector search test failed: {e}")


async def test_entity_extraction():
    """Test entity extraction functionality."""
    
    print("\n🧪 Testing Entity Extraction")
    print("=" * 50)
    
    agent = RetrievalAgent()
    test_queries = [
        "What is the relationship between machine learning and artificial intelligence?",
        "How does Python compare to JavaScript for web development?",
        "Explain the differences between Docker containers and Kubernetes orchestration",
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        try:
            entities = await agent._extract_entities(query)
            print(f"✅ Extracted {len(entities)} entities:")
            for entity in entities:
                print(f"  - {entity['text']} ({entity['type']}, confidence: {entity['confidence']:.2f})")
        except Exception as e:
            print(f"❌ Entity extraction failed: {e}")


async def main():
    """Run all tests."""
    print("🚀 Starting Multi-Source Retrieval Tests")
    print("=" * 60)
    
    # Test entity extraction
    await test_entity_extraction()
    
    # Test individual sources
    await test_individual_sources()
    
    # Test hybrid retrieval
    await test_multi_source_retrieval()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main()) 