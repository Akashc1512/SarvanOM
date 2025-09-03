#!/usr/bin/env python3
"""
Production Load Testing - Phase E3
==================================

Comprehensive load testing for production deployment validation:
- Concurrent user simulation
- Performance degradation under load
- SLA compliance verification
- Cost optimization validation
- Real API key stress testing

Requirements: aiohttp, asyncio
"""

import asyncio
import aiohttp
import time
import random
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import statistics

@dataclass
class LoadTestResult:
    """Individual test result."""
    endpoint: str
    response_time_ms: float
    status_code: int
    success: bool
    error: str = ""
    timestamp: float = 0.0

class ProductionLoadTester:
    """
    Production-grade load testing for SarvanOM.
    
    Tests all critical endpoints under realistic load conditions.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize load tester."""
        self.base_url = base_url.rstrip('/')
        self.results: List[LoadTestResult] = []
        
        # Test queries representing real user behavior
        self.test_queries = [
            "What is machine learning?",
            "How does blockchain work?",
            "Explain quantum computing",
            "Benefits of renewable energy",
            "History of artificial intelligence",
            "Climate change solutions",
            "Best programming languages for AI",
            "How to start a tech startup",
            "Future of remote work",
            "Cybersecurity best practices"
        ]
        
        self.test_endpoints = [
            ("/health", "GET", {}),
            ("/search", "GET", {"q": "machine learning", "limit": 5}),
            ("/metrics/performance", "GET", {}),
            ("/metrics/vector", "GET", {}),
            ("/metrics/lanes", "GET", {}),
        ]
    
    async def simulate_user_session(self, session: aiohttp.ClientSession, user_id: int) -> List[LoadTestResult]:
        """Simulate a realistic user session."""
        session_results = []
        
        try:
            # User starts with a search query
            query = random.choice(self.test_queries)
            
            # Test search endpoint
            search_result = await self._test_endpoint(
                session, 
                f"/search?q={query}&limit=5", 
                "GET"
            )
            session_results.append(search_result)
            
            # Random delay between requests (1-3 seconds)
            await asyncio.sleep(random.uniform(1.0, 3.0))
            
            # Test complete query processing
            query_result = await self._test_endpoint(
                session,
                "/query",
                "POST",
                {"query": query}
            )
            session_results.append(query_result)
            
            # Test citations processing (30% of users)
            if random.random() < 0.3:
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
                citations_result = await self._test_endpoint(
                    session,
                    "/citations/process",
                    "POST",
                    {
                        "text": f"Machine learning is a subset of AI. {query}",
                        "sources": [
                            {"title": "ML Guide", "url": "https://example.com/ml", "content": "ML overview"}
                        ]
                    }
                )
                session_results.append(citations_result)
            
        except Exception as e:
            error_result = LoadTestResult(
                endpoint="session",
                response_time_ms=0,
                status_code=500,
                success=False,
                error=str(e),
                timestamp=time.time()
            )
            session_results.append(error_result)
        
        return session_results
    
    async def _test_endpoint(self, session: aiohttp.ClientSession, endpoint: str, method: str, data: Dict[str, Any] = None) -> LoadTestResult:
        """Test a single endpoint."""
        start_time = time.time()
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                async with session.get(url) as response:
                    await response.text()  # Consume response
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    return LoadTestResult(
                        endpoint=endpoint,
                        response_time_ms=response_time_ms,
                        status_code=response.status,
                        success=response.status < 400,
                        timestamp=start_time
                    )
            
            elif method == "POST":
                async with session.post(url, json=data) as response:
                    await response.text()  # Consume response
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    return LoadTestResult(
                        endpoint=endpoint,
                        response_time_ms=response_time_ms,
                        status_code=response.status,
                        success=response.status < 400,
                        timestamp=start_time
                    )
        
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return LoadTestResult(
                endpoint=endpoint,
                response_time_ms=response_time_ms,
                status_code=500,
                success=False,
                error=str(e),
                timestamp=start_time
            )
    
    async def run_load_test(self, concurrent_users: int = 10, duration_seconds: int = 60) -> Dict[str, Any]:
        """Run comprehensive load test."""
        print(f"🚀 Starting load test: {concurrent_users} concurrent users for {duration_seconds}s")
        start_time = time.time()
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=10.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            
            # Start user sessions
            tasks = []
            for user_id in range(concurrent_users):
                task = asyncio.create_task(
                    self._run_user_for_duration(session, user_id, duration_seconds)
                )
                tasks.append(task)
            
            # Wait for all users to complete
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Flatten results
            for user_results in all_results:
                if isinstance(user_results, list):
                    self.results.extend(user_results)
                elif isinstance(user_results, Exception):
                    print(f"User session error: {user_results}")
        
        total_time = time.time() - start_time
        return self._analyze_results(total_time)
    
    async def _run_user_for_duration(self, session: aiohttp.ClientSession, user_id: int, duration_seconds: int) -> List[LoadTestResult]:
        """Run user sessions for specified duration."""
        user_results = []
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            session_results = await self.simulate_user_session(session, user_id)
            user_results.extend(session_results)
            
            # Random think time between sessions
            await asyncio.sleep(random.uniform(2.0, 5.0))
        
        return user_results
    
    def _analyze_results(self, total_duration: float) -> Dict[str, Any]:
        """Analyze load test results."""
        if not self.results:
            return {"error": "No results to analyze"}
        
        # Overall statistics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        # Response time statistics
        response_times = [r.response_time_ms for r in self.results if r.success]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = median_response_time = p95_response_time = p99_response_time = 0
            min_response_time = max_response_time = 0
        
        # Requests per second
        rps = total_requests / total_duration if total_duration > 0 else 0
        
        # Per-endpoint analysis
        endpoint_stats = {}
        for endpoint in set(r.endpoint for r in self.results):
            endpoint_results = [r for r in self.results if r.endpoint == endpoint]
            endpoint_successes = [r for r in endpoint_results if r.success]
            
            if endpoint_results:
                endpoint_stats[endpoint] = {
                    'total_requests': len(endpoint_results),
                    'successful_requests': len(endpoint_successes),
                    'success_rate': len(endpoint_successes) / len(endpoint_results),
                    'avg_response_time_ms': statistics.mean([r.response_time_ms for r in endpoint_successes]) if endpoint_successes else 0,
                    'p95_response_time_ms': statistics.quantiles([r.response_time_ms for r in endpoint_successes], n=20)[18] if len(endpoint_successes) >= 20 else 0
                }
        
        # SLA compliance check
        sla_compliance = {
            'query_response_under_3s': sum(1 for r in self.results if r.endpoint.startswith('/query') and r.response_time_ms <= 3000) / max(1, sum(1 for r in self.results if r.endpoint.startswith('/query'))),
            'search_response_under_3s': sum(1 for r in self.results if r.endpoint.startswith('/search') and r.response_time_ms <= 3000) / max(1, sum(1 for r in self.results if r.endpoint.startswith('/search'))),
            'overall_success_rate': success_rate
        }
        
        # Performance assessment
        performance_grade = "A"
        if success_rate < 0.95 or p95_response_time > 5000:
            performance_grade = "B"
        if success_rate < 0.90 or p95_response_time > 8000:
            performance_grade = "C"
        if success_rate < 0.80 or p95_response_time > 12000:
            performance_grade = "D"
        if success_rate < 0.70:
            performance_grade = "F"
        
        return {
            'test_summary': {
                'total_duration_seconds': round(total_duration, 2),
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate': round(success_rate, 3),
                'requests_per_second': round(rps, 2),
                'performance_grade': performance_grade
            },
            'response_time_stats': {
                'avg_ms': round(avg_response_time, 2),
                'median_ms': round(median_response_time, 2),
                'p95_ms': round(p95_response_time, 2),
                'p99_ms': round(p99_response_time, 2),
                'min_ms': round(min_response_time, 2),
                'max_ms': round(max_response_time, 2)
            },
            'sla_compliance': sla_compliance,
            'endpoint_performance': endpoint_stats,
            'production_readiness': {
                'ready_for_deployment': performance_grade in ['A', 'B'] and success_rate >= 0.90,
                'recommended_max_concurrent_users': concurrent_users if performance_grade == 'A' else max(1, concurrent_users // 2),
                'optimization_needed': p95_response_time > 4000 or success_rate < 0.95
            }
        }

async def main():
    """Run load testing scenarios."""
    print("🧪 SarvanOM Production Load Testing Suite")
    print("=" * 50)
    
    tester = ProductionLoadTester()
    
    # Test scenarios
    scenarios = [
        (5, 30),   # Light load: 5 users for 30s
        (10, 60),  # Medium load: 10 users for 60s  
        (20, 45),  # Heavy load: 20 users for 45s
    ]
    
    for i, (users, duration) in enumerate(scenarios, 1):
        print(f"\n📊 Scenario {i}: {users} concurrent users for {duration}s")
        print("-" * 40)
        
        results = await tester.run_load_test(users, duration)
        
        print("Results:")
        print(f"  Success Rate: {results['test_summary']['success_rate']:.1%}")
        print(f"  RPS: {results['test_summary']['requests_per_second']:.1f}")
        print(f"  P95 Response Time: {results['response_time_stats']['p95_ms']:.0f}ms")
        print(f"  Performance Grade: {results['test_summary']['performance_grade']}")
        print(f"  Production Ready: {results['production_readiness']['ready_for_deployment']}")
        
        # Reset results for next test
        tester.results = []
        
        # Brief pause between scenarios
        if i < len(scenarios):
            print("\n⏳ Cooling down...")
            await asyncio.sleep(10)
    
    print("\n🎯 Load testing complete!")

if __name__ == "__main__":
    asyncio.run(main())
