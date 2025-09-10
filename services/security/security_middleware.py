"""
Security Middleware - SarvanOM v2

Automatic security enforcement for all requests.
"""

import time
import hashlib
from typing import Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic security enforcement"""
    
    def __init__(self, app, security_service_url: str = "http://localhost:8007"):
        super().__init__(app)
        self.security_service_url = security_service_url
        self.blocked_ips = set()
        self.suspicious_patterns = [
            r"<script", r"javascript:", r"onload=", r"onerror=",
            r"union select", r"drop table", r"delete from",
            r"../", r"..\\", r"cmd.exe", r"/bin/sh"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request with security enforcement"""
        start_time = time.time()
        
        # Extract request information
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        path = request.url.path
        method = request.method
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning("Blocked IP attempted access", ip=client_ip, path=path)
            return Response(
                content="Access denied",
                status_code=403,
                headers={"X-Blocked-Reason": "ip_blocked"}
            )
        
        # Analyze user agent
        ua_analysis = self._analyze_user_agent(user_agent)
        if ua_analysis["action"] == "block":
            logger.warning("Blocked suspicious user agent", user_agent=user_agent, ip=client_ip)
            return Response(
                content="Access denied",
                status_code=403,
                headers={"X-Blocked-Reason": "suspicious_user_agent"}
            )
        
        # Check for malicious patterns in URL
        if self._detect_malicious_patterns(path):
            logger.warning("Blocked malicious URL pattern", path=path, ip=client_ip)
            return Response(
                content="Access denied",
                status_code=403,
                headers={"X-Blocked-Reason": "malicious_pattern"}
            )
        
        # Check for malicious patterns in query parameters
        if self._detect_malicious_patterns(str(request.query_params)):
            logger.warning("Blocked malicious query pattern", query_params=str(request.query_params), ip=client_ip)
            return Response(
                content="Access denied",
                status_code=403,
                headers={"X-Blocked-Reason": "malicious_query_pattern"}
            )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Apply security headers
            response = self._apply_security_headers(response)
            
            # Log successful request
            duration = time.time() - start_time
            logger.info(
                "Request processed",
                ip=client_ip,
                method=method,
                path=path,
                status_code=response.status_code,
                duration=duration,
                user_agent_type=ua_analysis["type"]
            )
            
            return response
            
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                "Request processing failed",
                ip=client_ip,
                method=method,
                path=path,
                error=str(e),
                duration=duration
            )
            
            # Return error response with security headers
            error_response = Response(
                content="Internal server error",
                status_code=500
            )
            return self._apply_security_headers(error_response)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def _analyze_user_agent(self, user_agent: str) -> Dict[str, Any]:
        """Analyze user agent for abuse detection"""
        if not user_agent or user_agent.strip() == "":
            return {
                "type": "empty",
                "risk_score": 1.0,
                "action": "block",
                "reason": "empty_user_agent"
            }
        
        user_agent_lower = user_agent.lower()
        
        # Check for bot patterns
        bot_patterns = [
            r"bot", r"crawler", r"spider", r"scraper",
            r"curl", r"wget", r"python", r"java",
            r"postman", r"insomnia", r"httpie"
        ]
        
        for pattern in bot_patterns:
            if pattern in user_agent_lower:
                return {
                    "type": "bot",
                    "risk_score": 0.5,
                    "action": "rate_limit",
                    "reason": f"bot_pattern_detected: {pattern}"
                }
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r"^$", r"^Mozilla$", r"^User-Agent$",
            r"^[A-Za-z]{1,3}$", r"^[0-9]+$"
        ]
        
        for pattern in suspicious_patterns:
            if pattern == user_agent:
                return {
                    "type": "suspicious",
                    "risk_score": 0.8,
                    "action": "block",
                    "reason": f"suspicious_pattern: {pattern}"
                }
        
        # Default to browser
        return {
            "type": "browser",
            "risk_score": 0.1,
            "action": "allow",
            "reason": "normal_browser"
        }
    
    def _detect_malicious_patterns(self, text: str) -> bool:
        """Detect malicious patterns in text"""
        import re
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _apply_security_headers(self, response: Response) -> Response:
        """Apply security headers to response"""
        # Content Security Policy
        csp_value = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.sarvanom.com; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "media-src 'self'; "
            "camera 'none'; "
            "microphone 'none'; "
            "clipboard-read 'none'; "
            "clipboard-write 'none'"
        )
        response.headers["Content-Security-Policy"] = csp_value
        
        # HTTP Strict Transport Security
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Referrer-Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy (for LMM flows)
        permissions_policy = (
            "camera=(), microphone=(), clipboard-read=(), clipboard-write=(), "
            "geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=(), "
            "accelerometer=(), ambient-light-sensor=(), autoplay=(), "
            "battery=(), display-capture=(), document-domain=(), "
            "encrypted-media=(), fullscreen=(), picture-in-picture=(), "
            "publickey-credentials-get=(), screen-wake-lock=(), sync-xhr=(), "
            "web-share=(), xr-spatial-tracking=()"
        )
        response.headers["Permissions-Policy"] = permissions_policy
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting"""
    
    def __init__(self, app, redis_client, rate_limits: Dict[str, Dict[str, int]]):
        super().__init__(app)
        self.redis = redis_client
        self.rate_limits = rate_limits
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Get client identifier
        client_ip = self._get_client_ip(request)
        user_id = request.headers.get("X-User-ID")
        
        # Determine tier
        tier = self._determine_tier(request)
        
        # Check rate limit
        identifier = user_id if user_id else client_ip
        rate_limit_result = self._check_rate_limit(identifier, tier)
        
        if not rate_limit_result["allowed"]:
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={
                    "X-RateLimit-Limit": str(rate_limit_result["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(rate_limit_result["reset_time"]),
                    "Retry-After": str(rate_limit_result["reset_time"] - int(time.time()))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_limit_result["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_result["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_limit_result["reset_time"])
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def _determine_tier(self, request: Request) -> str:
        """Determine user tier for rate limiting"""
        # Check for API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return "api"
        
        # Check for authentication
        auth_header = request.headers.get("Authorization")
        if auth_header:
            return "authenticated"
        
        # Default to anonymous
        return "anonymous"
    
    def _check_rate_limit(self, identifier: str, tier: str) -> Dict[str, Any]:
        """Check rate limit for identifier"""
        limits = self.rate_limits.get(tier, self.rate_limits["anonymous"])
        
        # Check per-minute limit
        minute_key = f"rate_limit:{identifier}:minute:{int(time.time() // 60)}"
        minute_count = self.redis.get(minute_key)
        
        if minute_count and int(minute_count) >= limits["rpm"]:
            return {
                "allowed": False,
                "limit": limits["rpm"],
                "remaining": 0,
                "reset_time": int(time.time() // 60) * 60 + 60,
                "reason": "minute_limit_exceeded"
            }
        
        # Check per-hour limit
        hour_key = f"rate_limit:{identifier}:hour:{int(time.time() // 3600)}"
        hour_count = self.redis.get(hour_key)
        
        if hour_count and int(hour_count) >= limits["rph"]:
            return {
                "allowed": False,
                "limit": limits["rph"],
                "remaining": 0,
                "reset_time": int(time.time() // 3600) * 3600 + 3600,
                "reason": "hour_limit_exceeded"
            }
        
        # Increment counters
        self.redis.incr(minute_key)
        self.redis.expire(minute_key, 60)
        
        self.redis.incr(hour_key)
        self.redis.expire(hour_key, 3600)
        
        # Calculate remaining
        minute_remaining = limits["rpm"] - (int(minute_count) + 1 if minute_count else 1)
        hour_remaining = limits["rph"] - (int(hour_count) + 1 if hour_count else 1)
        
        return {
            "allowed": True,
            "limit": limits["rpm"],
            "remaining": min(minute_remaining, hour_remaining),
            "reset_time": int(time.time() // 60) * 60 + 60,
            "reason": "allowed"
        }

class PIIRedactionMiddleware(BaseHTTPMiddleware):
    """Middleware for PII redaction in logs"""
    
    def __init__(self, app):
        super().__init__(app)
        self.pii_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with PII redaction"""
        # Process request
        response = await call_next(request)
        
        # Redact PII from response if needed
        if response.headers.get("content-type", "").startswith("application/json"):
            # Note: In a real implementation, you would redact PII from response content
            # This is a simplified version
            pass
        
        return response
    
    def _redact_pii(self, text: str) -> str:
        """Redact PII from text"""
        import re
        
        redacted_text = text
        
        for pii_type, pattern in self.pii_patterns.items():
            if pii_type == "email":
                redacted_text = re.sub(pattern, r'***@\2', redacted_text)
            elif pii_type == "phone":
                redacted_text = re.sub(pattern, '***-***-****', redacted_text)
            elif pii_type == "ssn":
                redacted_text = re.sub(pattern, '***-**-****', redacted_text)
            elif pii_type == "credit_card":
                redacted_text = re.sub(pattern, '****-****-****-****', redacted_text)
            elif pii_type == "ip_address":
                redacted_text = re.sub(pattern, '***.***.***.***', redacted_text)
        
        return redacted_text
