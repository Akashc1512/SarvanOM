"""
Production security configuration for the Universal Knowledge Platform.

This module provides security configuration for production deployment
including authentication, authorization, and security best practices.
"""

import hashlib
import secrets
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from config.production.settings import get_security_config, get_rate_limit_config


class SecurityLevel(Enum):
    """Security level enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Security event record."""

    event_type: str
    user_id: Optional[str]
    ip_address: Optional[str]
    timestamp: datetime
    details: Dict[str, Any]
    severity: SecurityLevel


class SecurityConfig:
    """Security configuration manager."""

    def __init__(self):
        self.security_config = get_security_config()
        self.rate_limit_config = get_rate_limit_config()

        # Security settings
        self.secret_key = self.security_config.get("secret_key")
        self.algorithm = self.security_config.get("algorithm", "HS256")
        self.access_token_expire_minutes = self.security_config.get(
            "access_token_expire_minutes", 30
        )
        self.refresh_token_expire_days = self.security_config.get(
            "refresh_token_expire_days", 7
        )

        # Rate limiting
        self.rate_limit_per_minute = self.rate_limit_config.get("per_minute", 60)
        self.rate_limit_per_hour = self.rate_limit_config.get("per_hour", 1000)
        self.rate_limit_per_day = self.rate_limit_config.get("per_day", 10000)

        # Security events tracking
        self.security_events: List[SecurityEvent] = []

        # Rate limiting tracking
        self.rate_limit_tracking: Dict[str, Dict[str, List[float]]] = {}

        # Blocked IPs
        self.blocked_ips: Dict[str, datetime] = {}

        # Failed login attempts
        self.failed_logins: Dict[str, List[datetime]] = {}

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(length)

    def hash_password(self, password: str) -> str:
        """Hash a password using secure hashing."""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return f"{salt}${hash_obj.hex()}"

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            salt, hash_hex = hashed_password.split("$")
            hash_obj = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
            )
            return hash_obj.hex() == hash_hex
        except (ValueError, AttributeError):
            return False

    def check_rate_limit(self, identifier: str, limit_type: str = "per_minute") -> bool:
        """Check if rate limit is exceeded."""
        current_time = time.time()

        if identifier not in self.rate_limit_tracking:
            self.rate_limit_tracking[identifier] = {}

        if limit_type not in self.rate_limit_tracking[identifier]:
            self.rate_limit_tracking[identifier][limit_type] = []

        # Get the appropriate limit
        if limit_type == "per_minute":
            limit = self.rate_limit_per_minute
            window = 60  # 60 seconds
        elif limit_type == "per_hour":
            limit = self.rate_limit_per_hour
            window = 3600  # 3600 seconds
        elif limit_type == "per_day":
            limit = self.rate_limit_per_day
            window = 86400  # 86400 seconds
        else:
            return True  # Unknown limit type, allow

        # Clean old timestamps
        self.rate_limit_tracking[identifier][limit_type] = [
            ts
            for ts in self.rate_limit_tracking[identifier][limit_type]
            if current_time - ts < window
        ]

        # Check if limit exceeded
        if len(self.rate_limit_tracking[identifier][limit_type]) >= limit:
            return False

        # Add current timestamp
        self.rate_limit_tracking[identifier][limit_type].append(current_time)
        return True

    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked."""
        if ip_address in self.blocked_ips:
            # Check if block has expired (24 hours)
            if datetime.utcnow() - self.blocked_ips[ip_address] > timedelta(hours=24):
                del self.blocked_ips[ip_address]
                return False
            return True
        return False

    def block_ip(self, ip_address: str):
        """Block an IP address."""
        self.blocked_ips[ip_address] = datetime.utcnow()

    def record_failed_login(self, identifier: str):
        """Record a failed login attempt."""
        if identifier not in self.failed_logins:
            self.failed_logins[identifier] = []

        self.failed_logins[identifier].append(datetime.utcnow())

        # Keep only last 10 failed attempts
        if len(self.failed_logins[identifier]) > 10:
            self.failed_logins[identifier] = self.failed_logins[identifier][-10:]

    def check_account_lockout(
        self, identifier: str, max_attempts: int = 5, lockout_duration: int = 15
    ) -> bool:
        """Check if account should be locked out."""
        if identifier not in self.failed_logins:
            return False

        recent_attempts = [
            attempt
            for attempt in self.failed_logins[identifier]
            if datetime.utcnow() - attempt < timedelta(minutes=lockout_duration)
        ]

        return len(recent_attempts) >= max_attempts

    def record_security_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: SecurityLevel = SecurityLevel.MEDIUM,
    ):
        """Record a security event."""
        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=datetime.utcnow(),
            details=details or {},
            severity=severity,
        )

        self.security_events.append(event)

        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]

    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary."""
        return {
            "blocked_ips_count": len(self.blocked_ips),
            "security_events_count": len(self.security_events),
            "rate_limit_tracking_count": len(self.rate_limit_tracking),
            "failed_logins_count": len(self.failed_logins),
            "recent_security_events": [
                {
                    "event_type": event.event_type,
                    "user_id": event.user_id,
                    "ip_address": event.ip_address,
                    "timestamp": event.timestamp.isoformat(),
                    "severity": event.severity.value,
                    "details": event.details,
                }
                for event in self.security_events[-10:]  # Last 10 events
            ],
        }

    def validate_input(self, input_data: str, max_length: int = 1000) -> bool:
        """Validate input data for security."""
        if not input_data or len(input_data) > max_length:
            return False

        # Check for potentially dangerous patterns
        dangerous_patterns = [
            "<script>",
            "javascript:",
            "onload=",
            "onerror=",
            "eval(",
            "document.cookie",
            "localStorage",
            "sql injection",
            "xss",
            "csrf",
        ]

        input_lower = input_data.lower()
        for pattern in dangerous_patterns:
            if pattern in input_lower:
                return False

        return True

    def sanitize_input(self, input_data: str) -> str:
        """Sanitize input data."""
        import html

        # HTML escape
        sanitized = html.escape(input_data)

        # Remove potentially dangerous characters
        sanitized = sanitized.replace("'", "&#39;")
        sanitized = sanitized.replace('"', "&#34;")

        return sanitized

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            "algorithm": self.algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "refresh_token_expire_days": self.refresh_token_expire_days,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "rate_limit_per_hour": self.rate_limit_per_hour,
            "rate_limit_per_day": self.rate_limit_per_day,
            "blocked_ips_count": len(self.blocked_ips),
            "security_events_count": len(self.security_events),
        }


