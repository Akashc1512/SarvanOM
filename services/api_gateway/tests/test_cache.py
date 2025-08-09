import asyncio
import pytest


pytestmark = pytest.mark.asyncio


async def test_cache_hit_and_miss():
    from services.api_gateway.lead_orchestrator import SemanticCacheManager

    cache = SemanticCacheManager(ttl_seconds=60, namespace="test")

    # Miss initially
    assert await cache.get_cached_response("hello world") is None

    # Cache response
    await cache.cache_response("hello world", {"answer": "hi"})

    # Exact hit
    hit = await cache.get_cached_response("hello world")
    assert hit is not None
    assert hit.get("answer") == "hi"


async def test_cache_ttl_expiry():
    from services.api_gateway.lead_orchestrator import SemanticCacheManager

    cache = SemanticCacheManager(ttl_seconds=1, namespace="test")
    await cache.cache_response("expire me", {"answer": "gone"})

    # Immediate hit
    assert await cache.get_cached_response("expire me") is not None

    # Wait to expire
    await asyncio.sleep(1.2)

    # Prune and ensure miss
    pruned = await cache.prune()
    assert pruned >= 1
    assert await cache.get_cached_response("expire me") is None
