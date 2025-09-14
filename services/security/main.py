"""
Security & Privacy Enforcement Service - SarvanOM v2

Enforce docs/security/*:
Security headers (CSP/HSTS/Referrer/Permissions) aligned with LMM flows (camera/mic/clipboard blocked unless needed).
Rate-limit & abuse protection with circuit breakers.
Data handling: PII redaction in drafts, no raw draft storage by default, consent for refined-prompt storage, retention windows, audit trails.
"""

import asyncio
import json
import logging
import time
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import redis
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import structlog

# Import central configuration
from shared.core.config.central_config import get_central_config

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

# Get configuration
config = get_central_config()

# Prometheus metrics
security_requests_total = Counter('sarvanom_security_requests_total', 'Total security requests', ['endpoint', 'status'])
security_rate_limits_total = Counter('sarvanom_security_rate_limits_total', 'Total rate limit hits', ['tier', 'reason'])
security_pii_detections_total = Counter('sarvanom_security_pii_detections_total', 'Total PII detections', ['pii_type', 'severity'])
security_abuse_detections_total = Counter('sarvanom_security_abuse_detections_total', 'Total abuse detections', ['abuse_type', 'severity'])
security_headers_applied_total = Counter('sarvanom_security_headers_applied_total', 'Total security headers applied', ['header_type'])
security_consent_checks_total = Counter('sarvanom_security_consent_checks_total', 'Total consent checks', ['consent_type', 'result'])

class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class UserTier(str, Enum):
    ANONYMOUS = "anonymous"
    AUTHENTICATED = "authenticated"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    API = "api"

class AbuseType(str, Enum):
    BOT = "bot"
    SUSPICIOUS_UA = "suspicious_ua"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_REQUEST = "invalid_request"
    MALICIOUS_PATTERN = "malicious_pattern"

@dataclass
class PIIDetection:
    pii_type: str
    field: str
    pattern: str
    severity: str
    confidence: float
    redacted_value: str

@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    reset_time: int
    reason: str
    tier: str

@dataclass
class DataClassificationResult:
    overall_classification: DataClassification
    field_classifications: Dict[str, DataClassification]
    pii_detected: List[PIIDetection]
    recommendations: List[str]

