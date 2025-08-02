#!/usr/bin/env python3
"""
Debug Meilisearch index configuration and scoring issues.
"""

import asyncio
import sys
import os
import logging

# Set logging level to see debug messages
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.search_service.core.meilisearch_engine import MeilisearchEngine


async def debug_meilisearch_index():
    """Debug Meilisearch index configuration and scoring."""
    print("🔍 Debugging Meilisearch Index Configuration")
    print("=" * 50)
    
    # Create engine
    meilisearch_url = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
    meilisearch_api_key = os.getenv("MEILISEARCH_API_KEY")
    
    engine = MeilisearchEngine(meilisearch_url, meilisearch_api_key)
    
    try:
        # 1. Check if Meilisearch is running
        print("\n📋 Step 1: Health Check")
        health = await engine.health_check()
        print(f"   Meilisearch Health: {'✅ Running' if health else '❌ Not Running'}")
        
        # 2. Get index stats
        print("\n📋 Step 2: Index Statistics")
        stats = await engine.get_stats()
        print(f"   Documents in Index: {stats.get('numberOfDocuments', 0)}")
        print(f"   Index Size: {stats.get('rawDocumentDbSize', 0)} bytes")
        print(f"   Average Document Size: {stats.get('avgDocumentSize', 0)} bytes")
        print(f"   Is Indexing: {stats.get('isIndexing', False)}")
        print(f"   Field Distribution: {stats.get('fieldDistribution', {})}")
        
        # 3. Test different search queries
        print("\n📋 Step 3: Search Query Tests")
        test_queries = [
            "machine learning",
            "Python",
            "React",
            "Kubernetes",
            "deep learning",
            "API authentication"
        ]
        
        for query in test_queries:
            print(f"\n   🔍 Query: '{query}'")
            results = await engine.search(query, top_k=3)
            print(f"      Found: {len(results)} results")
            
            for i, result in enumerate(results, 1):
                title = result.metadata.get('title', 'Unknown')
                raw_score = result.metadata.get('raw_score', 'N/A')
                normalized_score = result.score
                print(f"      {i}. {title}")
                print(f"         Raw Score: {raw_score}")
                print(f"         Normalized Score: {normalized_score}")
                print(f"         Content Preview: {result.content[:50]}...")
        
        # 4. Test exact title matches
        print("\n📋 Step 4: Exact Title Match Tests")
        exact_titles = [
            "Machine Learning Algorithms for Natural Language Processing",
            "Python Async Programming Patterns",
            "React Hooks State Management"
        ]
        
        for title in exact_titles:
            print(f"\n   🔍 Exact Title: '{title}'")
            results = await engine.search(title, top_k=1)
            if results:
                result = results[0]
                print(f"      Found: {result.metadata.get('title', 'Unknown')}")
                print(f"      Raw Score: {result.metadata.get('raw_score', 'N/A')}")
                print(f"      Normalized Score: {result.score}")
            else:
                print("      ❌ No exact match found")
        
        # 5. Test with different search parameters
        print("\n📋 Step 5: Advanced Search Tests")
        
        # Test with filters
        print("   🔍 Testing with filters...")
        results = await engine.search("Python", top_k=5, filters="tags:programming")
        print(f"      Results with filter: {len(results)}")
        
        # Test with different limits
        print("   🔍 Testing with different limits...")
        results = await engine.search("machine learning", top_k=10)
        print(f"      Results with limit 10: {len(results)}")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
    finally:
        await engine.close()


async def main():
    """Main function."""
    try:
        await debug_meilisearch_index()
        return 0
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 