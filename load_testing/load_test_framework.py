"""
SarvanOM Load Testing Framework

This module provides comprehensive load testing capabilities for all microservices
in the SarvanOM platform. It includes concurrent request testing, performance
benchmarking, and stress testing scenarios.

Features:
- Concurrent user simulation
- Service-specific load tests
- Performance metrics collection
- Stress testing scenarios
- Real-time monitoring integration
"""

import asyncio
import aiohttp
import time
import json
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LoadTestResult:
    """Results from a load test execution"""
    service_name: str
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    errors: List[str]
    timestamp: datetime

@dataclass
class LoadTestConfig:
    """Configuration for load testing"""
    service_url: str
    endpoint: str
    method: str = "GET"
    payload: Optional[Dict] = None
    headers: Optional[Dict] = None
    concurrent_users: int = 10
    duration_seconds: int = 60
    ramp_up_seconds: int = 10

class LoadTestFramework:
    """Main load testing framework"""
    
    def __init__(self):
        self.results: List[LoadTestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, config: LoadTestConfig) -> Dict[str, Any]:
        """Make a single HTTP request"""
        start_time = time.time()
        try:
            if config.method.upper() == "GET":
                async with self.session.get(
                    f"{config.service_url}{config.endpoint}",
                    headers=config.headers
                ) as response:
                    response_text = await response.text()
                    end_time = time.time()
                    return {
                        "success": response.status < 400,
                        "status_code": response.status,
                        "response_time": end_time - start_time,
                        "response_size": len(response_text),
                        "error": None
                    }
            elif config.method.upper() == "POST":
                async with self.session.post(
                    f"{config.service_url}{config.endpoint}",
                    json=config.payload,
                    headers=config.headers
                ) as response:
                    response_text = await response.text()
                    end_time = time.time()
                    return {
                        "success": response.status < 400,
                        "status_code": response.status,
                        "response_time": end_time - start_time,
                        "response_size": len(response_text),
                        "error": None
                    }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "status_code": 0,
                "response_time": end_time - start_time,
                "response_size": 0,
                "error": str(e)
            }
    
    async def run_load_test(self, config: LoadTestConfig) -> LoadTestResult:
        """Run a load test for a specific service and endpoint"""
        logger.info(f"Starting load test for {config.service_url}{config.endpoint}")
        logger.info(f"Concurrent users: {config.concurrent_users}, Duration: {config.duration_seconds}s")
        
        start_time = time.time()
        end_time = start_time + config.duration_seconds
        ramp_up_end = start_time + config.ramp_up_seconds
        
        # Track results
        response_times = []
        successful_requests = 0
        failed_requests = 0
        errors = []
        
        # Create tasks for concurrent users
        tasks = []
        for user_id in range(config.concurrent_users):
            task = asyncio.create_task(
                self._user_simulation(config, start_time, end_time, ramp_up_end, user_id)
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        user_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        for user_result in user_results:
            if isinstance(user_result, Exception):
                errors.append(f"User simulation error: {str(user_result)}")
                continue
                
            for result in user_result:
                response_times.append(result["response_time"])
                if result["success"]:
                    successful_requests += 1
                else:
                    failed_requests += 1
                    if result["error"]:
                        errors.append(result["error"])
        
        total_requests = successful_requests + failed_requests
        actual_duration = time.time() - start_time
        
        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = self._percentile(response_times, 95)
            p99_response_time = self._percentile(response_times, 99)
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        requests_per_second = total_requests / actual_duration if actual_duration > 0 else 0
        
        result = LoadTestResult(
            service_name=config.service_url.split("//")[1].split(":")[0],
            endpoint=config.endpoint,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            errors=errors[:10],  # Limit errors to first 10
            timestamp=datetime.now()
        )
        
        self.results.append(result)
        logger.info(f"Load test completed: {successful_requests}/{total_requests} successful, "
                   f"{requests_per_second:.2f} req/s, avg {avg_response_time:.3f}s")
        
        return result
    
    async def _user_simulation(self, config: LoadTestConfig, start_time: float, 
                             end_time: float, ramp_up_end: float, user_id: int) -> List[Dict]:
        """Simulate a single user making requests"""
        results = []
        current_time = time.time()
        
        while current_time < end_time:
            # Ramp up phase - gradually increase request rate
            if current_time < ramp_up_end:
                ramp_up_progress = (current_time - start_time) / (ramp_up_end - start_time)
                # Start with 1 request per second, ramp up to full rate
                base_interval = 1.0 / (1 + ramp_up_progress * 9)  # 1s to 0.1s
            else:
                base_interval = 0.1  # 10 requests per second
            
            # Add some jitter
            interval = base_interval + (time.time() % 0.1) * 0.1
            
            # Make request
            result = await self.make_request(config)
            results.append(result)
            
            # Wait before next request
            await asyncio.sleep(interval)
            current_time = time.time()
        
        return results
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def generate_report(self) -> str:
        """Generate a comprehensive load test report"""
        if not self.results:
            return "No load test results available."
        
        report = []
        report.append("=" * 80)
        report.append("SARVANOM LOAD TESTING REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {len(self.results)}")
        report.append("")
        
        for result in self.results:
            report.append(f"Service: {result.service_name}")
            report.append(f"Endpoint: {result.endpoint}")
            report.append(f"Total Requests: {result.total_requests}")
            report.append(f"Successful: {result.successful_requests} ({result.successful_requests/result.total_requests*100:.1f}%)")
            report.append(f"Failed: {result.failed_requests} ({result.failed_requests/result.total_requests*100:.1f}%)")
            report.append(f"Requests/sec: {result.requests_per_second:.2f}")
            report.append(f"Avg Response Time: {result.avg_response_time:.3f}s")
            report.append(f"Min Response Time: {result.min_response_time:.3f}s")
            report.append(f"Max Response Time: {result.max_response_time:.3f}s")
            report.append(f"95th Percentile: {result.p95_response_time:.3f}s")
            report.append(f"99th Percentile: {result.p99_response_time:.3f}s")
            
            if result.errors:
                report.append(f"Errors: {len(result.errors)}")
                for error in result.errors[:3]:  # Show first 3 errors
                    report.append(f"  - {error}")
            
            report.append("-" * 40)
        
        return "\n".join(report)
    
    def save_results(self, filename: str = None):
        """Save results to JSON file"""
        if not filename:
            filename = f"load_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert results to serializable format
        serializable_results = []
        for result in self.results:
            serializable_results.append({
                "service_name": result.service_name,
                "endpoint": result.endpoint,
                "total_requests": result.total_requests,
                "successful_requests": result.successful_requests,
                "failed_requests": result.failed_requests,
                "avg_response_time": result.avg_response_time,
                "min_response_time": result.min_response_time,
                "max_response_time": result.max_response_time,
                "p95_response_time": result.p95_response_time,
                "p99_response_time": result.p99_response_time,
                "requests_per_second": result.requests_per_second,
                "errors": result.errors,
                "timestamp": result.timestamp.isoformat()
            })
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"Results saved to {filename}")

