"""
Pytest Configuration - SarvanOM v2
Test fixtures and configuration for comprehensive testing.
"""

import pytest
import asyncio
import time
import logging
from typing import Dict, Any, Generator
import aiohttp
import os
import sys

# Add the tests directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_matrix_runner import TestMatrixRunner
from sla_validator import SLAMonitor
from synthetic_prompt_suites import SyntheticPromptSuites
from comprehensive_test_runner import ComprehensiveTestRunner

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API under test"""
    return os.getenv("TEST_BASE_URL", "http://localhost:8004")

@pytest.fixture(scope="session")
async def api_health_check(base_url):
    """Check if the API is healthy before running tests"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    logger.info("API health check passed")
                    return True
                else:
                    logger.warning(f"API health check failed with status {response.status}")
                    return False
    except Exception as e:
        logger.warning(f"API health check failed: {e}")
        return False

@pytest.fixture(scope="session")
def test_matrix_runner(base_url):
    """Test matrix runner fixture"""
    return TestMatrixRunner(base_url)

@pytest.fixture(scope="session")
def sla_monitor(base_url):
    """SLA monitor fixture"""
    monitor = SLAMonitor(base_url)
    yield monitor
    monitor.stop_monitoring()

@pytest.fixture(scope="session")
def prompt_suites(base_url):
    """Synthetic prompt suites fixture"""
    return SyntheticPromptSuites(base_url)

@pytest.fixture(scope="session")
def comprehensive_runner(base_url):
    """Comprehensive test runner fixture"""
    return ComprehensiveTestRunner(base_url)

@pytest.fixture(scope="function")
async def clean_sla_monitor(base_url):
    """Clean SLA monitor for individual tests"""
    monitor = SLAMonitor(base_url)
    yield monitor
    monitor.stop_monitoring()

@pytest.fixture(scope="function")
def mock_test_data():
    """Mock test data for testing"""
    return {
        "simple_queries": [
            "What is the capital of France?",
            "Define machine learning",
            "What is 15% of 200?"
        ],
        "technical_queries": [
            "Write a Python function to sort a list",
            "How does a neural network work?",
            "How do I use the OpenAI API?"
        ],
        "research_queries": [
            "Compare the pros and cons of different AI approaches",
            "What are the latest developments in NLP?",
            "Analyze the impact of AI on healthcare"
        ],
        "guided_prompt_scenarios": {
            "ambiguous": ["Show me apple", "Tell me about python"],
            "pii_heavy": ["My email is john@example.com", "Call me at 555-123-4567"],
            "multilingual": ["¿Cuál es la capital de España?", "東京の人口は何人ですか？"],
            "constraints": ["Show me recent news about AI", "Find academic papers on ML"]
        }
    }

@pytest.fixture(scope="function")
def performance_benchmarks():
    """Performance benchmarks for SLA validation"""
    return {
        "simple_query_sla": 5.0,
        "technical_query_sla": 7.0,
        "research_query_sla": 10.0,
        "guided_prompt_sla": 0.8,
        "gateway_routing_sla": 0.1,
        "retrieval_search_sla": 2.0,
        "synthesis_generation_sla": 5.0,
        "fact_check_validation_sla": 3.0
    }

@pytest.fixture(scope="function")
def quality_thresholds():
    """Quality thresholds for test validation"""
    return {
        "min_success_rate": 0.90,
        "min_sla_compliance": 0.90,
        "min_quality_score": 0.85,
        "min_guided_prompt_trigger_rate": 0.30,
        "max_error_rate": 0.05,
        "min_availability": 0.99
    }

@pytest.fixture(scope="function")
async def test_environment_setup(base_url):
    """Set up test environment"""
    # Check if services are running
    services = [
        "/health",
        "/retrieval/health", 
        "/synthesis/health",
        "/fact-check/health",
        "/guided-prompt/health"
    ]
    
    available_services = []
    async with aiohttp.ClientSession() as session:
        for service in services:
            try:
                async with session.get(f"{base_url}{service}", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        available_services.append(service)
            except Exception:
                pass
    
    logger.info(f"Available services: {available_services}")
    return {
        "base_url": base_url,
        "available_services": available_services,
        "all_services_available": len(available_services) >= 3  # At least 3 services should be available
    }

@pytest.fixture(scope="function")
def test_timeout():
    """Test timeout configuration"""
    return 30  # 30 seconds timeout for individual tests

@pytest.fixture(scope="function")
def retry_config():
    """Retry configuration for flaky tests"""
    return {
        "max_retries": 3,
        "retry_delay": 1.0,  # 1 second delay between retries
        "retry_on_exceptions": (aiohttp.ClientError, asyncio.TimeoutError)
    }

# Pytest markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "sla: marks tests as SLA validation tests")
    config.addinivalue_line("markers", "guided_prompt: marks tests as Guided Prompt tests")
    config.addinivalue_line("markers", "requires_api: marks tests that require API to be running")

# Pytest collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add markers based on test names
        if "test_matrix" in item.name:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)
        elif "sla" in item.name:
            item.add_marker(pytest.mark.sla)
            item.add_marker(pytest.mark.integration)
        elif "guided_prompt" in item.name:
            item.add_marker(pytest.mark.guided_prompt)
            item.add_marker(pytest.mark.integration)
        elif "synthetic" in item.name or "prompt" in item.name:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)
        else:
            item.add_marker(pytest.mark.unit)
        
        # Add requires_api marker for integration tests
        if item.get_closest_marker("integration"):
            item.add_marker(pytest.mark.requires_api)

