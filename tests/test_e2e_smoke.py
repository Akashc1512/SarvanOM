#!/usr/bin/env python3
"""
End-to-End Smoke Test - Phase H1
================================

Comprehensive smoke test that validates the complete end-to-end flow:
- Query → Retrieval → Synthesis → Citations → Response
- Performance budget validation 
- Real API integration verification
- Complete system health validation

Maps to Phase H1 requirements for production deployment verification.
"""

import asyncio
import aiohttp
import time
import json
import os
from typing import Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class SmokeTestResult:
    """Individual smoke test result."""
    test_name: str
    success: bool
    response_time_ms: float
    details: Dict[str, Any]
    error: str = ""

class EndToEndSmokeTest:
    """
    Comprehensive end-to-end smoke testing for production deployment.
    
    Validates complete query processing pipeline with real performance budgets.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize smoke tester."""
        self.base_url = base_url.rstrip('/')
        self.results: List[SmokeTestResult] = []
        
        # Test queries representing real user scenarios
        self.test_queries = [
            "What is machine learning and how does it work?",
            "How to implement authentication in a web application?",
            "What are the benefits of renewable energy sources?"
        ]
        
        # Performance budgets (as per Phase H1 requirements)
        self.budgets = {
            'e2e_budget_ms': 3000,      # E2E ≤3s
            'vector_budget_ms': 2000,   # Vector ≤2s (after warmup)
            'kg_budget_ms': 1500        # KG ≤1.5s
        }
    
    async def test_system_health_pre_check(self) -> SmokeTestResult:
        """Test system health before running end-to-end tests."""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status != 200:
                        return SmokeTestResult(
                            test_name="system_health_pre_check",
                            success=False,
                            response_time_ms=response_time_ms,
                            details={},
                            error=f"Health check failed with status {response.status}"
                        )
                    
                    health_data = await response.json()
                    
                    # Check required services
                    required_services = ['vector', 'arangodb']
                    missing_services = []
                    
                    for service in required_services:
                        if service not in health_data or health_data[service] != "ok":
                            missing_services.append(service)
                    
                    success = len(missing_services) == 0
                    
                    return SmokeTestResult(
                        test_name="system_health_pre_check",
                        success=success,
                        response_time_ms=response_time_ms,
                        details={
                            'health_data': health_data,
                            'missing_services': missing_services,
                            'all_services_healthy': success
                        },
                        error="" if success else f"Missing healthy services: {missing_services}"
                    )
        
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return SmokeTestResult(
                test_name="system_health_pre_check",
                success=False,
                response_time_ms=response_time_ms,
                details={},
                error=str(e)
            )
    
    async def test_search_endpoint_budget(self, query: str) -> SmokeTestResult:
        """Test search endpoint with performance budget validation."""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {"q": query, "limit": 6}
                async with session.get(f"{self.base_url}/search", params=params) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status != 200:
                        return SmokeTestResult(
                            test_name=f"search_budget_{query[:20]}",
                            success=False,
                            response_time_ms=response_time_ms,
                            details={},
                            error=f"Search failed with status {response.status}"
                        )
                    
                    search_data = await response.json()
                    
                    # Validate response structure
                    required_fields = ['query', 'results', 'total_results', 'search_time_ms']
                    missing_fields = [field for field in required_fields if field not in search_data]
                    
                    # Validate performance budget
                    within_budget = response_time_ms <= self.budgets['e2e_budget_ms']
                    
                    # Validate minimum results (≥6 sources as per requirements)
                    min_results_met = search_data.get('total_results', 0) >= 6
                    
                    success = (
                        len(missing_fields) == 0 and 
                        within_budget and 
                        min_results_met and 
                        search_data.get('status') == 'success'
                    )
                    
                    return SmokeTestResult(
                        test_name=f"search_budget_{query[:20]}",
                        success=success,
                        response_time_ms=response_time_ms,
                        details={
                            'search_data': search_data,
                            'missing_fields': missing_fields,
                            'within_budget': within_budget,
                            'min_results_met': min_results_met,
                            'budget_ms': self.budgets['e2e_budget_ms'],
                            'actual_results': search_data.get('total_results', 0)
                        },
                        error="" if success else f"Budget/structure validation failed"
                    )
        
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return SmokeTestResult(
                test_name=f"search_budget_{query[:20]}",
                success=False,
                response_time_ms=response_time_ms,
                details={},
                error=str(e)
            )
    
    async def test_complete_query_processing(self, query: str) -> SmokeTestResult:
        """Test complete query processing with citations."""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"query": query}
                async with session.post(f"{self.base_url}/query", json=payload) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status != 200:
                        return SmokeTestResult(
                            test_name=f"complete_query_{query[:20]}",
                            success=False,
                            response_time_ms=response_time_ms,
                            details={},
                            error=f"Query processing failed with status {response.status}"
                        )
                    
                    query_data = await response.json()
                    
                    # Validate complete processing chain
                    required_fields = ['query', 'success', 'total_time_ms', 'lane_results']
                    missing_fields = [field for field in required_fields if field not in query_data]
                    
                    # Validate lane execution
                    lane_results = query_data.get('lane_results', {})
                    expected_lanes = ['retrieval', 'vector', 'knowledge_graph', 'llm_synthesis']
                    executed_lanes = list(lane_results.keys())
                    missing_lanes = [lane for lane in expected_lanes if lane not in executed_lanes]
                    
                    # Validate performance budget
                    within_budget = response_time_ms <= self.budgets['e2e_budget_ms']
                    
                    # Validate success
                    query_success = query_data.get('success', False)
                    
                    # Check for final answer
                    has_final_answer = query_data.get('final_answer') is not None
                    
                    success = (
                        len(missing_fields) == 0 and
                        len(missing_lanes) == 0 and
                        within_budget and
                        query_success and
                        has_final_answer
                    )
                    
                    return SmokeTestResult(
                        test_name=f"complete_query_{query[:20]}",
                        success=success,
                        response_time_ms=response_time_ms,
                        details={
                            'query_data': query_data,
                            'missing_fields': missing_fields,
                            'missing_lanes': missing_lanes,
                            'executed_lanes': executed_lanes,
                            'within_budget': within_budget,
                            'query_success': query_success,
                            'has_final_answer': has_final_answer,
                            'budget_ms': self.budgets['e2e_budget_ms']
                        },
                        error="" if success else "Complete query validation failed"
                    )
        
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return SmokeTestResult(
                test_name=f"complete_query_{query[:20]}",
                success=False,
                response_time_ms=response_time_ms,
                details={},
                error=str(e)
            )
    
    async def test_citations_processing(self) -> SmokeTestResult:
        """Test citations processing functionality."""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                test_text = "Machine learning is a subset of artificial intelligence. It involves training algorithms on data to make predictions."
                test_sources = [
                    {"title": "ML Guide", "url": "https://example.com/ml", "content": "Machine learning overview"},
                    {"title": "AI Handbook", "url": "https://example.com/ai", "content": "Artificial intelligence concepts"}
                ]
                
                payload = {
                    "text": test_text,
                    "sources": test_sources
                }
                
                async with session.post(f"{self.base_url}/citations/process", json=payload) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status != 200:
                        return SmokeTestResult(
                            test_name="citations_processing",
                            success=False,
                            response_time_ms=response_time_ms,
                            details={},
                            error=f"Citations processing failed with status {response.status}"
                        )
                    
                    citation_data = await response.json()
                    
                    # Validate citations structure
                    required_fields = ['text', 'cited_text', 'claims', 'citations', 'status']
                    missing_fields = [field for field in required_fields if field not in citation_data]
                    
                    # Validate processing success
                    processing_success = citation_data.get('status') == 'success'
                    
                    # Validate citations present
                    has_citations = len(citation_data.get('citations', [])) > 0
                    
                    # Validate performance (citations budget)
                    citations_budget = 2000  # 2s for citations processing
                    within_budget = response_time_ms <= citations_budget
                    
                    success = (
                        len(missing_fields) == 0 and
                        processing_success and
                        has_citations and
                        within_budget
                    )
                    
                    return SmokeTestResult(
                        test_name="citations_processing",
                        success=success,
                        response_time_ms=response_time_ms,
                        details={
                            'citation_data': citation_data,
                            'missing_fields': missing_fields,
                            'processing_success': processing_success,
                            'has_citations': has_citations,
                            'within_budget': within_budget,
                            'budget_ms': citations_budget
                        },
                        error="" if success else "Citations validation failed"
                    )
        
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return SmokeTestResult(
                test_name="citations_processing",
                success=False,
                response_time_ms=response_time_ms,
                details={},
                error=str(e)
            )
    
    async def test_performance_metrics_availability(self) -> SmokeTestResult:
        """Test that performance metrics are available and functional."""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test multiple metrics endpoints
                endpoints = [
                    "/metrics/performance",
                    "/metrics/vector", 
                    "/metrics/lanes",
                    "/metrics/router"
                ]
                
                all_success = True
                endpoint_results = {}
                
                for endpoint in endpoints:
                    try:
                        async with session.get(f"{self.base_url}{endpoint}") as response:
                            if response.status == 200:
                                data = await response.json()
                                endpoint_results[endpoint] = {
                                    'status': 'success',
                                    'has_data': len(data) > 0
                                }
                            else:
                                endpoint_results[endpoint] = {
                                    'status': 'failed',
                                    'status_code': response.status
                                }
                                all_success = False
                    except Exception as e:
                        endpoint_results[endpoint] = {
                            'status': 'error',
                            'error': str(e)
                        }
                        all_success = False
                
                response_time_ms = (time.time() - start_time) * 1000
                
                return SmokeTestResult(
                    test_name="performance_metrics_availability",
                    success=all_success,
                    response_time_ms=response_time_ms,
                    details={
                        'endpoint_results': endpoint_results,
                        'all_endpoints_healthy': all_success
                    },
                    error="" if all_success else "Some metrics endpoints failed"
                )
        
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return SmokeTestResult(
                test_name="performance_metrics_availability",
                success=False,
                response_time_ms=response_time_ms,
                details={},
                error=str(e)
            )
    
    async def run_complete_smoke_test(self) -> Dict[str, Any]:
        """Run complete end-to-end smoke test suite."""
        print("🧪 Starting End-to-End Smoke Test Suite")
        print("=" * 50)
        
        # Pre-check: System health
        print("1. System health pre-check...")
        health_result = await self.test_system_health_pre_check()
        self.results.append(health_result)
        
        if not health_result.success:
            print(f"   ❌ Health check failed: {health_result.error}")
            print("   Stopping smoke test - system not ready")
            return self._generate_report()
        else:
            print(f"   ✅ System healthy ({health_result.response_time_ms:.0f}ms)")
        
        # Test search endpoints with all test queries
        print("\n2. Search endpoint budget validation...")
        for i, query in enumerate(self.test_queries, 1):
            print(f"   Testing query {i}: {query[:30]}...")
            search_result = await self.test_search_endpoint_budget(query)
            self.results.append(search_result)
            
            if search_result.success:
                print(f"   ✅ Search passed ({search_result.response_time_ms:.0f}ms)")
            else:
                print(f"   ❌ Search failed: {search_result.error}")
        
        # Test complete query processing
        print("\n3. Complete query processing validation...")
        for i, query in enumerate(self.test_queries, 1):
            print(f"   Testing complete processing {i}: {query[:30]}...")
            query_result = await self.test_complete_query_processing(query)
            self.results.append(query_result)
            
            if query_result.success:
                print(f"   ✅ Complete query passed ({query_result.response_time_ms:.0f}ms)")
            else:
                print(f"   ❌ Complete query failed: {query_result.error}")
        
        # Test citations processing
        print("\n4. Citations processing validation...")
        citations_result = await self.test_citations_processing()
        self.results.append(citations_result)
        
        if citations_result.success:
            print(f"   ✅ Citations passed ({citations_result.response_time_ms:.0f}ms)")
        else:
            print(f"   ❌ Citations failed: {citations_result.error}")
        
        # Test metrics availability
        print("\n5. Performance metrics validation...")
        metrics_result = await self.test_performance_metrics_availability()
        self.results.append(metrics_result)
        
        if metrics_result.success:
            print(f"   ✅ Metrics available ({metrics_result.response_time_ms:.0f}ms)")
        else:
            print(f"   ❌ Metrics failed: {metrics_result.error}")
        
        return self._generate_report()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive smoke test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        # Performance analysis
        response_times = [r.response_time_ms for r in self.results if r.success]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # Budget compliance
        budget_violations = [
            r for r in self.results 
            if r.success and r.response_time_ms > self.budgets['e2e_budget_ms']
        ]
        
        # Overall assessment
        deployment_ready = (
            success_rate >= 0.90 and  # 90%+ success rate
            len(budget_violations) == 0 and  # No budget violations
            passed_tests >= 7  # Minimum test coverage
        )
        
        return {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': round(success_rate, 3)
            },
            'performance_analysis': {
                'avg_response_time_ms': round(avg_response_time, 2),
                'max_response_time_ms': round(max_response_time, 2),
                'budget_violations': len(budget_violations),
                'e2e_budget_ms': self.budgets['e2e_budget_ms']
            },
            'deployment_readiness': {
                'ready_for_deployment': deployment_ready,
                'recommendation': 'DEPLOY' if deployment_ready else 'FIX_ISSUES',
                'critical_issues': [r.error for r in self.results if not r.success]
            },
            'detailed_results': [
                {
                    'test_name': r.test_name,
                    'success': r.success,
                    'response_time_ms': round(r.response_time_ms, 2),
                    'error': r.error,
                    'key_metrics': {
                        k: v for k, v in r.details.items() 
                        if k in ['within_budget', 'query_success', 'all_services_healthy']
                    }
                }
                for r in self.results
            ]
        }

