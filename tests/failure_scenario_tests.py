#!/usr/bin/env python3
"""
Failure Scenario Tests for SarvanOM - Graceful Degradation Testing

This module tests how the system behaves under various failure scenarios:
1. No paid API keys available
2. Vector store down
3. Knowledge graph down
4. Web search down
5. Mixed failures

Ensures graceful degradation and maintains quality standards.
"""

import asyncio
import time
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append('.')

@dataclass
class FailureScenarioResult:
    """Result of a failure scenario test."""
    scenario: str
    success: bool
    latency_ms: float
    result_count: int
    method_used: str
    error_message: Optional[str]
    graceful_degradation: bool
    quality_maintained: bool

class FailureScenarioTester:
    """Tests graceful degradation under various failure scenarios."""
    
    def __init__(self):
        self.scenarios = [
            "no_paid_keys",
            "vector_down",
            "kg_down", 
            "web_down",
            "mixed_failures"
        ]
        self.results: List[FailureScenarioResult] = []
        
        # Test prompts for failure scenarios
        self.test_prompts = [
            "What is artificial intelligence?",
            "Explain machine learning basics",
            "How do neural networks work?"
        ]
    
    async def run_all_failure_scenarios(self) -> List[FailureScenarioResult]:
        """Run all failure scenario tests."""
        print("🧪 Running Failure Scenario Tests")
        print("=" * 50)
        
        for scenario in self.scenarios:
            print(f"\n🔧 Testing scenario: {scenario}")
            result = await self._test_scenario(scenario)
            self.results.append(result)
            
            if result.success:
                print(f"   ✅ PASSED - Latency: {result.latency_ms:.1f}ms, "
                      f"Results: {result.result_count}, Method: {result.method_used}")
            else:
                print(f"   ❌ FAILED - {result.error_message}")
        
        return self.results
    
    async def _test_scenario(self, scenario: str) -> FailureScenarioResult:
        """Test a specific failure scenario."""
        start_time = time.time()
        
        try:
            if scenario == "no_paid_keys":
                return await self._test_no_paid_keys()
            elif scenario == "vector_down":
                return await self._test_vector_down()
            elif scenario == "kg_down":
                return await self._test_kg_down()
            elif scenario == "web_down":
                return await self._test_web_down()
            elif scenario == "mixed_failures":
                return await self._test_mixed_failures()
            else:
                raise ValueError(f"Unknown scenario: {scenario}")
                
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            return FailureScenarioResult(
                scenario=scenario,
                success=False,
                latency_ms=total_time,
                result_count=0,
                method_used="error",
                error_message=str(e),
                graceful_degradation=False,
                quality_maintained=False
            )
    
    async def _test_no_paid_keys(self) -> FailureScenarioResult:
        """Test behavior when no paid API keys are available."""
        start_time = time.time()
        
        try:
            # Mock environment to remove paid API keys
            with patch.dict(os.environ, {
                'OPENAI_API_KEY': '',
                'ANTHROPIC_API_KEY': '',
                'BRAVE_SEARCH_API_KEY': '',
                'SERPAPI_KEY': ''
            }):
                # Import and test
                from services.retrieval.orchestrator import get_orchestrator
                from shared.contracts.query import RetrievalSearchRequest
                
                orchestrator = get_orchestrator()
                
                # Test with a simple query
                request = RetrievalSearchRequest(
                    query="What is artificial intelligence?",
                    max_results=5
                )
                
                response = await orchestrator.orchestrate_retrieval(request)
                
                total_time = (time.time() - start_time) * 1000
                
                # Check if we got results despite no paid keys
                success = (
                    response.total_results > 0 and
                    total_time <= 5000 and  # Allow more time for fallback
                    response.method != "error"
                )
                
                return FailureScenarioResult(
                    scenario="no_paid_keys",
                    success=success,
                    latency_ms=total_time,
                    result_count=response.total_results,
                    method_used=response.method,
                    error_message=None,
                    graceful_degradation=success,
                    quality_maintained=response.total_results >= 1
                )
                
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            return FailureScenarioResult(
                scenario="no_paid_keys",
                success=False,
                latency_ms=total_time,
                result_count=0,
                method_used="error",
                error_message=str(e),
                graceful_degradation=False,
                quality_maintained=False
            )
    
    async def _test_vector_down(self) -> FailureScenarioResult:
        """Test behavior when vector store is down."""
        start_time = time.time()
        
        try:
            # Mock vector store failure by patching the orchestrator's vector search method
            from services.retrieval.orchestrator import get_orchestrator
            from shared.contracts.query import RetrievalSearchRequest
            
            orchestrator = get_orchestrator()
            
            # Mock the vector search to fail
            with patch.object(orchestrator, '_vector_search_lane') as mock_vector:
                mock_vector.side_effect = Exception("Vector Store Unavailable")
                
                request = RetrievalSearchRequest(
                    query="Explain machine learning basics",
                    max_results=5
                )
                
                response = await orchestrator.orchestrate_retrieval(request)
                
                total_time = (time.time() - start_time) * 1000
                
                # Check if we got results despite vector store being down
                success = (
                    response.total_results > 0 and
                    total_time <= 5000 and
                    response.method != "error"
                )
                
                return FailureScenarioResult(
                    scenario="vector_down",
                    success=success,
                    latency_ms=total_time,
                    result_count=response.total_results,
                    method_used=response.method,
                    error_message=None,
                    graceful_degradation=success,
                    quality_maintained=response.total_results >= 1
                )
                
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            return FailureScenarioResult(
                scenario="vector_down",
                success=False,
                latency_ms=total_time,
                result_count=0,
                method_used="error",
                error_message=str(e),
                graceful_degradation=False,
                quality_maintained=False
            )
    
    async def _test_kg_down(self) -> FailureScenarioResult:
        """Test behavior when knowledge graph is down."""
        start_time = time.time()
        
        try:
            # Mock knowledge graph failure by patching the orchestrator's KG method
            from services.retrieval.orchestrator import get_orchestrator
            from shared.contracts.query import RetrievalSearchRequest
            
            orchestrator = get_orchestrator()
            
            # Mock the KG search to fail
            with patch.object(orchestrator, '_knowledge_graph_lane') as mock_kg:
                mock_kg.side_effect = Exception("KG Service Unavailable")
                
                request = RetrievalSearchRequest(
                    query="How do neural networks work?",
                    max_results=5
                )
                
                response = await orchestrator.orchestrate_retrieval(request)
                
                total_time = (time.time() - start_time) * 1000
                
                # Check if we got results despite KG being down
                success = (
                    response.total_results > 0 and
                    total_time <= 5000 and
                    response.method != "error"
                )
                
                return FailureScenarioResult(
                    scenario="kg_down",
                    success=success,
                    latency_ms=total_time,
                    result_count=response.total_results,
                    method_used=response.method,
                    error_message=None,
                    graceful_degradation=success,
                    quality_maintained=response.total_results >= 1
                )
                
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            return FailureScenarioResult(
                scenario="kg_down",
                success=False,
                latency_ms=total_time,
                result_count=0,
                method_used="error",
                error_message=str(e),
                graceful_degradation=False,
                quality_maintained=False
            )
    
    async def _test_web_down(self) -> FailureScenarioResult:
        """Test behavior when web search is down."""
        start_time = time.time()
        
        try:
            # Mock web search failure by patching the orchestrator's web search method
            from services.retrieval.orchestrator import get_orchestrator
            from shared.contracts.query import RetrievalSearchRequest
            
            orchestrator = get_orchestrator()
            
            # Mock the web search to fail
            with patch.object(orchestrator, '_web_search_lane') as mock_web:
                mock_web.side_effect = Exception("Web Search Unavailable")
                
                request = RetrievalSearchRequest(
                    query="What is artificial intelligence?",
                    max_results=5
                )
                
                response = await orchestrator.orchestrate_retrieval(request)
                
                total_time = (time.time() - start_time) * 1000
                
                # Check if we got results despite web search being down
                success = (
                    response.total_results > 0 and
                    total_time <= 5000 and
                    response.method != "error"
                )
                
                return FailureScenarioResult(
                    scenario="web_down",
                    success=success,
                    latency_ms=total_time,
                    result_count=response.total_results,
                    method_used=response.method,
                    error_message=None,
                    graceful_degradation=success,
                    quality_maintained=response.total_results >= 1
                )
                
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            return FailureScenarioResult(
                scenario="web_down",
                success=False,
                latency_ms=total_time,
                result_count=0,
                method_used="error",
                error_message=str(e),
                graceful_degradation=False,
                quality_maintained=False
            )
    
    async def _test_mixed_failures(self) -> FailureScenarioResult:
        """Test behavior when multiple services are down."""
        start_time = time.time()
        
        try:
            # Mock multiple service failures by patching the orchestrator's methods
            from services.retrieval.orchestrator import get_orchestrator
            from shared.contracts.query import RetrievalSearchRequest
            
            orchestrator = get_orchestrator()
            
            # Mock multiple methods to fail
            with patch.object(orchestrator, '_vector_search_lane') as mock_vector, \
                 patch.object(orchestrator, '_knowledge_graph_lane') as mock_kg, \
                 patch.object(orchestrator, '_web_search_lane') as mock_web:
                
                mock_vector.side_effect = Exception("Vector Store Unavailable")
                mock_kg.side_effect = Exception("KG Service Unavailable")
                mock_web.side_effect = Exception("Web Search Unavailable")
                
                request = RetrievalSearchRequest(
                    query="Explain machine learning basics",
                    max_results=5
                )
                
                response = await orchestrator.orchestrate_retrieval(request)
                
                total_time = (time.time() - start_time) * 1000
                
                # Check if we got results despite multiple services being down
                success = (
                    response.total_results > 0 and
                    total_time <= 5000 and
                    response.method != "error"
                )
                
                return FailureScenarioResult(
                    scenario="mixed_failures",
                    success=success,
                    latency_ms=total_time,
                    result_count=response.total_results,
                    method_used=response.method,
                    error_message=None,
                    graceful_degradation=success,
                    quality_maintained=response.total_results >= 1
                )
                
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            return FailureScenarioResult(
                scenario="mixed_failures",
                success=False,
                latency_ms=total_time,
                result_count=0,
                method_used="error",
                error_message=str(e),
                graceful_degradation=False,
                quality_maintained=False
            )
    
    def analyze_failure_scenarios(self) -> Dict[str, Any]:
        """Analyze failure scenario test results."""
        if not self.results:
            return {
                "total_scenarios": 0,
                "passed_scenarios": 0,
                "failed_scenarios": 0,
                "graceful_degradation_rate": 0.0,
                "quality_maintenance_rate": 0.0,
                "overall_success": False
            }
        
        total_scenarios = len(self.results)
        passed_scenarios = sum(1 for r in self.results if r.success)
        failed_scenarios = total_scenarios - passed_scenarios
        
        graceful_degradation_count = sum(1 for r in self.results if r.graceful_degradation)
        quality_maintained_count = sum(1 for r in self.results if r.quality_maintained)
        
        graceful_degradation_rate = graceful_degradation_count / total_scenarios
        quality_maintenance_rate = quality_maintained_count / total_scenarios
        
        overall_success = (
            graceful_degradation_rate >= 0.8 and  # At least 80% graceful degradation
            quality_maintenance_rate >= 0.7       # At least 70% quality maintained
        )
        
        return {
            "total_scenarios": total_scenarios,
            "passed_scenarios": passed_scenarios,
            "failed_scenarios": failed_scenarios,
            "graceful_degradation_rate": graceful_degradation_rate,
            "quality_maintenance_rate": quality_maintenance_rate,
            "overall_success": overall_success,
            "scenario_details": [
                {
                    "scenario": r.scenario,
                    "success": r.success,
                    "graceful_degradation": r.graceful_degradation,
                    "quality_maintained": r.quality_maintained,
                    "latency_ms": r.latency_ms,
                    "result_count": r.result_count
                }
                for r in self.results
            ]
        }
    
    def print_analysis(self) -> None:
        """Print failure scenario analysis."""
        analysis = self.analyze_failure_scenarios()
        
        print(f"\n📊 FAILURE SCENARIO ANALYSIS")
        print("=" * 50)
        print(f"Total Scenarios: {analysis['total_scenarios']}")
        print(f"Passed: {analysis['passed_scenarios']}")
        print(f"Failed: {analysis['failed_scenarios']}")
        print(f"Graceful Degradation Rate: {analysis['graceful_degradation_rate']:.1%}")
        print(f"Quality Maintenance Rate: {analysis['quality_maintenance_rate']:.1%}")
        print(f"Overall Success: {'✅ YES' if analysis['overall_success'] else '❌ NO'}")
        
        print(f"\n📋 Scenario Details:")
        for detail in analysis['scenario_details']:
            status = "✅ PASS" if detail['success'] else "❌ FAIL"
            graceful = "✅ YES" if detail['graceful_degradation'] else "❌ NO"
            quality = "✅ YES" if detail['quality_maintained'] else "❌ NO"
            
            print(f"   {detail['scenario']}: {status}")
            print(f"     Graceful Degradation: {graceful}")
            print(f"     Quality Maintained: {quality}")
            print(f"     Latency: {detail['latency_ms']:.1f}ms")
            print(f"     Results: {detail['result_count']}")

async def main():
    """Main function for failure scenario testing."""
    print("🧪 Failure Scenario Testing - Graceful Degradation")
    print("=" * 60)
    
    # Initialize tester
    tester = FailureScenarioTester()
    
    # Run all failure scenarios
    results = await tester.run_all_failure_scenarios()
    
    # Analyze results
    tester.print_analysis()
    
    # Determine overall success
    analysis = tester.analyze_failure_scenarios()
    
    if analysis['overall_success']:
        print(f"\n🎉 All failure scenarios handled gracefully!")
        print("   System demonstrates robust fault tolerance.")
        sys.exit(0)
    else:
        print(f"\n❌ Some failure scenarios not handled gracefully!")
        print("   System needs improvement in fault tolerance.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
