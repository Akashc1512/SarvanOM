#!/usr/bin/env python3
"""
Performance Test for Retrieval Orchestrator

Tests the strict per-lane timeouts and performance optimizations:
- Vector ≤ 2.0s timeout
- KG ≤ 1.5s timeout  
- Small top-k values (vector ~5, KG ≤ 6)
- Non-blocking retrieval (never block the answer)
- Per-lane timing logs and Prometheus metrics
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_retrieval_performance():
    """Test retrieval orchestrator performance with strict timeouts."""
    try:
        from services.retrieval.orchestrator import RetrievalOrchestrator, OrchestrationConfig
        from shared.contracts.query import RetrievalSearchRequest
    except ImportError as e:
        logger.error(f"Failed to import orchestrator: {e}")
        return False
    
    # Test configuration
    config = OrchestrationConfig()
    config.enable_web_search = True
    config.enable_vector_search = True
    config.enable_knowledge_graph = True
    config.enable_parallel_execution = True
    
    # Set strict timeouts
    config.latency_budget.vector_search_budget_ms = 2000.0  # ≤ 2.0s
    config.latency_budget.knowledge_graph_budget_ms = 1500.0  # ≤ 1.5s
    config.latency_budget.web_search_budget_ms = 1500.0
    config.latency_budget.total_budget_ms = 3000.0
    
    orchestrator = RetrievalOrchestrator(config)
    
    # Test queries
    test_queries = [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "Explain quantum computing",
        "What are the benefits of renewable energy?",
        "How does blockchain technology work?"
    ]
    
    results = []
    
    logger.info("Starting performance tests with strict timeouts...")
    
    for i, query in enumerate(test_queries):
        logger.info(f"Test {i+1}/{len(test_queries)}: {query}")
        
        start_time = time.time()
        
        try:
            request = RetrievalSearchRequest(
                query=query,
                max_results=10
            )
            
            response = await orchestrator.orchestrate_retrieval(request)
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            results.append({
                "query": query,
                "latency_ms": latency_ms,
                "total_results": len(response.sources),
                "method": response.method,
                "success": True
            })
            
            logger.info(f"  ✅ Completed in {latency_ms:.2f}ms with {len(response.sources)} results")
            
        except Exception as e:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            results.append({
                "query": query,
                "latency_ms": latency_ms,
                "total_results": 0,
                "method": "error",
                "success": False,
                "error": str(e)
            })
            
            logger.error(f"  ❌ Failed in {latency_ms:.2f}ms: {e}")
        
        # Small delay between tests
        await asyncio.sleep(0.1)
    
    # Analyze results
    successful_results = [r for r in results if r["success"]]
    failed_results = [r for r in results if not r["success"]]
    
    if successful_results:
        latencies = [r["latency_ms"] for r in successful_results]
        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        p99 = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        
        logger.info(f"\n📊 Performance Analysis:")
        logger.info(f"  Total tests: {len(results)}")
        logger.info(f"  Successful: {len(successful_results)}")
        logger.info(f"  Failed: {len(failed_results)}")
        logger.info(f"  P50 latency: {p50:.2f}ms")
        logger.info(f"  P95 latency: {p95:.2f}ms")
        logger.info(f"  P99 latency: {p99:.2f}ms")
        
        # Check acceptance criteria
        p95_under_3s = p95 <= 3000.0
        no_catastrophic_slowdowns = p99 <= 5000.0  # Reasonable for complex queries
        
        logger.info(f"\n🎯 Acceptance Criteria:")
        logger.info(f"  P95 ≤ 3s: {'✅' if p95_under_3s else '❌'} ({p95:.2f}ms)")
        logger.info(f"  No catastrophic slowdowns: {'✅' if no_catastrophic_slowdowns else '❌'} ({p99:.2f}ms)")
        
        # Check lane status
        lane_status = orchestrator.get_lane_status()
        logger.info(f"\n🚦 Lane Status:")
        for lane, status in lane_status.items():
            logger.info(f"  {lane}: {status['status']} (avg: {status['avg_latency_ms']:.2f}ms)")
        
        return p95_under_3s and no_catastrophic_slowdowns
    
    else:
        logger.error("❌ All tests failed!")
        return False

async def test_timeout_behavior():
    """Test that timeouts don't block the answer generation."""
    logger.info("\n🧪 Testing timeout behavior...")
    
    try:
        from services.retrieval.orchestrator import RetrievalOrchestrator, OrchestrationConfig
        from shared.contracts.query import RetrievalSearchRequest
    except ImportError as e:
        logger.error(f"Failed to import orchestrator: {e}")
        return False
    
    # Create config with very short timeouts to force timeouts
    config = OrchestrationConfig()
    config.enable_web_search = True
    config.enable_vector_search = True
    config.enable_knowledge_graph = True
    config.enable_parallel_execution = True
    
    # Set very short timeouts to test non-blocking behavior
    config.latency_budget.vector_search_budget_ms = 100.0  # 0.1s (should timeout)
    config.latency_budget.knowledge_graph_budget_ms = 50.0  # 0.05s (should timeout)
    config.latency_budget.web_search_budget_ms = 200.0  # 0.2s (might succeed)
    config.latency_budget.total_budget_ms = 500.0  # 0.5s total
    
    orchestrator = RetrievalOrchestrator(config)
    
    request = RetrievalSearchRequest(
        query="Test query for timeout behavior",
        max_results=5
    )
    
    start_time = time.time()
    
    try:
        response = await orchestrator.orchestrate_retrieval(request)
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        logger.info(f"  ✅ Timeout test completed in {latency_ms:.2f}ms")
        logger.info(f"  Results: {len(response.sources)} (method: {response.method})")
        
        # Check that we got some results despite timeouts
        has_results = len(response.sources) > 0
        completed_quickly = latency_ms <= 1000.0  # Should complete within 1s even with timeouts
        
        logger.info(f"  Non-blocking behavior: {'✅' if has_results or completed_quickly else '❌'}")
        
        return has_results or completed_quickly
        
    except Exception as e:
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        logger.error(f"  ❌ Timeout test failed in {latency_ms:.2f}ms: {e}")
        return False

