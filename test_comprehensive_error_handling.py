#!/usr/bin/env python3
"""
Comprehensive Error Handling Test for LeadOrchestrator

This script tests the enhanced error handling and fallback strategies
implemented in the LeadOrchestrator.
"""

import asyncio
import logging
import time
import sys
import os
from typing import Dict, Any, List

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.core.agents.lead_orchestrator import LeadOrchestrator
from shared.core.agents.base_agent import QueryContext, AgentType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorHandlingTester:
    """Test class for comprehensive error handling scenarios."""
    
    def __init__(self):
        self.orchestrator = LeadOrchestrator()
        self.test_results = []
        
    async def run_comprehensive_tests(self):
        """Run all comprehensive error handling tests."""
        logger.info("🚀 Starting Comprehensive Error Handling Tests")
        
        test_scenarios = [
            ("Normal Query", self.test_normal_query),
            ("Retrieval Failure", self.test_retrieval_failure),
            ("Fact Check Failure", self.test_fact_check_failure),
            ("Synthesis Failure", self.test_synthesis_failure),
            ("Citation Failure", self.test_citation_failure),
            ("Multiple Agent Failures", self.test_multiple_failures),
            ("Timeout Scenarios", self.test_timeout_scenarios),
            ("Empty Results", self.test_empty_results),
            ("Malformed Input", self.test_malformed_input),
            ("Fallback Strategies", self.test_fallback_strategies),
        ]
        
        for test_name, test_func in test_scenarios:
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Running Test: {test_name}")
                logger.info(f"{'='*60}")
                
                start_time = time.time()
                result = await test_func()
                end_time = time.time()
                
                test_result = {
                    "test_name": test_name,
                    "success": result.get("success", False),
                    "execution_time": end_time - start_time,
                    "pipeline_health": result.get("pipeline_health", "unknown"),
                    "response_type": result.get("response_type", "unknown"),
                    "confidence": result.get("confidence", 0.0),
                    "warnings": result.get("warnings", []),
                    "fallback_messages": result.get("fallback_messages", []),
                    "error": result.get("error", None)
                }
                
                self.test_results.append(test_result)
                
                logger.info(f"✅ Test '{test_name}' completed in {test_result['execution_time']:.2f}s")
                logger.info(f"   Success: {test_result['success']}")
                logger.info(f"   Pipeline Health: {test_result['pipeline_health']}")
                logger.info(f"   Response Type: {test_result['response_type']}")
                logger.info(f"   Confidence: {test_result['confidence']:.2f}")
                
                if test_result['warnings']:
                    logger.info(f"   Warnings: {len(test_result['warnings'])}")
                if test_result['fallback_messages']:
                    logger.info(f"   Fallback Messages: {len(test_result['fallback_messages'])}")
                
            except Exception as e:
                logger.error(f"❌ Test '{test_name}' failed with exception: {e}")
                self.test_results.append({
                    "test_name": test_name,
                    "success": False,
                    "error": str(e),
                    "exception": True
                })
        
        # Generate comprehensive report
        await self.generate_test_report()
    
    async def test_normal_query(self) -> Dict[str, Any]:
        """Test normal query processing without errors."""
        query = "What is artificial intelligence?"
        user_context = {"user_id": "test_user", "session_id": "test_session"}
        
        result = await self.orchestrator.process_query(query, user_context)
        return result
    
    async def test_retrieval_failure(self) -> Dict[str, Any]:
        """Test scenario where retrieval agent fails."""
        # This test simulates retrieval failure by using a query that might not find results
        query = "xyz123nonexistentquery456abc"
        user_context = {"user_id": "test_user", "session_id": "test_session"}
        
        result = await self.orchestrator.process_query(query, user_context)
        return result
    
    async def test_fact_check_failure(self) -> Dict[str, Any]:
        """Test scenario where fact checking fails."""
        # Use a query that might trigger fact checking issues
        query = "What are the latest conspiracy theories about the moon landing?"
        user_context = {"user_id": "test_user", "session_id": "test_session"}
        
        result = await self.orchestrator.process_query(query, user_context)
        return result
    
    async def test_synthesis_failure(self) -> Dict[str, Any]:
        """Test scenario where synthesis fails."""
        # Use a very complex query that might overwhelm synthesis
        query = "Please provide a comprehensive analysis of the intersection between quantum mechanics, artificial intelligence, climate change, economic theory, and political philosophy, including historical context, current developments, and future implications for society, technology, and human civilization."
        user_context = {"user_id": "test_user", "session_id": "test_session"}
        
        result = await self.orchestrator.process_query(query, user_context)
        return result
    
    async def test_citation_failure(self) -> Dict[str, Any]:
        """Test scenario where citation fails."""
        # Use a query that might have citation issues
        query = "What are the main principles of machine learning?"
        user_context = {"user_id": "test_user", "session_id": "test_session"}
        
        result = await self.orchestrator.process_query(query, user_context)
        return result
    
    async def test_multiple_failures(self) -> Dict[str, Any]:
        """Test scenario where multiple agents fail."""
        # Use a query that might trigger multiple issues
        query = "xyz123nonexistentquery456abc with very complex requirements that might overwhelm multiple agents"
        user_context = {"user_id": "test_user", "session_id": "test_session"}
        
        result = await self.orchestrator.process_query(query, user_context)
        return result
    
    async def test_timeout_scenarios(self) -> Dict[str, Any]:
        """Test timeout scenarios."""
        # Use a query that might trigger timeouts
        query = "Please provide an extremely detailed analysis of every aspect of human civilization from prehistoric times to the present day, including all major events, technological developments, cultural changes, and their interconnections."
        user_context = {"user_id": "test_user", "session_id": "test_session"}
        
        result = await self.orchestrator.process_query(query, user_context)
        return result
    
    async def test_empty_results(self) -> Dict[str, Any]:
        """Test scenario with empty retrieval results."""
        query = "xyz123nonexistentquery456abc"
        user_context = {"user_id": "test_user", "session_id": "test_session"}
        
        result = await self.orchestrator.process_query(query, user_context)
        return result
    
    async def test_malformed_input(self) -> Dict[str, Any]:
        """Test malformed input handling."""
        # Test various malformed inputs
        malformed_queries = [
            "",  # Empty query
            "   ",  # Whitespace only
            "a" * 10000,  # Very long query
            "🚀🌟💫✨🎉🎊🎈🎁🎂🎄🎃🎗️🎟️🎫🎪🎭🎨🎬🎤🎧🎼🎹🎸🎺🎻🥁🎷🎺🎸🎹🎼🎧🎤🎬🎨🎭🎪🎫🎟️🎗️🎃🎄🎂🎁🎈🎊🎉✨💫🌟🚀",  # Emoji only
        ]
        
        results = []
        for i, query in enumerate(malformed_queries):
            logger.info(f"  Testing malformed input {i+1}/{len(malformed_queries)}")
            result = await self.orchestrator.process_query(query, {})
            results.append(result)
        
        # Return the first result for reporting
        return results[0] if results else {"success": False, "error": "No malformed input tests completed"}
    
    async def test_fallback_strategies(self) -> Dict[str, Any]:
        """Test fallback strategies."""
        # Test queries that should trigger fallback strategies
        fallback_queries = [
            "What is the meaning of life?",  # Philosophical query
            "How do I fix my computer?",  # Technical query
            "What's the weather like?",  # Real-time query
        ]
        
        results = []
        for i, query in enumerate(fallback_queries):
            logger.info(f"  Testing fallback strategy {i+1}/{len(fallback_queries)}")
            result = await self.orchestrator.process_query(query, {})
            results.append(result)
        
        # Return the first result for reporting
        return results[0] if results else {"success": False, "error": "No fallback strategy tests completed"}
    
    async def generate_test_report(self):
        """Generate a comprehensive test report."""
        logger.info(f"\n{'='*80}")
        logger.info("COMPREHENSIVE ERROR HANDLING TEST REPORT")
        logger.info(f"{'='*80}")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get("success", False))
        failed_tests = total_tests - successful_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Successful: {successful_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Analyze pipeline health distribution
        health_stats = {}
        response_types = {}
        confidence_scores = []
        
        for result in self.test_results:
            if not result.get("exception", False):
                health = result.get("pipeline_health", "unknown")
                health_stats[health] = health_stats.get(health, 0) + 1
                
                response_type = result.get("response_type", "unknown")
                response_types[response_type] = response_types.get(response_type, 0) + 1
                
                confidence = result.get("confidence", 0.0)
                confidence_scores.append(confidence)
        
        logger.info(f"\nPipeline Health Distribution:")
        for health, count in health_stats.items():
            percentage = (count / total_tests) * 100
            logger.info(f"  {health}: {count} ({percentage:.1f}%)")
        
        logger.info(f"\nResponse Type Distribution:")
        for response_type, count in response_types.items():
            percentage = (count / total_tests) * 100
            logger.info(f"  {response_type}: {count} ({percentage:.1f}%)")
        
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            min_confidence = min(confidence_scores)
            max_confidence = max(confidence_scores)
            logger.info(f"\nConfidence Statistics:")
            logger.info(f"  Average: {avg_confidence:.3f}")
            logger.info(f"  Min: {min_confidence:.3f}")
            logger.info(f"  Max: {max_confidence:.3f}")
        
        # Detailed test results
        logger.info(f"\nDetailed Test Results:")
        for result in self.test_results:
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            execution_time = result.get("execution_time", 0)
            health = result.get("pipeline_health", "unknown")
            response_type = result.get("response_type", "unknown")
            
            logger.info(f"  {status} {result['test_name']} ({execution_time:.2f}s) - {health}/{response_type}")
            
            if result.get("warnings"):
                logger.info(f"    Warnings: {len(result['warnings'])}")
            if result.get("fallback_messages"):
                logger.info(f"    Fallback Messages: {len(result['fallback_messages'])}")
            if result.get("error"):
                logger.info(f"    Error: {result['error']}")
        
        # Recommendations
        logger.info(f"\nRecommendations:")
        if failed_tests > 0:
            logger.info(f"  ⚠️  {failed_tests} tests failed - review error handling")
        if health_stats.get("complete_failure", 0) > 0:
            logger.info(f"  ⚠️  {health_stats['complete_failure']} complete failures - improve fallback strategies")
        if health_stats.get("partial_failure", 0) > 0:
            logger.info(f"  ⚠️  {health_stats['partial_failure']} partial failures - review agent coordination")
        
        if successful_tests == total_tests:
            logger.info(f"  ✅ All tests passed - error handling is robust")
        elif successful_tests >= total_tests * 0.8:
            logger.info(f"  ✅ Good error handling - {successful_tests}/{total_tests} tests passed")
        else:
            logger.info(f"  ❌ Error handling needs improvement - only {successful_tests}/{total_tests} tests passed")


async def main():
    """Main test execution function."""
    try:
        tester = ErrorHandlingTester()
        await tester.run_comprehensive_tests()
        
        logger.info("\n🎉 Comprehensive Error Handling Tests Completed!")
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 