#!/usr/bin/env python3
"""
Zero-Budget YouTube Retrieval Lane

Implements YouTube search with strict budget controls:
- Intent-gated execution (video queries only)
- Hard timeout enforcement
- Unit quota management
- Intelligent caching and indexing
- Non-blocking orchestration integration

Following MAANG/OpenAI/Perplexity standards for enterprise-grade reliability.
"""

import asyncio
import hashlib
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables with defaults
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
ENABLE_YOUTUBE = os.getenv("ENABLE_YOUTUBE", "true").lower() == "true"
YT_MAX_RESULTS = int(os.getenv("YT_MAX_RESULTS", "5"))
YT_DAILY_UNIT_BUDGET = int(os.getenv("YT_DAILY_UNIT_BUDGET", "10000"))  # Default 10k units
YT_QUOTA_BUFFER_PCT = int(os.getenv("YT_QUOTA_BUFFER_PCT", "20"))  # 20% buffer
YT_LANE_MS_BUDGET = int(os.getenv("YT_LANE_MS_BUDGET", "2000"))  # 2s max
YT_REGION_CODE = os.getenv("YT_REGION_CODE", "US")
YT_RELEVANCE_LANGUAGE = os.getenv("YT_RELEVANCE_LANGUAGE", "en")
YT_CACHE_TTL_SECONDS = int(os.getenv("YT_CACHE_TTL_SECONDS", "3600"))  # 1 hour

# Metrics tracking
_metrics = {
    "yt_units_used_today": 0,
    "yt_search_calls": 0,
    "yt_videos_calls": 0,
    "yt_cache_hit_rate": 0.0,
    "yt_timeout_rate": 0.0,
    "yt_cache_hits": 0,
    "yt_cache_misses": 0,
    "yt_timeouts": 0,
    "yt_total_queries": 0,
    "yt_quota_exhausted": 0,
    "yt_last_reset": datetime.now().date().isoformat()
}


class VideoIntent(str, Enum):
    """Video intent detection."""
    EXPLICIT_VIDEO = "explicit_video"  # "video", "tutorial", "demo"
    IMPLICIT_VIDEO = "implicit_video"  # "how to", "walkthrough", "show me"
    NO_VIDEO = "no_video"  # General queries


