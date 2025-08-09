"""
Query Validator Service

This module contains validation logic for queries.
It ensures queries meet requirements before processing.
"""

import re
import logging
from typing import Dict, Any, List
from datetime import datetime

from ...models.domain.query import Query, QueryType
from ...models.domain.user import UserContext

logger = logging.getLogger(__name__)


class QueryValidator:
    """Validates queries before processing."""

    def __init__(self):
        self.max_query_length = 10000
        self.min_query_length = 1
        self.forbidden_patterns = [
            r"<script.*?>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript protocol
            r"data:text/html",  # Data URLs
            r"vbscript:",  # VBScript protocol
        ]
        self.suspicious_patterns = [
            r"(\b(?:select|insert|update|delete|drop|create|alter)\b)",  # SQL keywords
            r"(\b(?:eval|exec|system|shell)\b)",  # Dangerous functions
            r"(\b(?:union|select|from|where)\b)",  # SQL injection patterns
        ]

    async def validate_query(self, query: Query) -> bool:
        """Validate a query for processing."""
        try:
            # Basic validation
            self._validate_basic_requirements(query)

            # Security validation
            self._validate_security(query)

            # Content validation
            self._validate_content(query)

            # Context validation
            self._validate_context(query)

            logger.info(f"Query {query.id} validation passed")
            return True

        except ValueError as e:
            logger.warning(f"Query {query.id} validation failed: {e}")
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error during query validation: {e}", exc_info=True
            )
            raise ValueError(f"Query validation error: {e}")

    def _validate_basic_requirements(self, query: Query):
        """Validate basic query requirements."""
        if not query.text or not query.text.strip():
            raise ValueError("Query text cannot be empty")

        if len(query.text) < self.min_query_length:
            raise ValueError(
                f"Query too short (minimum {self.min_query_length} characters)"
            )

        if len(query.text) > self.max_query_length:
            raise ValueError(
                f"Query too long (maximum {self.max_query_length} characters)"
            )

        # Check for excessive whitespace
        if len(query.text.strip()) < self.min_query_length:
            raise ValueError("Query contains only whitespace")

    def _validate_security(self, query: Query):
        """Validate query for security concerns."""
        query_lower = query.text.lower()

        # Check for forbidden patterns
        for pattern in self.forbidden_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                raise ValueError("Query contains forbidden content")

        # Check for suspicious patterns
        suspicious_count = 0
        for pattern in self.suspicious_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                suspicious_count += 1

        if suspicious_count >= 2:
            raise ValueError("Query contains suspicious patterns")

        # Check for excessive special characters
        special_char_ratio = len(re.findall(r"[^\w\s]", query.text)) / len(query.text)
        if special_char_ratio > 0.3:
            raise ValueError("Query contains too many special characters")

    def _validate_content(self, query: Query):
        """Validate query content quality."""
        # Check for repetitive characters
        if self._has_repetitive_chars(query.text):
            raise ValueError("Query contains repetitive characters")

        # Check for excessive numbers
        number_ratio = len(re.findall(r"\d", query.text)) / len(query.text)
        if number_ratio > 0.5:
            raise ValueError("Query contains too many numbers")

        # Check for proper word boundaries
        words = query.text.split()
        if len(words) < 1:
            raise ValueError("Query must contain at least one word")

        # Check for excessively long words
        long_words = [word for word in words if len(word) > 50]
        if long_words:
            raise ValueError("Query contains excessively long words")

    def _validate_context(self, query: Query):
        """Validate query context."""
        if not query.context:
            raise ValueError("Query context is required")

        if not query.context.user_id:
            raise ValueError("User ID is required in context")

        if not query.context.session_id:
            raise ValueError("Session ID is required in context")

        # Validate max_tokens
        if query.context.max_tokens < 1 or query.context.max_tokens > 10000:
            raise ValueError("Max tokens must be between 1 and 10000")

        # Validate confidence threshold
        if (
            query.context.confidence_threshold < 0.0
            or query.context.confidence_threshold > 1.0
        ):
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")

    def _has_repetitive_chars(self, text: str, threshold: int = 5) -> bool:
        """Check if text has repetitive characters."""
        for char in text:
            if text.count(char) > threshold:
                return True
        return False

    async def validate_query_type(self, query: Query, query_type: QueryType) -> bool:
        """Validate if query is appropriate for the specified type."""
        if query_type == QueryType.BASIC:
            return await self._validate_basic_query(query)
        elif query_type == QueryType.COMPREHENSIVE:
            return await self._validate_comprehensive_query(query)
        elif query_type == QueryType.FACT_CHECK:
            return await self._validate_fact_check_query(query)
        elif query_type == QueryType.SYNTHESIS:
            return await self._validate_synthesis_query(query)
        else:
            raise ValueError(f"Unknown query type: {query_type}")

    async def _validate_basic_query(self, query: Query) -> bool:
        """Validate query for basic processing."""
        # Basic queries should be relatively simple
        word_count = len(query.text.split())
        if word_count > 100:
            raise ValueError("Basic queries should be concise (max 100 words)")

        return True

    async def _validate_comprehensive_query(self, query: Query) -> bool:
        """Validate query for comprehensive processing."""
        # Comprehensive queries can be longer and more complex
        word_count = len(query.text.split())
        if word_count < 3:
            raise ValueError("Comprehensive queries should be detailed (min 3 words)")

        return True

    async def _validate_fact_check_query(self, query: Query) -> bool:
        """Validate query for fact checking."""
        # Fact check queries should contain factual claims
        fact_check_indicators = [
            "is it true",
            "fact check",
            "verify",
            "confirm",
            "accurate",
            "correct",
            "right",
            "wrong",
            "false",
            "true",
        ]

        query_lower = query.text.lower()
        has_fact_check_indicator = any(
            indicator in query_lower for indicator in fact_check_indicators
        )

        if not has_fact_check_indicator:
            raise ValueError(
                "Fact check queries should contain factual claims to verify"
            )

        return True

    async def _validate_synthesis_query(self, query: Query) -> bool:
        """Validate query for synthesis processing."""
        # Synthesis queries should ask for analysis or comparison
        synthesis_indicators = [
            "compare",
            "analyze",
            "synthesize",
            "summarize",
            "overview",
            "review",
            "examine",
            "study",
            "research",
        ]

        query_lower = query.text.lower()
        has_synthesis_indicator = any(
            indicator in query_lower for indicator in synthesis_indicators
        )

        if not has_synthesis_indicator:
            raise ValueError("Synthesis queries should ask for analysis or comparison")

        return True

    def get_validation_summary(self, query: Query) -> Dict[str, Any]:
        """Get a summary of query validation results."""
        try:
            self._validate_basic_requirements(query)
            self._validate_security(query)
            self._validate_content(query)
            self._validate_context(query)

            return {
                "valid": True,
                "query_id": query.id,
                "word_count": len(query.text.split()),
                "char_count": len(query.text),
                "has_special_chars": bool(re.search(r"[^\w\s]", query.text)),
                "confidence_threshold": query.context.confidence_threshold,
                "max_tokens": query.context.max_tokens,
            }

        except ValueError as e:
            return {
                "valid": False,
                "query_id": query.id,
                "error": str(e),
                "error_type": "validation_error",
            }
