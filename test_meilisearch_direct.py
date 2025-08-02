from shared.core.api.config import get_settings
#!/usr/bin/env python3
settings = get_settings()
"""
Direct test of Meilisearch engine to see what scores are being returned.
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


async def test_meilisearch_direct():
    """Test Meilisearch engine directly."""
    print("🔍 Direct Meilisearch Test")
    print("=" * 40)
    
    # Create engine
    meilisearch_url = settings.meilisearch_url or "http://localhost:7700"
    meilisearch_api_key = settings.meilisearch_api_key
    
    engine = MeilisearchEngine(meilisearch_url, meilisearch_api_key)
    
    # Test queries
    test_queries = [
        "machine learning algorithms",
        "Python async programming",
        "React hooks state management"
    ]
    
    for query in test_queries:
        print(f"\n📋 Query: '{query}'")
        
        try:
            results = await engine.search(query, top_k=3)
            
            print(f"   Found {len(results)} results")
            
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result.metadata.get('title', 'Unknown')}")
                print(f"      Raw Score: {result.metadata.get('raw_score', 'N/A')}")
                print(f"      Normalized Score: {result.score}")
                print(f"      Content Preview: {result.content[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    await engine.close()


async def main():
    """Main function."""
    try:
        await test_meilisearch_direct()
        return 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 