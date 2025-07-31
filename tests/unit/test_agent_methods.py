"""
Comprehensive Agent Method Tests - MAANG Standards

This module provides comprehensive unit tests for all agent methods,
ensuring proper functionality, error handling, and performance compliance.

Test Coverage:
    - Synthesis Agent methods
    - Search/Retrieval Agent methods
    - FactCheck Agent methods
    - Agent Orchestration methods
    - Agent Communication patterns
    - Error handling and fallbacks
    - Performance optimization
    - Memory management
    - Concurrent processing

Authors:
    - Universal Knowledge Platform Engineering Team
    
Version:
    2.0.0 (2024-12-28)
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

# Import agent classes
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Add service paths
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'services', 'synthesis-service'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'services', 'search-service'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'services', 'factcheck-service'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'services', 'api-gateway'))
from synthesis_agent import SynthesisAgent
from citation_agent import CitationAgent
from retrieval_agent import RetrievalAgent
from factcheck_agent import FactCheckAgent
from lead_orchestrator import LeadOrchestrator
from shared.core.agent_pattern import AgentStrategy, AgentFactory, AgentType
from shared.core.llm_client_v3 import EnhancedLLMClient

class TestSynthesisAgent:
    """Test Synthesis Agent methods."""
    
    @pytest.fixture
    def synthesis_agent(self):
        """Create synthesis agent instance."""
        return SynthesisAgent()
    
    @pytest.fixture
    def sample_context(self):
        """Sample query context."""
        return {
            "query": "What is Python programming?",
            "user_id": "test_user",
            "session_id": "test_session",
            "preferences": {
                "detail_level": "comprehensive",
                "include_sources": True,
                "format": "markdown"
            }
        }
    
    @pytest.fixture
    def sample_facts(self):
        """Sample facts for synthesis."""
        return [
            {
                "content": "Python is a high-level programming language",
                "source": "python.org",
                "confidence": 0.95,
                "relevance": 0.9
            },
            {
                "content": "Python emphasizes code readability",
                "source": "wikipedia.org",
                "confidence": 0.92,
                "relevance": 0.85
            }
        ]
    
    @pytest.mark.asyncio
    async def test_synthesize_answer_success(self, synthesis_agent, sample_context, sample_facts):
        """Test successful answer synthesis."""
        with patch.object(synthesis_agent, '_call_llm') as mock_llm:
            mock_llm.return_value = {
                "content": "Python is a high-level programming language that emphasizes code readability...",
                "tokens_used": 150,
                "confidence": 0.95
            }
            
            result = await synthesis_agent.synthesize_answer(
                query=sample_context["query"],
                facts=sample_facts,
                context=sample_context
            )
            
            assert result["success"] is True
            assert "answer" in result["data"]
            assert "sources" in result["data"]
            assert "confidence" in result["data"]
    
    @pytest.mark.asyncio
    async def test_synthesize_answer_no_facts(self, synthesis_agent, sample_context):
        """Test synthesis with no facts provided."""
        result = await synthesis_agent.synthesize_answer(
            query=sample_context["query"],
            facts=[],
            context=sample_context
        )
        
        assert result["success"] is False
        assert "No facts provided" in result["error"]
    
    @pytest.mark.asyncio
    async def test_synthesize_answer_llm_error(self, synthesis_agent, sample_context, sample_facts):
        """Test synthesis with LLM error."""
        with patch.object(synthesis_agent, '_call_llm') as mock_llm:
            mock_llm.side_effect = Exception("LLM service unavailable")
            
            result = await synthesis_agent.synthesize_answer(
                query=sample_context["query"],
                facts=sample_facts,
                context=sample_context
            )
            
            assert result["success"] is False
            assert "LLM service unavailable" in result["error"]
    
    @pytest.mark.asyncio
    async def test_format_facts(self, synthesis_agent, sample_facts):
        """Test fact formatting."""
        formatted = synthesis_agent._format_facts(sample_facts)
        
        assert isinstance(formatted, str)
        assert "Python is a high-level programming language" in formatted
        assert "python.org" in formatted
    
    @pytest.mark.asyncio
    async def test_validate_synthesis_input(self, synthesis_agent):
        """Test synthesis input validation."""
        # Valid input
        assert synthesis_agent._validate_input("What is Python?", [{"content": "test"}]) is True
        
        # Invalid input - empty query
        assert synthesis_agent._validate_input("", [{"content": "test"}]) is False
        
        # Invalid input - no facts
        assert synthesis_agent._validate_input("What is Python?", []) is False
    
    @pytest.mark.asyncio
    async def test_synthesis_performance(self, synthesis_agent, sample_context, sample_facts):
        """Test synthesis performance."""
        import time
        
        start_time = time.time()
        
        with patch.object(synthesis_agent, '_call_llm') as mock_llm:
            mock_llm.return_value = {
                "content": "Synthesized answer...",
                "tokens_used": 100,
                "confidence": 0.9
            }
            
            result = await synthesis_agent.synthesize_answer(
                query=sample_context["query"],
                facts=sample_facts,
                context=sample_context
            )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert result["success"] is True
        assert processing_time < 5.0  # Should complete within 5 seconds

class TestCitationAgent:
    """Test Citation Agent methods."""
    
    @pytest.fixture
    def citation_agent(self):
        """Create citation agent instance."""
        return CitationAgent()
    
    @pytest.fixture
    def sample_content(self):
        """Sample content for citation."""
        return "Python is a programming language that was created by Guido van Rossum."
    
    @pytest.fixture
    def sample_sources(self):
        """Sample sources for citation."""
        return [
            {
                "url": "https://python.org",
                "title": "Python Programming Language",
                "author": "Python Software Foundation",
                "date": "2024-01-01"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_generate_citations_success(self, citation_agent, sample_content, sample_sources):
        """Test successful citation generation."""
        with patch.object(citation_agent, '_call_llm') as mock_llm:
            mock_llm.return_value = {
                "content": "Python is a programming language that was created by Guido van Rossum [1].",
                "citations": [
                    {
                        "text": "Python is a programming language",
                        "source_index": 0,
                        "confidence": 0.95
                    }
                ]
            }
            
            result = await citation_agent.generate_citations(
                content=sample_content,
                sources=sample_sources
            )
            
            assert result["success"] is True
            assert "cited_content" in result["data"]
            assert "citations" in result["data"]
    
    @pytest.mark.asyncio
    async def test_validate_sources(self, citation_agent, sample_sources):
        """Test source validation."""
        # Valid sources
        assert citation_agent._validate_sources(sample_sources) is True
        
        # Invalid sources - empty
        assert citation_agent._validate_sources([]) is False
        
        # Invalid sources - missing required fields
        invalid_sources = [{"url": "https://example.com"}]  # Missing title
        assert citation_agent._validate_sources(invalid_sources) is False
    
    @pytest.mark.asyncio
    async def test_format_citations(self, citation_agent, sample_sources):
        """Test citation formatting."""
        formatted = citation_agent._format_citations(sample_sources)
        
        assert isinstance(formatted, str)
        assert "python.org" in formatted
        assert "Python Software Foundation" in formatted

class TestRetrievalAgent:
    """Test Retrieval Agent methods."""
    
    @pytest.fixture
    def retrieval_agent(self):
        """Create retrieval agent instance."""
        return RetrievalAgent()
    
    @pytest.fixture
    def sample_query(self):
        """Sample query for retrieval."""
        return "What is Python programming language?"
    
    @pytest.mark.asyncio
    async def test_retrieve_documents_success(self, retrieval_agent, sample_query):
        """Test successful document retrieval."""
        with patch.object(retrieval_agent, '_vector_search') as mock_vector, \
             patch.object(retrieval_agent, '_keyword_search') as mock_keyword:
            
            mock_vector.return_value = [
                {"content": "Python is a programming language", "score": 0.95}
            ]
            mock_keyword.return_value = [
                {"content": "Python emphasizes readability", "score": 0.88}
            ]
            
            result = await retrieval_agent.retrieve_documents(
                query=sample_query,
                max_results=10
            )
            
            assert result["success"] is True
            assert "documents" in result["data"]
            assert len(result["data"]["documents"]) > 0
    
    @pytest.mark.asyncio
    async def test_hybrid_retrieve_success(self, retrieval_agent, sample_query):
        """Test hybrid retrieval (vector + keyword)."""
        with patch.object(retrieval_agent, '_vector_search') as mock_vector, \
             patch.object(retrieval_agent, '_keyword_search') as mock_keyword:
            
            mock_vector.return_value = [
                {"content": "Vector result", "score": 0.95}
            ]
            mock_keyword.return_value = [
                {"content": "Keyword result", "score": 0.88}
            ]
            
            result = await retrieval_agent.hybrid_retrieve(
                query=sample_query,
                max_results=10
            )
            
            assert result["success"] is True
            assert "documents" in result["data"]
            assert len(result["data"]["documents"]) > 0
    
    @pytest.mark.asyncio
    async def test_vector_search(self, retrieval_agent, sample_query):
        """Test vector search functionality."""
        with patch.object(retrieval_agent, '_get_embedding') as mock_embedding, \
             patch.object(retrieval_agent, '_search_vector_db') as mock_search:
            
            mock_embedding.return_value = [0.1, 0.2, 0.3]
            mock_search.return_value = [
                {"content": "Vector search result", "score": 0.95}
            ]
            
            results = await retrieval_agent._vector_search(sample_query, 5)
            
            assert len(results) > 0
            assert "content" in results[0]
            assert "score" in results[0]
    
    @pytest.mark.asyncio
    async def test_keyword_search(self, retrieval_agent, sample_query):
        """Test keyword search functionality."""
        with patch.object(retrieval_agent, '_search_elasticsearch') as mock_search:
            mock_search.return_value = [
                {"content": "Keyword search result", "score": 0.88}
            ]
            
            results = await retrieval_agent._keyword_search(sample_query, 5)
            
            assert len(results) > 0
            assert "content" in results[0]
            assert "score" in results[0]
    
    @pytest.mark.asyncio
    async def test_merge_results(self, retrieval_agent):
        """Test result merging and deduplication."""
        vector_results = [
            {"content": "Python is a language", "score": 0.95, "source": "doc1"}
        ]
        keyword_results = [
            {"content": "Python emphasizes readability", "score": 0.88, "source": "doc2"}
        ]
        
        merged = retrieval_agent._merge_results(vector_results, keyword_results)
        
        assert len(merged) > 0
        assert all("content" in doc for doc in merged)
        assert all("score" in doc for doc in merged)
    
    @pytest.mark.asyncio
    async def test_retrieval_error_handling(self, retrieval_agent, sample_query):
        """Test retrieval error handling."""
        with patch.object(retrieval_agent, '_vector_search') as mock_vector:
            mock_vector.side_effect = Exception("Vector search failed")
            
            result = await retrieval_agent.retrieve_documents(
                query=sample_query,
                max_results=10
            )
            
            assert result["success"] is False
            assert "Vector search failed" in result["error"]

class TestFactCheckAgent:
    """Test FactCheck Agent methods."""
    
    @pytest.fixture
    def factcheck_agent(self):
        """Create factcheck agent instance."""
        return FactCheckAgent()
    
    @pytest.fixture
    def sample_claim(self):
        """Sample claim for fact checking."""
        return "Python was created by Guido van Rossum in 1991"
    
    @pytest.fixture
    def sample_sources(self):
        """Sample sources for fact checking."""
        return [
            {
                "content": "Python was created by Guido van Rossum",
                "source": "python.org",
                "date": "2024-01-01"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_verify_claim_success(self, factcheck_agent, sample_claim, sample_sources):
        """Test successful claim verification."""
        with patch.object(factcheck_agent, '_call_llm') as mock_llm:
            mock_llm.return_value = {
                "content": "SUPPORTED: The claim is verified by multiple sources",
                "confidence": 0.95,
                "reasoning": "Python.org confirms Guido van Rossum created Python"
            }
            
            result = await factcheck_agent.verify_claim(
                claim=sample_claim,
                sources=sample_sources
            )
            
            assert result["success"] is True
            assert "verdict" in result["data"]
            assert "confidence" in result["data"]
            assert "reasoning" in result["data"]
    
    @pytest.mark.asyncio
    async def test_verify_claim_contradicted(self, factcheck_agent, sample_claim, sample_sources):
        """Test claim verification with contradiction."""
        with patch.object(factcheck_agent, '_call_llm') as mock_llm:
            mock_llm.return_value = {
                "content": "CONTRADICTED: The claim is contradicted by sources",
                "confidence": 0.85,
                "reasoning": "Sources indicate different creator"
            }
            
            result = await factcheck_agent.verify_claim(
                claim=sample_claim,
                sources=sample_sources
            )
            
            assert result["success"] is True
            assert result["data"]["verdict"] == "CONTRADICTED"
    
    @pytest.mark.asyncio
    async def test_verify_claim_unclear(self, factcheck_agent, sample_claim, sample_sources):
        """Test claim verification with unclear result."""
        with patch.object(factcheck_agent, '_call_llm') as mock_llm:
            mock_llm.return_value = {
                "content": "UNCLEAR: Insufficient evidence to verify claim",
                "confidence": 0.3,
                "reasoning": "Sources are ambiguous or conflicting"
            }
            
            result = await factcheck_agent.verify_claim(
                claim=sample_claim,
                sources=sample_sources
            )
            
            assert result["success"] is True
            assert result["data"]["verdict"] == "UNCLEAR"
    
    @pytest.mark.asyncio
    async def test_validate_claim_input(self, factcheck_agent):
        """Test claim input validation."""
        # Valid input
        assert factcheck_agent._validate_input("Valid claim", [{"content": "source"}]) is True
        
        # Invalid input - empty claim
        assert factcheck_agent._validate_input("", [{"content": "source"}]) is False
        
        # Invalid input - no sources
        assert factcheck_agent._validate_input("Valid claim", []) is False
    
    @pytest.mark.asyncio
    async def test_parse_verdict(self, factcheck_agent):
        """Test verdict parsing."""
        # Test supported verdict
        result = factcheck_agent._parse_verdict("SUPPORTED: This is true")
        assert result["verdict"] == "SUPPORTED"
        assert "This is true" in result["reasoning"]
        
        # Test contradicted verdict
        result = factcheck_agent._parse_verdict("CONTRADICTED: This is false")
        assert result["verdict"] == "CONTRADICTED"
        
        # Test unclear verdict
        result = factcheck_agent._parse_verdict("UNCLEAR: Insufficient evidence")
        assert result["verdict"] == "UNCLEAR"

class TestLeadOrchestrator:
    """Test Lead Orchestrator methods."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return LeadOrchestrator()
    
    @pytest.fixture
    def sample_query(self):
        """Sample query for orchestration."""
        return "What is Python programming language?"
    
    @pytest.mark.asyncio
    async def test_process_query_success(self, orchestrator, sample_query):
        """Test successful query processing."""
        with patch.object(orchestrator, '_retrieve_documents') as mock_retrieve, \
             patch.object(orchestrator, '_fact_check') as mock_factcheck, \
             patch.object(orchestrator, '_synthesize_answer') as mock_synthesize:
            
            mock_retrieve.return_value = {
                "success": True,
                "data": {"documents": [{"content": "Python is a language"}]}
            }
            mock_factcheck.return_value = {
                "success": True,
                "data": {"verified_facts": [{"content": "Python is a language", "verdict": "SUPPORTED"}]}
            }
            mock_synthesize.return_value = {
                "success": True,
                "data": {"answer": "Python is a programming language..."}
            }
            
            result = await orchestrator.process_query(sample_query)
            
            assert result["success"] is True
            assert "answer" in result["data"]
            assert "sources" in result["data"]
    
    @pytest.mark.asyncio
    async def test_process_query_retrieval_failure(self, orchestrator, sample_query):
        """Test query processing with retrieval failure."""
        with patch.object(orchestrator, '_retrieve_documents') as mock_retrieve:
            mock_retrieve.return_value = {
                "success": False,
                "error": "Retrieval failed"
            }
            
            result = await orchestrator.process_query(sample_query)
            
            assert result["success"] is False
            assert "Retrieval failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_orchestrate_agents(self, orchestrator):
        """Test agent orchestration."""
        agents = {
            "retrieval": Mock(),
            "factcheck": Mock(),
            "synthesis": Mock()
        }
        
        with patch.object(orchestrator, '_create_agents', return_value=agents):
            result = await orchestrator._orchestrate_agents("test query")
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_parallel_processing(self, orchestrator):
        """Test parallel agent processing."""
        tasks = [
            {"agent": "retrieval", "data": "query"},
            {"agent": "factcheck", "data": "facts"},
            {"agent": "synthesis", "data": "content"}
        ]
        
        with patch.object(orchestrator, '_execute_agent_task') as mock_execute:
            mock_execute.return_value = {"success": True, "data": {}}
            
            results = await orchestrator._process_parallel(tasks)
            
            assert len(results) == len(tasks)
            assert all(result["success"] for result in results)
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, orchestrator):
        """Test error recovery mechanisms."""
        with patch.object(orchestrator, '_retrieve_documents') as mock_retrieve:
            # First call fails, second succeeds
            mock_retrieve.side_effect = [
                {"success": False, "error": "Primary failed"},
                {"success": True, "data": {"documents": []}}
            ]
            
            result = await orchestrator._retrieve_with_fallback("test query")
            
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, orchestrator, sample_query):
        """Test performance monitoring."""
        import time
        
        start_time = time.time()
        
        with patch.object(orchestrator, '_retrieve_documents') as mock_retrieve, \
             patch.object(orchestrator, '_fact_check') as mock_factcheck, \
             patch.object(orchestrator, '_synthesize_answer') as mock_synthesize:
            
            mock_retrieve.return_value = {"success": True, "data": {"documents": []}}
            mock_factcheck.return_value = {"success": True, "data": {"verified_facts": []}}
            mock_synthesize.return_value = {"success": True, "data": {"answer": "test"}}
            
            result = await orchestrator.process_query(sample_query)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert result["success"] is True
        assert processing_time < 10.0  # Should complete within 10 seconds

