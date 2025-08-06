"""
Enhanced API Documentation Generator for Universal Knowledge Platform
This module provides comprehensive API documentation with examples and SDK generation.
"""

import logging
from shared.core.unified_logging import get_logger
import json
import yaml
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import httpx
import asyncio

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

logger = get_logger(__name__)


class APIVersion(str, Enum):
    """API versions."""
    
    V1 = "v1"
    V2 = "v2"


class DocumentationConfig:
    """Configuration for API documentation."""
    
    def __init__(self):
        # API metadata
        self.title = "Universal Knowledge Platform API"
        self.version = "2.0.0"
        self.description = """
        # Universal Knowledge Platform API v2.0.0
        
        A comprehensive API for intelligent knowledge retrieval, analysis, and synthesis.
        
        ## Features
        
        - **Intelligent Query Processing**: Advanced NLP-powered query understanding
        - **Multi-Source Retrieval**: Vector search, database queries, and web crawling
        - **Fact-Checking**: Automated verification and citation generation
        - **Expert Validation**: Human-in-the-loop quality assurance
        - **Real-time Collaboration**: WebSocket-based collaborative features
        - **Analytics & Monitoring**: Comprehensive usage analytics and health monitoring
        
        ## Quick Start
        
        ```python
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.universal-knowledge-hub.com/v2/query",
                headers={"Authorization": "Bearer YOUR_API_KEY"},
                json={
                    "query": "What is machine learning?",
                    "max_tokens": 1000,
                    "confidence_threshold": 0.8
                }
            )
            result = response.json()
        ```
        
        ## Authentication
        
        All API endpoints require authentication using Bearer tokens.
        
        ```python
        headers = {
            "Authorization": "Bearer YOUR_API_KEY",
            "Content-Type": "application/json"
        }
        ```
        
        ## Rate Limiting
        
        - **Standard Plan**: 100 requests per minute
        - **Professional Plan**: 1000 requests per minute
        - **Enterprise Plan**: Custom limits
        
        ## Error Handling
        
        The API uses standard HTTP status codes and returns detailed error messages.
        
        ```json
        {
            "request_id": "uuid",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "error",
            "version": "2.0.0",
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded",
                "details": {
                    "limit": 100,
                    "reset_time": "2024-01-01T00:01:00Z"
                }
            }
        }
        ```
        
        ## Examples

        ### Basic Query

        ```python
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
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
        async with httpx.AsyncClient() as client:
            response = await client.post(
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
            },
            "required": ["request_id", "timestamp", "status", "version", "data"],
        }

        # Query request schema
        components["QueryRequest"] = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The user's question"},
                "max_tokens": {"type": "integer", "default": 1000},
                "confidence_threshold": {"type": "number", "default": 0.8},
                "include_sources": {"type": "boolean", "default": True},
                "include_citations": {"type": "boolean", "default": True},
            },
            "required": ["query"],
        }

        # Query response schema
        components["QueryResponse"] = {
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "confidence": {"type": "number"},
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
                "processing_time": {"type": "number"},
                "token_usage": {"type": "object"},
            },
        }

        schema["components"] = components

    def _add_examples(self, schema: Dict[str, Any]) -> None:
        """Add comprehensive examples."""
        examples = {
            "basic_query": {
                "summary": "Basic query example",
                "description": "Simple query with default parameters",
                "value": {
                    "query": "What is machine learning?",
                    "max_tokens": 1000,
                    "confidence_threshold": 0.8,
                },
            },
            "complex_query": {
                "summary": "Complex query example",
                "description": "Query with all parameters specified",
                "value": {
                    "query": "Explain the differences between supervised and unsupervised learning with examples",
                    "max_tokens": 2000,
                    "confidence_threshold": 0.9,
                    "include_sources": True,
                    "include_citations": True,
                },
            },
            "batch_query": {
                "summary": "Batch query example",
                "description": "Multiple queries in a single request",
                "value": {
                    "queries": [
                        {"query": "What is AI?"},
                        {"query": "Explain neural networks"},
                        {"query": "How does deep learning work?"},
                    ],
                },
            },
        }

        # Add examples to schema
        if "components" not in schema:
            schema["components"] = {}
        schema["components"]["examples"] = examples

    def _add_error_responses(self, schema: Dict[str, Any]) -> None:
        """Add comprehensive error response documentation."""
        error_responses = {
            "400": {
                "description": "Bad Request",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "example": {
                            "request_id": "550e8400-e29b-41d4-a716-446655440000",
                            "timestamp": "2024-01-01T00:00:00Z",
                            "status": "error",
                            "version": "2.0.0",
                            "error": {
                                "code": "INVALID_REQUEST",
                                "message": "Invalid query parameter",
                                "details": {"field": "query", "issue": "Empty query"},
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
                        "example": {
                            "request_id": "550e8400-e29b-41d4-a716-446655440001",
                            "timestamp": "2024-01-01T00:00:00Z",
                            "status": "error",
                            "version": "2.0.0",
                            "error": {
                                "code": "UNAUTHORIZED",
                                "message": "Invalid or missing API key",
                            },
                        },
                    }
                },
            },
            "429": {
                "description": "Too Many Requests",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "example": {
                            "request_id": "550e8400-e29b-41d4-a716-446655440002",
                            "timestamp": "2024-01-01T00:00:00Z",
                            "status": "error",
                            "version": "2.0.0",
                            "error": {
                                "code": "RATE_LIMIT_EXCEEDED",
                                "message": "Rate limit exceeded",
                                "details": {
                                    "limit": 100,
                                    "reset_time": "2024-01-01T00:01:00Z",
                                },
                            },
                        },
                    }
                },
            },
            "500": {
                "description": "Internal Server Error",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "example": {
                            "request_id": "550e8400-e29b-41d4-a716-446655440003",
                            "timestamp": "2024-01-01T00:00:00Z",
                            "status": "error",
                            "version": "2.0.0",
                            "error": {
                                "code": "INTERNAL_ERROR",
                                "message": "An internal error occurred",
                            },
                        },
                    }
                },
            },
        }

        # Add error responses to schema
        if "components" not in schema:
            schema["components"] = {}
        schema["components"]["responses"] = error_responses

    def _add_rate_limiting_docs(self, schema: Dict[str, Any]) -> None:
        """Add rate limiting documentation."""
        rate_limiting_info = {
            "description": "Rate limiting is applied per API key",
            "headers": {
                "X-RateLimit-Limit": {
                    "description": "Request limit per window",
                    "schema": {"type": "integer"},
                },
                "X-RateLimit-Remaining": {
                    "description": "Remaining requests in current window",
                    "schema": {"type": "integer"},
                },
                "X-RateLimit-Reset": {
                    "description": "Time when the rate limit resets",
                    "schema": {"type": "string", "format": "date-time"},
                },
            },
        }

        # Add to schema
        if "components" not in schema:
            schema["components"] = {}
        schema["components"]["rateLimiting"] = rate_limiting_info

    def _add_security_schemes(self, schema: Dict[str, Any]) -> None:
        """Add security scheme documentation."""
        security_schemes = {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "API key in Bearer format: Bearer YOUR_API_KEY",
            },
            "OAuth2": {
                "type": "oauth2",
                "flows": {
                    "clientCredentials": {
                        "tokenUrl": "/oauth/token",
                        "scopes": {
                            "read": "Read access to API",
                            "write": "Write access to API",
                        },
                    }
                },
            },
        }

        # Add to schema
        if "components" not in schema:
            schema["components"] = {}
        schema["components"]["securitySchemes"] = security_schemes

    def _add_sdk_examples(self, schema: Dict[str, Any]) -> None:
        """Add SDK examples for different languages."""
        sdk_examples = {
            "python": {
                "description": "Python SDK example using httpx",
                "code": """
