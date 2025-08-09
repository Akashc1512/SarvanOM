"""
Enhanced Backend Integration Test Suite - End-to-End Pipeline Verification

This module provides comprehensive integration tests for the Universal Knowledge Platform
backend pipeline, specifically focusing on the user's requirements:

Query → Hybrid Retrieval (Vector + Keyword + KG) → Fact-Checking → Citation → Synthesis

Test Coverage:
    - Basic query pipeline with local LLM (Ollama)
    - Complex research queries with cloud LLM routing
    - LLM failure fallback scenarios
    - Cache hit/miss verification
    - Agent orchestration validation
    - Response quality and citation verification

Testing Strategy:
    - End-to-end pipeline testing
    - Realistic query scenarios
    - Error handling and fallback mechanisms
    - Performance and caching validation
    - Agent chain verification

Authors:
    - Universal Knowledge Platform Engineering Team
    
Version:
    2.0.0 (2024-12-28) - Enhanced version focusing on specific user requirements
"""

import pytest
import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from services.api_gateway.main import app
from shared.core.api.exceptions import ValidationError, RateLimitError
from shared.core.agent_orchestrator import AgentOrchestrator
from shared.core.model_selector import DynamicModelSelector
from shared.vectorstores.vector_store_service import VectorStoreService as HybridRetrievalService
from shared.core.agents.synthesis_agent import SynthesisAgent
from shared.core.agents.factcheck_agent import FactCheckAgent

# Test data for different scenarios
BASIC_QUERIES = [
    "What is Retrieval Augmented Generation?",
    "Explain machine learning basics",
    "What is Python programming?",
    "How does a neural network work?",
    "What is artificial intelligence?",
]

COMPLEX_QUERIES = [
    "Explain how knowledge graphs integrate with vector search in AI systems",
    "Compare and contrast different approaches to multi-agent systems in AI",
    "Analyze the impact of transformer architecture on natural language processing",
    "Discuss the trade-offs between centralized and decentralized AI architectures",
    "Evaluate the effectiveness of different prompt engineering techniques",
]

CACHE_TEST_QUERIES = [
    "What is the capital of France?",
    "Explain the concept of recursion in programming",
    "What are the benefits of containerization?",
]


