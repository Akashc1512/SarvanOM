#!/usr/bin/env python3
"""
Backend Functionality Test Runner

This script runs the comprehensive backend functionality tests to verify
all backend systems are working as expected with real LLM providers.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """Setup test environment variables."""
    # Set test-specific environment variables
    os.environ.setdefault("TESTING", "true")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    # LLM configuration
    os.environ.setdefault("MODEL_POLICY", "cheap_first")
    os.environ.setdefault("OLLAMA_ENABLED", "true")
    os.environ.setdefault("USE_VECTOR_DB", "true")
    
    # Performance thresholds for real LLM testing
    os.environ.setdefault("PERFORMANCE_THRESHOLD", "30.0")
    os.environ.setdefault("TEST_TIMEOUT", "60.0")

def run_tests(test_pattern=None, markers=None, verbose=False, coverage=False):
    """Run the backend functionality tests."""
    setup_environment()
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test file
    test_file = project_root / "tests" / "test_backend_functionality.py"
    if test_pattern:
        cmd.extend(["-k", test_pattern])
    else:
        cmd.append(str(test_file))
    
    # Add markers
    if markers:
        for marker in markers:
            cmd.extend(["-m", marker])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=services",
            "--cov=shared", 
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    # Add additional options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print(f"Project root: {project_root}")
    print(f"Test file: {test_file}")
    print()
    
    # Run tests
    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def run_health_checks():
    """Run only health check tests."""
    return run_tests(markers=["health"])

def run_performance_tests():
    """Run only performance tests."""
    return run_tests(markers=["performance"])

def run_llm_tests():
    """Run only LLM integration tests."""
    return run_tests(markers=["llm"])

def run_quick_tests():
    """Run quick tests excluding slow ones."""
    return run_tests(markers=["not slow"])

def main():
    """Main function to run tests based on command line arguments."""
    parser = argparse.ArgumentParser(description="Run backend functionality tests")
    parser.add_argument(
        "--pattern", "-k",
        help="Test pattern to run (pytest -k pattern)"
    )
    parser.add_argument(
        "--markers", "-m",
        nargs="+",
        help="Test markers to run (e.g., health, performance, llm)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--health-only",
        action="store_true",
        help="Run only health check tests"
    )
    parser.add_argument(
        "--performance-only",
        action="store_true",
        help="Run only performance tests"
    )
    parser.add_argument(
        "--llm-only",
        action="store_true",
        help="Run only LLM integration tests"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick tests (exclude slow tests)"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not (project_root / "tests" / "test_backend_functionality.py").exists():
        print("Error: test file not found. Make sure you're running from the project root.")
        sys.exit(1)
    
    # Run specific test suites
    if args.health_only:
        success = run_health_checks()
    elif args.performance_only:
        success = run_performance_tests()
    elif args.llm_only:
        success = run_llm_tests()
    elif args.quick:
        success = run_quick_tests()
    else:
        # Run all tests or filtered tests
        success = run_tests(
            test_pattern=args.pattern,
            markers=args.markers,
            verbose=args.verbose,
            coverage=args.coverage
        )
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