import httpx

async def query_knowledge(query: str, api_key: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.universal-knowledge-hub.com/v2/query",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"query": query}
        )
        return response.json()
""",
            },
            "javascript": {
                "description": "JavaScript SDK example using fetch",
                "code": """
async function queryKnowledge(query, apiKey) {
    const response = await fetch(
        'https://api.universal-knowledge-hub.com/v2/query',
        {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        }
    );
    return response.json();
}
""",
            },
            "curl": {
                "description": "cURL example",
                "code": """
curl -X POST "https://api.universal-knowledge-hub.com/v2/query" \\
     -H "Authorization: Bearer YOUR_API_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{"query": "What is machine learning?"}'
""",
            },
        }

        # Add to schema
        if "components" not in schema:
            schema["components"] = {}
        schema["components"]["sdkExamples"] = sdk_examples

    def _generate_python_example(self, method: Dict[str, Any]) -> str:
        """Generate Python example for a method."""
        return f"""
import httpx

async with httpx.AsyncClient() as client:
    response = await client.{method['method'].lower()}(
        "{method['url']}",
        headers={{"Authorization": "Bearer YOUR_API_KEY"}},
        json={method.get('body', {})}
    )
    result = response.json()
"""

    def _generate_javascript_example(self, method: Dict[str, Any]) -> str:
        """Generate JavaScript example for a method."""
        return f"""
const response = await fetch("{method['url']}", {{
    method: "{method['method'].upper()}",
    headers: {{
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }},
    body: JSON.stringify({method.get('body', {})})
}});
const result = await response.json();
"""

    def _generate_curl_example(self, method: Dict[str, Any]) -> str:
        """Generate cURL example for a method."""
        body = json.dumps(method.get('body', {})) if method.get('body') else ""
        return f"""
curl -X {method['method'].upper()} "{method['url']}" \\
     -H "Authorization: Bearer YOUR_API_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{body}'
"""


def setup_enhanced_documentation(app: FastAPI) -> None:
    """Setup enhanced documentation for the FastAPI app."""
    generator = EnhancedAPIDocumentationGenerator(app)

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
        """Get documentation as Markdown."""
        # Implementation for markdown generation
        return {"message": "Markdown documentation endpoint"}

    @app.get("/docs/examples", include_in_schema=False)
    async def get_sdk_examples():
        """Get SDK examples for different languages."""
        # Implementation for SDK examples
        return {"message": "SDK examples endpoint"}
