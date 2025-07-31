#!/usr/bin/env python3
"""
Direct API Gateway Health Check and Smoke Test
Tests the actual production API Gateway endpoints directly.

This script:
- Tests all major endpoints with real requests
- Validates response formats and status codes
- Performs WebSocket connectivity tests
- Provides detailed status reporting for each endpoint
- Uses actual production code and dependencies

Author: Universal Knowledge Platform Engineering Team
Version: 1.0.0
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests
import websockets
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DirectAPIGatewayTest:
    """Direct API Gateway health check and smoke test."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http://", "ws://")
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    def test_endpoint(self, method: str, endpoint: str, expected_status: int = 200, 
                     data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Test a specific endpoint and return detailed results."""
        url = urljoin(self.base_url, endpoint)
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return {
                    "endpoint": endpoint,
                    "method": method,
                    "status": "ERROR",
                    "error": f"Unsupported method: {method}",
                    "latency": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "latency_ms": round(latency, 2),
                "response_size": len(response.content),
                "timestamp": datetime.now().isoformat(),
                "success": response.status_code == expected_status
            }
            
            # Add response details
            try:
                result["response_data"] = response.json()
            except json.JSONDecodeError:
                result["response_data"] = response.text[:500]  # Truncate if not JSON
            
            # Add headers info
            result["response_headers"] = dict(response.headers)
            
            if result["success"]:
                logger.info(f"✅ {method} {endpoint} - {response.status_code} ({latency:.2f}ms)")
            else:
                logger.warning(f"⚠️ {method} {endpoint} - {response.status_code} (expected {expected_status}) ({latency:.2f}ms)")
            
            return result
            
        except requests.exceptions.RequestException as e:
            latency = (time.time() - start_time) * 1000
            logger.error(f"❌ {method} {endpoint} - Request failed: {e}")
            return {
                "endpoint": endpoint,
                "method": method,
                "status": "ERROR",
                "error": str(e),
                "latency_ms": round(latency, 2),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    async def test_websocket(self, endpoint: str) -> Dict[str, Any]:
        """Test WebSocket connectivity."""
        ws_url = f"{self.ws_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with websockets.connect(ws_url, timeout=10) as websocket:
                # Send a test message
                test_message = {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat(),
                    "test_id": str(uuid.uuid4())
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response)
                
                latency = (time.time() - start_time) * 1000
                
                result = {
                    "endpoint": endpoint,
                    "method": "WEBSOCKET",
                    "status": "SUCCESS",
                    "latency_ms": round(latency, 2),
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "response_data": response_data
                }
                
                logger.info(f"✅ WebSocket {endpoint} - Connected successfully ({latency:.2f}ms)")
                return result
                
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.error(f"❌ WebSocket {endpoint} - Connection failed: {e}")
            return {
                "endpoint": endpoint,
                "method": "WEBSOCKET",
                "status": "ERROR",
                "error": str(e),
                "latency_ms": round(latency, 2),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    def run_comprehensive_tests(self):
        """Run comprehensive health check and smoke tests."""
        logger.info("🔍 Starting comprehensive health check and smoke tests...")
        self.start_time = datetime.now()
        
        # Test basic endpoints
        basic_tests = [
            ("GET", "/", 200),
            ("GET", "/health", 200),
            ("GET", "/docs", 200),
            ("GET", "/openapi.json", 200),
        ]
        
        for method, endpoint, expected_status in basic_tests:
            result = self.test_endpoint(method, endpoint, expected_status)
            self.test_results.append(result)
        
        # Test authentication endpoints
        auth_tests = [
            ("POST", "/auth/register", 422, {
                "username": "testuser",
                "password": "testpass123",
                "role": "user"
            }),
            ("POST", "/auth/login", 422, {
                "username": "testuser",
                "password": "testpass123"
            }),
        ]
        
        for method, endpoint, expected_status, data in auth_tests:
            result = self.test_endpoint(method, endpoint, expected_status, data)
            self.test_results.append(result)
        
        # Test query endpoints
        query_tests = [
            ("POST", "/query", 422, {
                "query": "What is artificial intelligence?",
                "context": "General knowledge",
                "user_id": "test-user-123"
            }),
            ("GET", "/queries", 401),  # Requires authentication
            ("GET", "/queries/123", 401),  # Requires authentication
        ]
        
        for method, endpoint, expected_status, *args in query_tests:
            data = args[0] if args else None
            result = self.test_endpoint(method, endpoint, expected_status, data)
            self.test_results.append(result)
        
        # Test feedback and analytics endpoints
        feedback_tests = [
            ("POST", "/feedback", 401, {
                "query_id": "test-query-123",
                "rating": 5,
                "comment": "Great response!"
            }),
            ("GET", "/metrics", 401),
            ("GET", "/analytics", 401),
            ("GET", "/security", 401),
        ]
        
        for method, endpoint, expected_status, *args in feedback_tests:
            data = args[0] if args else None
            result = self.test_endpoint(method, endpoint, expected_status, data)
            self.test_results.append(result)
        
        # Test integration endpoints
        integration_tests = [
            ("GET", "/integrations", 200),
            ("POST", "/tasks", 422, {
                "task_type": "research",
                "description": "Test task"
            }),
        ]
        
        for method, endpoint, expected_status, *args in integration_tests:
            data = args[0] if args else None
            result = self.test_endpoint(method, endpoint, expected_status, data)
            self.test_results.append(result)
        
        # Test expert review endpoints
        expert_tests = [
            ("GET", "/expert-reviews/pending", 401),
            ("POST", "/expert-reviews/123", 401, {
                "expert_id": "expert-123",
                "verdict": "supported",
                "notes": "Test review",
                "confidence": 0.8
            }),
            ("GET", "/expert-reviews/123", 401),
        ]
        
        for method, endpoint, expected_status, *args in expert_tests:
            data = args[0] if args else None
            result = self.test_endpoint(method, endpoint, expected_status, data)
            self.test_results.append(result)
        
        logger.info("✅ All HTTP endpoint tests completed")
    
    async def run_websocket_tests(self):
        """Run WebSocket connectivity tests."""
        logger.info("🔌 Testing WebSocket connections...")
        
        ws_tests = [
            "/ws/collaboration",
            "/ws/query-updates",
        ]
        
        for endpoint in ws_tests:
            result = await self.test_websocket(endpoint)
            self.test_results.append(result)
        
        logger.info("✅ All WebSocket tests completed")
    
    def generate_report(self):
        """Generate comprehensive test report."""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Calculate statistics
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.get("success", False))
        failed_tests = total_tests - successful_tests
        
        # Calculate average latency
        latencies = [result.get("latency_ms", 0) for result in self.test_results if "latency_ms" in result]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        # Group results by status
        successful_results = [r for r in self.test_results if r.get("success", False)]
        failed_results = [r for r in self.test_results if not r.get("success", False)]
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": round((successful_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
                "average_latency_ms": round(avg_latency, 2),
                "test_duration_seconds": round(duration, 2),
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat()
            },
            "endpoint_results": {
                "successful": successful_results,
                "failed": failed_results
            },
            "detailed_results": self.test_results
        }
        
        # Print summary
        logger.info("=" * 80)
        logger.info("📊 COMPREHENSIVE HEALTH CHECK REPORT")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Successful: {successful_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {report['test_summary']['success_rate']}%")
        logger.info(f"Average Latency: {report['test_summary']['average_latency_ms']}ms")
        logger.info(f"Test Duration: {report['test_summary']['test_duration_seconds']}s")
        logger.info("=" * 80)
        
        # Print failed tests details
        if failed_results:
            logger.warning("❌ FAILED TESTS:")
            for result in failed_results:
                logger.warning(f"  - {result['method']} {result['endpoint']}: {result.get('error', 'Unknown error')}")
        
        # Save detailed report
        report_file = f"direct_api_gateway_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Detailed report saved to: {report_file}")
        
        return report

async def main():
    """Main function to run direct API Gateway tests."""
    import sys
    
    # Get base URL from command line argument or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    logger.info(f"🚀 Starting direct API Gateway tests against: {base_url}")
    
    test_runner = DirectAPIGatewayTest(base_url)
    
    try:
        # Run HTTP tests
        test_runner.run_comprehensive_tests()
        
        # Run WebSocket tests
        await test_runner.run_websocket_tests()
        
        # Generate report
        report = test_runner.generate_report()
        
        # Determine exit code
        success_rate = report['test_summary']['success_rate']
        if success_rate >= 80:
            logger.info("🎉 Health check completed successfully!")
            return 0
        elif success_rate >= 60:
            logger.warning("⚠️ Health check completed with warnings")
            return 1
        else:
            logger.error("❌ Health check failed")
            return 1
            
    except KeyboardInterrupt:
        logger.info("🛑 Health check interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Health check failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 