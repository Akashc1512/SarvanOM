"""
WebSocket Models for API Gateway

This module contains WebSocket-specific models and message handling for real-time communication.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class MessageType(str, Enum):
    """Enumeration of WebSocket message types."""
    QUERY_UPDATE = "query_update"
    COLLABORATION = "collaboration"
    SYSTEM_NOTIFICATION = "system_notification"
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    TYPING_INDICATOR = "typing_indicator"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


class ConnectionStatus(str, Enum):
    """Enumeration of WebSocket connection statuses."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class WebSocketConnection(BaseModel):
    """Model for WebSocket connection information."""
    connection_id: str = Field(..., description="Unique connection identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    status: ConnectionStatus = Field(default=ConnectionStatus.CONNECTED, description="Connection status")
    connected_at: datetime = Field(..., description="Connection timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Connection metadata")


class WebSocketMessage(BaseModel):
    """Base model for WebSocket messages."""
    message_type: MessageType = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(..., description="Message timestamp")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    message_id: Optional[str] = Field(None, description="Unique message identifier")


class QueryUpdateMessage(BaseModel):
    """Model for query update messages."""
    query_id: str = Field(..., description="Query identifier")
    status: str = Field(..., description="Query status")
    progress: float = Field(..., ge=0.0, le=1.0, description="Processing progress")
    result: Optional[Dict[str, Any]] = Field(None, description="Query result")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


class CollaborationMessage(BaseModel):
    """Model for collaboration messages."""
    room_id: str = Field(..., description="Collaboration room identifier")
    user_id: str = Field(..., description="User identifier")
    action: str = Field(..., description="Collaboration action")
    content: Optional[str] = Field(None, description="Message content")
    cursor_position: Optional[Dict[str, Any]] = Field(None, description="Cursor position")
    selection: Optional[Dict[str, Any]] = Field(None, description="Text selection")


class SystemNotificationMessage(BaseModel):
    """Model for system notification messages."""
    notification_type: str = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    priority: str = Field(default="info", description="Notification priority")
    action_url: Optional[str] = Field(None, description="Action URL if applicable")


class UserActivityMessage(BaseModel):
    """Model for user activity messages."""
    user_id: str = Field(..., description="User identifier")
    activity_type: str = Field(..., description="Activity type")
    activity_data: Optional[Dict[str, Any]] = Field(None, description="Activity data")
    timestamp: datetime = Field(..., description="Activity timestamp")


class TypingIndicatorMessage(BaseModel):
    """Model for typing indicator messages."""
    user_id: str = Field(..., description="User identifier")
    room_id: str = Field(..., description="Room identifier")
    is_typing: bool = Field(..., description="Whether user is typing")
    timestamp: datetime = Field(..., description="Indicator timestamp")


class WebSocketError(BaseModel):
    """Model for WebSocket error messages."""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(..., description="Error timestamp")


class WebSocketEvent(BaseModel):
    """Model for WebSocket events."""
    event_type: str = Field(..., description="Event type")
    event_data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: datetime = Field(..., description="Event timestamp")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")


class WebSocketSubscription(BaseModel):
    """Model for WebSocket subscriptions."""
    subscription_id: str = Field(..., description="Subscription identifier")
    user_id: str = Field(..., description="User identifier")
    topics: List[str] = Field(..., description="Subscribed topics")
    created_at: datetime = Field(..., description="Subscription creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Subscription expiration timestamp")


class WebSocketMetrics(BaseModel):
    """Model for WebSocket metrics."""
    total_connections: int = Field(..., description="Total active connections")
    active_rooms: int = Field(..., description="Active collaboration rooms")
    messages_per_second: float = Field(..., description="Messages per second")
    average_latency: float = Field(..., description="Average message latency")
    error_rate: float = Field(..., description="Error rate percentage")
    timestamp: datetime = Field(..., description="Metrics timestamp")


class WebSocketConfig(BaseModel):
    """Model for WebSocket configuration."""
    max_connections: int = Field(default=1000, description="Maximum connections")
    message_queue_size: int = Field(default=1000, description="Message queue size")
    heartbeat_interval: int = Field(default=30, description="Heartbeat interval in seconds")
    connection_timeout: int = Field(default=300, description="Connection timeout in seconds")
    max_message_size: int = Field(default=65536, description="Maximum message size in bytes")
    enable_compression: bool = Field(default=True, description="Enable message compression")
    enable_encryption: bool = Field(default=True, description="Enable message encryption") 