#!/usr/bin/env python3
"""
Final Summary Test for SarvanOM System
Provides comprehensive overview of backend and frontend status.
"""

import requests
import time
from datetime import datetime
from typing import Dict, Any

class FinalSummaryTest:
    """Final summary test for the entire system."""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        
    def test_backend_status(self) -> Dict[str, Any]:
        """Test backend status."""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            return {
                "status": "✅ OPERATIONAL" if response.status_code == 200 else "❌ DOWN",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "details": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "❌ DOWN",
                "error": str(e)
            }
    
    def test_frontend_status(self) -> Dict[str, Any]:
        """Test frontend status."""
        try:
            response = requests.get(f"{self.frontend_url}/", timeout=5)
            return {
                "status": "✅ OPERATIONAL" if response.status_code == 200 else "❌ DOWN",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "has_html": "<html" in response.text.lower()
            }
        except Exception as e:
            return {
                "status": "❌ DOWN",
                "error": str(e)
            }
    
    def test_api_integration(self) -> Dict[str, Any]:
        """Test API integration."""
        try:
            # Test a simple API call
            response = requests.post(f"{self.backend_url}/query", timeout=5)
            return {
                "status": "✅ WORKING" if response.status_code == 200 else "❌ FAILED",
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "error": str(e)
            }
    
    def generate_summary(self):
        """Generate comprehensive system summary."""
        print("🚀 SARVANOM SYSTEM STATUS SUMMARY")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test backend
        print("🔧 Testing Backend...")
        backend_status = self.test_backend_status()
        print(f"Backend Status: {backend_status['status']}")
        if backend_status.get('response_time_ms'):
            print(f"Response Time: {backend_status['response_time_ms']:.2f}ms")
        if backend_status.get('details'):
            print(f"Service: {backend_status['details'].get('service', 'Unknown')}")
        if backend_status.get('error'):
            print(f"Error: {backend_status['error']}")
        print()
        
        # Test frontend
        print("🎨 Testing Frontend...")
        frontend_status = self.test_frontend_status()
        print(f"Frontend Status: {frontend_status['status']}")
        if frontend_status.get('response_time_ms'):
            print(f"Response Time: {frontend_status['response_time_ms']:.2f}ms")
        if frontend_status.get('has_html'):
            print("Content: HTML page loaded")
        if frontend_status.get('error'):
            print(f"Error: {frontend_status['error']}")
        print()
        
        # Test API integration
        print("🔗 Testing API Integration...")
        api_status = self.test_api_integration()
        print(f"API Integration: {api_status['status']}")
        if api_status.get('response_time_ms'):
            print(f"Response Time: {api_status['response_time_ms']:.2f}ms")
        if api_status.get('error'):
            print(f"Error: {api_status['error']}")
        print()
        
        # Overall assessment
        print("📊 OVERALL ASSESSMENT:")
        print("-" * 30)
        
        backend_ok = "OPERATIONAL" in backend_status['status']
        frontend_ok = "OPERATIONAL" in frontend_status['status']
        api_ok = "WORKING" in api_status['status']
        
        if backend_ok and frontend_ok and api_ok:
            print("🎉 FULLY OPERATIONAL")
            print("   All systems are running and working together.")
        elif backend_ok and api_ok:
            print("⚠️  BACKEND OPERATIONAL, FRONTEND ISSUES")
            print("   Backend is working, but frontend needs attention.")
        elif backend_ok:
            print("⚠️  BACKEND ONLY OPERATIONAL")
            print("   Backend is working, but frontend and API integration have issues.")
        else:
            print("❌ SYSTEM ISSUES")
            print("   Multiple components need attention.")
        
        print()
        print("📍 ACCESS URLs:")
        print("-" * 30)
        print(f"Backend API:     {self.backend_url}")
        print(f"Frontend App:    {self.frontend_url}")
        print(f"API Health:      {self.backend_url}/health")
        print(f"API Docs:        {self.backend_url}/docs")
        print()
        print("=" * 60)

def main():
    """Main function."""
    tester = FinalSummaryTest()
    tester.generate_summary()

if __name__ == "__main__":
    main() 