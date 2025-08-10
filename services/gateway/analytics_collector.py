#!/usr/bin/env python3
"""
Analytics Collector for SarvanOM Gateway

Consolidated from services/analytics/ implementations with privacy protection.
Tracks query performance and system metrics for the Universal Knowledge Platform.
"""

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if present
except ImportError:
    pass  # dotenv not installed, continue without it

import time
import hashlib
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json
import os


class AnalyticsCollector:
    """
    Privacy-focused analytics collector for SarvanOM.
    
    Tracks performance metrics while protecting user privacy according to
    the zero-budget, privacy-first approach described in Sarvanom_blueprint.md.
    """
    
    def __init__(self):
        # Performance metrics
        self.request_counter = 0
        self.error_counter = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_response_time = 0.0
        self.request_times = deque(maxlen=1000)  # Rolling window
        
        # Query analytics (anonymized)
        self.query_categories = defaultdict(int)
        self.complexity_distribution = defaultdict(int)
        self.provider_usage = defaultdict(int)
        self.user_activity = defaultdict(int)  # Hashed user IDs
        
        # System metrics
        self.agent_performance = defaultdict(list)
        self.error_types = defaultdict(int)
        
        # Privacy settings
        self.anonymize_queries = os.getenv("ANONYMIZE_QUERIES", "true").lower() == "true"
        self.retention_hours = int(os.getenv("ANALYTICS_RETENTION_HOURS", "24"))
        
        # Data cleanup
        self.last_cleanup = time.time()
        self.cleanup_interval = 3600  # 1 hour
    
    def track_request(self, 
                     query: str, 
                     user_id: Optional[str] = None, 
                     complexity: str = "medium",
                     provider: str = "unknown",
                     response_time_ms: int = 0,
                     success: bool = True,
                     error_type: Optional[str] = None):
        """Track a query request with privacy protection."""
        
        self.request_counter += 1
        
        if not success:
            self.error_counter += 1
            if error_type:
                self.error_types[error_type] += 1
        
        # Track response times
        self.total_response_time += response_time_ms
        self.request_times.append(response_time_ms)
        
        # Track query complexity (anonymized)
        self.complexity_distribution[complexity] += 1
        
        # Track provider usage
        self.provider_usage[provider] += 1
        
        # Track user activity (hashed for privacy)
        if user_id:
            hashed_user = self._hash_user_id(user_id)
            self.user_activity[hashed_user] += 1
        
        # Track query category (anonymized)
        category = self._categorize_query(query)
        self.query_categories[category] += 1
        
        # Periodic cleanup
        if time.time() - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_data()
    
    def track_cache_event(self, hit: bool):
        """Track cache hit/miss events."""
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
    
    def track_agent_performance(self, agent_type: str, execution_time_ms: int, success: bool):
        """Track individual agent performance."""
        self.agent_performance[agent_type].append({
            "execution_time_ms": execution_time_ms,
            "success": success,
            "timestamp": time.time()
        })
        
        # Keep only recent data
        cutoff_time = time.time() - (self.retention_hours * 3600)
        self.agent_performance[agent_type] = [
            entry for entry in self.agent_performance[agent_type]
            if entry["timestamp"] > cutoff_time
        ]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics.
        
        Enhanced with patterns from shared/core/unified_metrics.py and 
        shared/core/metrics_collector.py for production monitoring.
        """
        avg_response_time = (
            self.total_response_time / self.request_counter
            if self.request_counter > 0 else 0
        )
        
        cache_hit_rate = (
            self.cache_hits / (self.cache_hits + self.cache_misses)
            if (self.cache_hits + self.cache_misses) > 0 else 0
        )
        
        error_rate = (
            self.error_counter / self.request_counter
            if self.request_counter > 0 else 0
        )
        
        # Calculate percentiles from recent requests (enhanced algorithm)
        recent_times = list(self.request_times)
        recent_times.sort()
        
        percentiles = {}
        if recent_times:
            n = len(recent_times)
            percentiles = {
                "p50": recent_times[n // 2] if n > 0 else 0,
                "p90": recent_times[int(n * 0.90)] if n > 0 else 0,
                "p95": recent_times[int(n * 0.95)] if n > 0 else 0,
                "p99": recent_times[int(n * 0.99)] if n > 0 else 0,
                "min": min(recent_times) if recent_times else 0,
                "max": max(recent_times) if recent_times else 0
            }
        
        # Calculate request rate (requests per minute)
        current_time = time.time()
        recent_requests = len([
            rt for rt in recent_times 
            if current_time - rt < 300  # Last 5 minutes
        ])
        request_rate = recent_requests / 5.0  # Per minute
        
        # Top error types analysis
        top_errors = sorted(
            self.error_types.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # Quality score calculation (enhanced from metrics_collector.py)
        quality_score = 1.0
        if error_rate > 0.05:  # More than 5% errors
            quality_score *= 0.8
        if cache_hit_rate < 0.3:  # Less than 30% cache hits
            quality_score *= 0.9
        if avg_response_time > 3000:  # More than 3 seconds average
            quality_score *= 0.7
        
        return {
            "total_requests": self.request_counter,
            "total_errors": self.error_counter,
            "error_rate": round(error_rate, 4),
            "avg_response_time_ms": round(avg_response_time, 2),
            "request_rate_per_minute": round(request_rate, 2),
            "quality_score": round(quality_score, 3),
            "cache_performance": {
                "hit_rate": round(cache_hit_rate, 4),
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "total": self.cache_hits + self.cache_misses
            },
            "response_time_percentiles": percentiles,
            "active_users": len(self.user_activity),
            "complexity_distribution": dict(self.complexity_distribution),
            "provider_usage": dict(self.provider_usage),
            "query_categories": dict(self.query_categories),
            "top_error_types": top_errors,
            "data_retention_hours": self.retention_hours,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """Get agent-specific performance metrics."""
        agent_stats = {}
        
        for agent_type, performances in self.agent_performance.items():
            if not performances:
                continue
            
            execution_times = [p["execution_time_ms"] for p in performances]
            successes = [p["success"] for p in performances]
            
            agent_stats[agent_type] = {
                "total_invocations": len(performances),
                "success_rate": sum(successes) / len(successes),
                "avg_execution_time_ms": sum(execution_times) / len(execution_times),
                "min_execution_time_ms": min(execution_times),
                "max_execution_time_ms": max(execution_times)
            }
        
        return agent_stats
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        recent_requests = len([
            rt for rt in self.request_times 
            if time.time() - rt < 300  # Last 5 minutes
        ])
        
        health_score = 1.0
        health_factors = []
        
        # Factor in error rate
        error_rate = self.error_counter / max(self.request_counter, 1)
        if error_rate > 0.1:  # More than 10% errors
            health_score *= 0.7
            health_factors.append("high_error_rate")
        
        # Factor in response times
        if self.request_times:
            avg_recent_time = sum(list(self.request_times)[-10:]) / min(10, len(self.request_times))
            if avg_recent_time > 5000:  # More than 5 seconds
                health_score *= 0.8
                health_factors.append("slow_responses")
        
        # Factor in cache performance
        cache_hit_rate = self.cache_hits / max(self.cache_hits + self.cache_misses, 1)
        if cache_hit_rate < 0.3:  # Less than 30% cache hits
            health_score *= 0.9
            health_factors.append("low_cache_efficiency")
        
        return {
            "health_score": health_score,
            "status": "healthy" if health_score > 0.8 else ("degraded" if health_score > 0.5 else "critical"),
            "recent_request_rate": recent_requests,
            "health_factors": health_factors,
            "uptime_requests": self.request_counter,
            "timestamp": datetime.now().isoformat()
        }
    
    def _hash_user_id(self, user_id: str) -> str:
        """Hash user ID for privacy protection."""
        if not self.anonymize_queries:
            return user_id
        
        return hashlib.sha256(user_id.encode()).hexdigest()[:8]
    
    def _categorize_query(self, query: str) -> str:
        """Categorize query type without storing content."""
        if not query:
            return "empty"
        
        query_lower = query.lower()
        
        # Simple categorization based on keywords
        if any(word in query_lower for word in ["what", "who", "when", "where", "define"]):
            return "factual"
        elif any(word in query_lower for word in ["compare", "analyze", "evaluate"]):
            return "analytical"
        elif any(word in query_lower for word in ["how", "why", "explain"]):
            return "explanatory"
        elif any(word in query_lower for word in ["research", "study", "findings"]):
            return "research"
        else:
            return "general"
    
    def _cleanup_old_data(self):
        """Clean up old analytics data."""
        self.last_cleanup = time.time()
        
        # Reset counters if they get too large
        if self.request_counter > 1000000:
            self.request_counter = 0
            self.error_counter = 0
            self.total_response_time = 0.0
        
        # Clear old user activity data
        if len(self.user_activity) > 10000:
            # Keep only top active users
            sorted_users = sorted(self.user_activity.items(), key=lambda x: x[1], reverse=True)
            self.user_activity = dict(sorted_users[:5000])
        
        print(f"Analytics cleanup completed at {datetime.now()}")

    def test_microservice_connectivity(self) -> Dict[str, Any]:
        """
        Test connectivity to all microservices.
        Extracted from debug_connection.py and debug_sync.py patterns.
        """
        import requests
        
        services = {
            "retrieval": "http://localhost:8002/health",
            "synthesis": "http://localhost:8003/health", 
            "fact_check": "http://localhost:8004/health",
            "auth": "http://localhost:8005/health",
            "multimodal": "http://localhost:8006/health"
        }
        
        connectivity_results = {}
        
        for service_name, health_url in services.items():
            try:
                start_time = time.time()
                response = requests.get(health_url, timeout=5)
                end_time = time.time()
                
                connectivity_results[service_name] = {
                    "status": "online" if response.status_code == 200 else "degraded",
                    "response_time_ms": round((end_time - start_time) * 1000, 2),
                    "status_code": response.status_code
                }
            except Exception as e:
                connectivity_results[service_name] = {
                    "status": "offline",
                    "error": str(e),
                    "response_time_ms": None
                }
        
        # Calculate overall connectivity health
        online_services = sum(1 for result in connectivity_results.values() if result["status"] == "online")
        total_services = len(services)
        connectivity_score = online_services / total_services
        
        return {
            "connectivity_score": connectivity_score,
            "services": connectivity_results,
            "online_services": online_services,
            "total_services": total_services,
            "timestamp": time.time()
        }


# Global analytics instance
analytics = AnalyticsCollector()
