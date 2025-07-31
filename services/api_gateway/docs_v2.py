"""
Enhanced API Documentation Generator - MAANG Standards
Following OpenAI and Perplexity API documentation patterns.

Features:
- Comprehensive endpoint documentation
- Request/response examples
- Error code documentation
- SDK examples in multiple languages
- Interactive documentation
- Rate limiting documentation
- Authentication guides

Documentation Standards:
- Clear endpoint descriptions
- Complete request/response schemas
- Error handling examples
- Code samples in Python, JavaScript, cURL
- Rate limiting details
- Security considerations

Authors:
- Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

from typing import Dict, Any, List, Optional
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from enum import Enum
import json
import yaml
import logging

from shared.core.api.api_responses import ErrorCode, ResponseStatus
from shared.core.api.validators_v2 import (
    QueryRequestValidator,
    BatchQueryRequestValidator,
    FeedbackRequestValidator,
    SearchRequestValidator,
)

logger = logging.getLogger(__name__)


class APIVersion(str, Enum):
    """API versions."""

    V1 = "v1"
    V2 = "v2"


class DocumentationConfig:
    """Enhanced API documentation configuration."""

    def __init__(self):
        # API metadata
        self.title = "Universal Knowledge Platform API"
        self.description = """
        # Universal Knowledge Platform API

        A comprehensive API for intelligent knowledge retrieval and processing, following OpenAI and Perplexity design patterns.

        ## Features

        - **Intelligent Query Processing**: Advanced AI-powered query understanding
        - **Multi-Source Knowledge**: Integration with multiple knowledge bases
        - **Real-time Responses**: Fast, accurate responses with source citations
        - **User Management**: Secure authentication and user management
        - **Analytics**: Comprehensive usage analytics and insights
        - **Rate Limiting**: Fair usage policies with rate limiting
        - **Security**: Enterprise-grade security with threat detection

        ## Authentication

        The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

        ```bash
        Authorization: Bearer <your-token>
        ```

        ## Rate Limiting

        - **Standard Users**: 60 requests per minute
        - **Premium Users**: 200 requests per minute
        - **Enterprise Users**: 1000 requests per minute

        Rate limit headers are included in all responses:
        - `X-RateLimit-Limit`: Maximum requests per window
        - `X-RateLimit-Remaining`: Remaining requests in current window
        - `X-RateLimit-Reset`: Time when the rate limit resets

        ## Error Handling

        The API returns standard HTTP status codes and detailed error messages:

        - `400 Bad Request`: Invalid request data
        - `401 Unauthorized`: Invalid or missing authentication
        - `403 Forbidden`: Insufficient permissions
        - `404 Not Found`: Resource not found
        - `429 Too Many Requests`: Rate limit exceeded
        - `500 Internal Server Error`: Server error

        ## Response Format

        All responses follow a standardized format:

        ```json
        {
          "request_id": "uuid",
          "timestamp": "2024-12-28T10:30:00Z",
          "status": "success",
          "version": "2.0.0",
          "data": { ... },
          "metadata": { ... }
        }
        ```

        ## SDK Support

        Official SDKs are available for:
        - Python
        - JavaScript/TypeScript
        - Go
        - Java
        - C#

        ## Examples

        ### Basic Query

        ```python
        import requests

        response = requests.post(
            "https://api.universal-knowledge-hub.com/v2/query",
            headers={"Authorization": "Bearer YOUR_API_KEY"},
            json={
                "query": "What is machine learning?",
                "max_tokens": 1000,
                "confidence_threshold": 0.8
            }
        )
        ```

        ### Batch Processing

        ```python
        response = requests.post(
            "https://api.universal-knowledge-hub.com/v2/batch/query",
            headers={"Authorization": "Bearer YOUR_API_KEY"},
            json={
                "queries": [
                    {"query": "What is AI?"},
                    {"query": "Explain neural networks"}
                ]
            }
        )
        ```
        """

        # Contact information
        self.contact = {
            "name": "Universal Knowledge Platform Support",
            "email": "support@universal-knowledge-hub.com",
            "url": "https://docs.universal-knowledge-hub.com",
        }

        # License
        self.license = {"name": "MIT", "url": "https://opensource.org/licenses/MIT"}


class EnhancedAPIDocumentationGenerator:
    """Enhanced API documentation generator."""

    def __init__(self, app: FastAPI):
        self.app = app
        self.config = DocumentationConfig()

    def generate_openapi_schema(self) -> Dict[str, Any]:
        """Generate enhanced OpenAPI schema."""
        schema = get_openapi(
            title=self.config.title,
            version="2.0.0",
            description=self.config.description,
            routes=self.app.routes,
        )

        # Add enhanced components
        self._add_enhanced_components(schema)
        self._add_examples(schema)
        self._add_error_responses(schema)
        self._add_rate_limiting_docs(schema)
        self._add_security_schemes(schema)
        self._add_sdk_examples(schema)

        return schema

    def _add_enhanced_components(self, schema: Dict[str, Any]) -> None:
        """Add enhanced component schemas."""
        components = schema.get("components", {})

        # Enhanced error responses
        components["ErrorResponse"] = {
            "type": "object",
            "properties": {
                "request_id": {"type": "string", "format": "uuid"},
                "timestamp": {"type": "string", "format": "date-time"},
                "status": {"type": "string", "enum": ["error"]},
                "version": {"type": "string"},
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"},
                        "details": {"type": "object"},
                    },
                    "required": ["code", "message"],
                },
            },
            "required": ["request_id", "timestamp", "status", "version", "error"],
        }

        # Enhanced success responses
        components["SuccessResponse"] = {
            "type": "object",
            "properties": {
                "request_id": {"type": "string", "format": "uuid"},
                "timestamp": {"type": "string", "format": "date-time"},
                "status": {"type": "string", "enum": ["success"]},
                "version": {"type": "string"},
                "data": {"type": "object"},
                "metadata": {"type": "object"},
            },
            "required": ["request_id", "timestamp", "status", "version", "data"],
        }

        # Query request schema
        components["QueryRequest"] = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 10000,
                    "description": "The query to process",
                },
                "max_tokens": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100000,
                    "default": 1000,
                    "description": "Maximum tokens for response",
                },
                "confidence_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.7,
                    "description": "Minimum confidence threshold",
                },
                "language": {
                    "type": "string",
                    "default": "en",
                    "enum": ["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"],
                    "description": "Query language",
                },
                "search_type": {
                    "type": "string",
                    "default": "hybrid",
                    "enum": ["hybrid", "vector", "keyword", "graph"],
                    "description": "Type of search to perform",
                },
                "include_sources": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include source citations",
                },
                "metadata": {"type": "object", "description": "Additional metadata"},
            },
            "required": ["query"],
        }

        # Query response schema
        components["QueryResponse"] = {
            "type": "object",
            "properties": {
                "request_id": {"type": "string", "format": "uuid"},
                "timestamp": {"type": "string", "format": "date-time"},
                "status": {"type": "string", "enum": ["success"]},
                "version": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "answer": {"type": "string"},
                        "confidence": {"type": "number"},
                        "query_id": {"type": "string"},
                        "sources": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "url": {"type": "string"},
                                    "relevance": {"type": "number"},
                                },
                            },
                        },
                    },
                },
                "processing_time": {"type": "number"},
                "tokens_used": {"type": "integer"},
                "confidence": {"type": "number"},
            },
        }

        schema["components"] = components

    def _add_examples(self, schema: Dict[str, Any]) -> None:
        """Add comprehensive examples."""
        paths = schema.get("paths", {})

        # Query endpoint examples
        if "/v2/query" in paths:
            paths["/v2/query"]["post"]["examples"] = {
                "basic_query": {
                    "summary": "Basic query example",
                    "value": {
                        "query": "What is machine learning?",
                        "max_tokens": 1000,
                        "confidence_threshold": 0.8,
                    },
                },
                "advanced_query": {
                    "summary": "Advanced query with metadata",
                    "value": {
                        "query": "Explain neural networks in detail",
                        "max_tokens": 2000,
                        "confidence_threshold": 0.9,
                        "language": "en",
                        "search_type": "hybrid",
                        "include_sources": True,
                        "metadata": {
                            "user_id": "user123",
                            "session_id": "session456",
                            "context": "educational",
                        },
                    },
                },
            }

        # Batch query examples
        if "/v2/batch/query" in paths:
            paths["/v2/batch/query"]["post"]["examples"] = {
                "batch_queries": {
                    "summary": "Batch processing example",
                    "value": {
                        "queries": [
                            {
                                "query": "What is artificial intelligence?",
                                "max_tokens": 500,
                            },
                            {"query": "Explain deep learning", "max_tokens": 800},
                        ],
                        "parallel_processing": True,
                        "timeout_seconds": 300,
                    },
                }
            }

    def _add_error_responses(self, schema: Dict[str, Any]) -> None:
        """Add comprehensive error response documentation."""
        paths = schema.get("paths", {})

        # Standard error responses for all endpoints
        error_responses = {
            "400": {
                "description": "Bad Request",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "examples": {
                            "validation_error": {
                                "summary": "Validation Error",
                                "value": {
                                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                                    "timestamp": "2024-12-28T10:30:00Z",
                                    "status": "error",
                                    "version": "2.0.0",
                                    "error": {
                                        "code": "validation_error",
                                        "message": "Validation error: Query too short",
                                        "details": {
                                            "field": "query",
                                            "value": "",
                                            "type": "validation_error",
                                        },
                                    },
                                },
                            },
                            "malicious_input": {
                                "summary": "Security Violation",
                                "value": {
                                    "request_id": "550e8400-e29b-41d4-a716-446655440001",
                                    "timestamp": "2024-12-28T10:30:00Z",
                                    "status": "error",
                                    "version": "2.0.0",
                                    "error": {
                                        "code": "security_violation",
                                        "message": "Request blocked by security policy",
                                        "details": {
                                            "type": "malicious_input",
                                            "detected": "SQL injection attempt",
                                        },
                                    },
                                },
                            },
                        },
                    }
                },
            },
            "401": {
                "description": "Unauthorized",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "examples": {
                            "invalid_token": {
                                "summary": "Invalid Authentication",
                                "value": {
                                    "request_id": "550e8400-e29b-41d4-a716-446655440002",
                                    "timestamp": "2024-12-28T10:30:00Z",
                                    "status": "error",
                                    "version": "2.0.0",
                                    "error": {
                                        "code": "invalid_authentication",
                                        "message": "Authentication required",
                                        "details": {
                                            "type": "authentication_error",
                                            "reason": "Invalid or missing API key",
                                        },
                                    },
                                },
                            }
                        },
                    }
                },
            },
            "403": {
                "description": "Forbidden",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "examples": {
                            "insufficient_permissions": {
                                "summary": "Insufficient Permissions",
                                "value": {
                                    "request_id": "550e8400-e29b-41d4-a716-446655440003",
                                    "timestamp": "2024-12-28T10:30:00Z",
                                    "status": "error",
                                    "version": "2.0.0",
                                    "error": {
                                        "code": "insufficient_permissions",
                                        "message": "Insufficient permissions",
                                        "details": {
                                            "required_permission": "admin",
                                            "user_permissions": ["read", "write"],
                                            "type": "permission_error",
                                        },
                                    },
                                },
                            }
                        },
                    }
                },
            },
            "429": {
                "description": "Too Many Requests",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "examples": {
                            "rate_limit_exceeded": {
                                "summary": "Rate Limit Exceeded",
                                "value": {
                                    "request_id": "550e8400-e29b-41d4-a716-446655440004",
                                    "timestamp": "2024-12-28T10:30:00Z",
                                    "status": "error",
                                    "version": "2.0.0",
                                    "error": {
                                        "code": "rate_limit_exceeded",
                                        "message": "Rate limit exceeded: 60 requests per minute",
                                        "details": {
                                            "limit": 60,
                                            "window": "minute",
                                            "retry_after": 30,
                                            "type": "rate_limit_error",
                                        },
                                    },
                                },
                            }
                        },
                    }
                },
            },
            "500": {
                "description": "Internal Server Error",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "examples": {
                            "processing_error": {
                                "summary": "Processing Error",
                                "value": {
                                    "request_id": "550e8400-e29b-41d4-a716-446655440005",
                                    "timestamp": "2024-12-28T10:30:00Z",
                                    "status": "error",
                                    "version": "2.0.0",
                                    "error": {
                                        "code": "processing_error",
                                        "message": "Query processing failed",
                                        "details": {
                                            "type": "processing_error",
                                            "recoverable": True,
                                        },
                                    },
                                },
                            }
                        },
                    }
                },
            },
        }

        # Add error responses to all endpoints
        for path in paths.values():
            for method in path.values():
                if isinstance(method, dict) and "responses" in method:
                    method["responses"].update(error_responses)

    def _add_rate_limiting_docs(self, schema: Dict[str, Any]) -> None:
        """Add rate limiting documentation."""
        # Add rate limiting headers to all responses
        for path in schema.get("paths", {}).values():
            for method in path.values():
                if isinstance(method, dict) and "responses" in method:
                    for response in method["responses"].values():
                        if "headers" not in response:
                            response["headers"] = {}

                        response["headers"].update(
                            {
                                "X-RateLimit-Limit": {
                                    "description": "Rate limit requests per window",
                                    "schema": {"type": "integer"},
                                },
                                "X-RateLimit-Remaining": {
                                    "description": "Remaining requests in current window",
                                    "schema": {"type": "integer"},
                                },
                                "X-RateLimit-Reset": {
                                    "description": "Time when rate limit resets (Unix timestamp)",
                                    "schema": {"type": "integer"},
                                },
                                "X-Request-ID": {
                                    "description": "Unique request identifier",
                                    "schema": {"type": "string", "format": "uuid"},
                                },
                            }
                        )

    def _add_security_schemes(self, schema: Dict[str, Any]) -> None:
        """Add security scheme documentation."""
        components = schema.get("components", {})

        components["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token authentication",
            },
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key authentication",
            },
        }

        # Add security requirements to all endpoints
        for path in schema.get("paths", {}).values():
            for method in path.values():
                if isinstance(method, dict):
                    method["security"] = [{"BearerAuth": []}, {"ApiKeyAuth": []}]

    def _add_sdk_examples(self, schema: Dict[str, Any]) -> None:
        """Add SDK code examples."""
        # Add x-code-samples extension
        for path in schema.get("paths", {}).values():
            for method in path.values():
                if isinstance(method, dict):
                    method["x-code-samples"] = {
                        "python": {
                            "summary": "Python example",
                            "code": self._generate_python_example(method),
                        },
                        "javascript": {
                            "summary": "JavaScript example",
                            "code": self._generate_javascript_example(method),
                        },
                        "curl": {
                            "summary": "cURL example",
                            "code": self._generate_curl_example(method),
                        },
                    }

    def _generate_python_example(self, method: Dict[str, Any]) -> str:
        """Generate Python code example."""
        return """
