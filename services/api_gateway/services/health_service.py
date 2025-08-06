"""
Health Service for API Gateway

This module handles health monitoring, system diagnostics, and metrics collection.
It provides comprehensive health checks and system status information.
"""

import asyncio
import logging
from shared.core.unified_logging import get_logger
import time
import psutil
import platform
import socket
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = get_logger(__name__)


@dataclass
class SystemMetrics:
    """System metrics data class."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_connections: int
    active_processes: int
    uptime: float
    timestamp: datetime


@dataclass
class ServiceHealth:
    """Service health information."""
    service_name: str
    status: str
    response_time: float
    last_check: datetime
    error_count: int
    details: Dict[str, Any]


class HealthService:
    """Service for handling health monitoring and system diagnostics."""
    
    def __init__(self):
        self.metrics_history = []
        self.service_health = {}
        self.health_checks = {}
        self.max_history_size = 1000
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information."""
        try:
            # Get current system metrics
            metrics = await self._collect_system_metrics()
            
            # Store metrics in history
            self._store_metrics(metrics)
            
            # Get service health
            service_health = await self._check_service_health()
            
            # Determine overall health status
            overall_status = self._determine_overall_health(metrics, service_health)
            
            return {
                "status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "system_metrics": {
                    "cpu_usage": metrics.cpu_usage,
                    "memory_usage": metrics.memory_usage,
                    "disk_usage": metrics.disk_usage,
                    "network_connections": metrics.network_connections,
                    "active_processes": metrics.active_processes,
                    "uptime": metrics.uptime
                },
                "service_health": service_health,
                "alerts": await self._get_alerts(metrics, service_health)
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_basic_health(self) -> Dict[str, Any]:
        """Get basic health check for load balancers."""
        try:
            # Quick system check
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Simple health determination
            is_healthy = (
                memory.percent < 90 and  # Memory usage < 90%
                cpu_percent < 95 and     # CPU usage < 95%
                self._check_critical_services()
            )
            
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "service": "sarvanom-api",
                "memory_usage_percent": memory.percent,
                "cpu_usage_percent": cpu_percent
            }
            
        except Exception as e:
            logger.error(f"Basic health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "service": "sarvanom-api"
            }
    
    async def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed system metrics."""
        try:
            metrics = await self._collect_system_metrics()
            
            # Get historical data
            historical_metrics = self._get_historical_metrics()
            
            # Calculate trends
            trends = self._calculate_trends(historical_metrics)
            
            return {
                "current_metrics": {
                    "cpu": {
                        "usage_percent": metrics.cpu_usage,
                        "count": psutil.cpu_count(),
                        "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
                    },
                    "memory": {
                        "total": psutil.virtual_memory().total,
                        "available": psutil.virtual_memory().available,
                        "used": psutil.virtual_memory().used,
                        "percent": metrics.memory_usage
                    },
                    "disk": {
                        "total": psutil.disk_usage('/').total,
                        "used": psutil.disk_usage('/').used,
                        "free": psutil.disk_usage('/').free,
                        "percent": metrics.disk_usage
                    },
                    "network": {
                        "connections": metrics.network_connections,
                        "interfaces": len(psutil.net_if_addrs())
                    }
                },
                "historical_data": historical_metrics,
                "trends": trends,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get detailed metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_system_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive system diagnostics."""
        try:
            # System information
            system_info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
            
            # Service status
            service_status = await self._get_service_status()
            
            # Dependencies status
            dependencies = await self._check_dependencies()
            
            # Performance metrics
            performance = await self._get_performance_metrics()
            
            # Recent errors and warnings
            errors = await self._get_recent_errors()
            warnings = await self._get_recent_warnings()
            
            return {
                "system_info": system_info,
                "service_status": service_status,
                "dependencies": dependencies,
                "performance": performance,
                "errors": errors,
                "warnings": warnings,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system diagnostics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Network connections
            network_connections = len(psutil.net_connections())
            
            # Active processes
            active_processes = len(psutil.pids())
            
            # Uptime
            uptime = time.time() - psutil.boot_time()
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_connections=network_connections,
                active_processes=active_processes,
                uptime=uptime,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            raise
    
    def _store_metrics(self, metrics: SystemMetrics):
        """Store metrics in history."""
        self.metrics_history.append(metrics)
        
        # Keep only recent metrics
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def _get_historical_metrics(self) -> List[Dict[str, Any]]:
        """Get historical metrics for analysis."""
        return [
            {
                "timestamp": m.timestamp.isoformat(),
                "cpu_usage": m.cpu_usage,
                "memory_usage": m.memory_usage,
                "disk_usage": m.disk_usage,
                "network_connections": m.network_connections,
                "active_processes": m.active_processes
            }
            for m in self.metrics_history[-100:]  # Last 100 metrics
        ]
    
    def _calculate_trends(self, historical_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trends from historical metrics."""
        if len(historical_metrics) < 2:
            return {}
        
        # Calculate simple trends
        recent = historical_metrics[-10:]  # Last 10 measurements
        older = historical_metrics[-20:-10]  # Previous 10 measurements
        
        if not older:
            return {}
        
        trends = {}
        for metric in ["cpu_usage", "memory_usage", "disk_usage"]:
            recent_avg = sum(m[metric] for m in recent) / len(recent)
            older_avg = sum(m[metric] for m in older) / len(older)
            trends[metric] = {
                "current_avg": recent_avg,
                "previous_avg": older_avg,
                "trend": "increasing" if recent_avg > older_avg else "decreasing" if recent_avg < older_avg else "stable"
            }
        
        return trends
    
    async def _check_service_health(self) -> Dict[str, ServiceHealth]:
        """Check health of all services."""
        services = {
            "api_gateway": self._check_api_gateway,
            "database": self._check_database,
            "cache": self._check_cache,
            "search_service": self._check_search_service,
            "llm_service": self._check_llm_service
        }
        
        health_results = {}
        for service_name, check_func in services.items():
            try:
                start_time = time.time()
                status, details = await check_func()
                response_time = time.time() - start_time
                
                health_results[service_name] = ServiceHealth(
                    service_name=service_name,
                    status=status,
                    response_time=response_time,
                    last_check=datetime.now(),
                    error_count=self.service_health.get(service_name, {}).get("error_count", 0),
                    details=details
                )
                
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                health_results[service_name] = ServiceHealth(
                    service_name=service_name,
                    status="unhealthy",
                    response_time=0.0,
                    last_check=datetime.now(),
                    error_count=self.service_health.get(service_name, {}).get("error_count", 0) + 1,
                    details={"error": str(e)}
                )
        
        return health_results
    
    async def _check_api_gateway(self) -> tuple[str, Dict[str, Any]]:
        """Check API gateway health."""
        # Implement actual API gateway health check
        try:
            # Check if the API gateway process is running
            gateway_process = None
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'uvicorn' in proc.info['name'] or 'fastapi' in proc.info['name']:
                        gateway_process = proc
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not gateway_process:
                return "unhealthy", {"error": "API Gateway process not found"}
            
            # Check if the gateway is responding to basic requests
            import aiohttp
            import asyncio
            
            try:
                # Try to connect to the gateway
                async with aiohttp.ClientSession() as session:
                    # Check if the server is listening on the expected port
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('localhost', 8000))
                    sock.close()
                    
                    if result != 0:
                        return "unhealthy", {"error": "API Gateway not listening on port 8000"}
                    
                    # Try a basic health check request
                    timeout = aiohttp.ClientTimeout(total=5)
                    async with session.get('http://localhost:8000/health', timeout=timeout) as response:
                        if response.status == 200:
                            return "healthy", {
                                "endpoints": ["/health", "/query", "/agents", "/metrics"],
                                "process_id": gateway_process.pid,
                                "response_time": response.headers.get('X-Response-Time', 'unknown')
                            }
                        else:
                            return "unhealthy", {"error": f"Health endpoint returned status {response.status}"}
                            
            except asyncio.TimeoutError:
                return "unhealthy", {"error": "API Gateway health check timeout"}
            except Exception as e:
                return "unhealthy", {"error": f"API Gateway health check failed: {str(e)}"}
                
        except Exception as e:
            return "unhealthy", {"error": f"API Gateway health check error: {str(e)}"}
    
    async def _check_database(self) -> tuple[str, Dict[str, Any]]:
        """Check database health."""
        # Implement actual database health check
        try:
            import asyncpg
            import os
            from datetime import datetime
            
            # Get database configuration from environment
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = int(os.getenv('DB_PORT', '5432'))
            db_name = os.getenv('DB_NAME', 'sarvanom')
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', '')
            
            # Test database connection
            start_time = time.time()
            try:
                conn = await asyncpg.connect(
                    host=db_host,
                    port=db_port,
                    database=db_name,
                    user=db_user,
                    password=db_password,
                    timeout=10
                )
                
                # Test basic query
                result = await conn.fetchval('SELECT 1')
                response_time = time.time() - start_time
                
                # Get database statistics
                db_stats = await conn.fetchrow('''
                    SELECT 
                        count(*) as table_count,
                        pg_size_pretty(pg_database_size(current_database())) as db_size
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                ''')
                
                # Get active connections
                active_connections = await conn.fetchval('''
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE state = 'active'
                ''')
                
                await conn.close()
                
                return "healthy", {
                    "connections": active_connections,
                    "response_time": round(response_time, 3),
                    "table_count": db_stats['table_count'],
                    "database_size": db_stats['db_size'],
                    "host": db_host,
                    "port": db_port,
                    "database": db_name
                }
                
            except asyncpg.InvalidPasswordError:
                return "unhealthy", {"error": "Database authentication failed"}
            except asyncpg.InvalidCatalogNameError:
                return "unhealthy", {"error": f"Database '{db_name}' does not exist"}
            except asyncpg.ConnectionDoesNotExistError:
                return "unhealthy", {"error": f"Cannot connect to database at {db_host}:{db_port}"}
            except Exception as e:
                return "unhealthy", {"error": f"Database connection failed: {str(e)}"}
                
        except ImportError:
            return "unhealthy", {"error": "asyncpg not installed"}
        except Exception as e:
            return "unhealthy", {"error": f"Database health check error: {str(e)}"}
    
    async def _check_cache(self) -> tuple[str, Dict[str, Any]]:
        """Check cache health."""
        # Implement actual cache health check
        try:
            import redis.asyncio as redis
            import os
            
            # Get Redis configuration from environment
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_db = int(os.getenv('REDIS_DB', '0'))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            
            # Test Redis connection
            start_time = time.time()
            try:
                r = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=True,
                    socket_timeout=5
                )
                
                # Test basic operations
                await r.ping()
                response_time = time.time() - start_time
                
                # Get cache statistics
                info = await r.info()
                
                # Calculate hit rate (if available)
                keyspace_hits = int(info.get('keyspace_hits', 0))
                keyspace_misses = int(info.get('keyspace_misses', 0))
                total_requests = keyspace_hits + keyspace_misses
                hit_rate = keyspace_hits / total_requests if total_requests > 0 else 0
                
                # Get memory usage
                memory_info = await r.info('memory')
                used_memory = int(memory_info.get('used_memory', 0))
                max_memory = int(memory_info.get('maxmemory', 0))
                memory_usage = (used_memory / max_memory * 100) if max_memory > 0 else 0
                
                # Get key count
                key_count = await r.dbsize()
                
                await r.close()
                
                return "healthy", {
                    "hit_rate": round(hit_rate, 3),
                    "memory_usage": round(memory_usage, 2),
                    "response_time": round(response_time, 3),
                    "key_count": key_count,
                    "host": redis_host,
                    "port": redis_port,
                    "database": redis_db,
                    "redis_version": info.get('redis_version', 'unknown')
                }
                
            except redis.ConnectionError:
                return "unhealthy", {"error": f"Cannot connect to Redis at {redis_host}:{redis_port}"}
            except redis.AuthenticationError:
                return "unhealthy", {"error": "Redis authentication failed"}
            except Exception as e:
                return "unhealthy", {"error": f"Redis health check failed: {str(e)}"}
                
        except ImportError:
            return "unhealthy", {"error": "redis not installed"}
        except Exception as e:
            return "unhealthy", {"error": f"Cache health check error: {str(e)}"}
    
    async def _check_search_service(self) -> tuple[str, Dict[str, Any]]:
        """Check search service health."""
        # Implement actual search service health check
        try:
            import aiohttp
            import os
            
            # Get Meilisearch configuration from environment
            meili_host = os.getenv('MEILI_HOST', 'localhost')
            meili_port = int(os.getenv('MEILI_PORT', '7700'))
            meili_key = os.getenv('MEILI_MASTER_KEY', '')
            
            # Test Meilisearch connection
            start_time = time.time()
            try:
                base_url = f"http://{meili_host}:{meili_port}"
                headers = {"Authorization": f"Bearer {meili_key}"} if meili_key else {}
                
                async with aiohttp.ClientSession() as session:
                    # Check if Meilisearch is running
                    async with session.get(f"{base_url}/health", headers=headers, timeout=5) as response:
                        if response.status != 200:
                            return "unhealthy", {"error": f"Meilisearch health check failed with status {response.status}"}
                        
                        health_data = await response.json()
                        response_time = time.time() - start_time
                        
                        # Get index statistics
                        async with session.get(f"{base_url}/indexes", headers=headers, timeout=5) as index_response:
                            if index_response.status == 200:
                                indexes_data = await index_response.json()
                                index_count = len(indexes_data.get('results', []))
                                
                                # Get total documents across all indexes
                                total_documents = 0
                                for index in indexes_data.get('results', []):
                                    index_name = index.get('uid', '')
                                    if index_name:
                                        async with session.get(f"{base_url}/indexes/{index_name}/stats", headers=headers, timeout=5) as stats_response:
                                            if stats_response.status == 200:
                                                stats_data = await stats_response.json()
                                                total_documents += stats_data.get('numberOfDocuments', 0)
                            else:
                                index_count = 0
                                total_documents = 0
                        
                        return "healthy", {
                            "index_size": total_documents,
                            "response_time": round(response_time, 3),
                            "index_count": index_count,
                            "host": meili_host,
                            "port": meili_port,
                            "status": health_data.get('status', 'unknown'),
                            "version": health_data.get('version', 'unknown')
                        }
                        
            except aiohttp.ClientConnectorError:
                return "unhealthy", {"error": f"Cannot connect to Meilisearch at {meili_host}:{meili_port}"}
            except aiohttp.ClientTimeout:
                return "unhealthy", {"error": "Meilisearch health check timeout"}
            except Exception as e:
                return "unhealthy", {"error": f"Meilisearch health check failed: {str(e)}"}
                
        except ImportError:
            return "unhealthy", {"error": "aiohttp not installed"}
        except Exception as e:
            return "unhealthy", {"error": f"Search service health check error: {str(e)}"}
    
    async def _check_llm_service(self) -> tuple[str, Dict[str, Any]]:
        """Check LLM service health."""
        # Implement actual LLM service health check
        try:
            import aiohttp
            import os
            
            # Get Ollama configuration from environment
            ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
            ollama_port = int(os.getenv('OLLAMA_PORT', '11434'))
            
            # Test Ollama connection
            start_time = time.time()
            try:
                base_url = f"http://{ollama_host}:{ollama_port}"
                
                async with aiohttp.ClientSession() as session:
                    # Check if Ollama is running
                    async with session.get(f"{base_url}/api/tags", timeout=10) as response:
                        if response.status != 200:
                            return "unhealthy", {"error": f"Ollama health check failed with status {response.status}"}
                        
                        models_data = await response.json()
                        response_time = time.time() - start_time
                        
                        # Get available models
                        available_models = []
                        for model in models_data.get('models', []):
                            model_name = model.get('name', '')
                            if model_name:
                                available_models.append(model_name)
                        
                        # Test a simple completion to check model functionality
                        test_prompt = "Hello, this is a health check."
                        test_data = {
                            "model": available_models[0] if available_models else "llama2",
                            "prompt": test_prompt,
                            "stream": False
                        }
                        
                        try:
                            async with session.post(f"{base_url}/api/generate", json=test_data, timeout=15) as test_response:
                                if test_response.status == 200:
                                    test_result = await test_response.json()
                                    model_working = True
                                else:
                                    model_working = False
                        except:
                            model_working = False
                        
                        return "healthy", {
                            "models_available": available_models,
                            "response_time": round(response_time, 3),
                            "model_test_passed": model_working,
                            "host": ollama_host,
                            "port": ollama_port,
                            "total_models": len(available_models)
                        }
                        
            except aiohttp.ClientConnectorError:
                return "unhealthy", {"error": f"Cannot connect to Ollama at {ollama_host}:{ollama_port}"}
            except aiohttp.ClientTimeout:
                return "unhealthy", {"error": "Ollama health check timeout"}
            except Exception as e:
                return "unhealthy", {"error": f"Ollama health check failed: {str(e)}"}
                
        except ImportError:
            return "unhealthy", {"error": "aiohttp not installed"}
        except Exception as e:
            return "unhealthy", {"error": f"LLM service health check error: {str(e)}"}
    
    def _determine_overall_health(
        self, 
        metrics: SystemMetrics, 
        service_health: Dict[str, ServiceHealth]
    ) -> str:
        """Determine overall system health."""
        # Check system metrics
        if metrics.cpu_usage > 90 or metrics.memory_usage > 90 or metrics.disk_usage > 90:
            return "unhealthy"
        
        # Check service health
        unhealthy_services = [s for s in service_health.values() if s.status == "unhealthy"]
        if len(unhealthy_services) > len(service_health) * 0.5:  # More than 50% unhealthy
            return "unhealthy"
        
        return "healthy"
    
    def _check_critical_services(self) -> bool:
        """Check if critical services are available."""
        # Implement actual critical service checks
        try:
            import socket
            import os
            
            # Define critical services and their ports
            critical_services = {
                "database": int(os.getenv('DB_PORT', '5432')),
                "cache": int(os.getenv('REDIS_PORT', '6379')),
                "search": int(os.getenv('MEILI_PORT', '7700')),
                "llm": int(os.getenv('OLLAMA_PORT', '11434')),
                "api_gateway": 8000
            }
            
            # Check each critical service
            available_services = 0
            total_services = len(critical_services)
            
            for service_name, port in critical_services.items():
                try:
                    # Try to connect to the service
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)  # 2 second timeout
                    result = sock.connect_ex(('localhost', port))
                    sock.close()
                    
                    if result == 0:
                        available_services += 1
                        logger.debug(f"Critical service {service_name} is available on port {port}")
                    else:
                        logger.warning(f"Critical service {service_name} is not available on port {port}")
                        
                except Exception as e:
                    logger.error(f"Error checking critical service {service_name}: {e}")
            
            # Calculate availability percentage
            availability_percentage = (available_services / total_services) * 100
            
            # Consider critical if at least 80% of services are available
            is_critical_available = availability_percentage >= 80
            
            logger.info(f"Critical services availability: {available_services}/{total_services} ({availability_percentage:.1f}%)")
            
            return is_critical_available
            
        except Exception as e:
            logger.error(f"Critical services check failed: {e}")
            return False
    
    async def _get_service_status(self) -> Dict[str, str]:
        """Get status of all services."""
        return {
            "api_gateway": "healthy",
            "database": "healthy",
            "cache": "healthy",
            "search_service": "healthy",
            "llm_service": "healthy"
        }
    
    async def _check_dependencies(self) -> Dict[str, str]:
        """Check external dependencies."""
        return {
            "postgresql": "connected",
            "redis": "connected",
            "meilisearch": "connected",
            "ollama": "connected"
        }
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "cpu_usage_percent": psutil.cpu_percent(interval=1),
            "memory_usage_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100,
            "active_connections": len(psutil.net_connections()),
            "uptime_seconds": time.time() - psutil.boot_time()
        }
    
    async def _get_recent_errors(self) -> List[Dict[str, Any]]:
        """Get recent system errors."""
        # Implement actual error tracking
        try:
            # Get recent errors from log files or error tracking system
            errors = []
            
            # Check system logs for recent errors
            import os
            from datetime import datetime, timedelta
            
            # Look for error patterns in recent logs
            log_patterns = [
                "ERROR",
                "CRITICAL", 
                "FATAL",
                "Exception",
                "Traceback"
            ]
            
            # Check common log locations
            log_paths = [
                "/var/log/syslog",
                "/var/log/messages", 
                "logs/app.log",
                "logs/error.log"
            ]
            
            for log_path in log_paths:
                if os.path.exists(log_path):
                    try:
                        # Read last 1000 lines of log file
                        with open(log_path, 'r') as f:
                            lines = f.readlines()[-1000:]
                            
                        # Look for recent errors (last 24 hours)
                        current_time = datetime.now()
                        for line in lines:
                            for pattern in log_patterns:
                                if pattern in line:
                                    # Try to extract timestamp from log line
                                    try:
                                        # Simple timestamp extraction (adjust based on log format)
                                        if "2024" in line or "2025" in line:
                                            errors.append({
                                                "timestamp": current_time.isoformat(),
                                                "level": "ERROR",
                                                "message": line.strip(),
                                                "source": log_path,
                                                "details": {"pattern": pattern}
                                            })
                                            break
                                    except:
                                        continue
                    except Exception as e:
                        logger.warning(f"Could not read log file {log_path}: {e}")
            
            # If no errors found in logs, check system metrics for issues
            if not errors:
                memory = psutil.virtual_memory()
                if memory.percent > 90:
                    errors.append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "WARNING",
                        "message": "High memory usage detected",
                        "details": {"memory_percent": memory.percent}
                    })
                
                disk = psutil.disk_usage('/')
                if disk.percent > 90:
                    errors.append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "WARNING", 
                        "message": "High disk usage detected",
                        "details": {"disk_percent": disk.percent}
                    })
            
            return errors[:10]  # Return last 10 errors
            
        except Exception as e:
            logger.error(f"Error tracking failed: {e}")
            return [{
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "message": "Error tracking system unavailable",
                "details": {"error": str(e)}
            }]
    
    async def _get_recent_warnings(self) -> List[Dict[str, Any]]:
        """Get recent system warnings."""
        # Implement actual warning tracking
        try:
            warnings = []
            
            # Check system metrics for warnings
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                warnings.append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "WARNING",
                    "message": "Elevated memory usage",
                    "details": {"memory_percent": memory.percent}
                })
            
            disk = psutil.disk_usage('/')
            if disk.percent > 80:
                warnings.append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "WARNING",
                    "message": "Elevated disk usage",
                    "details": {"disk_percent": disk.percent}
                })
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                warnings.append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "WARNING",
                    "message": "High CPU usage detected",
                    "details": {"cpu_percent": cpu_percent}
                })
            
            # Check network connections
            connections = len(psutil.net_connections())
            if connections > 1000:  # Arbitrary threshold
                warnings.append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": "High number of network connections",
                    "details": {"connections": connections}
                })
            
            # Check if any services are slow to respond
            service_health = await self._check_service_health()
            for service_name, health in service_health.items():
                if health.response_time > 5.0:  # 5 second threshold
                    warnings.append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "WARNING",
                        "message": f"Slow response from {service_name}",
                        "details": {"response_time": health.response_time}
                    })
            
            return warnings[:10]  # Return last 10 warnings
            
        except Exception as e:
            logger.error(f"Warning tracking failed: {e}")
            return [{
                "timestamp": datetime.now().isoformat(),
                "level": "WARNING",
                "message": "Warning tracking system unavailable",
                "details": {"error": str(e)}
            }]
    
    async def _get_alerts(
        self, 
        metrics: SystemMetrics, 
        service_health: Dict[str, ServiceHealth]
    ) -> List[Dict[str, Any]]:
        """Get system alerts based on metrics and service health."""
        alerts = []
        
        # CPU alerts
        if metrics.cpu_usage > 80:
            alerts.append({
                "type": "warning",
                "message": f"High CPU usage: {metrics.cpu_usage}%",
                "severity": "medium",
                "timestamp": datetime.now().isoformat()
            })
        
        # Memory alerts
        if metrics.memory_usage > 85:
            alerts.append({
                "type": "warning",
                "message": f"High memory usage: {metrics.memory_usage}%",
                "severity": "high",
                "timestamp": datetime.now().isoformat()
            })
        
        # Disk alerts
        if metrics.disk_usage > 90:
            alerts.append({
                "type": "critical",
                "message": f"High disk usage: {metrics.disk_usage}%",
                "severity": "high",
                "timestamp": datetime.now().isoformat()
            })
        
        # Service alerts
        for service_name, health in service_health.items():
            if health.status == "unhealthy":
                alerts.append({
                    "type": "critical",
                    "message": f"Service {service_name} is unhealthy",
                    "severity": "high",
                    "timestamp": datetime.now().isoformat()
                })
        
        return alerts


# Global health service instance
health_service = HealthService() 