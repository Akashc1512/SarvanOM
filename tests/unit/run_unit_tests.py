#!/usr/bin/env python3
"""
Unit test runner for SarvanOM backend.

This script runs all unit tests with coverage reporting and generates
detailed reports for analysis.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_tests_with_coverage(
    test_paths: List[str] = None,
    coverage_report: str = "html",
    coverage_fail_under: int = 80,
    verbose: bool = False,
    parallel: bool = False,
    markers: List[str] = None
) -> int:
    """
    Run unit tests with coverage reporting.
    
    Args:
        test_paths: List of test paths to run
        coverage_report: Type of coverage report (html, xml, term)
        coverage_fail_under: Minimum coverage percentage required
        verbose: Enable verbose output
        parallel: Run tests in parallel
        markers: pytest markers to run
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    
    # Default test paths if none provided
    if test_paths is None:
        test_paths = [
            "tests/unit/test_vector_search_formatting.py",
            "tests/unit/test_llm_response_parsing.py", 
            "tests/unit/test_auth_token_creation.py",
            "tests/unit/test_cache_service.py",
            "tests/unit/test_database_operations.py"
        ]
    
    # Build pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=shared",
        "--cov=backend", 
        "--cov=services",
        "--cov-report=term-missing",
        f"--cov-fail-under={coverage_fail_under}",
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ]
    
    # Add coverage report type
    if coverage_report == "html":
        cmd.append("--cov-report=html:htmlcov")
    elif coverage_report == "xml":
        cmd.append("--cov-report=xml:coverage.xml")
    elif coverage_report == "both":
        cmd.append("--cov-report=html:htmlcov")
        cmd.append("--cov-report=xml:coverage.xml")
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    
    # Add parallel execution
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # Add markers
    if markers:
        for marker in markers:
            cmd.extend(["-m", marker])
    
    # Add test paths
    cmd.extend(test_paths)
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print(f"Test paths: {test_paths}")
    print(f"Coverage report: {coverage_report}")
    print(f"Coverage threshold: {coverage_fail_under}%")
    print("-" * 80)
    
    # Run tests
    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running tests: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1


def run_specific_test_suite(suite_name: str, **kwargs) -> int:
    """
    Run a specific test suite.
    
    Args:
        suite_name: Name of the test suite to run
        **kwargs: Additional arguments for run_tests_with_coverage
    
    Returns:
        Exit code
    """
    
    suite_paths = {
        "vector_search": ["tests/unit/test_vector_search_formatting.py"],
        "llm_parsing": ["tests/unit/test_llm_response_parsing.py"],
        "auth": ["tests/unit/test_auth_token_creation.py"],
        "cache": ["tests/unit/test_cache_service.py"],
        "database": ["tests/unit/test_database_operations.py"],
        "all": None  # Will use default paths
    }
    
    if suite_name not in suite_paths:
        print(f"Unknown test suite: {suite_name}")
        print(f"Available suites: {list(suite_paths.keys())}")
        return 1
    
    test_paths = suite_paths[suite_name]
    return run_tests_with_coverage(test_paths=test_paths, **kwargs)


def generate_coverage_report(coverage_data_file: str = "coverage.xml") -> None:
    """
    Generate a detailed coverage report.
    
    Args:
        coverage_data_file: Path to coverage data file
    """
    
    if not os.path.exists(coverage_data_file):
        print(f"Coverage data file not found: {coverage_data_file}")
        return
    
    try:
        import coverage
        
        # Load coverage data
        cov = coverage.Coverage()
        cov.load()
        
        # Generate report
        print("\n" + "=" * 80)
        print("DETAILED COVERAGE REPORT")
        print("=" * 80)
        
        # Overall statistics
        total_statements = cov.get_analysis().statements
        missing_statements = cov.get_analysis().missing
        covered_statements = total_statements - missing_statements
        coverage_percentage = (covered_statements / total_statements) * 100 if total_statements > 0 else 0
        
        print(f"Total statements: {total_statements}")
        print(f"Covered statements: {covered_statements}")
        print(f"Missing statements: {missing_statements}")
        print(f"Coverage percentage: {coverage_percentage:.2f}%")
        
        # File-by-file breakdown
        print("\nFile-by-file coverage:")
        print("-" * 80)
        
        for filename in cov.get_analysis().measured_files():
            file_analysis = cov.analysis2(filename)
            file_statements = len(file_analysis[1])
            file_missing = len(file_analysis[2])
            file_covered = file_statements - file_missing
            file_coverage = (file_covered / file_statements) * 100 if file_statements > 0 else 0
            
            print(f"{filename}: {file_coverage:.1f}% ({file_covered}/{file_statements})")
            
            if file_missing > 0:
                print(f"  Missing lines: {sorted(file_analysis[2])}")
        
    except ImportError:
        print("coverage package not available for detailed reporting")
    except Exception as e:
        print(f"Error generating coverage report: {e}")


def main():
    """Main entry point for the test runner."""
    
    parser = argparse.ArgumentParser(description="Run SarvanOM unit tests with coverage")
    parser.add_argument(
        "--suite", 
        choices=["vector_search", "llm_parsing", "auth", "cache", "database", "all"],
        default="all",
        help="Test suite to run"
    )
    parser.add_argument(
        "--coverage-report",
        choices=["html", "xml", "term", "both"],
        default="html",
        help="Type of coverage report to generate"
    )
    parser.add_argument(
        "--coverage-threshold",
        type=int,
        default=80,
        help="Minimum coverage percentage required"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--markers", "-m",
        nargs="+",
        help="pytest markers to run"
    )
    parser.add_argument(
        "--detailed-report",
        action="store_true",
        help="Generate detailed coverage report"
    )
    
    args = parser.parse_args()
    
    # Run tests
    exit_code = run_specific_test_suite(
        suite_name=args.suite,
        coverage_report=args.coverage_report,
        coverage_fail_under=args.coverage_threshold,
        verbose=args.verbose,
        parallel=args.parallel,
        markers=args.markers
    )
    
    # Generate detailed report if requested
    if args.detailed_report:
        generate_coverage_report()
    
    # Print summary
    print("\n" + "=" * 80)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 80)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
