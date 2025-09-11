# Failure Policy & Degradation - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE ARCHITECTURE**  
**Purpose**: Define failure policy and degradation strategies (timeouts, circuit breakers, partials)

---

## 🛡️ **Resilience Philosophy**

SarvanOM v2 is designed to be resilient to failures at multiple levels. The system implements graceful degradation, circuit breakers, and partial result delivery to ensure users always receive a response, even when individual components fail.

### **Core Principles**
1. **Graceful Degradation**: System continues to function with reduced capabilities
2. **Partial Results**: Return available data even when some lanes fail
3. **Circuit Breakers**: Prevent cascade failures by isolating problematic components
4. **Timeout Management**: Strict timeouts prevent hanging requests
5. **Fallback Chains**: Multiple fallback options for each component

---

## ⚡ **Timeout Strategies**

### **Timeout Hierarchy**
```
Global Timeout (5s/7s/10s)
├─ Orchestrator Timeout (500ms/700ms/900ms)
├─ Lane Timeouts (per lane budget)
├─ External API Timeouts (800ms)
├─ Database Timeouts (100ms)
└─ Cache Timeouts (10ms)
```

### **Timeout Configuration**
| Component | Timeout | Fallback Strategy | Retry Policy |
|-----------|---------|-------------------|--------------|
| **Global Query** | 5s/7s/10s | Return partial results | No retry |
| **Orchestrator** | 500ms/700ms/900ms | Skip complex coordination | No retry |
| **Web Retrieval** | 1000ms | Use cached results | 1 retry |
| **Vector Search** | 1000ms | Use keyword search | No retry |
| **Knowledge Graph** | 1000ms | Use vector search | No retry |
| **LLM Synthesis** | 1000ms | Use faster model | 1 retry |
| **External APIs** | 800ms | Use cached data | 1 retry |
| **Database** | 100ms | Use cache | 2 retries |
| **Cache** | 10ms | Skip cache | No retry |

### **Timeout Implementation**
```python
# Example timeout implementation
import asyncio
from typing import Any, Optional

class TimeoutManager:
    def __init__(self, default_timeout: float = 5.0):
        self.default_timeout = default_timeout
    
    async def execute_with_timeout(
        self, 
        coro, 
        timeout: Optional[float] = None,
        fallback: Optional[Any] = None
    ) -> Any:
        """Execute coroutine with timeout and fallback"""
        timeout = timeout or self.default_timeout
        
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            if fallback is not None:
                return fallback
            raise TimeoutError(f"Operation timed out after {timeout}s")
```

---

## 🔄 **Circuit Breaker Pattern**

### **Circuit Breaker States**
| State | Description | Behavior | Transition Condition |
|-------|-------------|----------|---------------------|
| **CLOSED** | Normal operation | All requests pass through | Initial state |
| **OPEN** | Service unavailable | All requests fail fast | Error rate > threshold |
| **HALF_OPEN** | Testing recovery | Limited requests allowed | After timeout period |

### **Circuit Breaker Configuration**
| Service | Failure Threshold | Timeout | Success Threshold | Max Requests |
|---------|------------------|---------|-------------------|--------------|
| **LLM Providers** | 50% | 60s | 80% | 5 |
| **External APIs** | 30% | 30s | 70% | 3 |
| **Database** | 20% | 10s | 90% | 10 |
| **Cache** | 10% | 5s | 95% | 20 |
| **Vector DB** | 25% | 15s | 85% | 5 |
| **Search Engine** | 25% | 15s | 85% | 5 |

### **Circuit Breaker Implementation**
```python
# Example circuit breaker implementation
import time
from enum import Enum
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        success_threshold: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.timeout
        )
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

---

## 🔄 **Fallback Chains**

### **Primary Fallback Chains**
```
Web Retrieval:
Primary → Cached Results → Knowledge Base → Error

Vector Search:
Qdrant → Meilisearch → Cached Results → Error

Knowledge Graph:
ArangoDB → Vector Search → Cached Results → Error

LLM Synthesis:
Primary Model → Secondary Model → Local Model → Cached Response → Error

External APIs:
Primary API → Secondary API → Cached Data → Error

