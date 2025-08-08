"""
Validation Utilities - Common Validation Patterns

This module provides utilities for common validation patterns found across the codebase.
Extracted from duplicate validation logic to provide consistent behavior.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str] = None
    sanitized_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ValidationUtils:
    """Common validation utilities."""
    
    @staticmethod
    def validate_string(
        value: Any,
        field_name: str,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        allow_empty: bool = False
    ) -> ValidationResult:
        """
        Validate a string value.
        
        This replaces common string validation patterns.
        """
        errors = []
        
        # Check if value is a string
        if not isinstance(value, str):
            errors.append(f"{field_name} must be a string")
            return ValidationResult(is_valid=False, errors=errors)
        
        # Check if empty
        if not allow_empty and len(value.strip()) == 0:
            errors.append(f"{field_name} cannot be empty")
            return ValidationResult(is_valid=False, errors=errors)
        
        # Check minimum length
        if min_length is not None and len(value) < min_length:
            errors.append(f"{field_name} must be at least {min_length} characters long")
        
        # Check maximum length
        if max_length is not None and len(value) > max_length:
            errors.append(f"{field_name} must be no more than {max_length} characters long")
        
        if errors:
            return ValidationResult(is_valid=False, errors=errors)
        
        return ValidationResult(
            is_valid=True,
            sanitized_data={field_name: value.strip()}
        )
    
    @staticmethod
    def validate_non_empty(
        value: Any,
        field_name: str
    ) -> ValidationResult:
        """
        Validate that a value is not empty.
        
        This replaces: if len(value.strip()) == 0:
        """
        if not value or (isinstance(value, str) and len(value.strip()) == 0):
            return ValidationResult(
                is_valid=False,
                errors=[f"{field_name} cannot be empty"]
            )
        
        return ValidationResult(
            is_valid=True,
            sanitized_data={field_name: value}
        )
    
    @staticmethod
    def validate_length(
        value: Any,
        field_name: str,
        max_length: int,
        min_length: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate the length of a value.
        
        This replaces: if len(value) > max_length:
        """
        errors = []
        
        if not isinstance(value, (str, list, dict)):
            errors.append(f"{field_name} must be a string, list, or dictionary")
            return ValidationResult(is_valid=False, errors=errors)
        
        length = len(value)
        
        if min_length is not None and length < min_length:
            errors.append(f"{field_name} must be at least {min_length} items long")
        
        if length > max_length:
            errors.append(f"{field_name} must be no more than {max_length} items long")
        
        if errors:
            return ValidationResult(is_valid=False, errors=errors)
        
        return ValidationResult(
            is_valid=True,
            sanitized_data={field_name: value}
        )
    
    @staticmethod
    def validate_required_fields(
        data: Dict[str, Any],
        required_fields: List[str],
        allow_empty: bool = False
    ) -> ValidationResult:
        """
        Validate that required fields are present.
        
        This replaces: missing_fields = []
        """
        missing_fields = []
        sanitized_data = {}
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif not allow_empty and not data[field]:
                missing_fields.append(field)
            else:
                sanitized_data[field] = data[field]
        
        if missing_fields:
            return ValidationResult(
                is_valid=False,
                errors=[f"Missing required fields: {', '.join(missing_fields)}"]
            )
        
        return ValidationResult(
            is_valid=True,
            sanitized_data=sanitized_data
        )
    
    @staticmethod
    def validate_query_input(
        task: Dict[str, Any],
        context: Any = None
    ) -> ValidationResult:
        """
        Validate query input for agents.
        
        This provides consistent query validation across agents.
        """
        query = task.get("query", "")
        
        # Validate query string
        query_validation = ValidationUtils.validate_string(
            value=query,
            field_name="query",
            max_length=10000,
            allow_empty=False
        )
        
        if not query_validation.is_valid:
            return query_validation
        
        return ValidationResult(
            is_valid=True,
            sanitized_data={"query": query_validation.sanitized_data["query"]}
        )
    
    @staticmethod
    def validate_documents_input(
        task: Dict[str, Any],
        context: Any = None
    ) -> ValidationResult:
        """
        Validate documents input for agents.
        
        This provides consistent document validation across agents.
        """
        documents = task.get("documents", [])
        
        if not documents:
            return ValidationResult(
                is_valid=False,
                errors=["No documents provided for processing"]
            )
        
        if not isinstance(documents, list):
            return ValidationResult(
                is_valid=False,
                errors=["Documents must be a list"]
            )
        
        # Validate each document
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
    def validate_sources_input(
        task: Dict[str, Any],
        context: Any = None
    ) -> ValidationResult:
        """
        Validate sources input for citation agents.
        
        This provides consistent source validation across agents.
        """
        sources = task.get("sources", [])
        
        if not sources:
            return ValidationResult(
                is_valid=False,
                errors=["No sources provided for citation processing"]
            )
        
        if not isinstance(sources, list):
            return ValidationResult(
                is_valid=False,
                errors=["Sources must be a list"]
            )
        
        # Validate each source
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
    def validate_agent_task(
        task: Dict[str, Any],
        required_fields: List[str],
        context: Any = None
    ) -> ValidationResult:
        """
        Validate agent task with required fields.
        
        This provides consistent task validation across agents.
        """
        # First validate required fields
        required_validation = ValidationUtils.validate_required_fields(
            data=task,
            required_fields=required_fields
        )
        
        if not required_validation.is_valid:
            return required_validation
        
        # Additional validation based on task type
        task_type = task.get("task_type", "general")
        
        if task_type == "query":
            return ValidationUtils.validate_query_input(task, context)
        elif task_type == "documents":
            return ValidationUtils.validate_documents_input(task, context)
        elif task_type == "sources":
            return ValidationUtils.validate_sources_input(task, context)
        
        return ValidationResult(
            is_valid=True,
            sanitized_data=required_validation.sanitized_data
        )


