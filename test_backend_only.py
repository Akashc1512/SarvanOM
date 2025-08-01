#!/usr/bin/env python3
"""
Focused Backend Test for SarvanOM
Tests all backend endpoints and functionality.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

class BackendTest:
    """Comprehensive backend testing."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        
    def test_root_endpoint(self) -> Dict[str, Any]:
        """Test the root endpoint."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            return {
                "endpoint": "Root (/)",
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "response": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "Root (/)",
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_health_endpoint(self) -> Dict[str, Any]:
        """Test the health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return {
                "endpoint": "Health (/health)",
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "response": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "Health (/health)",
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_basic_health_endpoint(self) -> Dict[str, Any]:
        """Test the basic health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/health/basic", timeout=10)
            return {
                "endpoint": "Basic Health (/health/basic)",
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "response": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "Basic Health (/health/basic)",
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_query_endpoint(self) -> Dict[str, Any]:
        """Test the query endpoint."""
        try:
            response = requests.post(f"{self.base_url}/query", timeout=10)
            return {
                "endpoint": "Query (/query)",
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "response": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "Query (/query)",
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_query_with_data(self) -> Dict[str, Any]:
        """Test the query endpoint with actual data."""
        try:
            test_data = {
                "query": "What are the latest developments in quantum computing?",
                "user_id": "test_user",
                "session_id": "test_session"
            }
            response = requests.post(
                f"{self.base_url}/query",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return {
                "endpoint": "Query with Data (/query)",
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "response": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "Query with Data (/query)",
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_docs_endpoint(self) -> Dict[str, Any]:
        """Test the docs endpoint."""
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            return {
                "endpoint": "Docs (/docs)",
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "response": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "endpoint": "Docs (/docs)",
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_server_performance(self) -> Dict[str, Any]:
        """Test server performance with multiple requests."""
        try:
            start_time = time.time()
            responses = []
            
            # Make 5 concurrent requests to test performance
            for i in range(5):
                response = requests.get(f"{self.base_url}/health", timeout=10)
                responses.append(response)
            
            end_time = time.time()
            total_time = (end_time - start_time) * 1000
            avg_time = total_time / 5
            
            success_count = sum(1 for r in responses if r.status_code == 200)
            
            return {
                "endpoint": "Performance Test",
                "status": "✅ PASS" if success_count == 5 else "❌ FAIL",
                "total_time_ms": total_time,
                "avg_time_ms": avg_time,
                "success_rate": f"{success_count}/5"
            }
        except Exception as e:
            return {
                "endpoint": "Performance Test",
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def run_all_tests(self):
        """Run all backend tests."""
        print("🚀 Starting Backend Test Suite...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_root_endpoint(),
            self.test_health_endpoint(),
            self.test_basic_health_endpoint(),
            self.test_query_endpoint(),
            self.test_query_with_data(),
            self.test_docs_endpoint(),
            self.test_server_performance()
        ]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate report
        self.generate_report(tests, duration)
    
    def generate_report(self, tests: list, duration: float):
        """Generate comprehensive test report."""
        print("\n" + "=" * 60)
        print("📊 BACKEND TEST REPORT")
        print("=" * 60)
        
        # Test Results
        print("\n🔧 TEST RESULTS:")
        print("-" * 50)
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            print(f"{test['endpoint']:25} : {test['status']}")
            if test.get('status_code'):
                print(f"  Status Code: {test['status_code']}")
            if test.get('response_time_ms'):
                print(f"  Response Time: {test['response_time_ms']:.2f}ms")
            if test.get('response'):
                print(f"  Response: {json.dumps(test['response'], indent=2)}")
            if test.get('error'):
                print(f"  Error: {test['error']}")
            if test.get('success_rate'):
                print(f"  Success Rate: {test['success_rate']}")
            if test.get('avg_time_ms'):
                print(f"  Avg Time: {test['avg_time_ms']:.2f}ms")
            print()
            
            if "PASS" in test['status']:
                passed += 1
        
        # Summary
        print("📈 SUMMARY:")
        print("-" * 30)
        print(f"Total Tests:     {total}")
        print(f"Passed:          {passed}")
        print(f"Failed:          {total - passed}")
        print(f"Success Rate:     {(passed/total)*100:.1f}%")
        print(f"Total Duration:   {duration:.2f} seconds")
        
        # Overall status
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Backend is fully operational.")
        elif passed > total * 0.8:
            print("\n⚠️  MOST TESTS PASSED. Backend is mostly operational.")
        else:
            print("\n❌ MANY TESTS FAILED. Backend needs attention.")
        
        print("=" * 60)

def main():
    """Main test function."""
    tester = BackendTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 