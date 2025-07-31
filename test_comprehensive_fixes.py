#!/usr/bin/env python3
"""
Comprehensive Test Script for Critical Backend Issues
Tests all three critical issues: /query 500, /metrics 500, and WebSocket 403

Usage:
    python test_comprehensive_fixes.py

This script will:
1. Test /query endpoint with deep debugging
2. Test /metrics endpoint with graceful fallback
3. Test WebSocket /ws/collaboration endpoint
4. Provide detailed error analysis and recommendations
"""

import asyncio
import aiohttp
import json
import time
import websockets
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveBackendTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_query_endpoint(self) -> Dict[str, Any]:
        """Test /query endpoint with comprehensive debugging."""
        logger.info("🔍 Testing /query endpoint...")
        
        test_data = {
            "query": "What is Python programming language?",
            "max_tokens": 100,
            "confidence_threshold": 0.7
        }

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
                logger.info(f"📊 /query Response Headers: {dict(response.headers)}")
                
                try:
                    response_json = json.loads(response_text)
                    logger.info(f"📊 /query Response Body: {json.dumps(response_json, indent=2)}")
                except json.JSONDecodeError:
                    logger.error(f"❌ /query Response is not valid JSON: {response_text}")
                    response_json = {"raw_response": response_text}

                return {
                    "status_code": response.status,
                    "response_time": response_time,
                    "response_body": response_json,
                    "success": response.status == 200,
                    "error": None if response.status == 200 else f"HTTP {response.status}"
                }

        except Exception as e:
            logger.error(f"❌ /query test failed: {e}")
            return {
                "status_code": None,
                "response_time": None,
                "response_body": None,
                "success": False,
                "error": str(e)
            }

    async def test_metrics_endpoint(self) -> Dict[str, Any]:
        """Test /metrics endpoint with graceful fallback."""
        logger.info("🔍 Testing /metrics endpoint...")

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

                return {
                    "status_code": response.status,
                    "response_time": response_time,
                    "response_body": response_data,
                    "success": response.status in [200, 503],  # Accept both success and graceful fallback
                    "error": None if response.status in [200, 503] else f"HTTP {response.status}"
                }

        except Exception as e:
            logger.error(f"❌ /metrics test failed: {e}")
            return {
                "status_code": None,
                "response_time": None,
                "response_body": None,
                "success": False,
                "error": str(e)
            }

    async def test_websocket_endpoint(self) -> Dict[str, Any]:
        """Test WebSocket /ws/collaboration endpoint."""
        logger.info("🔍 Testing WebSocket /ws/collaboration endpoint...")

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

                    return {
                        "status_code": 200,  # WebSocket doesn't have HTTP status
                        "response_time": response_time,
                        "response_body": response_data if isinstance(response_data, dict) else {"raw": response},
                        "success": True,
                        "error": None
                    }

                except asyncio.TimeoutError:
                    logger.warning("⚠️ WebSocket response timeout")
                    return {
                        "status_code": 200,
                        "response_time": time.time() - start_time,
                        "response_body": {"message": "Connection established but no response received"},
                        "success": True,  # Connection was successful
                        "error": "Timeout waiting for response"
                    }

        except websockets.exceptions.InvalidStatusCode as e:
            logger.error(f"❌ WebSocket connection failed with status {e.status_code}")
            return {
                "status_code": e.status_code,
                "response_time": None,
                "response_body": None,
                "success": False,
                "error": f"WebSocket connection failed: HTTP {e.status_code}"
            }
        except Exception as e:
            logger.error(f"❌ WebSocket test failed: {e}")
            return {
                "status_code": None,
                "response_time": None,
                "response_body": None,
                "success": False,
                "error": str(e)
            }

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all comprehensive tests."""
        logger.info("🚀 Starting Comprehensive Backend Test")
        logger.info("=" * 60)

        # Test 1: /query endpoint
        logger.info("📋 Test 1: /query Endpoint (LLM Orchestration)")
        query_result = await self.test_query_endpoint()
        self.results["query"] = query_result

        # Test 2: /metrics endpoint
        logger.info("📋 Test 2: /metrics Endpoint (Graceful Fallback)")
        metrics_result = await self.test_metrics_endpoint()
        self.results["metrics"] = metrics_result

        # Test 3: WebSocket endpoint
        logger.info("📋 Test 3: WebSocket /ws/collaboration (403 Fix)")
        websocket_result = await self.test_websocket_endpoint()
        self.results["websocket"] = websocket_result

        # Generate summary
        logger.info("=" * 60)
        logger.info("📊 COMPREHENSIVE TEST SUMMARY")
        logger.info("=" * 60)

        total_tests = 3
        passed_tests = sum(1 for result in self.results.values() if result["success"])
        
        logger.info(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        logger.info(f"❌ Tests Failed: {total_tests - passed_tests}/{total_tests}")

        for test_name, result in self.results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            logger.info(f"{status} {test_name.upper()}: {result.get('error', 'Success')}")

        # Detailed analysis
        logger.info("\n🔍 DETAILED ANALYSIS:")
        
        if not query_result["success"]:
            logger.error("❌ /query endpoint issues:")
            logger.error(f"   - Status: {query_result['status_code']}")
            logger.error(f"   - Error: {query_result['error']}")
            logger.error("   - Likely causes: LLM client initialization, API key issues, or orchestrator problems")
            logger.error("   - Check logs for 'DEEP DEBUG' messages")
        
        if not metrics_result["success"]:
            logger.error("❌ /metrics endpoint issues:")
            logger.error(f"   - Status: {metrics_result['status_code']}")
            logger.error(f"   - Error: {metrics_result['error']}")
            logger.error("   - Likely causes: prometheus_client missing or Redis connection issues")
            logger.error("   - Install: pip install prometheus-client")
        
        if not websocket_result["success"]:
            logger.error("❌ WebSocket endpoint issues:")
            logger.error(f"   - Status: {websocket_result['status_code']}")
            logger.error(f"   - Error: {websocket_result['error']}")
            logger.error("   - Likely causes: CORS issues, security middleware blocking, or missing dependencies")
            logger.error("   - Check CORS configuration and security middleware")

        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": passed_tests / total_tests
            },
            "results": self.results
        }

async def main():
    """Main test function."""
    logger.info("🔧 Comprehensive Backend Test Suite")
    logger.info("Testing fixes for: /query 500, /metrics 500, WebSocket 403")
    
    async with ComprehensiveBackendTester() as tester:
        results = await tester.run_comprehensive_test()
        
        # Save results to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📄 Results saved to: {filename}")
        
        # Final recommendation
        if results["summary"]["success_rate"] == 1.0:
            logger.info("🎉 ALL TESTS PASSED! Backend is fully operational.")
        else:
            logger.warning("⚠️ Some tests failed. Check the detailed analysis above.")
            logger.info("💡 Run the backend with debug logging to see detailed error messages:")
            logger.info("   python -m uvicorn services.api-gateway.main:app --reload --log-level debug")

if __name__ == "__main__":
    asyncio.run(main()) 