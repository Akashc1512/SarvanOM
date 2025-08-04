# DEAD CODE - Candidate for deletion: This backend directory is not used by the main application
"""
Crawler Service

This service handles web crawling and data collection operations including:
- Web page crawling and scraping
- Data extraction and parsing
- Content discovery and indexing
- Rate limiting and politeness
- Data quality assessment
"""

from .crawler_service import CrawlerService

__all__ = ["CrawlerService"] 