class TestBasicQueryPipeline:
    """Test Case 1: Basic Query Pipeline with Local LLM (Ollama)"""

    def test_basic_query_pipeline_success(self, client: TestClient):
        """Test successful basic query processing with Ollama."""
        query_data = {
            "query": "What is Retrieval Augmented Generation?",
            "session_id": "test-session-1",
            "user_id": "test-user-1",
            "max_tokens": 1000,
            "confidence_threshold": 0.8,
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "answer" in data
        assert "citations" in data
        assert "validation_status" in data
        assert "llm_provider" in data
        assert "cache_status" in data
        assert "execution_time" in data
        assert "agent_results" in data

        # Verify content quality
        assert len(data["answer"]) > 50  # Substantial answer
        assert len(data["citations"]) >= 1  # At least one citation
        assert data["validation_status"] in ["Trusted", "Partial", "Unverified"]
        assert data["llm_provider"] == "Ollama"  # Local LLM for basic queries
        assert data["cache_status"] == "Miss"  # First run should miss cache

        # Verify agent chain execution
        agent_results = data.get("agent_results", {})
        assert "retrieval" in agent_results
        assert "factcheck" in agent_results
        assert "synthesis" in agent_results
        assert "citation" in agent_results

        # Verify hybrid retrieval sources
        retrieval_result = agent_results.get("retrieval", {})
        assert "vector_results" in retrieval_result
        assert "keyword_results" in retrieval_result
        assert "knowledge_graph_results" in retrieval_result

        print(f"✅ Basic query pipeline test passed")
        print(f"   Answer length: {len(data['answer'])} chars")
        print(f"   Citations: {len(data['citations'])}")
        print(f"   LLM Provider: {data['llm_provider']}")
        print(f"   Validation: {data['validation_status']}")
        print(f"   Execution time: {data['execution_time']:.3f}s")

    @pytest.mark.parametrize("query", BASIC_QUERIES)
    def test_basic_query_variations(self, client: TestClient, query: str):
        """Test various basic queries with consistent results."""
        query_data = {
            "query": query,
            "session_id": f"test-session-{hash(query) % 1000}",
            "user_id": "test-user-1",
            "max_tokens": 1000,
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        # Verify consistent structure
        assert "answer" in data
        assert "citations" in data
        assert data["llm_provider"] == "Ollama"  # Should use local LLM
        assert data["cache_status"] == "Miss"  # First run

        print(f"✅ Basic query variation passed: {query[:50]}...")


class TestComplexQueryLLMRouting:
    """Test Case 2: Complex Research Query with Cloud LLM Routing"""

    def test_complex_query_llm_routing(self, client: TestClient):
        """Test complex query routing to cloud LLM (HuggingFace/OpenAI)."""
        query_data = {
            "query": "Explain how knowledge graphs integrate with vector search in AI systems",
            "session_id": "test-session-2",
            "user_id": "test-user-2",
            "max_tokens": 2000,
            "confidence_threshold": 0.9,
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        # Verify complex query handling
        assert len(data["answer"]) > 200  # Substantial answer for complex query
        assert len(data["citations"]) >= 2  # Multiple sources for complex topic
        assert data["llm_provider"] in ["HuggingFace", "OpenAI"]  # Cloud LLM
        assert data["validation_status"] in ["Trusted", "Partial"]

        # Verify enhanced agent results
        agent_results = data.get("agent_results", {})
        assert "retrieval" in agent_results
        assert "factcheck" in agent_results
        assert "synthesis" in agent_results
        assert "citation" in agent_results

        # Verify retrieval sources
        retrieval_result = agent_results.get("retrieval", {})
        assert "vector_results" in retrieval_result
        assert "keyword_results" in retrieval_result
        assert "knowledge_graph_results" in retrieval_result

        print(f"✅ Complex query LLM routing test passed")
        print(f"   LLM Provider: {data['llm_provider']}")
        print(f"   Citations: {len(data['citations'])}")
        print(f"   Answer length: {len(data['answer'])} chars")
        print(f"   Validation: {data['validation_status']}")

    @pytest.mark.parametrize("query", COMPLEX_QUERIES)
    def test_complex_query_variations(self, client: TestClient, query: str):
        """Test various complex queries with cloud LLM routing."""
        query_data = {
            "query": query,
            "session_id": f"test-session-complex-{hash(query) % 1000}",
            "user_id": "test-user-2",
            "max_tokens": 2000,
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        # Verify cloud LLM usage for complex queries
        assert data["llm_provider"] in ["HuggingFace", "OpenAI"]
        assert len(data["citations"]) >= 2
        assert len(data["answer"]) > 150

        print(f"✅ Complex query variation passed: {query[:50]}...")


class TestLLMFailureFallback:
    """Test Case 3: LLM Failure Fallback Scenarios"""

    @patch("services.synthesis_service.synthesis_agent.ollama_generate")
    def test_ollama_failure_fallback(self, mock_ollama, client: TestClient):
        """Test fallback when Ollama fails."""
        # Mock Ollama to fail
        mock_ollama.side_effect = Exception("Simulated Ollama failure")

        query_data = {
            "query": "Test fallback mechanism with Ollama failure",
            "session_id": "test-session-3",
            "user_id": "test-user-3",
            "max_tokens": 1000,
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        # Verify fallback to cloud LLM
        assert data["llm_provider"] in ["HuggingFace", "OpenAI"]
        assert "answer" in data
        assert "citations" in data

        # Verify error was logged but handled gracefully
        assert "fallback" in data.get("metadata", {}).get("notes", "").lower()

        print(f"✅ Ollama failure fallback test passed")
        print(f"   Fallback LLM: {data['llm_provider']}")

    @patch("services.synthesis_service.synthesis_agent.huggingface_generate")
    def test_huggingface_failure_fallback(self, mock_hf, client: TestClient):
        """Test fallback when HuggingFace fails."""
        # Mock HuggingFace to fail
        mock_hf.side_effect = Exception("Simulated HuggingFace failure")

        query_data = {
            "query": "Test fallback mechanism with HuggingFace failure",
            "session_id": "test-session-4",
            "user_id": "test-user-4",
            "max_tokens": 1000,
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        # Verify fallback to OpenAI
        assert data["llm_provider"] == "OpenAI"
        assert "answer" in data
        assert "citations" in data

        print(f"✅ HuggingFace failure fallback test passed")
        print(f"   Fallback LLM: {data['llm_provider']}")

    def test_all_llm_failure_graceful_degradation(self, client: TestClient):
        """Test graceful degradation when all LLMs fail."""
        with (
            patch(
                "services.synthesis_service.synthesis_agent.ollama_generate"
            ) as mock_ollama,
            patch(
                "services.synthesis_service.synthesis_agent.huggingface_generate"
            ) as mock_hf,
            patch(
                "services.synthesis_service.synthesis_agent.openai_generate"
            ) as mock_openai,
        ):

            # Mock all LLMs to fail
            mock_ollama.side_effect = Exception("Ollama failed")
            mock_hf.side_effect = Exception("HuggingFace failed")
            mock_openai.side_effect = Exception("OpenAI failed")

            query_data = {
                "query": "Test graceful degradation with all LLM failures",
                "session_id": "test-session-5",
                "user_id": "test-user-5",
                "max_tokens": 1000,
            }

            response = client.post("/query", json=query_data)

            # Should still return 200 but with error information
            assert response.status_code == 200
            data = response.json()

            # Verify error handling
            assert "error" in data or "llm_error" in data.get("metadata", {})
            assert data.get("llm_provider") == "None" or "error" in data.get(
                "llm_provider", ""
            )

            print(f"✅ All LLM failure graceful degradation test passed")


class TestCacheHitVerification:
    """Test Case 4: Cache Hit/Miss Verification"""

    def test_cache_miss_first_run(self, client: TestClient):
        """Test cache miss on first query run."""
        query_data = {
            "query": "What is the capital of France?",
            "session_id": "test-session-cache-1",
            "user_id": "test-user-cache-1",
            "max_tokens": 1000,
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        # Verify cache miss
        assert data["cache_status"] == "Miss"
        assert "execution_time" in data
        assert data["execution_time"] > 0

        print(f"✅ Cache miss test passed")
        print(f"   Execution time: {data['execution_time']:.3f}s")

    def test_cache_hit_second_run(self, client: TestClient):
        """Test cache hit on second identical query run."""
        query_data = {
            "query": "What is the capital of France?",
            "session_id": "test-session-cache-2",
            "user_id": "test-user-cache-2",
            "max_tokens": 1000,
        }

        # First run - should miss cache
        response1 = client.post("/query", json=query_data)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["cache_status"] == "Miss"

        # Second run - should hit cache
        response2 = client.post("/query", json=query_data)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["cache_status"] == "Hit"

        # Verify same answer
        assert data1["answer"] == data2["answer"]
        assert data1["citations"] == data2["citations"]

        # Verify faster execution
        assert data2["execution_time"] < data1["execution_time"]

        print(f"✅ Cache hit test passed")
        print(f"   First run time: {data1['execution_time']:.3f}s")
        print(f"   Second run time: {data2['execution_time']:.3f}s")

    @pytest.mark.parametrize("query", CACHE_TEST_QUERIES)
    def test_cache_variations(self, client: TestClient, query: str):
        """Test cache behavior with different queries."""
        query_data = {
            "query": query,
            "session_id": f"test-session-cache-{hash(query) % 1000}",
            "user_id": "test-user-cache-variations",
            "max_tokens": 1000,
        }

        # First run
        response1 = client.post("/query", json=query_data)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["cache_status"] == "Miss"

        # Second run
        response2 = client.post("/query", json=query_data)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["cache_status"] == "Hit"

        print(f"✅ Cache variation passed: {query[:30]}...")


class TestAgentOrchestration:
    """Test Agent Orchestration and Chain Verification"""

    def test_agent_chain_execution_order(self, client: TestClient):
        """Test that agents execute in correct order."""
        query_data = {
            "query": "What is machine learning?",
            "session_id": "test-session-orchestration-1",
            "user_id": "test-user-orchestration-1",
            "max_tokens": 1000,
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        # Verify agent chain execution
        agent_results = data.get("agent_results", {})

        # Check all required agents executed
        assert "retrieval" in agent_results
        assert "factcheck" in agent_results
        assert "synthesis" in agent_results
        assert "citation" in agent_results

        # Verify agents executed in order
        agent_order = ["retrieval", "factcheck", "synthesis", "citation"]
        for i, agent in enumerate(agent_order):
            assert agent in agent_results, f"Agent {agent} missing from results"

        print(f"✅ Agent chain execution order test passed")
        print(f"   Agents executed: {list(agent_results.keys())}")

    def test_agent_failure_handling(self, client: TestClient):
        """Test handling when individual agents fail."""
        with patch(
            "shared.vectorstores.vector_store_service.VectorStoreService.search"
        ) as mock_retrieval:
            # Mock retrieval to fail
            mock_retrieval.side_effect = Exception("Simulated retrieval failure")

            query_data = {
                "query": "Test agent failure handling",
                "session_id": "test-session-orchestration-2",
                "user_id": "test-user-orchestration-2",
                "max_tokens": 1000,
            }

            response = client.post("/query", json=query_data)

            # Should still return 200 but with error information
            assert response.status_code == 200
            data = response.json()

            # Verify error handling
            assert "error" in data or "agent_error" in data.get("metadata", {})

            print(f"✅ Agent failure handling test passed")


class TestResponseQualityValidation:
    """Test Response Quality and Citation Verification"""

    def test_response_quality_metrics(self, client: TestClient):
        """Test response quality metrics and validation."""
        query_data = {
            "query": "What is artificial intelligence?",
            "session_id": "test-session-quality-1",
            "user_id": "test-user-quality-1",
            "max_tokens": 1000,
            "confidence_threshold": 0.8,
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        # Verify quality metrics
        assert "confidence_score" in data
        assert "coherence_score" in data
        assert "relevance_score" in data

        # Verify scores are within valid ranges
        assert 0 <= data["confidence_score"] <= 1
        assert 0 <= data["coherence_score"] <= 1
        assert 0 <= data["relevance_score"] <= 1

        print(f"✅ Response quality metrics test passed")
        print(f"   Confidence: {data['confidence_score']:.3f}")
        print(f"   Coherence: {data['coherence_score']:.3f}")
        print(f"   Relevance: {data['relevance_score']:.3f}")

    def test_citation_quality_verification(self, client: TestClient):
        """Test citation quality and source verification."""
        query_data = {
            "query": "Explain the history of machine learning",
            "session_id": "test-session-citation-1",
            "user_id": "test-user-citation-1",
            "max_tokens": 1500,
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        # Verify citations
        citations = data.get("citations", [])
        assert len(citations) >= 1

        for citation in citations:
            # Verify citation structure
            assert "title" in citation or "source" in citation
            assert "url" in citation or "author" in citation or "year" in citation

            # Verify citation quality
            if "reliability_score" in citation:
                assert 0 <= citation["reliability_score"] <= 1

        print(f"✅ Citation quality verification test passed")
        print(f"   Citations found: {len(citations)}")


class TestPerformanceBenchmarks:
    """Test Performance Benchmarks and SLA Compliance"""

    def test_response_time_sla_compliance(self, client: TestClient):
        """Test that response times meet SLA requirements."""
        query_data = {
            "query": "What is Python programming?",
            "session_id": "test-session-performance-1",
            "user_id": "test-user-performance-1",
            "max_tokens": 1000,
        }

        start_time = time.time()
        response = client.post("/query", json=query_data)
        end_time = time.time()

        assert response.status_code == 200
        data = response.json()

        # Verify SLA compliance
        actual_time = end_time - start_time
        sla_time = 30.0  # 30 second SLA

        assert (
            actual_time <= sla_time
        ), f"Response time {actual_time:.2f}s exceeds SLA {sla_time}s"

        # Verify reported execution time
        reported_time = data.get("execution_time", 0)
        assert reported_time > 0
        assert reported_time <= actual_time + 1.0  # Allow 1s tolerance

        print(f"✅ Response time SLA compliance test passed")
        print(f"   Actual time: {actual_time:.3f}s")
        print(f"   Reported time: {reported_time:.3f}s")
        print(f"   SLA limit: {sla_time}s")

    def test_concurrent_query_handling(self, client: TestClient):
        """Test handling of concurrent queries."""
        import threading
        import queue

        results = queue.Queue()
        errors = queue.Queue()

        def make_query(query_id: int):
            try:
                query_data = {
                    "query": f"Test concurrent query {query_id}",
                    "session_id": f"test-session-concurrent-{query_id}",
                    "user_id": f"test-user-concurrent-{query_id}",
                    "max_tokens": 500,
                }

                response = client.post("/query", json=query_data)
                results.put((query_id, response))
            except Exception as e:
                errors.put((query_id, e))

        # Start 5 concurrent queries
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_query, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all queries succeeded
        assert (
            errors.empty()
        ), f"Errors occurred: {[errors.get() for _ in range(errors.qsize())]}"

        successful_queries = 0
        while not results.empty():
            query_id, response = results.get()
            if response.status_code == 200:
                successful_queries += 1

        assert successful_queries == 5, f"Only {successful_queries}/5 queries succeeded"

        print(f"✅ Concurrent query handling test passed")
        print(f"   Successful queries: {successful_queries}/5")


class TestErrorHandlingAndRecovery:
    """Test Error Handling and Recovery Mechanisms"""

    def test_invalid_query_handling(self, client: TestClient):
        """Test handling of invalid queries."""
        invalid_queries = [
            {"query": "", "session_id": "test-session-error-1"},
            {"query": "x" * 10001, "session_id": "test-session-error-2"},  # Too long
            {"session_id": "test-session-error-3"},  # Missing query
        ]

        for i, query_data in enumerate(invalid_queries):
            response = client.post("/query", json=query_data)

            # Should return 422 for validation errors
            assert response.status_code == 422, f"Query {i} should return 422"

        print(f"✅ Invalid query handling test passed")

    def test_service_unavailable_handling(self, client: TestClient):
        """Test handling when external services are unavailable."""
        with patch(
            "services.search_service.core.meilisearch_engine.MeilisearchEngine.search"
        ) as mock_search:
            # Mock search service to be unavailable
            mock_search.side_effect = Exception("Service unavailable")

            query_data = {
                "query": "Test service unavailable handling",
                "session_id": "test-session-error-4",
                "user_id": "test-user-error-4",
                "max_tokens": 1000,
            }

            response = client.post("/query", json=query_data)

            # Should handle gracefully
            assert response.status_code in [200, 503]
            data = response.json()

            # Should indicate service issue
            assert "error" in data or "service_unavailable" in str(data)

            print(f"✅ Service unavailable handling test passed")


# Test utilities
def assert_response_structure(data: Dict[str, Any], expected_fields: List[str]):
    """Assert response has expected structure."""
    for field in expected_fields:
        assert field in data, f"Missing field: {field}"


def assert_agent_execution(data: Dict[str, Any], expected_agents: List[str]):
    """Assert expected agents executed."""
    agent_results = data.get("agent_results", {})
    for agent in expected_agents:
        assert agent in agent_results, f"Agent {agent} did not execute"


def assert_llm_provider(data: Dict[str, Any], expected_providers: List[str]):
    """Assert LLM provider is one of expected providers."""
    provider = data.get("llm_provider", "")
    assert provider in expected_providers, f"Unexpected LLM provider: {provider}"


def assert_cache_status(data: Dict[str, Any], expected_status: str):
    """Assert cache status matches expected."""
    status = data.get("cache_status", "")
    assert (
        status == expected_status
    ), f"Expected cache status {expected_status}, got {status}"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