# Service configurations for load testing
SERVICE_CONFIGS = {
    "model_registry": {
        "url": "http://localhost:8000",
        "endpoints": ["/health", "/models", "/providers"]
    },
    "gateway": {
        "url": "http://localhost:8007", 
        "endpoints": ["/health", "/config"]
    },
    "synthesis": {
        "url": "http://localhost:8008",
        "endpoints": ["/health", "/synthesis/health"]
    },
    "feeds": {
        "url": "http://localhost:8005",
        "endpoints": ["/health", "/config"]
    },
    "retrieval": {
        "url": "http://localhost:8004",
        "endpoints": ["/health", "/config"]
    },
    "auth": {
        "url": "http://localhost:8012",
        "endpoints": ["/auth/health", "/auth/"]
    },
    "knowledge_graph": {
        "url": "http://localhost:8013",
        "endpoints": ["/health"]
    },
    "search": {
        "url": "http://localhost:8015",
        "endpoints": ["/search/health"]
    }
}

async def run_comprehensive_load_test():
    """Run comprehensive load tests across all services"""
    async with LoadTestFramework() as framework:
        logger.info("Starting comprehensive load testing...")
        
        # Test scenarios
        scenarios = [
            # Light load - 5 users, 30 seconds
            {"concurrent_users": 5, "duration_seconds": 30, "ramp_up_seconds": 5},
            # Medium load - 20 users, 60 seconds  
            {"concurrent_users": 20, "duration_seconds": 60, "ramp_up_seconds": 10},
            # Heavy load - 50 users, 120 seconds
            {"concurrent_users": 50, "duration_seconds": 120, "ramp_up_seconds": 20}
        ]
        
        for scenario in scenarios:
            logger.info(f"Running scenario: {scenario['concurrent_users']} users, "
                       f"{scenario['duration_seconds']}s duration")
            
            for service_name, service_config in SERVICE_CONFIGS.items():
                for endpoint in service_config["endpoints"]:
                    config = LoadTestConfig(
                        service_url=service_config["url"],
                        endpoint=endpoint,
                        method="GET",
                        concurrent_users=scenario["concurrent_users"],
                        duration_seconds=scenario["duration_seconds"],
                        ramp_up_seconds=scenario["ramp_up_seconds"]
                    )
                    
                    try:
                        await framework.run_load_test(config)
                        # Small delay between tests
                        await asyncio.sleep(2)
                    except Exception as e:
                        logger.error(f"Load test failed for {service_name}{endpoint}: {e}")
        
        # Generate and save report
        report = framework.generate_report()
        print(report)
        
        framework.save_results()
        
        return framework.results

if __name__ == "__main__":
    asyncio.run(run_comprehensive_load_test())
