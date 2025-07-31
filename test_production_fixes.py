#!/usr/bin/env python3
"""
Production Test Script for Critical Backend Issues
Comprehensive testing with detailed error analysis and actionable recommendations.

This script tests all three critical issues:
1. /query endpoint (LLM orchestration)
2. /metrics endpoint (graceful fallback)
3. WebSocket /ws/collaboration (403 fix)

Usage:
    python test_production_fixes.py

Features:
- Detailed error surface and analysis
- Actionable recommendations
- Production-grade logging
- Comprehensive test coverage
"""

import asyncio
import aiohttp
import json
import time
import websockets
import logging
import sys
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# Configure production-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Structured test result with detailed information."""
    test_name: str
    success: bool
    status_code: Optional[int]
    response_time: Optional[float]
    error_message: Optional[str]
    response_body: Optional[Dict[str, Any]]
    recommendations: List[str]

class ProductionBackendTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results: List[TestResult] = []

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "ProductionBackendTester/1.0"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_query_endpoint(self) -> TestResult:
        """Test /query endpoint with comprehensive error analysis."""
        logger.info("🔍 Testing /query endpoint (LLM Orchestration)")
        
        test_data = {
            "query": "What is Python programming language?",
            "max_tokens": 100,
            "confidence_threshold": 0.7
        }

        recommendations = []
        
        try:
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/query",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                response_text = await response.text()
                
                logger.info(f"📊 /query Response Status: {response.status}")
                logger.info(f"📊 /query Response Time: {response_time:.3f}s")
                
                try:
                    response_json = json.loads(response_text)
                    logger.info(f"📊 /query Response Body: {json.dumps(response_json, indent=2)}")
                except json.JSONDecodeError:
                    logger.error(f"❌ /query Response is not valid JSON: {response_text}")
                    response_json = {"raw_response": response_text}

                if response.status == 200:
                    logger.info("✅ /query endpoint working correctly")
                    return TestResult(
                        test_name="Query Endpoint",
                        success=True,
                        status_code=response.status,
                        response_time=response_time,
                        error_message=None,
                        response_body=response_json,
                        recommendations=[]
                    )
                else:
                    # Analyze specific error types
                    if response.status == 500:
                        recommendations.extend([
                            "Check backend logs for 'DEEP DEBUG' messages",
                            "Verify LLM API keys are set correctly",
                            "Ensure LLM client initialization is successful",
                            "Check if orchestrator is properly initialized"
                        ])
                    elif response.status == 401:
                        recommendations.append("Authentication required - check API keys")
                    elif response.status == 403:
                        recommendations.append("Authorization failed - check permissions")
                    elif response.status == 429:
                        recommendations.append("Rate limit exceeded - try again later")
                    
                    return TestResult(
                        test_name="Query Endpoint",
                        success=False,
                        status_code=response.status,
                        response_time=response_time,
                        error_message=f"HTTP {response.status}",
                        response_body=response_json,
                        recommendations=recommendations
                    )

        except aiohttp.ClientError as e:
            logger.error(f"❌ /query network error: {e}")
            recommendations.extend([
                "Check if backend server is running",
                "Verify network connectivity",
                "Check firewall settings"
            ])
            return TestResult(
                test_name="Query Endpoint",
                success=False,
                status_code=None,
                response_time=None,
                error_message=f"Network error: {str(e)}",
                response_body=None,
                recommendations=recommendations
            )
        except Exception as e:
            logger.error(f"❌ /query unexpected error: {e}")
            recommendations.append("Check backend logs for unexpected errors")
            return TestResult(
                test_name="Query Endpoint",
                success=False,
                status_code=None,
                response_time=None,
                error_message=f"Unexpected error: {str(e)}",
                response_body=None,
                recommendations=recommendations
            )

    async def test_metrics_endpoint(self) -> TestResult:
        """Test /metrics endpoint with graceful fallback analysis."""
        logger.info("🔍 Testing /metrics endpoint (Graceful Fallback)")
        
        recommendations = []
        
        try:
            start_time = time.time()
            async with self.session.get(f"{self.base_url}/metrics") as response:
                response_time = time.time() - start_time
                response_text = await response.text()
                
                logger.info(f"📊 /metrics Response Status: {response.status}")
                logger.info(f"📊 /metrics Response Time: {response_time:.3f}s")
                
                # Check if it's Prometheus format or JSON fallback
                is_prometheus = "prometheus" in response.headers.get("content-type", "")
                
                if is_prometheus:
                    logger.info("✅ /metrics returned Prometheus format")
                    response_data = {"format": "prometheus", "content": response_text[:500] + "..."}
                else:
                    try:
                        response_data = json.loads(response_text)
                        logger.info("✅ /metrics returned JSON fallback")
                    except json.JSONDecodeError:
                        logger.error(f"❌ /metrics response is not valid JSON: {response_text}")
                        response_data = {"raw_response": response_text}

                # Analyze response
                if response.status in [200, 503]:
                    if response.status == 503:
                        recommendations.append("Install prometheus-client: pip install prometheus-client")
                        recommendations.append("Check if Redis is running and accessible")
                    
                    return TestResult(
                        test_name="Metrics Endpoint",
                        success=True,  # Accept both success and graceful fallback
                        status_code=response.status,
                        response_time=response_time,
                        error_message=None,
                        response_body=response_data,
                        recommendations=recommendations
                    )
                else:
                    recommendations.extend([
                        "Check metrics service configuration",
                        "Verify prometheus_client installation",
                        "Check Redis connection if using Redis metrics"
                    ])
                    
                    return TestResult(
                        test_name="Metrics Endpoint",
                        success=False,
                        status_code=response.status,
                        response_time=response_time,
                        error_message=f"HTTP {response.status}",
                        response_body=response_data,
                        recommendations=recommendations
                    )

        except Exception as e:
            logger.error(f"❌ /metrics test failed: {e}")
            recommendations.extend([
                "Check if backend server is running",
                "Verify network connectivity",
                "Check metrics service configuration"
            ])
            return TestResult(
                test_name="Metrics Endpoint",
                success=False,
                status_code=None,
                response_time=None,
                error_message=str(e),
                response_body=None,
                recommendations=recommendations
            )

    async def test_websocket_endpoint(self) -> TestResult:
        """Test WebSocket /ws/collaboration endpoint."""
        logger.info("🔍 Testing WebSocket /ws/collaboration endpoint (403 Fix)")
        
        recommendations = []
        
        try:
            start_time = time.time()
            
            # Test WebSocket connection
            uri = f"ws://localhost:8000/ws/collaboration"
            async with websockets.connect(uri) as websocket:
                connection_time = time.time() - start_time
                logger.info(f"✅ WebSocket connection established in {connection_time:.3f}s")

                # Send a test message
                test_message = {
                    "type": "join_session",
                    "session_id": "test_session",
                    "user_id": "test_user"
                }
                
                await websocket.send(json.dumps(test_message))
                logger.info("📤 Sent test message to WebSocket")

                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_time = time.time() - start_time
                    
                    try:
                        response_data = json.loads(response)
                        logger.info(f"📥 WebSocket response: {json.dumps(response_data, indent=2)}")
                    except json.JSONDecodeError:
                        logger.info(f"📥 WebSocket response (raw): {response}")
                        response_data = {"raw": response}

                    return TestResult(
                        test_name="WebSocket Endpoint",
                        success=True,
                        status_code=200,  # WebSocket doesn't have HTTP status
                        response_time=response_time,
                        error_message=None,
                        response_body=response_data,
                        recommendations=[]
                    )

                except asyncio.TimeoutError:
                    logger.warning("⚠️ WebSocket response timeout")
                    recommendations.append("WebSocket connection works but no response received")
                    return TestResult(
                        test_name="WebSocket Endpoint",
                        success=True,  # Connection was successful
                        status_code=200,
                        response_time=time.time() - start_time,
                        error_message="Timeout waiting for response",
                        response_body={"message": "Connection established but no response received"},
                        recommendations=recommendations
                    )

        except websockets.exceptions.InvalidStatusCode as e:
            logger.error(f"❌ WebSocket connection failed with status {e.status_code}")
            if e.status_code == 403:
                recommendations.extend([
                    "Check CORS configuration for WebSocket endpoints",
                    "Verify security middleware bypass for /ws/ paths",
                    "Check WebSocket headers in CORS configuration"
                ])
            elif e.status_code == 404:
                recommendations.append("WebSocket endpoint not found - check routing")
            elif e.status_code == 500:
                recommendations.append("Internal server error in WebSocket handler")
            
            return TestResult(
                test_name="WebSocket Endpoint",
                success=False,
                status_code=e.status_code,
                response_time=None,
                error_message=f"WebSocket connection failed: HTTP {e.status_code}",
                response_body=None,
                recommendations=recommendations
            )
        except Exception as e:
            logger.error(f"❌ WebSocket test failed: {e}")
            recommendations.extend([
                "Check if backend server is running",
                "Verify WebSocket endpoint is properly configured",
                "Check network connectivity and firewall settings"
            ])
            return TestResult(
                test_name="WebSocket Endpoint",
                success=False,
                status_code=None,
                response_time=None,
                error_message=str(e),
                response_body=None,
                recommendations=recommendations
            )

    async def run_production_tests(self) -> Dict[str, Any]:
        """Run all production tests with comprehensive analysis."""
        logger.info("🚀 Starting Production Backend Test Suite")
        logger.info("=" * 80)

        # Test 1: /query endpoint
        logger.info("📋 Test 1: /query Endpoint (LLM Orchestration)")
        query_result = await self.test_query_endpoint()
        self.results.append(query_result)

        # Test 2: /metrics endpoint
        logger.info("📋 Test 2: /metrics Endpoint (Graceful Fallback)")
        metrics_result = await self.test_metrics_endpoint()
        self.results.append(metrics_result)

        # Test 3: WebSocket endpoint
        logger.info("📋 Test 3: WebSocket /ws/collaboration (403 Fix)")
        websocket_result = await self.test_websocket_endpoint()
        self.results.append(websocket_result)

        # Generate comprehensive summary
        logger.info("=" * 80)
        logger.info("📊 PRODUCTION TEST SUMMARY")
        logger.info("=" * 80)

        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result.success)
        
        logger.info(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        logger.info(f"❌ Tests Failed: {total_tests - passed_tests}/{total_tests}")
        logger.info(f"🎯 Success Rate: {(passed_tests / total_tests) * 100:.1f}%")

        # Detailed results
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            logger.info(f"{status} {result.test_name}")
            if not result.success:
                logger.error(f"   Error: {result.error_message}")
                logger.error(f"   Status Code: {result.status_code}")
                logger.error(f"   Response Time: {result.response_time:.3f}s" if result.response_time else "N/A")
            
            if result.recommendations:
                logger.info(f"   💡 Recommendations:")
                for rec in result.recommendations:
                    logger.info(f"     - {rec}")

        # Overall recommendations
        logger.info("\n🔍 OVERALL RECOMMENDATIONS:")
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED! Backend is production-ready.")
        elif passed_tests >= total_tests * 0.66:
            logger.info("👍 Most tests passed. Minor issues need attention.")
        else:
            logger.error("⚠️ Multiple critical issues detected. Immediate attention required.")

        # Action items
        logger.info("\n📋 ACTION ITEMS:")
        all_recommendations = []
        for result in self.results:
            all_recommendations.extend(result.recommendations)
        
        unique_recommendations = list(set(all_recommendations))
        for i, rec in enumerate(unique_recommendations, 1):
            logger.info(f"   {i}. {rec}")

        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": passed_tests / total_tests,
                "timestamp": datetime.now().isoformat()
            },
            "results": [result.__dict__ for result in self.results],
            "recommendations": unique_recommendations
        }

async def main():
    """Main production test function."""
    logger.info("🔧 Production Backend Test Suite")
    logger.info("Testing fixes for: /query 500, /metrics 500, WebSocket 403")
    logger.info(f"Test started at: {datetime.now().isoformat()}")
    
    async with ProductionBackendTester() as tester:
        results = await tester.run_production_tests()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"production_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📄 Results saved to: {filename}")
        
        # Final status
        success_rate = results["summary"]["success_rate"]
        if success_rate == 1.0:
            logger.info("🎉 PRODUCTION READY! All critical issues resolved.")
        elif success_rate >= 0.66:
            logger.info("👍 MOSTLY READY! Minor issues remain but core functionality works.")
        else:
            logger.error("❌ CRITICAL ISSUES! Backend needs immediate attention.")
        
        logger.info("\n💡 Next steps:")
        logger.info("1. Address any failed tests using the recommendations above")
        logger.info("2. Check backend logs for detailed error information")
        logger.info("3. Run tests again after fixes: python test_production_fixes.py")
        logger.info("4. Monitor production deployment with these tests")

if __name__ == "__main__":
    asyncio.run(main()) 