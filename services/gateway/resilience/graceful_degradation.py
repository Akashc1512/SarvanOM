#!/usr/bin/env python3
"""
Graceful Degradation System

Provides graceful degradation capabilities for:
- Retrieval-only fallback when LLM providers are unavailable
- Intelligent source summarization without LLM
- Fallback response generation with traceable errors
- Circuit breaker integration for automatic degradation
- User-friendly error messages with trace IDs

Following enterprise resilience patterns for high-availability systems.
"""

import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import re

from services.gateway.middleware.observability import (
    log_error,
    get_request_id,
    get_user_id
)

from services.gateway.resilience.circuit_breaker import (
    circuit_breaker_manager,
    CircuitBreakerError
)

logger = logging.getLogger(__name__)


class DegradationLevel(str, Enum):
    """Degradation levels for system resilience."""
    FULL = "full"                    # All services available
    LLM_DEGRADED = "llm_degraded"    # LLM unavailable, retrieval only
    RETRIEVAL_DEGRADED = "retrieval_degraded"  # Limited retrieval
    EMERGENCY = "emergency"          # Minimal functionality


@dataclass
class FallbackResponse:
    """Fallback response when LLM is unavailable."""
    answer: str
    sources: List[Dict[str, Any]]
    provider: str = "fallback_free_tier"
    confidence: float = 0.5
    degradation_level: DegradationLevel = DegradationLevel.LLM_DEGRADED
    trace_id: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class GracefulDegradationManager:
    """Manages graceful degradation and fallback responses."""
    
    def __init__(self):
        self.degradation_level = DegradationLevel.FULL
        self.fallback_templates = self._load_fallback_templates()
        self._lock = asyncio.Lock()
    
    def _load_fallback_templates(self) -> Dict[str, str]:
        """Load fallback response templates."""
        return {
            "general": """
Based on the available sources, here's what I found about your query:

{summary}

**Sources consulted:**
{source_list}

**Note:** This response was generated from retrieved sources only, as AI synthesis is currently unavailable. For more detailed analysis, please try again later.

**Trace ID:** {trace_id}
""",
            "technical": """
Here's the technical information I found:

{summary}

**Key sources:**
{source_list}

**Technical details:**
- {technical_points}

**Note:** This is a retrieval-only response. AI analysis is temporarily unavailable.

**Trace ID:** {trace_id}
""",
            "error": """
I found some information, but couldn't provide a complete answer:

{summary}

**Available sources:**
{source_list}

**Issue:** {error_message}

**Trace ID:** {trace_id}
**Support:** If this issue persists, please contact support with the trace ID above.
"""
        }
    
    async def check_system_health(self) -> DegradationLevel:
        """Check current system health and determine degradation level."""
        async with self._lock:
            # Check circuit breakers for LLM providers
            llm_providers = ["openai", "anthropic", "ollama", "huggingface"]
            available_llm_providers = 0
            
            for provider in llm_providers:
                try:
                    circuit_breaker = circuit_breaker_manager.get_circuit_breaker(provider)
                    if circuit_breaker.state.value != "open":
                        available_llm_providers += 1
                except Exception:
                    continue
            
            # Determine degradation level
            if available_llm_providers > 0:
                self.degradation_level = DegradationLevel.FULL
            else:
                self.degradation_level = DegradationLevel.LLM_DEGRADED
            
            return self.degradation_level
    
    async def generate_fallback_response(
        self,
        query: str,
        sources: List[Dict[str, Any]],
        error_message: Optional[str] = None
    ) -> FallbackResponse:
        """Generate a fallback response when LLM is unavailable."""
        trace_id = get_request_id() or str(uuid.uuid4())
        
        try:
            # Analyze sources and generate summary
            summary = await self._generate_source_summary(sources)
            source_list = self._format_source_list(sources)
            
            # Determine template based on query type
            template_key = self._determine_template_key(query)
            template = self.fallback_templates[template_key]
            
            # Generate response
            answer = template.format(
                summary=summary,
                source_list=source_list,
                technical_points=self._extract_technical_points(sources),
                error_message=error_message or "AI synthesis temporarily unavailable",
                trace_id=trace_id
            )
            
            # Log fallback generation
            log_error(
                "fallback_response_generated",
                f"Generated fallback response for query: {query[:100]}...",
                {
                    "query": query,
                    "trace_id": trace_id,
                    "user_id": get_user_id(),
                    "sources_count": len(sources),
                    "degradation_level": self.degradation_level.value,
                    "error_message": error_message
                }
            )
            
            return FallbackResponse(
                answer=answer.strip(),
                sources=sources,
                provider="fallback_free_tier",
                confidence=0.5,
                degradation_level=self.degradation_level,
                trace_id=trace_id,
                error_message=error_message,
                metadata={
                    "sources_count": len(sources),
                    "template_used": template_key,
                    "generation_method": "retrieval_only"
                }
            )
            
        except Exception as e:
            # Emergency fallback if even the fallback fails
            logger.error(f"Fallback generation failed: {e}")
            
            emergency_response = f"""
I'm experiencing technical difficulties and cannot provide a complete answer right now.

**Your query:** {query}

**Issue:** {error_message or "System temporarily unavailable"}

**Trace ID:** {trace_id}

Please try again in a few minutes, or contact support with the trace ID above if the issue persists.
"""
            
            return FallbackResponse(
                answer=emergency_response,
                sources=[],
                provider="fallback_free_tier",
                confidence=0.1,
                degradation_level=DegradationLevel.EMERGENCY,
                trace_id=trace_id,
                error_message=str(e),
                metadata={"emergency_fallback": True}
            )
    
    async def _generate_source_summary(self, sources: List[Dict[str, Any]]) -> str:
        """Generate a summary from available sources without LLM."""
        if not sources:
            return "No relevant sources were found for your query."
        
        # Extract key information from sources
        key_points = []
        domains = set()
        
        for source in sources:
            # Extract domain
            domain = source.get("domain", "unknown")
            domains.add(domain)
            
            # Extract title and snippet
            title = source.get("title", "")
            snippet = source.get("snippet", "")
            
            # Create a key point
            if title and snippet:
                # Truncate snippet for readability
                truncated_snippet = snippet[:200] + "..." if len(snippet) > 200 else snippet
                key_points.append(f"• **{title}** ({domain}): {truncated_snippet}")
        
        # Generate summary
        summary_parts = []
        
        if key_points:
            summary_parts.append("**Key findings:**")
            summary_parts.extend(key_points[:5])  # Limit to 5 key points
        
        if domains:
            summary_parts.append(f"\n**Sources consulted:** {len(domains)} different domains")
        
        return "\n".join(summary_parts)
    
    def _format_source_list(self, sources: List[Dict[str, Any]]) -> str:
        """Format source list for display."""
        if not sources:
            return "No sources available"
        
        formatted_sources = []
        for i, source in enumerate(sources[:10], 1):  # Limit to 10 sources
            title = source.get("title", "Untitled")
            url = source.get("url", "")
            domain = source.get("domain", "unknown")
            
            formatted_sources.append(f"{i}. [{title}]({url}) ({domain})")
        
        return "\n".join(formatted_sources)
    
    def _determine_template_key(self, query: str) -> str:
        """Determine which template to use based on query type."""
        query_lower = query.lower()
        
        # Technical keywords
        technical_keywords = [
            "error", "bug", "issue", "problem", "fix", "solution",
            "code", "programming", "development", "api", "sdk",
            "framework", "library", "database", "server", "client",
            "deployment", "configuration", "setup", "install"
        ]
        
        if any(keyword in query_lower for keyword in technical_keywords):
            return "technical"
        
        return "general"
    
    def _extract_technical_points(self, sources: List[Dict[str, Any]]) -> str:
        """Extract technical points from sources."""
        technical_points = []
        
        for source in sources:
            snippet = source.get("snippet", "")
            if snippet:
                # Look for technical patterns
                if any(pattern in snippet.lower() for pattern in [
                    "error", "exception", "bug", "fix", "solution",
                    "code", "function", "method", "class", "api"
                ]):
                    # Extract first sentence or key phrase
                    sentences = re.split(r'[.!?]', snippet)
                    if sentences:
                        technical_points.append(sentences[0].strip())
        
        # Limit to 3 technical points
        limited_points = technical_points[:3]
        return "\n- ".join(limited_points) if limited_points else "No specific technical details found"
    
    async def should_use_fallback(self, query: str) -> Tuple[bool, str]:
        """Determine if fallback should be used and why."""
        degradation_level = await self.check_system_health()
        
        if degradation_level == DegradationLevel.FULL:
            return False, "All services available"
        
        if degradation_level == DegradationLevel.LLM_DEGRADED:
            return True, "LLM providers unavailable, using retrieval-only fallback"
        
        if degradation_level == DegradationLevel.EMERGENCY:
            return True, "System in emergency mode"
        
        return False, "Unknown degradation level"
    
    def get_degradation_status(self) -> Dict[str, Any]:
        """Get current degradation status."""
        return {
            "degradation_level": self.degradation_level.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fallback_available": True,
            "templates_loaded": len(self.fallback_templates)
        }