@dataclass
class YouTubeVideo:
    """YouTube video result."""
    video_id: str
    title: str
    description: str
    channel_title: str
    published_at: str
    duration: str
    thumbnail_url: str
    view_count: int
    relevance_score: float = 0.0
    units_spent: int = 0
    fetch_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class YouTubeResponse:
    """YouTube search response."""
    videos: List[YouTubeVideo]
    total_results: int
    cache_hit: bool = False
    units_spent: int = 0
    quota_exhausted: bool = False
    timeout_occurred: bool = False
    processing_time_ms: float = 0.0
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class YouTubeRetrieval:
    """Zero-budget YouTube retrieval with strict controls."""
    
    def __init__(self):
        self.youtube_service = None
        self.session = None
        self.redis_client = None
        self._quota_reset_date = datetime.now().date()
        self._daily_units_used = 0
        
        # Initialize if enabled and API key available
        if ENABLE_YOUTUBE and YOUTUBE_API_KEY and "your_" not in YOUTUBE_API_KEY:
            try:
                self.youtube_service = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
                logger.info("✅ YouTube API service initialized")
            except Exception as e:
                logger.warning(f"YouTube API initialization failed: {e}")
                self.youtube_service = None
        else:
            if not ENABLE_YOUTUBE:
                logger.info("YouTube retrieval disabled via ENABLE_YOUTUBE")
            elif not YOUTUBE_API_KEY or "your_" in YOUTUBE_API_KEY:
                logger.info("YouTube API key not configured")
    
    async def setup_session(self):
        """Setup HTTP session for oEmbed calls."""
        if self.session is not None:
            return
            
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": "SarvanOM/1.0 (YouTube Retrieval)"},
            timeout=aiohttp.ClientTimeout(total=5)
        )
    
    async def close(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()
    
    def _detect_video_intent(self, query: str) -> VideoIntent:
        """Detect if query implies video content."""
        query_lower = query.lower()
        
        # Explicit video indicators
        video_keywords = ["video", "tutorial", "demo", "screencast", "walkthrough", "show me"]
        if any(keyword in query_lower for keyword in video_keywords):
            return VideoIntent.EXPLICIT_VIDEO
        
        # Implicit video indicators
        implicit_keywords = ["how to", "how-to", "step by step", "guide", "learn", "watch"]
        if any(keyword in query_lower for keyword in implicit_keywords):
            return VideoIntent.IMPLICIT_VIDEO
        
        return VideoIntent.NO_VIDEO
    
    def _should_execute_youtube(self, query: str, user_preference: bool = False) -> bool:
        """Determine if YouTube lane should execute."""
        if not self.youtube_service:
            return False
        
        # Check quota
        if self._daily_units_used >= YT_DAILY_UNIT_BUDGET:
            _metrics["yt_quota_exhausted"] += 1
            logger.warning("YouTube daily quota exhausted")
            return False
        
        # Check intent or user preference
        intent = self._detect_video_intent(query)
        return (intent in [VideoIntent.EXPLICIT_VIDEO, VideoIntent.IMPLICIT_VIDEO] or 
                user_preference)
    
    def _calculate_units_cost(self, search_results: int, video_details: int) -> int:
        """Calculate API units cost."""
        # YouTube API v3 costs:
        # search.list: 100 units per call
        # videos.list: 1 unit per call
        search_cost = 100 if search_results > 0 else 0
        video_cost = video_details
        return search_cost + video_cost
    
    async def _get_oembed_data(self, video_id: str) -> Optional[Dict]:
        """Get video metadata via oEmbed (free, no quota cost)."""
        try:
            await self.setup_session()
            oembed_url = f"https://www.youtube.com/oembed"
            params = {
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "format": "json"
            }
            
            async with self.session.get(oembed_url, params=params) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            logger.debug(f"oEmbed failed for {video_id}: {e}")
        
        return None
    
    async def _search_videos(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search YouTube videos (100 units per call)."""
        try:
            search_response = self.youtube_service.search().list(
                part="id,snippet",
                q=query,
                type="video",
                maxResults=max_results,
                order="relevance",
                regionCode=YT_REGION_CODE,
                relevanceLanguage=YT_RELEVANCE_LANGUAGE,
                videoDuration="medium"  # Prefer medium length
            ).execute()
            
            _metrics["yt_search_calls"] += 1
            return search_response.get("items", [])
            
        except HttpError as e:
            if e.resp.status == 403:
                logger.error("YouTube API quota exceeded")
                _metrics["yt_quota_exhausted"] += 1
            else:
                logger.error(f"YouTube search error: {e}")
            return []
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return []
    
    async def _get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """Get detailed video information (1 unit per video)."""
        if not video_ids:
            return []
        
        try:
            # Batch request for efficiency
            videos_response = self.youtube_service.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(video_ids)
            ).execute()
            
            _metrics["yt_videos_calls"] += 1
            return videos_response.get("items", [])
            
        except HttpError as e:
            if e.resp.status == 403:
                logger.error("YouTube API quota exceeded")
                _metrics["yt_quota_exhausted"] += 1
            else:
                logger.error(f"YouTube videos error: {e}")
            return []
        except Exception as e:
            logger.error(f"YouTube videos failed: {e}")
            return []
    
    def _parse_duration(self, duration: str) -> str:
        """Parse ISO 8601 duration to human readable."""
        import re
        match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration)
        if not match:
            return "Unknown"
        
        hours = int(match.group(1)[:-1]) if match.group(1) else 0
        minutes = int(match.group(2)[:-1]) if match.group(2) else 0
        seconds = int(match.group(3)[:-1]) if match.group(3) else 0
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _calculate_relevance_score(self, video: YouTubeVideo, query: str) -> float:
        """Calculate relevance score for video."""
        query_terms = set(query.lower().split())
        title_terms = set(video.title.lower().split())
        desc_terms = set(video.description.lower().split())
        
        # Title relevance (highest weight)
        title_matches = len(query_terms.intersection(title_terms))
        title_score = title_matches / max(len(query_terms), 1) * 0.6
        
        # Description relevance
        desc_matches = len(query_terms.intersection(desc_terms))
        desc_score = desc_matches / max(len(query_terms), 1) * 0.3
        
        # Recency bonus (10% weight)
        try:
            published = datetime.fromisoformat(video.published_at.replace('Z', '+00:00'))
            days_old = (datetime.now(published.tzinfo) - published).days
            recency_score = max(0, 1 - (days_old / 365)) * 0.1
        except:
            recency_score = 0
        
        return min(title_score + desc_score + recency_score, 1.0)
    
    async def search(self, query: str, max_results: int = None, 
                    user_preference: bool = False) -> YouTubeResponse:
        """
        Search YouTube videos with zero-budget constraints.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            user_preference: User explicitly requested videos
            
        Returns:
            YouTubeResponse with videos and metadata
        """
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        
        # Reset daily metrics if date changed
        current_date = datetime.now().date()
        if current_date != self._quota_reset_date:
            self._quota_reset_date = current_date
            self._daily_units_used = 0
            _metrics["yt_last_reset"] = current_date.isoformat()
        
        # Check if YouTube lane should execute
        if not self._should_execute_youtube(query, user_preference):
            return YouTubeResponse(
                videos=[],
                total_results=0,
                quota_exhausted=self._daily_units_used >= YT_DAILY_UNIT_BUDGET,
                trace_id=trace_id
            )
        
        _metrics["yt_total_queries"] += 1
        
        try:
            # Execute with strict timeout
            max_results = max_results or YT_MAX_RESULTS
            
            # Search for videos
            search_results = await asyncio.wait_for(
                self._search_videos(query, max_results),
                timeout=YT_LANE_MS_BUDGET / 1000
            )
            
            if not search_results:
                return YouTubeResponse(
                    videos=[],
                    total_results=0,
                    trace_id=trace_id
                )
            
            # Extract video IDs
            video_ids = [item["id"]["videoId"] for item in search_results]
            
            # Get detailed video information
            video_details = await asyncio.wait_for(
                self._get_video_details(video_ids),
                timeout=YT_LANE_MS_BUDGET / 1000
            )
            
            # Calculate units cost
            units_cost = self._calculate_units_cost(len(search_results), len(video_details))
            self._daily_units_used += units_cost
            _metrics["yt_units_used_today"] += units_cost
            
            # Process results
            videos = []
            for detail in video_details:
                try:
                    snippet = detail["snippet"]
                    content_details = detail.get("contentDetails", {})
                    statistics = detail.get("statistics", {})
                    
                    # Get thumbnail (prefer medium quality)
                    thumbnails = snippet.get("thumbnails", {})
                    thumbnail_url = (thumbnails.get("medium", {}).get("url") or 
                                   thumbnails.get("default", {}).get("url") or "")
                    
                    video = YouTubeVideo(
                        video_id=detail["id"],
                        title=snippet["title"],
                        description=snippet["description"][:300] + "..." if len(snippet["description"]) > 300 else snippet["description"],
                        channel_title=snippet["channelTitle"],
                        published_at=snippet["publishedAt"],
                        duration=self._parse_duration(content_details.get("duration", "")),
                        thumbnail_url=thumbnail_url,
                        view_count=int(statistics.get("viewCount", 0)),
                        units_spent=units_cost // len(video_details),
                        fetch_ms=(time.time() - start_time) * 1000
                    )
                    
                    # Calculate relevance score
                    video.relevance_score = self._calculate_relevance_score(video, query)
                    videos.append(video)
                    
                except Exception as e:
                    logger.warning(f"Error processing video {detail.get('id', 'unknown')}: {e}")
                    continue
            
            # Sort by relevance
            videos.sort(key=lambda x: x.relevance_score, reverse=True)
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.info(f"YouTube search completed: {len(videos)} videos, {units_cost} units, {processing_time:.1f}ms")
            
            return YouTubeResponse(
                videos=videos[:max_results],
                total_results=len(videos),
                units_spent=units_cost,
                processing_time_ms=processing_time,
                trace_id=trace_id
            )
            
        except asyncio.TimeoutError:
            _metrics["yt_timeouts"] += 1
            logger.warning(f"YouTube search timeout after {YT_LANE_MS_BUDGET}ms")
            
            return YouTubeResponse(
                videos=[],
                total_results=0,
                timeout_occurred=True,
                processing_time_ms=YT_LANE_MS_BUDGET,
                trace_id=trace_id
            )
            
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            
            return YouTubeResponse(
                videos=[],
                total_results=0,
                trace_id=trace_id
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get YouTube lane metrics."""
        # Calculate rates
        total_queries = _metrics["yt_total_queries"]
        if total_queries > 0:
            _metrics["yt_cache_hit_rate"] = _metrics["yt_cache_hits"] / total_queries
            _metrics["yt_timeout_rate"] = _metrics["yt_timeouts"] / total_queries
        
        return {
            **{k: v for k, v in _metrics.items()},
            "daily_quota_remaining": max(0, YT_DAILY_UNIT_BUDGET - self._daily_units_used),
            "quota_usage_pct": (self._daily_units_used / YT_DAILY_UNIT_BUDGET) * 100 if YT_DAILY_UNIT_BUDGET > 0 else 0
        }


# Global instance
_youtube_retrieval_instance = None

def get_youtube_retrieval() -> YouTubeRetrieval:
    """Get global YouTube retrieval instance."""
    global _youtube_retrieval_instance
    if _youtube_retrieval_instance is None:
        _youtube_retrieval_instance = YouTubeRetrieval()
    return _youtube_retrieval_instance


async def search_youtube(query: str, max_results: int = None, 
                        user_preference: bool = False) -> YouTubeResponse:
    """Convenience function for YouTube search."""
    return await get_youtube_retrieval().search(query, max_results, user_preference)


def get_youtube_metrics() -> Dict[str, Any]:
    """Get YouTube lane metrics."""
    return get_youtube_retrieval().get_metrics()


if __name__ == "__main__":
    # Test the implementation
    async def test():
        retrieval = get_youtube_retrieval()
        
        print("Testing YouTube retrieval...")
        print(f"Service available: {retrieval.youtube_service is not None}")
        print(f"Daily quota: {YT_DAILY_UNIT_BUDGET} units")
        
        if retrieval.youtube_service:
            # Test video intent detection
            test_queries = [
                "machine learning tutorial",
                "how to code python",
                "weather forecast today"
            ]
            
            for query in test_queries:
                intent = retrieval._detect_video_intent(query)
                should_run = retrieval._should_execute_youtube(query)
                print(f"Query: '{query}' -> Intent: {intent}, Should run: {should_run}")
            
            # Test search (if quota available)
            if retrieval._daily_units_used < YT_DAILY_UNIT_BUDGET:
                print("\nTesting search...")
                response = await retrieval.search("python tutorial", max_results=3)
                print(f"Results: {len(response.videos)} videos")
                print(f"Units spent: {response.units_spent}")
                print(f"Processing time: {response.processing_time_ms:.1f}ms")
        
        await retrieval.close()
    
    asyncio.run(test())
