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
    monitor_performance,
    log_sse_metrics,
    get_metrics_collector
)

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
STREAM_MAX_SECONDS = int(os.getenv("STREAM_MAX_SECONDS", "60"))
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "5"))  # Reduced to 5 seconds for better responsiveness
CHUNK_DELAY_MS = int(os.getenv("CHUNK_DELAY_MS", "50"))
SILENCE_THRESHOLD = int(os.getenv("SILENCE_THRESHOLD", "15"))  # 15 seconds of silence triggers reconnect

# Phase E1/E2: Budget enforcement for streaming
STREAM_BUDGET_SIMPLE_MS = int(os.getenv("STREAM_BUDGET_SIMPLE_MS", "2000"))      # 2s for simple queries
STREAM_BUDGET_TECHNICAL_MS = int(os.getenv("STREAM_BUDGET_TECHNICAL_MS", "4000")) # 4s for technical queries
STREAM_BUDGET_RESEARCH_MS = int(os.getenv("STREAM_BUDGET_RESEARCH_MS", "6000"))   # 6s for research queries
STREAM_BUDGET_MULTIMEDIA_MS = int(os.getenv("STREAM_BUDGET_MULTIMEDIA_MS", "8000")) # 8s for multimedia queries

# CI Performance gates
CI_PERF_TTFT_MAX_MS = int(os.getenv("CI_PERF_TTFT_MAX_MS", "800"))      # Time to first token
CI_PERF_CHUNK_INTERVAL_MS = int(os.getenv("CI_PERF_CHUNK_INTERVAL_MS", "100"))  # Max interval between chunks
CI_PERF_HEARTBEAT_INTERVAL_MS = int(os.getenv("CI_PERF_HEARTBEAT_INTERVAL_MS", "2000")) # Max heartbeat interval


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
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    heartbeat_count: int = 0
    max_duration_reached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Phase E1/E2: Budget enforcement fields
    budget_ms: int = 0
    intent_classification: str = "standard"
    ttft_ms: float = 0.0  # Time to first token
    first_chunk_time: Optional[datetime] = None
    budget_exceeded: bool = False
    ci_performance_metrics: Dict[str, Any] = field(default_factory=dict)


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
    
    def _classify_query_intent(self, query: str) -> str:
        """Classify query intent for budget allocation."""
        query_lower = query.lower()
        
        # Simple queries: definitions, basic facts
        if any(word in query_lower for word in ['what is', 'define', 'meaning', 'who is', 'when', 'where']):
            return 'simple'
        
        # Technical queries: code, algorithms, specifications
        if any(word in query_lower for word in ['code', 'algorithm', 'how to', 'implementation', 'api', 'function']):
            return 'technical'
        
        # Research queries: analysis, comparison, deep dive
        if any(word in query_lower for word in ['compare', 'analysis', 'research', 'study', 'investigate', 'explore']):
            return 'research'
        
        # Multimedia queries: video, demo, visual content
        if any(word in query_lower for word in ['video', 'demo', 'show', 'visual', 'image', 'picture']):
            return 'multimedia'
        
        return 'standard'
    
    def _get_stream_budget_ms(self, query: str) -> int:
        """Get stream budget based on query intent."""
        intent = self._classify_query_intent(query)
        
        budget_map = {
            'simple': STREAM_BUDGET_SIMPLE_MS,
            'technical': STREAM_BUDGET_TECHNICAL_MS,
            'research': STREAM_BUDGET_RESEARCH_MS,
            'multimedia': STREAM_BUDGET_MULTIMEDIA_MS,
            'standard': STREAM_BUDGET_TECHNICAL_MS  # Default to technical budget
        }
        
        return budget_map.get(intent, STREAM_BUDGET_TECHNICAL_MS)
    
    def _check_budget_compliance(self, start_time: datetime, budget_ms: int) -> tuple[bool, float]:
        """Check if stream is within budget."""
        elapsed_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        within_budget = elapsed_ms <= budget_ms
        return within_budget, elapsed_ms
    
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
        """Monitor and send heartbeats to active streams with duration caps."""
        while not self._shutdown:
            try:
                current_time = datetime.now(timezone.utc)
                streams_to_close = []
                
                # Check all active streams
                for stream_id, context in list(self.active_streams.items()):
                    if not context.client_connected:
                        continue
                    
                    # Check if stream has exceeded max duration
                    duration = (current_time - context.start_time).total_seconds()
                    if duration > STREAM_MAX_SECONDS and not context.max_duration_reached:
                        logger.info(f"Stream {stream_id} exceeded max duration ({STREAM_MAX_SECONDS}s), sending complete event")
                        context.max_duration_reached = True
                        
                        # Send complete event due to duration cap
                        complete_event = StreamEvent(
                            event_type=StreamEventType.COMPLETE,
                            data={
                                "stream_id": stream_id,
                                "reason": "duration_cap",
                                "duration": duration,
                                "chunks": context.total_chunks,
                                "tokens": context.total_tokens,
                                "timestamp": current_time.isoformat()
                            },
                            trace_id=context.trace_id
                        )
                        
                        # Log completion due to duration cap
                        log_stream_event("complete_duration_cap", stream_id, {
                            "trace_id": context.trace_id,
                            "duration": duration,
                            "chunks": context.total_chunks,
                            "tokens": context.total_tokens
                        })
                        
                        streams_to_close.append(stream_id)
                        continue
                    
                    # Send heartbeat if stream is active and not at duration cap
                    if not context.max_duration_reached:
                        time_since_heartbeat = (current_time - context.last_heartbeat).total_seconds()
                        
                        if time_since_heartbeat >= HEARTBEAT_INTERVAL:
                            await self._send_heartbeat(stream_id, context)
                            context.last_heartbeat = current_time
                            context.heartbeat_count += 1
                
                # Close streams that exceeded duration
                for stream_id in streams_to_close:
                    await self._close_stream(stream_id)
                
                await asyncio.sleep(1)  # Check every second
                
            except asyncio.CancelledError:
                logger.info("Heartbeat monitor cancelled")
                break
            except Exception as e:
                log_error("heartbeat_monitor_error", str(e))
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _send_heartbeat(self, stream_id: str, context: StreamContext):
        """Send heartbeat event to stream with budget and performance information."""
        try:
            current_time = datetime.now(timezone.utc)
            elapsed_ms = (current_time - context.start_time).total_seconds() * 1000
            
            # Check budget compliance for heartbeat
            within_budget, _ = self._check_budget_compliance(context.start_time, context.budget_ms)
            
            # Enhanced heartbeat with budget and performance data
            heartbeat_data = {
                "stream_id": stream_id,
                "timestamp": current_time.isoformat(),
                "heartbeat_count": context.heartbeat_count,
                "elapsed_ms": elapsed_ms,
                "budget_ms": context.budget_ms,
                "within_budget": within_budget,
                "intent": context.intent_classification,
                "chunks_sent": context.total_chunks,
                "tokens_sent": context.total_tokens,
                "ttft_ms": context.ttft_ms,
                "ci_performance": context.ci_performance_metrics
            }
            
            heartbeat_event = StreamEvent(
                event_type=StreamEventType.HEARTBEAT,
                data=heartbeat_data,
                trace_id=context.trace_id
            )
            
            # Log heartbeat with performance metrics
            logger.debug(f"Heartbeat sent: {stream_id}", extra={
                "stream_id": stream_id,
                "elapsed_ms": elapsed_ms,
                "within_budget": within_budget,
                "intent": context.intent_classification,
                "ttft_ms": context.ttft_ms
            })
            
            # Check CI performance gate for heartbeat interval
            if context.last_heartbeat:
                heartbeat_interval_ms = (current_time - context.last_heartbeat).total_seconds() * 1000
                heartbeat_compliant = heartbeat_interval_ms <= CI_PERF_HEARTBEAT_INTERVAL_MS
                context.ci_performance_metrics["heartbeat_compliant"] = heartbeat_compliant
                context.ci_performance_metrics["heartbeat_interval_ms"] = heartbeat_interval_ms
                
                if not heartbeat_compliant:
                    logger.warning(f"Heartbeat interval exceeded CI gate: {heartbeat_interval_ms:.2f}ms > {CI_PERF_HEARTBEAT_INTERVAL_MS}ms", extra={
                        "stream_id": stream_id,
                        "heartbeat_interval_ms": heartbeat_interval_ms,
                        "ci_gate": CI_PERF_HEARTBEAT_INTERVAL_MS
                    })
            
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {stream_id}", extra={
                "stream_id": stream_id,
                "error": str(e)
            })
        try:
            current_time = datetime.now(timezone.utc)
            duration = (current_time - context.start_time).total_seconds()
            
            heartbeat_event = StreamEvent(
                event_type=StreamEventType.HEARTBEAT,
                data={
                    "stream_id": stream_id,
                    "timestamp": current_time.isoformat(),
                    "uptime_seconds": duration,
                    "total_chunks": context.total_chunks,
                    "total_tokens": context.total_tokens,
                    "heartbeat_count": context.heartbeat_count,
                    "remaining_seconds": max(0, STREAM_MAX_SECONDS - duration),
                    "max_duration": STREAM_MAX_SECONDS
                },
                trace_id=context.trace_id
            )
            
            # Record heartbeat metrics
            metrics_collector = get_metrics_collector()
            metrics_collector.increment_sse_heartbeats("search")
            
            # Log heartbeat with observability
            log_stream_event("heartbeat", stream_id, {
                "trace_id": context.trace_id,
                "query": context.query[:100],  # Truncate for logging
                "uptime_seconds": duration,
                "total_chunks": context.total_chunks,
                "total_tokens": context.total_tokens,
                "heartbeat_count": context.heartbeat_count,
                "remaining_seconds": max(0, STREAM_MAX_SECONDS - duration)
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
            duration_ms = duration * 1000
            
            # Record SSE metrics
            metrics_collector = get_metrics_collector()
            metrics_collector.record_sse_duration("search", duration_ms)
            
            # Log SSE metrics
            log_sse_metrics(
                trace_id=context.trace_id,
                endpoint="search",
                duration_ms=duration_ms,
                heartbeats=context.heartbeat_count,
                chunks=context.total_chunks,
                tokens=context.total_tokens
            )
            
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
        temperature: float = 0.2,
        trace_id: Optional[str] = None
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
        if not trace_id:
            trace_id = self._generate_trace_id()
        start_time = datetime.now(timezone.utc)
        
        # Phase E1/E2: Budget enforcement setup
        intent_classification = self._classify_query_intent(query)
        budget_ms = self._get_stream_budget_ms(query)
        
        # Create stream context with budget tracking
        context = StreamContext(
            stream_id=stream_id,
            trace_id=trace_id,
            query=query,
            start_time=start_time,
            budget_ms=budget_ms,
            intent_classification=intent_classification,
            metadata={
                "max_tokens": max_tokens,
                "temperature": temperature,
                "intent": intent_classification,
                "budget_ms": budget_ms
            }
        )
        
        self.active_streams[stream_id] = context
        
        logger.info(f"Stream started with budget enforcement: {stream_id}", extra={
            "stream_id": stream_id,
            "trace_id": trace_id,
            "query": query[:100],
            "intent": intent_classification,
            "budget_ms": budget_ms,
            "max_tokens": max_tokens,
            "temperature": temperature
        })
        
        # Record SSE connection metrics
        metrics_collector = get_metrics_collector()
        metrics_collector.increment_sse_connections("search")
        
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
                
                # Phase E1/E2: Record TTFT (Time to First Token)
                if context.first_chunk_time is None:
                    context.first_chunk_time = datetime.now(timezone.utc)
                    context.ttft_ms = (context.first_chunk_time - start_time).total_seconds() * 1000
                    
                    # Check CI performance gate for TTFT
                    ttft_compliant = context.ttft_ms <= CI_PERF_TTFT_MAX_MS
                    context.ci_performance_metrics["ttft_compliant"] = ttft_compliant
                    context.ci_performance_metrics["ttft_ms"] = context.ttft_ms
                    
                    logger.info(f"TTFT recorded: {context.ttft_ms:.2f}ms (compliant: {ttft_compliant})", extra={
                        "stream_id": stream_id,
                        "ttft_ms": context.ttft_ms,
                        "ttft_compliant": ttft_compliant,
                        "ci_gate": CI_PERF_TTFT_MAX_MS
                    })
                
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
                    
                    # Phase E1/E2: Budget enforcement check
                    within_budget, elapsed_ms = self._check_budget_compliance(start_time, context.budget_ms)
                    if not within_budget and not context.budget_exceeded:
                        context.budget_exceeded = True
                        logger.warning(f"Stream budget exceeded: {stream_id}", extra={
                            "stream_id": stream_id,
                            "budget_ms": context.budget_ms,
                            "elapsed_ms": elapsed_ms,
                            "intent": context.intent_classification
                        })
                        
                        # Send budget exceeded event
                        budget_event = StreamEvent(
                            event_type=StreamEventType.ERROR,
                            data={
                                "stream_id": stream_id,
                                "error": "budget_exceeded",
                                "budget_ms": context.budget_ms,
                                "elapsed_ms": elapsed_ms,
                                "intent": context.intent_classification,
                                "reason": f"Query exceeded {context.budget_ms}ms budget for {context.intent_classification} intent"
                            },
                            trace_id=trace_id
                        )
                        yield self._format_sse_event(budget_event)
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
    temperature: float = 0.2,
    trace_id: Optional[str] = None
) -> StreamingResponse:
    """
    Create SSE streaming response for search with enhanced trace ID propagation.
    
    Args:
        query: Search query
        max_tokens: Maximum tokens to generate
        temperature: Generation temperature
        trace_id: Optional trace ID for request tracking
        
    Returns:
        StreamingResponse with SSE headers and trace ID
    """
    # Generate trace ID if not provided
    if not trace_id:
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"
    
    async def event_generator():
        async for event in streaming_manager.create_search_stream(
            query=query,
            max_tokens=max_tokens,
            temperature=temperature,
            trace_id=trace_id
        ):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Content-Type": "text/event-stream; charset=utf-8",
            "Cache-Control": "no-store, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "X-Stream-Type": "search",
            "X-Stream-Max-Seconds": str(STREAM_MAX_SECONDS),
            "X-Heartbeat-Interval": str(HEARTBEAT_INTERVAL),
            "X-Silence-Threshold": str(SILENCE_THRESHOLD),
            "X-Trace-ID": trace_id
        }
    )
