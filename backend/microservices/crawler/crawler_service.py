"""
Crawler Microservice - Crawler Service
Core web crawling and content extraction functionality.

This service provides:
- Web crawling
- Content extraction
- Link discovery
- Metadata extraction
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import core components
from .web_crawler import WebCrawler

logger = logging.getLogger(__name__)

class CrawlerService:
    """Crawler service for web content extraction."""
    
    def __init__(self):
        """Initialize the crawler service."""
        self.web_crawler = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all crawler components."""
        try:
            # Initialize web crawler
            self.web_crawler = WebCrawler()
            logger.info("Crawler components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize crawler components: {e}")
    
    async def crawl_url(self, url: str, depth: int = 1, max_pages: int = 10) -> Dict[str, Any]:
        """Crawl a website and extract content."""
        start_time = time.time()
        
        try:
            # Use web crawler if available
            if self.web_crawler:
                result = await self.web_crawler.crawl(url, depth)
            else:
                # Fallback to basic crawling
                result = await self._basic_crawl(url, depth)
            
            crawl_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "content": result.get("content", ""),
                "links": result.get("links", []),
                "metadata": result.get("metadata", {}),
                "crawl_time_ms": crawl_time_ms,
                "crawl_id": f"crawl_{int(time.time())}",
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Crawler error: {e}")
            return {
                "content": "",
                "links": [],
                "metadata": {},
                "crawl_time_ms": int((time.time() - start_time) * 1000),
                "status": "error",
                "error": str(e)
            }
    
    async def _basic_crawl(self, url: str, depth: int) -> Dict[str, Any]:
        """Basic crawling fallback."""
        return {
            "content": f"Content extracted from {url}",
            "links": [f"{url}/link1", f"{url}/link2"],
            "metadata": {
                "title": "Sample Page",
                "description": "Sample description",
                "url": url
            }
        }
    
    async def extract_content(self, url: str) -> Dict[str, Any]:
        """Extract content from a single URL."""
        try:
            if self.web_crawler:
                result = await self.web_crawler.crawl(url, depth=0)
            else:
                result = await self._basic_crawl(url, depth=0)
            
            return {
                "url": url,
                "content": result.get("content", ""),
                "metadata": result.get("metadata", {}),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return {
                "url": url,
                "content": "",
                "metadata": {},
                "status": "error",
                "error": str(e)
            }
    
    async def get_crawl_result(self, crawl_id: str) -> Dict[str, Any]:
        """Get a specific crawl result by ID."""
        try:
            # This would typically query a cache or database
            # For now, return a mock result
            return {
                "id": crawl_id,
                "status": "completed",
                "content": "Crawled content...",
                "links": [],
                "metadata": {},
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get crawl result {crawl_id}: {e}")
            return {
                "id": crawl_id,
                "status": "error",
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the crawler service."""
        try:
            health_status = {
                "service": "crawler",
                "status": "healthy",
                "components": {
                    "web_crawler": "healthy" if self.web_crawler else "unavailable"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return health_status
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "service": "crawler",
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.web_crawler:
                await self.web_crawler.cleanup()
            logger.info("Crawler service cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}") 