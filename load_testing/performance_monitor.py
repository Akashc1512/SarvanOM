"""
Performance Monitoring and Benchmarking System

This module provides real-time performance monitoring, SLA tracking,
and automated benchmarking for the SarvanOM platform.
"""

import asyncio
import aiohttp
import time
import json
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import psutil
import os

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a service"""
    service_name: str
    endpoint: str
    timestamp: datetime
    response_time_ms: float
    status_code: int
    success: bool
    cpu_usage_percent: float
    memory_usage_mb: float
    active_connections: int

@dataclass
class SLABenchmark:
    """SLA benchmark definition"""
    service_name: str
    endpoint: str
    max_response_time_ms: float
    min_success_rate_percent: float
    min_requests_per_second: float
    max_cpu_usage_percent: float
    max_memory_usage_mb: float

@dataclass
class SLAReport:
    """SLA compliance report"""
    service_name: str
    endpoint: str
    benchmark: SLABenchmark
    actual_metrics: Dict[str, float]
    sla_compliant: bool
    violations: List[str]
    timestamp: datetime

class PerformanceMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.sla_benchmarks: Dict[str, SLABenchmark] = {}
        self.sla_reports: List[SLAReport] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Initialize SLA benchmarks
        self._initialize_sla_benchmarks()
    
    def _initialize_sla_benchmarks(self):
        """Initialize SLA benchmarks for all services"""
        benchmarks = [
            # Health endpoints - should be very fast
            SLABenchmark(
                service_name="model_registry",
                endpoint="/health",
                max_response_time_ms=100,
                min_success_rate_percent=99.9,
                min_requests_per_second=100,
                max_cpu_usage_percent=80,
                max_memory_usage_mb=512
            ),
            SLABenchmark(
                service_name="feeds",
                endpoint="/health", 
                max_response_time_ms=100,
                min_success_rate_percent=99.9,
                min_requests_per_second=100,
                max_cpu_usage_percent=80,
                max_memory_usage_mb=512
            ),
            SLABenchmark(
                service_name="retrieval",
                endpoint="/health",
                max_response_time_ms=100,
                min_success_rate_percent=99.9,
                min_requests_per_second=100,
                max_cpu_usage_percent=80,
                max_memory_usage_mb=512
            ),
            SLABenchmark(
                service_name="auth",
                endpoint="/auth/health",
                max_response_time_ms=100,
                min_success_rate_percent=99.9,
                min_requests_per_second=100,
                max_cpu_usage_percent=80,
                max_memory_usage_mb=512
            ),
            
            # Data processing endpoints - can be slower
            SLABenchmark(
                service_name="feeds",
                endpoint="/fetch",
                max_response_time_ms=5000,
                min_success_rate_percent=95,
                min_requests_per_second=10,
                max_cpu_usage_percent=90,
                max_memory_usage_mb=1024
            ),
            
            # Config endpoints - moderate performance
            SLABenchmark(
                service_name="feeds",
                endpoint="/config",
                max_response_time_ms=500,
                min_success_rate_percent=99,
                min_requests_per_second=50,
                max_cpu_usage_percent=85,
                max_memory_usage_mb=768
            ),
            SLABenchmark(
                service_name="retrieval",
                endpoint="/config",
                max_response_time_ms=500,
                min_success_rate_percent=99,
                min_requests_per_second=50,
                max_cpu_usage_percent=85,
                max_memory_usage_mb=768
            ),
            
            # Model registry operations
            SLABenchmark(
                service_name="model_registry",
                endpoint="/models",
                max_response_time_ms=200,
                min_success_rate_percent=99.5,
                min_requests_per_second=50,
                max_cpu_usage_percent=80,
                max_memory_usage_mb=512
            ),
            SLABenchmark(
                service_name="model_registry",
                endpoint="/providers",
                max_response_time_ms=200,
                min_success_rate_percent=99.5,
                min_requests_per_second=50,
                max_cpu_usage_percent=80,
                max_memory_usage_mb=512
            )
        ]
        
        for benchmark in benchmarks:
            key = f"{benchmark.service_name}:{benchmark.endpoint}"
            self.sla_benchmarks[key] = benchmark
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def monitor_service(self, service_url: str, endpoint: str, 
                            duration_seconds: int = 60, interval_seconds: int = 1):
        """Monitor a service endpoint continuously"""
        logger.info(f"Starting monitoring for {service_url}{endpoint}")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        while time.time() < end_time:
            try:
                # Get system metrics
                cpu_usage = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()
                memory_usage_mb = memory_info.used / 1024 / 1024
                
                # Make request and measure response time
                request_start = time.time()
                async with self.session.get(f"{service_url}{endpoint}") as response:
                    response_text = await response.text()
                    request_end = time.time()
                    
                    response_time_ms = (request_end - request_start) * 1000
                    
                    # Create metrics record
                    service_name = service_url.split("//")[1].split(":")[0]
                    metrics = PerformanceMetrics(
                        service_name=service_name,
                        endpoint=endpoint,
                        timestamp=datetime.now(),
                        response_time_ms=response_time_ms,
                        status_code=response.status,
                        success=response.status < 400,
                        cpu_usage_percent=cpu_usage,
                        memory_usage_mb=memory_usage_mb,
                        active_connections=len(psutil.net_connections())
                    )
                    
                    self.metrics_history.append(metrics)
                    
                    # Check SLA compliance
                    await self._check_sla_compliance(metrics)
                    
            except Exception as e:
                logger.error(f"Monitoring error for {service_url}{endpoint}: {e}")
            
            await asyncio.sleep(interval_seconds)
    
    async def _check_sla_compliance(self, metrics: PerformanceMetrics):
        """Check SLA compliance for a metrics record"""
        key = f"{metrics.service_name}:{metrics.endpoint}"
        benchmark = self.sla_benchmarks.get(key)
        
        if not benchmark:
            return
        
        violations = []
        
        # Check response time
        if metrics.response_time_ms > benchmark.max_response_time_ms:
            violations.append(f"Response time {metrics.response_time_ms:.2f}ms exceeds limit {benchmark.max_response_time_ms}ms")
        
        # Check CPU usage
        if metrics.cpu_usage_percent > benchmark.max_cpu_usage_percent:
            violations.append(f"CPU usage {metrics.cpu_usage_percent:.1f}% exceeds limit {benchmark.max_cpu_usage_percent}%")
        
        # Check memory usage
        if metrics.memory_usage_mb > benchmark.max_memory_usage_mb:
            violations.append(f"Memory usage {metrics.memory_usage_mb:.1f}MB exceeds limit {benchmark.max_memory_usage_mb}MB")
        
        # Calculate success rate (simplified - would need more data for accurate calculation)
        recent_metrics = [m for m in self.metrics_history[-100:] 
                         if m.service_name == metrics.service_name and m.endpoint == metrics.endpoint]
        if recent_metrics:
            success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics) * 100
            if success_rate < benchmark.min_success_rate_percent:
                violations.append(f"Success rate {success_rate:.1f}% below limit {benchmark.min_success_rate_percent}%")
        
        # Create SLA report
        sla_compliant = len(violations) == 0
        report = SLAReport(
            service_name=metrics.service_name,
            endpoint=metrics.endpoint,
            benchmark=benchmark,
            actual_metrics={
                "response_time_ms": metrics.response_time_ms,
                "cpu_usage_percent": metrics.cpu_usage_percent,
                "memory_usage_mb": metrics.memory_usage_mb,
                "success": metrics.success
            },
            sla_compliant=sla_compliant,
            violations=violations,
            timestamp=datetime.now()
        )
        
        self.sla_reports.append(report)
        
        if not sla_compliant:
            logger.warning(f"SLA violation for {metrics.service_name}{metrics.endpoint}: {violations}")
    
    def get_performance_summary(self, service_name: str = None, 
                              endpoint: str = None, 
                              time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get performance summary for specified criteria"""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        # Filter metrics
        filtered_metrics = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff_time and
            (service_name is None or m.service_name == service_name) and
            (endpoint is None or m.endpoint == endpoint)
        ]
        
        if not filtered_metrics:
            return {"error": "No metrics found for specified criteria"}
        
        # Calculate statistics
        response_times = [m.response_time_ms for m in filtered_metrics]
        success_count = sum(1 for m in filtered_metrics if m.success)
        total_count = len(filtered_metrics)
        
        summary = {
            "service_name": service_name or "all",
            "endpoint": endpoint or "all",
            "time_window_minutes": time_window_minutes,
            "total_requests": total_count,
            "successful_requests": success_count,
            "success_rate_percent": (success_count / total_count * 100) if total_count > 0 else 0,
            "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "p95_response_time_ms": self._percentile(response_times, 95) if response_times else 0,
            "p99_response_time_ms": self._percentile(response_times, 99) if response_times else 0,
            "avg_cpu_usage_percent": statistics.mean([m.cpu_usage_percent for m in filtered_metrics]),
            "avg_memory_usage_mb": statistics.mean([m.memory_usage_mb for m in filtered_metrics]),
            "sla_violations": len([r for r in self.sla_reports 
                                 if not r.sla_compliant and r.timestamp >= cutoff_time])
        }
        
        return summary
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def generate_sla_report(self) -> str:
        """Generate comprehensive SLA compliance report"""
        if not self.sla_reports:
            return "No SLA reports available."
        
        report = []
        report.append("=" * 80)
        report.append("SARVANOM SLA COMPLIANCE REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Group reports by service:endpoint
        grouped_reports = {}
        for sla_report in self.sla_reports:
            key = f"{sla_report.service_name}:{sla_report.endpoint}"
            if key not in grouped_reports:
                grouped_reports[key] = []
            grouped_reports[key].append(sla_report)
        
        for key, reports in grouped_reports.items():
            service_name, endpoint = key.split(":", 1)
            total_reports = len(reports)
            compliant_reports = sum(1 for r in reports if r.sla_compliant)
            compliance_rate = (compliant_reports / total_reports * 100) if total_reports > 0 else 0
            
            report.append(f"Service: {service_name}")
            report.append(f"Endpoint: {endpoint}")
            report.append(f"Total Checks: {total_reports}")
            report.append(f"Compliant: {compliant_reports} ({compliance_rate:.1f}%)")
            report.append(f"Violations: {total_reports - compliant_reports}")
            
            # Show recent violations
            recent_violations = [r for r in reports[-5:] if not r.sla_compliant]
            if recent_violations:
                report.append("Recent Violations:")
                for violation in recent_violations:
                    report.append(f"  {violation.timestamp.strftime('%H:%M:%S')}: {', '.join(violation.violations)}")
            
            report.append("-" * 40)
        
        return "\n".join(report)
    
    def save_metrics(self, filename: str = None):
        """Save metrics to JSON file"""
        if not filename:
            filename = f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert metrics to serializable format
        serializable_metrics = []
        for metric in self.metrics_history:
            serializable_metrics.append({
                "service_name": metric.service_name,
                "endpoint": metric.endpoint,
                "timestamp": metric.timestamp.isoformat(),
                "response_time_ms": metric.response_time_ms,
                "status_code": metric.status_code,
                "success": metric.success,
                "cpu_usage_percent": metric.cpu_usage_percent,
                "memory_usage_mb": metric.memory_usage_mb,
                "active_connections": metric.active_connections
            })
        
        with open(filename, 'w') as f:
            json.dump(serializable_metrics, f, indent=2)
        
        logger.info(f"Metrics saved to {filename}")

async def run_performance_monitoring():
    """Run comprehensive performance monitoring"""
    async with PerformanceMonitor() as monitor:
        logger.info("Starting performance monitoring...")
        
        # Monitor multiple services simultaneously
        tasks = []
        
        # Health endpoints
        health_endpoints = [
            ("http://localhost:8000", "/health"),
            ("http://localhost:8004", "/health"),
            ("http://localhost:8005", "/health"),
            ("http://localhost:8012", "/auth/health"),
            ("http://localhost:8013", "/health")
        ]
        
        for service_url, endpoint in health_endpoints:
            task = asyncio.create_task(
                monitor.monitor_service(service_url, endpoint, duration_seconds=300, interval_seconds=2)
            )
            tasks.append(task)
        
        # Data processing endpoints
        data_endpoints = [
            ("http://localhost:8005", "/fetch"),
            ("http://localhost:8000", "/models"),
            ("http://localhost:8004", "/config")
        ]
        
        for service_url, endpoint in data_endpoints:
            task = asyncio.create_task(
                monitor.monitor_service(service_url, endpoint, duration_seconds=300, interval_seconds=5)
            )
            tasks.append(task)
        
        # Wait for all monitoring tasks to complete
        await asyncio.gather(*tasks)
        
        # Generate reports
        sla_report = monitor.generate_sla_report()
        print(sla_report)
        
        # Save metrics
        monitor.save_metrics()
        
        # Generate performance summary
        summary = monitor.get_performance_summary()
        print(f"\nPerformance Summary: {json.dumps(summary, indent=2)}")

if __name__ == "__main__":
    asyncio.run(run_performance_monitoring())
