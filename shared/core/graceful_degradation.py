#!/usr/bin/env python3
"""
SarvanOM Graceful Degradation Verification System
Handles negative scenarios and verifies graceful degradation behavior
"""

import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DegradationType(Enum):
    """Types of graceful degradation"""
    LANE_SKIPPED = "lane_skipped"
    LANE_TIMEOUT = "lane_timeout"
    LANE_SLOW = "lane_slow"
    PARTIAL_RESPONSE = "partial_response"
    REDUCED_CITATIONS = "reduced_citations"
    UNCERTAINTY_FLAGS = "uncertainty_flags"

class LaneFailureMode(Enum):
    """Lane failure modes for testing"""
    AUTH_FAILURE = "auth_failure"
    SERVICE_DOWN = "service_down"
    SERVICE_SLOW = "service_slow"
    NETWORK_TIMEOUT = "network_timeout"
    CIRCUIT_OPEN = "circuit_open"

@dataclass
class DegradationAssertion:
    """Assertion for graceful degradation behavior"""
    name: str
    condition: str
    message: str
    required: bool = True

@dataclass
class LaneFailureSimulation:
    """Configuration for simulating lane failures"""
    lane_name: str
    failure_mode: LaneFailureMode
    timeout_ms: int
    delay_ms: int = 0
    error_message: str = ""
    should_skip: bool = False

@dataclass
class DegradationTestResult:
    """Result of a degradation test"""
    test_name: str
    success: bool
    assertions_passed: List[str]
    assertions_failed: List[str]
    degradation_flags: List[str]
    uncertainty_flags: List[str]
    lane_statuses: Dict[str, str]
    response_time_ms: float
    citation_count: int
    error_message: Optional[str] = None

