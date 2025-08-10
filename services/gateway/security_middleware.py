#!/usr/bin/env python3
"""
Security Middleware for SarvanOM Gateway

Extracted and simplified from services/api_gateway/middleware/auth.py
Implements essential security patterns for the Universal Knowledge Platform.
"""

import time
import hashlib
from typing import Dict, Any, Optional, Set
from fastapi import Request, HTTPException
from collections import defaultdict


class SecurityMiddleware:
    """Lightweight security middleware for SarvanOM Gateway."""
    
    def __init__(self):
        self.blocked_ips: Set[str] = set()
        self.rate_limits: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.config = {
            "max_requests_per_minute": 60,
            "max_tokens_per_minute": 10000,
            "blocked_keywords": ["malicious", "attack", "exploit"],
            "bypass_paths": ["/health", "/metrics", "/docs", "/"],
        }
    
    async def check_request_security(self, request: Request, query: str = "") -> Dict[str, Any]:
        """Perform basic security checks on incoming requests."""
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            raise HTTPException(status_code=403, detail="IP address blocked")
        
        # Check rate limits
        if not self._check_rate_limit(client_ip):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Check for malicious content
        security_score = self._analyze_content_security(query)
        
        return {
            "client_ip": client_ip,
            "security_score": security_score,
            "passed": security_score < 0.8,  # Threshold for blocking
            "timestamp": time.time()
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return getattr(request.client, "host", "unknown")
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Advanced rate limiting with sliding window algorithm.
        
        Extracted and enhanced from shared/core/rate_limiter_v2.py for better accuracy.
        """
        current_time = time.time()
        minute_window = int(current_time // 60)
        
        # Initialize if new client
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = {}
        
        # Sliding window implementation (enhanced from rate_limiter_v2.py)
        window_size = 60  # 1 minute
        current_timestamp = int(current_time)
        
        # Clean old entries (more than window_size seconds old)
        cutoff_time = current_timestamp - window_size
        self.rate_limits[client_ip] = {
            timestamp: count for timestamp, count in self.rate_limits[client_ip].items()
            if timestamp > cutoff_time
        }
        
        # Count requests in current window
        total_requests = sum(self.rate_limits[client_ip].values())
        
        # Add current request
        if current_timestamp not in self.rate_limits[client_ip]:
            self.rate_limits[client_ip][current_timestamp] = 0
        self.rate_limits[client_ip][current_timestamp] += 1
        total_requests += 1
        
        # Check against limit
        limit = self.config["max_requests_per_minute"]
        return total_requests <= limit
    
    def _analyze_content_security(self, content: str) -> float:
        """Analyze content for security threats."""
        if not content:
            return 0.0
        
        content_lower = content.lower()
        threat_score = 0.0
        
        # Check for blocked keywords
        for keyword in self.config["blocked_keywords"]:
            if keyword in content_lower:
                threat_score += 0.3
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r"<script[^>]*>",  # Script tags
            r"javascript:",     # JavaScript URLs
            r"eval\s*\(",      # Eval calls
            r"exec\s*\(",      # Exec calls
        ]
        
        import re
        for pattern in suspicious_patterns:
            if re.search(pattern, content_lower):
                threat_score += 0.2
        
        # Check content length (very long queries might be attacks)
        if len(content) > 10000:
            threat_score += 0.1
        
        return min(threat_score, 1.0)


class AuthenticationHelper:
    """Simple authentication helper for development and testing."""
    
    def __init__(self):
        self.test_mode = True  # Enable test mode for development
    
    async def get_current_user_or_test_user(self, request: Request) -> Dict[str, Any]:
        """Get current user or return test user in development."""
        if self.test_mode:
            return {
                "user_id": "test_user",
                "role": "user",
                "permissions": ["read", "write"],
                "test_mode": True
            }
        
        # In production, implement proper JWT validation here
        auth_header = request.headers.get("authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="No authorization header")
        
        # Simple token validation (replace with proper JWT validation)
        token = auth_header.replace("Bearer ", "")
        if not token:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "user_id": "authenticated_user",
            "role": "user",
            "permissions": ["read", "write"],
            "test_mode": False
        }
    
    async def require_write_or_test(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Require write permissions or allow in test mode."""
        if user.get("test_mode") or "write" in user.get("permissions", []):
            return user
        
        raise HTTPException(status_code=403, detail="Write permission required")


# Global instances
security_middleware = SecurityMiddleware()
auth_helper = AuthenticationHelper()
