"""
Response Utilities - Common Response Formatting Patterns

This module provides utilities for common response formatting patterns found across the codebase.
Extracted from duplicate response logic to provide consistent behavior.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from shared.core.utilities.timing_utilities import get_processing_time


@dataclass
class ResponseData:
    """Standardized response data structure."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    confidence: float = 0.0
    execution_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResponseFormatter:
    """Formats responses with consistent patterns."""

    @staticmethod
    def create_success_response(
        data: Dict[str, Any],
        confidence: float = 1.0,
        execution_time_ms: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a standardized success response.

        This replaces the common pattern: return {"success": True, "data": data, ...}
        """
        response = {
            "success": True,
            "data": data,
            "confidence": confidence,
            "execution_time_ms": execution_time_ms,
            "metadata": metadata or {},
        }

        return response

    @staticmethod
    def create_error_response(
        error: str,
        execution_time_ms: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a standardized error response.

        This replaces the common pattern: return {"success": False, "error": str(e), ...}
        """
        response = {
            "success": False,
            "error": error,
            "confidence": 0.0,
            "execution_time_ms": execution_time_ms,
            "metadata": metadata or {},
        }

        return response

    @staticmethod
    def add_execution_time(
        response: Dict[str, Any], start_time: float
    ) -> Dict[str, Any]:
        """
        Add execution time to a response.

        This replaces the common pattern: "execution_time_ms": int((time.time() - start_time) * 1000)
        """
        execution_time = get_processing_time(start_time)
        response["execution_time_ms"] = execution_time
        return response

    @staticmethod
    def add_confidence(response: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """
        Add confidence to a response.

        This replaces the common pattern: "confidence": confidence
        """
        response["confidence"] = confidence
        return response

    @staticmethod
    def format_agent_response(
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        confidence: float = 0.0,
        execution_time_ms: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Format a standardized agent response.

        This provides consistent formatting for all agent responses.
        """
        if success:
            return ResponseFormatter.create_success_response(
                data=data or {},
                confidence=confidence,
                execution_time_ms=execution_time_ms,
                metadata=metadata,
            )
        else:
            return ResponseFormatter.create_error_response(
                error=error or "Unknown error",
                execution_time_ms=execution_time_ms,
                metadata=metadata,
            )

    @staticmethod
    def format_retrieval_response(
        documents: List[Dict[str, Any]],
        search_type: str,
        total_hits: int,
        query_time_ms: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Format a standardized retrieval response.

        This provides consistent formatting for retrieval operations.
        """
        return ResponseFormatter.create_success_response(
            data={
                "documents": documents,
                "search_type": search_type,
                "total_hits": total_hits,
                "query_time_ms": query_time_ms,
            },
            confidence=min(len(documents) / 10.0, 1.0),
            execution_time_ms=query_time_ms,
            metadata=metadata or {},
        )

    @staticmethod
    def format_synthesis_response(
        answer: str,
        synthesis_method: str,
        fact_count: int,
        processing_time_ms: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Format a standardized synthesis response.

        This provides consistent formatting for synthesis operations.
        """
        return ResponseFormatter.create_success_response(
            data={
                "answer": answer,
                "synthesis_method": synthesis_method,
                "fact_count": fact_count,
                "processing_time_ms": processing_time_ms,
            },
            confidence=min(fact_count / 5.0, 1.0),
            execution_time_ms=processing_time_ms,
            metadata=metadata or {},
        )

    @staticmethod
    def format_citation_response(
        cited_content: str,
        citations: List[Dict[str, Any]],
        citation_format: str,
        processing_time_ms: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Format a standardized citation response.

        This provides consistent formatting for citation operations.
        """
        return ResponseFormatter.create_success_response(
            data={
                "cited_content": cited_content,
                "citations": citations,
                "citation_format": citation_format,
                "processing_time_ms": processing_time_ms,
            },
            confidence=min(len(citations) / 5.0, 1.0),
            execution_time_ms=processing_time_ms,
            metadata=metadata or {},
        )


# Convenience functions for common patterns


def create_success_response(
    data: Dict[str, Any],
    confidence: float = 1.0,
    execution_time_ms: int = 0,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a success response.

    This replaces: return {"success": True, "data": data, ...}
    """
    return ResponseFormatter.create_success_response(
        data=data,
        confidence=confidence,
        execution_time_ms=execution_time_ms,
        metadata=metadata,
    )


def create_error_response(
    error: str, execution_time_ms: int = 0, metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create an error response.

    This replaces: return {"success": False, "error": str(e), ...}
    """
    return ResponseFormatter.create_error_response(
        error=error, execution_time_ms=execution_time_ms, metadata=metadata
    )


def add_execution_time(response: Dict[str, Any], start_time: float) -> Dict[str, Any]:
    """
    Add execution time to a response.

    This replaces: "execution_time_ms": int((time.time() - start_time) * 1000)
    """
    return ResponseFormatter.add_execution_time(response, start_time)


def add_confidence(response: Dict[str, Any], confidence: float) -> Dict[str, Any]:
    """
    Add confidence to a response.

    This replaces: "confidence": confidence
    """
    return ResponseFormatter.add_confidence(response, confidence)


def format_standard_response(
    success: bool,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    confidence: float = 0.0,
    execution_time_ms: int = 0,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Format a standardized response.

    This provides consistent formatting for all responses.
    """
    return ResponseFormatter.format_agent_response(
        success=success,
        data=data,
        error=error,
        confidence=confidence,
        execution_time_ms=execution_time_ms,
        metadata=metadata,
    )