# Convenience functions for common patterns

def validate_string(
    value: Any,
    field_name: str,
    max_length: Optional[int] = None,
    min_length: Optional[int] = None,
    allow_empty: bool = False
) -> ValidationResult:
    """
    Validate a string value.
    
    This replaces common string validation patterns.
    """
    return ValidationUtils.validate_string(
        value=value,
        field_name=field_name,
        max_length=max_length,
        min_length=min_length,
        allow_empty=allow_empty
    )


def validate_non_empty(
    value: Any,
    field_name: str
) -> ValidationResult:
    """
    Validate that a value is not empty.
    
    This replaces: if len(value.strip()) == 0:
    """
    return ValidationUtils.validate_non_empty(value, field_name)


def validate_length(
    value: Any,
    field_name: str,
    max_length: int,
    min_length: Optional[int] = None
) -> ValidationResult:
    """
    Validate the length of a value.
    
    This replaces: if len(value) > max_length:
    """
    return ValidationUtils.validate_length(
        value=value,
        field_name=field_name,
        max_length=max_length,
        min_length=min_length
    )


def validate_required_fields(
    data: Dict[str, Any],
    required_fields: List[str],
    allow_empty: bool = False
) -> ValidationResult:
    """
    Validate that required fields are present.
    
    This replaces: missing_fields = []
    """
    return ValidationUtils.validate_required_fields(
        data=data,
        required_fields=required_fields,
        allow_empty=allow_empty
    )


def validate_query_input(
    task: Dict[str, Any],
    context: Any = None
) -> ValidationResult:
    """
    Validate query input for agents.
    
    This provides consistent query validation across agents.
    """
    return ValidationUtils.validate_query_input(task, context)


def validate_documents_input(
    task: Dict[str, Any],
    context: Any = None
) -> ValidationResult:
    """
    Validate documents input for agents.
    
    This provides consistent document validation across agents.
    """
    return ValidationUtils.validate_documents_input(task, context)


def validate_sources_input(
    task: Dict[str, Any],
    context: Any = None
) -> ValidationResult:
    """
    Validate sources input for citation agents.
    
    This provides consistent source validation across agents.
    """
    return ValidationUtils.validate_sources_input(task, context) 