#!/usr/bin/env python3
"""
Comprehensive Guardrails Test Runner for SarvanOM

This script runs all guardrails tests:
1. Golden test suite (quality, latency, groundedness)
2. Failure scenario tests (graceful degradation)
3. Regression detection and analysis
4. Artifact generation and CI integration

Ensures the build fails on measurable regressions.
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append('.')

class GuardrailsTestRunner:
    """Comprehensive test runner for all guardrails."""
    
    def __init__(self):
        self.results = {}
        self.overall_success = True
        self.output_dir = "code_garden"
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(exist_ok=True)
    
    async def run_all_guardrails(self) -> bool:
        """Run all guardrail tests and return overall success."""
        print("🚀 SARVANOM GUARDRAILS TEST RUNNER")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Output Directory: {self.output_dir}")
        print()
        
        # Run golden test suite
        print("🔧 PHASE 1: Golden Test Suite")
        print("-" * 40)
        golden_success = await self._run_golden_tests()
        self.results['golden_tests'] = golden_success
        
        # Run failure scenario tests
        print("\n🔧 PHASE 2: Failure Scenario Tests")
        print("-" * 40)
        failure_success = await self._run_failure_scenarios()
        self.results['failure_scenarios'] = failure_success
        
        # Run regression analysis
        print("\n🔧 PHASE 3: Regression Analysis")
        print("-" * 40)
        regression_success = await self._run_regression_analysis()
        self.results['regression_analysis'] = regression_success
        
        # Generate comprehensive artifacts
        print("\n🔧 PHASE 4: Artifact Generation")
        print("-" * 40)
        self._generate_comprehensive_artifacts()
        
        # Determine overall success
        self.overall_success = all(self.results.values())
        
        # Print final summary
        self._print_final_summary()
        
        return self.overall_success
    
    async def _run_golden_tests(self) -> bool:
        """Run the golden test suite."""
        try:
            from tests.golden_test_suite import GoldenTestSuite
            
            print("   Running golden test suite...")
            test_suite = GoldenTestSuite()
            
            # Run tests
            results = await test_suite.run_golden_tests()
            
            # Analyze results
            metrics = test_suite.analyze_results()
            
            # Store results for artifact generation
            self.results['golden_metrics'] = metrics
            self.results['golden_results'] = results
            
            # Check if build should fail
            if metrics.build_should_fail:
                print("   ❌ Golden tests indicate build should fail")
                return False
            else:
                print("   ✅ Golden tests passed - build can proceed")
                return True
                
        except Exception as e:
            print(f"   ❌ Golden test suite failed: {e}")
            return False
    
    async def _run_failure_scenarios(self) -> bool:
        """Run failure scenario tests."""
        try:
            from tests.failure_scenario_tests import FailureScenarioTester
            
            print("   Running failure scenario tests...")
            tester = FailureScenarioTester()
            
            # Run tests
            results = await tester.run_all_failure_scenarios()
            
            # Analyze results
            analysis = tester.analyze_failure_scenarios()
            
            # Store results for artifact generation
            self.results['failure_analysis'] = analysis
            self.results['failure_results'] = results
            
            # Check if graceful degradation requirements are met
            if analysis['overall_success']:
                print("   ✅ Failure scenarios handled gracefully")
                return True
            else:
                print("   ❌ Some failure scenarios not handled gracefully")
                return False
                
        except Exception as e:
            print(f"   ❌ Failure scenario tests failed: {e}")
            return False
    
    async def _run_regression_analysis(self) -> bool:
        """Run regression analysis and trend monitoring."""
        try:
            print("   Analyzing for regressions...")
            
            # Load baseline metrics if available
            baseline_file = Path(self.output_dir) / "baseline_metrics.json"
            baseline_metrics = None
            
            if baseline_file.exists():
                with open(baseline_file, 'r') as f:
                    baseline_metrics = json.load(f)
                print("   ✅ Baseline metrics loaded for comparison")
            else:
                print("   ⚠️ No baseline metrics found - creating new baseline")
            
            # Get current metrics
            current_metrics = {
                'golden_tests': self.results.get('golden_metrics', {}),
                'failure_scenarios': self.results.get('failure_analysis', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            # Perform regression analysis
            regression_analysis = self._analyze_regressions(baseline_metrics, current_metrics)
            
            # Store results
            self.results['regression_analysis'] = regression_analysis
            self.results['current_metrics'] = current_metrics
            
            # Check if regressions are detected
            if regression_analysis['regressions_detected']:
                print("   ❌ Regressions detected - build should fail")
                return False
            else:
                print("   ✅ No regressions detected - build can proceed")
                
                # Update baseline if no regressions
                if not baseline_metrics or regression_analysis['baseline_updated']:
                    self._update_baseline(current_metrics)
                
                return True
                
        except Exception as e:
            print(f"   ❌ Regression analysis failed: {e}")
            return False
    
    def _analyze_regressions(self, baseline: Dict, current: Dict) -> Dict[str, Any]:
        """Analyze current metrics against baseline for regressions."""
        if not baseline:
            return {
                'regressions_detected': False,
                'baseline_updated': True,
                'reason': 'No baseline available - creating new one'
            }
        
        regressions = []
        
        # Compare golden test metrics
        if 'golden_metrics' in baseline and 'golden_metrics' in current:
            baseline_golden = baseline['golden_metrics']
            current_golden = current['golden_metrics']
            
            # Check pass rate regression
            baseline_pass_rate = baseline_golden.get('passed_tests', 0) / max(baseline_golden.get('total_tests', 1), 1)
            current_pass_rate = current_golden.get('passed_tests', 0) / max(current_golden.get('total_tests', 1), 1)
            
            if current_pass_rate < baseline_pass_rate * 0.95:  # 5% regression threshold
                regressions.append(f"Pass rate regression: {current_pass_rate:.1%} vs {baseline_pass_rate:.1%}")
            
            # Check latency regression
            baseline_latency = baseline_golden.get('avg_latency_ms', 0)
            current_latency = current_golden.get('avg_latency_ms', 0)
            
            if current_latency > baseline_latency * 1.15:  # 15% latency increase threshold
                regressions.append(f"Latency regression: {current_latency:.1f}ms vs {baseline_latency:.1f}ms")
            
            # Check citation coverage regression
            baseline_citation = baseline_golden.get('avg_citation_coverage', 0)
            current_citation = current_golden.get('avg_citation_coverage', 0)
            
            if current_citation < baseline_citation * 0.95:  # 5% citation coverage drop threshold
                regressions.append(f"Citation coverage regression: {current_citation:.1%} vs {baseline_citation:.1%}")
        
        # Compare failure scenario metrics
        if 'failure_scenarios' in baseline and 'failure_scenarios' in current:
            baseline_failure = baseline['failure_scenarios']
            current_failure = current['failure_scenarios']
            
            baseline_graceful = baseline_failure.get('graceful_degradation_rate', 0)
            current_graceful = current_failure.get('graceful_degradation_rate', 0)
            
            if current_graceful < baseline_graceful * 0.9:  # 10% graceful degradation regression threshold
                regressions.append(f"Graceful degradation regression: {current_graceful:.1%} vs {baseline_graceful:.1%}")
        
        # Determine if regressions are detected
        regressions_detected = len(regressions) > 0
        
        return {
            'regressions_detected': regressions_detected,
            'baseline_updated': not regressions_detected,
            'regressions': regressions,
            'baseline_timestamp': baseline.get('timestamp', 'unknown'),
            'current_timestamp': current.get('timestamp', 'unknown')
        }
    
    def _update_baseline(self, current_metrics: Dict) -> None:
        """Update baseline metrics with current successful run."""
        baseline_file = Path(self.output_dir) / "baseline_metrics.json"
        
        with open(baseline_file, 'w') as f:
            json.dump(current_metrics, f, indent=2)
        
        print(f"   ✅ Baseline metrics updated: {baseline_file}")
    
    def _generate_comprehensive_artifacts(self) -> None:
        """Generate comprehensive test artifacts."""
        print("   Generating comprehensive artifacts...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate comprehensive JSON report
        comprehensive_report = {
            'timestamp': timestamp,
            'overall_success': self.overall_success,
            'test_results': self.results,
            'summary': {
                'golden_tests_passed': self.results.get('golden_tests', False),
                'failure_scenarios_passed': self.results.get('failure_scenarios', False),
                'regression_analysis_passed': self.results.get('regression_analysis', False),
                'build_should_fail': not self.overall_success
            }
        }
        
        # Save comprehensive report
        json_file = Path(self.output_dir) / f"guardrails_comprehensive_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            # Use custom encoder to handle dataclasses
            json.dump(comprehensive_report, f, indent=2, default=lambda obj: obj.__dict__ if hasattr(obj, '__dict__') else str(obj))
        
        # Generate comprehensive HTML report
        html_report = self._generate_comprehensive_html(comprehensive_report)
        html_file = Path(self.output_dir) / f"guardrails_comprehensive_report_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # Generate comprehensive Markdown report
        md_report = self._generate_comprehensive_markdown(comprehensive_report)
        md_file = Path(self.output_dir) / f"guardrails_comprehensive_report_{timestamp}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_report)
        
        # Create latest symlinks
        latest_files = [
            ("guardrails_comprehensive_report_latest.json", json_file),
            ("guardrails_comprehensive_report_latest.html", html_file),
            ("guardrails_comprehensive_report_latest.md", md_file)
        ]
        
        for latest_name, source_file in latest_files:
            latest_file = Path(self.output_dir) / latest_name
            try:
                if latest_file.exists():
                    latest_file.unlink()
                latest_file.symlink_to(source_file.name)
            except:
                # On Windows, symlinks might not work, so copy instead
                import shutil
                shutil.copy2(source_file, latest_file)
        
        print(f"   ✅ Comprehensive artifacts generated:")
        print(f"      JSON: {json_file}")
        print(f"      HTML: {html_file}")
        print(f"      Markdown: {md_file}")
    
    def _generate_comprehensive_html(self, data: Dict) -> str:
        """Generate comprehensive HTML report."""
        summary = data['summary']
        timestamp = data['timestamp']
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SarvanOM Guardrails Comprehensive Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .status {{ padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .success {{ background: #e8f5e8; }}
        .failure {{ background: #ffe8e8; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ background: #fff; padding: 15px; border: 1px solid #ddd; border-radius: 5px; text-align: center; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .section h3 {{ margin-top: 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 SarvanOM Guardrails Comprehensive Report</h1>
        <p><strong>Timestamp:</strong> {timestamp}</p>
        <p><strong>Overall Status:</strong> {'✅ SUCCESS' if summary['build_should_fail'] == False else '❌ FAILURE'}</p>
    </div>
    
    <div class="{'failure' if summary['build_should_fail'] else 'success'}">
        <h2>{'❌ BUILD SHOULD FAIL' if summary['build_should_fail'] else '✅ BUILD SHOULD PASS'}</h2>
        <p><strong>Reason:</strong> {'Quality regressions or failures detected' if summary['build_should_fail'] else 'All guardrails passed successfully'}</p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <div class="metric-value">{'✅' if summary['golden_tests_passed'] else '❌'}</div>
            <div class="metric-label">Golden Tests</div>
        </div>
        <div class="metric">
            <div class="metric-value">{'✅' if summary['failure_scenarios_passed'] else '❌'}</div>
            <div class="metric-label">Failure Scenarios</div>
        </div>
        <div class="metric">
            <div class="metric-value">{'✅' if summary['regression_analysis_passed'] else '❌'}</div>
            <div class="metric-label">Regression Analysis</div>
        </div>
    </div>
    
    <div class="section">
        <h3>📊 Test Results Summary</h3>
        <p><strong>Golden Tests:</strong> {'PASSED' if summary['golden_tests_passed'] else 'FAILED'}</p>
        <p><strong>Failure Scenarios:</strong> {'PASSED' if summary['failure_scenarios_passed'] else 'FAILED'}</p>
        <p><strong>Regression Analysis:</strong> {'PASSED' if summary['regression_analysis_passed'] else 'FAILED'}</p>
    </div>
    
    <div class="section">
        <h3>🎯 Build Decision</h3>
        <p><strong>Final Decision:</strong> {'BUILD SHOULD FAIL' if summary['build_should_fail'] else 'BUILD CAN PROCEED'}</p>
        <p><strong>Reason:</strong> {'Quality thresholds exceeded or regressions detected' if summary['build_should_fail'] else 'All quality and performance requirements met'}</p>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_comprehensive_markdown(self, data: Dict) -> str:
        """Generate comprehensive Markdown report."""
        summary = data['summary']
        timestamp = data['timestamp']
        
        md = f"""# 🚀 SarvanOM Guardrails Comprehensive Report

