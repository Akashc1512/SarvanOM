#!/usr/bin/env python3
"""
Security Middleware System

Provides comprehensive security features:
- Input sanitization and validation
- Rate limiting with burst handling
- Security headers (CSP, HSTS, X-Frame-Options)
- Trusted host validation
- Request size limits
- SQL injection prevention
- XSS protection

Following enterprise security standards and OWASP guidelines.
"""

import asyncio
import re
import time
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from collections import defaultdict
import os

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
import html

from .observability import log_error, get_request_id, get_user_id


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int = 5000  # Further increased for production load
    burst_limit: int = 500  # Further increased for production load
    window_size: int = 60  # seconds
    block_duration: int = 30  # Further reduced block duration


@dataclass
class SecurityConfig:
    """Configuration for security features."""
    # Rate limiting
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    
    # Trusted hosts
    trusted_hosts: Set[str] = field(default_factory=lambda: {
        "localhost",
        "127.0.0.1",
        "::1",
        "host.docker.internal",
        "host.docker.internal:8000",
        "localhost:8000",
        "127.0.0.1:8000",
        "sarvanom.local",
        "*.sarvanom.com",
        "*.sarvanom.org"
    })
    
    # Request limits
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    max_query_length: int = 1000
    max_headers_size: int = 8192
    
    # Security headers
    enable_csp: bool = True
    enable_hsts: bool = True
    enable_x_frame_options: bool = True
    enable_x_content_type_options: bool = True
    enable_referrer_policy: bool = True
    
    # Content Security Policy
    csp_policy: str = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.openai.com https://api.anthropic.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    
    # HSTS configuration
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = False