import requests

response = requests.post(
    "https://api.universal-knowledge-hub.com/v2/query",
    headers={
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    },
    json={
        "query": "What is machine learning?",
        "max_tokens": 1000,
        "confidence_threshold": 0.8
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Answer: {result['data']['answer']}")
else:
    print(f"Error: {response.json()['error']['message']}")
"""

    def _generate_javascript_example(self, method: Dict[str, Any]) -> str:
        """Generate JavaScript code example."""
        return """
const response = await fetch('https://api.universal-knowledge-hub.com/v2/query', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        query: 'What is machine learning?',
        max_tokens: 1000,
        confidence_threshold: 0.8
    })
});

if (response.ok) {
    const result = await response.json();
    console.log(`Answer: ${result.data.answer}`);
} else {
    const error = await response.json();
    console.error(`Error: ${error.error.message}`);
}
"""

    def _generate_curl_example(self, method: Dict[str, Any]) -> str:
        """Generate cURL code example."""
        return """
curl -X POST "https://api.universal-knowledge-hub.com/v2/query" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "What is machine learning?",
    "max_tokens": 1000,
    "confidence_threshold": 0.8
  }'
"""


def setup_enhanced_documentation(app: FastAPI) -> None:
    """Setup enhanced API documentation."""
    generator = EnhancedAPIDocumentationGenerator(app)

    # Override default OpenAPI schema
    app.openapi = lambda: generator.generate_openapi_schema()

    # Add documentation endpoints
    @app.get("/docs/openapi.json", include_in_schema=False)
    async def get_openapi_json():
        """Get OpenAPI schema as JSON."""
        return generator.generate_openapi_schema()

    @app.get("/docs/openapi.yaml", include_in_schema=False)
    async def get_openapi_yaml():
        """Get OpenAPI schema as YAML."""
        schema = generator.generate_openapi_schema()
        return yaml.dump(schema, default_flow_style=False)

    @app.get("/docs/markdown", include_in_schema=False)
    async def get_markdown_docs():
        """Get API documentation as Markdown."""
        return generator.config.description

    @app.get("/docs/examples", include_in_schema=False)
    async def get_sdk_examples():
        """Get SDK code examples."""
        return {
            "python": generator._generate_python_example({}),
            "javascript": generator._generate_javascript_example({}),
            "curl": generator._generate_curl_example({}),
        }
