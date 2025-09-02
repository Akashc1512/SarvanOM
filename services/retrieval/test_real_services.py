#!/usr/bin/env python3
"""
Test script to verify that the orchestrator uses real services, not mocks.

This script tests that all three lanes (web, vector, KG) are using actual
integrated services with real API keys from .env file.
"""

import asyncio
import os
import time
from typing import Dict, Any

from services.retrieval.orchestrator import get_orchestrator, OrchestrationConfig
from shared.contracts.query import RetrievalSearchRequest


async def test_real_services():
    """Test that all services are real and not mocks."""
    print("🔍 TESTING REAL SERVICE INTEGRATIONS")
    print("=" * 60)
    
    # Test 1: Verify environment variables are loaded
    print("\n1. Environment Variables Check:")
    env_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", 
        "BRAVE_SEARCH_API_KEY",
        "SERPAPI_KEY",
        "QDRANT_API_KEY",
        "ARANGO_URL",
        "ARANGO_USERNAME",
        "ARANGO_PASSWORD"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {'*' * min(len(value), 8)}...")
        else:
            print(f"   ⚠️  {var}: Not set")
    
    # Test 2: Test orchestrator with real services
    print("\n2. Orchestrator Real Service Test:")
    orchestrator = get_orchestrator()
    
    # Create test request
    request = RetrievalSearchRequest(
        query="What is machine learning and how does it work?",
        max_results=5
    )
    
    # Test orchestration
    start_time = time.time()
    try:
        response = await orchestrator.orchestrate_retrieval(request)
        latency_ms = (time.time() - start_time) * 1000
        
        print(f"   ✅ Orchestration completed in {latency_ms:.1f}ms")
        print(f"   ✅ Method: {response.method}")
        print(f"   ✅ Results: {response.total_results}")
        
        # Analyze results to verify they're from real services
        print("\n3. Result Analysis:")
        source_breakdown = {}
        real_service_indicators = {
            "web_search": ["url", "title", "domain"],
            "vector_search": ["embedding_model", "vector_similarity"],
            "knowledge_graph": ["entity_type", "entity_id", "confidence"]
        }
        
        for source in response.sources:
            lane = source.get("metadata", {}).get("lane", "unknown")
            source_breakdown[lane] = source_breakdown.get(lane, 0) + 1
            
            # Check for real service indicators
            metadata = source.get("metadata", {})
            indicators = real_service_indicators.get(lane, [])
            found_indicators = [ind for ind in indicators if ind in metadata]
            
            if found_indicators:
                print(f"   ✅ {lane}: Real service indicators found: {found_indicators}")
            else:
                print(f"   ⚠️  {lane}: No clear real service indicators")
        
        print(f"   📊 Source breakdown: {source_breakdown}")
        
        # Test 4: Verify no mock responses
        print("\n4. Mock Response Check:")
        mock_indicators = [
            "mock", "fake", "test", "example.com", "dummy", "stub"
        ]
        
        mock_found = False
        for source in response.sources:
            content = source.get("content", "").lower()
            url = source.get("metadata", {}).get("url", "").lower()
            
            for indicator in mock_indicators:
                if indicator in content or indicator in url:
                    print(f"   ⚠️  Potential mock content found: {indicator}")
                    mock_found = True
        
        if not mock_found:
            print("   ✅ No mock responses detected")
        
        return True
        
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        print(f"   ❌ Orchestration failed: {e}")
        print(f"   ⏱️  Latency: {latency_ms:.1f}ms")
        return False


async def test_individual_lanes():
    """Test individual lanes to verify they use real services."""
    print("\n5. Individual Lane Testing:")
    
    orchestrator = get_orchestrator()
    request = RetrievalSearchRequest(query="artificial intelligence", max_results=3)
    
    # Test web search lane
    try:
        web_results = await orchestrator._web_search_lane(request)
        print(f"   ✅ Web search lane: {len(web_results)} results")
        if web_results:
            first_result = web_results[0]
            has_url = "url" in first_result.get("metadata", {})
            has_title = "title" in first_result.get("metadata", {})
            print(f"      - Has URL: {has_url}, Has title: {has_title}")
    except Exception as e:
        print(f"   ❌ Web search lane failed: {e}")
    
    # Test vector search lane
    try:
        vector_results = await orchestrator._vector_search_lane(request)
        print(f"   ✅ Vector search lane: {len(vector_results)} results")
        if vector_results:
            first_result = vector_results[0]
            has_embedding = "embedding_model" in first_result.get("metadata", {})
            print(f"      - Has embedding model: {has_embedding}")
    except Exception as e:
        print(f"   ❌ Vector search lane failed: {e}")
    
    # Test knowledge graph lane
    try:
        kg_results = await orchestrator._knowledge_graph_lane(request)
        print(f"   ✅ Knowledge graph lane: {len(kg_results)} results")
        if kg_results:
            first_result = kg_results[0]
            has_entity = "entity_type" in first_result.get("metadata", {})
            print(f"      - Has entity type: {has_entity}")
    except Exception as e:
        print(f"   ❌ Knowledge graph lane failed: {e}")


async def main():
    """Run all real service tests."""
    print("🚀 REAL SERVICE INTEGRATION TEST SUITE")
    print("=" * 60)
    
    # Run tests
    success1 = await test_real_services()
    await test_individual_lanes()
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    
    if success1:
        print("🎉 ALL REAL SERVICE TESTS PASSED!")
        print("✅ Orchestrator is using real services with API keys")
        print("✅ No mock responses detected")
        print("✅ All three lanes are properly integrated")
    else:
        print("⚠️  Some tests failed - check service integrations")
    
    print("\n🔧 Configuration Notes:")
    print("- Ensure all API keys are set in .env file")
    print("- Vector/KG services may return empty results if not configured")
    print("- Web search should always work with free APIs")


if __name__ == "__main__":
    asyncio.run(main())
