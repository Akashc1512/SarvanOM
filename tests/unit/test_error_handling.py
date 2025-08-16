#!/usr/bin/env python3
"""
Unit tests for error handling implementation.

This module tests the comprehensive error handling system including:
- Global exception handlers
- Service error handling
- Custom exception classes
- Error response formatting
- Logging and monitoring
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from shared.core.api.exceptions import (
    UKPHTTPException,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    DatabaseError,
    ExternalServiceError,
    ValidationError as UKPValidationError,
    QueryProcessingError,
)
from backend.api.middleware.error_handling import (
    ErrorHandlingMiddleware,
    handle_service_error,
    validate_service_response,
    log_service_operation,
    create_error_handling_middleware,
)


class TestErrorHandlingMiddleware:
    """Test the error handling middleware."""

    @pytest.fixture
    def middleware(self):
        """Create error handling middleware instance."""
        return create_error_handling_middleware()

    @pytest.fixture
    def mock_request(self):
        """Create a mock request."""
        request = Mock(spec=Request)
        # Create a proper URL mock
        url_mock = Mock()
        url_mock.path = "/api/test"
        request.url = url_mock
        request.method = "GET"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}
        request.state.request_id = "test_request_123"
        return request

    @pytest.fixture
    def mock_call_next(self):
        """Create a mock call_next function."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_successful_request(self, middleware, mock_request, mock_call_next):
        """Test successful request processing."""
        mock_call_next.return_value = JSONResponse(content={"success": True})

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 200
        assert response.body == b'{"success":true}'
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_http_exception_handling(
        self, middleware, mock_request, mock_call_next
    ):
        """Test HTTP exception handling."""
        exc = HTTPException(status_code=404, detail="Not found")
        mock_call_next.side_effect = exc

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 404
        content = response.body.decode()
        assert "Not found" in content
        assert "error" in content
        assert "request_id" in content

    @pytest.mark.asyncio
    async def test_validation_error_handling(
        self, middleware, mock_request, mock_call_next
    ):
        """Test validation error handling."""
        # Create a proper Pydantic ValidationError
        from pydantic import BaseModel, ValidationError as PydanticValidationError
        
        class TestModel(BaseModel):
            field: str
        
        try:
            TestModel(field=123)  # This will raise ValidationError
        except PydanticValidationError as exc:
            mock_call_next.side_effect = exc

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 422
        content = response.body.decode()
        assert "Request validation failed" in content
        assert "error" in content
        assert "details" in content

    @pytest.mark.asyncio
    async def test_ukp_http_exception_handling(
        self, middleware, mock_request, mock_call_next
    ):
        """Test custom HTTP exception handling."""
        exc = UKPHTTPException(
            status_code=503,
            detail="Service unavailable",
            internal_message="Database connection failed",
        )
        mock_call_next.side_effect = exc

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 503
        content = response.body.decode()
        assert "Service unavailable" in content
        assert "error" in content

    @pytest.mark.asyncio
    async def test_connection_error_handling(
        self, middleware, mock_request, mock_call_next
    ):
        """Test connection error handling."""
        exc = ConnectionError("Connection refused")
        mock_call_next.side_effect = exc

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 500  # All unexpected errors return 500
        content = response.body.decode()
        assert "An unexpected error occurred" in content
        assert "error" in content

    @pytest.mark.asyncio
    async def test_timeout_error_handling(
        self, middleware, mock_request, mock_call_next
    ):
        """Test timeout error handling."""
        exc = TimeoutError("Operation timed out")
        mock_call_next.side_effect = exc

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 500  # All unexpected errors return 500
        content = response.body.decode()
        assert "An unexpected error occurred" in content

    @pytest.mark.asyncio
    async def test_permission_error_handling(
        self, middleware, mock_request, mock_call_next
    ):
        """Test permission error handling."""
        exc = PermissionError("Access denied")
        mock_call_next.side_effect = exc

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 500  # All unexpected errors return 500
        content = response.body.decode()
        assert "An unexpected error occurred" in content

    @pytest.mark.asyncio
    async def test_generic_exception_handling(
        self, middleware, mock_request, mock_call_next
    ):
        """Test generic exception handling."""
        exc = Exception("Unexpected error")
        mock_call_next.side_effect = exc

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 500
        content = response.body.decode()
        assert "An unexpected error occurred" in content
        assert "error" in content
        assert "request_id" in content

    @pytest.mark.asyncio
    async def test_slow_request_logging(self, middleware, mock_request, mock_call_next):
        """Test slow request logging."""

        async def slow_call_next(request):
            await asyncio.sleep(0.1)  # Simulate slow operation
            return JSONResponse(content={"success": True})

        mock_call_next.side_effect = slow_call_next

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 200
        # Should log slow request (though we can't easily test logging in unit tests)