async def main():
    """Run comprehensive end-to-end smoke test."""
    print("🚀 SarvanOM End-to-End Smoke Test")
    print("Phase H1: Complete Production Validation")
    print()
    
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status != 200:
                    print("❌ Server not responding. Please start the server first:")
                    print("   uvicorn services.gateway.main:app --reload")
                    return
    except:
        print("❌ Server not running. Please start the server first:")
        print("   uvicorn services.gateway.main:app --reload")
        return
    
    # Run smoke tests
    tester = EndToEndSmokeTest()
    report = await tester.run_complete_smoke_test()
    
    # Print final report
    print("\n" + "=" * 60)
    print("🎯 SMOKE TEST REPORT")
    print("=" * 60)
    
    summary = report['test_summary']
    performance = report['performance_analysis']
    deployment = report['deployment_readiness']
    
    print(f"Tests Run: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']} | Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['success_rate']:.1%}")
    print(f"Avg Response Time: {performance['avg_response_time_ms']:.0f}ms")
    print(f"Max Response Time: {performance['max_response_time_ms']:.0f}ms")
    print(f"Budget Violations: {performance['budget_violations']}")
    print()
    print(f"🎯 Deployment Ready: {deployment['ready_for_deployment']}")
    print(f"Recommendation: {deployment['recommendation']}")
    
    if deployment['critical_issues']:
        print("\n🚨 Critical Issues:")
        for issue in deployment['critical_issues']:
            print(f"   • {issue}")
    
    print("\n🏆 Phase H1: End-to-End Smoke Test COMPLETE!")

if __name__ == "__main__":
    asyncio.run(main())
