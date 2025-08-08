#!/usr/bin/env python3
"""
Test script for migrated backend components.

This script tests the clean architecture implementation to ensure
the migrated components work correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.models.domain.query import Query, QueryContext, QueryType
from backend.models.domain.agent import AgentType
from backend.services.core.cache_service import CacheService
from backend.services.core.metrics_service import MetricsService
from backend.services.agents.agent_coordinator import AgentCoordinator
from backend.services.agents.agent_factory import AgentFactory
from backend.services.query.query_processor import QueryProcessor
from backend.services.query.query_validator import QueryValidator
from backend.services.query.query_orchestrator import QueryOrchestrator


async def test_domain_models():
    """Test domain models functionality."""
    print("Testing domain models...")
    
    # Test Query creation
    context = QueryContext(
        user_id="test_user",
        session_id="test_session",
        max_tokens=1000,
        confidence_threshold=0.8,
        metadata={"test": "data"}
    )
    
    query = Query(
        id="test_query_1",
        text="What is the capital of France?",
        context=context,
        query_type=QueryType.BASIC
    )
    
    print(f"✓ Query created: {query.id}")
    print(f"✓ Query text: {query.text}")
    print(f"✓ Query type: {query.query_type}")
    print(f"✓ Query status: {query.status}")
    
    # Test status transitions
    query.mark_processing()
    print(f"✓ Query marked as processing: {query.status}")
    
    query.mark_completed({
        "answer": "Paris is the capital of France.",
        "confidence": 0.95,
        "processing_time": 1.5
    })
    print(f"✓ Query marked as completed: {query.status}")
    
    return True


async def test_core_services():
    """Test core services functionality."""
    print("\nTesting core services...")
    
    # Test CacheService
    cache_service = CacheService()
    
    # Test set and get
    await cache_service.set("test_key", {"data": "test_value"}, ttl=60)
    cached_value = await cache_service.get("test_key")
    
    if cached_value and cached_value.get("data") == "test_value":
        print("✓ CacheService set/get working")
    else:
        print("✗ CacheService set/get failed")
        return False
    
    # Test MetricsService
    metrics_service = MetricsService()
    
    # Track some metrics
    await metrics_service.track_query_processing(
        query_id="test_query",
        query_type="basic",
        processing_time=1.5,
        cache_hit=False
    )
    
    metrics = metrics_service.get_metrics_summary()
    if metrics.get("total_queries", 0) > 0:
        print("✓ MetricsService tracking working")
    else:
        print("✗ MetricsService tracking failed")
        return False
    
    return True


async def test_agent_system():
    """Test agent system functionality."""
    print("\nTesting agent system...")
    
    # Test AgentFactory
    agent_factory = AgentFactory()
    
    # Test agent creation
    retrieval_agent = agent_factory.create_agent(AgentType.RETRIEVAL)
    synthesis_agent = agent_factory.create_agent(AgentType.SYNTHESIS)
    fact_check_agent = agent_factory.create_agent(AgentType.FACT_CHECK)
    
    if all([retrieval_agent, synthesis_agent, fact_check_agent]):
        print("✓ AgentFactory creating agents")
    else:
        print("✗ AgentFactory failed to create agents")
        return False
    
    # Test AgentCoordinator
    agent_coordinator = AgentCoordinator()
    
    # Test getting agents
    agent = await agent_coordinator.get_agent(AgentType.RETRIEVAL)
    if agent:
        print("✓ AgentCoordinator getting agents")
    else:
        print("✗ AgentCoordinator failed to get agent")
        return False
    
    return True


async def test_query_processing():
    """Test query processing functionality."""
    print("\nTesting query processing...")
    
    # Create dependencies
    cache_service = CacheService()
    metrics_service = MetricsService()
    agent_factory = AgentFactory()
    agent_coordinator = AgentCoordinator()
    
    # Create query processor
    query_processor = QueryProcessor(agent_coordinator, cache_service)
    
    # Create test query
    context = QueryContext(
        user_id="test_user",
        session_id="test_session",
        max_tokens=1000,
        confidence_threshold=0.8,
        metadata={"test": "data"}
    )
    
    query = Query(
        id="test_query_2",
        text="What is the weather like today?",
        context=context,
        query_type=QueryType.BASIC
    )
    
    try:
        # Test basic query processing
        result = await query_processor.process_basic_query(query)
        
        if result and isinstance(result, dict):
            print("✓ QueryProcessor processing basic queries")
        else:
            print("✗ QueryProcessor failed to process basic query")
            return False
            
    except Exception as e:
        print(f"✗ QueryProcessor error: {e}")
        return False
    
    # Test query validator
    query_validator = QueryValidator()
    
    try:
        await query_validator.validate_query(query)
        print("✓ QueryValidator validating queries")
    except Exception as e:
        print(f"✗ QueryValidator error: {e}")
        return False
    
    return True


async def test_query_orchestrator():
    """Test query orchestrator functionality."""
    print("\nTesting query orchestrator...")
    
    # Create dependencies
    cache_service = CacheService()
    metrics_service = MetricsService()
    agent_factory = AgentFactory()
    agent_coordinator = AgentCoordinator()
    query_processor = QueryProcessor(agent_coordinator, cache_service)
    query_validator = QueryValidator()
    
    # Create orchestrator
    orchestrator = QueryOrchestrator(
        query_processor=query_processor,
        query_validator=query_validator,
        cache_service=cache_service,
        metrics_service=metrics_service
    )
    
    # Test query status
    try:
        status = await orchestrator.get_query_status("nonexistent_query")
        print("✗ Should have raised ValueError for nonexistent query")
        return False
    except ValueError:
        print("✓ QueryOrchestrator properly handling nonexistent queries")
    
    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING MIGRATED BACKEND COMPONENTS")
    print("=" * 60)
    
    tests = [
        ("Domain Models", test_domain_models),
        ("Core Services", test_core_services),
        ("Agent System", test_agent_system),
        ("Query Processing", test_query_processing),
        ("Query Orchestrator", test_query_orchestrator)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The migrated backend is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 