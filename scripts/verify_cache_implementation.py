#!/usr/bin/env python3
"""
Simple Cache Implementation Verification

This script verifies that the core caching functionality is working correctly
without requiring heavy dependencies.
"""

import asyncio
import time
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_basic_cache_functionality():
    """Test basic cache functionality."""
    print("🧪 Testing Basic Cache Functionality")
    print("-" * 50)
    
    try:
        # Test imports
        from shared.core.cache.cache_config import CacheLevel, get_cache_config
        from shared.core.cache.cache_manager import UnifiedCacheManager
        print("✅ Cache imports successful")
        
        # Test configuration
        config = get_cache_config()
        print(f"✅ Cache configuration loaded: backend={config.backend.value}")
        
        # Test cache manager
        manager = UnifiedCacheManager.get_instance(CacheLevel.QUERY_RESULTS)
        print("✅ Cache manager created")
        
        # Test basic operations
        test_key = "test_verification_key"
        test_value = {"message": "Cache verification test", "timestamp": time.time()}
        
        # Test set
        success = await manager.set(test_key, test_value)
        print(f"✅ Cache set operation: {success}")
        
        # Test get
        retrieved = await manager.get(test_key)
        cache_hit = retrieved is not None and retrieved == test_value
        print(f"✅ Cache get operation: {cache_hit}")
        
        # Test delete
        deleted = await manager.delete(test_key)
        print(f"✅ Cache delete operation: {deleted}")
        
        # Test miss after delete
        missing = await manager.get(test_key)
        cache_miss = missing is None
        print(f"✅ Cache miss after delete: {cache_miss}")
        
        # Test statistics
        stats = manager.get_stats()
        print(f"✅ Cache statistics available: {isinstance(stats, dict)}")
        
        return success and cache_hit and deleted and cache_miss
        
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False

async def test_performance_improvement():
    """Test that caching provides performance improvements."""
    print("\n🚀 Testing Performance Improvement")
    print("-" * 50)
    
    try:
        from shared.core.cache.cache_manager import UnifiedCacheManager
        from shared.core.cache.cache_config import CacheLevel
        
        manager = UnifiedCacheManager.get_instance(CacheLevel.QUERY_RESULTS)
        
        # Simulate expensive operation
        async def expensive_operation(key):
            # Simulate database/API delay
            await asyncio.sleep(0.1)  # 100ms delay
            return {"result": f"Expensive result for {key}", "computed_at": time.time()}
        
        test_key = "performance_test_key"
        
        # First call - cache miss (expensive)
        start_time = time.time()
        
        # Check cache first
        cached_result = await manager.get(test_key)
        if cached_result is None:
            # Cache miss - do expensive operation
            result = await expensive_operation(test_key)
            await manager.set(test_key, result)
        else:
            result = cached_result
        
        first_call_time = (time.time() - start_time) * 1000
        
        # Second call - cache hit (fast)
        start_time = time.time()
        
        cached_result = await manager.get(test_key)
        if cached_result is None:
            result = await expensive_operation(test_key)
            await manager.set(test_key, result)
        else:
            result = cached_result
        
        second_call_time = (time.time() - start_time) * 1000
        
        # Calculate improvement
        improvement = first_call_time / second_call_time if second_call_time > 0 else float('inf')
        
        print(f"First call (cache miss): {first_call_time:.1f}ms")
        print(f"Second call (cache hit): {second_call_time:.1f}ms")
        print(f"Performance improvement: {improvement:.1f}x faster")
        
        return improvement > 5  # Should be at least 5x faster
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

async def test_ttl_expiration():
    """Test TTL-based cache expiration."""
    print("\n⏰ Testing TTL Expiration")
    print("-" * 50)
    
    try:
        from shared.core.cache.cache_manager import UnifiedCacheManager
        from shared.core.cache.cache_config import CacheLevel
        
        manager = UnifiedCacheManager.get_instance(CacheLevel.QUERY_RESULTS)
        
        # Set value with short TTL
        test_key = "ttl_test_key"
        test_value = {"message": "This will expire soon"}
        
        success = await manager.set(test_key, test_value, ttl_seconds=1)  # 1 second TTL
        print(f"✅ Set value with 1s TTL: {success}")
        
        # Immediately retrieve (should hit)
        immediate_result = await manager.get(test_key)
        immediate_hit = immediate_result is not None
        print(f"✅ Immediate retrieval: {immediate_hit}")
        
        # Wait for expiration
        print("⏳ Waiting 2 seconds for expiration...")
        await asyncio.sleep(2)
        
        # Try to retrieve after expiration (should miss)
        expired_result = await manager.get(test_key)
        expired_miss = expired_result is None
        print(f"✅ Expired retrieval (should be None): {expired_miss}")
        
        return success and immediate_hit and expired_miss
        
    except Exception as e:
        print(f"❌ TTL test failed: {e}")
        return False

async def test_cache_levels():
    """Test different cache levels."""
    print("\n📊 Testing Multiple Cache Levels")
    print("-" * 50)
    
    try:
        from shared.core.cache.cache_manager import UnifiedCacheManager
        from shared.core.cache.cache_config import CacheLevel
        
        levels_to_test = [
            CacheLevel.QUERY_RESULTS,
            CacheLevel.EMBEDDINGS,
            CacheLevel.LLM_RESPONSES
        ]
        
        working_levels = 0
        
        for level in levels_to_test:
            try:
                manager = UnifiedCacheManager.get_instance(level)
                test_key = f"level_test_{level.value}"
                test_value = {"level": level.value, "data": "test"}
                
                # Test basic operations
                set_success = await manager.set(test_key, test_value)
                get_result = await manager.get(test_key)
                delete_success = await manager.delete(test_key)
                
                level_working = set_success and get_result is not None and delete_success
                
                if level_working:
                    working_levels += 1
                    print(f"✅ {level.value}: Working")
                else:
                    print(f"❌ {level.value}: Not working")
                    
            except Exception as e:
                print(f"❌ {level.value}: Error - {e}")
        
        print(f"\n📊 Cache levels working: {working_levels}/{len(levels_to_test)}")
        return working_levels == len(levels_to_test)
        
    except Exception as e:
        print(f"❌ Cache levels test failed: {e}")
        return False

async def main():
    """Run cache verification tests."""
    print("🎯 Cache Implementation Verification")
    print("🔧 Testing Core Caching Functionality")
    print("=" * 70)
    
    tests = [
        ("Basic Functionality", test_basic_cache_functionality),
        ("Performance Improvement", test_performance_improvement),
        ("TTL Expiration", test_ttl_expiration),
        ("Multiple Cache Levels", test_cache_levels)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 CACHE VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All cache verification tests passed!")
        print("\n✅ Cache Implementation Verified:")
        print("   - Basic cache operations working correctly")
        print("   - Performance improvements demonstrated")
        print("   - TTL expiration functioning properly")
        print("   - Multiple cache levels operational")
        
        print("\n🚀 Cache system is ready for production use!")
        print("📋 Benefits:")
        print("   - Faster response times for repeated queries")
        print("   - Reduced API calls to expensive services")
        print("   - Configurable behavior via environment variables")
        print("   - Thread-safe operations with memory management")
        
        return 0
    else:
        print("\n⚠️ Some cache verification tests failed.")
        print("🔧 Please check the errors above and ensure:")
        print("   - Required dependencies are installed")
        print("   - Cache configuration is properly set")
        print("   - No conflicting cache instances")
        
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)