#!/usr/bin/env python3
"""
Test script for the enhanced retrieval orchestrator.

This script tests the three-lane parallel retrieval system with different
scenarios: vector/KG up, vector/KG down, and mixed availability.
"""

import asyncio
import os
import time
from typing import Dict, Any

from services.retrieval.orchestrator import get_orchestrator, OrchestrationConfig
from shared.contracts.query import RetrievalSearchRequest


async def test_orchestrator_scenario(
    scenario_name: str,
    config_overrides: Dict[str, Any],
    query: str = "What is machine learning?"
):
    """Test orchestrator with specific configuration."""
    print(f"\n🧪 Testing Scenario: {scenario_name}")
    print("-" * 40)
    
    # Create custom config
    config = OrchestrationConfig()
    for key, value in config_overrides.items():
        setattr(config, key, value)
    
    # Create orchestrator with custom config
    orchestrator = get_orchestrator()
    orchestrator.config = config
    
    # Create test request
    request = RetrievalSearchRequest(query=query, max_results=5)
    
    # Test orchestration
    start_time = time.time()
    try:
        response = await orchestrator.orchestrate_retrieval(request)
        latency_ms = (time.time() - start_time) * 1000
        
        print(f"✅ Status: SUCCESS")
        print(f"   Method: {response.method}")
        print(f"   Results: {response.total_results}")
        print(f"   Latency: {latency_ms:.1f}ms")
        print(f"   Sources: {len(response.sources)}")
        
        # Show source breakdown
        source_breakdown = {}
        for source in response.sources:
            lane = source.get("metadata", {}).get("lane", "unknown")
            source_breakdown[lane] = source_breakdown.get(lane, 0) + 1
        
        print(f"   Source breakdown: {source_breakdown}")
        
        return True
        
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        print(f"❌ Status: FAILED")
        print(f"   Error: {e}")
        print(f"   Latency: {latency_ms:.1f}ms")
        return False


async def main():
    """Run all test scenarios."""
    print("🚀 ENHANCED RETRIEVAL ORCHESTRATOR TEST SUITE")
    print("=" * 60)
    
    # Test scenarios
    scenarios = [
        {
            "name": "All Lanes Enabled",
            "config": {
                "enable_web_search": True,
                "enable_vector_search": True,
                "enable_knowledge_graph": True,
                "enable_parallel_execution": True
            }
        },
        {
            "name": "Vector/KG Down (Web Only)",
            "config": {
                "enable_web_search": True,
                "enable_vector_search": False,
                "enable_knowledge_graph": False,
                "enable_parallel_execution": True
            }
        },
        {
            "name": "Web Down (Vector/KG Only)",
            "config": {
                "enable_web_search": False,
                "enable_vector_search": True,
                "enable_knowledge_graph": True,
                "enable_parallel_execution": True
            }
        },
        {
            "name": "Sequential Execution",
            "config": {
                "enable_web_search": True,
                "enable_vector_search": True,
                "enable_knowledge_graph": True,
                "enable_parallel_execution": False
            }
        },
        {
            "name": "Strict Timeout (1s)",
            "config": {
                "enable_web_search": True,
                "enable_vector_search": True,
                "enable_knowledge_graph": True,
                "enable_parallel_execution": True,
                "latency_budget": type('LatencyBudget', (), {
                    'total_budget_ms': 1000.0,
                    'web_search_budget_ms': 500.0,
                    'vector_search_budget_ms': 300.0,
                    'knowledge_graph_budget_ms': 300.0,
                    'fusion_budget_ms': 100.0
                })()
            }
        }
    ]
    
    # Run tests
    results = []
    for scenario in scenarios:
        success = await test_orchestrator_scenario(
            scenario["name"],
            scenario["config"]
        )
        results.append((scenario["name"], success))
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - ORCHESTRATOR READY FOR PRODUCTION!")
    else:
        print("⚠️  Some tests failed - check implementation")


if __name__ == "__main__":
    asyncio.run(main())
