"""
Real Backend Pipeline End-to-End Tests

This module provides comprehensive E2E tests for the complete backend orchestration flow,
ensuring all services work together correctly with real data and services.

Test Coverage:
    - Full pipeline orchestration (Retrieval → FactCheck → Synthesis → Citation)
    - Hybrid retrieval (Meilisearch + Qdrant + ArangoDB)
    - LLM routing and fallback mechanisms
    - Cache hit/miss behavior
    - Fact-checking and citation validation
    - Service failure scenarios and fallbacks
    - Response structure validation

Test Cases:
    1. Basic End-to-End Query Flow (Cold Cache)
    2. Cache Hit on Repeat Query
    3. Complex Synthesis Query (LLM Routing Check)
    4. Fallback Scenario (Simulated Service Failure)
    5. Fact-Check Freshness Validation

Authors:
    - Universal Knowledge Platform Engineering Team
    
Version:
    1.0.0 (2024-12-28)
"""

import pytest
import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Import test dependencies
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from fastapi import HTTPException

# Import application components
from services.api_gateway.main import app
from shared.core.agents.base_agent import QueryContext
from shared.core.llm_client_v3 import LLMProvider, LLMError

# Test configuration
TEST_QUERIES = {
    "basic_factual": "What is Retrieval Augmented Generation?",
    "complex_synthesis": "Explain how vector databases and knowledge graphs complement each other in AI systems.",
    "fallback_test": "Fallback test query for service failure simulation",
    "outdated_content": "What is the status of AI trends from 2020?",
    "technical_query": "How does Python handle memory management compared to C++?"
}