**Timestamp:** {timestamp}  
**Overall Status:** {'✅ SUCCESS' if summary['build_should_fail'] == False else '❌ FAILURE'}

## 🎯 Build Decision

{'❌ **BUILD SHOULD FAIL**' if summary['build_should_fail'] else '✅ **BUILD CAN PROCEED**'}

**Reason:** {'Quality regressions or failures detected' if summary['build_should_fail'] else 'All guardrails passed successfully'}

## 📊 Test Results Summary

| Test Category | Status |
|---------------|--------|
| Golden Tests | {'✅ PASSED' if summary['golden_tests_passed'] else '❌ FAILED'} |
| Failure Scenarios | {'✅ PASSED' if summary['failure_scenarios_passed'] else '❌ FAILED'} |
| Regression Analysis | {'✅ PASSED' if summary['regression_analysis_passed'] else '❌ FAILED'} |

## 🔧 Test Details

### Golden Tests
- **Status:** {'PASSED' if summary['golden_tests_passed'] else 'FAILED'}
- **Purpose:** Quality, latency, and groundedness validation
- **Impact:** {'Build can proceed' if summary['golden_tests_passed'] else 'Build should fail'}

### Failure Scenarios
- **Status:** {'PASSED' if summary['failure_scenarios_passed'] else 'FAILED'}
- **Purpose:** Graceful degradation testing
- **Impact:** {'System fault tolerance verified' if summary['failure_scenarios_passed'] else 'Fault tolerance issues detected'}

