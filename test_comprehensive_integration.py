#!/usr/bin/env python3
"""
Comprehensive Integration Test for SarvanOM Backend and Frontend
Tests both services and their integration.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class ComprehensiveIntegrationTest:
    """Comprehensive test for backend and frontend integration."""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3001"
        self.test_results = []
        
    def test_backend_endpoints(self) -> Dict[str, Any]:
        """Test all backend endpoints."""
        print("🔍 Testing Backend Endpoints...")
        results = {}
        
        # Test root endpoint
        try:
            response = requests.get(f"{self.backend_url}/", timeout=10)
            results["root"] = {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            results["root"] = {"status": "❌ FAIL", "error": str(e)}
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            results["health"] = {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            results["health"] = {"status": "❌ FAIL", "error": str(e)}
        
        # Test basic health endpoint
        try:
            response = requests.get(f"{self.backend_url}/health/basic", timeout=10)
            results["basic_health"] = {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            results["basic_health"] = {"status": "❌ FAIL", "error": str(e)}
        
        # Test query endpoint
        try:
            response = requests.post(f"{self.backend_url}/query", timeout=10)
            results["query"] = {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            results["query"] = {"status": "❌ FAIL", "error": str(e)}
        
        return results
    
    def test_frontend_endpoints(self) -> Dict[str, Any]:
        """Test frontend endpoints."""
        print("🎨 Testing Frontend Endpoints...")
        results = {}
        
        # Test main page
        try:
            response = requests.get(f"{self.frontend_url}/", timeout=10)
            results["main_page"] = {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "has_html": "<html" in response.text.lower()
            }
        except Exception as e:
            results["main_page"] = {"status": "❌ FAIL", "error": str(e)}
        
        # Test login page
        try:
            response = requests.get(f"{self.frontend_url}/login", timeout=10)
            results["login_page"] = {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "has_html": "<html" in response.text.lower()
            }
        except Exception as e:
            results["login_page"] = {"status": "❌ FAIL", "error": str(e)}
        
        # Test dashboard page
        try:
            response = requests.get(f"{self.frontend_url}/dashboard", timeout=10)
            results["dashboard_page"] = {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "has_html": "<html" in response.text.lower()
            }
        except Exception as e:
            results["dashboard_page"] = {"status": "❌ FAIL", "error": str(e)}
        
        return results
    
    def test_api_integration(self) -> Dict[str, Any]:
        """Test API integration between frontend and backend."""
        print("🔗 Testing API Integration...")
        results = {}
        
        # Test if frontend can access backend API
        try:
            # This would typically be done through the frontend's API calls
            # For now, we'll test if the backend is accessible from the frontend's perspective
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            results["backend_accessible"] = {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code
            }
        except Exception as e:
            results["backend_accessible"] = {"status": "❌ FAIL", "error": str(e)}
        
        return results
    
    def run_comprehensive_test(self):
        """Run all comprehensive tests."""
        print("🚀 Starting Comprehensive Integration Test...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test backend
        backend_results = self.test_backend_endpoints()
        
        # Test frontend
        frontend_results = self.test_frontend_endpoints()
        
        # Test integration
        integration_results = self.test_api_integration()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate report
        self.generate_report(backend_results, frontend_results, integration_results, duration)
    
    def generate_report(self, backend_results: Dict, frontend_results: Dict, 
                       integration_results: Dict, duration: float):
        """Generate comprehensive test report."""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE INTEGRATION TEST REPORT")
        print("=" * 60)
        
        # Backend Results
        print("\n🔧 BACKEND TEST RESULTS:")
        print("-" * 30)
        for endpoint, result in backend_results.items():
            print(f"{endpoint:15} : {result['status']}")
            if result.get('status_code'):
                print(f"  Status Code: {result['status_code']}")
            if result.get('error'):
                print(f"  Error: {result['error']}")
        
        # Frontend Results
        print("\n🎨 FRONTEND TEST RESULTS:")
        print("-" * 30)
        for endpoint, result in frontend_results.items():
            print(f"{endpoint:15} : {result['status']}")
            if result.get('status_code'):
                print(f"  Status Code: {result['status_code']}")
            if result.get('error'):
                print(f"  Error: {result['error']}")
        
        # Integration Results
        print("\n🔗 INTEGRATION TEST RESULTS:")
        print("-" * 30)
        for test, result in integration_results.items():
            print(f"{test:20} : {result['status']}")
            if result.get('error'):
                print(f"  Error: {result['error']}")
        
        # Summary
        print("\n📈 SUMMARY:")
        print("-" * 30)
        
        backend_passed = sum(1 for r in backend_results.values() if "PASS" in r.get('status', ''))
        frontend_passed = sum(1 for r in frontend_results.values() if "PASS" in r.get('status', ''))
        integration_passed = sum(1 for r in integration_results.values() if "PASS" in r.get('status', ''))
        
        total_backend = len(backend_results)
        total_frontend = len(frontend_results)
        total_integration = len(integration_results)
        
        print(f"Backend Tests:     {backend_passed}/{total_backend} passed")
        print(f"Frontend Tests:    {frontend_passed}/{total_frontend} passed")
        print(f"Integration Tests: {integration_passed}/{total_integration} passed")
        print(f"Total Duration:    {duration:.2f} seconds")
        
        # Overall status
        total_tests = total_backend + total_frontend + total_integration
        total_passed = backend_passed + frontend_passed + integration_passed
        
        if total_passed == total_tests:
            print("\n🎉 ALL TESTS PASSED! System is fully operational.")
        elif total_passed > total_tests * 0.8:
            print("\n⚠️  MOST TESTS PASSED. System is mostly operational.")
        else:
            print("\n❌ MANY TESTS FAILED. System needs attention.")
        
        print("=" * 60)

def main():
    """Main test function."""
    tester = ComprehensiveIntegrationTest()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main() 