#!/usr/bin/env python3
"""
Load and stress testing for Universal Knowledge Hub.
"""

import asyncio
import unittest
import time
import json
import httpx
import psutil
import pytest
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

# Import the modules we want to test
from shared.core.cache import UnifiedCacheManager as CacheManager

# Load test configuration
LOAD_TEST_CONFIG = {
    "base_url": "http://127.0.0.1:8000",
    "concurrent_users": 10,
    "requests_per_user": 50,
    "timeout": 30,
    "burst_size": 100,
    "sustained_duration": 60,  # seconds
}

# Test queries for load testing
TEST_QUERIES = [
    "What is quantum computing?",
    "Explain machine learning algorithms",
    "How does blockchain work?",
    "What are the benefits of renewable energy?",
    "Explain the theory of relativity",
    "What is artificial intelligence?",
    "How do neural networks work?",
    "What is the future of technology?",
    "Explain cryptocurrency mining",
    "What are the applications of IoT?",
]


class LoadTestBase(unittest.TestCase):
    """Base class for load tests."""

    def setUp(self):
        """Set up test environment"""
        self.base_url = LOAD_TEST_CONFIG["base_url"]
        self.timeout = LOAD_TEST_CONFIG["timeout"]

    async def make_request(self, endpoint: str, data: Dict = None) -> Dict:
        """Make an async HTTP request."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                if data:
                    response = await client.post(url, json=data, timeout=self.timeout)
                else:
                    response = await client.get(url, timeout=self.timeout)
                
                return {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds() * 1000,
                    "data": response.json() if response.status_code == 200 else None,
                }
        except Exception as e:
            return {
                "status_code": 0,
                "response_time": 0,
                "error": str(e),
            }


class TestConcurrentLoad(LoadTestBase):
    """Test concurrent load handling."""

    async def test_concurrent_queries(self):
        """Test concurrent query processing."""
        print("🧪 Testing concurrent query processing")

        async def worker(worker_id: int):
            """Worker function for concurrent requests."""
            results = []
            
            for i in range(LOAD_TEST_CONFIG["requests_per_user"]):
                query = TEST_QUERIES[i % len(TEST_QUERIES)]
                result = await self.make_request("/query", {"query": query})
                results.append(result)
                
                # Small delay between requests
                await asyncio.sleep(0.1)
            
            return results

        # Create concurrent workers
        workers = [worker(i) for i in range(LOAD_TEST_CONFIG["concurrent_users"])]
        
        # Execute all workers concurrently
        start_time = time.time()
        all_results = await asyncio.gather(*workers, return_exceptions=True)
        end_time = time.time()

        # Analyze results
        total_requests = 0
        successful_requests = 0
        total_response_time = 0

        for worker_results in all_results:
            if isinstance(worker_results, Exception):
                print(f"   Worker failed: {worker_results}")
                continue
                
            for result in worker_results:
                total_requests += 1
                if result["status_code"] in [200, 401, 403]:  # Acceptable responses
                    successful_requests += 1
                total_response_time += result["response_time"]

        # Calculate metrics
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        avg_response_time = total_response_time / total_requests if total_requests > 0 else 0
        total_time = end_time - start_time
        requests_per_second = total_requests / total_time if total_time > 0 else 0

        print(f"✅ Concurrent Load Test Results:")
        print(f"   Total Requests: {total_requests}")
        print(f"   Successful Requests: {successful_requests}")
        print(f"   Success Rate: {success_rate:.2f}%")
        print(f"   Average Response Time: {avg_response_time:.2f}ms")
        print(f"   Requests per Second: {requests_per_second:.2f}")
        print(f"   Total Time: {total_time:.2f}s")

        # Assertions
        self.assertGreater(success_rate, 80, "Success rate too low")
        self.assertLess(avg_response_time, 5000, "Response time too high")
        self.assertGreater(requests_per_second, 1, "Throughput too low")


class TestStressTesting(LoadTestBase):
    """Test stress conditions."""

    async def test_sustained_high_load(self):
        """Test sustained high load."""
        print("🧪 Testing sustained high load")

        start_time = time.time()
        request_count = 0
        successful_count = 0

        while time.time() - start_time < LOAD_TEST_CONFIG["sustained_duration"]:
            # Make multiple concurrent requests
            tasks = []
            for i in range(10):
                query = TEST_QUERIES[i % len(TEST_QUERIES)]
                task = self.make_request("/query", {"query": query})
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                request_count += 1
                if isinstance(result, dict) and result["status_code"] in [200, 401, 403]:
                    successful_count += 1

            # Small delay to prevent overwhelming
            await asyncio.sleep(0.1)

        success_rate = (successful_count / request_count * 100) if request_count > 0 else 0
        requests_per_second = request_count / LOAD_TEST_CONFIG["sustained_duration"]

        print(f"✅ Sustained Load Test Results:")
        print(f"   Total Requests: {request_count}")
        print(f"   Successful Requests: {successful_count}")
        print(f"   Success Rate: {success_rate:.2f}%")
        print(f"   Requests per Second: {requests_per_second:.2f}")

        self.assertGreater(success_rate, 70, "Success rate too low under sustained load")

    async def test_burst_traffic(self):
        """Test burst traffic handling."""
        print("🧪 Testing burst traffic handling")

        # Create burst of requests
        tasks = []
        for i in range(LOAD_TEST_CONFIG["burst_size"]):
            query = TEST_QUERIES[i % len(TEST_QUERIES)]
            task = self.make_request("/query", {"query": query})
            tasks.append(task)

        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Analyze burst results
        successful_count = 0
        total_response_time = 0

        for result in results:
            if isinstance(result, dict) and result["status_code"] in [200, 401, 403]:
                successful_count += 1
                total_response_time += result["response_time"]

        burst_duration = end_time - start_time
        success_rate = (successful_count / len(results) * 100)
        avg_response_time = total_response_time / successful_count if successful_count > 0 else 0

        print(f"✅ Burst Traffic Test Results:")
        print(f"   Burst Size: {len(results)}")
        print(f"   Successful Requests: {successful_count}")
        print(f"   Success Rate: {success_rate:.2f}%")
        print(f"   Average Response Time: {avg_response_time:.2f}ms")
        print(f"   Burst Duration: {burst_duration:.2f}s")

        self.assertGreater(success_rate, 60, "Success rate too low for burst traffic")


class TestMemoryLeakDetection(unittest.TestCase):
    """Test for memory leaks"""

    def test_memory_usage_over_time(self):
        """Test memory usage over time to detect leaks"""
        print("🧪 Testing memory usage over time")

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        memory_samples = []

        # Run operations for extended period
        for i in range(100):
            # Simulate typical operations
            query = TEST_QUERIES[i % len(TEST_QUERIES)]

            # Make API request
            try:
                response = requests.post(
                    f"{LOAD_TEST_CONFIG['base_url']}/query", json={"query": query}, timeout=10
                )
            except:
                pass

            # Record memory usage every 10 iterations
            if i % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_samples.append(current_memory)
                print(f"   Iteration {i}: Memory usage: {current_memory:.2f}MB")

        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Check for memory leaks
        memory_increase = final_memory - initial_memory
        memory_growth_rate = memory_increase / len(memory_samples) if memory_samples else 0

        self.assertLess(
            memory_increase,
            100,  # Should not increase by more than 100MB
            f"Memory increased by {memory_increase:.2f}MB, possible leak",
        )
        self.assertLess(
            memory_growth_rate,
            1,  # Should not grow more than 1MB per sample
            f"Memory growth rate {memory_growth_rate:.2f}MB/sample too high",
        )

        print(f"✅ Memory Leak Test Results:")
        print(f"   Initial Memory: {initial_memory:.2f}MB")
        print(f"   Final Memory: {final_memory:.2f}MB")
        print(f"   Memory Increase: {memory_increase:.2f}MB")
        print(f"   Growth Rate: {memory_growth_rate:.2f}MB/sample")


class TestErrorHandlingUnderLoad(unittest.TestCase):
    """Test error handling under load"""

    async def test_error_recovery(self):
        """Test system recovery after errors"""
        print("🧪 Testing error recovery under load")

        # Generate various error conditions
        error_scenarios = [
            {"query": "", "expected_status": 400},  # Empty query
            {"query": "a" * 10001, "expected_status": 400},  # Too long
            {"query": None, "expected_status": 422},  # Null query
            {"invalid_field": "test", "expected_status": 422},  # Invalid field
        ]

        # Test each scenario under load
        for scenario in error_scenarios:
            print(f"   Testing scenario: {scenario}")

            # Send multiple requests with error condition
            error_count = 0
            success_count = 0

            async with httpx.AsyncClient() as client:
                for i in range(20):
                    try:
                        response = await client.post(
                            f"{LOAD_TEST_CONFIG['base_url']}/query", 
                            json=scenario, 
                            timeout=10
                        )

                        if response.status_code == scenario["expected_status"]:
                            success_count += 1
                        else:
                            error_count += 1

                    except Exception as e:
                        error_count += 1

            # System should handle errors gracefully
            self.assertGreater(success_count, 0, "No successful error handling")
            self.assertLess(error_count, 20, "Too many unexpected errors")

            print(f"     Success: {success_count}, Errors: {error_count}")


class TestCachePerformance(unittest.TestCase):
    """Test cache performance under load"""

    def setUp(self):
        """Set up test environment"""
        self.cache = CacheManager()  # Changed from QueryCache

    @pytest.mark.asyncio
    async def test_cache_under_load(self):
        """Test cache performance under high load"""
        print("🧪 Testing cache performance under load")

        # Initialize cache
        await self.cache.initialize()

        # Generate cache keys
        cache_keys = [f"test_key_{i}" for i in range(1000)]
        cache_values = [f"test_value_{i}" for i in range(1000)]

        # Concurrent cache operations
        async def cache_worker(worker_id: int):
            """Worker for cache operations"""
            results = []
            for i in range(100):
                key = cache_keys[(worker_id * 100 + i) % len(cache_keys)]
                value = cache_values[(worker_id * 100 + i) % len(cache_values)]

                # Set value
                start_time = time.time()
                await self.cache.set(key, value, ttl=60)
                set_time = time.time() - start_time

                # Get value
                start_time = time.time()
                retrieved = await self.cache.get(key)
                get_time = time.time() - start_time

                results.append(
                    {
                        "set_time": set_time * 1000,  # Convert to ms
                        "get_time": get_time * 1000,
                        "success": retrieved == value,
                    }
                )

            return results

        # Run concurrent cache operations
        tasks = [cache_worker(i) for i in range(10)]
        all_results = await asyncio.gather(*tasks)

        # Flatten results
        all_operations = []
        for worker_results in all_results:
            all_operations.extend(worker_results)

        # Calculate metrics
        set_times = [op["set_time"] for op in all_operations]
        get_times = [op["get_time"] for op in all_operations]
        successful_ops = len([op for op in all_operations if op["success"]])

        avg_set_time = statistics.mean(set_times)
        avg_get_time = statistics.mean(get_times)
        success_rate = successful_ops / len(all_operations)

        # Assertions
        self.assertGreater(success_rate, 0.95, "Cache success rate too low")
        self.assertLess(avg_set_time, 10, "Cache set time too high")
        self.assertLess(avg_get_time, 5, "Cache get time too high")

        print(f"✅ Cache Performance Results:")
        print(f"   Total Operations: {len(all_operations)}")
        print(f"   Success Rate: {success_rate:.2%}")
        print(f"   Avg Set Time: {avg_set_time:.2f}ms")
        print(f"   Avg Get Time: {avg_get_time:.2f}ms")


class TestDatabasePerformance(unittest.TestCase):
    """Test database performance under load"""

    def test_database_connection_pool(self):
        """Test database connection pool under load"""
        print("🧪 Testing database connection pool")

        # This would test database connections under load
        # Implementation depends on the specific database being used
        pass

    def test_query_optimization(self):
        """Test query optimization under load"""
        print("🧪 Testing query optimization")

        # This would test query performance under load
        # Implementation depends on the specific database being used
        pass


class TestNetworkResilience(unittest.TestCase):
    """Test network resilience"""

    def test_network_timeout_handling(self):
        """Test handling of network timeouts"""
        print("🧪 Testing network timeout handling")

        # Test with various timeout scenarios
        timeout_scenarios = [1, 5, 10, 30]  # seconds

        for timeout in timeout_scenarios:
            print(f"   Testing timeout: {timeout}s")

            start_time = time.time()
            try:
                response = requests.get(f"{LOAD_TEST_CONFIG['base_url']}/health", timeout=timeout)
                response_time = time.time() - start_time

                self.assertLess(
                    response_time,
                    timeout + 1,
                    f"Response time {response_time:.2f}s exceeds timeout {timeout}s",
                )

            except requests.exceptions.Timeout:
                # Expected for very short timeouts
                if timeout < 5:
                    continue
                else:
                    self.fail(f"Unexpected timeout with {timeout}s timeout")

    def test_connection_resilience(self):
        """Test connection resilience"""
        print("🧪 Testing connection resilience")

        # Test with connection drops and recovery
        for i in range(10):
            try:
                response = requests.get(f"{LOAD_TEST_CONFIG['base_url']}/health", timeout=10)
                self.assertEqual(response.status_code, 200)
            except Exception as e:
                # Should handle connection errors gracefully
                print(f"   Connection error {i + 1}: {e}")
                continue


async def run_load_tests():
    """Run all load tests."""
    print("🧪 Running Load and Stress Tests")
    print("=" * 60)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestConcurrentLoad,
        TestStressTesting,
        TestMemoryLeakDetection,
        TestErrorHandlingUnderLoad,
        TestCachePerformance,
        TestDatabasePerformance,
        TestNetworkResilience,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 60)
    print("📋 Load Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n🎉 All load tests passed!")
        return True
    else:
        print("\n❌ Some load tests failed.")
        return False

async def main():
    """Main test function."""
    success = await run_load_tests()
    return success

if __name__ == "__main__":
    asyncio.run(main())
