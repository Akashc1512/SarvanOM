"""
Agent Decorators

This module provides decorators specifically for agent functions.
"""

import time
import functools
from typing import Callable, Any
import asyncio


def time_agent_function(agent_name: str):
    """
    Decorator to time agent function execution.
    
    Args:
        agent_name: Name of the agent for logging
        
    Returns:
        Decorated function with timing
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                # Log timing information
                print(f"Agent {agent_name} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"Agent {agent_name} failed after {execution_time:.3f}s: {e}")
                raise
                
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                # Log timing information
                print(f"Agent {agent_name} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"Agent {agent_name} failed after {execution_time:.3f}s: {e}")
                raise
                
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator
