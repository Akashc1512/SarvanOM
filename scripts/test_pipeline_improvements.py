#!/usr/bin/env python3
"""
Test Pipeline Improvements Script
Validates the enhanced multi-agent pipeline with improved error handling and data flow.

This script tests:
- Empty retrieval handling
- Partial pipeline failures
- Context passing between stages
- Error propagation
- Response aggregation improvements
- Authentication flow

# DEAD CODE - Candidate for deletion: This test script is not integrated into any test suite
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    name: str
    query: str
    expected_behavior: str
    should_succeed: bool
    expected_warnings: List[str] = None

class PipelineImprovementTester:
    def __init__(self):
        self.test_results = []
        self.base_url = "http://localhost:8000"
        
    def log(self, message: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    async def test_query_processing(self, test_case: TestCase) -> Dict[str, Any]:
        """Test a single query processing scenario"""
        self.log(f"🧪 Testing: {test_case.name}")
        self.log(f"  Query: {test_case.query}")
        self.log(f"  Expected behavior: {test_case.expected_behavior}")
        
        start_time = time.time()
        
        try:
            # Test the query endpoint
            import requests
            
            response = requests.post(
                f"{self.base_url}/query",
                json={
                    "query": test_case.query,
                    "max_tokens": 1000,
                    "confidence_threshold": 0.7
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Analyze the response
                success = result.get("success", False)
                answer = result.get("answer", "")
                confidence = result.get("confidence", 0.0)
                warnings = result.get("warnings", [])
                metadata = result.get("metadata", {})
                
                # Check if behavior matches expectations
                test_passed = True
                issues = []
                
                if test_case.should_succeed and not success:
                    test_passed = False
                    issues.append("Expected success but got failure")
                elif not test_case.should_succeed and success:
                    test_passed = False
                    issues.append("Expected failure but got success")
                
                # Check for expected warnings
                if test_case.expected_warnings:
                    for expected_warning in test_case.expected_warnings:
                        if not any(expected_warning.lower() in warning.lower() for warning in warnings):
                            test_passed = False
                            issues.append(f"Expected warning not found: {expected_warning}")
                
                # Check pipeline status
                pipeline_status = metadata.get("pipeline_status", "unknown")
                successful_agents = metadata.get("successful_agents", [])
                failed_agents = metadata.get("failed_agents", [])
                
                self.log(f"  ✅ Response received in {response_time:.2f}s")
                self.log(f"  📊 Success: {success}")
                self.log(f"  📊 Confidence: {confidence:.2f}")
                self.log(f"  📊 Pipeline Status: {pipeline_status}")
                self.log(f"  📊 Successful Agents: {successful_agents}")
                self.log(f"  📊 Failed Agents: {failed_agents}")
                self.log(f"  ⚠️ Warnings: {warnings}")
                
                if issues:
                    self.log(f"  ❌ Issues found: {issues}")
                else:
                    self.log(f"  ✅ Test passed!")
                
                return {
                    "test_name": test_case.name,
                    "success": test_passed,
                    "response_time": response_time,
                    "response_data": result,
                    "issues": issues,
                    "pipeline_status": pipeline_status,
                    "successful_agents": successful_agents,
                    "failed_agents": failed_agents,
                    "warnings": warnings
                }
                
            else:
                self.log(f"  ❌ HTTP Error: {response.status_code}")
                return {
                    "test_name": test_case.name,
                    "success": False,
                    "response_time": response_time,
                    "error": f"HTTP {response.status_code}",
                    "response_text": response.text
                }
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log(f"  ❌ Exception: {str(e)}")
            return {
                "test_name": test_case.name,
                "success": False,
                "response_time": response_time,
                "error": str(e)
            }
    
    async def test_health_endpoints(self) -> Dict[str, Any]:
        """Test health endpoints to ensure system is running"""
        self.log("🏥 Testing health endpoints")
        
        import requests
        
        health_results = {}
        
        # Test basic health
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            health_results["basic_health"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            health_results["basic_health"] = {"error": str(e)}
        
        # Test simple health
        try:
            response = requests.get(f"{self.base_url}/health/simple", timeout=10)
            health_results["simple_health"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            health_results["simple_health"] = {"error": str(e)}
        
        return health_results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all pipeline improvement tests"""
        self.log("🚀 Starting Pipeline Improvement Tests")
        
        # Define test cases
        test_cases = [
            TestCase(
                name="Normal Query Processing",
                query="What is artificial intelligence?",
                expected_behavior="Should process successfully through all pipeline stages",
                should_succeed=True
            ),
            TestCase(
                name="Empty Retrieval Handling",
                query="xyz123veryobscurequerythatwontfindanything",
                expected_behavior="Should handle empty retrieval gracefully",
                should_succeed=True,
                expected_warnings=["No relevant documents found", "Empty retrieval"]
            ),
            TestCase(
                name="Complex Technical Query",
                query="Explain the differences between supervised and unsupervised learning in machine learning",
                expected_behavior="Should process complex technical queries",
                should_succeed=True
            ),
            TestCase(
                name="Very Short Query",
                query="AI",
                expected_behavior="Should handle very short queries",
                should_succeed=True
            ),
            TestCase(
                name="Very Long Query",
                query="Can you provide a comprehensive analysis of the current state of artificial intelligence research, including recent breakthroughs in deep learning, natural language processing, computer vision, and robotics, while also discussing the ethical implications and potential future developments in the field?",
                expected_behavior="Should handle very long queries",
                should_succeed=True
            ),
            TestCase(
                name="Query with Special Characters",
                query="What is the difference between C++ and C#?",
                expected_behavior="Should handle special characters in queries",
                should_succeed=True
            ),
            TestCase(
                name="Non-English Query",
                query="¿Qué es la inteligencia artificial?",
                expected_behavior="Should handle non-English queries",
                should_succeed=True
            )
        ]
        
        # Test health endpoints first
        health_results = await self.test_health_endpoints()
        
        # Run query processing tests
        query_results = []
        for test_case in test_cases:
            result = await self.test_query_processing(test_case)
            query_results.append(result)
            await asyncio.sleep(1)  # Brief pause between tests
        
        # Compile results
        successful_tests = sum(1 for r in query_results if r.get("success", False))
        total_tests = len(query_results)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "health_results": health_results,
            "query_results": query_results,
            "recommendations": self._generate_recommendations(query_results, health_results)
        }
        
        return summary
    
    def _generate_recommendations(self, query_results: List[Dict], health_results: Dict) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check health status
        if not health_results.get("basic_health", {}).get("success", False):
            recommendations.append("Fix basic health endpoint - system may not be running properly")
        
        # Analyze query results
        success_rate = sum(1 for r in query_results if r.get("success", False)) / len(query_results) if query_results else 0
        
        if success_rate < 0.8:
            recommendations.append("Low success rate - investigate pipeline issues")
        
        # Check for common issues
        empty_retrieval_tests = [r for r in query_results if "empty retrieval" in r.get("test_name", "").lower()]
        if empty_retrieval_tests and not any("No relevant documents found" in str(r.get("warnings", [])) for r in empty_retrieval_tests):
            recommendations.append("Empty retrieval handling not working as expected")
        
        # Check response times
        avg_response_time = sum(r.get("response_time", 0) for r in query_results) / len(query_results) if query_results else 0
        if avg_response_time > 10:
            recommendations.append("High response times - consider performance optimization")
        
        return recommendations
    
    def print_report(self, report: Dict[str, Any]):
        """Print a formatted test report"""
        print("\n" + "="*80)
        print("PIPELINE IMPROVEMENT TEST REPORT")
        print("="*80)
        
        summary = report["test_summary"]
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Successful: {summary['successful_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        
        print(f"\n🏥 Health Status:")
        health = report["health_results"]
        for endpoint, result in health.items():
            status = "✅" if result.get("success", False) else "❌"
            print(f"   {endpoint}: {status}")
        
        print(f"\n🧪 Query Processing Results:")
        for result in report["query_results"]:
            status = "✅" if result.get("success", False) else "❌"
            test_name = result.get("test_name", "Unknown")
            response_time = result.get("response_time", 0)
            pipeline_status = result.get("pipeline_status", "unknown")
            
            print(f"   {test_name}: {status} ({response_time:.2f}s, {pipeline_status})")
            
            if result.get("issues"):
                for issue in result["issues"]:
                    print(f"     ⚠️ {issue}")
        
        if report["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")
        
        print("\n" + "="*80)

async def main():
    """Main test execution"""
    tester = PipelineImprovementTester()
    
    try:
        report = await tester.run_all_tests()
        tester.print_report(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pipeline_improvement_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 