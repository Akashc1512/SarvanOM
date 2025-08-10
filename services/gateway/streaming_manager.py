#!/usr/bin/env python3
"""
Advanced Streaming System for SarvanOM
Implements MAANG/OpenAI/Perplexity level streaming with SSE and WebSocket support
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, AsyncGenerator, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import aiohttp
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

class StreamType(Enum):
    """Stream types for different use cases"""
    SSE = "sse"  # Server-Sent Events
    WEBSOCKET = "websocket"
    HTTP_STREAM = "http_stream"

class StreamStatus(Enum):
    """Stream status states"""
    CONNECTING = "connecting"
    STREAMING = "streaming"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

@dataclass
class StreamEvent:
    """Stream event structure"""
    event_type: str
    data: Any
    timestamp: datetime
    stream_id: str
    sequence: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "stream_id": self.stream_id,
            "sequence": self.sequence,
            "metadata": self.metadata or {}
        }

class StreamManager:
    """
    Advanced streaming manager with SSE, WebSocket, and HTTP streaming support
    Following MAANG/OpenAI/Perplexity industry standards
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        max_concurrent_streams: int = 1000,
        stream_timeout: int = 300,  # 5 minutes
        enable_redis_pubsub: bool = True,
        chunk_size: int = 1024,
        enable_compression: bool = True
    ):
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        self.max_concurrent_streams = max_concurrent_streams
        self.stream_timeout = stream_timeout
        self.enable_redis_pubsub = enable_redis_pubsub
        self.chunk_size = chunk_size
        self.enable_compression = enable_compression
        
        # Active streams tracking
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        
        # Metrics
        self.metrics = {
            "total_streams": 0,
            "active_streams": 0,
            "completed_streams": 0,
            "failed_streams": 0,
            "total_events": 0,
            "total_bytes_sent": 0
        }
    
    async def initialize(self) -> None:
        """Initialize Redis connection for pub/sub"""
        try:
            if self.redis_url and self.enable_redis_pubsub:
                self.redis_client = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                await self.redis_client.ping()
                logger.info("✅ Redis pub/sub initialized for streaming")
            else:
                logger.info("ℹ️ Using in-memory streaming only")
        except Exception as e:
            logger.error(f"❌ Redis pub/sub initialization failed: {e}")
            self.redis_client = None
    
    def _generate_stream_id(self) -> str:
        """Generate unique stream ID"""
        return f"stream_{uuid.uuid4().hex[:16]}"
    
    async def create_sse_stream(
        self,
        query: str,
        user_id: str,
        endpoint: str,
        llm_processor: Any,
        **kwargs
    ) -> EventSourceResponse:
        """Create Server-Sent Events stream"""
        stream_id = self._generate_stream_id()
        
        async def event_generator():
            try:
                # Register stream
                await self._register_stream(stream_id, query, user_id, endpoint, StreamType.SSE)
                
                # Send connection event
                yield {
                    "event": "connect",
                    "data": {
                        "stream_id": stream_id,
                        "status": "connecting",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                # Start streaming
                async for event in self._stream_llm_response(
                    stream_id, query, user_id, endpoint, llm_processor, **kwargs
                ):
                    yield {
                        "event": event.event_type,
                        "data": event.data,
                        "id": str(event.sequence),
                        "retry": 3000  # 3 second retry
                    }
                
                # Send completion event
                yield {
                    "event": "complete",
                    "data": {
                        "stream_id": stream_id,
                        "status": "completed",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
            except Exception as e:
                logger.error(f"SSE stream error: {e}")
                yield {
                    "event": "error",
                    "data": {
                        "stream_id": stream_id,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                }
            finally:
                await self._unregister_stream(stream_id)
        
        return EventSourceResponse(event_generator())
    
    async def create_websocket_stream(
        self,
        websocket: WebSocket,
        query: str,
        user_id: str,
        endpoint: str,
        llm_processor: Any,
        **kwargs
    ) -> None:
        """Create WebSocket stream"""
        stream_id = self._generate_stream_id()
        
        try:
            await websocket.accept()
            self.websocket_connections[stream_id] = websocket
            
            # Register stream
            await self._register_stream(stream_id, query, user_id, endpoint, StreamType.WEBSOCKET)
            
            # Send connection event
            await websocket.send_json({
                "event_type": "connect",
                "data": {
                    "stream_id": stream_id,
                    "status": "connecting",
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            # Start streaming
            async for event in self._stream_llm_response(
                stream_id, query, user_id, endpoint, llm_processor, **kwargs
            ):
                await websocket.send_json(event.to_dict())
            
            # Send completion event
            await websocket.send_json({
                "event_type": "complete",
                "data": {
                    "stream_id": stream_id,
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                }
            })
            
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {stream_id}")
        except Exception as e:
            logger.error(f"WebSocket stream error: {e}")
            try:
                await websocket.send_json({
                    "event_type": "error",
                    "data": {
                        "stream_id": stream_id,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                })
            except:
                pass
        finally:
            await self._unregister_stream(stream_id)
            if stream_id in self.websocket_connections:
                del self.websocket_connections[stream_id]
    
    async def create_http_stream(
        self,
        query: str,
        user_id: str,
        endpoint: str,
        llm_processor: Any,
        **kwargs
    ) -> StreamingResponse:
        """Create HTTP streaming response"""
        stream_id = self._generate_stream_id()
        
        async def content_generator():
            try:
                # Register stream
                await self._register_stream(stream_id, query, user_id, endpoint, StreamType.HTTP_STREAM)
                
                # Send initial response
                yield json.dumps({
                    "stream_id": stream_id,
                    "status": "connecting",
                    "timestamp": datetime.now().isoformat()
                }) + "\n"
                
                # Start streaming
                async for event in self._stream_llm_response(
                    stream_id, query, user_id, endpoint, llm_processor, **kwargs
                ):
                    yield json.dumps(event.to_dict()) + "\n"
                
                # Send completion
                yield json.dumps({
                    "stream_id": stream_id,
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                }) + "\n"
                
            except Exception as e:
                logger.error(f"HTTP stream error: {e}")
                yield json.dumps({
                    "stream_id": stream_id,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }) + "\n"
            finally:
                await self._unregister_stream(stream_id)
        
        return StreamingResponse(
            content_generator(),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Stream-ID": stream_id
            }
        )
    
    async def _stream_llm_response(
        self,
        stream_id: str,
        query: str,
        user_id: str,
        endpoint: str,
        llm_processor: Any,
        **kwargs
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream LLM response with real-time updates"""
        sequence = 0
        
        try:
            # Send processing start event
            yield StreamEvent(
                event_type="processing_start",
                data={
                    "query": query,
                    "endpoint": endpoint,
                    "message": "Starting AI processing..."
                },
                timestamp=datetime.now(),
                stream_id=stream_id,
                sequence=sequence
            )
            sequence += 1
            
            # Update stream status
            await self._update_stream_status(stream_id, StreamStatus.STREAMING)
            
            # Start LLM processing based on endpoint
            if endpoint == "search":
                result = await llm_processor.search_with_ai(
                    query=query,
                    user_id=user_id,
                    max_results=kwargs.get("max_results", 10),
                    stream=True
                )
            elif endpoint == "fact_check":
                result = await llm_processor.fact_check_with_ai(
                    claim=query,
                    context=kwargs.get("context", ""),
                    sources=kwargs.get("sources", []),
                    stream=True
                )
            elif endpoint == "synthesize":
                result = await llm_processor.synthesize_with_ai(
                    content=query,
                    query=query,
                    sources=kwargs.get("sources", []),
                    stream=True
                )
            else:
                raise ValueError(f"Unsupported endpoint for streaming: {endpoint}")
            
            # Stream the result
            if hasattr(result, '__aiter__'):
                # Async generator result
                async for chunk in result:
                    yield StreamEvent(
                        event_type="content_chunk",
                        data=chunk,
                        timestamp=datetime.now(),
                        stream_id=stream_id,
                        sequence=sequence,
                        metadata={"chunk_size": len(str(chunk))}
                    )
                    sequence += 1
                    self.metrics["total_events"] += 1
            else:
                # Single result
                yield StreamEvent(
                    event_type="content_complete",
                    data=result,
                    timestamp=datetime.now(),
                    stream_id=stream_id,
                    sequence=sequence
                )
                sequence += 1
                self.metrics["total_events"] += 1
            
            # Send processing complete event
            yield StreamEvent(
                event_type="processing_complete",
                data={
                    "message": "AI processing completed",
                    "total_chunks": sequence - 1
                },
                timestamp=datetime.now(),
                stream_id=stream_id,
                sequence=sequence
            )
            
            # Update metrics
            self.metrics["completed_streams"] += 1
            
        except Exception as e:
            logger.error(f"Stream processing error: {e}")
            yield StreamEvent(
                event_type="error",
                data={
                    "error": str(e),
                    "message": "Processing failed"
                },
                timestamp=datetime.now(),
                stream_id=stream_id,
                sequence=sequence
            )
            self.metrics["failed_streams"] += 1
    
    async def _register_stream(
        self,
        stream_id: str,
        query: str,
        user_id: str,
        endpoint: str,
        stream_type: StreamType
    ) -> None:
        """Register new stream"""
        if len(self.active_streams) >= self.max_concurrent_streams:
            raise Exception("Maximum concurrent streams reached")
        
        self.active_streams[stream_id] = {
            "query": query,
            "user_id": user_id,
            "endpoint": endpoint,
            "stream_type": stream_type.value,
            "status": StreamStatus.CONNECTING.value,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "events_sent": 0,
            "bytes_sent": 0
        }
        
        self.metrics["total_streams"] += 1
        self.metrics["active_streams"] += 1
        
        # Publish to Redis if available
        if self.redis_client:
            try:
                await self.redis_client.publish(
                    "stream_events",
                    json.dumps({
                        "event": "stream_created",
                        "stream_id": stream_id,
                        "user_id": user_id,
                        "endpoint": endpoint
                    })
                )
            except Exception as e:
                logger.error(f"Redis publish error: {e}")
    
    async def _unregister_stream(self, stream_id: str) -> None:
        """Unregister stream"""
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]
            self.metrics["active_streams"] -= 1
        
        if stream_id in self.websocket_connections:
            del self.websocket_connections[stream_id]
    
    async def _update_stream_status(self, stream_id: str, status: StreamStatus) -> None:
        """Update stream status"""
        if stream_id in self.active_streams:
            self.active_streams[stream_id]["status"] = status.value
            self.active_streams[stream_id]["last_activity"] = datetime.now()
    
    async def cancel_stream(self, stream_id: str) -> bool:
        """Cancel active stream"""
        if stream_id in self.active_streams:
            await self._update_stream_status(stream_id, StreamStatus.CANCELLED)
            
            # Close WebSocket if exists
            if stream_id in self.websocket_connections:
                try:
                    await self.websocket_connections[stream_id].close()
                except:
                    pass
                del self.websocket_connections[stream_id]
            
            await self._unregister_stream(stream_id)
            return True
        return False
    
    async def get_stream_info(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get stream information"""
        return self.active_streams.get(stream_id)
    
    async def get_active_streams(self) -> List[Dict[str, Any]]:
        """Get all active streams"""
        return [
            {
                "stream_id": stream_id,
                **info
            }
            for stream_id, info in self.active_streams.items()
        ]
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get streaming metrics"""
        return {
            **self.metrics,
            "active_streams_count": len(self.active_streams),
            "websocket_connections": len(self.websocket_connections),
            "redis_connected": self.redis_client is not None
        }
    
    async def cleanup_expired_streams(self) -> int:
        """Clean up expired streams"""
        now = datetime.now()
        expired_streams = []
        
        for stream_id, info in self.active_streams.items():
            if (now - info["last_activity"]).total_seconds() > self.stream_timeout:
                expired_streams.append(stream_id)
        
        for stream_id in expired_streams:
            await self.cancel_stream(stream_id)
        
        return len(expired_streams)
    
    async def close(self) -> None:
        """Close all connections"""
        # Close all WebSocket connections
        for websocket in self.websocket_connections.values():
            try:
                await websocket.close()
            except:
                pass
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        # Clear active streams
        self.active_streams.clear()
        self.websocket_connections.clear()
        
        logger.info("Stream manager closed")

# Global stream manager instance
stream_manager = StreamManager()
