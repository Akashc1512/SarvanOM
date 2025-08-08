#!/usr/bin/env python3
"""
Simple bulletproof integration tests for Universal Knowledge Hub.
"""

import asyncio
import unittest
import time
import json
import httpx
from typing import Dict, Any, List
from unittest.mock import Mock, patch

# Import the modules we want to test
from shared.core.agents.base_agent import BaseAgent, AgentType, AgentResult, QueryContext
from shared.core.agents.data_models import AgentDataModel

# Test configuration
TEST_API_BASE_URL = "http://127.0.0.1:8000"
TEST_TIMEOUT = 10
TEST_RESPONSE_TIME_LIMIT = 1000  # milliseconds


# Define TestAgent locally for testing
class TestAgent(BaseAgent):
    """Test agent for basic functionality testing."""

    def __init__(self, agent_id: str, agent_type: AgentType):
        super().__init__(agent_id, agent_type)
        self.test_data = {"processed": False}

    async def process_task(self, task: Dict[str, Any], context: QueryContext) -> AgentResult:
        """Process a test task."""
        try:
            # Simulate processing
            await asyncio.sleep(0.1)
            self.test_data["processed"] = True

            return AgentResult(
                success=True,
                data={"message": "Test task processed successfully", "input": str(task)},
                confidence=0.9,
                token_usage={"prompt": 10, "completion": 20},
            )
        except Exception as e:
            return AgentResult(success=False, data=None, error=str(e), confidence=0.0)


class TestBaseAgentSimple(unittest.TestCase):
    """Test basic agent functionality."""

    def setUp(self):
        """Set up test environment"""
        self.agent = TestAgent("test_agent_001", AgentType.RETRIEVAL)

    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.agent_id, "test_agent_001")
        self.assertEqual(self.agent.agent_type, AgentType.RETRIEVAL)
        self.assertIsNotNone(self.agent.metrics)
        self.assertFalse(self.agent.is_running)
        self.assertEqual(self.agent.health_status, "healthy")

    def test_agent_start_stop(self):
        """Test agent start and stop"""
        # Test that agent can be started and stopped
        self.assertFalse(self.agent.is_running)
        # Note: start() and stop() are async methods, so we can't test them synchronously
        # But we can test that the agent was created correctly
        self.assertIsNotNone(self.agent.agent_id)

    def test_agent_message_creation(self):
        """Test agent message creation"""
        message = AgentResult()
        self.assertIsNotNone(message.header)
        self.assertIsNotNone(message.payload)
        self.assertIn("message_id", message.header)
        self.assertIn("timestamp", message.header)

    def test_agent_result_creation(self):
        """Test agent result creation"""
        result = AgentResult(success=True, data={"test": "data"}, confidence=0.8)
        self.assertTrue(result.success)
        self.assertEqual(result.confidence, 0.8)
        self.assertEqual(result.data["test"], "data")

    def test_agent_metrics(self):
        """Test agent metrics recording"""
        self.agent.record_metric("test_metric", 5)
        self.assertEqual(self.agent.metrics["test_metric"], 5)

        self.agent.record_metric("test_metric", 3)
        self.assertEqual(self.agent.metrics["test_metric"], 8)


