"""
Browser Service

This service handles web search and browsing functionality for the browser agent.
It provides web search, content extraction, and navigation capabilities.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
import json

from .base_service import BaseAgentService, ServiceType, ServiceStatus

logger = logging.getLogger(__name__)


class BrowserService(BaseAgentService):
    """
    Browser service for web search and browsing functionality.
    
    This service provides web search capabilities, content extraction,
    and navigation features for the browser agent.
    """
    
    def __init__(self, service_type: ServiceType, config: Optional[Dict[str, Any]] = None):
        """Initialize the browser service."""
        super().__init__(service_type, config)
        self.session: Optional[aiohttp.ClientSession] = None
        self.search_engines = self.get_config("search_engines", {
            "google": "https://www.google.com/search?q={}",
            "bing": "https://www.bing.com/search?q={}",
            "duckduckgo": "https://duckduckgo.com/?q={}"
        })
        self.max_results = self.get_config("max_results", 10)
        self.timeout = self.get_config("timeout", 30)
        self.user_agent = self.get_config("user_agent", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        logger.info("Browser service initialized")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check browser service health.
        
        Returns:
            Health status and metrics
        """
        try:
            # Test basic connectivity
            test_url = "https://httpbin.org/get"
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url, timeout=self.timeout) as response:
                    if response.status == 200:
                        self.update_status(ServiceStatus.HEALTHY)
                        return {
                            "healthy": True,
                            "connectivity": "OK",
                            "search_engines": list(self.search_engines.keys()),
                            "max_results": self.max_results,
                            "timeout": self.timeout
                        }
                    else:
                        self.update_status(ServiceStatus.DEGRADED)
                        return {
                            "healthy": False,
                            "connectivity": f"HTTP {response.status}",
                            "error": "Connectivity test failed"
                        }
        except Exception as e:
            self.update_status(ServiceStatus.UNHEALTHY)
            logger.error(f"Browser service health check failed: {e}")
            return {
                "healthy": False,
                "connectivity": "FAILED",
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get detailed browser service status.
        
        Returns:
            Service status information
        """
        health_info = await self.health_check()
        service_info = self.get_service_info()
        
        return {
            **service_info,
            **health_info,
            "capabilities": {
                "web_search": True,
                "content_extraction": True,
                "navigation": True,
                "multiple_search_engines": True
            },
            "configuration": {
                "search_engines": list(self.search_engines.keys()),
                "max_results": self.max_results,
                "timeout": self.timeout
            }
        }
    
    async def validate_config(self) -> bool:
        """
        Validate browser service configuration.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Check required configuration
            if not self.search_engines:
                logger.error("Browser service: No search engines configured")
                return False
            
            if self.max_results <= 0:
                logger.error("Browser service: Invalid max_results value")
                return False
            
            if self.timeout <= 0:
                logger.error("Browser service: Invalid timeout value")
                return False
            
            # Test search engine URLs
            for engine, url in self.search_engines.items():
                if not url or not url.startswith("http"):
                    logger.error(f"Browser service: Invalid URL for {engine}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Browser service config validation failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get browser service performance metrics.
        
        Returns:
            Performance metrics
        """
        base_metrics = self.get_service_info()
        
        # Add browser-specific metrics
        browser_metrics = {
            "search_operations": 0,  # TODO: Track actual search operations
            "content_extractions": 0,  # TODO: Track content extractions
            "average_response_time": 0.0,  # TODO: Track response times
            "success_rate": 1.0 if self.error_count == 0 else 0.0
        }
        
        return {**base_metrics, **browser_metrics}
    
    async def search_web(self, query: str, search_engine: str = "google", max_results: Optional[int] = None) -> Dict[str, Any]:
        """
        Perform web search.
        
        Args:
            query: Search query
            search_engine: Search engine to use
            max_results: Maximum number of results
            
        Returns:
            Search results
        """
        await self.pre_request()
        
        try:
            if search_engine not in self.search_engines:
                raise ValueError(f"Unsupported search engine: {search_engine}")
            
            max_results = max_results or self.max_results
            search_url = self.search_engines[search_engine].format(query)
            
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, timeout=self.timeout) as response:
                    if response.status != 200:
                        raise Exception(f"Search request failed with status {response.status}")
                    
                    content = await response.text()
                    results = self._parse_search_results(content, search_engine, max_results)
                    
                    await self.post_request(success=True)
                    
                    return {
                        "query": query,
                        "search_engine": search_engine,
                        "results": results,
                        "total_results": len(results),
                        "search_url": search_url
                    }
                    
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Web search failed: {e}")
            raise
    
    async def extract_content(self, url: str) -> Dict[str, Any]:
        """
        Extract content from a URL.
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted content
        """
        await self.pre_request()
        
        try:
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=self.timeout) as response:
                    if response.status != 200:
                        raise Exception(f"Content extraction failed with status {response.status}")
                    
                    content = await response.text()
                    extracted = self._extract_text_content(content, url)
                    
                    await self.post_request(success=True)
                    
                    return {
                        "url": url,
                        "title": extracted.get("title", ""),
                        "content": extracted.get("content", ""),
                        "links": extracted.get("links", []),
                        "metadata": extracted.get("metadata", {})
                    }
                    
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Content extraction failed: {e}")
            raise
    
    async def browse_page(self, url: str, follow_links: bool = False, max_links: int = 5) -> Dict[str, Any]:
        """
        Browse a page and optionally follow links.
        
        Args:
            url: URL to browse
            follow_links: Whether to follow links
            max_links: Maximum number of links to follow
            
        Returns:
            Browse results
        """
        await self.pre_request()
        
        try:
            # Extract main page content
            main_content = await self.extract_content(url)
            
            result = {
                "main_page": main_content,
                "followed_links": []
            }
            
            # Follow links if requested
            if follow_links and main_content.get("links"):
                links = main_content["links"][:max_links]
                
                for link in links:
                    try:
                        link_content = await self.extract_content(link)
                        result["followed_links"].append(link_content)
                    except Exception as e:
                        logger.warning(f"Failed to follow link {link}: {e}")
                        result["followed_links"].append({
                            "url": link,
                            "error": str(e)
                        })
            
            await self.post_request(success=True)
            return result
            
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Page browsing failed: {e}")
            raise
    
    def _parse_search_results(self, content: str, search_engine: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Parse search results from HTML content.
        
        Args:
            content: HTML content
            search_engine: Search engine used
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        results = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            if search_engine == "google":
                # Parse Google search results
                for result in soup.select('.g')[:max_results]:
                    title_elem = result.select_one('h3')
                    link_elem = result.select_one('a')
                    snippet_elem = result.select_one('.VwiC3b')
                    
                    if title_elem and link_elem:
                        results.append({
                            "title": title_elem.get_text(strip=True),
                            "url": link_elem.get('href', ''),
                            "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""
                        })
            
            elif search_engine == "bing":
                # Parse Bing search results
                for result in soup.select('.b_algo')[:max_results]:
                    title_elem = result.select_one('h2 a')
                    snippet_elem = result.select_one('.b_caption p')
                    
                    if title_elem:
                        results.append({
                            "title": title_elem.get_text(strip=True),
                            "url": title_elem.get('href', ''),
                            "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""
                        })
            
            else:
                # Generic parsing for other search engines
                for link in soup.find_all('a', href=True)[:max_results]:
                    if link.get_text(strip=True):
                        results.append({
                            "title": link.get_text(strip=True),
                            "url": link.get('href', ''),
                            "snippet": ""
                        })
            
        except Exception as e:
            logger.error(f"Failed to parse search results: {e}")
        
        return results
    
    def _extract_text_content(self, content: str, url: str) -> Dict[str, Any]:
        """
        Extract text content from HTML.
        
        Args:
            content: HTML content
            url: Source URL
            
        Returns:
            Extracted content
        """
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract title
            title = ""
            title_elem = soup.find('title')
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            # Extract main content
            content_text = ""
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            content_text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in content_text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and href.startswith('http'):
                    links.append(href)
            
            # Extract metadata
            metadata = {}
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    metadata[name] = content
            
            return {
                "title": title,
                "content": content_text[:5000],  # Limit content length
                "links": links[:20],  # Limit number of links
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to extract content: {e}")
            return {
                "title": "",
                "content": "",
                "links": [],
                "metadata": {}
            }
    
    async def shutdown(self) -> None:
        """Shutdown the browser service."""
        await super().shutdown()
        
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info("Browser service shutdown complete") 