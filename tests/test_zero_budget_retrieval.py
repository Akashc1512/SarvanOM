#!/usr/bin/env python3
"""
Unit tests for Zero-Budget Retrieval System

Tests all components including:
- MediaWiki API integration
- Brave Search API
- DuckDuckGo HTML parsing
- Caching functionality
- Result deduplication
- Error handling and retry logic

Following MAANG/OpenAI/Perplexity standards for comprehensive testing.
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime

# Import the zero-budget retrieval system
from services.retrieval.free_tier import (
    ZeroBudgetRetrieval, SearchResult, SearchResponse, SearchProvider,
    get_zero_budget_retrieval, combined_search, wiki_search, free_web_search
)


class TestZeroBudgetRetrieval:
    """Test zero-budget retrieval system."""
    
    @pytest.fixture
    async def retrieval_system(self):
        """Create a test retrieval system instance."""
        system = ZeroBudgetRetrieval()
        # Initialize async components
        await system.setup_session()
        return system
    
    @pytest.fixture
    def mock_session(self):
        """Mock aiohttp session."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value = AsyncMock()
            yield mock_session
    
    @pytest.mark.asyncio
    async def test_initialization(self, retrieval_system):
        """Test system initialization."""
        assert retrieval_system is not None
        assert hasattr(retrieval_system, 'redis_client')
        assert hasattr(retrieval_system, 'session')
    
    @pytest.mark.asyncio
    async def test_normalize_query(self, retrieval_system):
        """Test query normalization."""
        # Test basic normalization
        assert retrieval_system._normalize_query("  Test Query  ") == "test query"
        
        # Test multiple spaces
        assert retrieval_system._normalize_query("test   query   with   spaces") == "test query with spaces"
        
        # Test empty query
        assert retrieval_system._normalize_query("") == ""
    
    @pytest.mark.asyncio
    async def test_generate_cache_key(self, retrieval_system):
        """Test cache key generation."""
        key1 = retrieval_system._generate_cache_key("test query", "combined", 5)
        key2 = retrieval_system._generate_cache_key("test query", "combined", 5)
        key3 = retrieval_system._generate_cache_key("different query", "combined", 5)
        
        # Same query should generate same key
        assert key1 == key2
        
        # Different query should generate different key
        assert key1 != key3
        
        # Key should have proper format
        assert key1.startswith("retrieval:combined:")
        assert len(key1) > 20  # Should be reasonably long
    
    @pytest.mark.asyncio
    async def test_extract_domain(self, retrieval_system):
        """Test domain extraction from URLs."""
        assert retrieval_system._extract_domain("https://www.example.com/page") == "www.example.com"
        assert retrieval_system._extract_domain("http://example.com") == "example.com"
        assert retrieval_system._extract_domain("https://sub.domain.co.uk/path") == "sub.domain.co.uk"
        assert retrieval_system._extract_domain("invalid-url") == "unknown"
    
    @pytest.mark.asyncio
    async def test_calculate_relevance_score(self, retrieval_system):
        """Test relevance score calculation."""
        result = SearchResult(
            title="Artificial Intelligence and Machine Learning",
            url="https://example.com",
            snippet="This article discusses artificial intelligence and machine learning techniques.",
            domain="example.com",
            provider=SearchProvider.MEDIAWIKI
        )
        
        # Test with matching query
        score = retrieval_system._calculate_relevance_score(result, "artificial intelligence")
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be high for matching query
        
        # Test with non-matching query
        score = retrieval_system._calculate_relevance_score(result, "cooking recipes")
        assert 0.0 <= score <= 1.0
        assert score < 0.3  # Should be low for non-matching query
    
    @pytest.mark.asyncio
    async def test_title_similarity(self, retrieval_system):
        """Test title similarity calculation."""
        # Test similar titles
        similarity = retrieval_system._title_similarity(
            "Artificial Intelligence Guide",
            "AI Guide for Beginners"
        )
        assert 0.0 <= similarity <= 1.0
        
        # Test identical titles
        similarity = retrieval_system._title_similarity(
            "Machine Learning Basics",
            "Machine Learning Basics"
        )
        assert similarity == 1.0
        
        # Test completely different titles
        similarity = retrieval_system._title_similarity(
            "Cooking Recipes",
            "Quantum Physics"
        )
        assert similarity == 0.0
    
    @pytest.mark.asyncio
    async def test_deduplicate_results(self, retrieval_system):
        """Test result deduplication."""
        results = [
            SearchResult(
                title="AI Guide",
                url="https://example1.com",
                snippet="AI guide content",
                domain="example1.com",
                provider=SearchProvider.MEDIAWIKI
            ),
            SearchResult(
                title="AI Guide",  # Same title, different domain
                url="https://example2.com",
                snippet="AI guide content",
                domain="example2.com",
                provider=SearchProvider.BRAVE
            ),
            SearchResult(
                title="Machine Learning Basics",  # Different title
                url="https://example3.com",
                snippet="ML content",
                domain="example3.com",
                provider=SearchProvider.DUCKDUCKGO
            )
        ]
        
        deduplicated = retrieval_system._deduplicate_results(results)
        
        # Should have 3 results (different domains/titles)
        assert len(deduplicated) == 3
        
        # Test with duplicate title and domain
        duplicate_results = [
            SearchResult(
                title="AI Guide",
                url="https://example.com",
                snippet="AI guide content",
                domain="example.com",
                provider=SearchProvider.MEDIAWIKI
            ),
            SearchResult(
                title="AI Guide",
                url="https://example.com",
                snippet="AI guide content",
                domain="example.com",
                provider=SearchProvider.BRAVE
            )
        ]
        
        deduplicated = retrieval_system._deduplicate_results(duplicate_results)
        assert len(deduplicated) == 1  # Should remove duplicate
    
    @pytest.mark.asyncio
    async def test_wiki_search_success(self, retrieval_system, mock_session):
        """Test successful Wikipedia search."""
        # Mock MediaWiki API responses
        search_response = {
            "query": {
                "search": [
                    {
                        "title": "Artificial Intelligence",
                        "pageid": 12345,
                        "wordcount": 1000
                    }
                ]
            }
        }
        
        summary_response = {
            "extract": "Artificial intelligence (AI) is intelligence demonstrated by machines...",
            "content_urls": {
                "desktop": {
                    "page": "https://en.wikipedia.org/wiki/Artificial_intelligence"
                }
            }
        }
        
        # Mock the session responses
        mock_session.return_value.get.return_value.__aenter__.return_value.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value.json.side_effect = [
            search_response,
            summary_response
        ]
        
        results = await retrieval_system.wiki_search("artificial intelligence", k=1)
        
        assert len(results) == 1
        assert results[0].title == "Artificial Intelligence"
        assert results[0].domain == "wikipedia.org"
        assert results[0].provider == SearchProvider.MEDIAWIKI
        assert "Artificial intelligence (AI)" in results[0].snippet
    
    @pytest.mark.asyncio
    async def test_wiki_search_failure(self, retrieval_system, mock_session):
        """Test Wikipedia search failure handling."""
        # Mock failed response
        mock_session.return_value.get.return_value.__aenter__.return_value.status = 500
        
        results = await retrieval_system.wiki_search("test query", k=1)
        
        # Should return empty list on failure
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_brave_search_success(self, retrieval_system, mock_session):
        """Test successful Brave search."""
        # Mock Brave API response
        brave_response = {
            "web": {
                "results": [
                    {
                        "title": "AI Research Paper",
                        "url": "https://example.com/ai-paper",
                        "description": "Research on artificial intelligence...",
                        "age": "2024",
                        "language": "en"
                    }
                ]
            }
        }
        
        # Mock the session response
        mock_session.return_value.get.return_value.__aenter__.return_value.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value.json.return_value = brave_response
        
        with patch('services.retrieval.free_tier.BRAVE_API_KEY', 'test_key'):
            results = await retrieval_system._brave_search("artificial intelligence", k=1)
        
        assert len(results) == 1
        assert results[0].title == "AI Research Paper"
        assert results[0].provider == SearchProvider.BRAVE
        assert results[0].domain == "example.com"
    
    @pytest.mark.asyncio
    async def test_duckduckgo_search_success(self, retrieval_system, mock_session):
        """Test successful DuckDuckGo search."""
        # Mock HTML response
        html_content = """
        <html>
            <body>
                <a href="https://example.com/ai-guide">Artificial Intelligence Guide</a>
                <p>Comprehensive guide to artificial intelligence and machine learning...</p>
                <a href="https://example2.com/ml-basics">Machine Learning Basics</a>
                <p>Introduction to machine learning concepts and techniques...</p>
            </body>
        </html>
        """
        
        # Mock the session response
        mock_session.return_value.get.return_value.__aenter__.return_value.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value.text.return_value = html_content
        
        results = await retrieval_system._duckduckgo_search("artificial intelligence", k=2)
        
        assert len(results) >= 1
        assert any("Artificial Intelligence" in result.title for result in results)
        assert all(result.provider == SearchProvider.DUCKDUCKGO for result in results)
    
    @pytest.mark.asyncio
    async def test_free_web_search_brave_fallback(self, retrieval_system):
        """Test web search with Brave fallback to DuckDuckGo."""
        # Mock Brave search to fail
        with patch.object(retrieval_system, '_brave_search', return_value=[]):
            # Mock DuckDuckGo search to succeed
            with patch.object(retrieval_system, '_duckduckgo_search') as mock_ddg:
                mock_ddg.return_value = [
                    SearchResult(
                        title="Test Result",
                        url="https://example.com",
                        snippet="Test content",
                        domain="example.com",
                        provider=SearchProvider.DUCKDUCKGO
                    )
                ]
                
                results = await retrieval_system.free_web_search("test query", k=1)
                
                assert len(results) == 1
                assert results[0].provider == SearchProvider.DUCKDUCKGO
                mock_ddg.assert_called_once_with("test query", 1)
    
    @pytest.mark.asyncio
    async def test_search_with_cache_hit(self, retrieval_system):
        """Test search with cache hit."""
        # Mock cache to return data
        cached_data = [
            {
                "title": "Cached Result",
                "url": "https://example.com",
                "snippet": "Cached content",
                "domain": "example.com",
                "provider": "mediawiki",
                "relevance_score": 0.8,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {}
            }
        ]
        
        with patch.object(retrieval_system, '_cache_get', return_value=cached_data):
            with patch.object(retrieval_system, '_cache_set') as mock_cache_set:
                response = await retrieval_system.search("test query", k=1)
                
                assert response.cache_hit == True
                assert len(response.results) == 1
                assert response.results[0].title == "Cached Result"
                assert response.providers_used == [SearchProvider.CACHE]
                mock_cache_set.assert_not_called()  # Should not set cache on hit
    
    @pytest.mark.asyncio
    async def test_search_with_cache_miss(self, retrieval_system):
        """Test search with cache miss."""
        # Mock cache to return None (miss)
        with patch.object(retrieval_system, '_cache_get', return_value=None):
            with patch.object(retrieval_system, '_cache_set') as mock_cache_set:
                # Mock actual search to return results
                with patch.object(retrieval_system, 'wiki_search', return_value=[]):
                    with patch.object(retrieval_system, 'free_web_search', return_value=[]):
                        response = await retrieval_system.search("test query", k=1)
                        
                        assert response.cache_hit == False
                        assert len(response.results) == 0
                        mock_cache_set.assert_called_once()  # Should set cache on miss
    
    @pytest.mark.asyncio
    async def test_search_with_wiki_only(self, retrieval_system):
        """Test search with Wikipedia only."""
        wiki_results = [
            SearchResult(
                title="Wikipedia Result",
                url="https://wikipedia.org",
                snippet="Wikipedia content",
                domain="wikipedia.org",
                provider=SearchProvider.MEDIAWIKI
            )
        ]
        
        with patch.object(retrieval_system, '_cache_get', return_value=None):
            with patch.object(retrieval_system, 'wiki_search', return_value=wiki_results):
                with patch.object(retrieval_system, 'free_web_search', return_value=[]):
                    with patch.object(retrieval_system, '_cache_set'):
                        response = await retrieval_system.search("test query", k=1, use_wiki=True, use_web=False)
                        
                        assert len(response.results) == 1
                        assert response.results[0].provider == SearchProvider.MEDIAWIKI
                        assert SearchProvider.MEDIAWIKI in response.providers_used
    
    @pytest.mark.asyncio
    async def test_search_with_web_only(self, retrieval_system):
        """Test search with web search only."""
        web_results = [
            SearchResult(
                title="Web Result",
                url="https://example.com",
                snippet="Web content",
                domain="example.com",
                provider=SearchProvider.DUCKDUCKGO
            )
        ]
        
        with patch.object(retrieval_system, '_cache_get', return_value=None):
            with patch.object(retrieval_system, 'wiki_search', return_value=[]):
                with patch.object(retrieval_system, 'free_web_search', return_value=web_results):
                    with patch.object(retrieval_system, '_cache_set'):
                        response = await retrieval_system.search("test query", k=1, use_wiki=False, use_web=True)
                        
                        assert len(response.results) == 1
                        assert response.results[0].provider == SearchProvider.DUCKDUCKGO
                        assert SearchProvider.DUCKDUCKGO in response.providers_used
    
    @pytest.mark.asyncio
    async def test_make_request_with_retry_success(self, retrieval_system, mock_session):
        """Test HTTP request with retry logic - success case."""
        # Mock successful response
        mock_session.return_value.get.return_value.__aenter__.return_value.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value.json.return_value = {"test": "data"}
        
        result = await retrieval_system._make_request_with_retry("https://example.com")
        
        assert result == {"test": "data"}
    
    @pytest.mark.asyncio
    async def test_make_request_with_retry_failure(self, retrieval_system, mock_session):
        """Test HTTP request with retry logic - failure case."""
        # Mock failed response
        mock_session.return_value.get.return_value.__aenter__.return_value.status = 500
        
        result = await retrieval_system._make_request_with_retry("https://example.com")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_make_request_with_retry_exception(self, retrieval_system, mock_session):
        """Test HTTP request with retry logic - exception case."""
        # Mock exception
        mock_session.return_value.get.side_effect = Exception("Connection failed")
        
        result = await retrieval_system._make_request_with_retry("https://example.com")
        
        assert result is None