class TestAgentFactory:
    """Test Agent Factory methods."""
    
    @pytest.fixture
    def agent_factory(self):
        """Create agent factory instance."""
        return AgentFactory()
    
    def test_create_synthesis_agent(self, agent_factory):
        """Test synthesis agent creation."""
        agent = agent_factory.create_agent(AgentType.SYNTHESIS)
        
        assert agent is not None
        assert isinstance(agent, SynthesisAgent)
    
    def test_create_retrieval_agent(self, agent_factory):
        """Test retrieval agent creation."""
        agent = agent_factory.create_agent(AgentType.RETRIEVAL)
        
        assert agent is not None
        assert isinstance(agent, RetrievalAgent)
    
    def test_create_factcheck_agent(self, agent_factory):
        """Test factcheck agent creation."""
        agent = agent_factory.create_agent(AgentType.FACT_CHECK)
        
        assert agent is not None
        assert isinstance(agent, FactCheckAgent)
    
    def test_create_invalid_agent_type(self, agent_factory):
        """Test invalid agent type handling."""
        with pytest.raises(ValueError):
            agent_factory.create_agent("INVALID_TYPE")

class TestAgentCommunication:
    """Test agent communication patterns."""
    
    @pytest.fixture
    def synthesis_agent(self):
        """Create synthesis agent."""
        return SynthesisAgent()
    
    @pytest.fixture
    def retrieval_agent(self):
        """Create retrieval agent."""
        return RetrievalAgent()
    
    @pytest.fixture
    def factcheck_agent(self):
        """Create factcheck agent."""
        return FactCheckAgent()
    
    @pytest.mark.asyncio
    async def test_agent_message_passing(self, synthesis_agent, retrieval_agent):
        """Test message passing between agents."""
        # Mock retrieval agent response
        with patch.object(retrieval_agent, 'retrieve_documents') as mock_retrieve:
            mock_retrieve.return_value = {
                "success": True,
                "data": {"documents": [{"content": "test document"}]}
            }
            
            # Get documents from retrieval agent
            retrieval_result = await retrieval_agent.retrieve_documents("test query")
            
            # Pass to synthesis agent
            with patch.object(synthesis_agent, 'synthesize_answer') as mock_synthesize:
                mock_synthesize.return_value = {
                    "success": True,
                    "data": {"answer": "synthesized answer"}
                }
                
                synthesis_result = await synthesis_agent.synthesize_answer(
                    query="test query",
                    facts=retrieval_result["data"]["documents"]
                )
                
                assert synthesis_result["success"] is True
                assert "answer" in synthesis_result["data"]
    
    @pytest.mark.asyncio
    async def test_agent_error_propagation(self, synthesis_agent, retrieval_agent):
        """Test error propagation between agents."""
        # Mock retrieval agent failure
        with patch.object(retrieval_agent, 'retrieve_documents') as mock_retrieve:
            mock_retrieve.return_value = {
                "success": False,
                "error": "Retrieval failed"
            }
            
            retrieval_result = await retrieval_agent.retrieve_documents("test query")
            
            # Synthesis agent should handle the error gracefully
            synthesis_result = await synthesis_agent.synthesize_answer(
                query="test query",
                facts=retrieval_result.get("data", {}).get("documents", [])
            )
            
            assert synthesis_result["success"] is False
            assert "No facts provided" in synthesis_result["error"]

