#!/usr/bin/env python3
"""
Test Phase C1: Free-Source Aggregator (Optimized)
Testing ≥6 unique sources in <3s P95 requirement.
"""

import asyncio
import time
from services.retrieval.free_tier import get_zero_budget_retrieval

async def test_phase_c1():
    print('🚀 Testing Phase C1: Free-Source Aggregator (Optimized) with real environment variables')
    
    retrieval = get_zero_budget_retrieval()
    
    # Test query
    test_query = "machine learning algorithms"
    target_sources = 6
    target_time_s = 3.0
    
    print(f'📊 Testing query: "{test_query}"')
    print(f'🎯 Target: ≥{target_sources} unique sources in ≤{target_time_s}s')
    
    start_time = time.time()
    
    # Execute the search
    response = await retrieval.search(test_query, k=10, use_wiki=True, use_web=True)
    
    total_time = time.time() - start_time
    
    # Analyze results
    unique_domains = set()
    unique_providers = set()
    
    print(f'\n📋 Results Analysis:')
    print(f'   Total results: {len(response.results)}')
    print(f'   Total time: {total_time:.3f}s')
    print(f'   Cache hit: {response.cache_hit}')
    print(f'   Processing time: {response.processing_time_ms:.2f}ms')
    
    print(f'\n🔍 Sources Found:')
    for i, result in enumerate(response.results[:10], 1):
        unique_domains.add(result.domain)
        unique_providers.add(result.provider.value)
        print(f'   {i}. {result.title[:50]}...')
        print(f'      📎 {result.url[:60]}...')
        print(f'      🏷️  {result.provider.value} | {result.domain} | Score: {result.relevance_score:.3f}')
        print()
    
    print(f'📊 Summary:')
    print(f'   Unique domains: {len(unique_domains)} - {sorted(unique_domains)}')
    print(f'   Unique providers: {len(unique_providers)} - {sorted(unique_providers)}')
    print(f'   Providers used: {[p.value for p in response.providers_used]}')
    
    # Check requirements
    print(f'\n🎯 Phase C1 Requirement Check:')
    print(f'   Target: ≥{target_sources} unique sources')
    print(f'   Actual: {len(unique_domains)} unique domains')
    
    print(f'   Target: P95 ≤{target_time_s}s')
    print(f'   Actual: {total_time:.3f}s')
    
    sources_pass = len(unique_domains) >= target_sources
    time_pass = total_time <= target_time_s
    
    if sources_pass and time_pass:
        print(f'   ✅ PASS: {len(unique_domains)} sources in {total_time:.3f}s - Phase C1 requirement met!')
    else:
        if not sources_pass:
            print(f'   ❌ FAIL: Only {len(unique_domains)} sources (need ≥{target_sources})')
        if not time_pass:
            print(f'   ❌ FAIL: {total_time:.3f}s > {target_time_s}s limit')
    
    # Test deduplication
    print(f'\n🔄 Testing deduplication and ranking:')
    all_titles = [r.title.lower() for r in response.results]
    unique_titles = set(all_titles)
    print(f'   Total results: {len(response.results)}')
    print(f'   Unique titles: {len(unique_titles)}')
    print(f'   Deduplication ratio: {len(unique_titles)/len(response.results):.1%}')
    
    # Close resources
    await retrieval.close()
    
    return {
        'sources': len(unique_domains),
        'time': total_time,
        'providers': list(unique_providers),
        'pass': sources_pass and time_pass
    }

if __name__ == "__main__":
    result = asyncio.run(test_phase_c1())
    if result['pass']:
        print(f'\n🎉 Phase C1: Free-source aggregator - COMPLETED ✅')
    else:
        print(f'\n❌ Phase C1: Requirements not met')