class TestZeroBudgetRetrievalIntegration:
    """Integration tests for zero-budget retrieval."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_search(self):
        """Test end-to-end search functionality."""
        # Test with mocked providers
        retrieval_system = get_zero_budget_retrieval()
        with patch.object(retrieval_system, '_cache_get', return_value=None):
            with patch.object(retrieval_system, 'wiki_search', return_value=[]):
                with patch.object(retrieval_system, 'free_web_search', return_value=[]):
                    with patch.object(retrieval_system, '_cache_set'):
                        response = await combined_search("test query", k=3)
                        
                        assert response is not None
                        assert hasattr(response, 'query')
                        assert hasattr(response, 'results')
                        assert hasattr(response, 'cache_hit')
                        assert hasattr(response, 'providers_used')
                        assert hasattr(response, 'processing_time_ms')
                        assert hasattr(response, 'trace_id')
    
    @pytest.mark.asyncio
    async def test_convenience_functions(self):
        """Test convenience functions."""
        # Test wiki_search
        retrieval_system = get_zero_budget_retrieval()
        with patch.object(retrieval_system, 'wiki_search', return_value=[]) as mock_wiki:
            results = await wiki_search("test query", k=2)
            mock_wiki.assert_called_once_with("test query", 2)
        
        # Test free_web_search
        with patch.object(retrieval_system, 'free_web_search', return_value=[]) as mock_web:
            results = await free_web_search("test query", k=3)
            mock_web.assert_called_once_with("test query", 3)


class TestZeroBudgetRetrievalErrorHandling:
    """Test error handling in zero-budget retrieval."""
    
    @pytest.mark.asyncio
    async def test_redis_connection_failure(self):
        """Test handling of Redis connection failure."""
        # Create system with Redis connection failure
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_redis.side_effect = Exception("Redis connection failed")
            
            system = ZeroBudgetRetrieval()
            
            # Should continue without Redis
            assert system.redis_client is None
    
    @pytest.mark.asyncio
    async def test_cache_operations_without_redis(self):
        """Test cache operations when Redis is not available."""
        system = ZeroBudgetRetrieval()
        system.redis_client = None  # Simulate no Redis
        
        # Cache operations should not fail
        cache_data = await system._cache_get("test_key")
        assert cache_data is None
        
        # Cache set should not fail
        await system._cache_set("test_key", [{"test": "data"}], 10)
    
    @pytest.mark.asyncio
    async def test_session_cleanup(self):
        """Test proper session cleanup."""
        system = ZeroBudgetRetrieval()
        
        # Mock session close
        with patch.object(system.session, 'close') as mock_close:
            await system.close()
            mock_close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
