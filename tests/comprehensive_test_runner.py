"""
Comprehensive Test Runner - SarvanOM v2
Orchestrates all testing components: test matrix, SLA validation, and synthetic prompt suites.
"""

import asyncio
import time
import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse
import sys
import os

# Add the tests directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_matrix_runner import TestMatrixRunner
from sla_validator import SLAMonitor
from synthetic_prompt_suites import SyntheticPromptSuites

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestExecutionResult:
    test_type: str
    success: bool
    execution_time: float
    results: Dict[str, Any]
    error_message: Optional[str] = None

@dataclass
class ComprehensiveTestReport:
    execution_id: str
    start_time: float
    end_time: float
    total_execution_time: float
    test_results: List[TestExecutionResult]
    overall_success: bool
    summary: Dict[str, Any]
    recommendations: List[str]

class ComprehensiveTestRunner:
    """Comprehensive test runner that orchestrates all testing components"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.test_matrix_runner = TestMatrixRunner(base_url)
        self.sla_monitor = SLAMonitor(base_url)
        self.prompt_suites = SyntheticPromptSuites(base_url)
        
        # Test execution tracking
        self.execution_results: List[TestExecutionResult] = []
        self.start_time = 0.0
        self.end_time = 0.0

    async def run_test_matrix(self) -> TestExecutionResult:
        """Run the comprehensive test matrix"""
        logger.info("Starting Test Matrix execution...")
        start_time = time.time()
        
        try:
            report = await self.test_matrix_runner.run_full_test_matrix()
            
            execution_time = time.time() - start_time
            success = report['test_summary']['overall_sla_compliance'] >= 0.90
            
            result = TestExecutionResult(
                test_type="test_matrix",
                success=success,
                execution_time=execution_time,
                results=report
            )
            
            logger.info(f"Test Matrix completed in {execution_time:.2f}s - Success: {success}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Test Matrix failed: {e}")
            
            return TestExecutionResult(
                test_type="test_matrix",
                success=False,
                execution_time=execution_time,
                results={},
                error_message=str(e)
            )

    async def run_sla_validation(self, duration_minutes: int = 5) -> TestExecutionResult:
        """Run SLA validation monitoring"""
        logger.info(f"Starting SLA validation for {duration_minutes} minutes...")
        start_time = time.time()
        
        try:
            # Start SLA monitoring
            self.sla_monitor.start_monitoring()
            
            # Let it run for the specified duration
            await asyncio.sleep(duration_minutes * 60)
            
            # Generate report
            report = self.sla_monitor.generate_sla_report()
            
            execution_time = time.time() - start_time
            success = report['overall_metrics']['overall_compliance_rate'] >= 0.95
            
            result = TestExecutionResult(
                test_type="sla_validation",
                success=success,
                execution_time=execution_time,
                results=report
            )
            
            logger.info(f"SLA validation completed in {execution_time:.2f}s - Success: {success}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"SLA validation failed: {e}")
            
            return TestExecutionResult(
                test_type="sla_validation",
                success=False,
                execution_time=execution_time,
                results={},
                error_message=str(e)
            )
        finally:
            self.sla_monitor.stop_monitoring()

    async def run_synthetic_prompt_suites(self) -> TestExecutionResult:
        """Run synthetic prompt suites"""
        logger.info("Starting Synthetic Prompt Suites execution...")
        start_time = time.time()
        
        try:
            suite_results = await self.prompt_suites.run_all_suites()
            report = self.prompt_suites.generate_comprehensive_report(suite_results)
            
            execution_time = time.time() - start_time
            success = report['overall_metrics']['success_rate'] >= 0.90
            
            result = TestExecutionResult(
                test_type="synthetic_prompt_suites",
                success=success,
                execution_time=execution_time,
                results=report
            )
            
            logger.info(f"Synthetic Prompt Suites completed in {execution_time:.2f}s - Success: {success}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Synthetic Prompt Suites failed: {e}")
            
            return TestExecutionResult(
                test_type="synthetic_prompt_suites",
                success=False,
                execution_time=execution_time,
                results={},
                error_message=str(e)
            )

    async def run_guided_prompt_validation(self) -> TestExecutionResult:
        """Run specific Guided Prompt Confirmation validation"""
        logger.info("Starting Guided Prompt Confirmation validation...")
        start_time = time.time()
        
        try:
            # Test Guided Prompt specific scenarios
            guided_prompt_suites = [
                "guided_prompt_ambiguous",
                "guided_prompt_pii", 
                "guided_prompt_multilingual",
                "guided_prompt_constraints"
            ]
            
            suite_results = {}
            for suite_name in guided_prompt_suites:
                if suite_name in self.prompt_suites.suites:
                    result = await self.prompt_suites.run_suite(suite_name)
                    suite_results[suite_name] = result
            
            # Calculate Guided Prompt specific metrics
            total_tests = sum(result.total_tests for result in suite_results.values())
            guided_prompt_triggered = sum(
                sum(1 for r in result.results if r["guided_prompt_triggered"])
                for result in suite_results.values()
            )
            trigger_rate = guided_prompt_triggered / total_tests if total_tests > 0 else 0.0
            
            # Check Guided Prompt SLA compliance (≤ 500ms median, p95 ≤ 800ms)
            all_response_times = []
            for result in suite_results.values():
                all_response_times.extend([r["response_time"] for r in result.results if r["guided_prompt_triggered"]])
            
            if all_response_times:
                import statistics
                median_response_time = statistics.median(all_response_times)
                p95_response_time = statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) >= 20 else max(all_response_times)
                
                sla_compliant = median_response_time <= 0.5 and p95_response_time <= 0.8
            else:
                sla_compliant = False
                median_response_time = p95_response_time = 0.0
            
            report = {
                "guided_prompt_metrics": {
                    "total_tests": total_tests,
                    "guided_prompt_triggered": guided_prompt_triggered,
                    "trigger_rate": trigger_rate,
                    "median_response_time": median_response_time,
                    "p95_response_time": p95_response_time,
                    "sla_compliant": sla_compliant
                },
                "suite_results": {name: asdict(result) for name, result in suite_results.items()}
            }
            
            execution_time = time.time() - start_time
            success = sla_compliant and trigger_rate >= 0.3  # At least 30% trigger rate
            
            result = TestExecutionResult(
                test_type="guided_prompt_validation",
                success=success,
                execution_time=execution_time,
                results=report
            )
            
            logger.info(f"Guided Prompt validation completed in {execution_time:.2f}s - Success: {success}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Guided Prompt validation failed: {e}")
            
            return TestExecutionResult(
                test_type="guided_prompt_validation",
                success=False,
                execution_time=execution_time,
                results={},
                error_message=str(e)
            )

    async def run_comprehensive_tests(self, 
                                    include_test_matrix: bool = True,
                                    include_sla_validation: bool = True,
                                    include_prompt_suites: bool = True,
                                    include_guided_prompt: bool = True,
                                    sla_duration_minutes: int = 5) -> ComprehensiveTestReport:
        """Run comprehensive test suite"""
        
        execution_id = f"comprehensive_test_{int(time.time())}"
        self.start_time = time.time()
        
        logger.info(f"Starting comprehensive test execution: {execution_id}")
        logger.info(f"Test components: Matrix={include_test_matrix}, SLA={include_sla_validation}, "
                   f"Prompts={include_prompt_suites}, GuidedPrompt={include_guided_prompt}")
        
        self.execution_results = []
        
        try:
            # Run test matrix
            if include_test_matrix:
                result = await self.run_test_matrix()
                self.execution_results.append(result)
            
            # Run SLA validation
            if include_sla_validation:
                result = await self.run_sla_validation(sla_duration_minutes)
                self.execution_results.append(result)
            
            # Run synthetic prompt suites
            if include_prompt_suites:
                result = await self.run_synthetic_prompt_suites()
                self.execution_results.append(result)
            
            # Run Guided Prompt validation
            if include_guided_prompt:
                result = await self.run_guided_prompt_validation()
                self.execution_results.append(result)
            
        except Exception as e:
            logger.error(f"Comprehensive test execution failed: {e}")
            # Add error result
            self.execution_results.append(TestExecutionResult(
                test_type="comprehensive_execution",
                success=False,
                execution_time=0.0,
                results={},
                error_message=str(e)
            ))
        
        self.end_time = time.time()
        total_execution_time = self.end_time - self.start_time
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report(execution_id, total_execution_time)
        
        logger.info(f"Comprehensive test execution completed in {total_execution_time:.2f}s")
        logger.info(f"Overall success: {report.overall_success}")
        
        return report

    def _generate_comprehensive_report(self, execution_id: str, total_execution_time: float) -> ComprehensiveTestReport:
        """Generate comprehensive test report"""
        
        # Calculate overall success
        successful_tests = sum(1 for result in self.execution_results if result.success)
        total_tests = len(self.execution_results)
        overall_success = successful_tests == total_tests and total_tests > 0
        
        # Generate summary
        summary = {
            "total_test_components": total_tests,
            "successful_components": successful_tests,
            "failed_components": total_tests - successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0.0,
            "total_execution_time": total_execution_time,
            "component_results": {}
        }
        
        # Aggregate results by component
        for result in self.execution_results:
            summary["component_results"][result.test_type] = {
                "success": result.success,
                "execution_time": result.execution_time,
                "error_message": result.error_message
            }
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        report = ComprehensiveTestReport(
            execution_id=execution_id,
            start_time=self.start_time,
            end_time=self.end_time,
            total_execution_time=total_execution_time,
            test_results=self.execution_results,
            overall_success=overall_success,
            summary=summary,
            recommendations=recommendations
        )
        
        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        for result in self.execution_results:
            if not result.success:
                if result.test_type == "test_matrix":
                    recommendations.append("Test Matrix failed - investigate LLM provider and database performance issues")
                elif result.test_type == "sla_validation":
                    recommendations.append("SLA validation failed - optimize service response times and improve reliability")
                elif result.test_type == "synthetic_prompt_suites":
                    recommendations.append("Synthetic Prompt Suites failed - improve response quality and accuracy")
                elif result.test_type == "guided_prompt_validation":
                    recommendations.append("Guided Prompt validation failed - optimize refinement latency and improve trigger accuracy")
        
        # Add general recommendations based on overall performance
        if len(self.execution_results) > 0:
            avg_execution_time = sum(r.execution_time for r in self.execution_results) / len(self.execution_results)
            if avg_execution_time > 300:  # 5 minutes
                recommendations.append("Test execution times are high - consider optimizing test cases and infrastructure")
        
        return recommendations

    def save_report(self, report: ComprehensiveTestReport, filename: str = None):
        """Save comprehensive test report"""
        if filename is None:
            filename = f"comprehensive_test_report_{report.execution_id}.json"
        
        # Convert to serializable format
        serializable_report = {
            "execution_id": report.execution_id,
            "start_time": report.start_time,
            "end_time": report.end_time,
            "total_execution_time": report.total_execution_time,
            "test_results": [asdict(result) for result in report.test_results],
            "overall_success": report.overall_success,
            "summary": report.summary,
            "recommendations": report.recommendations
        }
        
        with open(filename, 'w') as f:
            json.dump(serializable_report, f, indent=2)
        
        logger.info(f"Comprehensive test report saved to {filename}")

    def print_summary(self, report: ComprehensiveTestReport):
        """Print test execution summary"""
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST EXECUTION SUMMARY")
        print("="*60)
        print(f"Execution ID: {report.execution_id}")
        print(f"Start Time: {time.ctime(report.start_time)}")
        print(f"End Time: {time.ctime(report.end_time)}")
        print(f"Total Execution Time: {report.total_execution_time:.2f} seconds")
        print(f"Overall Success: {'✅ PASS' if report.overall_success else '❌ FAIL'}")
        print()
        
        print("COMPONENT RESULTS:")
        for result in report.test_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"  {result.test_type}: {status} ({result.execution_time:.2f}s)")
            if result.error_message:
                print(f"    Error: {result.error_message}")
        
        print()
        print("SUMMARY METRICS:")
        print(f"  Total Components: {report.summary['total_test_components']}")
        print(f"  Successful: {report.summary['successful_components']}")
        print(f"  Failed: {report.summary['failed_components']}")
        print(f"  Success Rate: {report.summary['success_rate']:.2%}")
        
        if report.recommendations:
            print()
            print("RECOMMENDATIONS:")
            for i, recommendation in enumerate(report.recommendations, 1):
                print(f"  {i}. {recommendation}")
        
        print("="*60)

async def main():
    """Main entry point for comprehensive test runner"""
    parser = argparse.ArgumentParser(description="SarvanOM v2 Comprehensive Test Runner")
    parser.add_argument("--base-url", default="http://localhost:8004", help="Base URL for the API")
    parser.add_argument("--test-matrix", action="store_true", help="Run test matrix")
    parser.add_argument("--sla-validation", action="store_true", help="Run SLA validation")
    parser.add_argument("--prompt-suites", action="store_true", help="Run synthetic prompt suites")
    parser.add_argument("--guided-prompt", action="store_true", help="Run Guided Prompt validation")
    parser.add_argument("--all", action="store_true", help="Run all test components")
    parser.add_argument("--sla-duration", type=int, default=5, help="SLA validation duration in minutes")
    parser.add_argument("--output", help="Output filename for the report")
    
    args = parser.parse_args()
    
    # If no specific tests are selected, run all
    if not any([args.test_matrix, args.sla_validation, args.prompt_suites, args.guided_prompt]):
        args.all = True
    
    if args.all:
        args.test_matrix = True
        args.sla_validation = True
        args.prompt_suites = True
        args.guided_prompt = True
    
    # Create test runner
    runner = ComprehensiveTestRunner(args.base_url)
    
    try:
        # Run comprehensive tests
        report = await runner.run_comprehensive_tests(
            include_test_matrix=args.test_matrix,
            include_sla_validation=args.sla_validation,
            include_prompt_suites=args.prompt_suites,
            include_guided_prompt=args.guided_prompt,
            sla_duration_minutes=args.sla_duration
        )
        
        # Save report
        runner.save_report(report, args.output)
        
        # Print summary
        runner.print_summary(report)
        
        # Exit with appropriate code
        sys.exit(0 if report.overall_success else 1)
        
    except KeyboardInterrupt:
        logger.info("Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