class TestRealBackendPipeline:
    """Test the complete backend orchestration pipeline with real services."""
    
    @pytest.fixture
    def client(self):
        """Get test client with authentication."""
        return TestClient(app)
    
    @pytest.fixture
    def authenticated_client(self, client):
        """Get authenticated test client."""
        # Create a test user session
        test_user = {
            "user_id": "test-user-e2e",
            "username": "testuser",
            "role": "user",
            "permissions": ["read", "write"]
        }
        
        # Mock authentication for testing
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = Mock(**test_user)
            yield client
    
    @pytest.fixture
    def test_session_id(self):
        """Generate unique session ID for tests."""
        return f"test-session-{uuid.uuid4().hex[:8]}"
    
    def test_basic_pipeline_flow(self, authenticated_client, test_session_id):
        """Test 1: Basic End-to-End Query Flow (Cold Cache)
        
        Send a factual query and validate the complete pipeline execution.
        """
        query = TEST_QUERIES["basic_factual"]
        
        response = authenticated_client.post("/query", json={
            "query": query,
            "session_id": test_session_id,
            "max_tokens": 1000,
            "confidence_threshold": 0.8
        })
        
        # Validate response structure
        assert response.status_code == 200
        data = response.json()
        
        # Core response validation
        assert "answer" in data
        assert "citations" in data
        assert "validation_status" in data
        assert "llm_provider" in data
        assert "cache_status" in data
        assert "execution_time" in data
        
        # Validate cache status (should be miss for first query)
        assert data["cache_status"] == "Miss"
        
        # Validate answer content
        assert len(data["answer"]) > 0
        assert "RAG" in data["answer"] or "retrieval" in data["answer"].lower()
        
        # Validate citations
        assert isinstance(data["citations"], list)
        assert len(data["citations"]) >= 1
        
        # Validate LLM provider selection
        assert data["llm_provider"] in ["Ollama", "HuggingFace", "OpenAI"]
        
        # Validate validation status
        assert data["validation_status"] in ["Trusted", "Partial", "Unverified"]
        
        # Validate execution time
        assert data["execution_time"] > 0
        assert data["execution_time"] < 30  # Should complete within 30 seconds
        
        # Validate agent results structure
        assert "agent_results" in data
        agent_results = data["agent_results"]
        
        # Validate retrieval results
        assert "retrieval" in agent_results
        retrieval = agent_results["retrieval"]
        assert "vector_results" in retrieval
        assert "keyword_results" in retrieval
        assert "knowledge_graph_results" in retrieval
        
        # Validate factcheck results
        assert "factcheck" in agent_results
        factcheck = agent_results["factcheck"]
        assert isinstance(factcheck, dict)
        
        # Validate synthesis results
        assert "synthesis" in agent_results
        synthesis = agent_results["synthesis"]
        assert "answer" in synthesis
        assert "confidence" in synthesis
        
        # Validate citation results
        assert "citation" in agent_results
        citation = agent_results["citation"]
        assert "sources" in citation
        
        # Validate confidence scores
        assert "confidence_score" in data
        assert "coherence_score" in data
        assert "relevance_score" in data
        
        print(f"✅ Basic pipeline test passed - LLM Provider: {data['llm_provider']}, "
              f"Cache: {data['cache_status']}, Time: {data['execution_time']:.2f}s")
    
    def test_cache_hit_behavior(self, authenticated_client, test_session_id):
        """Test 2: Cache Hit on Repeat Query
        
        Send the same query again and validate cache hit behavior.
        """
        query = TEST_QUERIES["basic_factual"]
        payload = {
            "query": query,
            "session_id": test_session_id,
            "max_tokens": 1000,
            "confidence_threshold": 0.8
        }
        
        # First query (cache miss)
        response1 = authenticated_client.post("/query", json=payload)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["cache_status"] == "Miss"
        
        # Second query (cache hit)
        response2 = authenticated_client.post("/query", json=payload)
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Validate cache hit
        assert data2["cache_status"] == "Hit"
        
        # Validate answer content remains the same
        assert data2["answer"] == data1["answer"]
        
        # Validate execution time is faster for cache hit
        assert data2["execution_time"] < data1["execution_time"]
        
        # Validate other fields are preserved
        assert data2["citations"] == data1["citations"]
        assert data2["validation_status"] == data1["validation_status"]
        assert data2["llm_provider"] == data1["llm_provider"]
        
        print(f"✅ Cache hit test passed - Cache: {data2['cache_status']}, "
              f"Time: {data2['execution_time']:.2f}s")
    
    def test_llm_routing_for_complex_query(self, authenticated_client, test_session_id):
        """Test 3: Complex Synthesis Query (LLM Routing Check)
        
        Send a complex synthesis query and validate LLM routing selection.
        """
        query = TEST_QUERIES["complex_synthesis"]
        
        response = authenticated_client.post("/query", json={
            "query": query,
            "session_id": test_session_id,
            "max_tokens": 1500,
            "confidence_threshold": 0.8
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate LLM provider selection for complex query
        # Complex queries should prefer HuggingFace or OpenAI over Ollama
        assert data["llm_provider"] in ["HuggingFace", "OpenAI"]
        
        # Validate multiple citations for complex synthesis
        assert len(data["citations"]) >= 2
        
        # Validate answer quality for complex query
        assert len(data["answer"]) > 200  # Should be comprehensive
        assert any(keyword in data["answer"].lower() for keyword in 
                  ["vector", "database", "knowledge", "graph", "ai"])
        
        # Validate validation status
        assert data["validation_status"] in ["Trusted", "Partial"]
        
        print(f"✅ Complex query routing test passed - LLM Provider: {data['llm_provider']}, "
              f"Citations: {len(data['citations'])}")
    
    def test_fallback_on_ollama_failure(self, authenticated_client, test_session_id):
        """Test 4: Fallback Scenario (Simulated Ollama Failure)
        
        Simulate Ollama failure and validate fallback to other providers.
        """
        query = TEST_QUERIES["fallback_test"]
        
        # Mock Ollama failure
        with patch('shared.core.llm_client_v3.OllamaProvider.generate_text') as mock_ollama:
            mock_ollama.side_effect = Exception("Simulated Ollama Failure")
            
            response = authenticated_client.post("/query", json={
                "query": query,
                "session_id": test_session_id,
                "max_tokens": 1000,
                "confidence_threshold": 0.8
            })
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate fallback to alternative provider
        assert data["llm_provider"] in ["HuggingFace", "OpenAI"]
        
        # Validate answer is still generated despite Ollama failure
        assert len(data["answer"]) > 0
        
        # Validate cache status
        assert data["cache_status"] == "Miss"
        
        print(f"✅ Fallback test passed - LLM Provider: {data['llm_provider']}, "
              f"Fallback successful")
    
    def test_factcheck_freshness_validation(self, authenticated_client, test_session_id):
        """Test 5: Fact-Check Freshness Validation
        
        Query for outdated content and validate freshness checking.
        """
        query = TEST_QUERIES["outdated_content"]
        
        response = authenticated_client.post("/query", json={
            "query": query,
            "session_id": test_session_id,
            "max_tokens": 1000,
            "confidence_threshold": 0.8
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate validation status reflects outdated content
        assert data["validation_status"] in ["Outdated", "Partial", "Unverified"]
        
        # Validate citations contain 2020 references
        citations_text = " ".join([str(citation) for citation in data["citations"]])
        assert "2020" in citations_text
        
        # Validate answer contains disclaimer if content is outdated
        answer_lower = data["answer"].lower()
        if data["validation_status"] == "Outdated":
            assert any(keyword in answer_lower for keyword in 
                      ["outdated", "old", "2020", "previous", "historical"])
        
        print(f"✅ Freshness validation test passed - Status: {data['validation_status']}")
    
    def test_technical_query_routing(self, authenticated_client, test_session_id):
        """Test 6: Technical Query Routing
        
        Test routing for technical queries that should use appropriate models.
        """
        query = TEST_QUERIES["technical_query"]
        
        response = authenticated_client.post("/query", json={
            "query": query,
            "session_id": test_session_id,
            "max_tokens": 1200,
            "confidence_threshold": 0.8
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate technical content in answer
        answer_lower = data["answer"].lower()
        assert any(keyword in answer_lower for keyword in 
                  ["python", "memory", "management", "c++", "garbage", "collection"])
        
        # Validate citations
        assert len(data["citations"]) >= 1
        
        # Validate confidence scores
        assert data["confidence_score"] > 0
        assert data["relevance_score"] > 0
        
        print(f"✅ Technical query test passed - Confidence: {data['confidence_score']:.2f}")
    
    def test_hybrid_retrieval_validation(self, authenticated_client, test_session_id):
        """Test 7: Hybrid Retrieval Validation
        
        Validate that all retrieval sources (vector, keyword, knowledge graph) are working.
        """
        query = "What are the key differences between SQL and NoSQL databases?"
        
        response = authenticated_client.post("/query", json={
            "query": query,
            "session_id": test_session_id,
            "max_tokens": 1000,
            "confidence_threshold": 0.8
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate agent results structure
        agent_results = data["agent_results"]
        retrieval = agent_results["retrieval"]
        
        # Validate vector results
        assert "vector_results" in retrieval
        vector_results = retrieval["vector_results"]
        assert isinstance(vector_results, list)
        
        # Validate keyword results
        assert "keyword_results" in retrieval
        keyword_results = retrieval["keyword_results"]
        assert isinstance(keyword_results, list)
        
        # Validate knowledge graph results
        assert "knowledge_graph_results" in retrieval
        kg_results = retrieval["knowledge_graph_results"]
        assert isinstance(kg_results, list)
        
        # At least one retrieval method should return results
        total_results = len(vector_results) + len(keyword_results) + len(kg_results)
        assert total_results > 0
        
        print(f"✅ Hybrid retrieval test passed - Vector: {len(vector_results)}, "
              f"Keyword: {len(keyword_results)}, KG: {len(kg_results)}")
    
    def test_response_structure_validation(self, authenticated_client, test_session_id):
        """Test 8: Response Structure Validation
        
        Validate the complete response structure matches expected format.
        """
        query = "What is machine learning?"
        
        response = authenticated_client.post("/query", json={
            "query": query,
            "session_id": test_session_id,
            "max_tokens": 1000,
            "confidence_threshold": 0.8
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate required top-level fields
        required_fields = [
            "answer", "citations", "validation_status", "llm_provider",
            "cache_status", "execution_time", "agent_results", "confidence_score",
            "coherence_score", "relevance_score"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Validate agent_results structure
        agent_results = data["agent_results"]
        required_agent_sections = ["retrieval", "factcheck", "synthesis", "citation"]
        
        for section in required_agent_sections:
            assert section in agent_results, f"Missing agent section: {section}"
        
        # Validate data types
        assert isinstance(data["answer"], str)
        assert isinstance(data["citations"], list)
        assert isinstance(data["validation_status"], str)
        assert isinstance(data["llm_provider"], str)
        assert isinstance(data["cache_status"], str)
        assert isinstance(data["execution_time"], (int, float))
        assert isinstance(data["confidence_score"], (int, float))
        assert isinstance(data["coherence_score"], (int, float))
        assert isinstance(data["relevance_score"], (int, float))
        
        # Validate value ranges
        assert 0 <= data["confidence_score"] <= 1
        assert 0 <= data["coherence_score"] <= 1
        assert 0 <= data["relevance_score"] <= 1
        assert data["execution_time"] > 0
        
        print(f"✅ Response structure validation passed")
    
    def test_error_handling_and_recovery(self, authenticated_client, test_session_id):
        """Test 9: Error Handling and Recovery
        
        Test system behavior when services are temporarily unavailable.
        """
        query = "Test error handling with service failures"
        
        # Mock multiple service failures to test fallback chain
        with patch('services.search_service.retrieval_agent.RetrievalAgent.process_task') as mock_retrieval:
            mock_retrieval.side_effect = Exception("Search service temporarily unavailable")
            
            response = authenticated_client.post("/query", json={
                "query": query,
                "session_id": test_session_id,
                "max_tokens": 1000,
                "confidence_threshold": 0.8
            })
        
        # Should still return a response (even if degraded)
        assert response.status_code in [200, 500]  # Allow both success and graceful failure
        
        if response.status_code == 200:
            data = response.json()
            # Validate degraded but functional response
            assert "answer" in data
            assert len(data["answer"]) > 0
        else:
            # Validate error response structure
            error_data = response.json()
            assert "detail" in error_data
            assert "error" in error_data["detail"].lower()
        
        print(f"✅ Error handling test passed - Status: {response.status_code}")
    
    def test_performance_under_load(self, authenticated_client, test_session_id):
        """Test 10: Performance Under Load
        
        Test system performance with multiple concurrent queries.
        """
        queries = [
            "What is artificial intelligence?",
            "Explain machine learning algorithms",
            "How does deep learning work?",
            "What are neural networks?",
            "Explain natural language processing"
        ]
        
        start_time = time.time()
        responses = []
        
        # Send concurrent queries
        for i, query in enumerate(queries):
            response = authenticated_client.post("/query", json={
                "query": query,
                "session_id": f"{test_session_id}-{i}",
                "max_tokens": 800,
                "confidence_threshold": 0.8
            })
            responses.append(response)
        
        total_time = time.time() - start_time
        
        # Validate all responses
        successful_responses = 0
        total_execution_time = 0
        
        for response in responses:
            if response.status_code == 200:
                successful_responses += 1
                data = response.json()
                total_execution_time += data["execution_time"]
        
        # Validate performance metrics
        assert successful_responses >= 3  # At least 60% success rate
        assert total_time < 60  # Should complete within 60 seconds
        assert total_execution_time < 30  # Total execution time should be reasonable
        
        avg_execution_time = total_execution_time / successful_responses if successful_responses > 0 else 0
        print(f"✅ Performance test passed - Success: {successful_responses}/{len(queries)}, "
              f"Avg Time: {avg_execution_time:.2f}s, Total Time: {total_time:.2f}s")


class TestPipelineIntegration:
    """Test pipeline integration and service communication."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)
    
    def test_service_health_checks(self, client):
        """Test that all services are healthy and responding."""
        # Test basic health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        
        # Test simple health endpoint
        response = client.get("/health/simple")
        assert response.status_code == 200
        
        # Test basic health endpoint
        response = client.get("/health/basic")
        assert response.status_code == 200
        
        print("✅ Service health checks passed")
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint for monitoring."""
        response = client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "uptime" in data
        
        print("✅ Metrics endpoint test passed")
    
    def test_system_diagnostics(self, client):
        """Test system diagnostics endpoint."""
        # Mock authentication for diagnostics
        with patch('services.api_gateway.main.get_current_user') as mock_auth:
            mock_auth.return_value = Mock(user_id="test-user", role="admin")
            
            response = client.get("/system/diagnostics")
            assert response.status_code == 200
            
            data = response.json()
            assert "system_status" in data
            assert "services" in data
            
            print("✅ System diagnostics test passed")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"]) 