# Global security instance
security_config = SecurityConfig()


def get_security() -> SecurityConfig:
    """Get security configuration instance."""
    return security_config


def validate_api_key(api_key: str) -> bool:
    """Validate API key format and strength."""
    if not api_key or len(api_key) < 32:
        return False

    # Check for basic security requirements
    has_upper = any(c.isupper() for c in api_key)
    has_lower = any(c.islower() for c in api_key)
    has_digit = any(c.isdigit() for c in api_key)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in api_key)

    return has_upper and has_lower and has_digit and has_special


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength."""
    result = {"valid": True, "score": 0, "issues": []}

    if len(password) < 8:
        result["valid"] = False
        result["issues"].append("Password must be at least 8 characters long")

    if not any(c.isupper() for c in password):
        result["score"] += 1
        result["issues"].append("Add uppercase letters")

    if not any(c.islower() for c in password):
        result["score"] += 1
        result["issues"].append("Add lowercase letters")

    if not any(c.isdigit() for c in password):
        result["score"] += 1
        result["issues"].append("Add numbers")

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        result["score"] += 1
        result["issues"].append("Add special characters")

    if len(password) >= 12:
        result["score"] += 2
    elif len(password) >= 10:
        result["score"] += 1

    return result


def check_security_compliance() -> Dict[str, Any]:
    """Check security compliance."""
    security = get_security()

    compliance = {"overall_compliant": True, "checks": {}}

    # Check secret key strength
    if len(security.secret_key) < 32:
        compliance["checks"]["secret_key"] = {
            "compliant": False,
            "issue": "Secret key too short",
        }
        compliance["overall_compliant"] = False
    else:
        compliance["checks"]["secret_key"] = {"compliant": True, "issue": None}

    # Check rate limiting configuration
    if security.rate_limit_per_minute < 10:
        compliance["checks"]["rate_limiting"] = {
            "compliant": False,
            "issue": "Rate limiting too permissive",
        }
        compliance["overall_compliant"] = False
    else:
        compliance["checks"]["rate_limiting"] = {"compliant": True, "issue": None}

    # Check token expiration
    if security.access_token_expire_minutes > 60:
        compliance["checks"]["token_expiration"] = {
            "compliant": False,
            "issue": "Access token expiration too long",
        }
        compliance["overall_compliant"] = False
    else:
        compliance["checks"]["token_expiration"] = {"compliant": True, "issue": None}

    return compliance


def get_security_status() -> Dict[str, Any]:
    """Get comprehensive security status."""
    security = get_security()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "compliance": check_security_compliance(),
        "summary": security.get_security_summary(),
        "configuration": security.get_security_config(),
        "blocked_ips": list(security.blocked_ips.keys()),
        "rate_limit_status": {
            "tracking_count": len(security.rate_limit_tracking),
            "blocked_ips_count": len(security.blocked_ips),
            "failed_logins_count": len(security.failed_logins),
        },
    }
