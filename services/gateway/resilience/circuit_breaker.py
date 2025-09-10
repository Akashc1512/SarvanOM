"""
Circuit Breaker Implementation for MAANG Standards

Provides circuit breaker pattern for LLM providers to prevent cascade failures
and improve system reliability.
"""

import time
import asyncio
from typing import Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service is back


class CircuitBreakerException(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreakerError(CircuitBreakerException):
    """Alias for CircuitBreakerException for backward compatibility."""
    pass


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    timeout: int = 60
    expected_exception: type = Exception
    name: str = "circuit_breaker"


class CircuitBreaker:
    """
    Circuit breaker implementation following MAANG reliability standards.
    
    Prevents cascade failures by monitoring service health and failing fast
    when services are down.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception,
        name: str = "circuit_breaker"
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before trying to close circuit
            expected_exception: Exception type to count as failures
            name: Name for logging purposes
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.name = name
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED
        
        logger.info(f"Circuit breaker '{name}' initialized: threshold={failure_threshold}, timeout={timeout}s")
    
    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self.state == CircuitState.OPEN
    
    def is_closed(self) -> bool:
        """Check if circuit is closed."""
        return self.state == CircuitState.CLOSED
    
    def is_half_open(self) -> bool:
        """Check if circuit is half-open."""
        return self.state == CircuitState.HALF_OPEN
    
    def record_success(self):
        """Record a successful call."""
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit breaker '{self.name}' closing after successful call")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            logger.warning(f"Circuit breaker '{self.name}' opening after {self.failure_count} failures")
            self.state = CircuitState.OPEN
    
    def should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.state != CircuitState.OPEN:
            return False
        
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.timeout
    
    def attempt_reset(self):
        """Attempt to reset circuit to half-open state."""
        if self.should_attempt_reset():
            logger.info(f"Circuit breaker '{self.name}' attempting reset to half-open")
            self.state = CircuitState.HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerException: If circuit is open
            Exception: If function execution fails
        """
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self.should_attempt_reset():
                self.attempt_reset()
            else:
                logger.warning(f"Circuit breaker '{self.name}' is open, failing fast")
                raise CircuitBreakerException(f"Circuit breaker '{self.name}' is open")
        
        # Execute function
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self.record_success()
            return result
            
        except self.expected_exception as e:
            self.record_failure()
            logger.error(f"Circuit breaker '{self.name}' recorded failure: {e}")
            raise e
        except Exception as e:
            # Unexpected exception, don't count as failure
            logger.error(f"Circuit breaker '{self.name}' unexpected exception: {e}")
            raise e
    
    def get_status(self) -> dict:
        """Get current circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time,
            "timeout": self.timeout,
            "is_healthy": self.state == CircuitState.CLOSED
        }


class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers.
    
    Provides centralized management of circuit breakers for different services.
    """
    
    def __init__(self):
        self.breakers: dict[str, CircuitBreaker] = {}
    
    def get_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Get or create a circuit breaker."""
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(name=name, **kwargs)
        return self.breakers[name]
    
    def get_all_status(self) -> dict:
        """Get status of all circuit breakers."""
        return {
            name: breaker.get_status()
            for name, breaker in self.breakers.items()
        }
    
    def reset_all(self):
        """Reset all circuit breakers to closed state."""
        for breaker in self.breakers.values():
            breaker.state = CircuitState.CLOSED
            breaker.failure_count = 0
            breaker.last_failure_time = None
        logger.info("All circuit breakers reset")


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()