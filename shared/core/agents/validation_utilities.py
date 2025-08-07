"""
Validation Utilities - Common Validation Patterns for Agents
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Validation result."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    sanitized_data: Optional[Dict[str, Any]] = None


class CommonValidators:
    """Common validation functions."""
    
    @staticmethod
    async def validate_query_input(task: Dict[str, Any], context: Any = None) -> ValidationResult:
        """Validate query input."""
        query = task.get("query", "")
        
        if not query or not isinstance(query, str):
            return ValidationResult(
                is_valid=False,
                errors=["Query must be a non-empty string"]
            )
        
        if len(query.strip()) == 0:
            return ValidationResult(
                is_valid=False,
                errors=["Query cannot be empty"]
            )
        
        if len(query) > 10000:
            return ValidationResult(
                is_valid=False,
                errors=["Query too long (max 10000 characters)"]
            )
        
        return ValidationResult(
            is_valid=True,
            sanitized_data={"query": query.strip()}
        )
    
    @staticmethod
    async def validate_documents_input(task: Dict[str, Any], context: Any = None) -> ValidationResult:
        """Validate documents input."""
        documents = task.get("documents", [])
        
        if not documents:
            return ValidationResult(
                is_valid=False,
                errors=["No documents provided"]
            )
        
        if not isinstance(documents, list):
            return ValidationResult(
                is_valid=False,
                errors=["Documents must be a list"]
            )
        
        for i, doc in enumerate(documents):
            if not isinstance(doc, dict):
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Document {i} must be a dictionary"]
                )
            if "content" not in doc:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Document {i} missing 'content' field"]
                )
        
        return ValidationResult(
            is_valid=True,
            sanitized_data={"documents": documents}
        )
    
    @staticmethod
    async def validate_sources_input(task: Dict[str, Any], context: Any = None) -> ValidationResult:
        """Validate sources input."""
        sources = task.get("sources", [])
        
        if not sources:
            return ValidationResult(
                is_valid=False,
                errors=["No sources provided"]
            )
        
        if not isinstance(sources, list):
            return ValidationResult(
                is_valid=False,
                errors=["Sources must be a list"]
            )
        
        for i, source in enumerate(sources):
            if not isinstance(source, dict):
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Source {i} must be a dictionary"]
                )
        
        return ValidationResult(
            is_valid=True,
            sanitized_data={"sources": sources}
        )
    
    @staticmethod
    async def validate_required_fields(
        task: Dict[str, Any],
        required_fields: List[str],
        context: Any = None
    ) -> ValidationResult:
        """Validate required fields."""
        missing_fields = []
        
        for field in required_fields:
            if field not in task or not task[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return ValidationResult(
                is_valid=False,
                errors=[f"Missing required fields: {', '.join(missing_fields)}"]
            )
        
        return ValidationResult(
            is_valid=True,
            sanitized_data=task
        ) 