class GracefulDegradationVerifier:
    """Verifies graceful degradation behavior in negative scenarios"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _create_session(self):
        """Create aiohttp session"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    def _evaluate_assertion(self, assertion: DegradationAssertion, 
                          test_result: Dict[str, Any]) -> bool:
        """Evaluate a single assertion"""
        try:
            # Simple assertion evaluation (in real implementation, use a proper expression evaluator)
            condition = assertion.condition.lower()
            
            if "kg_lane.status == 'skipped'" in condition:
                kg_status = test_result.get("lane_statuses", {}).get("kg", "unknown")
                return kg_status == "skipped"
            
            elif "kg_lane.timeout == false" in condition:
                kg_timeout = test_result.get("lane_timeouts", {}).get("kg", True)
                return not kg_timeout
            
            elif "overall_success == true" in condition:
                return test_result.get("overall_success", False)
            
            elif "degradation_flags.contains" in condition:
                flag = condition.split("'")[1] if "'" in condition else ""
                degradation_flags = test_result.get("degradation_flags", [])
                return flag in degradation_flags
            
            elif "uncertainty_flags.contains" in condition:
                flag = condition.split("'")[1] if "'" in condition else ""
                uncertainty_flags = test_result.get("uncertainty_flags", [])
                return flag in uncertainty_flags
            
            elif "citation_count >=" in condition:
                min_citations = int(condition.split(">=")[1].strip())
                citation_count = test_result.get("citation_count", 0)
                return citation_count >= min_citations
            
            elif "total_latency_ms <=" in condition:
                max_latency = float(condition.split("<=")[1].strip())
                total_latency = test_result.get("response_time_ms", 0)
                return total_latency <= max_latency
            
            elif "vector_lane.status == 'timeout'" in condition:
                vector_status = test_result.get("lane_statuses", {}).get("vector", "unknown")
                return vector_status == "timeout"
            
            elif "vector_lane.duration_ms <=" in condition:
                max_duration = float(condition.split("<=")[1].strip())
                vector_duration = test_result.get("lane_durations", {}).get("vector", 0)
                return vector_duration <= max_duration
            
            elif "keyword_lane.status == 'completed'" in condition:
                keyword_status = test_result.get("lane_statuses", {}).get("keyword", "unknown")
                return keyword_status == "completed"
            
            elif "keyword_lane.duration_ms >=" in condition and "keyword_lane.duration_ms <=" in condition:
                # Parse range condition
                parts = condition.split("keyword_lane.duration_ms")
                min_duration = float(parts[1].split(">=")[1].split(" AND")[0].strip())
                max_duration = float(parts[1].split("<=")[1].strip())
                keyword_duration = test_result.get("lane_durations", {}).get("keyword", 0)
                return min_duration <= keyword_duration <= max_duration
            
            elif "completed_lanes ==" in condition:
                expected_lanes = int(condition.split("==")[1].strip())
                completed_lanes = test_result.get("completed_lanes", 0)
                return completed_lanes == expected_lanes
            
            elif "failed_lanes == 0" in condition:
                failed_lanes = test_result.get("failed_lanes", 0)
                return failed_lanes == 0
            
            elif "response_content.length >" in condition:
                min_length = int(condition.split(">")[1].strip())
                response_content = test_result.get("response_content", "")
                return len(response_content) > min_length
            
            elif "response_content.contains" in condition:
                content = condition.split("'")[1] if "'" in condition else ""
                response_content = test_result.get("response_content", "")
                return content in response_content
            
            # Default to False for unrecognized conditions
            logger.warning(f"Unrecognized assertion condition: {condition}")
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating assertion '{assertion.name}': {e}")
            return False
    
    async def _simulate_lane_failure(self, failure_sim: LaneFailureSimulation) -> Dict[str, Any]:
        """Simulate a lane failure for testing"""
        if not self.session:
            await self._create_session()
        
        # Create a test payload that will trigger the specific lane
        payload = {
            "query": f"Test query for {failure_sim.lane_name} lane",
            "complexity": "simple",
            "mode": "fast",
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        # Add failure simulation parameters
        payload["failure_simulation"] = {
            "lane": failure_sim.lane_name,
            "mode": failure_sim.failure_mode.value,
            "timeout_ms": failure_sim.timeout_ms,
            "delay_ms": failure_sim.delay_ms,
            "error_message": failure_sim.error_message,
            "should_skip": failure_sim.should_skip
        }
        
        start_time = time.time()
        
        try:
            async with self.session.post(f"{self.base_url}/api/search", json=payload) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {await response.text()}",
                        "response_time_ms": (time.time() - start_time) * 1000
                    }
                
                data = await response.json()
                response_time_ms = (time.time() - start_time) * 1000
                
                return {
                    "success": True,
                    "data": data,
                    "response_time_ms": response_time_ms,
                    "response_content": data.get("answer", ""),
                    "citation_count": len(data.get("citations", [])),
                    "degradation_flags": data.get("degradation_flags", []),
                    "uncertainty_flags": data.get("uncertainty_flags", []),
                    "lane_statuses": data.get("lane_statuses", {}),
                    "lane_durations": data.get("lane_durations", {}),
                    "lane_timeouts": data.get("lane_timeouts", {})
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Request timeout",
                "response_time_ms": (time.time() - start_time) * 1000
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": (time.time() - start_time) * 1000
            }
    
    async def test_arango_auth_failure(self) -> DegradationTestResult:
        """Test graceful degradation when ArangoDB authentication fails"""
        logger.info("Testing ArangoDB authentication failure scenario")
        
        # Simulate ArangoDB auth failure
        failure_sim = LaneFailureSimulation(
            lane_name="kg",
            failure_mode=LaneFailureMode.AUTH_FAILURE,
            timeout_ms=1000,
            error_message="Authentication failed",
            should_skip=True
        )
        
        # Execute test
        result = await self._simulate_lane_failure(failure_sim)
        
        # Define assertions
        assertions = [
            DegradationAssertion(
                name="kg_lane_skipped_not_timeout",
                condition="kg_lane.status == 'skipped' AND kg_lane.timeout == false",
                message="KG lane should be skipped due to auth failure, not timeout"
            ),
            DegradationAssertion(
                name="overall_success_with_degradation",
                condition="overall_success == true AND degradation_flags.contains('kg_unavailable')",
                message="Overall test should pass with degradation flag"
            ),
            DegradationAssertion(
                name="uncertainty_flags_present",
                condition="uncertainty_flags.contains('kg_lane_skipped')",
                message="Uncertainty flags should indicate KG lane was skipped"
            ),
            DegradationAssertion(
                name="sufficient_citations_without_kg",
                condition="citation_count >= 2 AND citation_count < 6",
                message="Should have some citations but fewer than with KG lane"
            ),
            DegradationAssertion(
                name="response_time_within_budget",
                condition="total_latency_ms <= 5000",
                message="Response time should be within budget despite KG failure"
            )
        ]
        
        # Evaluate assertions
        passed_assertions = []
        failed_assertions = []
        
        for assertion in assertions:
            if self._evaluate_assertion(assertion, result):
                passed_assertions.append(assertion.name)
            else:
                failed_assertions.append(assertion.name)
                logger.warning(f"Assertion failed: {assertion.message}")
        
        # Determine overall success
        overall_success = len(failed_assertions) == 0
        
        return DegradationTestResult(
            test_name="arango_auth_failure",
            success=overall_success,
            assertions_passed=passed_assertions,
            assertions_failed=failed_assertions,
            degradation_flags=result.get("degradation_flags", []),
            uncertainty_flags=result.get("uncertainty_flags", []),
            lane_statuses=result.get("lane_statuses", {}),
            response_time_ms=result.get("response_time_ms", 0),
            citation_count=result.get("citation_count", 0),
            error_message=result.get("error")
        )
    
    async def test_qdrant_pause_kill(self) -> DegradationTestResult:
        """Test graceful degradation when Qdrant is paused/killed"""
        logger.info("Testing Qdrant pause/kill scenario")
        
        # Simulate Qdrant pause/kill
        failure_sim = LaneFailureSimulation(
            lane_name="vector",
            failure_mode=LaneFailureMode.SERVICE_DOWN,
            timeout_ms=3000,
            error_message="Service unavailable",
            should_skip=False
        )
        
        # Execute test
        result = await self._simulate_lane_failure(failure_sim)
        
        # Define assertions
        assertions = [
            DegradationAssertion(
                name="vector_lane_timeout_within_budget",
                condition="vector_lane.status == 'timeout' AND vector_lane.duration_ms <= 3000",
                message="Vector lane should timeout within allocated budget"
            ),
            DegradationAssertion(
                name="overall_success_with_timeout",
                condition="overall_success == true AND degradation_flags.contains('vector_timeout')",
                message="Overall test should pass despite vector lane timeout"
            ),
            DegradationAssertion(
                name="uncertainty_flags_for_timeout",
                condition="uncertainty_flags.contains('vector_lane_timeout')",
                message="Uncertainty flags should indicate vector lane timeout"
            ),
            DegradationAssertion(
                name="sufficient_citations_without_vector",
                condition="citation_count >= 3 AND citation_count < 8",
                message="Should have adequate citations from other lanes"
            ),
            DegradationAssertion(
                name="response_time_within_budget",
                condition="total_latency_ms <= 7000",
                message="Response time should be within technical tier budget"
            ),
            DegradationAssertion(
                name="partial_answer_provided",
                condition="response_content.length > 100 AND response_content.contains('uncertainty')",
                message="Should provide partial answer with uncertainty indication"
            )
        ]
        
        # Evaluate assertions
        passed_assertions = []
        failed_assertions = []
        
        for assertion in assertions:
            if self._evaluate_assertion(assertion, result):
                passed_assertions.append(assertion.name)
            else:
                failed_assertions.append(assertion.name)
                logger.warning(f"Assertion failed: {assertion.message}")
        
        # Determine overall success
        overall_success = len(failed_assertions) == 0
        
        return DegradationTestResult(
            test_name="qdrant_pause_kill",
            success=overall_success,
            assertions_passed=passed_assertions,
            assertions_failed=failed_assertions,
            degradation_flags=result.get("degradation_flags", []),
            uncertainty_flags=result.get("uncertainty_flags", []),
            lane_statuses=result.get("lane_statuses", {}),
            response_time_ms=result.get("response_time_ms", 0),
            citation_count=result.get("citation_count", 0),
            error_message=result.get("error")
        )
    
    async def test_meilisearch_slow(self) -> DegradationTestResult:
        """Test graceful degradation when Meilisearch is slow"""
        logger.info("Testing Meilisearch slow response scenario")
        
        # Simulate Meilisearch slow response
        failure_sim = LaneFailureSimulation(
            lane_name="keyword",
            failure_mode=LaneFailureMode.SERVICE_SLOW,
            timeout_ms=2000,
            delay_ms=1000,  # 800-1200ms delay
            error_message="Service slow",
            should_skip=False
        )
        
        # Execute test
        result = await self._simulate_lane_failure(failure_sim)
        
        # Define assertions
        assertions = [
            DegradationAssertion(
                name="keyword_lane_completes_slowly",
                condition="keyword_lane.status == 'completed' AND keyword_lane.duration_ms >= 800 AND keyword_lane.duration_ms <= 1200",
                message="Keyword lane should complete but take 800-1200ms"
            ),
            DegradationAssertion(
                name="overall_success_with_slow_keyword",
                condition="overall_success == true AND degradation_flags.contains('keyword_slow')",
                message="Overall test should pass despite slow keyword search"
            ),
            DegradationAssertion(
                name="uncertainty_flags_for_slow_response",
                condition="uncertainty_flags.contains('keyword_search_delayed')",
                message="Uncertainty flags should indicate slow keyword search"
            ),
            DegradationAssertion(
                name="sufficient_citations_for_research",
                condition="citation_count >= 6",
                message="Should have adequate citations for research complexity"
            ),
            DegradationAssertion(
                name="response_time_within_research_budget",
                condition="total_latency_ms <= 10000",
                message="Response time should be within research tier budget"
            ),
            DegradationAssertion(
                name="all_lanes_completed",
                condition="completed_lanes == 4 AND failed_lanes == 0",
                message="All lanes should complete successfully despite slow keyword search"
            )
        ]
        
        # Evaluate assertions
        passed_assertions = []
        failed_assertions = []
        
        for assertion in assertions:
            if self._evaluate_assertion(assertion, result):
                passed_assertions.append(assertion.name)
            else:
                failed_assertions.append(assertion.name)
                logger.warning(f"Assertion failed: {assertion.message}")
        
        # Determine overall success
        overall_success = len(failed_assertions) == 0
        
        return DegradationTestResult(
            test_name="meilisearch_slow",
            success=overall_success,
            assertions_passed=passed_assertions,
            assertions_failed=failed_assertions,
            degradation_flags=result.get("degradation_flags", []),
            uncertainty_flags=result.get("uncertainty_flags", []),
            lane_statuses=result.get("lane_statuses", {}),
            response_time_ms=result.get("response_time_ms", 0),
            citation_count=result.get("citation_count", 0),
            error_message=result.get("error")
        )
    
    async def run_all_degradation_tests(self) -> List[DegradationTestResult]:
        """Run all graceful degradation tests"""
        await self._create_session()
        
        try:
            results = []
            
            # Run ArangoDB auth failure test
            arango_result = await self.test_arango_auth_failure()
            results.append(arango_result)
            
            # Run Qdrant pause/kill test
            qdrant_result = await self.test_qdrant_pause_kill()
            results.append(qdrant_result)
            
            # Run Meilisearch slow test
            meilisearch_result = await self.test_meilisearch_slow()
            results.append(meilisearch_result)
            
            return results
            
        finally:
            await self._close_session()
    
    def generate_degradation_report(self, results: List[DegradationTestResult]) -> Dict[str, Any]:
        """Generate a comprehensive degradation test report"""
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - successful_tests
        
        # Aggregate metrics
        total_assertions = sum(len(r.assertions_passed) + len(r.assertions_failed) for r in results)
        passed_assertions = sum(len(r.assertions_passed) for r in results)
        failed_assertions = sum(len(r.assertions_failed) for r in results)
        
        # Performance metrics
        response_times = [r.response_time_ms for r in results]
        citation_counts = [r.citation_count for r in results]
        
        # Degradation flags
        all_degradation_flags = []
        all_uncertainty_flags = []
        for r in results:
            all_degradation_flags.extend(r.degradation_flags)
            all_uncertainty_flags.extend(r.uncertainty_flags)
        
        return {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0
            },
            "assertions": {
                "total_assertions": total_assertions,
                "passed_assertions": passed_assertions,
                "failed_assertions": failed_assertions,
                "assertion_success_rate": (passed_assertions / total_assertions) * 100 if total_assertions > 0 else 0
            },
            "performance": {
                "average_response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
                "max_response_time_ms": max(response_times) if response_times else 0,
                "min_response_time_ms": min(response_times) if response_times else 0,
                "average_citation_count": sum(citation_counts) / len(citation_counts) if citation_counts else 0
            },
            "degradation_analysis": {
                "unique_degradation_flags": list(set(all_degradation_flags)),
                "unique_uncertainty_flags": list(set(all_uncertainty_flags)),
                "degradation_flag_frequency": {flag: all_degradation_flags.count(flag) for flag in set(all_degradation_flags)},
                "uncertainty_flag_frequency": {flag: all_uncertainty_flags.count(flag) for flag in set(all_uncertainty_flags)}
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "assertions_passed": len(r.assertions_passed),
                    "assertions_failed": len(r.assertions_failed),
                    "response_time_ms": r.response_time_ms,
                    "citation_count": r.citation_count,
                    "degradation_flags": r.degradation_flags,
                    "uncertainty_flags": r.uncertainty_flags,
                    "lane_statuses": r.lane_statuses
                }
                for r in results
            ]
        }
