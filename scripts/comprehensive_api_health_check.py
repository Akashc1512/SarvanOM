#!/usr/bin/env python3
"""
Comprehensive API Health Check Script
Tests all endpoints of the Universal Knowledge Hub API Gateway

This script performs:
- Health checks on all endpoints
- Authentication flow testing
- Response time measurements
- JSON validation
- Error handling verification
- WebSocket connectivity testing

Usage:
    python scripts/comprehensive_api_health_check.py
"""

import asyncio
import json
import time
import httpx
import websockets
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


@dataclass
class TestResult:
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    auth_required: bool = False
    auth_success: Optional[bool] = None


class APIHealthChecker:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.auth_token = None
        self.test_user = {
            "username": "testuser_health_check",
            "password": "testpass123",
            "email": "test@healthcheck.com",
        }
        self.results: List[TestResult] = []

    def log(self, message: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def test_endpoint(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        auth_required: bool = False,
        expected_status: Optional[int] = None,
    ) -> TestResult:
        """Test a single endpoint and return results"""
        return self.test_endpoint_with_headers(
            method, endpoint, data, headers, auth_required, expected_status
        )

    async def test_endpoint_with_headers(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        auth_required: bool = False,
        expected_status: Optional[int] = None,
    ) -> TestResult:
        """Test a single endpoint and return results"""
        url = urljoin(self.base_url, endpoint)
        start_time = time.time()

        try:
            if headers is None:
                headers = {}

            if self.auth_token and auth_required:
                headers["Authorization"] = f"Bearer {self.auth_token}"

            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, timeout=10.0)
                elif method.upper() == "POST":
                    response = await client.post(
                        url, json=data, headers=headers, timeout=10.0
                    )
                elif method.upper() == "PUT":
                    response = await client.put(
                        url, json=data, headers=headers, timeout=10.0
                    )
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=headers, timeout=10.0)
                else:
                    raise ValueError(f"Unsupported method: {method}")

            response_time = time.time() - start_time

            # Determine success based on status code
            if expected_status:
                success = response.status_code == expected_status
            elif auth_required:
                # For auth-required endpoints, 200/201 is success, 401 is expected for no auth
                success = response.status_code in [200, 201] or (
                    response.status_code == 401 and not self.auth_token
                )
            else:
                success = response.status_code in [200, 201]

            # Parse response data
            response_data = None
            try:
                if response.headers.get("content-type", "").startswith(
                    "application/json"
                ):
                    response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"raw_text": response.text[:500]}

            result = TestResult(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                response_data=response_data,
                auth_required=auth_required,
                auth_success=(
                    response.status_code in [200, 201] if auth_required else None
                ),
            )

            if not success:
                result.error_message = (
                    f"Expected success but got status {response.status_code}"
                )

        except httpx.RequestError as e:
            response_time = time.time() - start_time
            result = TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e),
                auth_required=auth_required,
            )

        self.results.append(result)
        return result

    async def test_health_endpoint(self) -> TestResult:
        """Test the health endpoint"""
        self.log("🔍 Testing /health endpoint...")
        return await self.test_endpoint_with_headers(
            "GET", "/health", expected_status=200
        )

    async def test_docs_endpoint(self) -> TestResult:
        """Test the API documentation endpoint"""
        self.log("📚 Testing /docs endpoint...")
        return await self.test_endpoint_with_headers(
            "GET", "/docs", expected_status=200
        )

    async def test_register_endpoint(self) -> TestResult:
        """Test user registration"""
        self.log("📝 Testing /auth/register endpoint...")
        return await self.test_endpoint_with_headers(
            "POST", "/auth/register", data=self.test_user, expected_status=201
        )

    async def test_login_endpoint(self) -> TestResult:
        """Test user login and capture auth token"""
        self.log("🔐 Testing /auth/login endpoint...")

        # Use OAuth2 form data format
        data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"],
            "grant_type": "password",
        }

        # Set content type to form data
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        result = await self.test_endpoint_with_headers(
            "POST", "/auth/login", data=data, headers=headers, expected_status=200
        )

        # Extract auth token if login successful
        if result.success and result.response_data:
            self.auth_token = result.response_data.get("access_token")
            if self.auth_token:
                self.log("✅ Authentication token captured successfully")
            else:
                self.log("⚠️  No auth token found in login response")

        return result

    async def test_query_endpoint(self) -> TestResult:
        """Test the main query endpoint"""
        self.log("❓ Testing /query endpoint...")
        query_data = {
            "query": "What is artificial intelligence?",
            "context": "General knowledge question",
            "preferences": {"depth": "comprehensive", "format": "structured"},
        }
        return await self.test_endpoint_with_headers(
            "POST", "/query", data=query_data, auth_required=True
        )

    def test_integrations_endpoint(self) -> TestResult:
        """Test the integrations status endpoint"""
        self.log("🔗 Testing /integrations endpoint...")
        return self.test_endpoint("GET", "/integrations", expected_status=200)

    def test_metrics_endpoint(self) -> TestResult:
        """Test the metrics endpoint (should require auth)"""
        self.log("📊 Testing /metrics endpoint...")
        return self.test_endpoint("GET", "/metrics", auth_required=True)

    def test_analytics_endpoint(self) -> TestResult:
        """Test the analytics endpoint (should require auth)"""
        self.log("📈 Testing /analytics endpoint...")
        return self.test_endpoint("GET", "/analytics", auth_required=True)

    def test_root_endpoint(self) -> TestResult:
        """Test the root endpoint"""
        self.log("🏠 Testing / (root) endpoint...")
        return self.test_endpoint("GET", "/", expected_status=200)

    async def test_websocket_endpoint(self) -> TestResult:
        """Test WebSocket connectivity"""
        self.log("🔌 Testing WebSocket /ws/collaboration endpoint...")
        start_time = time.time()

        try:
            async with websockets.connect(f"{WS_URL}/ws/collaboration") as websocket:
                # Send a test message
                test_message = {"type": "ping", "data": {"message": "health_check"}}
                await websocket.send(json.dumps(test_message))

                # Wait for response (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    response_time = time.time() - start_time

                    result = TestResult(
                        endpoint="/ws/collaboration",
                        method="WS",
                        status_code=200,
                        response_time=response_time,
                        success=True,
                        response_data=response_data,
                    )

                except asyncio.TimeoutError:
                    response_time = time.time() - start_time
                    result = TestResult(
                        endpoint="/ws/collaboration",
                        method="WS",
                        status_code=0,
                        response_time=response_time,
                        success=False,
                        error_message="WebSocket timeout - no response received",
                    )

        except Exception as e:
            response_time = time.time() - start_time
            result = TestResult(
                endpoint="/ws/collaboration",
                method="WS",
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=f"WebSocket connection failed: {str(e)}",
            )

        self.results.append(result)
        return result

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all endpoint tests and return comprehensive results"""
        self.log("🚀 Starting Comprehensive API Health Check")
        self.log("=" * 60)

        # Run all tests in parallel for better performance
        tasks = [
            self.test_root_endpoint(),
            self.test_health_endpoint(),
            self.test_docs_endpoint(),
            self.test_integrations_endpoint(),
            self.test_register_endpoint(),
            self.test_login_endpoint(),
            self.test_query_endpoint(),
            self.test_metrics_endpoint(),
            self.test_analytics_endpoint(),
            self.test_websocket_endpoint(),
        ]

        # Execute all tests concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive test report"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests

        # Calculate average response time
        response_times = [r.response_time for r in self.results if r.response_time > 0]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        # Group results by category
        public_endpoints = [
            r for r in self.results if not r.auth_required and r.method != "WS"
        ]
        auth_endpoints = [r for r in self.results if r.auth_required]
        websocket_tests = [r for r in self.results if r.method == "WS"]

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (
                    (successful_tests / total_tests * 100) if total_tests > 0 else 0
                ),
                "average_response_time": avg_response_time,
            },
            "endpoint_results": {
                "public_endpoints": [self._result_to_dict(r) for r in public_endpoints],
                "auth_endpoints": [self._result_to_dict(r) for r in auth_endpoints],
                "websocket_tests": [self._result_to_dict(r) for r in websocket_tests],
            },
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _result_to_dict(self, result: TestResult) -> Dict[str, Any]:
        """Convert TestResult to dictionary for JSON serialization"""
        return {
            "endpoint": result.endpoint,
            "method": result.method,
            "status_code": result.status_code,
            "response_time": result.response_time,
            "success": result.success,
            "error_message": result.error_message,
            "auth_required": result.auth_required,
            "auth_success": result.auth_success,
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Check for critical failures
        failed_endpoints = [r for r in self.results if not r.success]
        if failed_endpoints:
            recommendations.append(
                f"⚠️  {len(failed_endpoints)} endpoints failed - review server logs"
            )

        # Check response times
        slow_endpoints = [r for r in self.results if r.response_time > 1.0]
        if slow_endpoints:
            recommendations.append(
                f"🐌 {len(slow_endpoints)} endpoints are slow (>1s) - optimize performance"
            )

        # Check auth flow
        auth_tests = [r for r in self.results if r.auth_required]
        auth_success = [r for r in auth_tests if r.auth_success]
        if len(auth_tests) > 0 and len(auth_success) == 0:
            recommendations.append(
                "🔐 Authentication flow is not working - check auth service"
            )

        # Check WebSocket
        ws_tests = [r for r in self.results if r.method == "WS"]
        if ws_tests and not any(r.success for r in ws_tests):
            recommendations.append(
                "🔌 WebSocket connectivity failed - check WebSocket service"
            )

        if not recommendations:
            recommendations.append(
                "✅ All systems operational - no immediate issues detected"
            )

        return recommendations

    def print_report(self, report: Dict[str, Any]):
        """Print a formatted test report"""
        self.log("📊 COMPREHENSIVE API HEALTH CHECK REPORT")
        self.log("=" * 60)

        # Summary
        summary = report["summary"]
        self.log(f"📈 Test Summary:")
        self.log(f"   Total Tests: {summary['total_tests']}")
        self.log(f"   Successful: {summary['successful_tests']}")
        self.log(f"   Failed: {summary['failed_tests']}")
        self.log(f"   Success Rate: {summary['success_rate']:.1f}%")
        self.log(f"   Avg Response Time: {summary['average_response_time']:.3f}s")

        # Public Endpoints
        self.log(f"\n🌐 Public Endpoints:")
        for result in report["endpoint_results"]["public_endpoints"]:
            status = "✅" if result["success"] else "❌"
            self.log(
                f"   {status} {result['method']} {result['endpoint']} - {result['status_code']} ({result['response_time']:.3f}s)"
            )
            if result["error_message"]:
                self.log(f"      Error: {result['error_message']}")

        # Auth Endpoints
        self.log(f"\n🔐 Authentication Endpoints:")
        for result in report["endpoint_results"]["auth_endpoints"]:
            status = "✅" if result["success"] else "❌"
            auth_status = "🔓" if result["auth_success"] else "🔒"
            self.log(
                f"   {status} {auth_status} {result['method']} {result['endpoint']} - {result['status_code']} ({result['response_time']:.3f}s)"
            )
            if result["error_message"]:
                self.log(f"      Error: {result['error_message']}")

        # WebSocket Tests
        self.log(f"\n🔌 WebSocket Tests:")
        for result in report["endpoint_results"]["websocket_tests"]:
            status = "✅" if result["success"] else "❌"
            self.log(
                f"   {status} {result['method']} {result['endpoint']} - {result['status_code']} ({result['response_time']:.3f}s)"
            )
            if result["error_message"]:
                self.log(f"      Error: {result['error_message']}")

        # Recommendations
        self.log(f"\n💡 Recommendations:")
        for rec in report["recommendations"]:
            self.log(f"   {rec}")

        self.log("=" * 60)
        self.log("🏁 Health Check Complete")


async def main():
    """Main function to run the comprehensive health check"""
    print("🚀 Universal Knowledge Hub - Comprehensive API Health Check")
    print("=" * 70)

    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ Backend server is running and accessible")
            else:
                print(f"⚠️  Backend server responded with status {response.status_code}")
    except httpx.RequestError as e:
        print(f"❌ Cannot connect to backend server at {BASE_URL}")
        print(f"   Error: {e}")
        print("   Please ensure the server is running with:")
        print(
            "   uvicorn services.gateway.main:app --reload --host 0.0.0.0 --port 8004"
        )
        return

    # Run comprehensive health check
    checker = APIHealthChecker()
    report = await checker.run_all_tests()
    checker.print_report(report)

    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"comprehensive_api_health_check_{timestamp}.json"

    try:
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"⚠️  Could not save report file: {e}")


if __name__ == "__main__":
    asyncio.run(main())
