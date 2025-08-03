"""
Crawler Service
Handles web crawling and content extraction functionality.

This service provides:
- Web page crawling
- Content extraction and parsing
- Link discovery and following
- Rate limiting and politeness
"""

from .web_crawler import WebCrawler

__all__ = [
    "WebCrawler"
] 