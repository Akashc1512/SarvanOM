#!/usr/bin/env python3
"""
Streaming Manager for Server-Sent Events (SSE)

Provides SSE streaming capabilities with:
- Content chunk streaming per token
- Heartbeat monitoring every 10 seconds
- Graceful client disconnect handling
- Stream duration capping
- Comprehensive logging and tracing

Following MAANG/OpenAI/Perplexity standards for enterprise-grade streaming.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import os

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

# Import observability functions
from services.gateway.middleware.observability import (
    log_stream_event,
    log_error,
    monitor_performance
)

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
STREAM_MAX_SECONDS = int(os.getenv("STREAM_MAX_SECONDS", "60"))
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "10"))
CHUNK_DELAY_MS = int(os.getenv("CHUNK_DELAY_MS", "50"))


class StreamEventType(str, Enum):
    """SSE event types."""
    CONTENT_CHUNK = "content_chunk"
    HEARTBEAT = "heartbeat"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class StreamEvent:
    """SSE event structure."""
    event_type: StreamEventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    trace_id: Optional[str] = None


@dataclass
class StreamContext:
    """Stream context for tracking and management."""
    stream_id: str
    trace_id: str
    query: str
    start_time: datetime
    client_connected: bool = True
    total_chunks: int = 0
    total_tokens: int = 0
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


class StreamingManager:
    """Manages SSE streaming with lifecycle and monitoring."""
    
    def __init__(self):
        self.active_streams: Dict[str, StreamContext] = {}
        self.heartbeat_task: Optional[asyncio.Task] = None
        self._shutdown = False
    
    async def initialize(self):
        """Initialize the streaming manager."""
        logger.info("Initializing streaming manager")
        self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        logger.info("✅ Streaming manager initialized")
    
    async def close(self):
        """Cleanup streaming manager."""
        logger.info("Shutting down streaming manager")
        self._shutdown = True
        
        # Cancel heartbeat task
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close all active streams
        for stream_id in list(self.active_streams.keys()):
            await self._close_stream(stream_id)
        
        logger.info("✅ Streaming manager shutdown complete")
    
    def _generate_stream_id(self) -> str:
        """Generate unique stream ID."""
        return f"stream_{uuid.uuid4().hex[:8]}"
    
    def _generate_trace_id(self) -> str:
        """Generate unique trace ID."""
        return f"trace_{uuid.uuid4().hex[:16]}"
    
    def _format_sse_event(self, event: StreamEvent) -> str:
        """Format event as SSE message."""
        lines = [
            f"event: {event.event_type.value}",
            f"data: {json.dumps(event.data, ensure_ascii=False)}",
            f"id: {event.trace_id or 'unknown'}",
            f"timestamp: {event.timestamp.isoformat()}",
            "",  # Empty line to end event
        ]
        return "\n".join(lines)
    
    async def _heartbeat_monitor(self):
        """Monitor and send heartbeats to active streams."""
        while not self._shutdown:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Send heartbeats to active streams
                for stream_id, context in list(self.active_streams.items()):
                    if not context.client_connected:
                        continue
                    
                    time_since_heartbeat = (current_time - context.last_heartbeat).total_seconds()
                    
                    if time_since_heartbeat >= HEARTBEAT_INTERVAL:
                        await self._send_heartbeat(stream_id, context)
                        context.last_heartbeat = current_time
                
                await asyncio.sleep(1)  # Check every second
                
            except asyncio.CancelledError:
                logger.info("Heartbeat monitor cancelled")
                break
            except Exception as e:
                log_error("heartbeat_monitor_error", str(e))
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _send_heartbeat(self, stream_id: str, context: StreamContext):
        """Send heartbeat event to stream."""
        try:
            heartbeat_event = StreamEvent(
                event_type=StreamEventType.HEARTBEAT,
                data={
                    "stream_id": stream_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "uptime_seconds": (datetime.now(timezone.utc) - context.start_time).total_seconds(),
                    "total_chunks": context.total_chunks,
                    "total_tokens": context.total_tokens
                },
                trace_id=context.trace_id
            )
            
            # Log heartbeat with observability
            log_stream_event("heartbeat", stream_id, {
                "trace_id": context.trace_id,
                "query": context.query[:100],  # Truncate for logging
                "uptime_seconds": (datetime.now(timezone.utc) - context.start_time).total_seconds(),
                "total_chunks": context.total_chunks,
                "total_tokens": context.total_tokens
            })
            
        except Exception as e:
            log_error("heartbeat_failed", str(e), {
                "stream_id": stream_id,
                "trace_id": context.trace_id
            })
    
    async def _close_stream(self, stream_id: str):
        """Close a specific stream."""
        if stream_id in self.active_streams:
            context = self.active_streams[stream_id]
            context.client_connected = False
            
            duration = (datetime.now(timezone.utc) - context.start_time).total_seconds()
            
            logger.info(f"Stream closed: {stream_id}", extra={
                "stream_id": stream_id,
                "trace_id": context.trace_id,
                "duration_seconds": duration,
                "total_chunks": context.total_chunks,
                "total_tokens": context.total_tokens,
                "query": context.query
            })
            
            del self.active_streams[stream_id]
    
    async def create_search_stream(
        self, 
        query: str, 
        max_tokens: int = 1000,
        temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        """
        Create a streaming search response with comprehensive lifecycle management.
        
        Args:
            query: Search query
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            
        Yields:
            SSE formatted events
        """
        stream_id = self._generate_stream_id()
        trace_id = self._generate_trace_id()
        start_time = datetime.now(timezone.utc)
        
        # Create stream context
        context = StreamContext(
            stream_id=stream_id,
            trace_id=trace_id,
            query=query,
            start_time=start_time,
            metadata={
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        )
        
        self.active_streams[stream_id] = context
        
        logger.info(f"Stream started: {stream_id}", extra={
            "stream_id": stream_id,
            "trace_id": trace_id,
            "query": query[:100],
            "max_tokens": max_tokens,
            "temperature": temperature
        })
        
        try:
            # Check stream duration limit
            if (datetime.now(timezone.utc) - start_time).total_seconds() > STREAM_MAX_SECONDS:
                logger.warning(f"Stream duration limit exceeded: {stream_id}")
                context.client_connected = False
                return
            
            # First, get retrieval results
            from services.retrieval.free_tier import get_zero_budget_retrieval
            retrieval_system = get_zero_budget_retrieval()
            
            # Get search results
            retrieval_response = await retrieval_system.search(query, k=10)
            
            # Convert to context for LLM
            retrieval_context = []
            for result in retrieval_response.results:
                retrieval_context.append({
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.snippet,
                    "domain": result.domain,
                    "provider": result.provider.value
                })
            
            # Send context event with sources
            context_event = StreamEvent(
                event_type=StreamEventType.CONTENT_CHUNK,
                data={
                    "type": "context",
                    "stream_id": stream_id,
                    "sources": retrieval_context
                },
                trace_id=trace_id
            )
            
            yield self._format_sse_event(context_event)
            context.total_chunks += 1
            
            # Check if client is still connected
            if not context.client_connected:
                logger.info(f"Client disconnected before LLM generation: {stream_id}")
                return
            
            # Generate streaming response using LLM
            logger.info(f"Starting LLM generation for stream {stream_id}")
            
            # Use the LLM processor to generate streaming content
            from services.gateway.real_llm_integration import RealLLMProcessor
            llm_processor = RealLLMProcessor()
            
            llm_response = await llm_processor.call_llm_with_provider_gating(
                prompt=f"Based on the following search results, provide a comprehensive answer to: {query}\n\nSearch Results:\n{json.dumps(retrieval_context, indent=2)}",
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if llm_response.success:
                # Get the generated content
                content = llm_response.content
                
                # Now apply fact-checking and citations
                from services.gateway.citations import get_citations_manager
                citations_manager = get_citations_manager()
                
                # Convert retrieval results to SearchResult format for citations
                from services.retrieval.free_tier import SearchResult, SearchProvider
                search_results = []
                for i, result in enumerate(retrieval_response.results):
                    search_results.append(SearchResult(
                        title=result.title,
                        url=result.url,
                        snippet=result.snippet,
                        domain=result.domain,
                        provider=result.provider,
                        relevance_score=result.relevance_score,
                        credibility_score=getattr(result, 'credibility_score', 0.8)
                    ))
                
                # Apply fact-checking and citations
                fact_check_result = await citations_manager.fact_check_text(
                    text=content,
                    sources=search_results,
                    min_confidence=0.3
                )
                
                # Send citations event
                citations_event = StreamEvent(
                    event_type=StreamEventType.CONTENT_CHUNK,
                    data={
                        "type": "citations",
                        "stream_id": stream_id,
                        "citations": [
                            {
                                "marker": citation.marker,
                                "source": {
                                    "title": citation.source.title,
                                    "url": citation.source.url,
                                    "snippet": citation.source.snippet,
                                    "source_type": citation.source.provider.value,
                                    "relevance_score": citation.source.relevance_score,
                                    "credibility_score": citation.source.credibility_score,
                                    "domain": citation.source.domain,
                                    "provider": citation.source.provider.value
                                },
                                "confidence": citation.confidence,
                                "sentence_start": citation.sentence_start,
                                "sentence_end": citation.sentence_end,
                                "claim_type": citation.claim_type
                            }
                            for citation in fact_check_result.citations
                        ],
                        "bibliography": fact_check_result.bibliography,
                        "uncertainty_flags": fact_check_result.uncertainty_flags,
                        "overall_confidence": fact_check_result.overall_confidence
                    },
                    trace_id=trace_id
                )
                
                yield self._format_sse_event(citations_event)
                context.total_chunks += 1
                
                # Stream the fact-checked content with citations
                words = fact_check_result.text.split()
                chunk_size = max(1, len(words) // 20)  # Split into ~20 chunks
                
                for i in range(0, len(words), chunk_size):
                    # Check if client is still connected
                    if not context.client_connected:
                        logger.info(f"Client disconnected during streaming: {stream_id}")
                        break
                    
                    # Check stream duration limit
                    if (datetime.now(timezone.utc) - start_time).total_seconds() > STREAM_MAX_SECONDS:
                        logger.warning(f"Stream duration limit exceeded during generation: {stream_id}")
                        break
                    
                    chunk_words = words[i:i + chunk_size]
                    chunk_text = " ".join(chunk_words)
                    
                    chunk_event = StreamEvent(
                        event_type=StreamEventType.CONTENT_CHUNK,
                        data={
                            "type": "content",
                            "stream_id": stream_id,
                            "chunk_index": context.total_chunks,
                            "text": chunk_text,
                            "is_final": i + chunk_size >= len(words)
                        },
                        trace_id=trace_id
                    )
                    
                    yield self._format_sse_event(chunk_event)
                    context.total_chunks += 1
                    context.total_tokens += len(chunk_words)
                    
                    # Small delay between chunks for realistic streaming
                    await asyncio.sleep(CHUNK_DELAY_MS / 1000)
                
                # Send complete event with enhanced data
                complete_event = StreamEvent(
                    event_type=StreamEventType.COMPLETE,
                    data={
                        "stream_id": stream_id,
                        "total_chunks": context.total_chunks,
                        "total_tokens": context.total_tokens,
                        "duration_seconds": (datetime.now(timezone.utc) - start_time).total_seconds(),
                        "sources": retrieval_context,
                        "citations": [
                            {
                                "marker": citation.marker,
                                "source": {
                                    "title": citation.source.title,
                                    "url": citation.source.url,
                                    "snippet": citation.source.snippet,
                                    "source_type": citation.source.provider.value,
                                    "relevance_score": citation.source.relevance_score,
                                    "credibility_score": citation.source.credibility_score,
                                    "domain": citation.source.domain,
                                    "provider": citation.source.provider.value
                                },
                                "confidence": citation.confidence,
                                "sentence_start": citation.sentence_start,
                                "sentence_end": citation.sentence_end,
                                "claim_type": citation.claim_type
                            }
                            for citation in fact_check_result.citations
                        ],
                        "bibliography": fact_check_result.bibliography,
                        "uncertainty_flags": fact_check_result.uncertainty_flags,
                        "overall_confidence": fact_check_result.overall_confidence
                    },
                    trace_id=trace_id
                )
                
                yield self._format_sse_event(complete_event)
                
            else:
                # Send error event
                error_event = StreamEvent(
                    event_type=StreamEventType.ERROR,
                    data={
                        "stream_id": stream_id,
                        "error": "LLM generation failed",
                        "error_message": llm_response.error_message or "Unknown error"
                    },
                    trace_id=trace_id
                )
                
                yield self._format_sse_event(error_event)
            
        except asyncio.CancelledError:
            logger.info(f"Stream cancelled by client: {stream_id}", extra={
                "stream_id": stream_id,
                "trace_id": trace_id,
                "duration_seconds": (datetime.now(timezone.utc) - start_time).total_seconds()
            })
            context.client_connected = False
            
        except Exception as e:
            logger.error(f"Stream error: {stream_id}", extra={
                "stream_id": stream_id,
                "trace_id": trace_id,
                "error": str(e),
                "duration_seconds": (datetime.now(timezone.utc) - start_time).total_seconds()
            })
            
            # Send error event
            error_event = StreamEvent(
                event_type=StreamEventType.ERROR,
                data={
                    "stream_id": stream_id,
                    "error": "Stream processing failed",
                    "error_message": str(e)
                },
                trace_id=trace_id
            )
            
            yield self._format_sse_event(error_event)
            
        finally:
            # Cleanup
            await self._close_stream(stream_id)
    
    def get_stream_stats(self) -> Dict[str, Any]:
        """Get streaming statistics."""
        active_count = len([s for s in self.active_streams.values() if s.client_connected])
        total_chunks = sum(s.total_chunks for s in self.active_streams.values())
        total_tokens = sum(s.total_tokens for s in self.active_streams.values())
        
        return {
            "active_streams": active_count,
            "total_streams": len(self.active_streams),
            "total_chunks_sent": total_chunks,
            "total_tokens_sent": total_tokens,
            "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds() if hasattr(self, 'start_time') else 0
        }


# Global streaming manager instance
streaming_manager = StreamingManager()


async def create_sse_response(
    query: str,
    max_tokens: int = 1000,
    temperature: float = 0.2
) -> StreamingResponse:
    """
    Create SSE streaming response for search.
    
    Args:
        query: Search query
        max_tokens: Maximum tokens to generate
        temperature: Generation temperature
        
    Returns:
        StreamingResponse with SSE headers
    """
    async def event_generator():
        async for event in streaming_manager.create_search_stream(
            query=query,
            max_tokens=max_tokens,
            temperature=temperature
        ):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "X-Stream-Type": "search",
            "X-Stream-Max-Seconds": str(STREAM_MAX_SECONDS),
            "X-Heartbeat-Interval": str(HEARTBEAT_INTERVAL)
        }
    )