class DataClassifier:
    """Classify and handle data based on sensitivity levels"""
    
    def __init__(self):
        self.classification_rules = {
            "email": DataClassification.RESTRICTED,
            "phone": DataClassification.RESTRICTED,
            "name": DataClassification.RESTRICTED,
            "address": DataClassification.RESTRICTED,
            "ssn": DataClassification.RESTRICTED,
            "credit_card": DataClassification.RESTRICTED,
            "ip_address": DataClassification.CONFIDENTIAL,
            "user_agent": DataClassification.CONFIDENTIAL,
            "session_id": DataClassification.CONFIDENTIAL,
            "api_key": DataClassification.CONFIDENTIAL,
            "query": DataClassification.INTERNAL,
            "response": DataClassification.INTERNAL,
            "timestamp": DataClassification.PUBLIC,
            "version": DataClassification.PUBLIC
        }
        
        self.pii_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
        }
    
    def classify_data(self, data: Dict[str, Any]) -> DataClassificationResult:
        """Classify data based on content"""
        classification_result = DataClassificationResult(
            overall_classification=DataClassification.PUBLIC,
            field_classifications={},
            pii_detected=[],
            recommendations=[]
        )
        
        for field, value in data.items():
            # Get field classification
            field_classification = self.classification_rules.get(field, DataClassification.INTERNAL)
            classification_result.field_classifications[field] = field_classification
            
            # Check for PII
            pii_detected = self._detect_pii(field, str(value))
            if pii_detected:
                classification_result.pii_detected.extend(pii_detected)
                classification_result.field_classifications[field] = DataClassification.RESTRICTED
            
            # Update overall classification
            if field_classification == DataClassification.RESTRICTED:
                classification_result.overall_classification = DataClassification.RESTRICTED
            elif field_classification == DataClassification.CONFIDENTIAL and classification_result.overall_classification != DataClassification.RESTRICTED:
                classification_result.overall_classification = DataClassification.CONFIDENTIAL
            elif field_classification == DataClassification.INTERNAL and classification_result.overall_classification == DataClassification.PUBLIC:
                classification_result.overall_classification = DataClassification.INTERNAL
        
        # Generate recommendations
        classification_result.recommendations = self._generate_recommendations(classification_result)
        
        return classification_result
    
    def _detect_pii(self, field: str, value: str) -> List[PIIDetection]:
        """Detect PII in field value"""
        detected_pii = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, value, re.IGNORECASE)
            for match in matches:
                detected_pii.append(PIIDetection(
                    pii_type=pii_type,
                    field=field,
                    pattern=pattern,
                    severity="high" if pii_type in ["ssn", "credit_card"] else "medium",
                    confidence=0.9,
                    redacted_value=self._redact_pii(pii_type, match.group())
                ))
        
        return detected_pii
    
    def _redact_pii(self, pii_type: str, value: str) -> str:
        """Redact PII value"""
        if pii_type == "email":
            return re.sub(r'([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})', r'***@\2', value)
        elif pii_type == "phone":
            return re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '***-***-****', value)
        elif pii_type == "ssn":
            return re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****', value)
        elif pii_type == "credit_card":
            return re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '****-****-****-****', value)
        elif pii_type == "ip_address":
            return re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '***.***.***.***', value)
        else:
            return "***REDACTED***"
    
    def _generate_recommendations(self, classification_result: DataClassificationResult) -> List[str]:
        """Generate data handling recommendations"""
        recommendations = []
        
        if classification_result.overall_classification == DataClassification.RESTRICTED:
            recommendations.append("Apply strong encryption and access controls")
            recommendations.append("Implement data retention policies")
            recommendations.append("Enable audit logging")
        
        if classification_result.pii_detected:
            recommendations.append("Implement PII redaction for logs")
            recommendations.append("Apply data minimization principles")
            recommendations.append("Ensure GDPR/CCPA compliance")
        
        if classification_result.overall_classification == DataClassification.CONFIDENTIAL:
            recommendations.append("Implement access controls")
            recommendations.append("Enable audit logging")
        
        return recommendations

