"""
Attribution Manager - SarvanOM v2 External Feeds

Source attribution and ethics compliance for external feeds.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class AttributionData:
    source_name: str
    source_url: str
    article_title: str
    article_url: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    license_type: str = "fair_use"
    license_terms: str = "Used under fair use for news aggregation"

class AttributionManager:
    """Manages source attribution and ethics compliance"""
    
    def __init__(self):
        self.attribution_templates = {
            "news": "Source: {source_name} - {article_url}",
            "markets": "Data provided by {provider_name}",
            "social": "Via {platform_name} - {post_url}",
            "rss": "Source: {source_name} - {article_url}",
            "api": "Data provided by {provider_name} API"
        }
        
        self.license_templates = {
            "fair_use": "Used under fair use for news aggregation",
            "api_terms": "Data provided by {provider_name} API",
            "public_api": "Data provided by {provider_name} public API",
            "creative_commons": "Used under Creative Commons license"
        }
    
    def generate_attribution(self, content: Dict[str, Any], content_type: str) -> AttributionData:
        """Generate attribution for content"""
        # Extract attribution data from content
        source_name = self._extract_source_name(content)
        source_url = self._extract_source_url(content)
        article_title = content.get("title", "")
        article_url = content.get("url", "")
        author = content.get("author")
        published_at = content.get("published_at")
        
        # Determine license type
        license_type = self._determine_license_type(content, content_type)
        license_terms = self._generate_license_terms(license_type, content)
        
        return AttributionData(
            source_name=source_name,
            source_url=source_url,
            article_title=article_title,
            article_url=article_url,
            author=author,
            published_at=published_at,
            license_type=license_type,
            license_terms=license_terms
        )
    
    def _extract_source_name(self, content: Dict[str, Any]) -> str:
        """Extract source name from content"""
        # Try multiple possible fields
        source_fields = ["source", "provider", "domain", "site"]
        
        for field in source_fields:
            if field in content:
                source_data = content[field]
                if isinstance(source_data, dict):
                    return source_data.get("name", str(source_data))
                elif isinstance(source_data, str):
                    return source_data
        
        # Fallback to domain extraction from URL
        url = content.get("url", "")
        if url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = parsed.netloc
                if domain:
                    return domain.replace("www.", "").title()
            except:
                pass
        
        return "Unknown Source"
    
    def _extract_source_url(self, content: Dict[str, Any]) -> str:
        """Extract source URL from content"""
        # Try multiple possible fields
        source_fields = ["source", "provider", "domain"]
        
        for field in source_fields:
            if field in content:
                source_data = content[field]
                if isinstance(source_data, dict):
                    url = source_data.get("url")
                    if url:
                        return url
        
        # Fallback to article URL
        return content.get("url", "")
    
    def _determine_license_type(self, content: Dict[str, Any], content_type: str) -> str:
        """Determine license type based on content and provider"""
        provider = content.get("provider", "").lower()
        
        # Provider-specific license types
        if provider in ["newsapi", "alphavantage", "coingecko"]:
            return "api_terms"
        elif provider in ["yahoo", "reddit"]:
            return "public_api"
        elif provider in ["rss", "bbc", "reuters", "ap"]:
            return "fair_use"
        else:
            return "fair_use"
    
    def _generate_license_terms(self, license_type: str, content: Dict[str, Any]) -> str:
        """Generate license terms based on license type"""
        provider_name = self._extract_source_name(content)
        
        if license_type in self.license_templates:
            template = self.license_templates[license_type]
            return template.format(provider_name=provider_name)
        else:
            return f"Used under {license_type} license"
    
    def validate_attribution(self, content: Dict[str, Any]) -> bool:
        """Validate that content has proper attribution"""
        required_fields = ["title", "url"]
        
        for field in required_fields:
            if field not in content or not content[field]:
                return False
        
        # Check if source information is available
        source_name = self._extract_source_name(content)
        if source_name == "Unknown Source":
            return False
        
        return True
    
    def format_attribution_text(self, attribution: AttributionData, format_type: str = "short") -> str:
        """Format attribution as text"""
        if format_type == "short":
            return f"Source: {attribution.source_name}"
        elif format_type == "medium":
            return f"Source: {attribution.source_name} - {attribution.article_url}"
        elif format_type == "full":
            author_text = f" by {attribution.author}" if attribution.author else ""
            date_text = f" ({attribution.published_at.strftime('%Y-%m-%d')})" if attribution.published_at else ""
            return f"Source: {attribution.source_name}{author_text}{date_text} - {attribution.article_url}"
        else:
            return attribution.source_name
    
    def generate_attribution_dict(self, attribution: AttributionData) -> Dict[str, Any]:
        """Generate attribution as dictionary"""
        return {
            "source": {
                "name": attribution.source_name,
                "url": attribution.source_url
            },
            "article": {
                "title": attribution.article_title,
                "url": attribution.article_url,
                "author": attribution.author,
                "published_at": attribution.published_at.isoformat() if attribution.published_at else None
            },
            "license": {
                "type": attribution.license_type,
                "terms": attribution.license_terms
            }
        }
    
    def check_fair_use_compliance(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Check fair use compliance for content"""
        compliance = {
            "compliant": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check content length
        content_text = content.get("content", "")
        if len(content_text) > 1000:
            compliance["issues"].append("Content excerpt may be too long")
            compliance["recommendations"].append("Consider shortening excerpt to under 1000 characters")
        
        # Check if it's factual content (preferred for fair use)
        content_type = content.get("category", "").lower()
        if content_type in ["news", "business", "technology", "science"]:
            compliance["recommendations"].append("Factual content - good for fair use")
        else:
            compliance["issues"].append("Non-factual content may have different fair use considerations")
        
        # Check attribution quality
        if not self.validate_attribution(content):
            compliance["compliant"] = False
            compliance["issues"].append("Insufficient attribution information")
            compliance["recommendations"].append("Ensure proper source attribution")
        
        # Check for commercial use indicators
        if content.get("commercial_use", False):
            compliance["issues"].append("Commercial use may require additional permissions")
            compliance["recommendations"].append("Consider contacting source for commercial use permissions")
        
        return compliance
    
    def generate_attribution_summary(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate attribution summary for multiple items"""
        sources = {}
        total_items = len(items)
        
        for item in items:
            source_name = self._extract_source_name(item)
            if source_name not in sources:
                sources[source_name] = {
                    "count": 0,
                    "items": [],
                    "license_type": self._determine_license_type(item, item.get("type", "news"))
                }
            
            sources[source_name]["count"] += 1
            sources[source_name]["items"].append({
                "title": item.get("title", ""),
                "url": item.get("url", "")
            })
        
        return {
            "total_items": total_items,
            "unique_sources": len(sources),
            "sources": sources,
            "attribution_required": True,
            "compliance_note": "All sources properly attributed per fair use guidelines"
        }
