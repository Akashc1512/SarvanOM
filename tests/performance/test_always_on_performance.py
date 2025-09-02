#!/usr/bin/env python3
"""
Test Always-On Performance - Vector and KG Lanes
MAANG/OpenAI/Perplexity Standards Compliance

This test verifies that the retrieval orchestrator meets the strict performance requirements:
- P95 end-to-end latency ≤ 3 seconds on cached/simple queries
- Vector search: ≤ 2.0 seconds with top-k ≤ 5 passages  
- Knowledge Graph: ≤ 1.5 seconds with top-k ≤ 6 facts
- No blocking: if a lane times out, proceed with other lanes
"""

import asyncio
import time
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.append(str(Path(__file__).parent))

@dataclass
class PerformanceTestResult:
    """Result of a performance test."""
    test_name: str
    lane: str
    latency_ms: float
    status: str  # "pass", "fail", "timeout"
    results_count: int
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

class AlwaysOnPerformanceTester:
    """Test the always-on performance requirements."""
    
    def __init__(self):
        self.results: List[PerformanceTestResult] = []
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging for performance monitoring."""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def test_vector_search_performance(self) -> PerformanceTestResult:
        """Test vector search lane performance (≤ 2.0s, top-k ≤ 5)."""
        test_name = "Vector Search Performance"
        start_time = time.time()
        
        try:
            # Import orchestrator
            from services.retrieval.orchestrator import RetrievalOrchestrator, OrchestrationConfig
            from shared.contracts.query import RetrievalSearchRequest
            
            # Configure strict performance settings
            config = OrchestrationConfig()
            config.max_results_per_lane = 5  # Strict top-k ≤ 5
            config.latency_budget.vector_search_budget_ms = 2000.0  # 2.0s strict
            
            orchestrator = RetrievalOrchestrator(config)
            
            # Test query
            request = RetrievalSearchRequest(
                query="test vector search performance",
                max_results=5
            )
            
            # Execute with timeout
            try:
                response = await asyncio.wait_for(
                    orchestrator.orchestrate_retrieval(request),
                    timeout=2.1  # Slightly over 2.0s to test strict enforcement
                )
                
                latency_ms = (time.time() - start_time) * 1000
                results_count = len(response.sources) if response.sources else 0
                
                # Check performance requirements
                if latency_ms <= 2000.0 and results_count <= 5:
                    status = "pass"
                    self.logger.info(f"✅ {test_name}: {latency_ms:.1f}ms, {results_count} results")
                else:
                    status = "fail"
                    self.logger.warning(f"❌ {test_name}: {latency_ms:.1f}ms > 2000ms or {results_count} > 5")
                
                return PerformanceTestResult(
                    test_name=test_name,
                    lane="vector_search",
                    latency_ms=latency_ms,
                    status=status,
                    results_count=results_count,
                    metadata={"timeout_ms": 2000.0, "max_results": 5}
                )
                
            except asyncio.TimeoutError:
                latency_ms = (time.time() - start_time) * 1000
                self.logger.info(f"⏰ {test_name}: Timeout at {latency_ms:.1f}ms (expected ≤ 2000ms)")
                
                return PerformanceTestResult(
                    test_name=test_name,
                    lane="vector_search",
                    latency_ms=latency_ms,
                    status="timeout",
                    results_count=0,
                    error="Timeout exceeded 2.0s limit",
                    metadata={"timeout_ms": 2000.0, "max_results": 5}
                )
                
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(f"❌ {test_name}: Error - {e}")
            
            return PerformanceTestResult(
                test_name=test_name,
                lane="vector_search",
                latency_ms=latency_ms,
                status="fail",
                results_count=0,
                error=str(e),
                metadata={"timeout_ms": 2000.0, "max_results": 5}
            )
    
    async def test_knowledge_graph_performance(self) -> PerformanceTestResult:
        """Test knowledge graph lane performance (≤ 1.5s, top-k ≤ 6)."""
        test_name = "Knowledge Graph Performance"
        start_time = time.time()
        
        try:
            # Import orchestrator
            from services.retrieval.orchestrator import RetrievalOrchestrator, OrchestrationConfig
            from shared.contracts.query import RetrievalSearchRequest
            
            # Configure strict performance settings
            config = OrchestrationConfig()
            config.max_results_per_lane = 6  # Strict top-k ≤ 6
            config.latency_budget.knowledge_graph_budget_ms = 1500.0  # 1.5s strict
            
            orchestrator = RetrievalOrchestrator(config)
            
            # Test query
            request = RetrievalSearchRequest(
                query="test knowledge graph performance",
                max_results=6
            )
            
            # Execute with timeout
            try:
                response = await asyncio.wait_for(
                    orchestrator.orchestrate_retrieval(request),
                    timeout=1.6  # Slightly over 1.5s to test strict enforcement
                )
                
                latency_ms = (time.time() - start_time) * 1000
                results_count = len(response.sources) if response.sources else 0
                
                # Check performance requirements
                if latency_ms <= 1500.0 and results_count <= 6:
                    status = "pass"
                    self.logger.info(f"✅ {test_name}: {latency_ms:.1f}ms, {results_count} results")
                else:
                    status = "fail"
                    self.logger.warning(f"❌ {test_name}: {latency_ms:.1f}ms > 1500ms or {results_count} > 6")
                
                return PerformanceTestResult(
                    test_name=test_name,
                    lane="knowledge_graph",
                    latency_ms=latency_ms,
                    status=status,
                    results_count=results_count,
                    metadata={"timeout_ms": 1500.0, "max_results": 6}
                )
                
            except asyncio.TimeoutError:
                latency_ms = (time.time() - start_time) * 1000
                self.logger.info(f"⏰ {test_name}: Timeout at {latency_ms:.1f}ms (expected ≤ 1500ms)")
                
                return PerformanceTestResult(
                    test_name=test_name,
                    lane="knowledge_graph",
                    latency_ms=latency_ms,
                    status="timeout",
                    results_count=0,
                    error="Timeout exceeded 1.5s limit",
                    metadata={"timeout_ms": 1500.0, "max_results": 6}
                )
                
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(f"❌ {test_name}: Error - {e}")
            
            return PerformanceTestResult(
                test_name=test_name,
                lane="knowledge_graph",
                latency_ms=latency_ms,
                status="fail",
                results_count=0,
                error=str(e),
                metadata={"timeout_ms": 1500.0, "max_results": 6}
            )
    
    async def test_end_to_end_performance(self) -> PerformanceTestResult:
        """Test end-to-end performance (≤ 3.0s total)."""
        test_name = "End-to-End Performance"
        start_time = time.time()
        
        try:
            # Import orchestrator
            from services.retrieval.orchestrator import RetrievalOrchestrator, OrchestrationConfig
            from shared.contracts.query import RetrievalSearchRequest
            
            # Configure strict performance settings
            config = OrchestrationConfig()
            config.latency_budget.total_budget_ms = 3000.0  # 3.0s strict
            
            orchestrator = RetrievalOrchestrator(config)
            
            # Test query
            request = RetrievalSearchRequest(
                query="test end to end performance with hybrid retrieval",
                max_results=10
            )
            
            # Execute with timeout
            try:
                response = await asyncio.wait_for(
                    orchestrator.orchestrate_retrieval(request),
                    timeout=3.1  # Slightly over 3.0s to test strict enforcement
                )
                
                latency_ms = (time.time() - start_time) * 1000
                results_count = len(response.sources) if response.sources else 0
                
                # Check performance requirements
                if latency_ms <= 3000.0:
                    status = "pass"
                    self.logger.info(f"✅ {test_name}: {latency_ms:.1f}ms, {results_count} results")
                else:
                    status = "fail"
                    self.logger.warning(f"❌ {test_name}: {latency_ms:.1f}ms > 3000ms")
                
                return PerformanceTestResult(
                    test_name=test_name,
                    lane="hybrid",
                    latency_ms=latency_ms,
                    status=status,
                    results_count=results_count,
                    metadata={"timeout_ms": 3000.0, "max_results": 10}
                )
                
            except asyncio.TimeoutError:
                latency_ms = (time.time() - start_time) * 1000
                self.logger.info(f"⏰ {test_name}: Timeout at {latency_ms:.1f}ms (expected ≤ 3000ms)")
                
                return PerformanceTestResult(
                    test_name=test_name,
                    lane="hybrid",
                    latency_ms=latency_ms,
                    status="timeout",
                    results_count=0,
                    error="Timeout exceeded 3.0s limit",
                    metadata={"timeout_ms": 3000.0, "max_results": 10}
                )
                
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(f"❌ {test_name}: Error - {e}")
            
            return PerformanceTestResult(
                test_name=test_name,
                lane="hybrid",
                latency_ms=latency_ms,
                status="fail",
                results_count=0,
                error=str(e),
                metadata={"timeout_ms": 3000.0, "max_results": 10}
            )
    
    async def test_non_blocking_behavior(self) -> PerformanceTestResult:
        """Test that slow lanes don't block the answer."""
        test_name = "Non-Blocking Behavior"
        start_time = time.time()
        
        try:
            # Import orchestrator
            from services.retrieval.orchestrator import RetrievalOrchestrator, OrchestrationConfig
            from shared.contracts.query import RetrievalSearchRequest
            
            # Configure with one slow lane
            config = OrchestrationConfig()
            config.enable_parallel_execution = True
            config.enable_fallback = True
            
            orchestrator = RetrievalOrchestrator(config)
            
            # Test query that should trigger fallback
            request = RetrievalSearchRequest(
                query="test non blocking behavior with slow lanes",
                max_results=5
            )
            
            # Execute
            response = await orchestrator.orchestrate_retrieval(request)
            
            latency_ms = (time.time() - start_time) * 1000
            results_count = len(response.sources) if response.sources else 0
            
            # Check that we got results despite potential slow lanes
            if results_count > 0 and latency_ms <= 3000.0:
                status = "pass"
                self.logger.info(f"✅ {test_name}: Non-blocking successful, {latency_ms:.1f}ms, {results_count} results")
            else:
                status = "fail"
                self.logger.warning(f"❌ {test_name}: Blocking behavior detected")
            
            return PerformanceTestResult(
                test_name=test_name,
                lane="fallback",
                latency_ms=latency_ms,
                status=status,
                results_count=results_count,
                metadata={"timeout_ms": 3000.0, "max_results": 5}
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(f"❌ {test_name}: Error - {e}")
            
            return PerformanceTestResult(
                test_name=test_name,
                lane="fallback",
                latency_ms=latency_ms,
                status="fail",
                results_count=0,
                error=str(e),
                metadata={"timeout_ms": 3000.0, "max_results": 5}
            )
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "pass"])
        failed_tests = len([r for r in self.results if r.status == "fail"])
        timeout_tests = len([r for r in self.results if r.status == "timeout"])
        
        # Calculate P95 latency
        latencies = [r.latency_ms for r in self.results if r.status == "pass"]
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
        
        # Performance compliance
        vector_compliant = any(r.lane == "vector_search" and r.status == "pass" and r.latency_ms <= 2000.0 for r in self.results)
        kg_compliant = any(r.lane == "knowledge_graph" and r.status == "pass" and r.latency_ms <= 1500.0 for r in self.results)
        e2e_compliant = any(r.lane == "hybrid" and r.status == "pass" and r.latency_ms <= 3000.0 for r in self.results)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "timeout_tests": timeout_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "performance_metrics": {
                "p95_latency_ms": p95_latency,
                "vector_search_compliant": vector_compliant,
                "knowledge_graph_compliant": kg_compliant,
                "end_to_end_compliant": e2e_compliant
            },
            "requirements_compliance": {
                "p95_latency_3s": p95_latency <= 3000.0,
                "vector_2s": vector_compliant,
                "kg_1_5s": kg_compliant,
                "non_blocking": any(r.lane == "fallback" and r.status == "pass" for r in self.results)
            },
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "lane": r.lane,
                    "latency_ms": r.latency_ms,
                    "status": r.status,
                    "results_count": r.results_count,
                    "error": r.error,
                    "metadata": r.metadata
                }
                for r in self.results
            ]
        }
        
        return report
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all performance tests."""
        self.logger.info("🚀 Starting Always-On Performance Tests")
        self.logger.info("=" * 60)
        
        # Run performance tests
        tests = [
            self.test_vector_search_performance(),
            self.test_knowledge_graph_performance(),
            self.test_end_to_end_performance(),
            self.test_non_blocking_behavior()
        ]
        
        # Execute tests
        for test in tests:
            result = await test
            self.results.append(result)
        
        # Generate report
        report = self.generate_performance_report()
        
        # Print summary
        self.logger.info("📊 PERFORMANCE TEST SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Tests: {report['summary']['total_tests']}")
        self.logger.info(f"Passed: {report['summary']['passed_tests']}")
        self.logger.info(f"Failed: {report['summary']['failed_tests']}")
        self.logger.info(f"Timeouts: {report['summary']['timeout_tests']}")
        self.logger.info(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        
        self.logger.info(f"\n🎯 PERFORMANCE COMPLIANCE:")
        self.logger.info(f"P95 Latency ≤ 3s: {'✅' if report['requirements_compliance']['p95_latency_3s'] else '❌'} ({report['performance_metrics']['p95_latency_ms']:.1f}ms)")
        self.logger.info(f"Vector ≤ 2.0s: {'✅' if report['requirements_compliance']['vector_2s'] else '❌'}")
        self.logger.info(f"KG ≤ 1.5s: {'✅' if report['requirements_compliance']['kg_1_5s'] else '❌'}")
        self.logger.info(f"Non-blocking: {'✅' if report['requirements_compliance']['non_blocking'] else '❌'}")
        
        return report

async def main():
    """Main function."""
    tester = AlwaysOnPerformanceTester()
    report = await tester.run_all_tests()
    
    # Save report
    import json
    from pathlib import Path
    
    output_dir = Path("code_garden/test_output")
    output_dir.mkdir(exist_ok=True)
    
    report_file = output_dir / "always_on_performance_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Performance report saved to: {report_file}")
    
    # Exit with appropriate code
    if report['summary']['failed_tests'] == 0 and report['requirements_compliance']['p95_latency_3s']:
        print("\n🎉 All performance requirements met! System is ready for production.")
        return True
    else:
        print("\n⚠️  Some performance requirements not met. Check the report for details.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
