"""
Common Processors for Agents

This module provides common processing utilities that agents can use
for consistent behavior across the system.
"""

from typing import Dict, Any, List, Optional


class CommonProcessors:
    """Common processing utilities for agents."""
    
    @staticmethod
    async def extract_task_data(task: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """
        Extract and validate required fields from a task.
        
        Args:
            task: Task data dictionary
            required_fields: List of required field names
            
        Returns:
            Dictionary with extracted data
        """
        extracted_data = {}
        
        for field in required_fields:
            if field in task:
                extracted_data[field] = task[field]
            else:
                extracted_data[field] = None
                
        return extracted_data
    
    @staticmethod
    def calculate_confidence(data: Dict[str, Any], confidence_fields: List[str]) -> float:
        """
        Calculate confidence based on data quality.
        
        Args:
            data: Data dictionary
            confidence_fields: Fields to consider for confidence calculation
            
        Returns:
            Confidence score between 0 and 1
        """
        if not data or not confidence_fields:
            return 0.5
            
        total_confidence = 0.0
        valid_fields = 0
        
        for field in confidence_fields:
            if field in data:
                value = data[field]
                if value is not None and value != "":
                    if isinstance(value, list) and len(value) > 0:
                        total_confidence += 0.8
                    elif isinstance(value, dict) and value:
                        total_confidence += 0.7
                    elif isinstance(value, (str, int, float)) and value:
                        total_confidence += 0.9
                    valid_fields += 1
        
        if valid_fields == 0:
            return 0.0
            
        return min(1.0, total_confidence / valid_fields)
