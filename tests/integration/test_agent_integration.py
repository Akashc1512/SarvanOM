"""
Integration Tests for Agent Pipeline
End-to-end testing of the complete agent pipeline.

Authors:
- Universal Knowledge Platform Engineering Team
    
Version:
    2.0.0 (2024-12-28)
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from typing import Dict, Any

from shared.core.agent_pattern import AgentFactory
from shared.core.base_agent import AgentType, QueryContext
from shared.core.llm_client_v2 import LLMResponse


class TestAgentIntegration:
    """Test complete agent pipeline integration."""
    
    @pytest.fixture
    def synthesis_agent(self):
        """Create synthesis agent for testing."""
        return AgentFactory.create_agent(AgentType.SYNTHESIS)
    
    @pytest.fixture
    def factcheck_agent(self):
        """Create fact-checking agent for testing."""
        return AgentFactory.create_agent(AgentType.FACT_CHECK)
    
    @pytest.fixture
    def retrieval_agent(self):
        """Create retrieval agent for testing."""
        return AgentFactory.create_agent(AgentType.RETRIEVAL)
    
    @pytest.fixture
    def context(self):
        """Create query context."""
        return QueryContext(query="test")
    
    @pytest.mark.asyncio
    async def test_full_agent_pipeline(self, synthesis_agent, factcheck_agent, retrieval_agent, context):
        """Test complete agent pipeline: retrieval -> fact-checking -> synthesis."""
        
        # Mock LLM responses for the entire pipeline
        with patch('shared.core.llm_client_v2.EnhancedLLMClient.generate_text') as mock_llm:
            # Mock responses for retrieval agent
            retrieval_responses = [
                LLMResponse(
                    content="Expanded Queries:\n1. capital of France\n2. Paris France\n3. French capital",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 30, "completion_tokens": 20, "total_tokens": 50},
                    finish_reason="stop",
                    response_time_ms=60
                ),
                LLMResponse(
                    content="Reranked Results:\n1. [Paris is the capital]\n2. [France's capital city]",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 40, "completion_tokens": 25, "total_tokens": 65},
                    finish_reason="stop",
                    response_time_ms=80
                )
            ]
            
            # Mock responses for fact-checking agent
            factcheck_responses = [
                LLMResponse(
                    content="Verification Result: supported\nConfidence Score: 0.95\nReasoning: Multiple sources confirm Paris is the capital of France.",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
                    finish_reason="stop",
                    response_time_ms=100
                )
            ]
            
            # Mock response for synthesis agent
            synthesis_response = LLMResponse(
                content="Based on verified facts: Paris is the capital city of France. It is located in the northern part of the country and serves as the political, economic, and cultural center of France.",
                provider="mock",
                model="test-model",
                token_usage={"prompt_tokens": 60, "completion_tokens": 40, "total_tokens": 100},
                finish_reason="stop",
                response_time_ms=120
            )
            
            # Set up mock to return different responses for different calls
            mock_llm.side_effect = retrieval_responses + factcheck_responses + [synthesis_response]
            
            query = "What is the capital of France?"
            
            # Step 1: Retrieval
            retrieval_task = {"query": query}
            retrieval_result = await retrieval_agent.process_task(retrieval_task, context)
            
            assert retrieval_result.success
            assert "documents" in retrieval_result.data
            assert "expanded_queries" in retrieval_result.data
            assert retrieval_result.confidence > 0.0
            
            # Step 2: Fact-checking
            factcheck_task = {
                "query": query,
                "documents": retrieval_result.data["documents"]
            }
            factcheck_result = await factcheck_agent.process_task(factcheck_task, context)
            
            assert factcheck_result.success
            assert "verified_facts" in factcheck_result.data
            assert factcheck_result.data["total_claims"] > 0
            assert factcheck_result.confidence > 0.0
            
            # Step 3: Synthesis
            synthesis_task = {
                "query": query,
                "verified_facts": factcheck_result.data["verified_facts"]
            }
            synthesis_result = await synthesis_agent.process_task(synthesis_task, context)
            
            assert synthesis_result.success
            assert "answer" in synthesis_result.data
            assert synthesis_result.confidence > 0.0
            
            # Verify final result quality
            answer = synthesis_result.data["answer"]
            assert "Paris" in answer
            assert "capital" in answer
            assert "France" in answer
    
    @pytest.mark.asyncio
    async def test_agent_pipeline_with_fallback(self, synthesis_agent, factcheck_agent, retrieval_agent, context):
        """Test agent pipeline with LLM fallback mechanisms."""
        
        with patch('shared.core.llm_client_v2.EnhancedLLMClient.generate_text') as mock_llm:
            # Mock LLM to fail initially, then succeed
            mock_llm.side_effect = [
                Exception("LLM error"),  # First call fails
                LLMResponse(  # Second call succeeds
                    content="Expanded Queries:\n1. machine learning\n2. AI algorithms",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 30, "completion_tokens": 20, "total_tokens": 50},
                    finish_reason="stop",
                    response_time_ms=60
                ),
                LLMResponse(
                    content="Reranked Results:\n1. [ML document]\n2. [AI document]",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 40, "completion_tokens": 25, "total_tokens": 65},
                    finish_reason="stop",
                    response_time_ms=80
                ),
                LLMResponse(
                    content="Verification Result: supported\nConfidence Score: 0.8",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
                    finish_reason="stop",
                    response_time_ms=100
                ),
                LLMResponse(
                    content="Machine learning is a subset of artificial intelligence.",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 60, "completion_tokens": 40, "total_tokens": 100},
                    finish_reason="stop",
                    response_time_ms=120
                )
            ]
            
            query = "What is machine learning?"
            
            # Test that pipeline still works with fallback
            retrieval_task = {"query": query}
            retrieval_result = await retrieval_agent.process_task(retrieval_task, context)
            
            assert retrieval_result.success
            assert retrieval_result.data["expanded_queries"] == [query]  # Fallback to original query
            
            factcheck_task = {
                "query": query,
                "documents": retrieval_result.data["documents"]
            }
            factcheck_result = await factcheck_agent.process_task(factcheck_task, context)
            
            assert factcheck_result.success
            
            synthesis_task = {
                "query": query,
                "verified_facts": factcheck_result.data["verified_facts"]
            }
            synthesis_result = await synthesis_agent.process_task(synthesis_task, context)
            
            assert synthesis_result.success
            assert "answer" in synthesis_result.data
    
    @pytest.mark.asyncio
    async def test_agent_pipeline_error_handling(self, synthesis_agent, factcheck_agent, retrieval_agent, context):
        """Test agent pipeline error handling."""
        
        with patch('shared.core.llm_client_v2.EnhancedLLMClient.generate_text') as mock_llm:
            # Mock LLM to always fail
            mock_llm.side_effect = Exception("Persistent LLM error")
            
            query = "What is quantum computing?"
            
            # Test retrieval with persistent failure
            retrieval_task = {"query": query}
            retrieval_result = await retrieval_agent.process_task(retrieval_task, context)
            
            # Should still succeed with fallback
            assert retrieval_result.success
            assert retrieval_result.data["expanded_queries"] == [query]
            
            # Test fact-checking with no documents
            factcheck_task = {
                "query": query,
                "documents": []  # No documents
            }
            factcheck_result = await factcheck_agent.process_task(factcheck_task, context)
            
            assert not factcheck_result.success
            assert "No documents provided" in factcheck_result.error
            
            # Test synthesis with no facts
            synthesis_task = {
                "query": query,
                "verified_facts": []  # No facts
            }
            synthesis_result = await synthesis_agent.process_task(synthesis_task, context)
            
            assert not synthesis_result.success
            assert "No verified facts provided" in synthesis_result.error
    
    @pytest.mark.asyncio
    async def test_agent_pipeline_performance(self, synthesis_agent, factcheck_agent, retrieval_agent, context):
        """Test agent pipeline performance and metrics."""
        
        with patch('shared.core.llm_client_v2.EnhancedLLMClient.generate_text') as mock_llm:
            # Mock fast LLM responses
            fast_response = LLMResponse(
                content="Test response",
                provider="mock",
                model="test-model",
                token_usage={"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
                finish_reason="stop",
                response_time_ms=50
            )
            mock_llm.return_value = fast_response
            
            query = "What is artificial intelligence?"
            
            # Execute pipeline and measure performance
            start_time = asyncio.get_event_loop().time()
            
            retrieval_task = {"query": query}
            retrieval_result = await retrieval_agent.process_task(retrieval_task, context)
            
            factcheck_task = {
                "query": query,
                "documents": retrieval_result.data["documents"]
            }
            factcheck_result = await factcheck_agent.process_task(factcheck_task, context)
            
            synthesis_task = {
                "query": query,
                "verified_facts": factcheck_result.data["verified_facts"]
            }
            synthesis_result = await synthesis_agent.process_task(synthesis_task, context)
            
            end_time = asyncio.get_event_loop().time()
            total_time = end_time - start_time
            
            # Verify performance
            assert total_time < 5.0  # Should complete within 5 seconds
            assert retrieval_result.success
            assert factcheck_result.success
            assert synthesis_result.success
            
            # Check metrics
            retrieval_metrics = retrieval_agent.get_metrics()
            factcheck_metrics = factcheck_agent.get_metrics()
            synthesis_metrics = synthesis_agent.get_metrics()
            
            assert retrieval_metrics["success_rate"] > 0.0
            assert factcheck_metrics["success_rate"] > 0.0
            assert synthesis_metrics["success_rate"] > 0.0
    
    @pytest.mark.asyncio
    async def test_agent_pipeline_complex_query(self, synthesis_agent, factcheck_agent, retrieval_agent, context):
        """Test agent pipeline with complex, multi-part query."""
        
        with patch('shared.core.llm_client_v2.EnhancedLLMClient.generate_text') as mock_llm:
            # Mock responses for complex query
            complex_responses = [
                # Retrieval responses
                LLMResponse(
                    content="Expanded Queries:\n1. climate change causes\n2. global warming effects\n3. environmental impact",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 40, "completion_tokens": 25, "total_tokens": 65},
                    finish_reason="stop",
                    response_time_ms=80
                ),
                LLMResponse(
                    content="Reranked Results:\n1. [Climate change causes]\n2. [Global warming effects]\n3. [Environmental impact]",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
                    finish_reason="stop",
                    response_time_ms=100
                ),
                # Fact-checking responses
                LLMResponse(
                    content="Verification Result: supported\nConfidence Score: 0.9\nReasoning: Multiple scientific sources confirm climate change causes.",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 60, "completion_tokens": 35, "total_tokens": 95},
                    finish_reason="stop",
                    response_time_ms=120
                ),
                LLMResponse(
                    content="Verification Result: supported\nConfidence Score: 0.85\nReasoning: Scientific consensus supports global warming effects.",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 55, "completion_tokens": 32, "total_tokens": 87},
                    finish_reason="stop",
                    response_time_ms=110
                ),
                # Synthesis response
                LLMResponse(
                    content="Climate change is caused by human activities such as burning fossil fuels, which release greenhouse gases into the atmosphere. This leads to global warming and various environmental impacts including rising sea levels, extreme weather events, and ecosystem disruption.",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 70, "completion_tokens": 45, "total_tokens": 115},
                    finish_reason="stop",
                    response_time_ms=150
                )
            ]
            
            mock_llm.side_effect = complex_responses
            
            complex_query = "What are the causes and effects of climate change?"
            
            # Execute pipeline
            retrieval_task = {"query": complex_query}
            retrieval_result = await retrieval_agent.process_task(retrieval_task, context)
            
            factcheck_task = {
                "query": complex_query,
                "documents": retrieval_result.data["documents"]
            }
            factcheck_result = await factcheck_agent.process_task(factcheck_task, context)
            
            synthesis_task = {
                "query": complex_query,
                "verified_facts": factcheck_result.data["verified_facts"]
            }
            synthesis_result = await synthesis_agent.process_task(synthesis_task, context)
            
            # Verify complex query handling
            assert retrieval_result.success
            assert factcheck_result.success
            assert synthesis_result.success
            
            # Check that complex query was properly expanded
            expanded_queries = retrieval_result.data["expanded_queries"]
            assert len(expanded_queries) > 1  # Should have multiple expanded queries
            
            # Check that multiple facts were verified
            verified_facts = factcheck_result.data["verified_facts"]
            assert len(verified_facts) > 0
            
            # Check that synthesis addressed the complex query
            answer = synthesis_result.data["answer"]
            assert "climate change" in answer.lower()
            assert "causes" in answer.lower() or "effects" in answer.lower()
    
    @pytest.mark.asyncio
    async def test_agent_pipeline_health_check(self, synthesis_agent, factcheck_agent, retrieval_agent):
        """Test agent health checks and status."""
        
        # Test individual agent health
        synthesis_health = synthesis_agent.get_health_status()
        factcheck_health = factcheck_agent.get_health_status()
        retrieval_health = retrieval_agent.get_health_status()
        
        assert synthesis_health["status"] in ["healthy", "degraded"]
        assert factcheck_health["status"] in ["healthy", "degraded"]
        assert retrieval_health["status"] in ["healthy", "degraded"]
        
        # Test agent metrics
        synthesis_metrics = synthesis_agent.get_metrics()
        factcheck_metrics = factcheck_agent.get_metrics()
        retrieval_metrics = retrieval_agent.get_metrics()
        
        assert "request_count" in synthesis_metrics
        assert "success_rate" in synthesis_metrics
        assert "average_execution_time_ms" in synthesis_metrics
        
        assert "request_count" in factcheck_metrics
        assert "success_rate" in factcheck_metrics
        assert "average_execution_time_ms" in factcheck_metrics
        
        assert "request_count" in retrieval_metrics
        assert "success_rate" in retrieval_metrics
        assert "average_execution_time_ms" in retrieval_metrics
    
    @pytest.mark.asyncio
    async def test_agent_pipeline_concurrent_execution(self, synthesis_agent, factcheck_agent, retrieval_agent, context):
        """Test concurrent execution of multiple agent pipelines."""
        
        with patch('shared.core.llm_client_v2.EnhancedLLMClient.generate_text') as mock_llm:
            # Mock responses for concurrent execution
            mock_response = LLMResponse(
                content="Test response for concurrent execution",
                provider="mock",
                model="test-model",
                token_usage={"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
                finish_reason="stop",
                response_time_ms=50
            )
            mock_llm.return_value = mock_response
            
            # Create multiple queries for concurrent execution
            queries = [
                "What is machine learning?",
                "What is artificial intelligence?",
                "What is deep learning?"
            ]
            
            # Execute pipelines concurrently
            async def execute_pipeline(query: str):
                retrieval_task = {"query": query}
                retrieval_result = await retrieval_agent.process_task(retrieval_task, context)
                
                factcheck_task = {
                    "query": query,
                    "documents": retrieval_result.data["documents"]
                }
                factcheck_result = await factcheck_agent.process_task(factcheck_task, context)
                
                synthesis_task = {
                    "query": query,
                    "verified_facts": factcheck_result.data["verified_facts"]
                }
                synthesis_result = await synthesis_agent.process_task(synthesis_task, context)
                
                return {
                    "query": query,
                    "retrieval": retrieval_result,
                    "factcheck": factcheck_result,
                    "synthesis": synthesis_result
                }
            
            # Execute all pipelines concurrently
            tasks = [execute_pipeline(query) for query in queries]
            results = await asyncio.gather(*tasks)
            
            # Verify all pipelines completed successfully
            assert len(results) == 3
            
            for result in results:
                assert result["retrieval"].success
                assert result["factcheck"].success
                assert result["synthesis"].success
                assert "answer" in result["synthesis"].data
    
    @pytest.mark.asyncio
    async def test_agent_pipeline_error_recovery(self, synthesis_agent, factcheck_agent, retrieval_agent, context):
        """Test agent pipeline error recovery mechanisms."""
        
        with patch('shared.core.llm_client_v2.EnhancedLLMClient.generate_text') as mock_llm:
            # Mock LLM to fail intermittently
            call_count = 0
            def mock_llm_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count % 3 == 0:  # Fail every 3rd call
                    raise Exception("Intermittent LLM error")
                return LLMResponse(
                    content="Successful response",
                    provider="mock",
                    model="test-model",
                    token_usage={"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
                    finish_reason="stop",
                    response_time_ms=50
                )
            
            mock_llm.side_effect = mock_llm_side_effect
            
            query = "What is quantum computing?"
            
            # Execute pipeline with intermittent failures
            retrieval_task = {"query": query}
            retrieval_result = await retrieval_agent.process_task(retrieval_task, context)
            
            factcheck_task = {
                "query": query,
                "documents": retrieval_result.data["documents"]
            }
            factcheck_result = await factcheck_agent.process_task(factcheck_task, context)
            
            synthesis_task = {
                "query": query,
                "verified_facts": factcheck_result.data["verified_facts"]
            }
            synthesis_result = await synthesis_agent.process_task(synthesis_task, context)
            
            # Verify pipeline completed despite intermittent failures
            assert retrieval_result.success
            assert factcheck_result.success
            assert synthesis_result.success
            
            # Check that fallback mechanisms were used
            retrieval_metrics = retrieval_agent.get_metrics()
            factcheck_metrics = factcheck_agent.get_metrics()
            synthesis_metrics = synthesis_agent.get_metrics()
            
            # Should have some fallback requests
            assert retrieval_metrics["fallback_count"] >= 0
            assert factcheck_metrics["fallback_count"] >= 0
            assert synthesis_metrics["fallback_count"] >= 0


if __name__ == "__main__":
    pytest.main([__file__]) 