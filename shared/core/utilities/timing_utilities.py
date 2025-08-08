"""
Timing Utilities - Common Timing Patterns

This module provides utilities for common timing patterns found across the codebase.
Extracted from duplicate timing logic to provide consistent behavior.
"""

import time
import asyncio
from typing import Callable, Any, Dict, Optional
from functools import wraps
from dataclasses import dataclass
from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


@dataclass
class TimingContext:
    """Context for timing operations."""
    start_time: float
    operation_name: str
    timeout_seconds: Optional[float] = None
    max_retries: int = 3


class TimingManager:
    """Manages timing operations with consistent patterns."""
    
    def __init__(self):
        self.active_timers = {}
    
    def start_timer(self, operation_name: str) -> TimingContext:
        """
        Start a timer for an operation.
        
        This replaces the common pattern: start_time = time.time()
        """
        start_time = time.time()
        context = TimingContext(
            start_time=start_time,
            operation_name=operation_name
        )
        self.active_timers[operation_name] = context
        return context
    
    def calculate_execution_time(self, context: TimingContext) -> int:
        """
        Calculate execution time in milliseconds.
        
        This replaces the common pattern: execution_time = (time.time() - start_time) * 1000
        """
        execution_time = (time.time() - context.start_time) * 1000
        return int(execution_time)
    
    def get_processing_time(self, context: TimingContext) -> int:
        """
        Get processing time in milliseconds.
        
        This replaces the common pattern: processing_time = int((time.time() - start_time) * 1000)
        """
        return self.calculate_execution_time(context)
    
    def end_timer(self, operation_name: str) -> Optional[int]:
        """End a timer and return execution time."""
        if operation_name in self.active_timers:
            context = self.active_timers[operation_name]
            execution_time = self.calculate_execution_time(context)
            del self.active_timers[operation_name]
            return execution_time
        return None


# Global timing manager instance
timing_manager = TimingManager()


def time_operation(operation_name: str, log_result: bool = True):
    """
    Decorator to time operations with consistent logging.
    
    This replaces the common pattern of manual timing in functions.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            context = timing_manager.start_timer(operation_name)
            
            try:
                result = await func(*args, **kwargs)
                execution_time = timing_manager.calculate_execution_time(context)
                
                if log_result:
                    logger.info(
                        f"Operation {operation_name} completed in {execution_time:.2f}ms",
                        operation=operation_name,
                        execution_time_ms=execution_time
                    )
                
                return result
                
            except Exception as e:
                execution_time = timing_manager.calculate_execution_time(context)
                
                if log_result:
                    logger.error(
                        f"Operation {operation_name} failed after {execution_time:.2f}ms: {str(e)}",
                        operation=operation_name,
                        execution_time_ms=execution_time,
                        error=str(e)
                    )
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            context = timing_manager.start_timer(operation_name)
            
            try:
                result = func(*args, **kwargs)
                execution_time = timing_manager.calculate_execution_time(context)
                
                if log_result:
                    logger.info(
                        f"Operation {operation_name} completed in {execution_time:.2f}ms",
                        operation=operation_name,
                        execution_time_ms=execution_time
                    )
                
                return result
                
            except Exception as e:
                execution_time = timing_manager.calculate_execution_time(context)
                
                if log_result:
                    logger.error(
                        f"Operation {operation_name} failed after {execution_time:.2f}ms: {str(e)}",
                        operation=operation_name,
                        execution_time_ms=execution_time,
                        error=str(e)
                    )
                raise
        
        # Return async wrapper if function is async, sync wrapper otherwise
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def execute_with_timeout(
    operation_name: str,
    timeout_seconds: float = 30.0,
    max_retries: int = 3,
    fallback_func: Optional[Callable] = None
):
    """
    Execute function with timeout and retry logic.
    
    This provides consistent timeout handling across the codebase.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            context = timing_manager.start_timer(operation_name)
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout_seconds
                    )
                    
                    execution_time = timing_manager.calculate_execution_time(context)
                    logger.info(
                        f"Operation {operation_name} completed in {execution_time:.2f}ms",
                        operation=operation_name,
                        execution_time_ms=execution_time,
                        attempts=attempt + 1
                    )
                    
                    return result
                    
                except asyncio.TimeoutError:
                    execution_time = timing_manager.calculate_execution_time(context)
                    logger.warning(
                        f"Operation {operation_name} timed out after {timeout_seconds}s (attempt {attempt + 1}/{max_retries + 1})",
                        operation=operation_name,
                        execution_time_ms=execution_time,
                        attempt=attempt + 1
                    )
                    
                    if attempt == max_retries:
                        if fallback_func:
                            try:
                                fallback_result = await fallback_func(*args, **kwargs)
                                logger.info(f"Fallback for {operation_name} succeeded")
                                return fallback_result
                            except Exception as e:
                                logger.error(f"Fallback for {operation_name} also failed: {e}")
                        
                        raise asyncio.TimeoutError(f"Operation {operation_name} timed out after {timeout_seconds} seconds")
                    
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
                except Exception as e:
                    last_exception = e
                    execution_time = timing_manager.calculate_execution_time(context)
                    logger.error(
                        f"Operation {operation_name} failed (attempt {attempt + 1}/{max_retries + 1}): {e}",
                        operation=operation_name,
                        execution_time_ms=execution_time,
                        attempt=attempt + 1,
                        error=str(e)
                    )
                    
                    if attempt == max_retries:
                        if fallback_func:
                            try:
                                fallback_result = await fallback_func(*args, **kwargs)
                                logger.info(f"Fallback for {operation_name} succeeded")
                                return fallback_result
                            except Exception as fallback_error:
                                logger.error(f"Fallback for {operation_name} also failed: {fallback_error}")
                        
                        raise last_exception
                    
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return async_wrapper
    return decorator


def create_timing_context(operation_name: str) -> TimingContext:
    """Create a timing context for manual timing."""
    return timing_manager.start_timer(operation_name)


def get_execution_time(context: TimingContext) -> int:
    """Get execution time from a timing context."""
    return timing_manager.calculate_execution_time(context)


def end_timing(operation_name: str) -> Optional[int]:
    """End timing for an operation and return execution time."""
    return timing_manager.end_timer(operation_name)


# Convenience functions for common patterns

def start_timer() -> float:
    """
    Start a timer and return the start time.
    
    This replaces: start_time = time.time()
    """
    return time.time()


def calculate_execution_time(start_time: float) -> int:
    """
    Calculate execution time in milliseconds.
    
    This replaces: execution_time = (time.time() - start_time) * 1000
    """
    execution_time = (time.time() - start_time) * 1000
    return int(execution_time)


def get_processing_time(start_time: float) -> int:
    """
    Get processing time in milliseconds.
    
    This replaces: processing_time = int((time.time() - start_time) * 1000)
    """
    return calculate_execution_time(start_time) 