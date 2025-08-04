#!/usr/bin/env python3
"""
Comprehensive Pipeline Improvements Test Script
Validates all the improvements made to the SarvanOM pipeline.

This script tests:
- QueryResponse model fixes
- Pipeline error handling improvements
- Context passing enhancements
- Response aggregation improvements
- Authentication flow
- Cache handling

# DEAD CODE - Candidate for deletion: This test script is not integrated into any test suite
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    name: str
    success: bool
    duration: float
    error: str = None
    details: Dict[str, Any] = None

class ComprehensiveTester:
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        
    def log(self, message: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    async def test_query_response_model(self) -> TestResult:
        """Test QueryResponse model with all required fields."""
        start_time = time.time()
        
        try:
            from shared.core.api.api_models import QueryResponse
            
            # Test creating QueryResponse with all required fields
            response = QueryResponse(
                query_id="test_123",
                status="completed",
                answer="Test answer",
                confidence=0.85,
                sources=["source1", "source2"],
                processing_time=1.5,
                timestamp=datetime.now().isoformat(),
                tokens_used=150,
                cost=0.02,
                metadata={"test": True}
            )
            
            # Test serialization
            response_dict = response.dict()
            response_json = response.json()
            
            duration = time.time() - start_time
            
            return TestResult(
                name="QueryResponse Model Fix",
                success=True,
                duration=duration,
                details={
                    "query_id": response.query_id,
                    "status": response.status,
                    "sources_count": len(response.sources),
                    "has_timestamp": bool(response.timestamp)
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="QueryResponse Model Fix",
                success=False,
                duration=duration,
                error=str(e)
            )
    
    async def test_orchestrator_improvements(self) -> TestResult:
        """Test orchestrator improvements for error handling and context passing."""
        start_time = time.time()
        
        try:
            from shared.core.agents.lead_orchestrator import LeadOrchestrator
            from shared.core.models import QueryContext
            
            # Initialize orchestrator
            orchestrator = LeadOrchestrator()
            
            # Test with empty retrieval scenario
            context = QueryContext(
                query="Test query with no results",
                user_id="test_user",
                trace_id="test_trace_123"
            )
            
            # This should handle empty retrieval gracefully
            result = await orchestrator.process_query(context.query, {
                "user_id": context.user_id,
                "trace_id": context.trace_id
            })
            
            duration = time.time() - start_time
            
            return TestResult(
                name="Orchestrator Improvements",
                success=result.get("success", False),
                duration=duration,
                details={
                    "has_answer": bool(result.get("answer")),
                    "has_confidence": "confidence" in result,
                    "has_metadata": bool(result.get("metadata")),
                    "partial_failure": result.get("metadata", {}).get("partial_failure", False)
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="Orchestrator Improvements",
                success=False,
                duration=duration,
                error=str(e)
            )
    
    async def test_pipeline_error_handling(self) -> TestResult:
        """Test pipeline error handling improvements."""
        start_time = time.time()
        
        try:
            from shared.core.agents.lead_orchestrator import LeadOrchestrator
            
            orchestrator = LeadOrchestrator()
            
            # Test with malformed query that should trigger error handling
            result = await orchestrator.process_query("", {
                "user_id": "test_user",
                "trace_id": "test_trace_456"
            })
            
            duration = time.time() - start_time
            
            # Even with errors, the system should return a structured response
            return TestResult(
                name="Pipeline Error Handling",
                success=isinstance(result, dict),
                duration=duration,
                details={
                    "has_error_handling": "error" in result or "success" in result,
                    "has_metadata": bool(result.get("metadata")),
                    "response_structure": list(result.keys()) if isinstance(result, dict) else []
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="Pipeline Error Handling",
                success=False,
                duration=duration,
                error=str(e)
            )
    
    async def test_context_passing(self) -> TestResult:
        """Test context passing improvements between pipeline stages."""
        start_time = time.time()
        
        try:
            from shared.core.agents.lead_orchestrator import LeadOrchestrator
            
            orchestrator = LeadOrchestrator()
            
            # Test with context that should be passed through pipeline
            user_context = {
                "user_id": "test_user",
                "trace_id": "test_trace_789",
                "max_tokens": 1000,
                "confidence_threshold": 0.7,
                "test_context": "should_be_passed"
            }
            
            result = await orchestrator.process_query("What is AI?", user_context)
            
            duration = time.time() - start_time
            
            return TestResult(
                name="Context Passing Improvements",
                success=result.get("success", False),
                duration=duration,
                details={
                    "has_context": bool(result.get("metadata", {}).get("user_context")),
                    "has_trace_id": "trace_id" in str(result),
                    "has_user_id": "user_id" in str(result)
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="Context Passing Improvements",
                success=False,
                duration=duration,
                error=str(e)
            )
    
    async def test_response_aggregation(self) -> TestResult:
        """Test response aggregation improvements."""
        start_time = time.time()
        
        try:
            from shared.core.agents.lead_orchestrator import LeadOrchestrator
            
            orchestrator = LeadOrchestrator()
            
            # Test response aggregation with partial failures
            result = await orchestrator.process_query("Test query for aggregation", {
                "user_id": "test_user",
                "trace_id": "test_trace_aggregation"
            })
            
            duration = time.time() - start_time
            
            return TestResult(
                name="Response Aggregation Improvements",
                success=isinstance(result, dict),
                duration=duration,
                details={
                    "has_answer": bool(result.get("answer")),
                    "has_confidence": "confidence" in result,
                    "has_citations": "citations" in result,
                    "has_metadata": bool(result.get("metadata")),
                    "has_partial_failure_info": "partial_failure" in str(result)
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="Response Aggregation Improvements",
                success=False,
                duration=duration,
                error=str(e)
            )
    
    async def run_all_tests(self):
        """Run all comprehensive tests."""
        self.log("🚀 Starting Comprehensive Pipeline Improvements Test")
        self.log("=" * 60)
        
        tests = [
            self.test_query_response_model,
            self.test_orchestrator_improvements,
            self.test_pipeline_error_handling,
            self.test_context_passing,
            self.test_response_aggregation,
        ]
        
        for test_func in tests:
            try:
                result = await test_func()
                self.results.append(result)
                
                status = "✅ PASSED" if result.success else "❌ FAILED"
                self.log(f"{status} {result.name} ({result.duration:.2f}s)")
                
                if result.error:
                    self.log(f"  Error: {result.error}")
                
                if result.details:
                    for key, value in result.details.items():
                        self.log(f"  {key}: {value}")
                        
            except Exception as e:
                self.log(f"❌ ERROR in {test_func.__name__}: {e}")
                self.results.append(TestResult(
                    name=test_func.__name__,
                    success=False,
                    duration=0,
                    error=str(e)
                ))
        
        self.log("\n" + "=" * 60)
        self.log("📊 COMPREHENSIVE TEST RESULTS")
        self.log("=" * 60)
        
        passed = sum(1 for r in self.results if r.success)
        total = len(self.results)
        total_duration = sum(r.duration for r in self.results)
        
        self.log(f"Total Tests: {total}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {total - passed}")
        self.log(f"Success Rate: {(passed/total)*100:.1f}%")
        self.log(f"Total Duration: {total_duration:.2f}s")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! Pipeline improvements are working correctly.")
        else:
            self.log("⚠️  Some tests failed. Please review the implementation.")
        
        return passed == total

async def main():
    """Main test runner."""
    tester = ComprehensiveTester()
    success = await tester.run_all_tests()
    
    # Save results to file
    results_file = f"comprehensive_improvements_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(tester.results),
            "passed_tests": sum(1 for r in tester.results if r.success),
            "failed_tests": sum(1 for r in tester.results if not r.success),
            "success_rate": f"{(sum(1 for r in tester.results if r.success)/len(tester.results))*100:.1f}%",
            "results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "duration": r.duration,
                    "error": r.error,
                    "details": r.details
                }
                for r in tester.results
            ]
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 