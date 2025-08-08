"""
Metrics Service

This module provides metrics collection and monitoring functionality.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MetricsService:
    """Provides metrics collection and monitoring functionality."""
    
    def __init__(self):
        self._metrics: Dict[str, Any] = defaultdict(dict)
        self._counters: Dict[str, int] = defaultdict(int)
        self._timers: Dict[str, List[float]] = defaultdict(list)
        self._histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._start_time = datetime.now()
    
    async def track_query_processing(
        self, 
        query_id: str, 
        query_type: str, 
        processing_time: float, 
        cache_hit: bool
    ):
        """Track query processing metrics."""
        try:
            # Increment counters
            self._counters["total_queries"] += 1
            self._counters[f"queries_{query_type}"] += 1
            
            if cache_hit:
                self._counters["cache_hits"] += 1
            else:
                self._counters["cache_misses"] += 1
            
            # Track processing time
            self._timers["query_processing_time"].append(processing_time)
            self._histograms["query_processing_time"].append(processing_time)
            
            # Track by query type
            self._timers[f"query_processing_time_{query_type}"].append(processing_time)
            
            # Track cache performance
            cache_key = "cache_hit_rate"
            total_queries = self._counters["total_queries"]
            cache_hits = self._counters["cache_hits"]
            self._metrics[cache_key] = cache_hits / total_queries if total_queries > 0 else 0
            
            logger.debug(f"Tracked query processing: {query_id}, type: {query_type}, time: {processing_time}s")
            
        except Exception as e:
            logger.error(f"Error tracking query processing metrics: {e}", exc_info=True)
    
    async def track_query_error(
        self, 
        query_id: str, 
        error_type: str, 
        processing_time: float
    ):
        """Track query error metrics."""
        try:
            # Increment error counters
            self._counters["total_errors"] += 1
            self._counters[f"errors_{error_type}"] += 1
            
            # Track error processing time
            self._timers["error_processing_time"].append(processing_time)
            self._histograms["error_processing_time"].append(processing_time)
            
            # Calculate error rate
            total_queries = self._counters["total_queries"]
            total_errors = self._counters["total_errors"]
            self._metrics["error_rate"] = total_errors / total_queries if total_queries > 0 else 0
            
            logger.debug(f"Tracked query error: {query_id}, type: {error_type}, time: {processing_time}s")
            
        except Exception as e:
            logger.error(f"Error tracking query error metrics: {e}", exc_info=True)
    
    async def track_agent_usage(self, agent_type: str, processing_time: float, success: bool):
        """Track agent usage metrics."""
        try:
            # Increment agent counters
            self._counters[f"agent_calls_{agent_type}"] += 1
            
            if success:
                self._counters[f"agent_success_{agent_type}"] += 1
            else:
                self._counters[f"agent_errors_{agent_type}"] += 1
            
            # Track processing time
            self._timers[f"agent_processing_time_{agent_type}"].append(processing_time)
            self._histograms[f"agent_processing_time_{agent_type}"].append(processing_time)
            
            # Calculate success rate
            total_calls = self._counters[f"agent_calls_{agent_type}"]
            successful_calls = self._counters[f"agent_success_{agent_type}"]
            self._metrics[f"agent_success_rate_{agent_type}"] = (
                successful_calls / total_calls if total_calls > 0 else 0
            )
            
            logger.debug(f"Tracked agent usage: {agent_type}, success: {success}, time: {processing_time}s")
            
        except Exception as e:
            logger.error(f"Error tracking agent usage metrics: {e}", exc_info=True)
    
    async def track_cache_operation(self, operation: str, key: str, success: bool, duration: float):
        """Track cache operation metrics."""
        try:
            # Increment cache counters
            self._counters[f"cache_{operation}"] += 1
            
            if success:
                self._counters[f"cache_{operation}_success"] += 1
            else:
                self._counters[f"cache_{operation}_errors"] += 1
            
            # Track operation duration
            self._timers[f"cache_{operation}_duration"].append(duration)
            self._histograms[f"cache_{operation}_duration"].append(duration)
            
            logger.debug(f"Tracked cache operation: {operation}, key: {key}, success: {success}, duration: {duration}s")
            
        except Exception as e:
            logger.error(f"Error tracking cache operation metrics: {e}", exc_info=True)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        try:
            uptime = (datetime.now() - self._start_time).total_seconds()
            
            # Calculate averages
            avg_processing_time = self._calculate_average(self._timers["query_processing_time"])
            avg_error_time = self._calculate_average(self._timers["error_processing_time"])
            
            # Calculate percentiles
            p95_processing_time = self._calculate_percentile(self._timers["query_processing_time"], 95)
            p99_processing_time = self._calculate_percentile(self._timers["query_processing_time"], 99)
            
            return {
                "uptime_seconds": uptime,
                "total_queries": self._counters["total_queries"],
                "total_errors": self._counters["total_errors"],
                "cache_hits": self._counters["cache_hits"],
                "cache_misses": self._counters["cache_misses"],
                "cache_hit_rate": self._metrics.get("cache_hit_rate", 0),
                "error_rate": self._metrics.get("error_rate", 0),
                "avg_processing_time": avg_processing_time,
                "avg_error_time": avg_error_time,
                "p95_processing_time": p95_processing_time,
                "p99_processing_time": p99_processing_time,
                "queries_per_minute": self._calculate_rate("total_queries", uptime),
                "errors_per_minute": self._calculate_rate("total_errors", uptime)
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}", exc_info=True)
            return {}
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """Get agent-specific metrics."""
        try:
            agent_metrics = {}
            
            # Get all agent types from counters
            agent_types = set()
            for key in self._counters.keys():
                if key.startswith("agent_calls_"):
                    agent_type = key.replace("agent_calls_", "")
                    agent_types.add(agent_type)
            
            for agent_type in agent_types:
                total_calls = self._counters.get(f"agent_calls_{agent_type}", 0)
                successful_calls = self._counters.get(f"agent_success_{agent_type}", 0)
                error_calls = self._counters.get(f"agent_errors_{agent_type}", 0)
                
                avg_processing_time = self._calculate_average(self._timers.get(f"agent_processing_time_{agent_type}", []))
                
                agent_metrics[agent_type] = {
                    "total_calls": total_calls,
                    "successful_calls": successful_calls,
                    "error_calls": error_calls,
                    "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
                    "avg_processing_time": avg_processing_time
                }
            
            return agent_metrics
            
        except Exception as e:
            logger.error(f"Error getting agent metrics: {e}", exc_info=True)
            return {}
    
    def get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache-specific metrics."""
        try:
            cache_metrics = {}
            
            # Get all cache operations from counters
            operations = set()
            for key in self._counters.keys():
                if key.startswith("cache_") and not key.endswith("_success") and not key.endswith("_errors"):
                    operation = key.replace("cache_", "")
                    operations.add(operation)
            
            for operation in operations:
                total_ops = self._counters.get(f"cache_{operation}", 0)
                successful_ops = self._counters.get(f"cache_{operation}_success", 0)
                error_ops = self._counters.get(f"cache_{operation}_errors", 0)
                
                avg_duration = self._calculate_average(self._timers.get(f"cache_{operation}_duration", []))
                
                cache_metrics[operation] = {
                    "total_operations": total_ops,
                    "successful_operations": successful_ops,
                    "error_operations": error_ops,
                    "success_rate": successful_ops / total_ops if total_ops > 0 else 0,
                    "avg_duration": avg_duration
                }
            
            return cache_metrics
            
        except Exception as e:
            logger.error(f"Error getting cache metrics: {e}", exc_info=True)
            return {}
    
    def _calculate_average(self, values: List[float]) -> float:
        """Calculate average of values."""
        if not values:
            return 0.0
        return sum(values) / len(values)
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _calculate_rate(self, counter_key: str, time_period: float) -> float:
        """Calculate rate per minute."""
        count = self._counters.get(counter_key, 0)
        minutes = time_period / 60.0
        return count / minutes if minutes > 0 else 0
    
    def reset_metrics(self):
        """Reset all metrics."""
        try:
            self._metrics.clear()
            self._counters.clear()
            self._timers.clear()
            self._histograms.clear()
            self._start_time = datetime.now()
            
            logger.info("Metrics reset")
            
        except Exception as e:
            logger.error(f"Error resetting metrics: {e}", exc_info=True)
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics for external monitoring."""
        try:
            return {
                "summary": self.get_metrics_summary(),
                "agents": self.get_agent_metrics(),
                "cache": self.get_cache_metrics(),
                "raw_counters": dict(self._counters),
                "raw_timers": {k: self._calculate_average(v) for k, v in self._timers.items()},
                "exported_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}", exc_info=True)
            return {} 