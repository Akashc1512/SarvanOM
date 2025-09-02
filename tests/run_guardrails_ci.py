#!/usr/bin/env python3
"""
CI/CD Integration Script for Automated Guardrails

This script is designed to be run in CI/CD pipelines to:
1. Run the golden test suite
2. Check quality thresholds
3. Fail the build if regressions are detected
4. Generate reports for monitoring

Usage in CI/CD:
    python tests/run_guardrails_ci.py

Exit codes:
    0: All tests passed, build can proceed
    1: Quality thresholds not met, build should fail
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.golden_test_suite import GoldenTestSuite

# Configure logging for CI environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('guardrails_ci.log')
    ]
)

logger = logging.getLogger(__name__)


async def run_ci_guardrails():
    """Run guardrails in CI environment."""
    logger.info("🚀 Starting CI Guardrails Execution")
    
    try:
        # Initialize and run golden test suite
        suite = GoldenTestSuite()
        results, should_fail = await suite.run_golden_tests()
        
        # Log summary for CI
        overall_metrics = results["overall_metrics"]
        logger.info("=" * 60)
        logger.info("📊 CI GUARDRAILS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {overall_metrics['total_tests']}")
        logger.info(f"Passed: {overall_metrics['total_passed']}")
        logger.info(f"Failed: {overall_metrics['total_failed']}")
        logger.info(f"Success Rate: {overall_metrics['success_rate']:.1%}")
        logger.info(f"Total Duration: {overall_metrics['total_duration_ms']:.2f}ms")
        
        # Log category results
        for category, summary in results["test_summary"].items():
            success_rate = summary["passed"] / summary["total_tests"]
            status = "✅ PASS" if success_rate >= 0.8 else "❌ FAIL"
            logger.info(f"{category}: {status} ({summary['passed']}/{summary['total_tests']})")
        
        # Log failure scenario results
        logger.info("\n🔧 Failure Scenario Results:")
        for scenario, result in results["failure_scenario_results"].items():
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            logger.info(f"  {scenario}: {status}")
        
        # Determine build outcome
        if should_fail:
            logger.error("🚨 BUILD FAILED - Quality thresholds not met")
            logger.error("The following issues were detected:")
            
            # Check specific failure reasons
            if overall_metrics["success_rate"] < 0.8:
                logger.error(f"  - Overall success rate {overall_metrics['success_rate']:.1%} < 80%")
            
            for category, summary in results["test_summary"].items():
                category_success_rate = summary["passed"] / summary["total_tests"]
                if category_success_rate < 0.7:
                    logger.error(f"  - {category} success rate {category_success_rate:.1%} < 70%")
            
            if overall_metrics["total_duration_ms"] > 5000:
                logger.error(f"  - Total duration {overall_metrics['total_duration_ms']:.2f}ms > 5000ms")
            
            return False
        else:
            logger.info("✅ BUILD SUCCESS - All quality thresholds met")
            return True
            
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR in CI Guardrails: {e}")
        logger.error("Build should fail due to guardrails execution error")
        return False


def main():
    """Main entry point for CI execution."""
    try:
        success = asyncio.run(run_ci_guardrails())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.error("🛑 CI Guardrails interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error in CI Guardrails: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