# Pytest session hooks
def pytest_sessionstart(session):
    """Called after the Session object has been created"""
    logger.info("Starting SarvanOM v2 test session")

def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished"""
    logger.info(f"SarvanOM v2 test session finished with exit status: {exitstatus}")

# Custom pytest fixtures for specific test scenarios
@pytest.fixture
async def guided_prompt_test_scenarios():
    """Specific test scenarios for Guided Prompt validation"""
    return {
        "ambiguous_queries": [
            {
                "prompt": "Show me apple",
                "expected_refinement_type": "disambiguation",
                "expected_acceptance_rate": 0.7
            },
            {
                "prompt": "Tell me about python", 
                "expected_refinement_type": "disambiguation",
                "expected_acceptance_rate": 0.8
            }
        ],
        "pii_queries": [
            {
                "prompt": "My email is john@example.com and I need help",
                "expected_refinement_type": "sanitization",
                "expected_acceptance_rate": 0.9
            },
            {
                "prompt": "Call me at 555-123-4567 about the meeting",
                "expected_refinement_type": "sanitization", 
                "expected_acceptance_rate": 0.9
            }
        ],
        "multilingual_queries": [
            {
                "prompt": "¿Cuál es la capital de España?",
                "expected_refinement_type": "intent_analysis",
                "expected_acceptance_rate": 0.8
            },
            {
                "prompt": "東京の人口は何人ですか？",
                "expected_refinement_type": "intent_analysis",
                "expected_acceptance_rate": 0.8
            }
        ]
    }

@pytest.fixture
def sla_test_scenarios():
    """SLA test scenarios for validation"""
    return {
        "response_time_tests": [
            {
                "service": "gateway",
                "operation": "routing",
                "threshold": 0.1,
                "test_queries": ["health check", "status check"]
            },
            {
                "service": "retrieval", 
                "operation": "search",
                "threshold": 2.0,
                "test_queries": ["search test", "query test"]
            },
            {
                "service": "synthesis",
                "operation": "generation", 
                "threshold": 5.0,
                "test_queries": ["generate response", "create content"]
            }
        ],
        "availability_tests": [
            {
                "service": "gateway",
                "min_availability": 0.9995
            },
            {
                "service": "retrieval",
                "min_availability": 0.999
            },
            {
                "service": "synthesis", 
                "min_availability": 0.999
            }
        ]
    }

@pytest.fixture
def performance_test_data():
    """Performance test data for load testing"""
    return {
        "concurrent_requests": [1, 5, 10, 20, 50],
        "test_duration_seconds": 60,
        "ramp_up_seconds": 10,
        "test_queries": [
            "What is machine learning?",
            "How does a neural network work?",
            "Compare different AI approaches",
            "Write a Python function to sort a list"
        ]
    }

# Utility functions for tests
def assert_sla_compliance(response_time: float, threshold: float, tolerance: float = 0.1):
    """Assert SLA compliance with tolerance"""
    assert response_time <= threshold * (1 + tolerance), \
        f"Response time {response_time:.3f}s exceeds SLA threshold {threshold:.3f}s"

def assert_quality_score(score: float, min_score: float = 0.85):
    """Assert quality score meets minimum threshold"""
    assert score >= min_score, f"Quality score {score:.2f} below minimum threshold {min_score:.2f}"

def assert_guided_prompt_triggered(result: Dict[str, Any], expected: bool = True):
    """Assert Guided Prompt was triggered as expected"""
    triggered = result.get("guided_prompt_triggered", False)
    assert triggered == expected, f"Guided Prompt trigger mismatch: expected {expected}, got {triggered}"

def assert_response_success(result: Dict[str, Any]):
    """Assert response was successful"""
    assert result.get("success", False), f"Request failed: {result.get('error_message', 'Unknown error')}"

# Test data generators
def generate_test_queries(complexity: str, count: int = 5) -> list:
    """Generate test queries for a given complexity level"""
    query_templates = {
        "simple": [
            "What is the capital of {country}?",
            "Define {term}",
            "What is {percentage}% of {number}?",
            "Who is the current president of {country}?",
            "What day is it today?"
        ],
        "technical": [
            "How does {technology} work?",
            "Write a {language} function to {task}",
            "Explain the difference between {concept1} and {concept2}",
            "How do I use the {api} API?",
            "What is the difference between {tech1} and {tech2}?"
        ],
        "research": [
            "Compare the pros and cons of {topic}",
            "What are the latest developments in {field}?",
            "Analyze the impact of {technology} on {industry}",
            "Review the current state of {field}",
            "Evaluate the effectiveness of {approach}"
        ]
    }
    
    templates = query_templates.get(complexity, query_templates["simple"])
    return templates[:count]

def generate_guided_prompt_test_cases(scenario_type: str, count: int = 3) -> list:
    """Generate Guided Prompt test cases for a given scenario type"""
    test_cases = {
        "ambiguous": [
            "Show me {term}",
            "Tell me about {term}",
            "What's the latest on {term}?"
        ],
        "pii_heavy": [
            "My email is {email} and I need help",
            "Call me at {phone} about the meeting",
            "My SSN is {ssn}, help me with taxes"
        ],
        "multilingual": [
            "¿Cuál es la capital de {country}?",
            "{city}の人口は何人ですか？",
            "Quelle est la population de {city}?"
        ],
        "constraints": [
            "Show me recent news about {topic}",
            "Find academic papers on {subject}",
            "Search for free resources on {topic}"
        ]
    }
    
    templates = test_cases.get(scenario_type, test_cases["ambiguous"])
    return templates[:count]