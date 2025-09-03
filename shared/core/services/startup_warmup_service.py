#!/usr/bin/env python3
"""
Startup Warmup Service - Background Warmup for All Services

This service coordinates background warmup tasks for:
- Vector singleton service (embedding model + vector store)
- ArangoDB knowledge graph service
- LLM provider health checks
- Any other services requiring warmup

Key Features:
- Non-blocking background warmup execution
- Structured progress logging
- Health monitoring integration
- Graceful degradation if warmup fails
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from shared.core.unified_logging import get_logger

logger = get_logger(__name__)

class WarmupStatus(Enum):
    """Warmup task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WarmupTask:
    """Individual warmup task definition."""
    
    name: str
    description: str
    priority: int  # Lower number = higher priority
    timeout_seconds: float
    required: bool  # If True, failure blocks application startup
    status: WarmupStatus = WarmupStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    
    @property
    def duration_ms(self) -> float:
        """Get task duration in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0


class StartupWarmupService:
    """Coordinates background warmup for all services."""
    
    def __init__(self):
        """Initialize warmup service."""
        self.tasks: List[WarmupTask] = []
        self.warmup_completed = False
        self.warmup_start_time = 0
        self.warmup_end_time = 0
        self.failed_tasks: List[str] = []
        
        # Define warmup tasks
        self._define_warmup_tasks()
        
        logger.info("StartupWarmupService initialized", 
                   total_tasks=len(self.tasks),
                   required_tasks=sum(1 for t in self.tasks if t.required))
    
    def _define_warmup_tasks(self):
        """Define all warmup tasks in priority order."""
        self.tasks = [
            # Priority 1: Vector Services (highest priority for search performance)
            WarmupTask(
                name="vector_singleton_init",
                description="Initialize vector singleton service (embedding + vector store)",
                priority=1,
                timeout_seconds=30.0,
                required=False  # Graceful degradation if vector services unavailable
            ),
            
            # Priority 2: Knowledge Graph Services  
            WarmupTask(
                name="arangodb_warmup",
                description="Initialize ArangoDB connection and warmup",
                priority=2,
                timeout_seconds=10.0,
                required=False  # Graceful degradation if ArangoDB unavailable
            ),
            
            # Priority 3: LLM Provider Health Checks
            WarmupTask(
                name="llm_providers_health",
                description="Check LLM provider availability and health",
                priority=3,
                timeout_seconds=15.0,
                required=False  # Application works without LLM providers
            ),
            
            # Priority 4: Search Services
            WarmupTask(
                name="search_services_warmup",
                description="Initialize Meilisearch and other search services",
                priority=4,
                timeout_seconds=10.0,
                required=False  # Search can be initialized on-demand
            ),
            
            # Priority 5: Cache Services
            WarmupTask(
                name="cache_warmup",
                description="Initialize and test cache connections",
                priority=5,
                timeout_seconds=5.0,
                required=False  # Cache failures are handled gracefully
            )
        ]
        
        # Sort by priority
        self.tasks.sort(key=lambda t: t.priority)
    
    async def _warmup_vector_singleton(self) -> bool:
        """Warmup vector singleton service."""
        try:
            from shared.core.services.vector_singleton_service import get_vector_singleton_service
            
            service = await get_vector_singleton_service()
            
            # Service initialization includes warmup
            health = await service.health_check()
            
            logger.info("Vector singleton warmup completed", 
                       initialized=health.get("initialized", False),
                       embedding_loaded=health.get("embedding", {}).get("model_loaded", False),
                       vector_connected=health.get("vector_store", {}).get("connected", False))
            
            return health.get("initialized", False)
            
        except Exception as e:
            logger.error("Vector singleton warmup failed", error=str(e))
            return False
    
    async def _warmup_arangodb(self) -> bool:
        """Warmup ArangoDB service."""
        try:
            from shared.core.services.arangodb_service import warmup_arangodb, get_arangodb_health
            
            # Execute full warmup (probe + background tasks)
            warmup_result = await warmup_arangodb()
            
            # Get health status after warmup
            health = await get_arangodb_health()
            
            logger.info("ArangoDB warmup completed",
                       warmup_status=warmup_result.get("status", "unknown"),
                       health_status=health.get("status", "unknown"),
                       warmup_completed=warmup_result.get("warmup_completed", False))
            
            return health.get("status") == "ok" and warmup_result.get("warmup_completed", False)
            
        except Exception as e:
            logger.error("ArangoDB warmup failed", error=str(e))
            return False
    
    async def _warmup_llm_providers(self) -> bool:
        """Check LLM provider health."""
        try:
            from services.gateway.real_llm_integration import real_llm_processor
            
            if hasattr(real_llm_processor, 'get_gpu_provider_health'):
                health = await real_llm_processor.get_gpu_provider_health()
                
                available_providers = health.get('available_providers', [])
                
                logger.info("LLM providers health check completed",
                           available_providers=available_providers,
                           provider_count=len(available_providers))
                
                return len(available_providers) > 0
            else:
                logger.info("LLM provider health check skipped - method not available")
                return True
                
        except Exception as e:
            logger.error("LLM providers warmup failed", error=str(e))
            return False
    
    async def _warmup_search_services(self) -> bool:
        """Warmup search services (Meilisearch, etc.)."""
        try:
            # TODO: Add Meilisearch warmup when implemented
            logger.info("Search services warmup skipped - not implemented yet")
            return True
            
        except Exception as e:
            logger.error("Search services warmup failed", error=str(e))
            return False
    
    async def _warmup_cache(self) -> bool:
        """Warmup cache services."""
        try:
            # TODO: Add cache warmup when implemented
            logger.info("Cache warmup skipped - not implemented yet")
            return True
            
        except Exception as e:
            logger.error("Cache warmup failed", error=str(e))
            return False
    
    async def _execute_task(self, task: WarmupTask) -> bool:
        """Execute a single warmup task."""
        task.status = WarmupStatus.IN_PROGRESS
        task.start_time = time.time()
        
        logger.info("Starting warmup task", 
                   task=task.name,
                   description=task.description,
                   timeout=task.timeout_seconds,
                   required=task.required)
        
        try:
            # Map task names to methods
            task_methods = {
                "vector_singleton_init": self._warmup_vector_singleton,
                "arangodb_warmup": self._warmup_arangodb,
                "llm_providers_health": self._warmup_llm_providers,
                "search_services_warmup": self._warmup_search_services,
                "cache_warmup": self._warmup_cache
            }
            
            method = task_methods.get(task.name)
            if not method:
                task.status = WarmupStatus.SKIPPED
                task.error_message = f"No method found for task {task.name}"
                logger.warning("Warmup task skipped", task=task.name, reason="method not found")
                return False
            
            # Execute with timeout
            success = await asyncio.wait_for(
                method(),
                timeout=task.timeout_seconds
            )
            
            task.end_time = time.time()
            
            if success:
                task.status = WarmupStatus.COMPLETED
                logger.info("Warmup task completed successfully",
                           task=task.name,
                           duration_ms=round(task.duration_ms, 2))
                return True
            else:
                task.status = WarmupStatus.FAILED
                task.error_message = "Task returned False"
                logger.warning("Warmup task failed",
                              task=task.name,
                              duration_ms=round(task.duration_ms, 2))
                return False
                
        except asyncio.TimeoutError:
            task.end_time = time.time()
            task.status = WarmupStatus.FAILED
            task.error_message = f"Timeout after {task.timeout_seconds}s"
            logger.error("Warmup task timed out",
                        task=task.name,
                        timeout=task.timeout_seconds,
                        duration_ms=round(task.duration_ms, 2))
            return False
            
        except Exception as e:
            task.end_time = time.time()
            task.status = WarmupStatus.FAILED
            task.error_message = str(e)
            logger.error("Warmup task failed with exception",
                        task=task.name,
                        error=str(e),
                        duration_ms=round(task.duration_ms, 2))
            return False
    
    async def execute_warmup(self) -> bool:
        """Execute all warmup tasks in priority order."""
        if self.warmup_completed:
            return True
            
        self.warmup_start_time = time.time()
        
        logger.info("Starting application warmup",
                   total_tasks=len(self.tasks),
                   required_tasks=sum(1 for t in self.tasks if t.required))
        
        # Execute tasks in priority order
        required_failures = 0
        total_failures = 0
        
        for task in self.tasks:
            success = await self._execute_task(task)
            
            if not success:
                total_failures += 1
                self.failed_tasks.append(task.name)
                
                if task.required:
                    required_failures += 1
                    logger.error("Required warmup task failed - this may affect application functionality",
                                task=task.name,
                                error=task.error_message)
        
        self.warmup_end_time = time.time()
        total_warmup_time_ms = (self.warmup_end_time - self.warmup_start_time) * 1000
        
        # Determine overall success
        self.warmup_completed = True
        overall_success = required_failures == 0
        
        if overall_success:
            logger.info("Application warmup completed successfully",
                       total_time_ms=round(total_warmup_time_ms, 2),
                       completed_tasks=len(self.tasks) - total_failures,
                       failed_tasks=total_failures,
                       required_failures=required_failures)
        else:
            logger.error("Application warmup completed with required failures",
                        total_time_ms=round(total_warmup_time_ms, 2),
                        completed_tasks=len(self.tasks) - total_failures,
                        failed_tasks=total_failures,
                        required_failures=required_failures,
                        failed_task_names=self.failed_tasks)
        
        return overall_success
    
    async def start_background_warmup(self):
        """Start warmup in background (non-blocking)."""
        async def warmup_task():
            try:
                await self.execute_warmup()
            except Exception as e:
                logger.error("Background warmup failed", error=str(e))
        
        # Start warmup task in background
        asyncio.create_task(warmup_task())
        logger.info("Background warmup started")
    
    def get_warmup_status(self) -> Dict[str, Any]:
        """Get current warmup status."""
        completed_tasks = [t for t in self.tasks if t.status == WarmupStatus.COMPLETED]
        failed_tasks = [t for t in self.tasks if t.status == WarmupStatus.FAILED]
        in_progress_tasks = [t for t in self.tasks if t.status == WarmupStatus.IN_PROGRESS]
        
        total_time_ms = 0
        if self.warmup_start_time and self.warmup_end_time:
            total_time_ms = (self.warmup_end_time - self.warmup_start_time) * 1000
        
        return {
            "warmup_completed": self.warmup_completed,
            "total_tasks": len(self.tasks),
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            "in_progress_tasks": len(in_progress_tasks),
            "failed_task_names": self.failed_tasks,
            "total_warmup_time_ms": total_time_ms,
            "tasks": [
                {
                    "name": task.name,
                    "description": task.description,
                    "status": task.status.value,
                    "duration_ms": task.duration_ms,
                    "required": task.required,
                    "error": task.error_message
                }
                for task in self.tasks
            ]
        }


# Global warmup service instance
_startup_warmup_service: Optional[StartupWarmupService] = None

def get_startup_warmup_service() -> StartupWarmupService:
    """Get or create global startup warmup service."""
    global _startup_warmup_service
    
    if _startup_warmup_service is None:
        _startup_warmup_service = StartupWarmupService()
    
    return _startup_warmup_service

async def start_application_warmup():
    """Start application warmup in background."""
    warmup_service = get_startup_warmup_service()
    await warmup_service.start_background_warmup()

def get_warmup_status() -> Dict[str, Any]:
    """Get application warmup status for /health endpoint."""
    warmup_service = get_startup_warmup_service()
    return warmup_service.get_warmup_status()
