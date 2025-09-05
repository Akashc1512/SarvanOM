#!/usr/bin/env python3
"""
Audit Service for End-to-End Request Tracking and Provenance

Provides comprehensive audit trails for:
- Request/response lifecycle tracking
- Service call provenance
- Performance metrics correlation
- Error tracking and debugging
- Compliance and regulatory requirements

Following MAANG/OpenAI/Perplexity standards for enterprise audit systems.
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import os
import logging

from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "90"))
AUDIT_MAX_ENTRIES = int(os.getenv("AUDIT_MAX_ENTRIES", "10000"))
AUDIT_ENABLED = os.getenv("AUDIT_ENABLED", "true").lower() == "true"


class AuditEventType(str, Enum):
    """Types of audit events."""
    REQUEST_START = "request_start"
    REQUEST_END = "request_end"
    SERVICE_CALL = "service_call"
    SERVICE_RESPONSE = "service_response"
    ERROR = "error"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"


class AuditSeverity(str, Enum):
    """Audit event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Individual audit event."""
    event_id: str
    trace_id: str
    event_type: AuditEventType
    timestamp: datetime
    service_name: str
    operation: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    severity: AuditSeverity = AuditSeverity.LOW
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class AuditTrail:
    """Complete audit trail for a request."""
    trace_id: str
    request_id: str
    user_id: Optional[str]
    session_id: Optional[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_ms: Optional[float] = None
    events: List[AuditEvent] = field(default_factory=list)
    service_calls: Dict[str, List[AuditEvent]] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[AuditEvent] = field(default_factory=list)
    security_events: List[AuditEvent] = field(default_factory=list)
    status: str = "in_progress"
    final_status_code: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AuditService:
    """Comprehensive audit service for request tracking and provenance."""
    
    def __init__(self):
        self.audit_trails: Dict[str, AuditTrail] = {}
        self.cleanup_task: Optional[asyncio.Task] = None
        self._shutdown = False
        
    async def initialize(self):
        """Initialize the audit service."""
        if not AUDIT_ENABLED:
            logger.info("Audit service disabled via environment variable")
            return
            
        logger.info("Initializing audit service")
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_old_trails())
        
        logger.info("✅ Audit service initialized")
    
    async def close(self):
        """Cleanup audit service."""
        logger.info("Shutting down audit service")
        self._shutdown = True
        
        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Audit service shutdown complete")
    
    def start_audit_trail(
        self,
        trace_id: str,
        request_id: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditTrail:
        """Start a new audit trail for a request."""
        if not AUDIT_ENABLED:
            return None
            
        start_time = datetime.now(timezone.utc)
        
        audit_trail = AuditTrail(
            trace_id=trace_id,
            request_id=request_id,
            user_id=user_id,
            session_id=session_id,
            start_time=start_time,
            metadata=metadata or {}
        )
        
        self.audit_trails[trace_id] = audit_trail
        
        # Log request start
        self._add_event(
            trace_id=trace_id,
            event_type=AuditEventType.REQUEST_START,
            service_name="gateway",
            operation="request_start",
            message=f"Request started: {request_id}",
            metadata={
                "request_id": request_id,
                "user_id": user_id,
                "session_id": session_id
            }
        )
        
        logger.debug(f"Started audit trail: {trace_id}")
        return audit_trail
    
    def end_audit_trail(
        self,
        trace_id: str,
        status_code: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AuditTrail]:
        """End an audit trail for a request."""
        if not AUDIT_ENABLED:
            return None
            
        if trace_id not in self.audit_trails:
            logger.warning(f"Audit trail not found: {trace_id}")
            return None
        
        audit_trail = self.audit_trails[trace_id]
        end_time = datetime.now(timezone.utc)
        
        audit_trail.end_time = end_time
        audit_trail.total_duration_ms = (end_time - audit_trail.start_time).total_seconds() * 1000
        audit_trail.status = "completed"
        audit_trail.final_status_code = status_code
        
        if metadata:
            audit_trail.metadata.update(metadata)
        
        # Log request end
        self._add_event(
            trace_id=trace_id,
            event_type=AuditEventType.REQUEST_END,
            service_name="gateway",
            operation="request_end",
            message=f"Request completed: {audit_trail.request_id}",
            status_code=status_code,
            duration_ms=audit_trail.total_duration_ms,
            metadata={
                "request_id": audit_trail.request_id,
                "total_duration_ms": audit_trail.total_duration_ms,
                "status_code": status_code
            }
        )
        
        logger.debug(f"Ended audit trail: {trace_id} ({audit_trail.total_duration_ms:.2f}ms)")
        return audit_trail
    
    def log_service_call(
        self,
        trace_id: str,
        service_name: str,
        operation: str,
        start_time: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log a service call start."""
        if not AUDIT_ENABLED:
            return None
            
        call_id = f"call_{uuid.uuid4().hex[:8]}"
        
        self._add_event(
            trace_id=trace_id,
            event_type=AuditEventType.SERVICE_CALL,
            service_name=service_name,
            operation=operation,
            message=f"Service call started: {service_name}.{operation}",
            metadata={
                "call_id": call_id,
                "service_name": service_name,
                "operation": operation,
                "start_time": (start_time or datetime.now(timezone.utc)).isoformat()
            }
        )
        
        # Track in service calls
        if trace_id in self.audit_trails:
            if service_name not in self.audit_trails[trace_id].service_calls:
                self.audit_trails[trace_id].service_calls[service_name] = []
            self.audit_trails[trace_id].service_calls[service_name].append(
                self.audit_trails[trace_id].events[-1]
            )
        
        return call_id
    
    def log_service_response(
        self,
        trace_id: str,
        service_name: str,
        operation: str,
        status_code: int,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log a service call response."""
        if not AUDIT_ENABLED:
            return
            
        self._add_event(
            trace_id=trace_id,
            event_type=AuditEventType.SERVICE_RESPONSE,
            service_name=service_name,
            operation=operation,
            message=f"Service call completed: {service_name}.{operation}",
            status_code=status_code,
            duration_ms=duration_ms,
            metadata=metadata or {}
        )
    
    def log_error(
        self,
        trace_id: str,
        service_name: str,
        operation: str,
        error_message: str,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an error event."""
        if not AUDIT_ENABLED:
            return
            
        event = self._add_event(
            trace_id=trace_id,
            event_type=AuditEventType.ERROR,
            service_name=service_name,
            operation=operation,
            message=f"Error in {service_name}.{operation}: {error_message}",
            severity=severity,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        # Track in errors
        if trace_id in self.audit_trails:
            self.audit_trails[trace_id].errors.append(event)
    
    def log_performance_metric(
        self,
        trace_id: str,
        metric_name: str,
        value: Union[int, float],
        unit: str = "ms",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log a performance metric."""
        if not AUDIT_ENABLED:
            return
            
        self._add_event(
            trace_id=trace_id,
            event_type=AuditEventType.PERFORMANCE,
            service_name="gateway",
            operation="performance_metric",
            message=f"Performance metric: {metric_name} = {value} {unit}",
            metadata={
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                **(metadata or {})
            }
        )
        
        # Track in performance metrics
        if trace_id in self.audit_trails:
            self.audit_trails[trace_id].performance_metrics[metric_name] = {
                "value": value,
                "unit": unit,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def log_security_event(
        self,
        trace_id: str,
        event_type: str,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log a security event."""
        if not AUDIT_ENABLED:
            return
            
        event = self._add_event(
            trace_id=trace_id,
            event_type=AuditEventType.SECURITY,
            service_name="security",
            operation=event_type,
            message=message or f"Security event: {event_type}",
            severity=severity,
            metadata=metadata or {}
        )
        
        # Track in security events
        if trace_id in self.audit_trails:
            self.audit_trails[trace_id].security_events.append(event)
    
    def _add_event(
        self,
        trace_id: str,
        event_type: AuditEventType,
        service_name: str,
        operation: str,
        message: str = "",
        severity: AuditSeverity = AuditSeverity.LOW,
        duration_ms: Optional[float] = None,
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """Add an event to the audit trail."""
        if trace_id not in self.audit_trails:
            logger.warning(f"Audit trail not found for event: {trace_id}")
            return None
        
        event = AuditEvent(
            event_id=f"event_{uuid.uuid4().hex[:8]}",
            trace_id=trace_id,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            service_name=service_name,
            operation=operation,
            user_id=self.audit_trails[trace_id].user_id,
            session_id=self.audit_trails[trace_id].session_id,
            severity=severity,
            message=message,
            duration_ms=duration_ms,
            status_code=status_code,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        self.audit_trails[trace_id].events.append(event)
        return event
    
    def get_audit_trail(self, trace_id: str) -> Optional[AuditTrail]:
        """Get an audit trail by trace ID."""
        return self.audit_trails.get(trace_id)
    
    def get_audit_trails(
        self,
        user_id: Optional[str] = None,
        service_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditTrail]:
        """Get audit trails with filtering."""
        trails = list(self.audit_trails.values())
        
        # Apply filters
        if user_id:
            trails = [t for t in trails if t.user_id == user_id]
        
        if start_time:
            trails = [t for t in trails if t.start_time >= start_time]
        
        if end_time:
            trails = [t for t in trails if t.start_time <= end_time]
        
        # Sort by start time (newest first)
        trails.sort(key=lambda t: t.start_time, reverse=True)
        
        return trails[:limit]
    
    async def _cleanup_old_trails(self):
        """Cleanup old audit trails."""
        while not self._shutdown:
            try:
                current_time = datetime.now(timezone.utc)
                cutoff_time = current_time - timedelta(days=AUDIT_RETENTION_DAYS)
                
                # Remove old trails
                trails_to_remove = []
                for trace_id, trail in self.audit_trails.items():
                    if trail.start_time < cutoff_time:
                        trails_to_remove.append(trace_id)
                
                for trace_id in trails_to_remove:
                    del self.audit_trails[trace_id]
                
                if trails_to_remove:
                    logger.info(f"Cleaned up {len(trails_to_remove)} old audit trails")
                
                # Limit total number of trails
                if len(self.audit_trails) > AUDIT_MAX_ENTRIES:
                    # Remove oldest trails
                    sorted_trails = sorted(
                        self.audit_trails.items(),
                        key=lambda x: x[1].start_time
                    )
                    
                    excess_count = len(self.audit_trails) - AUDIT_MAX_ENTRIES
                    for trace_id, _ in sorted_trails[:excess_count]:
                        del self.audit_trails[trace_id]
                    
                    logger.info(f"Removed {excess_count} excess audit trails")
                
                # Wait 1 hour before next cleanup
                await asyncio.sleep(3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Audit cleanup error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error


# Global audit service instance
audit_service = AuditService()


def get_audit_service() -> AuditService:
    """Get the global audit service instance."""
    return audit_service