Database:
Primary DB → Read Replica → Cache → Error
```

### **Fallback Implementation**
```python
# Example fallback chain implementation
class FallbackChain:
    def __init__(self, fallbacks: list):
        self.fallbacks = fallbacks
    
    async def execute(self, *args, **kwargs):
        """Execute fallback chain until success or exhaustion"""
        last_exception = None
        
        for i, fallback in enumerate(self.fallbacks):
            try:
                return await fallback(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if i == len(self.fallbacks) - 1:  # Last fallback
                    raise e
                continue
        
        raise last_exception

# Usage example
web_retrieval_chain = FallbackChain([
    fetch_from_web,
    get_cached_results,
    search_knowledge_base
])
```

---

## 📊 **Partial Result Delivery**

### **Partial Result Strategy**
When lanes timeout or fail, the system returns partial results with clear indicators of what data is available and what failed.

### **Partial Result Structure**
```json
{
  "status": "partial",
  "query": "What is artificial intelligence?",
  "response": "Artificial intelligence (AI) is...",
  "confidence": 0.75,
  "partial_reason": "Some lanes timed out",
  "lane_results": {
    "web_retrieval": {
      "status": "success",
      "results": [...],
      "time_ms": 800
    },
    "vector_search": {
      "status": "timeout",
      "partial_results": [...],
      "time_ms": 1000,
      "timeout_reason": "Exceeded 1000ms budget"
    },
    "knowledge_graph": {
      "status": "success",
      "results": [...],
      "time_ms": 600
    },
    "llm_synthesis": {
      "status": "success",
      "response": "Artificial intelligence (AI) is...",
      "time_ms": 900
    }
  },
  "citations": [...],
  "disagreement_detected": false,
  "trace_id": "abc123"
}
```

### **Partial Result Quality Indicators**
| Indicator | Description | Impact on Confidence |
|-----------|-------------|---------------------|
| **All Lanes Success** | 100% lane success | Confidence: 1.0 |
| **Critical Lanes Success** | LLM + 1 retrieval lane | Confidence: 0.8-0.9 |
| **LLM Success Only** | Only synthesis successful | Confidence: 0.6-0.7 |
| **Retrieval Only** | No synthesis available | Confidence: 0.4-0.5 |
| **Cached Results Only** | All lanes failed, cache used | Confidence: 0.3-0.4 |

---

## 🚨 **Error Handling & Recovery**

### **Error Classification**
| Error Type | Severity | Recovery Strategy | User Impact |
|------------|----------|-------------------|-------------|
| **Timeout** | Medium | Use fallback/partial results | Reduced quality |
| **Circuit Breaker Open** | High | Use alternative service | Service degradation |
| **External API Failure** | Medium | Use cached data | Stale information |
| **Database Failure** | High | Use cache/read replica | Service degradation |
| **LLM Provider Failure** | High | Use alternative model | Quality variation |
| **Cache Failure** | Low | Skip cache, direct access | Slightly slower |

### **Error Recovery Strategies**
```python
# Example error recovery implementation
class ErrorRecoveryManager:
    def __init__(self):
        self.recovery_strategies = {
            "timeout": self.handle_timeout,
            "circuit_breaker_open": self.handle_circuit_breaker,
            "external_api_failure": self.handle_external_api_failure,
            "database_failure": self.handle_database_failure,
            "llm_provider_failure": self.handle_llm_failure,
            "cache_failure": self.handle_cache_failure
        }
    
    async def recover(self, error_type: str, context: dict) -> Any:
        """Recover from error using appropriate strategy"""
        strategy = self.recovery_strategies.get(error_type)
        if strategy:
            return await strategy(context)
        else:
            raise UnrecoverableError(f"No recovery strategy for {error_type}")
    
    async def handle_timeout(self, context: dict) -> Any:
        """Handle timeout errors"""
        if "partial_results" in context:
            return context["partial_results"]
        elif "fallback" in context:
            return await context["fallback"]()
        else:
            raise TimeoutError("No recovery options available")
    
    async def handle_circuit_breaker(self, context: dict) -> Any:
        """Handle circuit breaker open errors"""
        if "alternative_service" in context:
            return await context["alternative_service"]()
        elif "cached_data" in context:
            return context["cached_data"]
        else:
            raise ServiceUnavailableError("No alternative services available")
```

---

## 📈 **Resilience Monitoring**

### **Key Resilience Metrics**
| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| **Error Rate** | % of requests with errors | < 5% | > 10% |
| **Timeout Rate** | % of requests timing out | < 3% | > 5% |
| **Circuit Breaker Open Rate** | % of time circuit breakers open | < 1% | > 5% |
| **Fallback Usage Rate** | % of requests using fallbacks | < 10% | > 20% |
| **Partial Result Rate** | % of requests returning partial results | < 5% | > 15% |
| **Recovery Success Rate** | % of errors successfully recovered | > 90% | < 80% |

### **Resilience Dashboard**
```python
# Example resilience monitoring
class ResilienceMonitor:
    def __init__(self):
        self.metrics = {
            "error_rate": 0.0,
            "timeout_rate": 0.0,
            "circuit_breaker_open_rate": 0.0,
            "fallback_usage_rate": 0.0,
            "partial_result_rate": 0.0,
            "recovery_success_rate": 0.0
        }
    
    def record_error(self, error_type: str, recovered: bool):
        """Record error and recovery status"""
        self.metrics["error_rate"] += 1
        if error_type == "timeout":
            self.metrics["timeout_rate"] += 1
        if recovered:
            self.metrics["recovery_success_rate"] += 1
    
    def record_circuit_breaker_state(self, service: str, state: str):
        """Record circuit breaker state changes"""
        if state == "open":
            self.metrics["circuit_breaker_open_rate"] += 1
    
    def record_fallback_usage(self, fallback_type: str):
        """Record fallback usage"""
        self.metrics["fallback_usage_rate"] += 1
    
    def record_partial_result(self, reason: str):
        """Record partial result delivery"""
        self.metrics["partial_result_rate"] += 1
```

---

## 🔧 **Resilience Configuration**

### **Environment Variables**
| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `CIRCUIT_BREAKER_FAILURE_THRESHOLD` | 5 | Failures before opening circuit | 5 |
| `CIRCUIT_BREAKER_TIMEOUT_SECONDS` | 60 | Time before attempting reset | 60 |
| `CIRCUIT_BREAKER_SUCCESS_THRESHOLD` | 3 | Successes to close circuit | 3 |
| `FALLBACK_ENABLED` | true | Enable fallback strategies | true |
| `PARTIAL_RESULTS_ENABLED` | true | Enable partial result delivery | true |
| `ERROR_RECOVERY_ENABLED` | true | Enable error recovery | true |

### **Resilience Testing**
```python
# Example resilience testing
class ResilienceTestSuite:
    def test_timeout_handling(self):
        """Test timeout handling and fallback"""
        result = self.process_query_with_timeout("Test query", timeout_ms=1000)
        assert result["status"] in ["success", "partial"]
        assert "timeout" in result.get("lane_results", {})
    
    def test_circuit_breaker(self):
        """Test circuit breaker functionality"""
        # Simulate failures to open circuit breaker
        for _ in range(6):
            try:
                self.call_failing_service()
            except Exception:
                pass
        
        # Circuit breaker should be open
        with pytest.raises(CircuitBreakerOpenError):
            self.call_failing_service()
    
    def test_fallback_chain(self):
        """Test fallback chain execution"""
        result = self.execute_with_failures("Test operation")
        assert result is not None
        assert "fallback_used" in result
    
    def test_partial_results(self):
        """Test partial result delivery"""
        result = self.process_query_with_lane_failures("Test query")
        assert result["status"] == "partial"
        assert "partial_reason" in result
        assert "lane_results" in result
```

---

## 📚 **References**

- System Context: `docs/architecture/system_context.md`
- Service Catalog: `docs/architecture/service_catalog.md`
- Budgets: `docs/architecture/budgets.md`
- Observability: `09_observability_and_budgets.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This resilience specification ensures SarvanOM v2 continues to function reliably even when individual components fail.*
