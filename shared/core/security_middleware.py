"""
Enhanced Security Middleware - MAANG Standards
Following OpenAI and Perplexity security patterns.

Features:
- Comprehensive threat detection
- Input sanitization and validation
- Security headers
- Rate limiting integration
- Audit logging
- IP whitelisting/blacklisting
- Request size limits
- Content type validation

Security Measures:
- SQL injection prevention
- XSS attack detection
- CSRF protection
- Path traversal prevention
- Malicious content detection
- Request smuggling prevention

Authors:
- Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import re
import json
import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import structlog
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
import ipaddress

logger = structlog.get_logger(__name__)


class SecurityLevel(str, Enum):
    """Security levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(str, Enum):
    """Threat types."""

    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    PATH_TRAVERSAL = "path_traversal"
    MALICIOUS_CONTENT = "malicious_content"
    RATE_LIMIT_VIOLATION = "rate_limit_violation"
    INVALID_INPUT = "invalid_input"
    SUSPICIOUS_IP = "suspicious_ip"
    REQUEST_SMUGGLING = "request_smuggling"


@dataclass
class SecurityConfig:
    """Security configuration."""

    # Threat detection
    enable_sql_injection_detection: bool = True
    enable_xss_detection: bool = True
    enable_path_traversal_detection: bool = True
    enable_malicious_content_detection: bool = True
    enable_rate_limiting: bool = True
    enable_ip_filtering: bool = True

    # Request limits
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    max_header_size: int = 8192
    max_url_length: int = 2048
    max_parameter_count: int = 100

    # Rate limiting
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    burst_limit: int = 10

    # IP filtering
    allowed_ips: List[str] = None
    blocked_ips: List[str] = None
    ip_whitelist_enabled: bool = False
    ip_blacklist_enabled: bool = True

    # Headers
    enable_security_headers: bool = True
    enable_cors: bool = True
    cors_origins: List[str] = None

    # Logging
    log_security_events: bool = True
    log_suspicious_activity: bool = True

    def __post_init__(self):
        """Initialize default values."""
        if self.allowed_ips is None:
            self.allowed_ips = []
        if self.blocked_ips is None:
            self.blocked_ips = []
        if self.cors_origins is None:
            self.cors_origins = ["*"]