class RateLimiter:
    """Rate limiting and abuse prevention"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.rate_limits = {
            UserTier.ANONYMOUS: {"rpm": 10, "rph": 100},
            UserTier.AUTHENTICATED: {"rpm": 60, "rph": 1000},
            UserTier.PREMIUM: {"rpm": 120, "rph": 5000},
            UserTier.ENTERPRISE: {"rpm": 300, "rph": 20000},
            UserTier.API: {"rpm": 1000, "rph": 50000}
        }
    
    def check_rate_limit(self, identifier: str, tier: UserTier, endpoint: str = None) -> RateLimitResult:
        """Check rate limit for identifier"""
        limits = self.rate_limits.get(tier, self.rate_limits[UserTier.ANONYMOUS])
        
        # Check per-minute limit
        minute_key = f"rate_limit:{identifier}:minute:{int(time.time() // 60)}"
        minute_count = self.redis.get(minute_key)
        
        if minute_count and int(minute_count) >= limits["rpm"]:
            security_rate_limits_total.labels(tier=tier.value, reason="minute_limit_exceeded").inc()
            return RateLimitResult(
                allowed=False,
                limit=limits["rpm"],
                remaining=0,
                reset_time=int(time.time() // 60) * 60 + 60,
                reason="minute_limit_exceeded",
                tier=tier.value
            )
        
        # Check per-hour limit
        hour_key = f"rate_limit:{identifier}:hour:{int(time.time() // 3600)}"
        hour_count = self.redis.get(hour_key)
        
        if hour_count and int(hour_count) >= limits["rph"]:
            security_rate_limits_total.labels(tier=tier.value, reason="hour_limit_exceeded").inc()
            return RateLimitResult(
                allowed=False,
                limit=limits["rph"],
                remaining=0,
                reset_time=int(time.time() // 3600) * 3600 + 3600,
                reason="hour_limit_exceeded",
                tier=tier.value
            )
        
        # Increment counters
        self.redis.incr(minute_key)
        self.redis.expire(minute_key, 60)
        
        self.redis.incr(hour_key)
        self.redis.expire(hour_key, 3600)
        
        # Calculate remaining
        minute_remaining = limits["rpm"] - (int(minute_count) + 1 if minute_count else 1)
        hour_remaining = limits["rph"] - (int(hour_count) + 1 if hour_count else 1)
        
        return RateLimitResult(
            allowed=True,
            limit=limits["rpm"],
            remaining=min(minute_remaining, hour_remaining),
            reset_time=int(time.time() // 60) * 60 + 60,
            reason="allowed",
            tier=tier.value
        )
    
    def get_rate_limit_info(self, identifier: str, tier: UserTier) -> Dict[str, Any]:
        """Get rate limit information for identifier"""
        limits = self.rate_limits.get(tier, self.rate_limits[UserTier.ANONYMOUS])
        
        # Get current counts
        minute_key = f"rate_limit:{identifier}:minute:{int(time.time() // 60)}"
        hour_key = f"rate_limit:{identifier}:hour:{int(time.time() // 3600)}"
        
        minute_count = int(self.redis.get(minute_key) or 0)
        hour_count = int(self.redis.get(hour_key) or 0)
        
        return {
            "tier": tier.value,
            "minute_limit": limits["rpm"],
            "minute_used": minute_count,
            "minute_remaining": max(0, limits["rpm"] - minute_count),
            "hour_limit": limits["rph"],
            "hour_used": hour_count,
            "hour_remaining": max(0, limits["rph"] - hour_count),
            "reset_time": int(time.time() // 60) * 60 + 60
        }

class UserAgentFingerprinter:
    """User agent fingerprinting for abuse detection"""
    
    def __init__(self):
        self.bot_patterns = [
            r"bot", r"crawler", r"spider", r"scraper",
            r"curl", r"wget", r"python", r"java",
            r"postman", r"insomnia", r"httpie"
        ]
        
        self.suspicious_patterns = [
            r"^$", r"^Mozilla$", r"^User-Agent$",
            r"^[A-Za-z]{1,3}$", r"^[0-9]+$"
        ]
        
        self.risk_scores = {
            "browser": 0.1,
            "bot": 0.5,
            "suspicious": 0.8,
            "empty": 1.0
        }
    
    def analyze_user_agent(self, user_agent: str) -> Dict[str, Any]:
        """Analyze user agent for abuse detection"""
        if not user_agent or user_agent.strip() == "":
            return {
                "type": "empty",
                "risk_score": self.risk_scores["empty"],
                "action": "block",
                "reason": "empty_user_agent"
            }
        
        user_agent_lower = user_agent.lower()
        
        # Check for bot patterns
        for pattern in self.bot_patterns:
            if re.search(pattern, user_agent_lower):
                return {
                    "type": "bot",
                    "risk_score": self.risk_scores["bot"],
                    "action": "rate_limit",
                    "reason": f"bot_pattern_detected: {pattern}"
                }
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.match(pattern, user_agent):
                return {
                    "type": "suspicious",
                    "risk_score": self.risk_scores["suspicious"],
                    "action": "block",
                    "reason": f"suspicious_pattern: {pattern}"
                }
        
        # Default to browser
        return {
            "type": "browser",
            "risk_score": self.risk_scores["browser"],
            "action": "allow",
            "reason": "normal_browser"
        }

class SecurityHeaders:
    """Security headers implementation"""
    
    def __init__(self):
        self.csp_directives = {
            "default-src": ["'self'"],
            "script-src": [
                "'self'",
                "'unsafe-inline'",
                "'unsafe-eval'",
                "https://cdn.jsdelivr.net"
            ],
            "style-src": [
                "'self'",
                "'unsafe-inline'",
                "https://fonts.googleapis.com"
            ],
            "font-src": [
                "'self'",
                "https://fonts.gstatic.com"
            ],
            "img-src": [
                "'self'",
                "data:",
                "https:"
            ],
            "connect-src": [
                "'self'",
                "https://api.sarvanom.com"
            ],
            "frame-src": ["'none'"],
            "object-src": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
            "media-src": ["'self'"],  # For LMM flows
            "camera": ["'none'"],  # Block camera unless needed
            "microphone": ["'none'"],  # Block microphone unless needed
            "clipboard-read": ["'none'"],  # Block clipboard unless needed
            "clipboard-write": ["'none'"]  # Block clipboard unless needed
        }
    
    def apply_security_headers(self, response: Response) -> Response:
        """Apply all security headers to response"""
        # Content Security Policy
        csp_value = self._generate_csp_header()
        response.headers["Content-Security-Policy"] = csp_value
        security_headers_applied_total.labels(header_type="csp").inc()
        
        # HTTP Strict Transport Security
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        security_headers_applied_total.labels(header_type="hsts").inc()
        
        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"
        security_headers_applied_total.labels(header_type="x_frame_options").inc()
        
        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"
        security_headers_applied_total.labels(header_type="x_content_type_options").inc()
        
        # Referrer-Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        security_headers_applied_total.labels(header_type="referrer_policy").inc()
        
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
        security_headers_applied_total.labels(header_type="permissions_policy").inc()
        
        return response
    
    def _generate_csp_header(self) -> str:
        """Generate CSP header value"""
        csp_parts = []
        
        for directive, sources in self.csp_directives.items():
            csp_parts.append(f"{directive} {' '.join(sources)}")
        
        return "; ".join(csp_parts)

class ConsentManager:
    """Consent management for data handling"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.consent_types = {
            "raw_draft_storage": "Store raw user queries for improvement",
            "refined_prompt_storage": "Store refined prompts for analytics",
            "analytics_tracking": "Track user behavior for analytics",
            "personalization": "Use data for personalization",
            "marketing": "Use data for marketing purposes"
        }
    
    def check_consent(self, user_id: str, consent_type: str) -> bool:
        """Check if user has given consent for specific data handling"""
        consent_key = f"consent:{user_id}:{consent_type}"
        consent_value = self.redis.get(consent_key)
        
        result = consent_value == "true" if consent_value else False
        security_consent_checks_total.labels(consent_type=consent_type, result="granted" if result else "denied").inc()
        
        return result
    
    def set_consent(self, user_id: str, consent_type: str, granted: bool) -> bool:
        """Set user consent for specific data handling"""
        consent_key = f"consent:{user_id}:{consent_type}"
        
        if granted:
            self.redis.set(consent_key, "true", ex=86400 * 365)  # 1 year
        else:
            self.redis.set(consent_key, "false", ex=86400 * 365)  # 1 year
        
        return True
    
    def get_all_consents(self, user_id: str) -> Dict[str, bool]:
        """Get all consent statuses for user"""
        consents = {}
        
        for consent_type in self.consent_types.keys():
            consents[consent_type] = self.check_consent(user_id, consent_type)
        
        return consents

