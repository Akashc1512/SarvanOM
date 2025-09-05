#!/usr/bin/env python3
"""
Test script for Phase C1: Zero-Budget Retrieval SLA Compliance
"""

import asyncio
import time
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the retrieval service
from services.retrieval.free_tier import get_zero_budget_retrieval

async def test_retrieval_sla():
    """Test the retrieval service for SLA compliance."""
    print("\n🚀 Testing Phase C1: Zero-Budget Retrieval SLA Compliance")
    print("=" * 60)
    
    # Set global timeout to 2.8 seconds
    os.environ["GLOBAL_SEARCH_TIMEOUT_MS"] = "2800"
    
    # Set provider timeouts
    os.environ["PROVIDER_TIMEOUT_MS"] = "1000"
    os.environ["WIKIPEDIA_TIMEOUT_MS"] = "800"
    os.environ["STACKEXCHANGE_TIMEOUT_MS"] = "800"
    os.environ["MDN_TIMEOUT_MS"] = "800"
    os.environ["GITHUB_TIMEOUT_MS"] = "800"
    os.environ["OPENALEX_TIMEOUT_MS"] = "800"
    os.environ["ARXIV_TIMEOUT_MS"] = "800"
    os.environ["YOUTUBE_TIMEOUT_MS"] = "800"
    os.environ["DUCKDUCKGO_TIMEOUT_MS"] = "800"
    
    # Get the retrieval service
    retrieval_service = get_zero_budget_retrieval()
    
    # Test queries
    queries = [
        "machine learning algorithms",
        "python async programming",
        "javascript frameworks"
    ]
    
    for query in queries:
        print(f"\n📊 Testing query: '{query}'")
        print(f"🎯 Target: ≥6 unique sources in ≤3.0s")
        
        # Execute search
        start_time = time.time()
        try:
            response = await retrieval_service.search(query, k=10)
            
            # Calculate time
            elapsed_time = time.time() - start_time
            
            # Analyze results
            unique_domains = set(result.domain for result in response.results)
            unique_providers = set(result.provider for result in response.results)
            
            print(f"\n📋 Results Analysis:")
            print(f"   Total results: {len(response.results)}")
            print(f"   Total time: {elapsed_time:.3f}s")
            print(f"   Processing time: {response.processing_time_ms:.2f}ms")
            print(f"   Cache hit: {response.cache_hit}")
            
            print(f"\n🔍 Sources Found:")
            print(f"   Unique domains: {len(unique_domains)} - {list(unique_domains)[:5]}...")
            print(f"   Unique providers: {len(unique_providers)} - {[p.value for p in unique_providers]}")
            
            # Check SLA compliance
            print(f"\n🎯 Phase C1 Requirement Check:")
            print(f"   Target: ≥6 unique sources")
            print(f"   Actual: {len(unique_domains)} unique domains")
            print(f"   Target: P95 ≤3.0s")
            print(f"   Actual: {elapsed_time:.3f}s")
            print(f"   SLA compliant: {'✅' if elapsed_time <= 3.0 else '❌'}")
            print(f"   Sufficient sources: {'✅' if len(unique_domains) >= 6 else '❌'}")
            
            if elapsed_time <= 3.0 and len(unique_domains) >= 6:
                print(f"\n✅ Phase C1: Requirements met!")
            else:
                print(f"\n❌ Phase C1: Requirements not met")
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"\n❌ Error: {e}")
            print(f"   Time before error: {elapsed_time:.3f}s")
    
    # Get provider health
    health_summary = retrieval_service.get_health_summary()
    print(f"\n🔍 Provider Health:")
    for provider, health in health_summary["provider_details"].items():
        status_icon = "✅" if health["status"] == "healthy" else "⚠️"
        print(f"   {status_icon} {provider}: {health['status']} (avg: {health['avg_response_time']:.3f}s)")
    
    print(f"\n📊 Performance Metrics:")
    print(f"   Overall health: {health_summary['overall_health']['health_percentage']:.1f}%")
    print(f"   Total requests: {health_summary['performance_metrics']['total_requests']}")
    
    # Close the retrieval service
    await retrieval_service.close()

if __name__ == "__main__":
    asyncio.run(test_retrieval_sla())
