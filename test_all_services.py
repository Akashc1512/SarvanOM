#!/usr/bin/env python3
"""
Comprehensive Integration Test for All SarvanOM Services
Tests all 16 services with real queries to verify functionality
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ServiceTester:
    def __init__(self):
        self.base_urls = {
            "model-registry": "http://localhost:8000",
            "model-router": "http://localhost:8001", 
            "auto-upgrade": "http://localhost:8002",
            "guided-prompt": "http://localhost:8003",
            "retrieval": "http://localhost:8004",
            "feeds": "http://localhost:8005",
            "observability": "http://localhost:8006",
            "gateway": "http://localhost:8007",
            "synthesis": "http://localhost:8008",
            "security": "http://localhost:8009",
            "cicd": "http://localhost:8010",
            "fact-check": "http://localhost:8011",
            "auth": "http://localhost:8012",
            "knowledge-graph": "http://localhost:8013",
            "search": "http://localhost:8014",
            "crud": "http://localhost:8015"
        }
        
        self.results = {}
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_endpoint(self, service_name: str, endpoint: str, method: str = "GET", 
                          data: Optional[Dict] = None, expected_status: int = 200) -> Dict[str, Any]:
        """Test a single endpoint"""
        url = f"{self.base_urls[service_name]}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                async with self.session.get(url) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            elif method == "POST":
                async with self.session.post(url, json=data) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            
            return {
                "status": "success" if response.status == expected_status else "failed",
                "status_code": response.status,
                "response_time": round(response_time, 3),
                "data": response_data,
                "url": url
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": url,
                "response_time": None
            }

    async def test_standard_endpoints(self, service_name: str) -> Dict[str, Any]:
        """Test standard endpoints for a service"""
        print(f"🔍 Testing {service_name} standard endpoints...")
        
        endpoints = [
            ("/health", "GET", 200),
            ("/ready", "GET", 200),
            ("/config", "GET", 200),
            ("/version", "GET", 200),
            ("/metrics", "GET", 200)
        ]
        
        results = {}
        for endpoint, method, expected_status in endpoints:
            result = await self.test_endpoint(service_name, endpoint, method, expected_status=expected_status)
            results[endpoint] = result
            
        return results

    async def test_service_specific_endpoints(self, service_name: str) -> Dict[str, Any]:
        """Test service-specific endpoints"""
        print(f"🎯 Testing {service_name} specific endpoints...")
        
        service_tests = {
            "model-registry": [
                ("/api/v1/models", "GET", 200),
                ("/api/v1/providers", "GET", 200),
                ("/api/v1/route", "POST", 200, {"query": "What is machine learning?", "context": "technical"}),
                ("/api/v1/refine", "POST", 200, {"query": "Tell me about AI", "constraints": {"time": 500}}),
                ("/api/v1/search", "POST", 200, {"query": "artificial intelligence", "lanes": ["web", "news"]}),
                ("/api/v1/news", "GET", 200),
                ("/api/v1/markets", "GET", 200)
            ],
            "model-router": [
                ("/route", "POST", 200, {"query": "What is Python?", "context": "programming"}),
                ("/models", "GET", 200)
            ],
            "auto-upgrade": [
                ("/scan", "POST", 200, {"provider": "openai"}),
                ("/evaluate", "POST", 200, {"model": "gpt-4", "task": "text-generation"})
            ],
            "guided-prompt": [
                ("/refine", "POST", 200, {"query": "Explain quantum computing", "constraints": {"time": 300}}),
                ("/analyze", "POST", 200, {"query": "What are the benefits of renewable energy?"})
            ],
            "retrieval": [
                ("/search", "POST", 200, {"query": "machine learning algorithms", "sources": ["web", "academic"]}),
                ("/retrieve", "POST", 200, {"query": "artificial intelligence", "limit": 10})
            ],
            "feeds": [
                ("/news", "GET", 200),
                ("/markets", "GET", 200),
                ("/feeds/providers", "GET", 200)
            ],
            "observability": [
                ("/metrics", "GET", 200),
                ("/health/detailed", "GET", 200),
                ("/traces", "GET", 200)
            ],
            "gateway": [
                ("/query", "POST", 200, {"query": "What is the weather today?", "context": "general"}),
                ("/analyze", "POST", 200, {"query": "Explain blockchain technology"})
            ],
            "synthesis": [
                ("/synthesize", "POST", 200, {"query": "Summarize the benefits of renewable energy", "sources": ["web", "academic"]}),
                ("/summarize", "POST", 200, {"content": "This is a test document about artificial intelligence and machine learning."})
            ],
            "security": [
                ("/scan", "POST", 200, {"content": "This is a test document for security scanning."}),
                ("/validate", "POST", 200, {"input": "test input for validation"})
            ],
            "cicd": [
                ("/gates/check", "POST", 200, {"check_types": ["lint", "type_check"]}),
                ("/deployments", "GET", 200),
                ("/gates/thresholds", "GET", 200)
            ],
            "fact-check": [
                ("/verify", "POST", 200, {"claim": "The Earth is round", "context": "scientific"}),
                ("/analyze", "POST", 200, {"text": "This is a test claim for fact-checking."})
            ],
            "auth": [
                ("/login", "POST", 200, {"username": "test", "password": "test"}),
                ("/register", "POST", 200, {"username": "testuser", "email": "test@example.com", "password": "testpass"})
            ],
            "knowledge-graph": [
                ("/query", "POST", 200, {"query": "What is the relationship between AI and ML?", "query_type": "entity_relationship"}),
                ("/add-entity", "POST", 200, {"name": "Test Entity", "type": "concept", "properties": {"description": "A test entity"}})
            ],
            "search": [
                ("/", "POST", 200, {"query": "artificial intelligence", "context": "technical"}),
                ("/comprehensive", "POST", 200, {"query": "machine learning applications", "sources": ["web", "academic", "news"]})
            ],
            "crud": [
                ("/cache", "POST", 200, {"key": "test_key", "value": "test_value", "ttl": 3600}),
                ("/cache/test_key", "GET", 200),
                ("/users", "POST", 200, {"username": "testuser", "email": "test@example.com"}),
                ("/models", "POST", 200, {"name": "test-model", "provider": "openai", "version": "1.0"})
            ]
        }
        
        if service_name not in service_tests:
            return {"message": "No specific tests defined for this service"}
        
        results = {}
        for test in service_tests[service_name]:
            if len(test) == 3:
                endpoint, method, expected_status = test
                data = None
            else:
                endpoint, method, expected_status, data = test
                
            result = await self.test_endpoint(service_name, endpoint, method, data, expected_status)
            results[endpoint] = result
            
        return results

    async def test_service(self, service_name: str) -> Dict[str, Any]:
        """Test a complete service"""
        print(f"\n🚀 Testing {service_name}...")
        print("=" * 50)
        
        # Test standard endpoints
        standard_results = await self.test_standard_endpoints(service_name)
        
        # Test service-specific endpoints
        specific_results = await self.test_service_specific_endpoints(service_name)
        
        # Calculate overall health
        all_results = {**standard_results, **specific_results}
        success_count = sum(1 for r in all_results.values() if r.get("status") == "success")
        total_count = len(all_results)
        health_percentage = (success_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "service": service_name,
            "health_percentage": round(health_percentage, 1),
            "success_count": success_count,
            "total_count": total_count,
            "standard_endpoints": standard_results,
            "specific_endpoints": specific_results,
            "overall_status": "healthy" if health_percentage >= 80 else "degraded" if health_percentage >= 50 else "unhealthy"
        }

    async def test_all_services(self) -> Dict[str, Any]:
        """Test all services"""
        print("🎯 Starting Comprehensive Service Testing")
        print("=" * 60)
        print(f"Testing {len(self.base_urls)} services...")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        results = {}
        overall_start_time = time.time()
        
        for service_name in self.base_urls.keys():
            try:
                result = await self.test_service(service_name)
                results[service_name] = result
            except Exception as e:
                results[service_name] = {
                    "service": service_name,
                    "health_percentage": 0,
                    "success_count": 0,
                    "total_count": 0,
                    "overall_status": "error",
                    "error": str(e)
                }
        
        overall_time = time.time() - overall_start_time
        
        # Calculate overall statistics
        total_services = len(results)
        healthy_services = sum(1 for r in results.values() if r.get("overall_status") == "healthy")
        degraded_services = sum(1 for r in results.values() if r.get("overall_status") == "degraded")
        unhealthy_services = sum(1 for r in results.values() if r.get("overall_status") in ["unhealthy", "error"])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_test_time": round(overall_time, 2),
            "summary": {
                "total_services": total_services,
                "healthy_services": healthy_services,
                "degraded_services": degraded_services,
                "unhealthy_services": unhealthy_services,
                "overall_health_percentage": round((healthy_services / total_services * 100), 1)
            },
            "services": results
        }

    def print_results(self, results: Dict[str, Any]):
        """Print test results in a formatted way"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE SERVICE TEST RESULTS")
        print("=" * 80)
        
        summary = results["summary"]
        print(f"📊 Overall Health: {summary['overall_health_percentage']}%")
        print(f"✅ Healthy Services: {summary['healthy_services']}/{summary['total_services']}")
        print(f"⚠️  Degraded Services: {summary['degraded_services']}")
        print(f"❌ Unhealthy Services: {summary['unhealthy_services']}")
        print(f"⏱️  Total Test Time: {results['total_test_time']}s")
        
        print("\n" + "=" * 80)
        print("📋 DETAILED SERVICE RESULTS")
        print("=" * 80)
        
        for service_name, result in results["services"].items():
            status_emoji = {
                "healthy": "✅",
                "degraded": "⚠️",
                "unhealthy": "❌",
                "error": "💥"
            }.get(result.get("overall_status", "unknown"), "❓")
            
            print(f"\n{status_emoji} {service_name.upper()}")
            print(f"   Health: {result.get('health_percentage', 0)}%")
            print(f"   Status: {result.get('overall_status', 'unknown')}")
            print(f"   Success: {result.get('success_count', 0)}/{result.get('total_count', 0)}")
            
            # Show failed endpoints
            if result.get("standard_endpoints"):
                failed_standard = [ep for ep, res in result["standard_endpoints"].items() 
                                 if res.get("status") != "success"]
                if failed_standard:
                    print(f"   Failed Standard Endpoints: {', '.join(failed_standard)}")
            
            if result.get("specific_endpoints"):
                failed_specific = [ep for ep, res in result["specific_endpoints"].items() 
                                 if res.get("status") != "success"]
                if failed_specific:
                    print(f"   Failed Specific Endpoints: {', '.join(failed_specific)}")
            
            if result.get("error"):
                print(f"   Error: {result['error']}")

async def main():
    """Main test function"""
    async with ServiceTester() as tester:
        results = await tester.test_all_services()
        tester.print_results(results)
        
        # Save results to file
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to test_results.json")
        
        # Return exit code based on overall health
        overall_health = results["summary"]["overall_health_percentage"]
        if overall_health >= 80:
            print("🎉 All services are healthy!")
            return 0
        elif overall_health >= 50:
            print("⚠️ Some services are degraded")
            return 1
        else:
            print("❌ Many services are unhealthy")
            return 2

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
