"""
Secure Input Validation & Sanitization - OpenAI/Anthropic Security Standards

Features:
- Comprehensive input validation
- XSS prevention with output encoding
- SQL injection prevention
- Path traversal prevention
- Command injection prevention
- Input sanitization and normalization
- Content Security Policy (CSP) headers
- Secure file upload validation

Security Measures:
- Whitelist-based validation
- Blacklist-based filtering
- Context-aware sanitization
- Output encoding
- Input length limits
- Character set validation
- Malicious pattern detection

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import re
import html
import urllib.parse
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog
from pydantic import BaseModel, Field, validator
import bleach
from markupsafe import Markup

logger = structlog.get_logger(__name__)


class ValidationLevel(str, Enum):
    """Validation levels."""

    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


class InputType(str, Enum):
    """Input types for validation."""

    TEXT = "text"
    HTML = "html"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"
    NUMBER = "number"
    FILE = "file"
    JSON = "json"
    SQL = "sql"


@dataclass
class ValidationConfig:
    """Input validation configuration."""

    # General settings
    max_length: int = 10000
    min_length: int = 1
    allow_empty: bool = False
    trim_whitespace: bool = True

    # Security settings
    prevent_xss: bool = True
    prevent_sql_injection: bool = True
    prevent_path_traversal: bool = True
    prevent_command_injection: bool = True

    # Content settings
    allowed_tags: List[str] = None
    allowed_attributes: List[str] = None
    allowed_protocols: List[str] = None

    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = None
    scan_for_malware: bool = True

    def __post_init__(self):
        """Initialize default values."""
        if self.allowed_tags is None:
            self.allowed_tags = []
        if self.allowed_attributes is None:
            self.allowed_attributes = []
        if self.allowed_protocols is None:
            self.allowed_protocols = ["http", "https"]
        if self.allowed_file_types is None:
            self.allowed_file_types = [".txt", ".pdf", ".doc", ".docx"]


class InputValidator:
    """Comprehensive input validation and sanitization."""

    # Threat patterns
    XSS_PATTERNS = [
        r"(<script|javascript:|onerror=|onclick=|<iframe|<object|<embed)",
        r"(vbscript:|data:text/html|data:application/x-javascript)",
        r"(expression\(|eval\(|setTimeout\(|setInterval\()",
        r"(alert\(|confirm\(|prompt\()",
        r"(document\.|window\.|location\.)",
        r"(localStorage|sessionStorage)",
        r"(fetch\(|XMLHttpRequest)",
        r"(<img.*onload=|<img.*onerror=)",
        r"(<a.*href=javascript:|<a.*href=data:)",
    ]

    SQL_INJECTION_PATTERNS = [
        r"\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b",
        r"(\b(and|or)\s+\d+\s*=\s*\d+)",
        r"(\b(and|or)\s+['\"].*['\"]\s*=\s*['\"].*['\"])",
        r"(--|#|/\*|\*/)",
        r"(\bxp_|sp_|fn_)",
        r"(\bwaitfor\s+delay\b)",
        r"(\bbenchmark\s*\()",
        r"(\bunion\s+select\b)",
        r"(\bor\s+1\s*=\s*1\b)",
        r"(\band\s+1\s*=\s*1\b)",
    ]

    PATH_TRAVERSAL_PATTERNS = [
        r"(\.\./|\.\.\\|%2e%2e|%2e%2e%2f|%2e%2e%5c)",
        r"(\.\.%2f|\.\.%5c|%2e%2e%2f|%2e%2e%5c)",
        r"(%252e%252e|%252e%252e%252f)",
        r"(\.\.%252f|\.\.%2525c)",
        r"(\.\.%c0%af|\.\.%c1%9c)",
    ]

    COMMAND_INJECTION_PATTERNS = [
        r"(\bcat\b|\bchmod\b|\bchown\b|\bcurl\b|\bwget\b)",
        r"(\brm\b|\brmdir\b|\bmkdir\b|\btouch\b|\bls\b)",
        r"(\bping\b|\bnslookup\b|\bdig\b|\bhost\b)",
        r"(\bnet\b|\bnetstat\b|\bifconfig\b|\bipconfig\b)",
        r"(\bwhoami\b|\bid\b|\buname\b|\bhostname\b)",
        r"(\b|&|\||;|\$\(|\`|\$\(|\$\[)",
    ]

    MALICIOUS_CONTENT_PATTERNS = [
        r"(alert\(|confirm\(|prompt\()",
        r"(document\.|window\.|location\.)",
        r"(localStorage|sessionStorage)",
        r"(fetch\(|XMLHttpRequest)",
        r"(eval\(|Function\()",
        r"(setTimeout\(|setInterval\()",
        r"(<script|javascript:|vbscript:)",
        r"(data:text/html|data:application/x-javascript)",
    ]

    @staticmethod
    def validate_text(
        text: str, config: ValidationConfig, input_type: InputType = InputType.TEXT
    ) -> Tuple[bool, str, Optional[str]]:
        """Validate and sanitize text input."""

        if not isinstance(text, str):
            return False, "Input must be a string", None

        # Check length
        if len(text) > config.max_length:
            return False, f"Input too long (max {config.max_length} characters)", None

        if len(text) < config.min_length:
            return False, f"Input too short (min {config.min_length} characters)", None

        # Handle empty input
        if not text.strip() and not config.allow_empty:
            return False, "Input cannot be empty", None

        # Trim whitespace
        if config.trim_whitespace:
            text = text.strip()

        # Type-specific validation
        if input_type == InputType.EMAIL:
            return InputValidator._validate_email(text, config)
        elif input_type == InputType.URL:
            return InputValidator._validate_url(text, config)
        elif input_type == InputType.PHONE:
            return InputValidator._validate_phone(text, config)
        elif input_type == InputType.DATE:
            return InputValidator._validate_date(text, config)
        elif input_type == InputType.NUMBER:
            return InputValidator._validate_number(text, config)
        elif input_type == InputType.HTML:
            return InputValidator._validate_html(text, config)
        else:
            return InputValidator._validate_generic_text(text, config)

    @staticmethod
    def _validate_generic_text(
        text: str, config: ValidationConfig
    ) -> Tuple[bool, str, Optional[str]]:
        """Validate generic text input."""

        # Check for malicious patterns
        if config.prevent_xss:
            for pattern in InputValidator.XSS_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    return False, f"XSS pattern detected: {pattern}", None

        if config.prevent_sql_injection:
            for pattern in InputValidator.SQL_INJECTION_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    return False, f"SQL injection pattern detected: {pattern}", None

        if config.prevent_path_traversal:
            for pattern in InputValidator.PATH_TRAVERSAL_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    return False, f"Path traversal pattern detected: {pattern}", None

        if config.prevent_command_injection:
            for pattern in InputValidator.COMMAND_INJECTION_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    return False, f"Command injection pattern detected: {pattern}", None

        # Sanitize text
        sanitized = InputValidator._sanitize_text(text)

        return True, "Input is valid", sanitized

    @staticmethod
    def _validate_email(
        text: str, config: ValidationConfig
    ) -> Tuple[bool, str, Optional[str]]:
        """Validate email address."""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_pattern, text):
            return False, "Invalid email format", None

        # Check for malicious patterns
        for pattern in InputValidator.MALICIOUS_CONTENT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Malicious content in email: {pattern}", None

        return True, "Email is valid", text.lower()

    @staticmethod
    def _validate_url(
        text: str, config: ValidationConfig
    ) -> Tuple[bool, str, Optional[str]]:
        """Validate URL."""
        try:
            parsed = urllib.parse.urlparse(text)

            # Check protocol
            if parsed.scheme not in config.allowed_protocols:
                return False, f"Protocol not allowed: {parsed.scheme}", None

            # Check for malicious patterns
            for pattern in InputValidator.MALICIOUS_CONTENT_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    return False, f"Malicious content in URL: {pattern}", None

            return True, "URL is valid", text

        except Exception:
            return False, "Invalid URL format", None

    @staticmethod
    def _validate_phone(
        text: str, config: ValidationConfig
    ) -> Tuple[bool, str, Optional[str]]:
        """Validate phone number."""
        # Remove all non-digit characters
        digits_only = re.sub(r"\D", "", text)

        if len(digits_only) < 10 or len(digits_only) > 15:
            return False, "Invalid phone number length", None

        # Check for malicious patterns
        for pattern in InputValidator.MALICIOUS_CONTENT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Malicious content in phone: {pattern}", None

        return True, "Phone number is valid", digits_only

    @staticmethod
    def _validate_date(
        text: str, config: ValidationConfig
    ) -> Tuple[bool, str, Optional[str]]:
        """Validate date format."""
        # Basic date pattern (YYYY-MM-DD)
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"

        if not re.match(date_pattern, text):
            return False, "Invalid date format (use YYYY-MM-DD)", None

        try:
            from datetime import datetime

            datetime.strptime(text, "%Y-%m-%d")
        except ValueError:
            return False, "Invalid date", None

        return True, "Date is valid", text

    @staticmethod
    def _validate_number(
        text: str, config: ValidationConfig
    ) -> Tuple[bool, str, Optional[str]]:
        """Validate number."""
        try:
            float(text)
            return True, "Number is valid", text
        except ValueError:
            return False, "Invalid number format", None

    @staticmethod
    def _validate_html(
        text: str, config: ValidationConfig
    ) -> Tuple[bool, str, Optional[str]]:
        """Validate and sanitize HTML."""

        # Check for malicious patterns
        for pattern in InputValidator.MALICIOUS_CONTENT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Malicious content in HTML: {pattern}", None

        # Sanitize HTML using bleach
        sanitized = bleach.clean(
            text,
            tags=config.allowed_tags,
            attributes=config.allowed_attributes,
            protocols=config.allowed_protocols,
            strip=True,
        )

        return True, "HTML is valid", sanitized

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """Sanitize text input."""
        # HTML encode special characters
        sanitized = html.escape(text)

        # Remove null bytes
        sanitized = sanitized.replace("\x00", "")

        # Remove control characters except newline and tab
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized)

        return sanitized.strip()

    @staticmethod
    def validate_file(
        file_data: bytes, filename: str, config: ValidationConfig
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Validate file upload."""

        # Check file size
        if len(file_data) > config.max_file_size:
            return False, f"File too large (max {config.max_file_size} bytes)", None

        # Check file extension
        file_ext = filename.lower().split(".")[-1] if "." in filename else ""
        if file_ext not in [ext.replace(".", "") for ext in config.allowed_file_types]:
            return False, f"File type not allowed: {file_ext}", None

        # Check for malicious patterns in filename
        for pattern in InputValidator.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                return False, f"Malicious filename pattern: {pattern}", None

        # Generate safe filename
        safe_filename = InputValidator._sanitize_filename(filename)

        return (
            True,
            "File is valid",
            {"filename": safe_filename, "size": len(file_data), "content": file_data},
        )

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename."""
        # Remove path traversal characters
        filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # Remove multiple dots
        filename = re.sub(r"\.+", ".", filename)

        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit(".", 1)
            filename = name[: 255 - len(ext) - 1] + "." + ext

        return filename


class OutputEncoder:
    """Secure output encoding to prevent XSS."""

    @staticmethod
    def encode_html(text: str) -> str:
        """Encode text for HTML output."""
        return html.escape(text)

    @staticmethod
    def encode_js(text: str) -> str:
        """Encode text for JavaScript output."""
        # Replace special characters
        encoded = text.replace("\\", "\\\\")
        encoded = encoded.replace('"', '\\"')
        encoded = encoded.replace("'", "\\'")
        encoded = encoded.replace("\n", "\\n")
        encoded = encoded.replace("\r", "\\r")
        encoded = encoded.replace("\t", "\\t")
        return encoded

    @staticmethod
    def encode_url(text: str) -> str:
        """Encode text for URL output."""
        return urllib.parse.quote(text, safe="")

    @staticmethod
    def encode_css(text: str) -> str:
        """Encode text for CSS output."""
        # CSS encoding
        encoded = text.replace("\\", "\\\\")
        encoded = encoded.replace('"', '\\"')
        encoded = encoded.replace("'", "\\'")
        return encoded


class ContentSecurityPolicy:
    """Content Security Policy (CSP) management."""

    @staticmethod
    def generate_csp_header() -> str:
        """Generate CSP header."""
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self'",
            "connect-src 'self'",
            "media-src 'self'",
            "object-src 'none'",
            "frame-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests",
        ]

        return "; ".join(csp_directives)

    @staticmethod
    def generate_nonce() -> str:
        """Generate CSP nonce."""
        import secrets

        return secrets.token_urlsafe(16)


class InputSanitizer:
    """Input sanitization utilities."""

    @staticmethod
    def sanitize_json(data: Any) -> Any:
        """Sanitize JSON data recursively."""
        if isinstance(data, dict):
            return {k: InputSanitizer.sanitize_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [InputSanitizer.sanitize_json(item) for item in data]
        elif isinstance(data, str):
            return InputValidator._sanitize_text(data)
        else:
            return data

    @staticmethod
    def sanitize_headers(headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize HTTP headers."""
        sanitized = {}

        for name, value in headers.items():
            # Sanitize header name
            safe_name = re.sub(r"[^\w\-]", "", name.lower())

            # Sanitize header value
            safe_value = InputValidator._sanitize_text(value)

            sanitized[safe_name] = safe_value

        return sanitized


# Export public API
__all__ = [
    # Classes
    "InputValidator",
    "OutputEncoder",
    "ContentSecurityPolicy",
    "InputSanitizer",
    "ValidationConfig",
    # Enums
    "ValidationLevel",
    "InputType",
]
