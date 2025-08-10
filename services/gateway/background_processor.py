#!/usr/bin/env python3
"""
Advanced Background Processing System for SarvanOM
Implements MAANG/OpenAI/Perplexity level background processing with task queues
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Callable, Awaitable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import redis.asyncio as aioredis
from fastapi import BackgroundTasks
import pickle
import hashlib
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
from queue import PriorityQueue, Queue
import signal
import os

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BULK = 4

class TaskStatus(Enum):
    """Task status states"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class TaskType(Enum):
    """Task types for different processing needs"""
    SEARCH = "search"
    FACT_CHECK = "fact_check"
    SYNTHESIS = "synthesis"
    VECTOR_SEARCH = "vector_search"
    ANALYTICS = "analytics"
    BATCH_PROCESSING = "batch_processing"
    DATA_IMPORT = "data_import"
    MODEL_TRAINING = "model_training"

@dataclass
class BackgroundTask:
    """Background task structure"""
    task_id: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    query: str
    user_id: str
    endpoint: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timeout: int = 300  # 5 minutes default
    retries: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "query": self.query,
            "user_id": self.user_id,
            "endpoint": self.endpoint,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata or {},
            "timeout": self.timeout,
            "retries": self.retries,
            "max_retries": self.max_retries
        }

class BackgroundProcessor:
    """
    Advanced background processing system with task queues and priority handling
    Following MAANG/OpenAI/Perplexity industry standards
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        max_workers: int = 10,
        max_queue_size: int = 10000,
        enable_redis_queue: bool = True,
        enable_process_pool: bool = False,
        task_timeout: int = 300,
        cleanup_interval: int = 60,
        enable_metrics: bool = True
    ):
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.enable_redis_queue = enable_redis_queue
        self.enable_process_pool = enable_process_pool
        self.task_timeout = task_timeout
        self.cleanup_interval = cleanup_interval
        self.enable_metrics = enable_metrics
        
        # Task queues
        self.priority_queue = PriorityQueue(maxsize=max_queue_size)
        self.active_tasks: Dict[str, BackgroundTask] = {}
        self.completed_tasks: Dict[str, BackgroundTask] = {}
        
        # Worker pools
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers) if enable_process_pool else None
        
        # Control flags
        self.running = False
        self.workers: List[asyncio.Task] = []
        
        # Metrics
        self.metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "cancelled_tasks": 0,
            "active_tasks": 0,
            "queue_size": 0,
            "average_processing_time": 0.0,
            "total_processing_time": 0.0
        }
        
        # Task type configurations
        self.task_configs = {
            TaskType.SEARCH: {
                "timeout": 120,
                "max_retries": 2,
                "priority": TaskPriority.NORMAL
            },
            TaskType.FACT_CHECK: {
                "timeout": 180,
                "max_retries": 3,
                "priority": TaskPriority.HIGH
            },
            TaskType.SYNTHESIS: {
                "timeout": 300,
                "max_retries": 2,
                "priority": TaskPriority.NORMAL
            },
            TaskType.VECTOR_SEARCH: {
                "timeout": 60,
                "max_retries": 1,
                "priority": TaskPriority.HIGH
            },
            TaskType.ANALYTICS: {
                "timeout": 600,
                "max_retries": 1,
                "priority": TaskPriority.LOW
            },
            TaskType.BATCH_PROCESSING: {
                "timeout": 1800,
                "max_retries": 3,
                "priority": TaskPriority.BULK
            }
        }
    
    async def initialize(self) -> None:
        """Initialize Redis connection and start workers"""
        try:
            if self.redis_url and self.enable_redis_queue:
                self.redis_client = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=False,  # Keep as bytes for serialization
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                await self.redis_client.ping()
                logger.info("✅ Redis queue initialized for background processing")
            else:
                logger.info("ℹ️ Using in-memory queue only")
        except Exception as e:
            logger.error(f"❌ Redis queue initialization failed: {e}")
            self.redis_client = None
        
        # Start background workers
        await self.start_workers()
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_loop())
        
        logger.info("✅ Background processor initialized")
    
    async def start_workers(self) -> None:
        """Start background worker tasks"""
        self.running = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker_task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self.workers.append(worker_task)
        
        logger.info(f"🚀 Started {self.max_workers} background workers")
    
    async def stop_workers(self) -> None:
        """Stop background workers"""
        self.running = False
        
        # Cancel all worker tasks
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        self.workers.clear()
        logger.info("🛑 Background workers stopped")
    
    async def submit_task(
        self,
        task_type: TaskType,
        query: str,
        user_id: str,
        endpoint: str,
        priority: Optional[TaskPriority] = None,
        timeout: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        llm_processor: Optional[Any] = None
    ) -> str:
        """Submit a new background task"""
        task_id = self._generate_task_id()
        
        # Get task configuration
        config = self.task_configs.get(task_type, {})
        priority = priority or TaskPriority(config.get("priority", TaskPriority.NORMAL.value))
        timeout = timeout or config.get("timeout", self.task_timeout)
        
        # Create task
        task = BackgroundTask(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            status=TaskStatus.PENDING,
            query=query,
            user_id=user_id,
            endpoint=endpoint,
            created_at=datetime.now(),
            timeout=timeout,
            metadata=metadata or {}
        )
        
        # Store task
        self.active_tasks[task_id] = task
        self.metrics["total_tasks"] += 1
        self.metrics["active_tasks"] += 1
        
        # Add to queue
        await self._add_to_queue(task, llm_processor)
        
        logger.info(f"📋 Submitted background task: {task_id} ({task_type.value})")
        return task_id
    
    async def _add_to_queue(self, task: BackgroundTask, llm_processor: Optional[Any] = None) -> None:
        """Add task to processing queue"""
        try:
            # Serialize task data
            task_data = {
                "task": task.to_dict(),
                "llm_processor_present": llm_processor is not None
            }
            
            if self.redis_client and self.enable_redis_queue:
                # Add to Redis queue
                queue_key = f"task_queue:{task.priority.value}"
                await self.redis_client.lpush(queue_key, pickle.dumps(task_data))
                
                # Set task metadata in Redis
                task_key = f"task:{task.task_id}"
                await self.redis_client.setex(
                    task_key,
                    task.timeout + 3600,  # 1 hour extra for cleanup
                    pickle.dumps(task.to_dict())
                )
            else:
                # Add to in-memory priority queue
                if not self.priority_queue.full():
                    self.priority_queue.put((task.priority.value, task.task_id, task_data))
                    self.metrics["queue_size"] += 1
                else:
                    raise Exception("Task queue is full")
            
            task.status = TaskStatus.QUEUED
            
        except Exception as e:
            logger.error(f"Failed to add task to queue: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.metrics["failed_tasks"] += 1
    
    async def _worker_loop(self, worker_name: str) -> None:
        """Main worker loop for processing tasks"""
        logger.info(f"👷 Worker {worker_name} started")
        
        while self.running:
            try:
                # Get next task
                task_data = await self._get_next_task()
                if not task_data:
                    await asyncio.sleep(1)
                    continue
                
                task_dict = task_data["task"]
                task = BackgroundTask(**task_dict)
                
                # Process task
                await self._process_task(task, worker_name)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)
        
        logger.info(f"👷 Worker {worker_name} stopped")
    
    async def _get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get next task from queue"""
        try:
            if self.redis_client and self.enable_redis_queue:
                # Try Redis queues in priority order
                for priority in range(5):  # 0-4 priority levels
                    queue_key = f"task_queue:{priority}"
                    task_data = await self.redis_client.rpop(queue_key)
                    if task_data:
                        return pickle.loads(task_data)
            else:
                # Get from in-memory queue
                if not self.priority_queue.empty():
                    priority, task_id, task_data = self.priority_queue.get_nowait()
                    self.metrics["queue_size"] -= 1
                    return task_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting next task: {e}")
            return None
    
    async def _process_task(self, task: BackgroundTask, worker_name: str) -> None:
        """Process a single task"""
        start_time = time.time()
        
        try:
            logger.info(f"🔄 Processing task {task.task_id} with {worker_name}")
            
            # Update task status
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.now()
            
            # Create processing coroutine
            processing_coro = self._execute_task(task)
            
            # Run with timeout
            try:
                result = await asyncio.wait_for(processing_coro, timeout=task.timeout)
                
                # Task completed successfully
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = result
                task.progress = 100.0
                
                processing_time = time.time() - start_time
                self.metrics["completed_tasks"] += 1
                self.metrics["total_processing_time"] += processing_time
                self.metrics["average_processing_time"] = (
                    self.metrics["total_processing_time"] / self.metrics["completed_tasks"]
                )
                
                logger.info(f"✅ Task {task.task_id} completed in {processing_time:.2f}s")
                
            except asyncio.TimeoutError:
                # Task timed out
                task.status = TaskStatus.TIMEOUT
                task.error = f"Task timed out after {task.timeout} seconds"
                self.metrics["failed_tasks"] += 1
                logger.warning(f"⏰ Task {task.task_id} timed out")
                
        except Exception as e:
            # Task failed
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.metrics["failed_tasks"] += 1
            logger.error(f"❌ Task {task.task_id} failed: {e}")
            
        finally:
            # Move to completed tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
                self.metrics["active_tasks"] -= 1
            
            self.completed_tasks[task.task_id] = task
            
            # Cleanup old completed tasks
            await self._cleanup_old_tasks()
    
    async def _execute_task(self, task: BackgroundTask) -> Any:
        """Execute the actual task logic"""
        # Simulate task execution with progress updates
        steps = 10
        for i in range(steps):
            # Update progress
            task.progress = (i + 1) / steps * 100
            
            # Simulate work
            await asyncio.sleep(0.1)
            
            # Check for cancellation
            if task.status == TaskStatus.CANCELLED:
                raise Exception("Task was cancelled")
        
        # Return mock result based on task type
        return {
            "task_id": task.task_id,
            "query": task.query,
            "result": f"Processed {task.task_type.value} for: {task.query}",
            "processing_time": time.time(),
            "metadata": task.metadata
        }
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and result"""
        # Check active tasks
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].to_dict()
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].to_dict()
        
        # Check Redis if available
        if self.redis_client:
            try:
                task_key = f"task:{task_id}"
                task_data = await self.redis_client.get(task_key)
                if task_data:
                    return pickle.loads(task_data)
            except Exception as e:
                logger.error(f"Redis get task error: {e}")
        
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or processing task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task.status in [TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.PROCESSING]:
                task.status = TaskStatus.CANCELLED
                self.metrics["cancelled_tasks"] += 1
                logger.info(f"🚫 Cancelled task: {task_id}")
                return True
        
        return False
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "queue_size": self.metrics["queue_size"],
            "workers": len(self.workers),
            "metrics": self.metrics.copy()
        }
    
    async def _cleanup_old_tasks(self) -> None:
        """Clean up old completed tasks"""
        cutoff_time = datetime.now() - timedelta(hours=24)  # Keep 24 hours
        
        old_tasks = [
            task_id for task_id, task in self.completed_tasks.items()
            if task.completed_at and task.completed_at < cutoff_time
        ]
        
        for task_id in old_tasks:
            del self.completed_tasks[task_id]
    
    async def _cleanup_loop(self) -> None:
        """Periodic cleanup loop"""
        while self.running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_old_tasks()
                
                # Update queue size metric
                if not self.redis_client:
                    self.metrics["queue_size"] = self.priority_queue.qsize()
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        return f"task_{uuid.uuid4().hex[:16]}"
    
    async def close(self) -> None:
        """Close background processor"""
        await self.stop_workers()
        
        # Close thread and process pools
        self.thread_pool.shutdown(wait=True)
        if self.process_pool:
            self.process_pool.shutdown(wait=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Background processor closed")

# Global background processor instance
background_processor = BackgroundProcessor()