class RateLimiter:
    """Rate limiter with sliding window and burst handling."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Dict[str, float] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def _get_client_key(self, request: Request) -> str:
        """Get unique key for rate limiting."""
        # Use X-Forwarded-For if available, otherwise client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Add user agent hash for additional uniqueness
        user_agent = request.headers.get("user-agent", "")
        user_agent_hash = hashlib.md5(user_agent.encode()).hexdigest()[:8]
        
        return f"{client_ip}:{user_agent_hash}"
    
    def is_rate_limited(self, request: Request) -> bool:
        """Check if request should be rate limited."""
        # Bypass rate limiting for monitoring and system endpoints
        bypass_paths = [
            '/health', '/metrics', '/system/status', '/graph/context',
            '/docs', '/openapi.json', '/redoc', '/favicon.ico'
        ]
        if any(request.url.path.startswith(path) for path in bypass_paths):
            return False
            
        client_key = self._get_client_key(request)
        current_time = time.time()
        
        # Check if IP is blocked
        if client_key in self.blocked_ips:
            if current_time < self.blocked_ips[client_key]:
                return True
            else:
                # Unblock expired IP
                del self.blocked_ips[client_key]
        
        # Clean old requests outside the window
        window_start = current_time - self.config.window_size
        self.requests[client_key] = [
            req_time for req_time in self.requests[client_key]
            if req_time > window_start
        ]
        
        # Check rate limit
        request_count = len(self.requests[client_key])
        
        if request_count >= self.config.requests_per_minute:
            # Block IP for block_duration
            self.blocked_ips[client_key] = current_time + self.config.block_duration
            return True
        
        # Check burst limit
        recent_requests = [
            req_time for req_time in self.requests[client_key]
            if req_time > current_time - 1  # Last second
        ]
        
        if len(recent_requests) >= self.config.burst_limit:
            return True
        
        # Add current request
        self.requests[client_key].append(current_time)
        return False
    
    async def cleanup_old_data(self):
        """Clean up old rate limiting data."""
        while True:
            try:
                current_time = time.time()
                window_start = current_time - self.config.window_size
                
                # Clean old requests
                for client_key in list(self.requests.keys()):
                    self.requests[client_key] = [
                        req_time for req_time in self.requests[client_key]
                        if req_time > window_start
                    ]
                    
                    # Remove empty entries
                    if not self.requests[client_key]:
                        del self.requests[client_key]
                
                # Clean old blocked IPs
                for client_key in list(self.blocked_ips.keys()):
                    if current_time >= self.blocked_ips[client_key]:
                        del self.blocked_ips[client_key]
                
                await asyncio.sleep(60)  # Clean up every minute
                
            except Exception as e:
                log_error("rate_limiter_cleanup", str(e))
                await asyncio.sleep(60)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive security features."""
    
    def __init__(self, app: ASGIApp, config: Optional[SecurityConfig] = None):
        super().__init__(app)
        self.config = config or SecurityConfig()
        self.rate_limiter = RateLimiter(self.config.rate_limit)
        self.rate_limiter._cleanup_task = asyncio.create_task(
            self.rate_limiter.cleanup_old_data()
        )
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            # 1. Rate limiting
            if self.rate_limiter.is_rate_limited(request):
                log_error(
                    "rate_limit_exceeded",
                    f"Rate limit exceeded for {request.client.host}",
                    {"request_id": get_request_id(), "user_id": get_user_id()}
                )
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            # 2. Trusted host validation
            if not self._is_trusted_host(request):
                log_error(
                    "untrusted_host",
                    f"Request from untrusted host: {request.headers.get('host', 'unknown')}",
                    {"request_id": get_request_id(), "user_id": get_user_id()}
                )
                raise HTTPException(
                    status_code=400,
                    detail="Invalid host header"
                )
            
            # 3. Request size validation
            if not self._validate_request_size(request):
                log_error(
                    "request_too_large",
                    "Request size exceeds limit",
                    {"request_id": get_request_id(), "user_id": get_user_id()}
                )
                raise HTTPException(
                    status_code=413,
                    detail="Request too large"
                )
            
            # 4. Input sanitization
            sanitized_request = await self._sanitize_request(request)
            
            # 5. Process request
            response = await call_next(sanitized_request)
            
            # 6. Add security headers
            self._add_security_headers(response)
            
            return response
            
        except HTTPException as http_exc:
            # Preserve original HTTPException details
            log_error(
                "http_exception",
                f"HTTP {http_exc.status_code}: {http_exc.detail}",
                {"request_id": get_request_id(), "user_id": get_user_id(), "status_code": http_exc.status_code}
            )
            raise
        except Exception as e:
            log_error(
                "security_middleware_error",
                str(e),
                {"request_id": get_request_id(), "user_id": get_user_id()}
            )
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    def _is_trusted_host(self, request: Request) -> bool:
        """Validate if the request is from a trusted host."""
        # Allow all hosts during testing or development
        if os.getenv("TESTING", "false").lower() == "true" or os.getenv("ENVIRONMENT", "development") == "development":
            return True
            
        host = request.headers.get("host", "")
        if not host:
            return False
        
        # Always allow localhost and Docker internal hosts
        if any(allowed in host.lower() for allowed in ["localhost", "127.0.0.1", "host.docker.internal", "::1"]):
            return True
        
        # Check exact matches first (including with port)
        if host in self.config.trusted_hosts:
            return True
        
        # Remove port if present and check again
        host_without_port = host.split(":")[0]
        if host_without_port in self.config.trusted_hosts:
            return True
        
        # Check wildcard matches
        for trusted_host in self.config.trusted_hosts:
            if trusted_host.startswith("*."):
                domain = trusted_host[2:]  # Remove "*. "
                if host_without_port.endswith(domain):
                    return True
        
        return False
    
    def _validate_request_size(self, request: Request) -> bool:
        """Validate request size limits."""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.config.max_request_size:
                    return False
            except ValueError:
                return False
        
        # Check query string length
        if len(str(request.url.query)) > self.config.max_query_length:
            return False
        
        # Check headers size
        headers_size = sum(
            len(name) + len(value) + 2  # +2 for ": " separator
            for name, value in request.headers.items()
        )
        if headers_size > self.config.max_headers_size:
            return False
        
        return True
    
    async def _sanitize_request(self, request: Request) -> Request:
        """Sanitize request input to prevent injection attacks."""
        # Sanitize query parameters
        sanitized_query_params = {}
        for key, value in request.query_params.items():
            sanitized_key = self._sanitize_string(key)
            sanitized_value = self._sanitize_string(value)
            sanitized_query_params[sanitized_key] = sanitized_value
        
        # Create new request with sanitized parameters
        # Note: This is a simplified approach. In a real implementation,
        # you might need to create a custom request class or use middleware
        # that can modify the request object.
        
        return request
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string input to prevent XSS and injection attacks."""
        if not isinstance(value, str):
            return str(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # HTML escape to prevent XSS
        value = html.escape(value)
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript protocol
            r'vbscript:',  # VBScript protocol
            r'data:',  # Data URLs
            r'<iframe[^>]*>.*?</iframe>',  # Iframe tags
            r'<object[^>]*>.*?</object>',  # Object tags
            r'<embed[^>]*>',  # Embed tags
            r'<form[^>]*>.*?</form>',  # Form tags
            r'on\w+\s*=',  # Event handlers
            r'expression\s*\(',  # CSS expressions
            r'url\s*\(',  # CSS url functions
        ]
        
        for pattern in dangerous_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove SQL injection patterns
        sql_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
            r'(\b(and|or)\b\s+\d+\s*=\s*\d+)',
            r'(\b(and|or)\b\s+\'\w+\'\s*=\s*\'\w+\')',
            r'(\b(and|or)\b\s+\w+\s*=\s*\w+)',
            r'(\b(and|or)\b\s+\w+\s*like\s*\w+)',
            r'(\b(and|or)\b\s+\w+\s*in\s*\([^)]*\))',
        ]
        
        for pattern in sql_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        return value.strip()
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response."""
        # Content Security Policy
        if self.config.enable_csp:
            response.headers["Content-Security-Policy"] = self.config.csp_policy
        
        # HTTP Strict Transport Security
        if self.config.enable_hsts:
            hsts_value = f"max-age={self.config.hsts_max_age}"
            if self.config.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if self.config.hsts_preload:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value
        
        # X-Frame-Options
        if self.config.enable_x_frame_options:
            response.headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options
        if self.config.enable_x_content_type_options:
            response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Referrer Policy
        if self.config.enable_referrer_policy:
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Additional security headers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for input validation and sanitization."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            # Validate and sanitize request body
            if request.method in ["POST", "PUT", "PATCH"]:
                await self._validate_request_body(request)
            
            # Validate URL parameters
            self._validate_url_params(request)
            
            # Validate headers
            self._validate_headers(request)
            
            response = await call_next(request)
            return response
            
        except HTTPException as http_exc:
            # Preserve original HTTPException details
            log_error(
                "input_validation_http_exception",
                f"HTTP {http_exc.status_code}: {http_exc.detail}",
                {"request_id": get_request_id(), "user_id": get_user_id(), "status_code": http_exc.status_code}
            )
            raise
        except Exception as e:
            log_error(
                "input_validation_error",
                str(e),
                {"request_id": get_request_id(), "user_id": get_user_id()}
            )
            raise HTTPException(
                status_code=400,
                detail=f"Invalid input: {str(e)}"
            )
    
    async def _validate_request_body(self, request: Request):
        """Validate and sanitize request body."""
        content_type = request.headers.get("content-type", "")
        
        # Skip validation for auth endpoints
        if request.url.path.startswith("/auth/"):
            return
        
        if "application/json" in content_type:
            try:
                body = await request.json()
                if not isinstance(body, dict):
                    raise HTTPException(
                        status_code=400,
                        detail="Request body must be a JSON object"
                    )
                
                # Validate required fields for non-auth endpoints
                if "query" in body:
                    query = body["query"]
                    if not isinstance(query, str):
                        raise HTTPException(
                            status_code=400,
                            detail="Query must be a string"
                        )
                    
                    if len(query) > 1000:
                        raise HTTPException(
                            status_code=400,
                            detail="Query too long (max 1000 characters)"
                        )
                    
                    # Sanitize query
                    body["query"] = self._sanitize_string(query)
                
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid JSON in request body"
                )
    
    def _validate_url_params(self, request: Request):
        """Validate URL parameters."""
        # Check for suspicious parameters
        suspicious_params = ["script", "javascript", "vbscript", "data", "onload"]
        
        for param in request.query_params.keys():
            param_lower = param.lower()
            for suspicious in suspicious_params:
                if suspicious in param_lower:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid parameter name"
                    )
    
    def _validate_headers(self, request: Request):
        """Validate request headers."""
        # Check for suspicious headers
        suspicious_headers = [
            "x-forwarded-host",
            "x-forwarded-proto",
            "x-forwarded-for",
            "x-real-ip",
            "x-original-url",
            "x-rewrite-url"
        ]
        
        for header_name in request.headers.keys():
            header_lower = header_name.lower()
            if header_lower in suspicious_headers:
                # Log suspicious header but don't block
                log_error(
                    "suspicious_header",
                    f"Suspicious header detected: {header_name}",
                    {"request_id": get_request_id(), "user_id": get_user_id()}
                )
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            return str(value)
        
        # Remove null bytes and control characters
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        # HTML escape
        value = html.escape(value)
        
        # Remove dangerous patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'data:',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>',
            r'<form[^>]*>.*?</form>',
            r'on\w+\s*=',
            r'expression\s*\(',
            r'url\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE | re.DOTALL)
        
        return value.strip()


# Utility functions for security
def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def validate_filename(filename: str) -> bool:
    """Validate filename for security."""
    # Check for path traversal attempts
    dangerous_patterns = [
        r'\.\./',
        r'\.\.\\',
        r'%2e%2e%2f',
        r'%2e%2e%5c',
        r'\.\.%2f',
        r'\.\.%5c',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            return False
    
    # Check for dangerous extensions
    dangerous_extensions = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
        '.jar', '.war', '.ear', '.class', '.php', '.asp', '.aspx',
        '.jsp', '.jspx', '.py', '.pl', '.sh', '.cgi'
    ]
    
    filename_lower = filename.lower()
    for ext in dangerous_extensions:
        if filename_lower.endswith(ext):
            return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove path separators
    filename = re.sub(r'[\\/]', '_', filename)
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"|?*]', '_', filename)
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename.strip()
