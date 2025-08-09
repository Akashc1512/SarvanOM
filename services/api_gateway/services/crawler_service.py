"""
Crawler Service

This service handles web crawling, content extraction, and link discovery functionality for the crawler agent.
It provides web crawling, content extraction, and sitemap generation capabilities.
"""

import logging
from shared.core.unified_logging import get_logger
import asyncio
import aiohttp
import tempfile
import os
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlunparse
import re
from bs4 import BeautifulSoup
import json
import hashlib
from collections import deque

from .base_service import BaseAgentService, ServiceType, ServiceStatus

logger = get_logger(__name__)


class CrawlerService(BaseAgentService):
    """
    Crawler service for web crawling and content extraction.

    This service provides web crawling, content extraction,
    and link discovery capabilities for the crawler agent.
    """

    def __init__(
        self, service_type: ServiceType, config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the crawler service."""
        super().__init__(service_type, config)
        self.max_depth = self.get_config("max_depth", 3)
        self.max_pages = self.get_config("max_pages", 100)
        self.timeout = self.get_config("timeout", 30)
        self.delay = self.get_config("delay", 1.0)  # seconds between requests
        self.user_agent = self.get_config(
            "user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.follow_redirects = self.get_config("follow_redirects", True)
        self.extract_images = self.get_config("extract_images", True)
        self.extract_links = self.get_config("extract_links", True)

        # Crawling state
        self.visited_urls: Set[str] = set()
        self.url_queue: deque = deque()
        self.session: Optional[aiohttp.ClientSession] = None

        logger.info("Crawler service initialized")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check crawler service health.

        Returns:
            Health status and metrics
        """
        try:
            # Test basic connectivity
            test_result = await self._test_crawler_connectivity()

            if test_result["success"]:
                self.update_status(ServiceStatus.HEALTHY)
                return {
                    "healthy": True,
                    "crawler_connectivity": "OK",
                    "max_depth": self.max_depth,
                    "max_pages": self.max_pages,
                    "timeout": self.timeout,
                    "delay": self.delay,
                    "visited_urls": len(self.visited_urls),
                }
            else:
                self.update_status(ServiceStatus.DEGRADED)
                return {
                    "healthy": False,
                    "crawler_connectivity": "FAILED",
                    "error": test_result.get("error", "Unknown error"),
                }

        except Exception as e:
            self.update_status(ServiceStatus.UNHEALTHY)
            logger.error(f"Crawler service health check failed: {e}")
            return {"healthy": False, "crawler_connectivity": "FAILED", "error": str(e)}

    async def get_status(self) -> Dict[str, Any]:
        """
        Get detailed crawler service status.

        Returns:
            Service status information
        """
        health_info = await self.health_check()
        service_info = self.get_service_info()

        return {
            **service_info,
            **health_info,
            "capabilities": {
                "web_crawling": True,
                "content_extraction": True,
                "link_discovery": True,
                "sitemap_generation": True,
                "image_extraction": self.extract_images,
            },
            "configuration": {
                "max_depth": self.max_depth,
                "max_pages": self.max_pages,
                "timeout": self.timeout,
                "delay": self.delay,
                "follow_redirects": self.follow_redirects,
                "extract_images": self.extract_images,
                "extract_links": self.extract_links,
            },
        }

    async def validate_config(self) -> bool:
        """
        Validate crawler service configuration.

        Returns:
            True if configuration is valid
        """
        try:
            # Check required configuration
            if self.max_depth <= 0:
                logger.error("Crawler service: Invalid max_depth value")
                return False

            if self.max_pages <= 0:
                logger.error("Crawler service: Invalid max_pages value")
                return False

            if self.timeout <= 0:
                logger.error("Crawler service: Invalid timeout value")
                return False

            if self.delay < 0:
                logger.error("Crawler service: Invalid delay value")
                return False

            return True

        except Exception as e:
            logger.error(f"Crawler service config validation failed: {e}")
            return False

    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get crawler service performance metrics.

        Returns:
            Performance metrics
        """
        base_metrics = self.get_service_info()

        # Add crawler-specific metrics
        crawler_metrics = {
            "pages_crawled": len(self.visited_urls),
            "links_discovered": 0,  # TODO: Track discovered links
            "images_extracted": 0,  # TODO: Track extracted images
            "average_crawl_time": 0.0,  # TODO: Track crawl times
            "success_rate": 1.0 if self.error_count == 0 else 0.0,
        }

        return {**base_metrics, **crawler_metrics}

    async def crawl_website(
        self,
        start_url: str,
        max_depth: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Crawl a website starting from a URL.

        Args:
            start_url: Starting URL for crawling
            max_depth: Maximum crawl depth
            max_pages: Maximum number of pages to crawl

        Returns:
            Crawling results
        """
        await self.pre_request()

        try:
            # Initialize crawling parameters
            depth_limit = max_depth or self.max_depth
            page_limit = max_pages or self.max_pages

            # Reset crawling state
            self.visited_urls.clear()
            self.url_queue.clear()

            # Add start URL to queue
            self.url_queue.append((start_url, 0))  # (url, depth)

            # Initialize results
            results = {
                "start_url": start_url,
                "pages_crawled": [],
                "total_pages": 0,
                "total_links": 0,
                "total_images": 0,
                "crawl_time": 0.0,
                "errors": [],
            }

            start_time = datetime.now()

            # Start crawling
            while self.url_queue and len(self.visited_urls) < page_limit:
                url, depth = self.url_queue.popleft()

                if depth > depth_limit:
                    continue

                if url in self.visited_urls:
                    continue

                try:
                    # Crawl the page
                    page_result = await self._crawl_page(url, depth)
                    results["pages_crawled"].append(page_result)
                    results["total_pages"] += 1
                    results["total_links"] += len(page_result.get("links", []))
                    results["total_images"] += len(page_result.get("images", []))

                    # Add discovered links to queue
                    if depth < depth_limit:
                        for link in page_result.get("links", []):
                            if link not in self.visited_urls:
                                self.url_queue.append((link, depth + 1))

                    # Mark as visited
                    self.visited_urls.add(url)

                    # Delay between requests
                    if self.delay > 0:
                        await asyncio.sleep(self.delay)

                except Exception as e:
                    error_info = {"url": url, "depth": depth, "error": str(e)}
                    results["errors"].append(error_info)
                    logger.error(f"Failed to crawl {url}: {e}")

            # Calculate crawl time
            results["crawl_time"] = (datetime.now() - start_time).total_seconds()

            await self.post_request(success=True)
            return results

        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Website crawling failed: {e}")
            raise

    async def extract_content(
        self,
        url: str,
        extract_images: Optional[bool] = None,
        extract_links: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Extract content from a single URL.

        Args:
            url: URL to extract content from
            extract_images: Whether to extract images
            extract_links: Whether to extract links

        Returns:
            Content extraction results
        """
        await self.pre_request()

        try:
            # Use service defaults if not specified
            extract_images = (
                extract_images if extract_images is not None else self.extract_images
            )
            extract_links = (
                extract_links if extract_links is not None else self.extract_links
            )

            # Extract content
            result = await self._extract_page_content(
                url, extract_images, extract_links
            )
            await self.post_request(success=True)
            return result

        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Content extraction failed: {e}")
            raise

    async def discover_links(
        self, url: str, max_links: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Discover links from a URL.

        Args:
            url: URL to discover links from
            max_links: Maximum number of links to discover

        Returns:
            Link discovery results
        """
        await self.pre_request()

        try:
            # Discover links
            result = await self._discover_page_links(url, max_links)
            await self.post_request(success=True)
            return result

        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Link discovery failed: {e}")
            raise

    async def generate_sitemap(
        self, start_url: str, max_pages: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a sitemap for a website.

        Args:
            start_url: Starting URL for sitemap generation
            max_pages: Maximum number of pages to include

        Returns:
            Sitemap generation results
        """
        await self.pre_request()

        try:
            # Crawl website to discover pages
            crawl_result = await self.crawl_website(
                start_url, max_depth=2, max_pages=max_pages or self.max_pages
            )

            # Generate sitemap
            sitemap = await self._generate_sitemap_xml(
                crawl_result["pages_crawled"], start_url
            )

            result = {
                "start_url": start_url,
                "total_pages": len(crawl_result["pages_crawled"]),
                "sitemap": sitemap,
                "pages": [page["url"] for page in crawl_result["pages_crawled"]],
            }

            await self.post_request(success=True)
            return result

        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Sitemap generation failed: {e}")
            raise

    async def crawl_with_filters(
        self,
        start_url: str,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Crawl website with URL filters.

        Args:
            start_url: Starting URL for crawling
            include_patterns: URL patterns to include
            exclude_patterns: URL patterns to exclude
            max_depth: Maximum crawl depth

        Returns:
            Filtered crawling results
        """
        await self.pre_request()

        try:
            # Crawl website
            crawl_result = await self.crawl_website(start_url, max_depth=max_depth)

            # Apply filters
            filtered_pages = []
            for page in crawl_result["pages_crawled"]:
                url = page["url"]

                # Check include patterns
                if include_patterns:
                    if not any(re.search(pattern, url) for pattern in include_patterns):
                        continue

                # Check exclude patterns
                if exclude_patterns:
                    if any(re.search(pattern, url) for pattern in exclude_patterns):
                        continue

                filtered_pages.append(page)

            result = {
                "start_url": start_url,
                "original_pages": len(crawl_result["pages_crawled"]),
                "filtered_pages": len(filtered_pages),
                "pages": filtered_pages,
                "include_patterns": include_patterns,
                "exclude_patterns": exclude_patterns,
            }

            await self.post_request(success=True)
            return result

        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Filtered crawling failed: {e}")
            raise

    async def _crawl_page(self, url: str, depth: int) -> Dict[str, Any]:
        """
        Crawl a single page.

        Args:
            url: URL to crawl
            depth: Current crawl depth

        Returns:
            Page crawling results
        """
        try:
            # Extract content
            content_result = await self._extract_page_content(
                url, self.extract_images, self.extract_links
            )

            # Add crawl metadata
            content_result.update(
                {"url": url, "depth": depth, "crawled_at": datetime.now().isoformat()}
            )

            return content_result

        except Exception as e:
            return {
                "url": url,
                "depth": depth,
                "error": str(e),
                "crawled_at": datetime.now().isoformat(),
            }

    async def _extract_page_content(
        self, url: str, extract_images: bool, extract_links: bool
    ) -> Dict[str, Any]:
        """
        Extract content from a page.

        Args:
            url: URL to extract content from
            extract_images: Whether to extract images
            extract_links: Whether to extract links

        Returns:
            Content extraction results
        """
        try:
            # Create session if not exists
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={"User-Agent": self.user_agent},
                )

            # Fetch page
            async with self.session.get(
                url, allow_redirects=self.follow_redirects
            ) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")

                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")

                # Extract basic information
                title = soup.find("title")
                title_text = title.get_text(strip=True) if title else ""

                # Extract text content
                for script in soup(["script", "style"]):
                    script.decompose()

                text_content = soup.get_text()
                lines = (line.strip() for line in text_content.splitlines())
                chunks = (
                    phrase.strip() for line in lines for phrase in line.split("  ")
                )
                text_content = " ".join(chunk for chunk in chunks if chunk)

                result = {
                    "title": title_text,
                    "content": text_content[:10000],  # Limit content length
                    "url": url,
                    "status_code": response.status,
                    "content_length": len(content),
                    "extracted_at": datetime.now().isoformat(),
                }

                # Extract links
                if extract_links:
                    links = []
                    for link in soup.find_all("a", href=True):
                        href = link.get("href")
                        if href:
                            absolute_url = urljoin(url, href)
                            if self._is_valid_url(absolute_url):
                                links.append(absolute_url)

                    result["links"] = list(set(links))  # Remove duplicates

                # Extract images
                if extract_images:
                    images = []
                    for img in soup.find_all("img", src=True):
                        src = img.get("src")
                        if src:
                            absolute_url = urljoin(url, src)
                            if self._is_valid_url(absolute_url):
                                images.append(
                                    {
                                        "src": absolute_url,
                                        "alt": img.get("alt", ""),
                                        "title": img.get("title", ""),
                                    }
                                )

                    result["images"] = images

                return result

        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "extracted_at": datetime.now().isoformat(),
            }

    async def _discover_page_links(
        self, url: str, max_links: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Discover links from a page.

        Args:
            url: URL to discover links from
            max_links: Maximum number of links to discover

        Returns:
            Link discovery results
        """
        try:
            # Extract content with links only
            content_result = await self._extract_page_content(
                url, extract_images=False, extract_links=True
            )

            links = content_result.get("links", [])

            # Limit results if specified
            if max_links and len(links) > max_links:
                links = links[:max_links]

            return {
                "url": url,
                "links": links,
                "total_links": len(links),
                "discovered_at": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "discovered_at": datetime.now().isoformat(),
            }

    async def _generate_sitemap_xml(
        self, pages: List[Dict[str, Any]], base_url: str
    ) -> str:
        """
        Generate XML sitemap.

        Args:
            pages: List of crawled pages
            base_url: Base URL for the sitemap

        Returns:
            XML sitemap string
        """
        try:
            xml_parts = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            ]

            for page in pages:
                if "url" in page and "error" not in page:
                    xml_parts.append("  <url>")
                    xml_parts.append(f'    <loc>{page["url"]}</loc>')

                    if "crawled_at" in page:
                        xml_parts.append(f'    <lastmod>{page["crawled_at"]}</lastmod>')

                    xml_parts.append("  </url>")

            xml_parts.append("</urlset>")

            return "\n".join(xml_parts)

        except Exception as e:
            logger.error(f"Failed to generate sitemap XML: {e}")
            return f"<!-- Error generating sitemap: {e} -->"

    def _is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid for crawling.

        Args:
            url: URL to check

        Returns:
            True if URL is valid
        """
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False

    async def _test_crawler_connectivity(self) -> Dict[str, Any]:
        """
        Test crawler connectivity.

        Returns:
            Test results
        """
        try:
            # Test with a simple HTTP request
            test_url = "https://httpbin.org/get"

            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={"User-Agent": self.user_agent},
                )

            async with self.session.get(test_url) as response:
                if response.status == 200:
                    return {"success": True}
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def shutdown(self) -> None:
        """Shutdown the crawler service."""
        await super().shutdown()

        # Close session
        if self.session:
            await self.session.close()
            self.session = None

        # Clear state
        self.visited_urls.clear()
        self.url_queue.clear()

        logger.info("Crawler service shutdown complete")
