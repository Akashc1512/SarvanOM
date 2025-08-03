"""
Logging Middleware for API Gateway

This module handles request logging and structured logging for the API gateway.
It provides comprehensive logging with request tracking and performance monitoring.
"""

import time
import logging
import uuid
from typing import Dict, Any, Optional
from fastapi import Request, Response
from datetime import datetime

logger = logging.getLogger(__name__)


class SafeJSONFormatter(logging.Formatter):
    """Custom JSON formatter that handles missing fields safely."""
    
    def format(self, record):
        # Add default values for common fields
        record.request_id = getattr(record, "request_id", "unknown")
        record.user_id = getattr(record, "user_id", "unknown")
        record.service = "sarvanom-api"
        record.version = "1.0.0"

        # Use JSON format with all fields
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": record.service,
            "version": record.version,
            "request_id": record.request_id,
            "user_id": record.user_id,
        }

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", "pathname", 
                          "filename", "module", "lineno", "funcName", "created", 
                          "msecs", "relativeCreated", "thread", "threadName", 
                          "processName", "process", "getMessage", "exc_info", 
                          "exc_text", "stack_info", "request_id", "user_id", 
                          "service", "version"]:
                log_obj[key] = value

        return str(log_obj)


class RequestLogger:
    """Request logging middleware for tracking API requests."""
    
    def __init__(self):
        self.request_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0
        }
    
    async def log_request(self, request: Request, call_next):
        """Log incoming request with performance metrics."""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Extract request information
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        url = str(request.url)
        content_length = request.headers.get("content-length", 0)
        
        # Log request start
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": method,
                "url": url,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "content_length": content_length,
                "event": "request_start"
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Update statistics
            self.request_stats["total_requests"] += 1
            if response.status_code < 400:
                self.request_stats["successful_requests"] += 1
            else:
                self.request_stats["failed_requests"] += 1
            
            # Update average response time
            current_avg = self.request_stats["average_response_time"]
            total_requests = self.request_stats["total_requests"]
            self.request_stats["average_response_time"] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
            
            # Log request completion
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "content_length": len(response.body) if hasattr(response, 'body') else 0,
                    "event": "request_complete"
                }
            )
            
            # Add performance headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = str(response_time)
            
            return response
            
        except Exception as e:
            # Calculate response time for failed requests
            response_time = time.time() - start_time
            
            # Update statistics
            self.request_stats["total_requests"] += 1
            self.request_stats["failed_requests"] += 1
            
            # Log request failure
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "response_time": response_time,
                    "error": str(e),
                    "event": "request_failed"
                }
            )
            
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current request statistics."""
        return self.request_stats.copy()


class PerformanceLogger:
    """Performance logging for monitoring system performance."""
    
    def __init__(self):
        self.performance_metrics = {
            "slow_requests": [],
            "error_rates": {},
            "throughput": []
        }
    
    async def log_performance(self, request: Request, response: Response, response_time: float):
        """Log performance metrics for the request."""
        # Log slow requests (over 1 second)
        if response_time > 1.0:
            self.performance_metrics["slow_requests"].append({
                "url": str(request.url),
                "method": request.method,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 100 slow requests
            if len(self.performance_metrics["slow_requests"]) > 100:
                self.performance_metrics["slow_requests"] = self.performance_metrics["slow_requests"][-100:]
        
        # Track error rates by endpoint
        endpoint = request.url.path
        if response.status_code >= 400:
            if endpoint not in self.performance_metrics["error_rates"]:
                self.performance_metrics["error_rates"][endpoint] = {"errors": 0, "total": 0}
            
            self.performance_metrics["error_rates"][endpoint]["errors"] += 1
            self.performance_metrics["error_rates"][endpoint]["total"] += 1
        else:
            if endpoint not in self.performance_metrics["error_rates"]:
                self.performance_metrics["error_rates"][endpoint] = {"errors": 0, "total": 0}
            self.performance_metrics["error_rates"][endpoint]["total"] += 1
        
        # Track throughput
        self.performance_metrics["throughput"].append({
            "timestamp": datetime.now().isoformat(),
            "response_time": response_time,
            "status_code": response.status_code
        })
        
        # Keep only last 1000 throughput entries
        if len(self.performance_metrics["throughput"]) > 1000:
            self.performance_metrics["throughput"] = self.performance_metrics["throughput"][-1000:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.performance_metrics.copy()


# Global instances
request_logger = RequestLogger()
performance_logger = PerformanceLogger()


async def add_request_id(request: Request, call_next):
    """Add request ID to request state."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


async def log_requests(request: Request, call_next):
    """Log all requests with performance metrics."""
    return await request_logger.log_request(request, call_next)


def get_request_stats() -> Dict[str, Any]:
    """Get current request statistics."""
    return request_logger.get_stats()


def get_performance_metrics() -> Dict[str, Any]:
    """Get current performance metrics."""
    return performance_logger.get_performance_metrics() 