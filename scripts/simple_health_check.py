#!/usr/bin/env python3
"""
Simple Health Check for Universal Knowledge Hub API Gateway

This script performs a basic health check on the API Gateway without complex dependencies.
It tests core connectivity and basic functionality.

Usage:
    python scripts/simple_health_check.py [--base-url BASE_URL]

Author: Universal Knowledge Platform Engineering Team
Version: 1.0.0
"""

import asyncio
import aiohttp
import json
import time
import sys
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class HealthTestResult:
    """Result of a health test."""

    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error: Optional[str] = None
    response_data: Optional[Dict] = None


class SimpleHealthChecker:
    """Simple health checker for the API Gateway."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = None
        self.results: List[HealthTestResult] = []

    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": "Simple-Health-Check/1.0.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def test_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> HealthTestResult:
        """Test a single endpoint."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response_time = time.time() - start_time
                    try:
                        response_data = (
                            await response.json()
                            if response.headers.get("content-type", "").startswith(
                                "application/json"
                            )
                            else None
                        )
                    except:
                        response_data = None

                    return HealthTestResult(
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status,
                        response_time=response_time,
                        success=200 <= response.status < 300,
                        response_data=response_data,
                    )
            elif method.upper() == "POST":
                async with self.session.post(
                    url, json=data, headers=headers
                ) as response:
                    response_time = time.time() - start_time
                    try:
                        response_data = (
                            await response.json()
                            if response.headers.get("content-type", "").startswith(
                                "application/json"
                            )
                            else None
                        )
                    except:
                        response_data = None

                    return HealthTestResult(
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status,
                        response_time=response_time,
                        success=200 <= response.status < 300,
                        response_data=response_data,
                    )
        except Exception as e:
            response_time = time.time() - start_time
            return HealthTestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e),
            )

    async def test_basic_endpoints(self) -> List[HealthTestResult]:
        """Test basic endpoints that don't require authentication."""
        logger.info("Testing basic endpoints...")

        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/docs", "GET"),
            ("/openapi.json", "GET"),
        ]

        tasks = []
        for endpoint, method in endpoints:
            tasks.append(self.test_endpoint(endpoint, method))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and add to results
        for result in results:
            if isinstance(result, HealthTestResult):
                self.results.append(result)
            else:
                logger.error(f"Exception during endpoint test: {result}")

        return [r for r in results if isinstance(r, HealthTestResult)]

    async def test_auth_endpoints(self) -> List[HealthTestResult]:
        """Test authentication endpoints."""
        logger.info("Testing authentication endpoints...")

        # Test login with test credentials
        login_data = {"username": "test_user", "password": "test_password"}

        login_result = await self.test_endpoint("/auth/login", "POST", login_data)
        self.results.append(login_result)

        return [login_result]

    async def test_query_endpoints(self) -> List[HealthTestResult]:
        """Test query processing endpoints."""
        logger.info("Testing query endpoints...")

        # Test query endpoint without authentication
        query_data = {
            "query": "What is artificial intelligence?",
            "context": "health_check_test",
            "max_tokens": 100,
        }

        query_result = await self.test_endpoint("/query", "POST", query_data)
        self.results.append(query_result)

        return [query_result]

    def generate_report(self) -> Dict[str, Any]:
        """Generate health check report."""
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - successful_tests

        # Find slow responses (>300ms)
        slow_responses = [r for r in self.results if r.response_time > 0.3]

        # Group results by endpoint type
        basic_endpoints = [
            r
            for r in self.results
            if r.endpoint in ["/", "/health", "/docs", "/openapi.json"]
        ]
        auth_endpoints = [r for r in self.results if "auth" in r.endpoint]
        query_endpoints = [r for r in self.results if "query" in r.endpoint]

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (
                    (successful_tests / total_tests * 100) if total_tests > 0 else 0
                ),
                "slow_responses": len(slow_responses),
            },
            "endpoint_results": {
                "basic_endpoints": [self._result_to_dict(r) for r in basic_endpoints],
                "auth_endpoints": [self._result_to_dict(r) for r in auth_endpoints],
                "query_endpoints": [self._result_to_dict(r) for r in query_endpoints],
            },
            "slow_responses": [self._result_to_dict(r) for r in slow_responses],
            "failed_tests": [
                self._result_to_dict(r) for r in self.results if not r.success
            ],
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _result_to_dict(self, result: HealthTestResult) -> Dict[str, Any]:
        """Convert HealthTestResult to dictionary."""
        return {
            "endpoint": result.endpoint,
            "method": result.method,
            "status_code": result.status_code,
            "response_time": round(result.response_time, 3),
            "success": result.success,
            "error": result.error,
            "response_data": result.response_data,
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Check for failed tests
        failed_tests = [r for r in self.results if not r.success]
        if failed_tests:
            recommendations.append(f"Fix {len(failed_tests)} failed endpoint tests")

        # Check for slow responses
        slow_responses = [r for r in self.results if r.response_time > 0.3]
        if slow_responses:
            recommendations.append(
                f"Optimize {len(slow_responses)} slow endpoints (>300ms)"
            )

        # Check if API Gateway is not running
        connection_errors = [
            r
            for r in self.results
            if "refused" in str(r.error).lower() or "connect" in str(r.error).lower()
        ]
        if connection_errors:
            recommendations.append("Start the API Gateway service")

        if not recommendations:
            recommendations.append("All systems are healthy and performing well!")

        return recommendations

    async def run_health_check(self) -> Dict[str, Any]:
        """Run the complete health check."""
        logger.info("Starting simple health check...")

        # Run all tests
        await self.test_basic_endpoints()
        await self.test_auth_endpoints()
        await self.test_query_endpoints()

        # Generate report
        report = self.generate_report()

        logger.info("Simple health check completed!")
        return report


def print_report(report: Dict[str, Any]):
    """Print a formatted health check report."""
    print("\n" + "=" * 80)
    print("UNIVERSAL KNOWLEDGE HUB - SIMPLE HEALTH CHECK REPORT")
    print("=" * 80)

    # Summary
    summary = report["summary"]
    print(f"\n📊 SUMMARY")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Successful: {summary['successful_tests']}")
    print(f"   Failed: {summary['failed_tests']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Slow Responses (>300ms): {summary['slow_responses']}")

    # Failed tests
    failed_tests = report["failed_tests"]
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)})")
        for test in failed_tests:
            print(
                f"   {test['method']} {test['endpoint']} - {test['status_code']} ({test['response_time']}s)"
            )
            if test["error"]:
                print(f"      Error: {test['error']}")

    # Slow responses
    slow_responses = report["slow_responses"]
    if slow_responses:
        print(f"\n🐌 SLOW RESPONSES (>300ms)")
        for test in slow_responses:
            print(f"   {test['method']} {test['endpoint']} - {test['response_time']}s")

    # Successful tests
    successful_tests = [
        r
        for r in report["endpoint_results"]["basic_endpoints"]
        + report["endpoint_results"]["auth_endpoints"]
        + report["endpoint_results"]["query_endpoints"]
        if r["success"]
    ]

    if successful_tests:
        print(f"\n✅ SUCCESSFUL TESTS ({len(successful_tests)})")
        for test in successful_tests:
            print(
                f"   {test['method']} {test['endpoint']} - {test['status_code']} ({test['response_time']}s)"
            )

    # Recommendations
    recommendations = report["recommendations"]
    print(f"\n💡 RECOMMENDATIONS")
    for rec in recommendations:
        print(f"   • {rec}")

    print("\n" + "=" * 80)


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Simple Health Check for API Gateway")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the API Gateway",
    )
    parser.add_argument(
        "--timeout", type=int, default=10, help="Request timeout in seconds"
    )
    parser.add_argument("--output", help="Output file for JSON report")

    args = parser.parse_args()

    try:
        async with SimpleHealthChecker(args.base_url, args.timeout) as checker:
            report = await checker.run_health_check()

            # Print formatted report
            print_report(report)

            # Save JSON report if requested
            if args.output:
                with open(args.output, "w") as f:
                    json.dump(report, f, indent=2)
                print(f"\n📄 JSON report saved to: {args.output}")

            # Exit with error code if there are failures
            if report["summary"]["failed_tests"] > 0:
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Health check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
