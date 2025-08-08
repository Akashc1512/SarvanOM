"""
Test script to verify the new clean architecture structure.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models.domain.query import Query, QueryContext, QueryType
from backend.models.requests.query_requests import QueryRequest
from backend.services.core.cache_service import CacheService
from backend.services.core.metrics_service import MetricsService
from backend.services.query.query_validator import QueryValidator


async def test_domain_models():
    """Test domain models."""
    print("Testing domain models...")
    
    # Test QueryContext
    context = QueryContext(
        user_id="test_user",
        session_id="test_session",
        max_tokens=1000,
        confidence_threshold=0.8
    )
    print(f"✓ QueryContext created: {context.user_id}")
    
    # Test Query
    query = Query(
        id="test_query_id",
        text="What is the capital of France?",
        context=context,
        query_type=QueryType.BASIC
    )
    print(f"✓ Query created: {query.id}")
    
    # Test query validation
    validator = QueryValidator()
    is_valid = await validator.validate_query(query)
    print(f"✓ Query validation: {is_valid}")
    
    return True


async def test_request_models():
    """Test request models."""
    print("Testing request models...")
    
    # Test QueryRequest
    request = QueryRequest(
        query="What is the capital of France?",
        session_id="test_session",
        max_tokens=1000,
        confidence_threshold=0.8
    )
    print(f"✓ QueryRequest created: {request.query}")
    
    return True


async def test_core_services():
    """Test core services."""
    print("Testing core services...")
    
    # Test CacheService
    cache_service = CacheService()
    await cache_service.set("test_key", "test_value", ttl=60)
    value = await cache_service.get("test_key")
    print(f"✓ CacheService: {value}")
    
    # Test MetricsService
    metrics_service = MetricsService()
    await metrics_service.track_query_processing(
        query_id="test_query",
        query_type="basic",
        processing_time=1.5,
        cache_hit=False
    )
    summary = metrics_service.get_metrics_summary()
    print(f"✓ MetricsService: {summary.get('total_queries', 0)} queries tracked")
    
    return True


async def test_agent_factory():
    """Test agent factory."""
    print("Testing agent factory...")
    
    from backend.services.agents.agent_factory import AgentFactory
    from backend.models.domain.agent import AgentType
    
    factory = AgentFactory()
    
    # Test agent creation
    agent = await factory.create_agent(AgentType.RETRIEVAL)
    print(f"✓ Agent created: {agent.id} ({agent.agent_type.value})")
    
    # Test supported types
    supported_types = factory.get_supported_agent_types()
    print(f"✓ Supported agent types: {len(supported_types)}")
    
    return True


async def main():
    """Run all tests."""
    print("🧪 Testing Clean Architecture Structure")
    print("=" * 50)
    
    try:
        await test_domain_models()
        await test_request_models()
        await test_core_services()
        await test_agent_factory()
        
        print("\n✅ All tests passed! Clean architecture structure is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 