class TestAgentPerformance:
    """Test agent performance characteristics."""
    
    @pytest.fixture
    def synthesis_agent(self):
        """Create synthesis agent."""
        return SynthesisAgent()
    
    @pytest.mark.asyncio
    async def test_memory_usage(self, synthesis_agent):
        """Test memory usage during processing."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform synthesis operation
        with patch.object(synthesis_agent, '_call_llm') as mock_llm:
            mock_llm.return_value = {
                "content": "Synthesized content...",
                "tokens_used": 100
            }
            
            await synthesis_agent.synthesize_answer(
                query="test query",
                facts=[{"content": "test fact"}]
            )
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 100MB)
        assert memory_increase < 100 * 1024 * 1024
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, synthesis_agent):
        """Test concurrent agent processing."""
        import asyncio
        
        async def process_query(query_id):
            with patch.object(synthesis_agent, '_call_llm') as mock_llm:
                mock_llm.return_value = {
                    "content": f"Synthesized content for query {query_id}",
                    "tokens_used": 100
                }
                
                return await synthesis_agent.synthesize_answer(
                    query=f"query {query_id}",
                    facts=[{"content": f"fact {query_id}"}]
                )
        
        # Process multiple queries concurrently
        tasks = [process_query(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(result["success"] for result in results)

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 