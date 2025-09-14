"""
Simple Load Test Runner for SarvanOM Services

This is a simplified load testing script that can run immediately
without complex import dependencies.
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleLoadTester:
    """Simple load testing class"""
    
    def __init__(self):
        self.results = []
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, url: str, concurrent_users: int = 10, duration_seconds: int = 30):
        """Test a single endpoint with concurrent users"""
        logger.info(f"Testing {url} with {concurrent_users} users for {duration_seconds} seconds")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        # Create tasks for concurrent users
        tasks = []
        for user_id in range(concurrent_users):
            task = asyncio.create_task(self._user_simulation(url, start_time, end_time, user_id))
            tasks.append(task)
        
        # Wait for all tasks to complete
        user_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        all_results = []
        for user_result in user_results:
            if isinstance(user_result, Exception):
                logger.error(f"User simulation error: {user_result}")
                continue
            all_results.extend(user_result)
        
        # Calculate statistics
        if all_results:
            response_times = [r['response_time'] for r in all_results]
            successful = sum(1 for r in all_results if r['success'])
            total = len(all_results)
            
            result = {
                'url': url,
                'total_requests': total,
                'successful_requests': successful,
                'failed_requests': total - successful,
                'success_rate': (successful / total * 100) if total > 0 else 0,
                'avg_response_time': statistics.mean(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'requests_per_second': total / duration_seconds,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            logger.info(f"✅ {url}: {successful}/{total} successful, {result['requests_per_second']:.2f} req/s, avg {result['avg_response_time']:.3f}s")
            return result
        else:
            logger.error(f"❌ No results for {url}")
            return None
    
    async def _user_simulation(self, url: str, start_time: float, end_time: float, user_id: int):
        """Simulate a single user making requests"""
        results = []
        current_time = time.time()
        
        while current_time < end_time:
            try:
                request_start = time.time()
                async with self.session.get(url) as response:
                    response_text = await response.text()
                    request_end = time.time()
                    
                    results.append({
                        'success': response.status < 400,
                        'status_code': response.status,
                        'response_time': request_end - request_start,
                        'response_size': len(response_text)
                    })
                    
            except Exception as e:
                results.append({
                    'success': False,
                    'status_code': 0,
                    'response_time': 0,
                    'response_size': 0,
                    'error': str(e)
                })
            
            # Wait before next request
            await asyncio.sleep(0.1)  # 10 requests per second per user
            current_time = time.time()
        
        return results
    
    def generate_report(self):
        """Generate a simple test report"""
        if not self.results:
            return "No test results available."
        
        report = []
        report.append("=" * 80)
        report.append("SARVANOM SIMPLE LOAD TEST REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {len(self.results)}")
        report.append("")
        
        for result in self.results:
            report.append(f"URL: {result['url']}")
            report.append(f"Total Requests: {result['total_requests']}")
            report.append(f"Successful: {result['successful_requests']} ({result['success_rate']:.1f}%)")
            report.append(f"Failed: {result['failed_requests']}")
            report.append(f"Requests/sec: {result['requests_per_second']:.2f}")
            report.append(f"Avg Response Time: {result['avg_response_time']:.3f}s")
            report.append(f"Min Response Time: {result['min_response_time']:.3f}s")
            report.append(f"Max Response Time: {result['max_response_time']:.3f}s")
            report.append("-" * 40)
        
        return "\n".join(report)

async def run_simple_load_tests():
    """Run simple load tests on all services"""
    logger.info("🚀 Starting Simple Load Tests for SarvanOM Services")
    
    # Service endpoints to test
    endpoints = [
        ("http://localhost:8000/health", "Model Registry Health"),
        ("http://localhost:8004/health", "Retrieval Health"),
        ("http://localhost:8005/health", "Feeds Health"),
        ("http://localhost:8012/auth/health", "Auth Health"),
        ("http://localhost:8013/health", "Knowledge Graph Health"),
        ("http://localhost:8000/models", "Model Registry Models"),
        ("http://localhost:8004/config", "Retrieval Config"),
        ("http://localhost:8005/config", "Feeds Config")
    ]
    
    async with SimpleLoadTester() as tester:
        # Test each endpoint
        for url, description in endpoints:
            logger.info(f"Testing: {description}")
            try:
                await tester.test_endpoint(url, concurrent_users=5, duration_seconds=20)
                await asyncio.sleep(2)  # Brief pause between tests
            except Exception as e:
                logger.error(f"Failed to test {url}: {e}")
        
        # Generate and display report
        report = tester.generate_report()
        print(report)
        
        # Save results
        with open(f"simple_load_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(tester.results, f, indent=2)
        
        logger.info("✅ Simple load testing completed!")
        return tester.results

async def run_health_check_tests():
    """Run quick health check tests"""
    logger.info("🏥 Starting Health Check Tests")
    
    health_endpoints = [
        "http://localhost:8000/health",
        "http://localhost:8004/health", 
        "http://localhost:8005/health",
        "http://localhost:8012/auth/health",
        "http://localhost:8013/health"
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        results = []
        
        for url in health_endpoints:
            try:
                start_time = time.time()
                async with session.get(url) as response:
                    response_text = await response.text()
                    end_time = time.time()
                    
                    result = {
                        'url': url,
                        'status_code': response.status,
                        'response_time': end_time - start_time,
                        'healthy': response.status == 200,
                        'response_size': len(response_text)
                    }
                    
                    results.append(result)
                    
                    status = "✅ HEALTHY" if result['healthy'] else "❌ UNHEALTHY"
                    logger.info(f"{status} {url} - {result['response_time']:.3f}s - {result['status_code']}")
                    
            except Exception as e:
                result = {
                    'url': url,
                    'status_code': 0,
                    'response_time': 0,
                    'healthy': False,
                    'error': str(e)
                }
                results.append(result)
                logger.error(f"❌ ERROR {url} - {e}")
        
        # Summary
        healthy_count = sum(1 for r in results if r['healthy'])
        total_count = len(results)
        
        logger.info(f"🏥 Health Check Summary: {healthy_count}/{total_count} services healthy")
        
        return results

async def run_feeds_integration_test():
    """Run integration test on feeds service"""
    logger.info("📰 Starting Feeds Integration Test")
    
    test_payload = {
        "query": "artificial intelligence news",
        "feed_type": "news",
        "user_id": "test_user_001",
        "session_id": "test_session_001",
        "trace_id": "test_trace_001",
        "constraints": {"limit": 3}
    }
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        try:
            start_time = time.time()
            async with session.post(
                "http://localhost:8005/fetch",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_text = await response.text()
                end_time = time.time()
                
                result = {
                    'status_code': response.status,
                    'response_time': end_time - start_time,
                    'response_size': len(response_text),
                    'success': response.status == 200,
                    'has_data': len(response_text) > 100
                }
                
                if result['success'] and result['has_data']:
                    logger.info(f"✅ Feeds Integration Test PASSED - {result['response_time']:.3f}s - {result['response_size']} bytes")
                else:
                    logger.warning(f"⚠️ Feeds Integration Test ISSUES - Status: {result['status_code']}, Size: {result['response_size']}")
                
                return result
                
        except Exception as e:
            logger.error(f"❌ Feeds Integration Test FAILED - {e}")
            return {'success': False, 'error': str(e)}

async def main():
    """Main testing function"""
    logger.info("🎯 Starting SarvanOM Comprehensive Testing")
    
    # Phase 1: Health Checks
    logger.info("\n" + "="*60)
    logger.info("PHASE 1: HEALTH CHECKS")
    logger.info("="*60)
    health_results = await run_health_check_tests()
    
    # Phase 2: Integration Tests
    logger.info("\n" + "="*60)
    logger.info("PHASE 2: INTEGRATION TESTS")
    logger.info("="*60)
    feeds_result = await run_feeds_integration_test()
    
    # Phase 3: Load Tests
    logger.info("\n" + "="*60)
    logger.info("PHASE 3: LOAD TESTS")
    logger.info("="*60)
    load_results = await run_simple_load_tests()
    
    # Final Summary
    logger.info("\n" + "="*60)
    logger.info("FINAL TESTING SUMMARY")
    logger.info("="*60)
    
    healthy_services = sum(1 for r in health_results if r['healthy'])
    total_services = len(health_results)
    
    logger.info(f"🏥 Health Checks: {healthy_services}/{total_services} services healthy")
    logger.info(f"📰 Integration Tests: {'PASSED' if feeds_result.get('success') else 'FAILED'}")
    logger.info(f"🚀 Load Tests: {len(load_results)} endpoints tested")
    
    if healthy_services == total_services and feeds_result.get('success'):
        logger.info("🎉 ALL TESTS PASSED - System is ready for production!")
        return True
    else:
        logger.warning("⚠️ Some tests failed - Review results before production deployment")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
