#!/usr/bin/env python3
"""
End-to-End Test Runner for Real Backend Pipeline

This script runs comprehensive E2E tests for the complete backend orchestration flow,
ensuring all services work together correctly with real data and services.

Usage:
    python run_e2e_tests.py [--verbose] [--specific-test TEST_NAME]

Examples:
    python run_e2e_tests.py                    # Run all tests
    python run_e2e_tests.py --verbose          # Run with verbose output
    python run_e2e_tests.py --specific-test test_basic_pipeline_flow  # Run specific test
"""

import sys
import os
import argparse
import subprocess
import time
from datetime import datetime

def setup_environment():
    """Setup the test environment."""
    print("🔧 Setting up test environment...")
    
    # Add project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Check if required services are running
    print("🔍 Checking service availability...")
    
    # Check if FastAPI app can be imported
    try:
        from services.api_gateway.main import app
        print("✅ FastAPI app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        return False
    
    # Check if test dependencies are available
    try:
        import pytest
        from fastapi.testclient import TestClient
        print("✅ Test dependencies available")
    except ImportError as e:
        print(f"❌ Missing test dependencies: {e}")
        print("Please install test dependencies: pip install pytest httpx")
        return False
    
    return True

def run_health_checks():
    """Run basic health checks before tests."""
    print("🏥 Running health checks...")
    
    try:
        from services.api_gateway.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test basic health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health endpoint responding")
        else:
            print(f"⚠️ Health endpoint returned {response.status_code}")
        
        # Test simple health endpoint
        response = client.get("/health/simple")
        if response.status_code == 200:
            print("✅ Simple health endpoint responding")
        else:
            print(f"⚠️ Simple health endpoint returned {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health checks failed: {e}")
        return False

def run_tests(verbose=False, specific_test=None):
    """Run the E2E tests."""
    print("🚀 Starting E2E tests...")
    
    # Build pytest command
    cmd = [
        "python", "-m", "pytest",
        "tests/e2e/test_real_backend_pipeline.py",
        "-v" if verbose else "-q",
        "--tb=short",
        "--color=yes"
    ]
    
    if specific_test:
        cmd.extend(["-k", specific_test])
    
    # Add coverage if available
    try:
        import coverage
        cmd.extend(["--cov=services", "--cov-report=term-missing"])
    except ImportError:
        print("ℹ️ Coverage not available, running without coverage")
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Run tests
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=False)
    end_time = time.time()
    
    duration = end_time - start_time
    
    if result.returncode == 0:
        print(f"✅ All tests passed in {duration:.2f} seconds")
        return True
    else:
        print(f"❌ Some tests failed in {duration:.2f} seconds")
        return False

def generate_test_report():
    """Generate a test report."""
    print("\n📊 Test Report")
    print("=" * 50)
    
    # Test summary
    test_cases = [
        "Basic End-to-End Query Flow (Cold Cache)",
        "Cache Hit on Repeat Query", 
        "Complex Synthesis Query (LLM Routing Check)",
        "Fallback Scenario (Simulated Service Failure)",
        "Fact-Check Freshness Validation",
        "Technical Query Routing",
        "Hybrid Retrieval Validation",
        "Response Structure Validation",
        "Error Handling and Recovery",
        "Performance Under Load"
    ]
    
    print("Test Cases Covered:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"  {i:2d}. {test_case}")
    
    print("\nExpected Outcomes:")
    print("✅ Full pipeline orchestration (Retrieval → FactCheck → Synthesis → Citation)")
    print("✅ Hybrid retrieval (Meilisearch + Qdrant + ArangoDB)")
    print("✅ LLM routing and fallback mechanisms")
    print("✅ Cache hit/miss behavior")
    print("✅ Fact-checking and citation validation")
    print("✅ Service failure scenarios and fallbacks")
    print("✅ Response structure validation")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run E2E tests for real backend pipeline")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--specific-test", "-t", help="Run specific test by name")
    parser.add_argument("--health-only", action="store_true", help="Run only health checks")
    parser.add_argument("--report-only", action="store_true", help="Generate test report only")
    
    args = parser.parse_args()
    
    print("🧪 Real Backend Pipeline E2E Test Runner")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if args.report_only:
        generate_test_report()
        return
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    # Run health checks
    if not run_health_checks():
        print("⚠️ Health checks failed, but continuing with tests...")
    
    if args.health_only:
        print("✅ Health checks completed")
        return
    
    # Run tests
    success = run_tests(verbose=args.verbose, specific_test=args.specific_test)
    
    # Generate report
    generate_test_report()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("\nNext Steps:")
        print("1. Review test results and logs")
        print("2. Check service metrics and performance")
        print("3. Validate response quality and accuracy")
        print("4. Monitor system resources and stability")
    else:
        print("\n⚠️ Some tests failed. Please check:")
        print("1. Service availability and health")
        print("2. Environment configuration")
        print("3. Test logs for specific failures")
        print("4. System resources and dependencies")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 