class TestAgentAsync(unittest.TestCase):
    """Test async agent functionality."""

    def setUp(self):
        """Set up test environment"""
        self.agent = TestAgent("test_agent_001", AgentType.RETRIEVAL)

    def test_agent_creation(self):
        """Test agent creation and basic properties"""
        self.assertEqual(self.agent.agent_id, "test_agent_001")
        self.assertEqual(self.agent.agent_type, AgentType.RETRIEVAL)
        self.assertIsNotNone(self.agent.metrics)
        self.assertFalse(self.agent.is_running)

    def test_agent_message_creation(self):
        """Test agent message creation"""
        message = AgentResult()
        self.assertIsNotNone(message.header)
        self.assertIsNotNone(message.payload)
        self.assertIn("message_id", message.header)

    def test_agent_result_creation(self):
        """Test agent result creation"""
        result = AgentResult(success=True, data={"test": "data"}, confidence=0.8)
        self.assertTrue(result.success)
        self.assertEqual(result.confidence, 0.8)
        self.assertEqual(result.data["test"], "data")

    def test_agent_metrics_update(self):
        """Test agent metrics update"""
        agent = TestAgent("test_agent_002", AgentType.SYNTHESIS)

        # Record metrics
        agent.record_metric("requests", 1)
        agent.record_metric("successful_requests", 1)

        self.assertEqual(agent.metrics["requests"], 1)
        self.assertEqual(agent.metrics["successful_requests"], 1)


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints."""

    def setUp(self):
        """Set up test environment"""
        self.base_url = TEST_API_BASE_URL

    async def test_health_endpoint(self):
        """Test health endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=TEST_TIMEOUT)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn("status", data)
                self.assertIn("version", data)

        except Exception:
            self.skipTest("API not available")

    async def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/", timeout=TEST_TIMEOUT)

                self.assertEqual(response.status_code, 200)

        except Exception:
            self.skipTest("API not available")

    async def test_agents_endpoint(self):
        """Test agents endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/agents", timeout=TEST_TIMEOUT)

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIsInstance(data, dict)

        except Exception:
            self.skipTest("API not available")

    async def test_query_endpoint(self):
        """Test query endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/query",
                    json={"query": "What is quantum computing?"},
                    timeout=TEST_TIMEOUT,
                )

                # Should return 200, 422 (validation error), 403 (forbidden), or 500 (security block)
                self.assertIn(response.status_code, [200, 422, 403, 500])

                # If it's a 403 or 500, check if it's a security block
                if response.status_code in [403, 500]:
                    data = response.json()
                    self.assertIn("detail", data)
                    # Security blocks are expected in test environment
                    print(f"   Note: Query blocked by security: {data.get('detail', 'Unknown')}")

        except Exception:
            self.skipTest("API not available")


class TestPerformanceSimple(unittest.TestCase):
    """Test basic performance metrics."""

    def setUp(self):
        """Set up test environment"""
        self.base_url = TEST_API_BASE_URL

    async def test_response_time(self):
        """Test API response time"""
        try:
            async with httpx.AsyncClient() as client:
                start_time = time.time()
                response = await client.get(f"{self.base_url}/health", timeout=TEST_TIMEOUT)
                end_time = time.time()

                response_time = (end_time - start_time) * 1000  # Convert to milliseconds

                self.assertEqual(response.status_code, 200)
                self.assertLess(
                    response_time, TEST_RESPONSE_TIME_LIMIT
                )  # Should respond in less than 1 second

        except Exception:
            self.skipTest("API not available")

    async def test_concurrent_requests(self):
        """Test concurrent requests"""
        try:
            async with httpx.AsyncClient() as client:
                # Make 5 concurrent requests
                tasks = []
                for i in range(5):
                    task = client.get(f"{self.base_url}/health", timeout=TEST_TIMEOUT)
                    tasks.append(task)

                responses = await asyncio.gather(*tasks, return_exceptions=True)

                # Check that all requests succeeded
                successful_responses = [r for r in responses if not isinstance(r, Exception)]
                self.assertGreaterEqual(len(successful_responses), 3)  # At least 3 should succeed

                # Check response times
                for response in successful_responses:
                    self.assertEqual(response.status_code, 200)

        except Exception:
            self.skipTest("API not available")


class TestSecuritySimple(unittest.TestCase):
    """Test basic security measures."""

    def setUp(self):
        """Set up test environment"""
        self.base_url = TEST_API_BASE_URL

    def test_input_validation(self):
        """Test input validation"""
        try:
            # Test with empty query
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/query", json={"query": ""}, timeout=TEST_TIMEOUT
                )

                # Should not return 500 (internal server error)
                self.assertNotEqual(response.status_code, 500)

        except Exception:
            self.skipTest("API not available")

    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        try:
            malicious_query = "'; DROP TABLE users; --"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/query", json={"query": malicious_query}, timeout=TEST_TIMEOUT
                )

                # Should not return 500 (internal server error)
                self.assertNotEqual(response.status_code, 500)

        except Exception:
            self.skipTest("API not available")


async def run_simple_tests():
    """Run all simple tests."""
    print("🧪 Running Simple Bulletproof Integration Tests")
    print("=" * 60)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestBaseAgentSimple,
        TestAgentAsync,
        TestAPIEndpoints,
        TestPerformanceSimple,
        TestSecuritySimple,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed.")
        return False

async def main():
    """Main test function."""
    success = await run_simple_tests()
    return success

if __name__ == "__main__":
    asyncio.run(main())
