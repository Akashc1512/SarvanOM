#!/usr/bin/env python3
"""
Test Phase C1: Optimized Retrieval Performance

Tests the new performance optimizations:
- Per-provider circuit breakers
- Individual provider timeouts
- Health-aware execution
- Performance monitoring
"""

import asyncio
import time
from services.retrieval.free_tier import ZeroBudgetRetrieval

async def test_optimized_retrieval():
    """Test the optimized retrieval service."""
    print("🚀 Testing Phase C1: Optimized Retrieval Performance")
    
    # Initialize retrieval service
    retrieval_service = ZeroBudgetRetrieval()
    
    # Test query
    query = "machine learning algorithms"
    print(f"\n📊 Testing query: '{query}'")
    print(f"🎯 Target: ≥6 unique sources in ≤3.0s")
    
    # Get initial health status
    initial_health = retrieval_service.get_health_summary()
    print(f"\n🔍 Initial Provider Health:")
    for provider, health in initial_health['provider_details'].items():
        status_emoji = "✅" if health['status'] == 'healthy' else "⚠️" if health['status'] == 'degraded' else "❌"
        print(f"   {status_emoji} {provider}: {health['status']} (avg: {health['avg_response_time']:.3f}s)")
    
    # Execute search with timing
    start_time = time.time()
    print(f"\n🔍 Executing search...")
    
    try:
        response = await retrieval_service.search(query, k=10, use_wiki=True, use_web=True)
        
        total_time = time.time() - start_time
        total_time_ms = total_time * 1000
        
        print(f"\n📋 Results Analysis:")
        print(f"   Total results: {response.total_results}")
        print(f"   Total time: {total_time:.3f}s")
        print(f"   Processing time: {response.processing_time_ms:.2f}ms")
        print(f"   Cache hit: {response.cache_hit}")
        
        # Analyze sources
        domains = set()
        providers = set()
        for result in response.results:
            domains.add(result.domain)
            providers.add(result.provider.value)
        
        print(f"\n🔍 Sources Found:")
        print(f"   Unique domains: {len(domains)} - {list(domains)[:5]}{'...' if len(domains) > 5 else ''}")
        print(f"   Unique providers: {len(providers)} - {list(providers)}")
        
        # Check requirements
        sla_compliant = total_time_ms <= 3000
        sufficient_sources = len(domains) >= 6
        
        print(f"\n🎯 Phase C1 Requirement Check:")
        print(f"   Target: ≥6 unique sources")
        print(f"   Actual: {len(domains)} unique domains")
        print(f"   Target: P95 ≤3.0s")
        print(f"   Actual: {total_time:.3f}s")
        print(f"   SLA compliant: {'✅' if sla_compliant else '❌'}")
        print(f"   Sufficient sources: {'✅' if sufficient_sources else '❌'}")
        
        if sla_compliant and sufficient_sources:
            print(f"\n🎉 Phase C1: Requirements MET!")
        else:
            print(f"\n❌ Phase C1: Requirements not met")
        
        # Get final health status
        final_health = retrieval_service.get_health_summary()
        print(f"\n🔍 Final Provider Health:")
        for provider, health in final_health['provider_details'].items():
            status_emoji = "✅" if health['status'] == 'healthy' else "⚠️" if health['status'] == 'degraded' else "❌"
            print(f"   {status_emoji} {provider}: {health['status']} (avg: {health['avg_response_time']:.3f}s)")
        
        # Performance metrics
        print(f"\n📊 Performance Metrics:")
        print(f"   Overall health: {final_health['overall_health']['health_percentage']:.1f}%")
        print(f"   Total requests: {final_health['performance_metrics']['total_requests']}")
        
        return sla_compliant and sufficient_sources
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await retrieval_service.close()

async def test_provider_timeouts():
    """Test individual provider timeouts."""
    print(f"\n⏱️ Testing Provider Timeouts:")
    
    retrieval_service = ZeroBudgetRetrieval()
    
    # Test each provider's timeout configuration
    providers = ['wikipedia', 'stackexchange', 'mdn', 'github', 'openalex', 'arxiv', 'youtube', 'duckduckgo']
    
    for provider in providers:
        timeout = retrieval_service._get_provider_timeout(provider)
        print(f"   {provider}: {timeout*1000:.0f}ms")
    
    await retrieval_service.close()

if __name__ == "__main__":
    print("🧪 Phase C1 Performance Optimization Test")
    print("=" * 60)
    
    try:
        # Test provider timeouts
        asyncio.run(test_provider_timeouts())
        
        # Test optimized retrieval
        success = asyncio.run(test_optimized_retrieval())
        
        if success:
            print(f"\n🎉 All tests completed successfully!")
        else:
            print(f"\n⚠️ Tests completed with issues - review output above")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
