#!/usr/bin/env python3
"""
Backend Integration Test Runner

This script runs the enhanced backend integration test suite and provides
comprehensive reporting on the end-to-end pipeline verification.

Usage:
    python run_backend_integration_tests.py

Requirements:
    - FastAPI test client
    - pytest
    - All backend services running (API Gateway, Search Service, etc.)
"""

import sys
import os
import time
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import pytest
        import fastapi
        from fastapi.testclient import TestClient
        print("✅ All required dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages: pip install pytest fastapi httpx")
        return False

def check_services_running():
    """Check if backend services are running."""
    import requests
    
    services = [
        ("API Gateway", "http://localhost:8000/health"),
        ("Search Service", "http://localhost:8001/health"),
        ("Synthesis Service", "http://localhost:8002/health"),
    ]
    
    running_services = []
    for service_name, health_url in services:
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                running_services.append(service_name)
                print(f"✅ {service_name} is running")
            else:
                print(f"⚠️  {service_name} responded with status {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"❌ {service_name} is not running")
    
    return len(running_services) == len(services)

def run_tests():
    """Run the enhanced backend integration tests."""
    print("\n" + "="*60)
    print("🚀 Running Enhanced Backend Integration Tests")
    print("="*60)
    
    # Test file path
    test_file = "tests/integration/test_backend_integration_enhanced.py"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    # Run tests with verbose output
    cmd = [
        sys.executable, "-m", "pytest",
        test_file,
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        end_time = time.time()
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        print("-" * 60)
        print(f"⏱️  Total test execution time: {end_time - start_time:.2f}s")
        print(f"📊 Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_specific_test_cases():
    """Run specific test cases to demonstrate functionality."""
    print("\n" + "="*60)
    print("🎯 Running Specific Test Cases")
    print("="*60)
    
    test_cases = [
        "TestBasicQueryPipeline::test_basic_query_pipeline_success",
        "TestComplexQueryLLMRouting::test_complex_query_llm_routing",
        "TestCacheHitVerification::test_cache_hit_second_run",
        "TestPerformanceBenchmarks::test_response_time_sla_compliance"
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Running: {test_case}")
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/integration/test_backend_integration_enhanced.py",
            f"-k {test_case}",
            "-v",
            "--tb=short"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {test_case} - PASSED")
            else:
                print(f"❌ {test_case} - FAILED")
                print(result.stdout)
        except Exception as e:
            print(f"❌ Error running {test_case}: {e}")

def generate_test_report():
    """Generate a comprehensive test report."""
    print("\n" + "="*60)
    print("📋 Test Report Summary")
    print("="*60)
    
    report = {
        "test_suite": "Enhanced Backend Integration Tests",
        "version": "2.0.0",
        "test_cases": {
            "basic_query_pipeline": "Verifies end-to-end pipeline with local LLM",
            "complex_query_routing": "Tests cloud LLM routing for complex queries",
            "llm_failure_fallback": "Validates graceful fallback mechanisms",
            "cache_verification": "Ensures proper cache hit/miss behavior",
            "agent_orchestration": "Verifies agent chain execution order",
            "response_quality": "Validates response quality metrics",
            "performance_benchmarks": "Tests SLA compliance and concurrent handling",
            "error_handling": "Validates error handling and recovery"
        },
        "expected_outcomes": [
            "All API responses are validated",
            "Orchestrator correctly routes queries",
            "Fallbacks are tested and working",
            "Cache hits are confirmed",
            "Full backend agent chain is operational"
        ]
    }
    
    print(f"Test Suite: {report['test_suite']}")
    print(f"Version: {report['version']}")
    print("\nTest Cases:")
    for case, description in report['test_cases'].items():
        print(f"  • {case}: {description}")
    
    print("\nExpected Outcomes:")
    for outcome in report['expected_outcomes']:
        print(f"  • {outcome}")

def main():
    """Main function to run the test suite."""
    print("🔧 Backend Integration Test Runner")
    print("="*60)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check if services are running
    print("\n🔍 Checking service availability...")
    if not check_services_running():
        print("\n⚠️  Warning: Some services may not be running.")
        print("   Tests may fail if required services are unavailable.")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return 1
    
    # Generate test report
    generate_test_report()
    
    # Run specific test cases
    run_specific_test_cases()
    
    # Run full test suite
    success = run_tests()
    
    print("\n" + "="*60)
    if success:
        print("🎉 All tests completed successfully!")
        print("✅ Backend integration pipeline is working correctly")
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        print("🔧 Review the failed tests and fix any issues")
    
    print("="*60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 