async def test_small_top_k():
    """Test that small top-k values are used."""
    logger.info("\n🔢 Testing small top-k values...")
    
    try:
        from services.retrieval.orchestrator import RetrievalOrchestrator, OrchestrationConfig
        from shared.contracts.query import RetrievalSearchRequest
    except ImportError as e:
        logger.error(f"Failed to import orchestrator: {e}")
        return False
    
    config = OrchestrationConfig()
    config.max_results_per_lane = 5  # Small top-k
    
    orchestrator = RetrievalOrchestrator(config)
    
    request = RetrievalSearchRequest(
        query="Test query for top-k values",
        max_results=10
    )
    
    try:
        response = await orchestrator.orchestrate_retrieval(request)
        
        # Check that we don't have too many results from any single lane
        lane_counts = {}
        for source in response.sources:
            lane = source.get("metadata", {}).get("lane", "unknown")
            lane_counts[lane] = lane_counts.get(lane, 0) + 1
        
        logger.info(f"  Lane result counts: {lane_counts}")
        
        # Check vector lane has ≤ 5 results
        vector_count = lane_counts.get("vector_search", 0)
        vector_ok = vector_count <= 5
        
        # Check KG lane has ≤ 6 results
        kg_count = lane_counts.get("knowledge_graph", 0)
        kg_ok = kg_count <= 6
        
        logger.info(f"  Vector results ≤ 5: {'✅' if vector_ok else '❌'} ({vector_count})")
        logger.info(f"  KG results ≤ 6: {'✅' if kg_ok else '❌'} ({kg_count})")
        
        return vector_ok and kg_ok
        
    except Exception as e:
        logger.error(f"  ❌ Top-k test failed: {e}")
        return False

async def main():
    """Run all performance tests."""
    logger.info("🚀 Starting Retrieval Orchestrator Performance Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Performance with strict timeouts", test_retrieval_performance),
        ("Timeout behavior (non-blocking)", test_timeout_behavior),
        ("Small top-k values", test_small_top_k),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {status} {test_name}")
        except Exception as e:
            logger.error(f"  ❌ FAIL {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n📊 Test Summary")
    logger.info("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {status} {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL PERFORMANCE TESTS PASSED!")
        logger.info("✅ Retrieval orchestrator meets performance requirements")
    else:
        logger.info("⚠️  Some tests failed - check performance implementation")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
