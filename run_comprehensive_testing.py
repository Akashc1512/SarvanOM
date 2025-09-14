"""
Comprehensive Testing Orchestrator

This script orchestrates all phases of testing for the SarvanOM platform:
1. Load Testing
2. User Acceptance Testing  
3. Performance Monitoring
4. Production Deployment Simulation

Usage:
    python run_comprehensive_testing.py [--phase=all|load|uat|performance|deployment]
"""

import asyncio
import argparse
import logging
import sys
import time
from datetime import datetime
from typing import Dict, Any

# Import testing modules
from load_testing.load_test_framework import run_comprehensive_load_test
from load_testing.service_specific_tests import run_service_specific_tests
from load_testing.performance_monitor import run_performance_monitoring
from user_acceptance_testing.uat_framework import run_user_acceptance_testing
from operations.deployment_pipeline import run_production_deployment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'comprehensive_testing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ComprehensiveTestingOrchestrator:
    """Orchestrates all testing phases"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.start_time = None
        self.end_time = None
    
    async def run_load_testing(self) -> Dict[str, Any]:
        """Run comprehensive load testing"""
        logger.info("🚀 Starting Load Testing Phase...")
        
        try:
            # Run comprehensive load tests
            load_results = await run_comprehensive_load_test()
            
            # Run service-specific tests
            await run_service_specific_tests()
            
            self.results["load_testing"] = {
                "status": "completed",
                "results": load_results,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("✅ Load Testing Phase Completed Successfully")
            return self.results["load_testing"]
            
        except Exception as e:
            logger.error(f"❌ Load Testing Phase Failed: {e}")
            self.results["load_testing"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return self.results["load_testing"]
    
    async def run_user_acceptance_testing(self) -> Dict[str, Any]:
        """Run user acceptance testing"""
        logger.info("👥 Starting User Acceptance Testing Phase...")
        
        try:
            uat_results = await run_user_acceptance_testing()
            
            self.results["user_acceptance_testing"] = {
                "status": "completed",
                "results": uat_results,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("✅ User Acceptance Testing Phase Completed Successfully")
            return self.results["user_acceptance_testing"]
            
        except Exception as e:
            logger.error(f"❌ User Acceptance Testing Phase Failed: {e}")
            self.results["user_acceptance_testing"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return self.results["user_acceptance_testing"]
    
    async def run_performance_monitoring(self) -> Dict[str, Any]:
        """Run performance monitoring"""
        logger.info("📊 Starting Performance Monitoring Phase...")
        
        try:
            await run_performance_monitoring()
            
            self.results["performance_monitoring"] = {
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("✅ Performance Monitoring Phase Completed Successfully")
            return self.results["performance_monitoring"]
            
        except Exception as e:
            logger.error(f"❌ Performance Monitoring Phase Failed: {e}")
            self.results["performance_monitoring"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return self.results["performance_monitoring"]
    
    async def run_deployment_simulation(self) -> Dict[str, Any]:
        """Run production deployment simulation"""
        logger.info("🚀 Starting Production Deployment Simulation...")
        
        try:
            deployment_success = await run_production_deployment()
            
            self.results["deployment_simulation"] = {
                "status": "completed" if deployment_success else "failed",
                "deployment_success": deployment_success,
                "timestamp": datetime.now().isoformat()
            }
            
            if deployment_success:
                logger.info("✅ Production Deployment Simulation Completed Successfully")
            else:
                logger.warning("⚠️ Production Deployment Simulation Failed")
            
            return self.results["deployment_simulation"]
            
        except Exception as e:
            logger.error(f"❌ Production Deployment Simulation Failed: {e}")
            self.results["deployment_simulation"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return self.results["deployment_simulation"]
    
    async def run_all_phases(self) -> Dict[str, Any]:
        """Run all testing phases"""
        logger.info("🎯 Starting Comprehensive Testing - All Phases")
        self.start_time = time.time()
        
        # Phase 1: Load Testing
        await self.run_load_testing()
        await asyncio.sleep(5)  # Brief pause between phases
        
        # Phase 2: User Acceptance Testing
        await self.run_user_acceptance_testing()
        await asyncio.sleep(5)
        
        # Phase 3: Performance Monitoring
        await self.run_performance_monitoring()
        await asyncio.sleep(5)
        
        # Phase 4: Deployment Simulation
        await self.run_deployment_simulation()
        
        self.end_time = time.time()
        
        # Generate final report
        final_report = self.generate_final_report()
        print(final_report)
        
        return self.results
    
    def generate_final_report(self) -> str:
        """Generate comprehensive final report"""
        if not self.start_time or not self.end_time:
            return "Testing not completed - no timing data available."
        
        total_duration = self.end_time - self.start_time
        
        report = []
        report.append("=" * 100)
        report.append("🎉 SARVANOM COMPREHENSIVE TESTING FINAL REPORT")
        report.append("=" * 100)
        report.append(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"⏱️  Total Duration: {total_duration:.2f} seconds ({total_duration/60:.1f} minutes)")
        report.append("")
        
        # Phase Results Summary
        report.append("📋 PHASE RESULTS SUMMARY")
        report.append("-" * 50)
        
        phases = [
            ("load_testing", "🚀 Load Testing"),
            ("user_acceptance_testing", "👥 User Acceptance Testing"),
            ("performance_monitoring", "📊 Performance Monitoring"),
            ("deployment_simulation", "🚀 Deployment Simulation")
        ]
        
        completed_phases = 0
        failed_phases = 0
        
        for phase_key, phase_name in phases:
            if phase_key in self.results:
                phase_result = self.results[phase_key]
                status = phase_result.get("status", "unknown")
                
                if status == "completed":
                    status_icon = "✅"
                    completed_phases += 1
                elif status == "failed":
                    status_icon = "❌"
                    failed_phases += 1
                else:
                    status_icon = "⚠️"
                
                report.append(f"{status_icon} {phase_name}: {status.upper()}")
                
                # Add specific results for UAT
                if phase_key == "user_acceptance_testing" and "results" in phase_result:
                    uat_results = phase_result["results"]
                    report.append(f"   📊 Pass Rate: {uat_results.get('pass_rate', 0):.1f}%")
                    report.append(f"   📈 Scenarios: {uat_results.get('passed_scenarios', 0)}/{uat_results.get('total_scenarios', 0)} passed")
                
                # Add deployment success
                if phase_key == "deployment_simulation" and "deployment_success" in phase_result:
                    deployment_success = phase_result["deployment_success"]
                    report.append(f"   🚀 Deployment: {'SUCCESS' if deployment_success else 'FAILED'}")
            else:
                report.append(f"⚠️ {phase_name}: NOT RUN")
        
        report.append("")
        
        # Overall Assessment
        report.append("🎯 OVERALL ASSESSMENT")
        report.append("-" * 50)
        
        total_phases = len(phases)
        success_rate = (completed_phases / total_phases * 100) if total_phases > 0 else 0
        
        if success_rate == 100:
            report.append("🎉 EXCELLENT: All testing phases completed successfully!")
            report.append("✅ System is ready for production deployment")
        elif success_rate >= 75:
            report.append("✅ GOOD: Most testing phases completed successfully")
            report.append("⚠️ Some issues detected - review failed phases")
        elif success_rate >= 50:
            report.append("⚠️ MODERATE: Half of testing phases completed")
            report.append("🔧 Significant issues detected - address before production")
        else:
            report.append("❌ POOR: Most testing phases failed")
            report.append("🚨 Major issues detected - system not ready for production")
        
        report.append(f"📊 Success Rate: {success_rate:.1f}% ({completed_phases}/{total_phases} phases)")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 50)
        
        if failed_phases > 0:
            report.append("🔧 Address the following issues:")
            for phase_key, phase_name in phases:
                if phase_key in self.results and self.results[phase_key].get("status") == "failed":
                    error = self.results[phase_key].get("error", "Unknown error")
                    report.append(f"   • {phase_name}: {error}")
        else:
            report.append("🎉 All systems are functioning correctly!")
            report.append("🚀 Proceed with production deployment")
            report.append("📊 Continue monitoring in production environment")
        
        report.append("")
        report.append("📁 Detailed logs and results saved to individual files")
        report.append("=" * 100)
        
        return "\n".join(report)
    
    def save_results(self, filename: str = None):
        """Save comprehensive results to JSON file"""
        if not filename:
            filename = f"comprehensive_testing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        
        results_with_metadata = {
            "test_run": {
                "start_time": self.start_time,
                "end_time": self.end_time,
                "duration_seconds": (self.end_time - self.start_time) if self.start_time and self.end_time else None,
                "timestamp": datetime.now().isoformat()
            },
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(results_with_metadata, f, indent=2)
        
        logger.info(f"Comprehensive testing results saved to {filename}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="SarvanOM Comprehensive Testing Orchestrator")
    parser.add_argument(
        "--phase", 
        choices=["all", "load", "uat", "performance", "deployment"],
        default="all",
        help="Testing phase to run (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    orchestrator = ComprehensiveTestingOrchestrator()
    
    try:
        if args.phase == "all":
            results = await orchestrator.run_all_phases()
        elif args.phase == "load":
            results = await orchestrator.run_load_testing()
        elif args.phase == "uat":
            results = await orchestrator.run_user_acceptance_testing()
        elif args.phase == "performance":
            results = await orchestrator.run_performance_monitoring()
        elif args.phase == "deployment":
            results = await orchestrator.run_deployment_simulation()
        
        # Save results
        orchestrator.save_results()
        
        # Exit with appropriate code
        if args.phase == "all":
            # Check if all phases completed successfully
            all_successful = all(
                result.get("status") == "completed" 
                for result in orchestrator.results.values()
            )
            sys.exit(0 if all_successful else 1)
        else:
            # Check if the specific phase completed successfully
            phase_result = orchestrator.results.get(args.phase, {})
            sys.exit(0 if phase_result.get("status") == "completed" else 1)
            
    except KeyboardInterrupt:
        logger.info("Testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