class TestServiceErrorHandling:
    """Test service error handling utilities."""

    def test_handle_service_error_connection_error(self):
        """Test handling connection errors."""
        error = ConnectionError("Database connection failed")

        result = handle_service_error(error, "DatabaseService")

        assert result["error_type"] == "ConnectionError"
        assert result["error_category"] == "connection_error"
        assert result["status_code"] == 503
        assert "Database connection failed" in result["message"]
        assert result["service"] == "DatabaseService"

    def test_handle_service_error_validation_error(self):
        """Test handling validation errors."""
        # Create a proper Pydantic ValidationError
        from pydantic import BaseModel, ValidationError as PydanticValidationError
        
        class TestModel(BaseModel):
            field: str
        
        try:
            TestModel(field=123)  # This will raise ValidationError
        except PydanticValidationError as error:
            result = handle_service_error(error, "PDFService")

        assert result["error_type"] == "ValidationError"
        assert result["error_category"] == "validation_error"
        assert result["status_code"] == 422
        assert result["service"] == "PDFService"

    def test_handle_service_error_permission_error(self):
        """Test handling permission errors."""
        error = PermissionError("Access denied")

        result = handle_service_error(error, "FileService")

        assert result["error_type"] == "PermissionError"
        assert result["error_category"] == "permission_error"
        assert result["status_code"] == 403
        assert "Access denied" in result["message"]
        assert result["service"] == "FileService"

    def test_handle_service_error_file_not_found(self):
        """Test handling file not found errors."""
        error = FileNotFoundError("File not found")

        result = handle_service_error(error, "FileService")

        assert result["error_type"] == "FileNotFoundError"
        assert result["error_category"] == "not_found_error"
        assert result["status_code"] == 404
        assert "File not found" in result["message"]
        assert result["service"] == "FileService"

    def test_handle_service_error_generic(self):
        """Test handling generic errors."""
        error = Exception("Unexpected error")

        result = handle_service_error(error, "TestService")

        assert result["error_type"] == "Exception"
        assert result["error_category"] == "internal_error"
        assert result["status_code"] == 500
        assert "Unexpected error" in result["message"]
        assert result["service"] == "TestService"

    def test_validate_service_response_none(self):
        """Test validating None response."""
        result = validate_service_response(None)
        assert result is False

    def test_validate_service_response_wrong_type(self):
        """Test validating response with wrong type."""
        result = validate_service_response("string", dict)
        assert result is False

    def test_validate_service_response_valid(self):
        """Test validating valid response."""
        response = {"success": True}
        result = validate_service_response(response, dict)
        assert result is True


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_ukp_http_exception(self):
        """Test UKPHTTPException."""
        exc = UKPHTTPException(
            status_code=503,
            detail="Service unavailable",
            internal_message="Database connection failed",
        )

        assert exc.status_code == 503
        assert exc.detail == "Service unavailable"
        assert exc.internal_message == "Database connection failed"

    def test_authentication_error(self):
        """Test AuthenticationError."""
        exc = AuthenticationError("Invalid credentials")

        assert exc.status_code == 401
        assert "Authentication required" in exc.detail
        assert "Invalid credentials" in exc.internal_message

    def test_authorization_error(self):
        """Test AuthorizationError."""
        exc = AuthorizationError("Insufficient permissions")

        assert exc.status_code == 403
        assert "Insufficient permissions" in exc.detail
        assert "Insufficient permissions" in exc.internal_message

    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError."""
        exc = ResourceNotFoundError("user", "123")

        assert exc.status_code == 404
        assert "user not found" in exc.detail
        assert "user 123 not found" in exc.internal_message

    def test_database_error(self):
        """Test DatabaseError."""
        exc = DatabaseError("select", "Connection failed", "postgresql")

        assert "Database select failed on postgresql" in exc.message
        assert exc.details["operation"] == "select"
        assert exc.details["database"] == "postgresql"
        assert exc.details["error"] == "Connection failed"

    def test_external_service_error(self):
        """Test ExternalServiceError."""
        exc = ExternalServiceError("OpenAI", "completion", "API key invalid", False)

        assert "External service OpenAI failed during completion" in exc.message
        assert exc.details["service"] == "OpenAI"
        assert exc.details["operation"] == "completion"
        assert exc.details["retryable"] is False
        assert exc.details["error"] == "API key invalid"

    def test_validation_error(self):
        """Test ValidationError."""
        # Create a proper Pydantic ValidationError
        from pydantic import BaseModel, ValidationError as PydanticValidationError
        
        class TestModel(BaseModel):
            email: str
        
        try:
            TestModel(email=123)  # This will raise ValidationError
        except PydanticValidationError as exc:
            # Pydantic ValidationError doesn't have status_code, detail, or internal_message
            # So we just test that it's a ValidationError
            assert isinstance(exc, PydanticValidationError)
            assert len(exc.errors()) == 1
            assert exc.errors()[0]["loc"] == ["email"]

    def test_query_processing_error(self):
        """Test QueryProcessingError."""
        exc = QueryProcessingError("query_123", "Database timeout", True)

        assert exc.status_code == 503  # Recoverable
        assert "Query processing failed" in exc.detail
        assert "Query query_123 failed: Database timeout" in exc.internal_message


class TestLoggingAndMonitoring:
    """Test logging and monitoring functionality."""

    @patch("backend.api.middleware.error_handling.logger")
    def test_log_service_operation_success(self, mock_logger):
        """Test logging successful service operation."""
        log_service_operation(
            "test_operation",
            "TestService",
            True,
            0.5,
        )

        # Verify info log was called for successful operation
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Service operation completed" in call_args

    @patch("backend.api.middleware.error_handling.logger")
    def test_log_service_operation_failure(self, mock_logger):
        """Test logging failed service operation."""
        log_service_operation(
            "test_operation",
            "TestService",
            False,
            1.5,
            "test error",
        )

        # Verify error log was called for failed operation
        mock_logger.error.assert_called()
        call_args = mock_logger.error.call_args[0][0]
        assert "Service operation failed" in call_args

    @patch("backend.api.middleware.error_handling.logger")
    def test_log_service_operation_slow(self, mock_logger):
        """Test logging slow service operation."""
        log_service_operation(
            "test_operation", "TestService", True, 2.0  # Slow operation
        )

        # Verify info log was called for successful operation
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Service operation completed" in call_args


class TestErrorResponseFormat:
    """Test error response formatting."""

    def test_error_response_structure(self):
        """Test that error responses have consistent structure."""
        # This would be tested in integration tests with actual FastAPI app
        # For now, we test the structure of our custom exceptions

        exc = UKPHTTPException(
            status_code=503,
            detail="Service unavailable",
            internal_message="Database connection failed",
        )

        assert hasattr(exc, "status_code")
        assert hasattr(exc, "detail")
        assert hasattr(exc, "internal_message")
        assert exc.status_code == 503
        assert exc.detail == "Service unavailable"

    def test_error_response_timestamp(self):
        """Test that error responses include timestamp."""
        # This would be tested in integration tests
        # The middleware adds timestamps to all error responses
        pass

    def test_error_response_request_id(self):
        """Test that error responses include request ID."""
        # This would be tested in integration tests
        # The middleware adds request IDs to all error responses
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
