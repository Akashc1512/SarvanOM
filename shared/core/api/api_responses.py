"""
Standardized API Response Models - MAANG Standards
Following OpenAI and Perplexity API design patterns.

Features:
- Consistent error response format
- Standardized status codes
- Request/response correlation
- Rate limiting headers
- Pagination support
- Metadata inclusion

Authors:
- Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import uuid

# Type variables for generic responses
T = TypeVar("T")


class ResponseStatus(str, Enum):
    """Standard response status values."""

    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class ErrorCode(str, Enum):
    """Standard error codes following OpenAI/Perplexity patterns."""

    # Authentication errors
    INVALID_API_KEY = "invalid_api_key"
    INVALID_AUTHENTICATION = "invalid_authentication"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"

    # Validation errors
    INVALID_REQUEST = "invalid_request"
    VALIDATION_ERROR = "validation_error"
    MISSING_REQUIRED_FIELD = "missing_required_field"

    # Processing errors
    PROCESSING_ERROR = "processing_error"
    TIMEOUT_ERROR = "timeout_error"
    SERVICE_UNAVAILABLE = "service_unavailable"

    # Resource errors
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_CONFLICT = "resource_conflict"

    # Security errors
    SECURITY_VIOLATION = "security_violation"
    MALICIOUS_INPUT = "malicious_input"


class BaseAPIResponse(BaseModel):
    """Base API response model with standard fields."""

    request_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique request identifier for tracking",
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp in ISO 8601 format",
    )

    status: ResponseStatus = Field(
        default=ResponseStatus.SUCCESS, description="Response status"
    )

    version: str = Field(default="2.0.0", description="API version")


class ErrorResponse(BaseAPIResponse):
    """Standardized error response model."""

    status: ResponseStatus = Field(
        default=ResponseStatus.ERROR, description="Error status"
    )

    error: Dict[str, Any] = Field(..., description="Error details")

    @field_validator("error")
    @classmethod
    def validate_error(cls, v):
        """Ensure error object has required fields."""
        if not isinstance(v, dict):
            raise ValueError("Error must be a dictionary")

        required_fields = ["code", "message"]
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Error missing required field: {field}")

        return v


class SuccessResponse(BaseAPIResponse, Generic[T]):
    """Standardized success response model."""

    data: T = Field(..., description="Response data")

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class PaginatedResponse(BaseAPIResponse, Generic[T]):
    """Paginated response model."""

    data: List[T] = Field(..., description="List of items")

    pagination: Dict[str, Any] = Field(..., description="Pagination information")

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class QueryResponse(SuccessResponse):
    """Query processing response."""

    data: Dict[str, Any] = Field(..., description="Query result data")

    processing_time: Optional[float] = Field(
        None, description="Processing time in seconds"
    )

    tokens_used: Optional[int] = Field(None, description="Tokens consumed")

    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence score"
    )


class HealthResponse(SuccessResponse):
    """Health check response."""

    data: Dict[str, Any] = Field(..., description="Health status information")

    uptime: float = Field(..., description="Service uptime in seconds")


class MetricsResponse(SuccessResponse):
    """Metrics response."""

    data: Dict[str, Any] = Field(..., description="Metrics data")

    time_range: Dict[str, datetime] = Field(..., description="Time range for metrics")


# Error response factories
def create_error_response(
    code: ErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400,
) -> ErrorResponse:
    """Create a standardized error response."""

    error_data = {"code": code.value, "message": message, "details": details or {}}

    return ErrorResponse(status=ResponseStatus.ERROR, error=error_data)


def create_validation_error(
    field: str, message: str, value: Any = None
) -> ErrorResponse:
    """Create a validation error response."""

    return create_error_response(
        code=ErrorCode.VALIDATION_ERROR,
        message=f"Validation error: {message}",
        details={"field": field, "value": value, "type": "validation_error"},
    )


def create_rate_limit_error(
    limit: int, window: str, retry_after: Optional[int] = None
) -> ErrorResponse:
    """Create a rate limit error response."""

    details = {"limit": limit, "window": window, "type": "rate_limit_error"}

    if retry_after:
        details["retry_after"] = retry_after

    return create_error_response(
        code=ErrorCode.RATE_LIMIT_EXCEEDED,
        message=f"Rate limit exceeded: {limit} requests per {window}",
        details=details,
    )


def create_authentication_error(
    message: str = "Authentication required", details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """Create an authentication error response."""

    return create_error_response(
        code=ErrorCode.INVALID_AUTHENTICATION,
        message=message,
        details=details or {"type": "authentication_error"},
    )


def create_permission_error(
    required_permission: str, user_permissions: List[str]
) -> ErrorResponse:
    """Create a permission error response."""

    return create_error_response(
        code=ErrorCode.INSUFFICIENT_PERMISSIONS,
        message="Insufficient permissions",
        details={
            "required_permission": required_permission,
            "user_permissions": user_permissions,
            "type": "permission_error",
        },
    )


# Response headers
def get_standard_headers(
    request_id: str, rate_limit_info: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """Get standard response headers."""

    headers = {
        "X-Request-ID": request_id,
        "X-API-Version": "2.0.0",
        "X-Response-Time": str(datetime.utcnow().timestamp()),
    }

    if rate_limit_info:
        headers.update(
            {
                "X-RateLimit-Limit": str(rate_limit_info.get("limit", 0)),
                "X-RateLimit-Remaining": str(rate_limit_info.get("remaining", 0)),
                "X-RateLimit-Reset": str(rate_limit_info.get("reset", 0)),
            }
        )

    return headers


# Utility functions
def format_response_time(start_time: float) -> float:
    """Format response time in seconds."""
    return round(datetime.utcnow().timestamp() - start_time, 3)


def validate_pagination_params(
    page: int = 1, page_size: int = 20, max_page_size: int = 100
) -> Dict[str, int]:
    """Validate and normalize pagination parameters."""

    if page < 1:
        page = 1

    if page_size < 1:
        page_size = 20
    elif page_size > max_page_size:
        page_size = max_page_size

    return {"page": page, "page_size": page_size, "offset": (page - 1) * page_size}
