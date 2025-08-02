#!/usr/bin/env python3
"""
Test Meilisearch with master key configuration.
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
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not available")

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.search_service.core.meilisearch_engine import MeilisearchEngine


async def test_with_master_key():
    """Test Meilisearch with master key configuration."""
    print("🔑 Testing Meilisearch with Master Key Configuration")
    print("=" * 55)
    
    # Get environment variables
    meilisearch_url = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
    meilisearch_api_key = os.getenv("MEILISEARCH_API_KEY")
    meili_master_key = os.getenv("MEILI_MASTER_KEY")
    
    print(f"📋 Configuration:")
    print(f"   Meilisearch URL: {meilisearch_url}")
    print(f"   API Key: {'✅ Set' if meilisearch_api_key else '❌ Not set'}")
    print(f"   Master Key: {'✅ Set' if meili_master_key else '❌ Not set'}")
    
    # Create engine with master key
    engine = MeilisearchEngine(meilisearch_url, meili_master_key)
    
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
        
        # 3. Test search with master key
        print("\n📋 Step 3: Search Tests with Master Key")
        test_queries = [
            "machine learning",
            "Python",
            "React",
            "Kubernetes"
        ]
        
        for query in test_queries:
            print(f"\n   🔍 Query: '{query}'")
            results = await engine.search(query, top_k=3)
            print(f"      Found: {len(results)} results")
            
            for i, result in enumerate(results, 1):
                title = result.metadata.get('title', 'Unknown')
                raw_score = result.metadata.get('raw_score', 'N/A')
                calculated_score = result.metadata.get('calculated_score', 'N/A')
                normalized_score = result.score
                print(f"      {i}. {title}")
                print(f"         Raw Score: {raw_score}")
                print(f"         Calculated Score: {calculated_score}")
                print(f"         Final Score: {normalized_score}")
        
        # 4. Test index configuration
        print("\n📋 Step 4: Index Configuration Test")
        try:
            # Try to reconfigure the index
            await engine._configure_index()
            print("   ✅ Index configuration successful")
        except Exception as e:
            print(f"   ❌ Index configuration failed: {e}")
        
        # 5. Test with different search parameters
        print("\n📋 Step 5: Advanced Search Tests")
        
        # Test with filters (should work better with master key)
        print("   🔍 Testing with filters...")
        try:
            results = await engine.search("Python", top_k=5, filters="tags:programming")
            print(f"      Results with filter: {len(results)}")
        except Exception as e:
            print(f"      ❌ Filter test failed: {e}")
        
        # Test with different limits
        print("   🔍 Testing with different limits...")
        results = await engine.search("machine learning", top_k=10)
        print(f"      Results with limit 10: {len(results)}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        await engine.close()


async def main():
    """Main function."""
    try:
        await test_with_master_key()
        return 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 