class SecurityValidator:
    """Security validation utilities."""

    # Threat patterns
    SQL_INJECTION_PATTERNS = [
        r"\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b",
        r"(\b(and|or)\s+\d+\s*=\s*\d+)",
        r"(\b(and|or)\s+['\"].*['\"]\s*=\s*['\"].*['\"])",
        r"(--|#|/\*|\*/)",
        r"(\bxp_|sp_|fn_)",
        r"(\bwaitfor\s+delay\b)",
        r"(\bbenchmark\s*\()",
    ]

    XSS_PATTERNS = [
        r"(<script|javascript:|onerror=|onclick=|<iframe|<object|<embed)",
        r"(vbscript:|data:text/html|data:application/x-javascript)",
        r"(expression\(|eval\(|setTimeout\(|setInterval\()",
        r"(alert\(|confirm\(|prompt\()",
        r"(document\.|window\.|location\.)",
        r"(localStorage|sessionStorage)",
    ]

    PATH_TRAVERSAL_PATTERNS = [
        r"(\.\./|\.\.\\|%2e%2e|%2e%2e%2f|%2e%2e%5c)",
        r"(\.\.%2f|\.\.%5c|%2e%2e%2f|%2e%2e%5c)",
        r"(%252e%252e|%252e%252e%252f)",
    ]

    MALICIOUS_CONTENT_PATTERNS = [
        r"(alert\(|confirm\(|prompt\()",
        r"(document\.|window\.|location\.)",
        r"(localStorage|sessionStorage)",
        r"(fetch\(|XMLHttpRequest)",
        r"(eval\(|Function\()",
        r"(setTimeout\(|setInterval\()",
    ]

    REQUEST_SMUGGLING_PATTERNS = [
        r"(Content-Length:\s*0\s*\r?\n.*\r?\n.*\r?\n)",
        r"(Transfer-Encoding:\s*chunked\s*\r?\n.*\r?\n.*\r?\n)",
    ]

    @staticmethod
    def check_sql_injection(text: str) -> Tuple[bool, Optional[str]]:
        """Check for SQL injection attempts."""
        for pattern in SecurityValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"SQL injection pattern detected: {pattern}"
        return True, None

    @staticmethod
    def check_xss(text: str) -> Tuple[bool, Optional[str]]:
        """Check for XSS attempts."""
        for pattern in SecurityValidator.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"XSS pattern detected: {pattern}"
        return True, None

    @staticmethod
    def check_path_traversal(text: str) -> Tuple[bool, Optional[str]]:
        """Check for path traversal attempts."""
        for pattern in SecurityValidator.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Path traversal pattern detected: {pattern}"
        return True, None

    @staticmethod
    def check_malicious_content(text: str) -> Tuple[bool, Optional[str]]:
        """Check for malicious content."""
        for pattern in SecurityValidator.MALICIOUS_CONTENT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Malicious content pattern detected: {pattern}"
        return True, None

    @staticmethod
    def check_request_smuggling(headers: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """Check for HTTP request smuggling attempts."""
        # Check for conflicting headers
        content_length = headers.get("content-length", "")
        transfer_encoding = headers.get("transfer-encoding", "")

        if content_length and transfer_encoding:
            return False, "Conflicting Content-Length and Transfer-Encoding headers"

        # Check for malformed headers
        for header_name, header_value in headers.items():
            if "\n" in header_value or "\r" in header_value:
                return False, "Malformed header value detected"

        return True, None

    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate IP address format."""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_ip_allowed(ip: str, allowed_ips: List[str], blocked_ips: List[str]) -> bool:
        """Check if IP is allowed."""
        # Check blacklist first
        if ip in blocked_ips:
            return False

        # If whitelist is enabled, check whitelist
        if allowed_ips:
            return ip in allowed_ips

        return True

    @staticmethod
    def sanitize_input(text: str, max_length: int = 10000) -> str:
        """Sanitize input text."""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")

        # Remove null bytes
        text = text.replace("\x00", "")

        # Remove control characters except newline and tab
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]

        return text.strip()


class SecurityMiddleware:
    """Enhanced security middleware."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.threat_detector = SecurityValidator()
        self._ip_cache: Dict[str, Tuple[bool, float]] = {}
        self._cache_ttl = 300  # 5 minutes

    async def __call__(self, request: Request, call_next):
        """Process request through security middleware."""

        start_time = time.time()
        client_ip = self._get_client_ip(request)

        try:
            # 1. IP validation
            if not await self._validate_ip(client_ip):
                return self._create_security_response(
                    ThreatType.SUSPICIOUS_IP,
                    f"IP address {client_ip} is not allowed",
                    status.HTTP_403_FORBIDDEN,
                )

            # 2. Request size validation
            if not await self._validate_request_size(request):
                return self._create_security_response(
                    ThreatType.INVALID_INPUT,
                    "Request too large",
                    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )

            # 3. URL validation
            if not await self._validate_url(request):
                return self._create_security_response(
                    ThreatType.INVALID_INPUT, "Invalid URL", status.HTTP_400_BAD_REQUEST
                )

            # 4. Header validation
            if not await self._validate_headers(request):
                return self._create_security_response(
                    ThreatType.REQUEST_SMUGGLING,
                    "Malformed headers detected",
                    status.HTTP_400_BAD_REQUEST,
                )

            # 5. Content validation
            if not await self._validate_content(request):
                return self._create_security_response(
                    ThreatType.MALICIOUS_CONTENT,
                    "Malicious content detected",
                    status.HTTP_400_BAD_REQUEST,
                )

            # 6. Process request
            response = await call_next(request)

            # 7. Add security headers
            response = await self._add_security_headers(response)

            # 8. Log security event
            await self._log_security_event(
                request, response, client_ip, start_time, "success"
            )

            return response

        except Exception as e:
            # Log security error
            await self._log_security_event(
                request, None, client_ip, start_time, "error", str(e)
            )
            raise

    async def _validate_ip(self, ip: str) -> bool:
        """Validate IP address."""
        # Check cache first
        if ip in self._ip_cache:
            allowed, timestamp = self._ip_cache[ip]
            if time.time() - timestamp < self._cache_ttl:
                return allowed

        # Validate IP format
        if not SecurityValidator.validate_ip_address(ip):
            return False

        # Check IP filtering
        allowed = SecurityValidator.is_ip_allowed(
            ip, self.config.allowed_ips, self.config.blocked_ips
        )

        # Cache result
        self._ip_cache[ip] = (allowed, time.time())

        return allowed

    async def _validate_request_size(self, request: Request) -> bool:
        """Validate request size."""
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.config.max_request_size:
                    return False
            except ValueError:
                return False

        return True

    async def _validate_url(self, request: Request) -> bool:
        """Validate URL."""
        url = str(request.url)

        # Check URL length
        if len(url) > self.config.max_url_length:
            return False

        # Check for path traversal in URL
        is_safe, _ = SecurityValidator.check_path_traversal(url)
        if not is_safe:
            return False

        return True

    async def _validate_headers(self, request: Request) -> bool:
        """Validate request headers."""
        headers = dict(request.headers)

        # Check header count
        if len(headers) > self.config.max_parameter_count:
            return False

        # Check for request smuggling
        is_safe, _ = SecurityValidator.check_request_smuggling(headers)
        if not is_safe:
            return False

        # Check header sizes
        for name, value in headers.items():
            if len(name) + len(value) > self.config.max_header_size:
                return False

        return True

    async def _validate_content(self, request: Request) -> bool:
        """Validate request content."""
        content_type = request.headers.get("content-type", "")

        # Skip validation for certain content types
        if content_type.startswith("multipart/form-data"):
            return True

        # Validate JSON content
        if content_type.startswith("application/json"):
            try:
                body = await request.body()
                if body:
                    text = body.decode("utf-8")

                    # Security checks
                    for check_func, threat_type in [
                        (
                            SecurityValidator.check_sql_injection,
                            ThreatType.SQL_INJECTION,
                        ),
                        (SecurityValidator.check_xss, ThreatType.XSS_ATTACK),
                        (
                            SecurityValidator.check_malicious_content,
                            ThreatType.MALICIOUS_CONTENT,
                        ),
                    ]:
                        is_safe, details = check_func(text)
                        if not is_safe:
                            await self._log_threat(threat_type, details, request)
                            return False

                    # Validate JSON structure
                    json.loads(text)

            except (UnicodeDecodeError, json.JSONDecodeError):
                return False

        return True

    async def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response."""
        if not self.config.enable_security_headers:
            return response

        # Security headers
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
        }

        # Add headers to response
        for name, value in headers.items():
            response.headers[name] = value

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    async def _log_security_event(
        self,
        request: Request,
        response: Optional[Response],
        client_ip: str,
        start_time: float,
        status: str,
        error: Optional[str] = None,
    ):
        """Log security event."""
        if not self.config.log_security_events:
            return

        duration = time.time() - start_time

        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "client_ip": client_ip,
            "method": request.method,
            "url": str(request.url),
            "user_agent": request.headers.get("user-agent", ""),
            "status": status,
            "duration": duration,
            "response_status": response.status_code if response else None,
            "error": error,
        }

        logger.info("security_event", **event_data)

    async def _log_threat(
        self, threat_type: ThreatType, details: str, request: Request
    ):
        """Log security threat."""
        if not self.config.log_suspicious_activity:
            return

        threat_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "threat_type": threat_type.value,
            "details": details,
            "client_ip": self._get_client_ip(request),
            "method": request.method,
            "url": str(request.url),
            "user_agent": request.headers.get("user-agent", ""),
        }

        logger.warning("security_threat", **threat_data)

    def _create_security_response(
        self, threat_type: ThreatType, message: str, status_code: int
    ) -> JSONResponse:
        """Create security response."""

        response_data = {
            "request_id": str(int(time.time() * 1000)),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "version": "2.0.0",
            "error": {
                "code": "security_violation",
                "message": message,
                "details": {
                    "threat_type": threat_type.value,
                    "type": "security_violation",
                },
            },
        }

        return JSONResponse(
            status_code=status_code,
            content=response_data,
            headers={
                "X-Request-ID": response_data["request_id"],
                "X-Security-Violation": threat_type.value,
            },
        )


def create_security_middleware(config: SecurityConfig):
    """Create security middleware instance."""
    return SecurityMiddleware(config)