### Regression Analysis
- **Status:** {'PASSED' if summary['regression_analysis_passed'] else 'FAILED'}
- **Purpose:** Trend monitoring and regression detection
- **Impact:** {'No regressions detected' if summary['regression_analysis_passed'] else 'Regressions detected'}

## 🎯 Final Decision

**BUILD STATUS:** {'❌ FAIL' if summary['build_should_fail'] else '✅ PASS'}

**Reason:** {'Quality thresholds exceeded or regressions detected' if summary['build_should_fail'] else 'All quality and performance requirements met'}

---
*Report generated by SarvanOM Guardrails Test Runner*
"""
        return md
    
    def _print_final_summary(self) -> None:
        """Print final test summary."""
        print(f"\n🎯 FINAL GUARDRAILS SUMMARY")
        print("=" * 50)
        print(f"Golden Tests: {'✅ PASSED' if self.results.get('golden_tests') else '❌ FAILED'}")
        print(f"Failure Scenarios: {'✅ PASSED' if self.results.get('failure_scenarios') else '❌ FAILED'}")
        print(f"Regression Analysis: {'✅ PASSED' if self.results.get('regression_analysis') else '❌ FAILED'}")
        print(f"Overall Success: {'✅ YES' if self.overall_success else '❌ NO'}")
        
        if self.overall_success:
            print(f"\n🎉 All guardrails passed successfully!")
            print("   Build can proceed with confidence.")
        else:
            print(f"\n❌ Some guardrails failed!")
            print("   Build should fail to prevent quality regression.")
        
        print(f"\n📊 Artifacts generated in: {self.output_dir}/")
        print(f"   Latest reports available with 'latest' suffix")

async def main():
    """Main function for running all guardrails."""
    # Initialize runner
    runner = GuardrailsTestRunner()
    
    # Run all guardrails
    success = await runner.run_all_guardrails()
    
    # Exit with appropriate code
    if success:
        print(f"\n🎉 Guardrails test runner completed successfully!")
        print("   All quality checks passed.")
        sys.exit(0)
    else:
        print(f"\n❌ Guardrails test runner detected issues!")
        print("   Build should fail to prevent quality regression.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
