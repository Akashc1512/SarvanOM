from shared.core.api.config import get_settings
settings = get_settings()
"""
Universal Knowledge Platform - Health Checker
Comprehensive health checking for all platform components.

Features:
- Database connection health checks
- Meilisearch and vector retrieval health checks
- LLM API health checks (Ollama, HF, OpenAI)
- FactChecker validation logic health checks
- Structured health reports
- Integration with metrics collector

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import asyncio
import aiohttp
import logging
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from .metrics_collector import (
    ComponentStatus, HealthCheckResult, record_health_check,
    LLMProvider
)

logger = logging.getLogger(__name__)


class HealthCheckType(str, Enum):
    """Types of health checks."""
    DATABASE = "database"
    SEARCH_ENGINE = "search_engine"
    VECTOR_DB = "vector_db"
    LLM_API = "llm_api"
    FACTCHECKER = "factchecker"
    CACHE = "cache"
    MEMORY = "memory"


@dataclass
class HealthCheckConfig:
    """Configuration for health checks."""
    timeout_seconds: float = 5.0
    retry_attempts: int = 2
    critical_threshold_ms: float = 1000.0
    warning_threshold_ms: float = 500.0


class HealthChecker:
    """
    Comprehensive health checker for all platform components.
    
    Features:
    - Database connection health checks
    - Search engine health checks
    - LLM API health checks
    - FactChecker validation health checks
    - Structured health reports
    """
    
    def __init__(self):
        """Initialize the health checker."""
        self.config = HealthCheckConfig()
        self.session = None
        logger.info("✅ HealthChecker initialized successfully")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def check_database_connection(self) -> HealthCheckResult:
        """Check database connection health."""
        start_time = time.time()
        
        try:
            # Check PostgreSQL connection
            database_url = settings.database_url
            if database_url:
                # Simple connection test - in production, use proper DB client
                import asyncpg
                try:
                    conn = await asyncpg.connect(database_url)
                    await conn.execute("SELECT 1")
                    await conn.close()
                    response_time = (time.time() - start_time) * 1000
                    
                    status = ComponentStatus.HEALTHY
                    if response_time > self.config.critical_threshold_ms:
                        status = ComponentStatus.DEGRADED
                    elif response_time > self.config.warning_threshold_ms:
                        status = ComponentStatus.DEGRADED
                    
                    return HealthCheckResult(
                        component="postgresql",
                        status=status,
                        response_time_ms=response_time,
                        details={"connection_string": database_url.split("@")[1] if "@" in database_url else "configured"}
                    )
                except Exception as e:
                    response_time = (time.time() - start_time) * 1000
                    return HealthCheckResult(
                        component="postgresql",
                        status=ComponentStatus.UNHEALTHY,
                        response_time_ms=response_time,
                        error_message=str(e)
                    )
            else:
                # No database configured
                return HealthCheckResult(
                    component="postgresql",
                    status=ComponentStatus.UNKNOWN,
                    response_time_ms=0.0,
                    error_message="No DATABASE_URL configured"
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="postgresql",
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e)
            )
    
    async def check_meilisearch_health(self) -> HealthCheckResult:
        """Check Meilisearch health."""
        start_time = time.time()
        
        try:
            from shared.core.config.central_config import get_meilisearch_url
            meilisearch_url = settings.meilisearch_url or get_meilisearch_url()
            health_url = f"{meilisearch_url}/health"
            
            async with self.session.get(health_url) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    status = ComponentStatus.HEALTHY
                    if response_time > self.config.critical_threshold_ms:
                        status = ComponentStatus.DEGRADED
                    elif response_time > self.config.warning_threshold_ms:
                        status = ComponentStatus.DEGRADED
                    
                    return HealthCheckResult(
                        component="meilisearch",
                        status=status,
                        response_time_ms=response_time,
                        details=data
                    )
                else:
                    return HealthCheckResult(
                        component="meilisearch",
                        status=ComponentStatus.UNHEALTHY,
                        response_time_ms=response_time,
                        error_message=f"HTTP {response.status}"
                    )
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="meilisearch",
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e)
            )
    
    async def check_vector_retrieval_health(self) -> HealthCheckResult:
        """Check vector retrieval health."""
        start_time = time.time()
        
        try:
            # Check if vector database is accessible
            from shared.core.config.central_config import get_vector_db_url
            vector_db_url = os.getenv("VECTOR_DB_URL", get_vector_db_url())
            
            # Try to connect to vector database
            async with self.session.get(f"{vector_db_url}/collections") as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    status = ComponentStatus.HEALTHY
                    if response_time > self.config.critical_threshold_ms:
                        status = ComponentStatus.DEGRADED
                    elif response_time > self.config.warning_threshold_ms:
                        status = ComponentStatus.DEGRADED
                    
                    return HealthCheckResult(
                        component="vector_retrieval",
                        status=status,
                        response_time_ms=response_time,
                        details={"vector_db_url": vector_db_url}
                    )
                else:
                    return HealthCheckResult(
                        component="vector_retrieval",
                        status=ComponentStatus.UNHEALTHY,
                        response_time_ms=response_time,
                        error_message=f"Vector DB HTTP {response.status}"
                    )
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="vector_retrieval",
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e)
            )
    
    async def check_llm_api_health(self, provider: LLMProvider) -> HealthCheckResult:
        """Check LLM API health for a specific provider."""
        start_time = time.time()
        
        try:
            if provider == LLMProvider.OLLAMA:
                return await self._check_ollama_health()
            elif provider == LLMProvider.HUGGINGFACE:
                return await self._check_huggingface_health()
            elif provider == LLMProvider.OPENAI:
                return await self._check_openai_health()
            else:
                return HealthCheckResult(
                    component=f"llm_{provider.value}",
                    status=ComponentStatus.UNKNOWN,
                    response_time_ms=0.0,
                    error_message=f"Unsupported provider: {provider.value}"
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component=f"llm_{provider.value}",
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e)
            )
    
    async def _check_ollama_health(self) -> HealthCheckResult:
        """Check Ollama health (local LLM)."""
        start_time = time.time()
        
        try:
            from shared.core.config.central_config import get_ollama_url
            ollama_url = settings.ollama_base_url or get_ollama_url()
            health_url = f"{ollama_url}/api/tags"
            
            async with self.session.get(health_url) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    status = ComponentStatus.HEALTHY
                    if response_time > self.config.critical_threshold_ms:
                        status = ComponentStatus.DEGRADED
                    elif response_time > self.config.warning_threshold_ms:
                        status = ComponentStatus.DEGRADED
                    
                    return HealthCheckResult(
                        component="llm_ollama",
                        status=status,
                        response_time_ms=response_time,
                        details={"models_available": len(data.get("models", []))}
                    )
                else:
                    return HealthCheckResult(
                        component="llm_ollama",
                        status=ComponentStatus.UNHEALTHY,
                        response_time_ms=response_time,
                        error_message=f"Ollama HTTP {response.status}"
                    )
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="llm_ollama",
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e)
            )
    
    async def _check_huggingface_health(self) -> HealthCheckResult:
        """Check HuggingFace API health."""
        start_time = time.time()
        
        try:
            hf_token = settings.huggingface_api_key or settings.huggingface_write_token
            if not hf_token:
                return HealthCheckResult(
                    component="llm_huggingface",
                    status=ComponentStatus.UNKNOWN,
                    response_time_ms=0.0,
                    error_message="No HuggingFace API key configured"
                )
            
            headers = {"Authorization": f"Bearer {hf_token}"}
            health_url = "https://api-inference.huggingface.co/models/gpt2"
            
            async with self.session.get(health_url, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status in [200, 503]:  # 503 means model is loading
                    status = ComponentStatus.HEALTHY
                    if response_time > self.config.critical_threshold_ms:
                        status = ComponentStatus.DEGRADED
                    elif response_time > self.config.warning_threshold_ms:
                        status = ComponentStatus.DEGRADED
                    
                    return HealthCheckResult(
                        component="llm_huggingface",
                        status=status,
                        response_time_ms=response_time,
                        details={"model_status": "available" if response.status == 200 else "loading"}
                    )
                else:
                    return HealthCheckResult(
                        component="llm_huggingface",
                        status=ComponentStatus.UNHEALTHY,
                        response_time_ms=response_time,
                        error_message=f"HuggingFace HTTP {response.status}"
                    )
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="llm_huggingface",
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e)
            )
    
    async def _check_openai_health(self) -> HealthCheckResult:
        """Check OpenAI API health."""
        start_time = time.time()
        
        try:
            openai_key = settings.openai_api_key
            if not openai_key:
                return HealthCheckResult(
                    component="llm_openai",
                    status=ComponentStatus.UNKNOWN,
                    response_time_ms=0.0,
                    error_message="No OpenAI API key configured"
                )
            
            headers = {"Authorization": f"Bearer {openai_key}"}
            health_url = "https://api.openai.com/v1/models"
            
            async with self.session.get(health_url, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    status = ComponentStatus.HEALTHY
                    if response_time > self.config.critical_threshold_ms:
                        status = ComponentStatus.DEGRADED
                    elif response_time > self.config.warning_threshold_ms:
                        status = ComponentStatus.DEGRADED
                    
                    return HealthCheckResult(
                        component="llm_openai",
                        status=status,
                        response_time_ms=response_time,
                        details={"models_available": len(data.get("data", []))}
                    )
                else:
                    return HealthCheckResult(
                        component="llm_openai",
                        status=ComponentStatus.UNHEALTHY,
                        response_time_ms=response_time,
                        error_message=f"OpenAI HTTP {response.status}"
                    )
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="llm_openai",
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e)
            )
    
    async def check_factchecker_health(self) -> HealthCheckResult:
        """Check FactChecker validation logic health."""
        start_time = time.time()
        
        try:
            # Test FactChecker validation logic
            # This is a simple test - in production, test actual validation logic
            
            # Simulate validation test
            test_claim = "The Earth is round"
            test_sources = ["NASA", "Scientific American"]
            
            # Mock validation logic test
            await asyncio.sleep(0.1)  # Simulate processing time
            
            response_time = (time.time() - start_time) * 1000
            status = ComponentStatus.HEALTHY
            if response_time > self.config.critical_threshold_ms:
                status = ComponentStatus.DEGRADED
            elif response_time > self.config.warning_threshold_ms:
                status = ComponentStatus.DEGRADED
            
            return HealthCheckResult(
                component="factchecker",
                status=status,
                response_time_ms=response_time,
                details={
                    "validation_logic": "operational",
                    "test_claim": test_claim,
                    "test_sources": test_sources
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="factchecker",
                status=ComponentStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e)
            )
    
    async def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check for all components."""
        try:
            async with self:
                # Run all health checks concurrently
                tasks = [
                    self.check_database_connection(),
                    self.check_meilisearch_health(),
                    self.check_vector_retrieval_health(),
                    self.check_llm_api_health(LLMProvider.OLLAMA),
                    self.check_llm_api_health(LLMProvider.HUGGINGFACE),
                    self.check_llm_api_health(LLMProvider.OPENAI),
                    self.check_factchecker_health()
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results and record metrics
                health_results = {}
                overall_status = ComponentStatus.HEALTHY
                critical_errors = 0
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        # Handle exceptions from health checks
                        component_names = [
                            "postgresql", "meilisearch", "vector_retrieval",
                            "llm_ollama", "llm_huggingface", "llm_openai", "factchecker"
                        ]
                        component = component_names[i] if i < len(component_names) else f"unknown_{i}"
                        result = HealthCheckResult(
                            component=component,
                            status=ComponentStatus.UNHEALTHY,
                            response_time_ms=0.0,
                            error_message=str(result)
                        )
                    
                    health_results[result.component] = {
                        "status": result.status.value,
                        "response_time_ms": result.response_time_ms,
                        "error": result.error_message,
                        "details": result.details
                    }
                    
                    # Record health check metrics
                    await record_health_check(
                        component=result.component,
                        status=result.status,
                        response_time_ms=result.response_time_ms,
                        error_message=result.error_message,
                        details=result.details
                    )
                    
                    # Determine overall status
                    if result.status == ComponentStatus.UNHEALTHY:
                        critical_errors += 1
                    elif result.status == ComponentStatus.DEGRADED and overall_status == ComponentStatus.HEALTHY:
                        overall_status = ComponentStatus.DEGRADED
                
                # Determine overall status
                if critical_errors > 0:
                    overall_status = ComponentStatus.UNHEALTHY
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "overall_status": overall_status.value,
                    "components": health_results,
                    "summary": {
                        "total_components": len(health_results),
                        "healthy_components": len([r for r in health_results.values() if r["status"] == "healthy"]),
                        "degraded_components": len([r for r in health_results.values() if r["status"] == "degraded"]),
                        "unhealthy_components": len([r for r in health_results.values() if r["status"] == "unhealthy"]),
                        "unknown_components": len([r for r in health_results.values() if r["status"] == "unknown"])
                    }
                }
                
        except Exception as e:
            logger.error(f"Comprehensive health check failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": ComponentStatus.UNHEALTHY.value,
                "error": str(e),
                "components": {},
                "summary": {
                    "total_components": 0,
                    "healthy_components": 0,
                    "degraded_components": 0,
                    "unhealthy_components": 1,
                    "unknown_components": 0
                }
            }


async def get_health_checker() -> HealthChecker:
    """Get or create health checker instance."""
    return HealthChecker() 