#!/usr/bin/env python3
"""
Circuit Breaker System for LLM Providers

Provides circuit breaker pattern implementation for:
- Per-provider failure tracking
- Configurable failure thresholds
- Automatic recovery mechanisms
- Graceful degradation to fallback providers
- Comprehensive monitoring and alerting

Following enterprise resilience patterns for high-availability systems.
"""

import asyncio
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import logging

from services.gateway.middleware.observability import (
    log_error,
    log_llm_call,
    get_request_id,
    get_user_id
)

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int = 5  # Number of failures before opening
    recovery_timeout: int = 60  # Seconds to wait before half-open
    success_threshold: int = 3  # Successes needed to close circuit
    timeout_threshold: float = 30.0  # Request timeout in seconds
    window_size: int = 60  # Time window for failure counting (seconds)
    max_failures_per_window: int = 10  # Max failures in window


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker monitoring."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    circuit_opens: int = 0
    circuit_closes: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    current_failure_count: int = 0
    current_success_count: int = 0


class CircuitBreaker:
    """Circuit breaker implementation for individual providers."""
    
    def __init__(self, provider_name: str, config: CircuitBreakerConfig):
        self.provider_name = provider_name
        self.config = config
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self.failure_times: List[datetime] = []
        self.success_times: List[datetime] = []
        self.last_state_change = datetime.now(timezone.utc)
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    await self._transition_to_half_open()
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker for {self.provider_name} is OPEN"
                    )
            
            if self.state == CircuitState.HALF_OPEN:
                # Only allow limited requests in half-open state
                if self.stats.current_success_count >= self.config.success_threshold:
                    await self._transition_to_closed()
                elif self.stats.current_failure_count >= self.config.failure_threshold:
                    await self._transition_to_open()
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker for {self.provider_name} failed recovery test"
                    )
        
        # Execute the function
        start_time = time.time()
        try:
            # Create timeout task
            timeout_task = asyncio.create_task(
                asyncio.wait_for(func(*args, **kwargs), timeout=self.config.timeout_threshold)
            )
            
            result = await timeout_task
            
            # Success
            await self._record_success()
            return result
            
        except asyncio.TimeoutError:
            # Timeout
            await self._record_timeout()
            raise CircuitBreakerTimeoutError(
                f"Request to {self.provider_name} timed out after {self.config.timeout_threshold}s"
            )
            
        except Exception as e:
            # Failure
            await self._record_failure()
            raise CircuitBreakerFailureError(
                f"Request to {self.provider_name} failed: {str(e)}"
            ) from e
    
    async def _record_success(self):
        """Record a successful request."""
        async with self._lock:
            current_time = datetime.now(timezone.utc)
            
            self.stats.total_requests += 1
            self.stats.successful_requests += 1
            self.stats.current_success_count += 1
            self.stats.last_success_time = current_time
            
            self.success_times.append(current_time)
            
            # Clean old success times
            self._clean_old_entries(self.success_times)
            
            # Log success
            log_llm_call(
                provider=self.provider_name,
                model="unknown",
                duration=0.0,  # Will be calculated by caller
                success=True
            )
            
            logger.info(f"Circuit breaker success for {self.provider_name}")
    
    async def _record_failure(self):
        """Record a failed request."""
        async with self._lock:
            current_time = datetime.now(timezone.utc)
            
            self.stats.total_requests += 1
            self.stats.failed_requests += 1
            self.stats.current_failure_count += 1
            self.stats.last_failure_time = current_time
            
            self.failure_times.append(current_time)
            
            # Clean old failure times
            self._clean_old_entries(self.failure_times)
            
            # Check if circuit should open
            if self._should_open_circuit():
                await self._transition_to_open()
            
            # Log failure
            log_llm_call(
                provider=self.provider_name,
                model="unknown",
                duration=0.0,  # Will be calculated by caller
                success=False,
                error_message="Circuit breaker failure"
            )
            
            log_error(
                "circuit_breaker_failure",
                f"Circuit breaker failure for {self.provider_name}",
                {
                    "provider": self.provider_name,
                    "request_id": get_request_id(),
                    "user_id": get_user_id(),
                    "failure_count": self.stats.current_failure_count,
                    "total_failures": self.stats.failed_requests
                }
            )
            
            logger.warning(f"Circuit breaker failure for {self.provider_name}")
    
    async def _record_timeout(self):
        """Record a timeout request."""
        async with self._lock:
            current_time = datetime.now(timezone.utc)
            
            self.stats.total_requests += 1
            self.stats.timeout_requests += 1
            self.stats.current_failure_count += 1
            self.stats.last_failure_time = current_time
            
            self.failure_times.append(current_time)
            
            # Clean old failure times
            self._clean_old_entries(self.failure_times)
            
            # Check if circuit should open
            if self._should_open_circuit():
                await self._transition_to_open()
            
            # Log timeout
            log_llm_call(
                provider=self.provider_name,
                model="unknown",
                duration=self.config.timeout_threshold,
                success=False,
                error_message="Circuit breaker timeout"
            )
            
            log_error(
                "circuit_breaker_timeout",
                f"Circuit breaker timeout for {self.provider_name}",
                {
                    "provider": self.provider_name,
                    "request_id": get_request_id(),
                    "user_id": get_user_id(),
                    "timeout_seconds": self.config.timeout_threshold,
                    "failure_count": self.stats.current_failure_count
                }
            )
            
            logger.warning(f"Circuit breaker timeout for {self.provider_name}")
    
    def _should_open_circuit(self) -> bool:
        """Check if circuit should open based on failure threshold."""
        if self.state == CircuitState.OPEN:
            return False
        
        # Check current failure count
        if self.stats.current_failure_count >= self.config.failure_threshold:
            return True
        
        # Check failures in time window
        window_start = datetime.now(timezone.utc) - timedelta(seconds=self.config.window_size)
        recent_failures = sum(1 for t in self.failure_times if t > window_start)
        
        return recent_failures >= self.config.max_failures_per_window
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        if self.state != CircuitState.OPEN:
            return False
        
        if not self.stats.last_failure_time:
            return True
        
        time_since_failure = datetime.now(timezone.utc) - self.stats.last_failure_time
        return time_since_failure.total_seconds() >= self.config.recovery_timeout
    
    async def _transition_to_open(self):
        """Transition circuit to OPEN state."""
        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.stats.circuit_opens += 1
            self.last_state_change = datetime.now(timezone.utc)
            
            # Reset success count for half-open testing
            self.stats.current_success_count = 0
            
            log_error(
                "circuit_breaker_opened",
                f"Circuit breaker opened for {self.provider_name}",
                {
                    "provider": self.provider_name,
                    "request_id": get_request_id(),
                    "user_id": get_user_id(),
                    "failure_count": self.stats.current_failure_count,
                    "total_failures": self.stats.failed_requests
                }
            )
            
            logger.error(f"Circuit breaker opened for {self.provider_name}")
    
    async def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state."""
        if self.state != CircuitState.HALF_OPEN:
            self.state = CircuitState.HALF_OPEN
            self.last_state_change = datetime.now(timezone.utc)
            
            # Reset counters for testing
            self.stats.current_failure_count = 0
            self.stats.current_success_count = 0
            
            logger.info(f"Circuit breaker half-open for {self.provider_name}")
    
    async def _transition_to_closed(self):
        """Transition circuit to CLOSED state."""
        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            self.stats.circuit_closes += 1
            self.last_state_change = datetime.now(timezone.utc)
            
            # Reset counters
            self.stats.current_failure_count = 0
            self.stats.current_success_count = 0
            
            logger.info(f"Circuit breaker closed for {self.provider_name}")
    
    def _clean_old_entries(self, times_list: List[datetime]):
        """Clean old entries from times list."""
        window_start = datetime.now(timezone.utc) - timedelta(seconds=self.config.window_size)
        times_list[:] = [t for t in times_list if t > window_start]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            "provider": self.provider_name,
            "state": self.state.value,
            "last_state_change": self.last_state_change.isoformat(),
            "stats": {
                "total_requests": self.stats.total_requests,
                "successful_requests": self.stats.successful_requests,
                "failed_requests": self.stats.failed_requests,
                "timeout_requests": self.stats.timeout_requests,
                "circuit_opens": self.stats.circuit_opens,
                "circuit_closes": self.stats.circuit_closes,
                "current_failure_count": self.stats.current_failure_count,
                "current_success_count": self.stats.current_success_count,
                "last_failure_time": self.stats.last_failure_time.isoformat() if self.stats.last_failure_time else None,
                "last_success_time": self.stats.last_success_time.isoformat() if self.stats.last_success_time else None,
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold,
                "timeout_threshold": self.config.timeout_threshold,
                "window_size": self.config.window_size,
                "max_failures_per_window": self.config.max_failures_per_window,
            }
        }


class CircuitBreakerManager:
    """Manages multiple circuit breakers for different providers."""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.default_config = CircuitBreakerConfig()
        self._lock = asyncio.Lock()
    
    def get_circuit_breaker(self, provider_name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get or create circuit breaker for provider."""
        if provider_name not in self.circuit_breakers:
            config = config or self.default_config
            self.circuit_breakers[provider_name] = CircuitBreaker(provider_name, config)
        
        return self.circuit_breakers[provider_name]
    
    async def call_with_fallback(
        self,
        providers: List[str],
        func: Callable[[str], Awaitable[Any]],
        *args,
        **kwargs
    ) -> tuple[Any, str]:
        """Call function with multiple providers and fallback logic."""
        last_error = None
        
        for provider in providers:
            circuit_breaker = self.get_circuit_breaker(provider)
            
            try:
                # Create provider-specific function
                provider_func = lambda p=provider: func(p)
                
                result = await circuit_breaker.call(provider_func, *args, **kwargs)
                return result, provider
                
            except (CircuitBreakerOpenError, CircuitBreakerTimeoutError, CircuitBreakerFailureError) as e:
                last_error = e
                logger.warning(f"Provider {provider} failed: {e}")
                continue
        
        # All providers failed
        if last_error:
            raise last_error
        
        raise CircuitBreakerError("No providers available")
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {
            provider: circuit_breaker.get_status()
            for provider, circuit_breaker in self.circuit_breakers.items()
        }
    
    async def reset_circuit_breaker(self, provider_name: str):
        """Manually reset circuit breaker for provider."""
        if provider_name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[provider_name]
            async with circuit_breaker._lock:
                await circuit_breaker._transition_to_closed()
    
    async def reset_all_circuit_breakers(self):
        """Reset all circuit breakers."""
        for provider_name in self.circuit_breakers:
            await self.reset_circuit_breaker(provider_name)


# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager()


# Custom exceptions
class CircuitBreakerError(Exception):
    """Base exception for circuit breaker errors."""
    pass


class CircuitBreakerOpenError(CircuitBreakerError):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreakerTimeoutError(CircuitBreakerError):
    """Raised when request times out."""
    pass


class CircuitBreakerFailureError(CircuitBreakerError):
    """Raised when request fails."""
    pass


# Decorator for easy circuit breaker usage
def with_circuit_breaker(provider_name: str, config: Optional[CircuitBreakerConfig] = None):
    """Decorator to add circuit breaker protection to async functions."""
    def decorator(func: Callable[..., Awaitable[Any]]):
        async def wrapper(*args, **kwargs):
            circuit_breaker = circuit_breaker_manager.get_circuit_breaker(provider_name, config)
            return await circuit_breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator
