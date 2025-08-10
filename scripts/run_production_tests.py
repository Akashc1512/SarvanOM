#!/usr/bin/env python3
"""
Production-Grade Test Runner for SarvanOM Backend

Following MAANG/OpenAI/Perplexity industry standards:
- Comprehensive test execution
- Performance monitoring
- Security validation
- Load testing
- Reporting and analytics
- CI/CD integration ready
"""

import argparse
import asyncio
import json
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import statistics

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_production_grade import PerformanceMetrics, TestConfig, CONFIG


@dataclass
class TestResult:
    """Test execution result with comprehensive metrics."""
    test_name: str
    status: str  # "passed", "failed", "skipped", "error"
    duration: float
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class TestSuiteResult:
    """Complete test suite execution result."""
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    total_duration: float
    start_time: str
    end_time: str
    performance_summary: Dict[str, Any]
    security_issues: List[str]
    recommendations: List[str]
    test_results: List[TestResult]


class ProductionTestRunner:
    """Production-grade test runner with comprehensive reporting."""
    
    def __init__(self, config: TestConfig = None):
        self.config = config or CONFIG
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        self.performance_metrics = PerformanceMetrics()
        
    def run_tests(self, test_patterns: List[str] = None, 
                  include_slow: bool = False,
                  parallel: bool = True,
                  output_format: str = "json") -> TestSuiteResult:
        """Run comprehensive test suite."""
        self.start_time = datetime.utcnow()
        
        print("🚀 Starting Production-Grade Test Suite")
        print(f"📊 Configuration: {self.config}")
        print(f"⏰ Start Time: {self.start_time}")
        print("=" * 80)
        
        # Determine test patterns
        if test_patterns is None:
            test_patterns = [
                "tests/test_backend_functionality_simple.py",
                "tests/test_production_grade.py"
            ]
        
        # Build pytest command
        cmd = [
            "python", "-m", "pytest",
            "-v",
            "--tb=short",
            "--durations=10",
            "--strict-markers"
        ]
        
        # Add test patterns
        for pattern in test_patterns:
            cmd.append(pattern)
        
        # Add markers
        if not include_slow:
            cmd.extend(["-m", "not slow"])
        
        # Add parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add output format
        if output_format == "json":
            cmd.extend(["--json-report", "--json-report-file=test-results.json"])
        
        # Add coverage
        cmd.extend([
            "--cov=services",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-report=term-missing"
        ])
        
        print(f"🔧 Executing: {' '.join(cmd)}")
        
        # Execute tests
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.TEST_DURATION_SECONDS * 2
            )
            
            # Parse results
            self._parse_pytest_output(result.stdout, result.stderr)
            
        except subprocess.TimeoutExpired:
            print("⏰ Test execution timed out")
            self.results.append(TestResult(
                test_name="test_execution",
                status="error",
                duration=self.config.TEST_DURATION_SECONDS * 2,
                error_message="Test execution timed out"
            ))
        
        self.end_time = datetime.utcnow()
        
        # Generate comprehensive report
        return self._generate_test_suite_result()
    
    def _parse_pytest_output(self, stdout: str, stderr: str):
        """Parse pytest output to extract test results."""
        lines = stdout.split('\n')
        current_test = None
        
        for line in lines:
            if line.startswith('test_') and '::' in line:
                # Extract test name
                test_name = line.split('::')[1].split()[0]
                current_test = TestResult(
                    test_name=test_name,
                    status="passed",
                    duration=0.0
                )
                
            elif current_test and "PASSED" in line:
                current_test.status = "passed"
                self.results.append(current_test)
                current_test = None
                
            elif current_test and "FAILED" in line:
                current_test.status = "failed"
                current_test.error_message = line
                self.results.append(current_test)
                current_test = None
                
            elif current_test and "SKIPPED" in line:
                current_test.status = "skipped"
                self.results.append(current_test)
                current_test = None
    
    def _generate_test_suite_result(self) -> TestSuiteResult:
        """Generate comprehensive test suite result."""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "passed"])
        failed_tests = len([r for r in self.results if r.status == "failed"])
        skipped_tests = len([r for r in self.results if r.status == "skipped"])
        error_tests = len([r for r in self.results if r.status == "error"])
        
        total_duration = sum(r.duration for r in self.results)
        
        # Calculate performance summary
        performance_summary = self._calculate_performance_summary()
        
        # Identify security issues
        security_issues = self._identify_security_issues()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            passed_tests, failed_tests, total_tests, performance_summary
        )
        
        return TestSuiteResult(
            suite_name="SarvanOM Production Test Suite",
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            error_tests=error_tests,
            total_duration=total_duration,
            start_time=self.start_time.isoformat(),
            end_time=self.end_time.isoformat(),
            performance_summary=performance_summary,
            security_issues=security_issues,
            recommendations=recommendations,
            test_results=self.results
        )
    
    def _calculate_performance_summary(self) -> Dict[str, Any]:
        """Calculate comprehensive performance summary."""
        if not self.results:
            return {}
        
        durations = [r.duration for r in self.results if r.duration > 0]
        
        if not durations:
            return {"message": "No performance data available"}
        
        return {
            "total_tests": len(self.results),
            "performance_tests": len(durations),
            "mean_duration": statistics.mean(durations),
            "median_duration": statistics.median(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "p95_duration": statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations),
            "p99_duration": statistics.quantiles(durations, n=100)[98] if len(durations) >= 100 else max(durations),
            "success_rate": (len([r for r in self.results if r.status == "passed"]) / len(self.results)) * 100,
            "failure_rate": (len([r for r in self.results if r.status in ["failed", "error"]]) / len(self.results)) * 100
        }
    
    def _identify_security_issues(self) -> List[str]:
        """Identify potential security issues from test results."""
        issues = []
        
        # Check for failed security tests
        security_failures = [r for r in self.results 
                           if "security" in r.test_name.lower() and r.status == "failed"]
        
        if security_failures:
            issues.append(f"Security tests failed: {len(security_failures)} failures")
        
        # Check for authentication/authorization issues
        auth_failures = [r for r in self.results 
                        if "auth" in r.test_name.lower() and r.status == "failed"]
        
        if auth_failures:
            issues.append(f"Authentication/Authorization tests failed: {len(auth_failures)} failures")
        
        # Check for input validation issues
        validation_failures = [r for r in self.results 
                             if "validation" in r.test_name.lower() and r.status == "failed"]
        
        if validation_failures:
            issues.append(f"Input validation tests failed: {len(validation_failures)} failures")
        
        return issues
    
    def _generate_recommendations(self, passed: int, failed: int, total: int, 
                                performance: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on test results."""
        recommendations = []
        
        # Success rate recommendations
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        if success_rate < 95:
            recommendations.append(f"⚠️  Low success rate ({success_rate:.1f}%). Review failed tests and fix critical issues.")
        
        if success_rate < 80:
            recommendations.append("🚨 Critical: Success rate below 80%. Block deployment until issues are resolved.")
        
        # Performance recommendations
        if "mean_duration" in performance:
            mean_duration = performance["mean_duration"]
            if mean_duration > self.config.P50_RESPONSE_TIME_MS / 1000:
                recommendations.append(f"🐌 Performance issue: Mean test duration ({mean_duration:.2f}s) exceeds threshold.")
        
        if "p95_duration" in performance:
            p95_duration = performance["p95_duration"]
            if p95_duration > self.config.P95_RESPONSE_TIME_MS / 1000:
                recommendations.append(f"🐌 Performance issue: P95 test duration ({p95_duration:.2f}s) exceeds threshold.")
        
        # Security recommendations
        if failed > 0:
            recommendations.append("🔒 Security: Review failed tests for potential security vulnerabilities.")
        
        # Coverage recommendations
        if "success_rate" in performance and performance["success_rate"] < 90:
            recommendations.append("📊 Coverage: Consider adding more test cases to improve coverage.")
        
        return recommendations
    
    def save_report(self, result: TestSuiteResult, output_file: str = "test-report.json"):
        """Save comprehensive test report to file."""
        report_data = asdict(result)
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"📄 Report saved to: {output_file}")
    
    def print_summary(self, result: TestSuiteResult):
        """Print comprehensive test summary."""
        print("\n" + "=" * 80)
        print("📊 PRODUCTION TEST SUITE SUMMARY")
        print("=" * 80)
        
        # Basic statistics
        print(f"📈 Test Results:")
        print(f"   Total Tests: {result.total_tests}")
        print(f"   ✅ Passed: {result.passed_tests}")
        print(f"   ❌ Failed: {result.failed_tests}")
        print(f"   ⏭️  Skipped: {result.skipped_tests}")
        print(f"   💥 Errors: {result.error_tests}")
        
        # Success rate
        success_rate = (result.passed_tests / result.total_tests) * 100 if result.total_tests > 0 else 0
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        
        # Duration
        print(f"\n⏱️  Duration:")
        print(f"   Total Duration: {result.total_duration:.2f}s")
        print(f"   Start Time: {result.start_time}")
        print(f"   End Time: {result.end_time}")
        
        # Performance summary
        if result.performance_summary:
            print(f"\n🚀 Performance Summary:")
            perf = result.performance_summary
            if "mean_duration" in perf:
                print(f"   Mean Duration: {perf['mean_duration']:.2f}s")
            if "p95_duration" in perf:
                print(f"   P95 Duration: {perf['p95_duration']:.2f}s")
            if "success_rate" in perf:
                print(f"   Performance Success Rate: {perf['success_rate']:.1f}%")
        
        # Security issues
        if result.security_issues:
            print(f"\n🔒 Security Issues:")
            for issue in result.security_issues:
                print(f"   ⚠️  {issue}")
        
        # Recommendations
        if result.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in result.recommendations:
                print(f"   {rec}")
        
        # Overall status
        print(f"\n🎯 Overall Status:")
        if success_rate >= 95 and not result.security_issues:
            print("   ✅ PRODUCTION READY")
        elif success_rate >= 80:
            print("   ⚠️  NEEDS ATTENTION - Review recommendations")
        else:
            print("   🚨 CRITICAL ISSUES - Block deployment")
        
        print("=" * 80)


def main():
    """Main entry point for production test runner."""
    parser = argparse.ArgumentParser(
        description="Production-Grade Test Runner for SarvanOM Backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python scripts/run_production_tests.py
  
  # Run specific test patterns
  python scripts/run_production_tests.py --patterns "tests/test_production_grade.py::TestProductionGradeAPI"
  
  # Run with slow tests included
  python scripts/run_production_tests.py --include-slow
  
  # Run in parallel with custom output
  python scripts/run_production_tests.py --parallel --output-format json
        """
    )
    
    parser.add_argument(
        "--patterns", "-p",
        nargs="+",
        help="Test patterns to run (default: all production tests)"
    )
    
    parser.add_argument(
        "--include-slow", "-s",
        action="store_true",
        help="Include slow tests (load testing, stress testing)"
    )
    
    parser.add_argument(
        "--parallel", "-n",
        action="store_true",
        default=True,
        help="Run tests in parallel (default: True)"
    )
    
    parser.add_argument(
        "--output-format", "-f",
        choices=["json", "text"],
        default="json",
        help="Output format for test results (default: json)"
    )
    
    parser.add_argument(
        "--output-file", "-o",
        default="test-report.json",
        help="Output file for test report (default: test-report.json)"
    )
    
    parser.add_argument(
        "--config-file", "-c",
        help="Path to test configuration file"
    )
    
    args = parser.parse_args()
    
    # Load configuration if provided
    config = CONFIG
    if args.config_file and os.path.exists(args.config_file):
        with open(args.config_file, 'r') as f:
            config_data = json.load(f)
            config = TestConfig(**config_data)
    
    # Create test runner
    runner = ProductionTestRunner(config)
    
    # Run tests
    try:
        result = runner.run_tests(
            test_patterns=args.patterns,
            include_slow=args.include_slow,
            parallel=args.parallel,
            output_format=args.output_format
        )
        
        # Print summary
        runner.print_summary(result)
        
        # Save report
        runner.save_report(result, args.output_file)
        
        # Exit with appropriate code
        success_rate = (result.passed_tests / result.total_tests) * 100 if result.total_tests > 0 else 0
        
        if success_rate >= 95 and not result.security_issues:
            print("✅ All critical tests passed. Ready for production deployment.")
            sys.exit(0)
        elif success_rate >= 80:
            print("⚠️  Tests completed with warnings. Review recommendations before deployment.")
            sys.exit(1)
        else:
            print("🚨 Critical test failures. Block deployment until issues are resolved.")
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"💥 Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
