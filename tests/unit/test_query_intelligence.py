"""
Unit Tests for Query Intelligence Layer
Tests for intent classification, complexity scoring, domain detection, and caching.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from services.search_service.core.query_processor import (
    QueryIntelligenceLayer,
    IntentClassifier,
    ComplexityScorer,
    DomainDetector,
    QueryCache,
    ProcessedQuery,
    IntentType,
    ComplexityLevel,
    DomainType
)


class TestIntentClassifier:
    """Test intent classification functionality."""
    
    @pytest.fixture
    def classifier(self):
        return IntentClassifier()
    
    @pytest.mark.asyncio
    async def test_factual_intent_classification(self, classifier):
        """Test factual intent classification."""
        query = "What is Python?"
        intent = await classifier.classify(query)
        assert intent == IntentType.FACTUAL
    
    @pytest.mark.asyncio
    async def test_analytical_intent_classification(self, classifier):
        """Test analytical intent classification."""
        query = "Why does Python use indentation?"
        intent = await classifier.classify(query)
        assert intent == IntentType.ANALYTICAL
    
    @pytest.mark.asyncio
    async def test_how_to_intent_classification(self, classifier):
        """Test how-to intent classification."""
        query = "How to install Python?"
        intent = await classifier.classify(query)
        assert intent == IntentType.HOW_TO
    
    @pytest.mark.asyncio
    async def test_definition_intent_classification(self, classifier):
        """Test definition intent classification."""
        query = "What is the definition of AI?"
        intent = await classifier.classify(query)
        assert intent == IntentType.DEFINITION
    
    @pytest.mark.asyncio
    async def test_complex_query_intent(self, classifier):
        """Test complex query intent classification."""
        query = "Explain the relationship between machine learning and artificial intelligence in modern computing systems"
        intent = await classifier.classify(query)
        assert intent == IntentType.ANALYTICAL


class TestComplexityScorer:
    """Test complexity scoring functionality."""
    
    @pytest.fixture
    def scorer(self):
        return ComplexityScorer()
    
    @pytest.mark.asyncio
    async def test_simple_complexity_scoring(self, scorer):
        """Test simple query complexity scoring."""
        query = "What is Python?"
        complexity = await scorer.score(query)
        assert complexity == ComplexityLevel.SIMPLE
    
    @pytest.mark.asyncio
    async def test_moderate_complexity_scoring(self, scorer):
        """Test moderate query complexity scoring."""
        query = "How does Python handle memory management?"
        complexity = await scorer.score(query)
        assert complexity == ComplexityLevel.MODERATE
    
    @pytest.mark.asyncio
    async def test_complex_complexity_scoring(self, scorer):
        """Test complex query complexity scoring."""
        query = "Explain the relationship between Python's garbage collection algorithm and memory optimization in distributed systems"
        complexity = await scorer.score(query)
        assert complexity == ComplexityLevel.COMPLEX
    
    @pytest.mark.asyncio
    async def test_expert_complexity_scoring(self, scorer):
        """Test expert query complexity scoring."""
        query = "Analyze the theoretical foundations of quantum computing algorithms and their implementation complexity in Python frameworks"
        complexity = await scorer.score(query)
        assert complexity == ComplexityLevel.EXPERT


class TestDomainDetector:
    """Test domain detection functionality."""
    
    @pytest.fixture
    def detector(self):
        return DomainDetector()
    
    @pytest.mark.asyncio
    async def test_technology_domain_detection(self, detector):
        """Test technology domain detection."""
        query = "What is machine learning?"
        domain = await detector.detect(query)
        assert domain == DomainType.TECHNOLOGY
    
    @pytest.mark.asyncio
    async def test_science_domain_detection(self, detector):
        """Test science domain detection."""
        query = "Explain quantum physics principles"
        domain = await detector.detect(query)
        assert domain == DomainType.SCIENCE
    
    @pytest.mark.asyncio
    async def test_healthcare_domain_detection(self, detector):
        """Test healthcare domain detection."""
        query = "What are the symptoms of diabetes?"
        domain = await detector.detect(query)
        assert domain == DomainType.HEALTHCARE
    
    @pytest.mark.asyncio
    async def test_general_domain_detection(self, detector):
        """Test general domain detection."""
        query = "What is the weather like?"
        domain = await detector.detect(query)
        assert domain == DomainType.GENERAL


class TestQueryCache:
    """Test query caching functionality."""
    
    @pytest.fixture
    def cache(self):
        return QueryCache()
    
    @pytest.mark.asyncio
    async def test_cache_storage_and_retrieval(self, cache):
        """Test basic cache storage and retrieval."""
        query = "What is Python?"
        result = ProcessedQuery(
            original=query,
            intent=IntentType.FACTUAL,
            complexity=ComplexityLevel.SIMPLE,
            domain=DomainType.TECHNOLOGY,
            fingerprint="test_fingerprint",
            routing_decision="standard_agents"
        )
        
        # Store result
        await cache.set(query, result)
        
        # Retrieve result
        cached_result = await cache.get(query)
        assert cached_result is not None
        assert cached_result.original == query
        assert cached_result.intent == IntentType.FACTUAL
    
    @pytest.mark.asyncio
    async def test_cache_similarity_matching(self, cache):
        """Test cache similarity matching."""
        query1 = "What is Python programming?"
        query2 = "Tell me about Python programming language"
        
        result = ProcessedQuery(
            original=query1,
            intent=IntentType.FACTUAL,
            complexity=ComplexityLevel.SIMPLE,
            domain=DomainType.TECHNOLOGY,
            fingerprint="test_fingerprint",
            routing_decision="standard_agents"
        )
        
        # Store result for query1
        await cache.set(query1, result)
        
        # Try to retrieve with similar query2
        cached_result = await cache.get(query2)
        # Should return None for now since similarity threshold is high
        assert cached_result is None


class TestQueryIntelligenceLayer:
    """Test main query intelligence layer."""
    
    @pytest.fixture
    def intelligence_layer(self):
        return QueryIntelligenceLayer()
    
    @pytest.mark.asyncio
    async def test_basic_query_processing(self, intelligence_layer):
        """Test basic query processing."""
        query = "What is Python?"
        context = {"user_id": "123", "session_id": "abc"}
        
        result = await intelligence_layer.process_query(query, context)
        
        assert isinstance(result, ProcessedQuery)
        assert result.original == query
        assert result.intent in [IntentType.FACTUAL, IntentType.DEFINITION]
        assert result.complexity in [ComplexityLevel.SIMPLE, ComplexityLevel.MODERATE]
        assert result.domain in [DomainType.TECHNOLOGY, DomainType.GENERAL]
        assert result.fingerprint is not None
        assert result.routing_decision is not None
    
    @pytest.mark.asyncio
    async def test_complex_query_processing(self, intelligence_layer):
        """Test complex query processing."""
        query = "Explain the relationship between machine learning algorithms and artificial intelligence in modern computing systems"
        context = {"user_id": "123", "session_id": "abc"}
        
        result = await intelligence_layer.process_query(query, context)
        
        assert isinstance(result, ProcessedQuery)
        assert result.original == query
        assert result.intent == IntentType.ANALYTICAL
        assert result.complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.EXPERT]
        assert result.domain == DomainType.TECHNOLOGY
    
    @pytest.mark.asyncio
    async def test_query_fingerprinting(self, intelligence_layer):
        """Test query fingerprinting."""
        query = "What is Python?"
        context1 = {"user_id": "123", "session_id": "abc"}
        context2 = {"user_id": "456", "session_id": "def"}
        
        result1 = await intelligence_layer.process_query(query, context1)
        result2 = await intelligence_layer.process_query(query, context2)
        
        # Fingerprints should be different due to different contexts
        assert result1.fingerprint != result2.fingerprint
    
    @pytest.mark.asyncio
    async def test_routing_decision_logic(self, intelligence_layer):
        """Test routing decision logic."""
        # Simple query
        simple_query = "What is Python?"
        simple_result = await intelligence_layer.process_query(simple_query, {})
        assert simple_result.routing_decision == "standard_agents"
        
        # Complex query
        complex_query = "Analyze the theoretical foundations of quantum computing algorithms"
        complex_result = await intelligence_layer.process_query(complex_query, {})
        assert complex_result.routing_decision in ["expert_agents", "multi_agent"]
    
    @pytest.mark.asyncio
    async def test_error_handling(self, intelligence_layer):
        """Test error handling in query processing."""
        # Test with empty query
        result = await intelligence_layer.process_query("", {})
        assert isinstance(result, ProcessedQuery)
        assert result.intent == IntentType.UNKNOWN
    
    @pytest.mark.asyncio
    async def test_cache_integration(self, intelligence_layer):
        """Test cache integration."""
        query = "What is Python?"
        context = {"user_id": "123", "session_id": "abc"}
        
        # First call - should process and cache
        result1 = await intelligence_layer.process_query(query, context)
        
        # Second call - should retrieve from cache
        result2 = await intelligence_layer.process_query(query, context)
        
        # Results should be identical
        assert result1.fingerprint == result2.fingerprint
        assert result1.intent == result2.intent
        assert result1.complexity == result2.complexity


class TestProcessedQuery:
    """Test ProcessedQuery data class."""
    
    def test_processed_query_creation(self):
        """Test ProcessedQuery creation."""
        query = ProcessedQuery(
            original="What is Python?",
            intent=IntentType.FACTUAL,
            complexity=ComplexityLevel.SIMPLE,
            domain=DomainType.TECHNOLOGY,
            fingerprint="test_fingerprint",
            routing_decision="standard_agents"
        )
        
        assert query.original == "What is Python?"
        assert query.intent == IntentType.FACTUAL
        assert query.complexity == ComplexityLevel.SIMPLE
        assert query.domain == DomainType.TECHNOLOGY
        assert query.fingerprint == "test_fingerprint"
        assert query.routing_decision == "standard_agents"
    
    def test_processed_query_to_dict(self):
        """Test ProcessedQuery to_dict method."""
        query = ProcessedQuery(
            original="What is Python?",
            intent=IntentType.FACTUAL,
            complexity=ComplexityLevel.SIMPLE,
            domain=DomainType.TECHNOLOGY,
            fingerprint="test_fingerprint",
            routing_decision="standard_agents"
        )
        
        query_dict = query.to_dict()
        
        assert query_dict["original"] == "What is Python?"
        assert query_dict["intent"] == "factual"
        assert query_dict["complexity"] == "simple"
        assert query_dict["domain"] == "technology"
        assert query_dict["fingerprint"] == "test_fingerprint"
        assert query_dict["routing_decision"] == "standard_agents"


# Integration tests
class TestQueryIntelligenceIntegration:
    """Integration tests for query intelligence layer."""
    
    @pytest.fixture
    def intelligence_layer(self):
        return QueryIntelligenceLayer()
    
    @pytest.mark.asyncio
    async def test_end_to_end_query_processing(self, intelligence_layer):
        """Test end-to-end query processing."""
        queries = [
            "What is Python?",
            "How does machine learning work?",
            "Explain quantum computing principles",
            "What are the symptoms of diabetes?",
            "Analyze the relationship between AI and healthcare"
        ]
        
        for query in queries:
            context = {"user_id": "test_user", "session_id": "test_session"}
            result = await intelligence_layer.process_query(query, context)
            
            # Verify result structure
            assert isinstance(result, ProcessedQuery)
            assert result.original == query
            assert result.intent is not None
            assert result.complexity is not None
            assert result.domain is not None
            assert result.fingerprint is not None
            assert result.routing_decision is not None
            assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_performance_benchmark(self, intelligence_layer):
        """Test performance of query processing."""
        import time
        
        query = "What is Python programming language?"
        context = {"user_id": "test_user", "session_id": "test_session"}
        
        start_time = time.time()
        result = await intelligence_layer.process_query(query, context)
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000
        
        # Should complete within reasonable time (less than 1 second)
        assert processing_time < 1000
        assert result.processing_time_ms > 0


if __name__ == "__main__":
    pytest.main([__file__]) 