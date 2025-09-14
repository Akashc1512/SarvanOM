"""
Service-Specific Load Tests

This module contains specialized load tests for different types of services
in the SarvanOM platform, including API endpoints, data processing, and
real-time operations.
"""

import asyncio
import json
from .load_test_framework import LoadTestFramework, LoadTestConfig
import logging

logger = logging.getLogger(__name__)

class ServiceSpecificLoadTests:
    """Specialized load tests for different service types"""
    
    def __init__(self):
        self.framework = LoadTestFramework()
    
    async def test_health_endpoints(self):
        """Test health endpoints under load"""
        logger.info("Testing health endpoints...")
        
        health_endpoints = [
            LoadTestConfig(
                service_url="http://localhost:8000",
                endpoint="/health",
                concurrent_users=100,
                duration_seconds=60,
                ramp_up_seconds=10
            ),
            LoadTestConfig(
                service_url="http://localhost:8004",
                endpoint="/health", 
                concurrent_users=100,
                duration_seconds=60,
                ramp_up_seconds=10
            ),
            LoadTestConfig(
                service_url="http://localhost:8005",
                endpoint="/health",
                concurrent_users=100,
                duration_seconds=60,
                ramp_up_seconds=10
            ),
            LoadTestConfig(
                service_url="http://localhost:8012",
                endpoint="/auth/health",
                concurrent_users=100,
                duration_seconds=60,
                ramp_up_seconds=10
            )
        ]
        
        async with self.framework:
            for config in health_endpoints:
                await self.framework.run_load_test(config)
                await asyncio.sleep(1)
    
    async def test_feeds_service_processing(self):
        """Test feeds service with real data processing"""
        logger.info("Testing feeds service data processing...")
        
        # Test with different query types
        test_queries = [
            {
                "query": "latest AI news",
                "feed_type": "news",
                "user_id": "load_test_user",
                "session_id": "load_test_session",
                "trace_id": "load_test_trace",
                "constraints": {"limit": 5}
            },
            {
                "query": "stock market analysis",
                "feed_type": "markets", 
                "user_id": "load_test_user",
                "session_id": "load_test_session",
                "trace_id": "load_test_trace",
                "constraints": {"limit": 10}
            },
            {
                "query": "technology trends",
                "feed_type": "news",
                "user_id": "load_test_user", 
                "session_id": "load_test_session",
                "trace_id": "load_test_trace",
                "constraints": {"limit": 8}
            }
        ]
        
        async with self.framework:
            for i, query in enumerate(test_queries):
                config = LoadTestConfig(
                    service_url="http://localhost:8005",
                    endpoint="/fetch",
                    method="POST",
                    payload=query,
                    headers={"Content-Type": "application/json"},
                    concurrent_users=20,
                    duration_seconds=90,
                    ramp_up_seconds=15
                )
                
                await self.framework.run_load_test(config)
                await asyncio.sleep(2)
    
    async def test_model_registry_operations(self):
        """Test model registry with concurrent model/provider requests"""
        logger.info("Testing model registry operations...")
        
        registry_tests = [
            LoadTestConfig(
                service_url="http://localhost:8000",
                endpoint="/models",
                concurrent_users=50,
                duration_seconds=60,
                ramp_up_seconds=10
            ),
            LoadTestConfig(
                service_url="http://localhost:8000",
                endpoint="/providers",
                concurrent_users=50,
                duration_seconds=60,
                ramp_up_seconds=10
            )
        ]
        
        async with self.framework:
            for config in registry_tests:
                await self.framework.run_load_test(config)
                await asyncio.sleep(1)
    
    async def test_auth_service_operations(self):
        """Test authentication service with various operations"""
        logger.info("Testing auth service operations...")
        
        auth_tests = [
            LoadTestConfig(
                service_url="http://localhost:8012",
                endpoint="/auth/",
                concurrent_users=30,
                duration_seconds=60,
                ramp_up_seconds=10
            )
        ]
        
        async with self.framework:
            for config in auth_tests:
                await self.framework.run_load_test(config)
                await asyncio.sleep(1)
    
    async def test_config_endpoints(self):
        """Test configuration endpoints under load"""
        logger.info("Testing config endpoints...")
        
        config_endpoints = [
            LoadTestConfig(
                service_url="http://localhost:8004",
                endpoint="/config",
                concurrent_users=40,
                duration_seconds=60,
                ramp_up_seconds=10
            ),
            LoadTestConfig(
                service_url="http://localhost:8005",
                endpoint="/config",
                concurrent_users=40,
                duration_seconds=60,
                ramp_up_seconds=10
            )
        ]
        
        async with self.framework:
            for config in config_endpoints:
                await self.framework.run_load_test(config)
                await asyncio.sleep(1)
    
    async def test_stress_scenarios(self):
        """Test system under extreme stress conditions"""
        logger.info("Running stress tests...")
        
        stress_tests = [
            # Extreme concurrent users on health endpoints
            LoadTestConfig(
                service_url="http://localhost:8000",
                endpoint="/health",
                concurrent_users=200,
                duration_seconds=120,
                ramp_up_seconds=30
            ),
            LoadTestConfig(
                service_url="http://localhost:8005",
                endpoint="/health",
                concurrent_users=200,
                duration_seconds=120,
                ramp_up_seconds=30
            )
        ]
        
        async with self.framework:
            for config in stress_tests:
                await self.framework.run_load_test(config)
                await asyncio.sleep(5)  # Longer delay between stress tests
    
    async def test_mixed_workload(self):
        """Test mixed workload across multiple services simultaneously"""
        logger.info("Testing mixed workload...")
        
        # Create multiple concurrent test scenarios
        tasks = []
        
        # Health checks
        health_task = asyncio.create_task(self._run_health_checks())
        tasks.append(health_task)
        
        # Feeds processing
        feeds_task = asyncio.create_task(self._run_feeds_processing())
        tasks.append(feeds_task)
        
        # Config requests
        config_task = asyncio.create_task(self._run_config_requests())
        tasks.append(config_task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
    
    async def _run_health_checks(self):
        """Run health check load test"""
        async with self.framework:
            config = LoadTestConfig(
                service_url="http://localhost:8000",
                endpoint="/health",
                concurrent_users=30,
                duration_seconds=60,
                ramp_up_seconds=10
            )
            await self.framework.run_load_test(config)
    
    async def _run_feeds_processing(self):
        """Run feeds processing load test"""
        async with self.framework:
            query = {
                "query": "mixed workload test",
                "feed_type": "news",
                "user_id": "mixed_test_user",
                "session_id": "mixed_test_session", 
                "trace_id": "mixed_test_trace",
                "constraints": {"limit": 5}
            }
            config = LoadTestConfig(
                service_url="http://localhost:8005",
                endpoint="/fetch",
                method="POST",
                payload=query,
                headers={"Content-Type": "application/json"},
                concurrent_users=15,
                duration_seconds=60,
                ramp_up_seconds=10
            )
            await self.framework.run_load_test(config)
    
    async def _run_config_requests(self):
        """Run config request load test"""
        async with self.framework:
            config = LoadTestConfig(
                service_url="http://localhost:8004",
                endpoint="/config",
                concurrent_users=20,
                duration_seconds=60,
                ramp_up_seconds=10
            )
            await self.framework.run_load_test(config)

async def run_service_specific_tests():
    """Run all service-specific load tests"""
    tester = ServiceSpecificLoadTests()
    
    logger.info("Starting service-specific load tests...")
    
    # Run tests in sequence
    await tester.test_health_endpoints()
    await asyncio.sleep(5)
    
    await tester.test_model_registry_operations()
    await asyncio.sleep(5)
    
    await tester.test_feeds_service_processing()
    await asyncio.sleep(5)
    
    await tester.test_auth_service_operations()
    await asyncio.sleep(5)
    
    await tester.test_config_endpoints()
    await asyncio.sleep(5)
    
    await tester.test_mixed_workload()
    await asyncio.sleep(5)
    
    # Run stress tests last
    await tester.test_stress_scenarios()
    
    logger.info("Service-specific load tests completed!")

if __name__ == "__main__":
    asyncio.run(run_service_specific_tests())
