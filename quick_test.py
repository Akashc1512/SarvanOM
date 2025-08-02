#!/usr/bin/env python3
"""
Quick test to verify hybrid retrieval is working with sample documents.
"""

import asyncio
import sys
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.search_service.core.hybrid_retrieval import (
    HybridRetrievalEngine,
    FusionStrategy,
    RetrievalSource
)


async def quick_test():
    """Quick test of hybrid retrieval with sample documents."""
    print("🔍 Quick Test of Hybrid Retrieval with Sample Documents")
    print("=" * 60)
    
    # Create engine
    engine = HybridRetrievalEngine()
    
    # Test queries that should match our sample documents
    test_queries = [
        "machine learning algorithms",
        "Python async programming",
        "React hooks state management",
        "Kubernetes container orchestration",
        "deep learning neural networks",
        "API authentication best practices"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: '{query}'")
        
        try:
            result = await engine.retrieve(
                query=query,
                max_results=5,
                fusion_strategy=FusionStrategy.WEIGHTED_SUM,
                sources=[RetrievalSource.MEILISEARCH, RetrievalSource.VECTOR_DB]
            )
            
            print(f"   Results found: {len(result.enhanced_results)}")
            print(f"   Confidence: {result.confidence_score:.3f}")
            print(f"   Processing time: {result.processing_time_ms:.2f}ms")
            
            if len(result.enhanced_results) > 0:
                print("   ✅ Found results!")
                for j, doc in enumerate(result.enhanced_results[:2], 1):
                    print(f"     {j}. {doc.title}")
                    print(f"        Score: {doc.combined_score:.3f}")
                    print(f"        Sources: {doc.source_types}")
            else:
                print("   ❌ No results found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🎉 Quick test completed!")


async def main():
    """Main function."""
    try:
        await quick_test()
        return 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 