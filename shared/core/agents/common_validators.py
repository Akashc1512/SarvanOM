"""
Common Validators for Agents

This module provides common validation utilities that agents can use
for consistent input validation across the system.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    
    is_valid: bool
    sanitized_data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None


class CommonValidators:
    """Common validation utilities for agents."""
    
    @staticmethod
    async def validate_required_fields(
        data: Dict[str, Any], 
        required_fields: List[str], 
        allow_empty: bool = False
    ) -> ValidationResult:
        """
        Validate that required fields are present.
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            allow_empty: Whether empty values are allowed
            
        Returns:
            ValidationResult with validation status
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
    async def validate_documents_input(
        task: Dict[str, Any], 
        context: Any = None
    ) -> ValidationResult:
        """
        Validate documents input for agents.
        
        Args:
            task: Task data to validate
            context: Optional context
            
        Returns:
            ValidationResult with validation status
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
    async def validate_query_input(
        task: Dict[str, Any], 
        context: Any = None
    ) -> ValidationResult:
        """
        Validate query input for agents.
        
        Args:
            task: Task data to validate
            context: Optional context
            
        Returns:
            ValidationResult with validation status
        """
        query = task.get("query", "")
        
        if not query or not isinstance(query, str):
            return ValidationResult(
                is_valid=False,
                errors=["Query must be a non-empty string"]
            )
        
        if len(query) > 10000:
            return ValidationResult(
                is_valid=False,
                errors=["Query too long (max 10000 characters)"]
            )
        
        return ValidationResult(
            is_valid=True,
            sanitized_data={"query": query}
        )
    
    @staticmethod
    async def validate_sources_input(
        task: Dict[str, Any], 
        context: Any = None
    ) -> ValidationResult:
        """
        Validate sources input for agents.
        
        Args:
            task: Task data to validate
            context: Optional context
            
        Returns:
            ValidationResult with validation status
        """
        sources = task.get("sources", [])
        
        if not sources:
            return ValidationResult(
                is_valid=False,
                errors=["No sources provided for processing"]
            )
        
        if not isinstance(sources, list):
            return ValidationResult(
                is_valid=False,
                errors=["Sources must be a list"]
            )
        
        return ValidationResult(
            is_valid=True,
            sanitized_data={"sources": sources}
        )
