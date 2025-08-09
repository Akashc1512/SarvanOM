"""
Universal Knowledge Hub - API Module
Core API components for the knowledge platform.

This module provides:
- Configuration management
- Exception handling
- API models and responses
- Monitoring and metrics

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

from .config import (
    Settings,
    get_settings,
    APISettings,
    DatabaseSettings,
    CacheSettings,
    SecuritySettings,
    AISettings,
    MonitoringSettings,
)
from .monitoring import (
    record_request,
    record_error,
    record_cache_hit,
    record_cache_miss,
    update_system_metrics,
    get_metrics_summary,
)
from .exceptions import (
    UKPException,
    UKPHTTPException,
    AuthenticationError,
    AuthorizationError,
    InvalidAPIKeyError,
    RateLimitExceededError,
    AgentError,
    AgentTimeoutError,
    AgentProcessingError,
    QueryProcessingError,
    ResourceNotFoundError,
    DatabaseError,
    CacheError,
    ExternalServiceError,
    ValidationError,
    SecurityViolationError,
    ConfigurationError,
    ExpertReviewError,
)
from .api_models import *
from .api_responses import *

__all__ = [
    "Settings",
    "get_settings",
    "APISettings",
    "DatabaseSettings",
    "CacheSettings",
    "SecuritySettings",
    "AISettings",
    "MonitoringSettings",
    "record_request",
    "record_error",
    "record_cache_hit",
    "record_cache_miss",
    "update_system_metrics",
    "get_metrics_summary",
    "UKPException",
    "UKPHTTPException",
    "AuthenticationError",
    "AuthorizationError",
    "InvalidAPIKeyError",
    "RateLimitExceededError",
    "AgentError",
    "AgentTimeoutError",
    "AgentProcessingError",
    "QueryProcessingError",
    "ResourceNotFoundError",
    "DatabaseError",
    "CacheError",
    "ExternalServiceError",
    "ValidationError",
    "SecurityViolationError",
    "ConfigurationError",
    "ExpertReviewError",
]
