"""
Unit Tests for Agent Pattern Architecture
Tests the strategy/factory pattern implementation for agents.

Authors:
- Universal Knowledge Platform Engineering Team
    
Version:
    2.0.0 (2024-12-28)
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from shared.core.agent_pattern import (
    AgentFactory,
    SynthesisStrategy,
    FactCheckStrategy,
    RetrievalStrategy,
    StrategyBasedAgent,
    BaseAgentStrategy
)
from shared.core.base_agent import AgentType, QueryContext, AgentResult
from shared.core.llm_client_v2 import LLMResponse, LLMRequest


class TestAgentFactory:
    """Test agent factory functionality."""
    
    def test_agent_factory_creation(self):
        """Test agent factory creates agents correctly."""
        # Test synthesis agent creation
        synthesis_agent = AgentFactory.create_agent(AgentType.SYNTHESIS)
        assert synthesis_agent.agent_type == AgentType.SYNTHESIS
        assert synthesis_agent.agent_id == "synthesis_agent"
        assert isinstance(synthesis_agent, StrategyBasedAgent)
        
        # Test fact-checking agent creation
        factcheck_agent = AgentFactory.create_agent(AgentType.FACT_CHECK)
        assert factcheck_agent.agent_type == AgentType.FACT_CHECK
        assert factcheck_agent.agent_id == "factcheck_agent"
        assert isinstance(factcheck_agent, StrategyBasedAgent)
        
        # Test retrieval agent creation
        retrieval_agent = AgentFactory.create_agent(AgentType.RETRIEVAL)
        assert retrieval_agent.agent_type == AgentType.RETRIEVAL
        assert retrieval_agent.agent_id == "retrieval_agent"
        assert isinstance(retrieval_agent, StrategyBasedAgent)
    
    def test_agent_factory_unsupported_type(self):
        """Test factory handles unsupported agent types."""
        with pytest.raises(ValueError, match="Unsupported agent type"):
            AgentFactory.create_agent("unsupported_type")
    
    def test_agent_factory_list_supported_types(self):
        """Test factory lists supported agent types."""
        supported_types = AgentFactory.list_supported_types()
        assert AgentType.SYNTHESIS in supported_types
        assert AgentType.FACT_CHECK in supported_types
        assert AgentType.RETRIEVAL in supported_types
    
    def test_agent_factory_register_strategy(self):
        """Test registering new strategies."""
        # Create a mock strategy
        class MockStrategy(BaseAgentStrategy):
            def get_strategy_name(self) -> str:
                return "mock"
            
            async def _execute_strategy(self, task: Dict[str, Any], context: QueryContext) -> AgentResult:
                return AgentResult(success=True, data={"mock": True})
        
        # Register the strategy
        AgentFactory.register_strategy(AgentType.CITATION, MockStrategy)
        
        # Test that the strategy is registered
        agent = AgentFactory.create_agent(AgentType.CITATION)
        assert agent.agent_type == AgentType.CITATION


class TestSynthesisStrategy:
    """Test synthesis strategy functionality."""
    
    @pytest.fixture
    def synthesis_strategy(self):
        """Create synthesis strategy for testing."""
        return SynthesisStrategy()
    
    @pytest.fixture
    def valid_task(self):
        """Create valid task for synthesis."""
        return {
            "verified_facts": [
                {
                    "claim": "Earth is round",
                    "confidence": 0.9,
                    "source": "science"
                },
                {
                    "claim": "Water boils at 100°C at sea level",
                    "confidence": 0.8,
                    "source": "chemistry"
                },
                {
                    "claim": "The sun is a star",
                    "confidence": 0.95,
                    "source": "astronomy"
                }
            ],
            "query": "What are some basic scientific facts?"
        }
    
    @pytest.fixture
    def context(self):
        """Create query context."""
        return QueryContext(query="test")
    
    @pytest.mark.asyncio
    async def test_synthesis_strategy_execution(self, synthesis_strategy, valid_task, context):
        """Test synthesis strategy execution with valid data."""
        with patch.object(synthesis_strategy, '_call_llm') as mock_llm:
            # Mock LLM response
            mock_response = LLMResponse(
                content="Based on verified facts: Earth is round, water boils at 100°C, and the sun is a star.",
                provider="mock",
                model="test-model",
                token_usage={"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
                finish_reason="stop",
                response_time_ms=100
            )
            mock_llm.return_value = mock_response
            
            # Execute strategy
            result = await synthesis_strategy.execute(valid_task, context)
            
            # Verify result
            assert result.success
            assert "answer" in result.data
            assert result.confidence > 0.0
            assert result.data["synthesis_method"] == "llm_based"
            assert result.data["fact_count"] == 3
            
            # Verify LLM was called
            mock_llm.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_synthesis_strategy_no_facts(self, synthesis_strategy, context):
        """Test synthesis strategy with no facts."""
        task = {"verified_facts": [], "query": "test"}
        
        result = await synthesis_strategy.execute(task, context)
        
        assert not result.success
        assert "No verified facts provided" in result.error
        assert result.confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_synthesis_strategy_llm_failure_fallback(self, synthesis_strategy, valid_task, context):
        """Test synthesis strategy fallback when LLM fails."""
        with patch.object(synthesis_strategy, '_call_llm') as mock_llm:
            # Mock LLM failure
            mock_llm.side_effect = Exception("LLM error")
            
            # Execute strategy
            result = await synthesis_strategy.execute(valid_task, context)
            
            # Verify fallback was used
            assert result.success
            assert result.data["synthesis_method"] == "rule_based"
            assert "Based on verified facts" in result.data["answer"]
    
    def test_synthesis_strategy_format_facts(self, synthesis_strategy):
        """Test fact formatting functionality."""
        facts = [
            {"claim": "Test claim 1", "confidence": 0.8, "source": "test1"},
            {"claim": "Test claim 2", "confidence": 0.9, "source": "test2"}
        ]
        
        formatted = synthesis_strategy._format_facts(facts)
        
        assert "Test claim 1" in formatted
        assert "Test claim 2" in formatted
        assert "0.80" in formatted
        assert "0.90" in formatted
        assert "test1" in formatted
        assert "test2" in formatted
    
    def test_synthesis_strategy_calculate_confidence(self, synthesis_strategy):
        """Test confidence calculation."""
        facts = [
            {"confidence": 0.8},
            {"confidence": 0.9},
            {"confidence": 0.7}
        ]
        
        confidence = synthesis_strategy._calculate_synthesis_confidence(facts)
        
        # Expected: (0.8 + 0.9 + 0.7) / 3 * (3/5) = 0.8 * 0.6 = 0.48
        assert 0.4 < confidence < 0.5
    
    def test_synthesis_strategy_fallback_synthesis(self, synthesis_strategy):
        """Test fallback synthesis functionality."""
        facts = [
            {"claim": "High confidence fact", "confidence": 0.9},
            {"claim": "Low confidence fact", "confidence": 0.3}
        ]
        
        result = synthesis_strategy._fallback_synthesis(facts, "test query")
        
        assert result.success
        assert result.data["synthesis_method"] == "rule_based"
        assert "High confidence fact" in result.data["answer"]
        assert "Low confidence fact" not in result.data["answer"]  # Should be filtered out


class TestFactCheckStrategy:
    """Test fact-checking strategy functionality."""
    
    @pytest.fixture
    def factcheck_strategy(self):
        """Create fact-checking strategy for testing."""
        return FactCheckStrategy()
    
    @pytest.fixture
    def valid_task(self):
        """Create valid task for fact-checking."""
        return {
            "documents": [
                {
                    "content": "The Earth is round and orbits the Sun. It has one natural satellite called the Moon."
                },
                {
                    "content": "Water boils at 100 degrees Celsius at sea level under normal atmospheric pressure."
                }
            ],
            "query": "Is the Earth round?"
        }
    
    @pytest.fixture
    def context(self):
        """Create query context."""
        return QueryContext(query="test")
    
    @pytest.mark.asyncio
    async def test_factcheck_strategy_execution(self, factcheck_strategy, valid_task, context):
        """Test fact-checking strategy execution with valid data."""
        with patch.object(factcheck_strategy, '_call_llm') as mock_llm:
            # Mock LLM response for verification
            mock_response = LLMResponse(
                content="Verification Result: supported\nConfidence Score: 0.9\nReasoning: The claim is supported by multiple sources.",
                provider="mock",
                model="test-model",
                token_usage={"prompt_tokens": 40, "completion_tokens": 25, "total_tokens": 65},
                finish_reason="stop",
                response_time_ms=80
            )
            mock_llm.return_value = mock_response
            
            # Execute strategy
            result = await factcheck_strategy.execute(valid_task, context)
            
            # Verify result
            assert result.success
            assert "verified_facts" in result.data
            assert result.data["total_claims"] > 0
            assert result.confidence > 0.0
    
    @pytest.mark.asyncio
    async def test_factcheck_strategy_no_documents(self, factcheck_strategy, context):
        """Test fact-checking strategy with no documents."""
        task = {"documents": [], "query": "test"}
        
        result = await factcheck_strategy.execute(task, context)
        
        assert not result.success
        assert "No documents provided" in result.error
        assert result.confidence == 0.0
    
    def test_factcheck_strategy_extract_claims_from_text(self, factcheck_strategy):
        """Test claim extraction from text."""
        text = "The Earth is round. The sky is blue. What do you think about this?"
        
        claims = factcheck_strategy._extract_claims_from_text(text)
        
        # Should extract factual statements, not questions or opinions
        assert "The Earth is round" in claims
        assert "The sky is blue" in claims
        assert "What do you think about this" not in claims  # Question
    
    def test_factcheck_strategy_is_factual_statement(self, factcheck_strategy):
        """Test factual statement detection."""
        # Factual statements
        assert factcheck_strategy._is_factual_statement("The Earth is round")
        assert factcheck_strategy._is_factual_statement("Water boils at 100 degrees")
        assert factcheck_strategy._is_factual_statement("The population is 8 billion")
        
        # Non-factual statements
        assert not factcheck_strategy._is_factual_statement("What is the capital?")  # Question
        assert not factcheck_strategy._is_factual_statement("I think it's good")  # Opinion
        assert not factcheck_strategy._is_factual_statement("This might be true")  # Uncertainty
    
    def test_factcheck_strategy_is_relevant_to_claim(self, factcheck_strategy):
        """Test relevance checking."""
        claim = "The Earth is round"
        
        # Relevant content
        assert factcheck_strategy._is_relevant_to_claim(claim, "The Earth is round and orbits the Sun")
        assert factcheck_strategy._is_relevant_to_claim(claim, "Planet Earth has a spherical shape")
        
        # Irrelevant content
        assert not factcheck_strategy._is_relevant_to_claim(claim, "The weather is sunny today")
        assert not factcheck_strategy._is_relevant_to_claim(claim, "Cats are domestic animals")
    
    def test_factcheck_strategy_parse_verification_response(self, factcheck_strategy):
        """Test verification response parsing."""
        response = """
        Verification Result: supported
        Confidence Score: 0.85
        Reasoning: The claim is supported by multiple sources.
        """
        
        result = factcheck_strategy._parse_verification_response(response)
        
        assert result["is_supported"] is True
        assert result["confidence"] == 0.85
        assert "supported by multiple sources" in result["reasoning"]
    
    def test_factcheck_strategy_fallback_verification(self, factcheck_strategy):
        """Test fallback verification."""
        claim = "The Earth is round"
        evidence = [
            "The Earth is round and orbits the Sun",
            "Planet Earth has a spherical shape",
            "The weather is sunny today"  # Irrelevant
        ]
        
        result = factcheck_strategy._fallback_verification(claim, evidence)
        
        assert result["claim"] == claim
        assert result["is_supported"] is True
        assert result["confidence"] > 0.0
        assert len(result["evidence"]) == 2  # Only relevant evidence
    
    def test_factcheck_strategy_filter_verified_facts(self, factcheck_strategy):
        """Test verified facts filtering."""
        verifications = [
            {"claim": "High confidence claim", "confidence": 0.9, "evidence": ["source1"]},
            {"claim": "Low confidence claim", "confidence": 0.5, "evidence": ["source2"]},
            {"claim": "Medium confidence claim", "confidence": 0.8, "evidence": ["source3"]}
        ]
        
        verified_facts = factcheck_strategy._filter_verified_facts(verifications)
        
        # Should only include facts with confidence >= 0.7
        assert len(verified_facts) == 2
        assert any(f["claim"] == "High confidence claim" for f in verified_facts)
        assert any(f["claim"] == "Medium confidence claim" for f in verified_facts)
        assert not any(f["claim"] == "Low confidence claim" for f in verified_facts)
    
    def test_factcheck_strategy_calculate_verification_confidence(self, factcheck_strategy):
        """Test verification confidence calculation."""
        verifications = [
            {"confidence": 0.8},
            {"confidence": 0.9},
            {"confidence": 0.7}
        ]
        
        confidence = factcheck_strategy._calculate_verification_confidence(verifications)
        
        # Expected: (0.8 + 0.9 + 0.7) / 3 = 0.8
        assert confidence == 0.8


class TestRetrievalStrategy:
    """Test retrieval strategy functionality."""
    
    @pytest.fixture
    def retrieval_strategy(self):
        """Create retrieval strategy for testing."""
        return RetrievalStrategy()
    
    @pytest.fixture
    def valid_task(self):
        """Create valid task for retrieval."""
        return {
            "query": "What is machine learning?"
        }
    
    @pytest.fixture
    def context(self):
        """Create query context."""
        return QueryContext(query="test")
    
    @pytest.mark.asyncio
    async def test_retrieval_strategy_execution(self, retrieval_strategy, valid_task, context):
        """Test retrieval strategy execution with valid data."""
        with patch.object(retrieval_strategy, '_call_llm') as mock_llm:
            # Mock LLM response for query expansion
            mock_expansion_response = LLMResponse(
                content="Expanded Queries:\n1. machine learning algorithms\n2. artificial intelligence\n3. deep learning",
                provider="mock",
                model="test-model",
                token_usage={"prompt_tokens": 30, "completion_tokens": 20, "total_tokens": 50},
                finish_reason="stop",
                response_time_ms=60
            )
            
            # Mock LLM response for ranking
            mock_ranking_response = LLMResponse(
                content="Reranked Results:\n1. [result 1]\n2. [result 2]",
                provider="mock",
                model="test-model",
                token_usage={"prompt_tokens": 40, "completion_tokens": 25, "total_tokens": 65},
                finish_reason="stop",
                response_time_ms=80
            )
            
            mock_llm.side_effect = [mock_expansion_response, mock_ranking_response]
            
            # Execute strategy
            result = await retrieval_strategy.execute(valid_task, context)
            
            # Verify result
            assert result.success
            assert "documents" in result.data
            assert "expanded_queries" in result.data
            assert result.confidence > 0.0
    
    @pytest.mark.asyncio
    async def test_retrieval_strategy_no_query(self, retrieval_strategy, context):
        """Test retrieval strategy with no query."""
        task = {"query": ""}
        
        result = await retrieval_strategy.execute(task, context)
        
        assert not result.success
        assert "No query provided" in result.error
        assert result.confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_retrieval_strategy_query_expansion_failure(self, retrieval_strategy, valid_task, context):
        """Test retrieval strategy when query expansion fails."""
        with patch.object(retrieval_strategy, '_call_llm') as mock_llm:
            # Mock LLM failure
            mock_llm.side_effect = Exception("LLM error")
            
            # Execute strategy
            result = await retrieval_strategy.execute(valid_task, context)
            
            # Should still succeed with fallback
            assert result.success
            assert result.data["expanded_queries"] == ["What is machine learning?"]  # Original query only
    
    def test_retrieval_strategy_parse_expanded_queries(self, retrieval_strategy):
        """Test expanded query parsing."""
        response = """
        Expanded Queries:
        1. machine learning algorithms
        2. artificial intelligence
        3. deep learning
        4. neural networks
        5. supervised learning
        """
        
        queries = retrieval_strategy._parse_expanded_queries(response)
        
        assert "machine learning algorithms" in queries
        assert "artificial intelligence" in queries
        assert "deep learning" in queries
        assert len(queries) <= 5  # Should be limited to 5
    
    def test_retrieval_strategy_deduplicate_results(self, retrieval_strategy):
        """Test result deduplication."""
        results = [
            {"content": "Document 1", "score": 0.9},
            {"content": "Document 2", "score": 0.8},
            {"content": "Document 1", "score": 0.7},  # Duplicate
            {"content": "Document 3", "score": 0.6}
        ]
        
        unique_results = retrieval_strategy._deduplicate_results(results)
        
        assert len(unique_results) == 3  # Should remove duplicate
        assert unique_results[0]["content"] == "Document 1"
        assert unique_results[1]["content"] == "Document 2"
        assert unique_results[2]["content"] == "Document 3"
    
    def test_retrieval_strategy_format_results_for_ranking(self, retrieval_strategy):
        """Test result formatting for ranking."""
        results = [
            {"content": "Test document 1", "score": 0.9, "source": "source1"},
            {"content": "Test document 2", "score": 0.8, "source": "source2"}
        ]
        
        formatted = retrieval_strategy._format_results_for_ranking(results)
        
        assert "Test document 1" in formatted
        assert "Test document 2" in formatted
        assert "0.90" in formatted
        assert "0.80" in formatted
        assert "source1" in formatted
        assert "source2" in formatted
    
    def test_retrieval_strategy_parse_ranked_results(self, retrieval_strategy):
        """Test ranked result parsing."""
        response = """
        Reranked Results:
        1. [result 1]
        2. [result 2]
        """
        
        original_results = [
            {"content": "Result 1", "score": 0.9},
            {"content": "Result 2", "score": 0.8},
            {"content": "Result 3", "score": 0.7}
        ]
        
        ranked_results = retrieval_strategy._parse_ranked_results(response, original_results)
        
        # Should maintain order and include all results
        assert len(ranked_results) == 3
    
    def test_retrieval_strategy_calculate_retrieval_confidence(self, retrieval_strategy):
        """Test retrieval confidence calculation."""
        results = [
            {"score": 0.9},
            {"score": 0.8},
            {"score": 0.7}
        ]
        
        confidence = retrieval_strategy._calculate_retrieval_confidence(results)
        
        # Expected: (0.9 + 0.8 + 0.7) / 3 * (3/10) = 0.8 * 0.3 = 0.24
        assert 0.2 < confidence < 0.3


class TestStrategyBasedAgent:
    """Test strategy-based agent functionality."""
    
    def test_strategy_based_agent_creation(self):
        """Test strategy-based agent creation."""
        strategy = SynthesisStrategy()
        agent = StrategyBasedAgent("test_agent", AgentType.SYNTHESIS, strategy)
        
        assert agent.agent_id == "test_agent"
        assert agent.agent_type == AgentType.SYNTHESIS
        assert agent.strategy == strategy
    
    @pytest.mark.asyncio
    async def test_strategy_based_agent_process_task(self):
        """Test strategy-based agent task processing."""
        strategy = SynthesisStrategy()
        agent = StrategyBasedAgent("test_agent", AgentType.SYNTHESIS, strategy)
        
        task = {"verified_facts": [{"claim": "test", "confidence": 0.8}], "query": "test"}
        context = QueryContext(query="test")
        
        with patch.object(strategy, 'execute') as mock_execute:
            mock_execute.return_value = AgentResult(success=True, data={"test": True})
            
            result = await agent.process_task(task, context)
            
            assert result.success
            assert result.data["test"] is True
            mock_execute.assert_called_once_with(task, context)
    
    def test_strategy_based_agent_metrics(self):
        """Test strategy-based agent metrics."""
        strategy = SynthesisStrategy()
        agent = StrategyBasedAgent("test_agent", AgentType.SYNTHESIS, strategy)
        
        metrics = agent.get_metrics()
        
        assert "agent_id" in metrics
        assert "agent_type" in metrics
        assert "strategy_metrics" in metrics
        assert metrics["agent_id"] == "test_agent"
        assert metrics["agent_type"] == AgentType.SYNTHESIS.value


if __name__ == "__main__":
    pytest.main([__file__]) 