class ErrorBoundary:
    """Error boundary for graceful error handling."""
    
    def __init__(self, degradation_manager: GracefulDegradationManager):
        self.degradation_manager = degradation_manager
    
    async def handle_llm_error(
        self,
        query: str,
        sources: List[Dict[str, Any]],
        error: Exception
    ) -> FallbackResponse:
        """Handle LLM errors with graceful degradation."""
        error_message = str(error)
        trace_id = get_request_id() or str(uuid.uuid4())
        
        # Log the error
        log_error(
            "llm_error_handled",
            f"LLM error handled with fallback: {error_message}",
            {
                "query": query,
                "trace_id": trace_id,
                "user_id": get_user_id(),
                "error_type": type(error).__name__,
                "error_message": error_message,
                "sources_count": len(sources)
            }
        )
        
        # Generate fallback response
        return await self.degradation_manager.generate_fallback_response(
            query=query,
            sources=sources,
            error_message=f"AI synthesis failed: {error_message}"
        )
    
    async def handle_retrieval_error(
        self,
        query: str,
        error: Exception
    ) -> FallbackResponse:
        """Handle retrieval errors with minimal fallback."""
        error_message = str(error)
        trace_id = get_request_id() or str(uuid.uuid4())
        
        # Log the error
        log_error(
            "retrieval_error_handled",
            f"Retrieval error handled: {error_message}",
            {
                "query": query,
                "trace_id": trace_id,
                "user_id": get_user_id(),
                "error_type": type(error).__name__,
                "error_message": error_message
            }
        )
        
        # Generate minimal fallback
        minimal_response = f"""
I'm unable to retrieve information for your query at the moment.

**Your query:** {query}

**Issue:** {error_message}

**Trace ID:** {trace_id}

Please try again in a few minutes, or contact support with the trace ID above if the issue persists.
"""
        
        return FallbackResponse(
            answer=minimal_response,
            sources=[],
            provider="fallback_free_tier",
            confidence=0.1,
            degradation_level=DegradationLevel.EMERGENCY,
            trace_id=trace_id,
            error_message=error_message,
            metadata={"emergency_fallback": True, "retrieval_failed": True}
        )


# Global instances
degradation_manager = GracefulDegradationManager()
error_boundary = ErrorBoundary(degradation_manager)


# Utility functions
async def get_fallback_response(
    query: str,
    sources: List[Dict[str, Any]],
    error: Optional[Exception] = None
) -> FallbackResponse:
    """Get fallback response for query."""
    if error:
        return await error_boundary.handle_llm_error(query, sources, error)
    else:
        return await degradation_manager.generate_fallback_response(query, sources)


async def check_fallback_needed(query: str) -> Tuple[bool, str]:
    """Check if fallback is needed for query."""
    return await degradation_manager.should_use_fallback(query)


def get_degradation_status() -> Dict[str, Any]:
    """Get current degradation status."""
    return degradation_manager.get_degradation_status()