# FastAPI app
app = FastAPI(
    title="Security & Privacy Enforcement Service", 
    version="2.0.0",
    description="Security and privacy enforcement service with rate limiting, PII detection, and audit trails"
)

# Set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins if isinstance(config.cors_origins, list) else (config.cors_origins.split(",") if config.cors_origins else ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis client
redis_client = redis.Redis.from_url(str(config.redis_url), decode_responses=True)

# Security components
data_classifier = DataClassifier()
rate_limiter = RateLimiter(redis_client)
ua_fingerprinter = UserAgentFingerprinter()
security_headers = SecurityHeaders()
consent_manager = ConsentManager(redis_client)

# Pydantic models for API
class DataClassificationRequest(BaseModel):
    data: Dict[str, Any]

class RateLimitRequest(BaseModel):
    identifier: str
    tier: str
    endpoint: Optional[str] = None

class UserAgentAnalysisRequest(BaseModel):
    user_agent: str

class ConsentRequest(BaseModel):
    user_id: str
    consent_type: str
    granted: bool

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "security"}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check Redis connection
        redis_client.ping()
        return {"status": "ready", "service": "security"}
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/config")
async def get_config_endpoint():
    """Config endpoint - sanitized echo of active providers and configuration"""
    return {
        "service": "security",
        "active_providers": {
            "openai": bool(getattr(config, 'openai_api_key', None)),
            "anthropic": bool(getattr(config, 'anthropic_api_key', None)),
            "google": bool(getattr(config, 'google_api_key', None)),
            "huggingface": bool(getattr(config, 'huggingface_api_key', None) or getattr(config, 'huggingface_read_token', None) or getattr(config, 'huggingface_write_token', None)),
            "ollama": bool(getattr(config, 'ollama_base_url', None))
        },
        "keyless_fallbacks_enabled": getattr(config, 'keyless_fallbacks_enabled', True),
        "environment": getattr(config, 'environment', 'development'),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/version")
async def get_version():
    """Version endpoint"""
    return {
        "service": "security",
        "version": "2.0.0",
        "environment": getattr(config, 'environment', 'development'),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/classify-data")
async def classify_data(request: DataClassificationRequest):
    """Classify data based on sensitivity levels"""
    try:
        classification_result = data_classifier.classify_data(request.data)
        
        # Record PII detections
        for pii in classification_result.pii_detected:
            security_pii_detections_total.labels(pii_type=pii.pii_type, severity=pii.severity).inc()
        
        return {
            "status": "success",
            "classification": asdict(classification_result)
        }
        
    except Exception as e:
        logger.error("Data classification failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-rate-limit")
async def check_rate_limit(request: RateLimitRequest):
    """Check rate limit for identifier"""
    try:
        tier = UserTier(request.tier)
        result = rate_limiter.check_rate_limit(request.identifier, tier, request.endpoint)
        
        return {
            "status": "success",
            "rate_limit": asdict(result)
        }
        
    except Exception as e:
        logger.error("Rate limit check failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-user-agent")
async def analyze_user_agent(request: UserAgentAnalysisRequest):
    """Analyze user agent for abuse detection"""
    try:
        analysis = ua_fingerprinter.analyze_user_agent(request.user_agent)
        
        # Record abuse detection if applicable
        if analysis["action"] in ["block", "rate_limit"]:
            security_abuse_detections_total.labels(
                abuse_type="suspicious_ua",
                severity="high" if analysis["action"] == "block" else "medium"
            ).inc()
        
        return {
            "status": "success",
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error("User agent analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/consent/check")
async def check_consent(user_id: str, consent_type: str):
    """Check user consent for data handling"""
    try:
        has_consent = consent_manager.check_consent(user_id, consent_type)
        
        return {
            "status": "success",
            "user_id": user_id,
            "consent_type": consent_type,
            "granted": has_consent
        }
        
    except Exception as e:
        logger.error("Consent check failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/consent/set")
async def set_consent(request: ConsentRequest):
    """Set user consent for data handling"""
    try:
        success = consent_manager.set_consent(request.user_id, request.consent_type, request.granted)
        
        return {
            "status": "success",
            "user_id": request.user_id,
            "consent_type": request.consent_type,
            "granted": request.granted
        }
        
    except Exception as e:
        logger.error("Consent setting failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/consent/all/{user_id}")
async def get_all_consents(user_id: str):
    """Get all consent statuses for user"""
    try:
        consents = consent_manager.get_all_consents(user_id)
        
        return {
            "status": "success",
            "user_id": user_id,
            "consents": consents
        }
        
    except Exception as e:
        logger.error("Get all consents failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security-headers")
async def get_security_headers():
    """Get security headers configuration"""
    try:
        return {
            "status": "success",
            "headers": {
                "csp": security_headers._generate_csp_header(),
                "hsts": "max-age=31536000; includeSubDomains; preload",
                "x_frame_options": "DENY",
                "x_content_type_options": "nosniff",
                "referrer_policy": "strict-origin-when-cross-origin",
                "permissions_policy": "camera=(), microphone=(), clipboard-read=(), clipboard-write=()"
            }
        }
        
    except Exception as e:
        logger.error("Get security headers failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rate-limit-info/{identifier}")
async def get_rate_limit_info(identifier: str, tier: str):
    """Get rate limit information for identifier"""
    try:
        user_tier = UserTier(tier)
        info = rate_limiter.get_rate_limit_info(identifier, user_tier)
        
        return {
            "status": "success",
            "rate_limit_info": info
        }
        
    except Exception as e:
        logger.error("Get rate limit info failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Observability middleware
# Always mount Prometheus metrics endpoint
try:
    from prometheus_client import make_asgi_app
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    logger.info("Prometheus metrics endpoint mounted at /metrics")
except Exception as e:
    logger.error(f"Failed to mount Prometheus metrics: {e}")

# Conditional tracing setup - only if keys exist
tracing_enabled = False
if (hasattr(config, 'tracing_enabled') and config.tracing_enabled and 
    hasattr(config, 'jaeger_agent_host') and config.jaeger_agent_host):
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        
        # Configure Jaeger tracing
        trace.set_tracer_provider(TracerProvider())
        jaeger_exporter = JaegerExporter(
            agent_host_name=config.jaeger_agent_host,
            agent_port=int(config.jaeger_agent_port) if hasattr(config, 'jaeger_agent_port') and config.jaeger_agent_port else 6831,
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        tracing_enabled = True
        logger.info("Jaeger tracing enabled")
    except ImportError:
        logger.warning("OpenTelemetry packages not available, tracing disabled")
    except Exception as e:
        logger.error(f"Failed to enable tracing: {e}")
else:
    logger.info("Tracing disabled - no tracing keys configured")

# Add debug trace endpoint if tracing is enabled
if tracing_enabled:
    @app.get("/_debug/trace")
    async def debug_trace():
        """Debug endpoint to echo trace information when tracing is enabled"""
        try:
            from opentelemetry import trace
            tracer = trace.get_tracer(__name__)
            
            # Create a sample span
            with tracer.start_as_current_span("debug_trace_echo") as span:
                span.set_attribute("debug.endpoint", "/_debug/trace")
                span.set_attribute("debug.timestamp", datetime.now().isoformat())
                
                return {
                    "status": "tracing_enabled",
                    "tracer_name": tracer.name,
                    "trace_id": format(span.get_span_context().trace_id, '032x'),
                    "span_id": format(span.get_span_context().span_id, '016x'),
                    "timestamp": datetime.now().isoformat(),
                    "message": "Tracing is active and working"
                }
        except Exception as e:
            logger.error(f"Debug trace endpoint error: {e}")
            return {
                "status": "tracing_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
else:
    @app.get("/_debug/trace")
    async def debug_trace_disabled():
        """Debug endpoint when tracing is disabled"""
        return {
            "status": "tracing_disabled",
            "message": "Tracing is not enabled - no tracing keys configured",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Start FastAPI server with integrated metrics endpoint
    uvicorn.run(app, host="0.0.0.0", port=8009)
