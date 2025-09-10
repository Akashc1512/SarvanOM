"""
Tracing Middleware - SarvanOM v2

Automatic trace propagation and span creation for all services.
"""

import time
import uuid
from typing import Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()

class TracingMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic trace propagation and span creation"""
    
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name
    
    async def dispatch(self, request: Request, call_next):
        """Process request with tracing"""
        # Extract or create trace context
        trace_context = self._extract_trace_context(request)
        
        # Create span for this request
        span_context = self._create_span(trace_context, f"{request.method} {request.url.path}")
        
        # Add trace headers to request state
        request.state.trace_context = span_context
        
        # Record request start
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record successful request
            duration = time.time() - start_time
            self._record_request_metrics(span_context, request, response, duration, None)
            
            # Add trace headers to response
            self._add_trace_headers(response, span_context)
            
            return response
            
        except Exception as e:
            # Record failed request
            duration = time.time() - start_time
            self._record_request_metrics(span_context, request, None, duration, str(e))
            
            # Re-raise exception
            raise
    
    def _extract_trace_context(self, request: Request) -> Dict[str, Any]:
        """Extract trace context from request headers"""
        trace_id = request.headers.get("X-Trace-ID")
        span_id = request.headers.get("X-Span-ID")
        parent_span_id = request.headers.get("X-Parent-Span-ID")
        service_name = request.headers.get("X-Service-Name")
        request_id = request.headers.get("X-Request-ID")
        
        if trace_id and span_id:
            # Existing trace context
            return {
                "trace_id": trace_id,
                "span_id": span_id,
                "parent_span_id": parent_span_id,
                "service_name": service_name or self.service_name,
                "request_id": request_id or str(uuid.uuid4())
            }
        else:
            # Create new trace context
            return self._create_new_trace()
    
    def _create_new_trace(self) -> Dict[str, Any]:
        """Create new trace context"""
        timestamp = time.strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4()).replace('-', '')[:12]
        
        return {
            "trace_id": f"{self.service_name}-{timestamp}-{random_suffix}",
            "span_id": str(uuid.uuid4()).replace('-', '')[:12],
            "parent_span_id": None,
            "service_name": self.service_name,
            "request_id": str(uuid.uuid4())
        }
    
    def _create_span(self, parent_context: Dict[str, Any], span_name: str) -> Dict[str, Any]:
        """Create child span"""
        return {
            "trace_id": parent_context["trace_id"],
            "span_id": str(uuid.uuid4()).replace('-', '')[:12],
            "parent_span_id": parent_context["span_id"],
            "service_name": parent_context["service_name"],
            "request_id": parent_context["request_id"],
            "span_name": span_name,
            "start_time": time.time()
        }
    
    def _record_request_metrics(self, span_context: Dict[str, Any], request: Request, 
                               response: Optional[Response], duration: float, error: Optional[str]):
        """Record request metrics"""
        status = "success" if response and response.status_code < 400 else "error"
        
        # Log structured trace information
        logger.info(
            "Request processed",
            trace_id=span_context["trace_id"],
            span_id=span_context["span_id"],
            parent_span_id=span_context["parent_span_id"],
            service_name=span_context["service_name"],
            span_name=span_context["span_name"],
            method=request.method,
            path=request.url.path,
            status_code=response.status_code if response else None,
            duration=duration,
            status=status,
            error=error
        )
    
    def _add_trace_headers(self, response: Response, span_context: Dict[str, Any]):
        """Add trace headers to response"""
        response.headers["X-Trace-ID"] = span_context["trace_id"]
        response.headers["X-Span-ID"] = span_context["span_id"]
        response.headers["X-Service-Name"] = span_context["service_name"]
        response.headers["X-Request-ID"] = span_context["request_id"]

class TraceContext:
    """Context manager for trace spans"""
    
    def __init__(self, service_name: str, span_name: str, attributes: Dict[str, Any] = None):
        self.service_name = service_name
        self.span_name = span_name
        self.attributes = attributes or {}
        self.span_context = None
        self.start_time = None
    
    def __enter__(self):
        """Enter trace context"""
        self.start_time = time.time()
        self.span_context = {
            "span_id": str(uuid.uuid4()).replace('-', '')[:12],
            "span_name": self.span_name,
            "service_name": self.service_name,
            "attributes": self.attributes,
            "start_time": self.start_time
        }
        
        logger.info(
            "Span started",
            span_id=self.span_context["span_id"],
            span_name=self.span_name,
            service_name=self.service_name,
            attributes=self.attributes
        )
        
        return self.span_context
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit trace context"""
        duration = time.time() - self.start_time
        status = "error" if exc_type else "success"
        
        logger.info(
            "Span completed",
            span_id=self.span_context["span_id"],
            span_name=self.span_name,
            service_name=self.service_name,
            duration=duration,
            status=status,
            error=str(exc_val) if exc_val else None
        )

def create_trace_headers(trace_context: Dict[str, Any]) -> Dict[str, str]:
    """Create trace headers for HTTP requests"""
    return {
        "X-Trace-ID": trace_context["trace_id"],
        "X-Span-ID": trace_context["span_id"],
        "X-Parent-Span-ID": trace_context.get("parent_span_id", ""),
        "X-Service-Name": trace_context["service_name"],
        "X-Request-ID": trace_context["request_id"]
    }

def extract_trace_context(request: Request) -> Optional[Dict[str, Any]]:
    """Extract trace context from request"""
    trace_id = request.headers.get("X-Trace-ID")
    span_id = request.headers.get("X-Span-ID")
    parent_span_id = request.headers.get("X-Parent-Span-ID")
    service_name = request.headers.get("X-Service-Name")
    request_id = request.headers.get("X-Request-ID")
    
    if not trace_id or not span_id:
        return None
    
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "service_name": service_name,
        "request_id": request_id
    }
