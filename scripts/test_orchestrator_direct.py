#!/usr/bin/env python3
"""
Direct Orchestrator Test Script
Tests the improved orchestrator functionality directly without requiring the full server.

This script validates:
- Empty retrieval handling
- Context passing improvements
- Error handling enhancements
- Response aggregation improvements

# DEAD CODE - Candidate for deletion: This test script is not integrated into any test suite
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorTester:
    def __init__(self):
        self.test_results = []
        
    def log(self, message: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    async def test_orchestrator_initialization(self):
        """Test orchestrator initialization"""
        self.log("🧪 Testing Orchestrator Initialization")
        
        try:
            from shared.core.agents.lead_orchestrator import LeadOrchestrator
            
            orchestrator = LeadOrchestrator()
            self.log("✅ Orchestrator initialized successfully")
            
            # Test basic functionality
            test_query = "What is artificial intelligence?"
            user_context = {"max_tokens": 1000, "confidence_threshold": 0.7}
            
            self.log(f"🧪 Testing query processing: {test_query}")
            result = await orchestrator.process_query(test_query, user_context)
            
            if result.get("success", False):
                self.log("✅ Query processing successful")
                self.log(f"  Answer length: {len(result.get('answer', ''))}")
                self.log(f"  Confidence: {result.get('confidence', 0.0)}")
                self.log(f"  Warnings: {result.get('warnings', [])}")
                
                # Check for improvements
                metadata = result.get("metadata", {})
                pipeline_status = metadata.get("pipeline_status", "unknown")
                successful_agents = metadata.get("successful_agents", [])
                failed_agents = metadata.get("failed_agents", [])
                
                self.log(f"  Pipeline Status: {pipeline_status}")
                self.log(f"  Successful Agents: {successful_agents}")
                self.log(f"  Failed Agents: {failed_agents}")
                
                return {
                    "test_name": "Orchestrator Initialization",
                    "success": True,
                    "pipeline_status": pipeline_status,
                    "successful_agents": successful_agents,
                    "failed_agents": failed_agents,
                    "warnings": result.get("warnings", [])
                }
            else:
                self.log(f"❌ Query processing failed: {result.get('error', 'Unknown error')}")
                return {
                    "test_name": "Orchestrator Initialization",
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            self.log(f"❌ Orchestrator initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "test_name": "Orchestrator Initialization",
                "success": False,
                "error": str(e)
            }
    
    async def test_empty_retrieval_handling(self):
        """Test handling of empty retrieval results"""
        self.log("🧪 Testing Empty Retrieval Handling")
        
        try:
            from shared.core.agents.lead_orchestrator import LeadOrchestrator
            
            orchestrator = LeadOrchestrator()
            
            # Test with a query that should return no results
            test_query = "xyz123veryobscurequerythatwontfindanything"
            user_context = {"max_tokens": 1000, "confidence_threshold": 0.7}
            
            self.log(f"🧪 Testing empty retrieval query: {test_query}")
            result = await orchestrator.process_query(test_query, user_context)
            
            if result.get("success", False):
                self.log("✅ Empty retrieval handling successful")
                
                # Check for empty retrieval warnings
                warnings = result.get("warnings", [])
                has_empty_warning = any("no relevant documents" in warning.lower() or "empty retrieval" in warning.lower() for warning in warnings)
                
                if has_empty_warning:
                    self.log("✅ Empty retrieval warning detected")
                else:
                    self.log("⚠️ No empty retrieval warning found")
                
                metadata = result.get("metadata", {})
                pipeline_status = metadata.get("pipeline_status", "unknown")
                
                self.log(f"  Pipeline Status: {pipeline_status}")
                self.log(f"  Warnings: {warnings}")
                
                return {
                    "test_name": "Empty Retrieval Handling",
                    "success": True,
                    "pipeline_status": pipeline_status,
                    "has_empty_warning": has_empty_warning,
                    "warnings": warnings
                }
            else:
                self.log(f"❌ Empty retrieval handling failed: {result.get('error', 'Unknown error')}")
                return {
                    "test_name": "Empty Retrieval Handling",
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            self.log(f"❌ Empty retrieval test failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "test_name": "Empty Retrieval Handling",
                "success": False,
                "error": str(e)
            }
    
    async def test_context_passing(self):
        """Test context passing between pipeline stages"""
        self.log("🧪 Testing Context Passing")
        
        try:
            from shared.core.agents.lead_orchestrator import LeadOrchestrator
            
            orchestrator = LeadOrchestrator()
            
            # Test with a normal query
            test_query = "What is machine learning?"
            user_context = {"max_tokens": 1000, "confidence_threshold": 0.7}
            
            self.log(f"🧪 Testing context passing with query: {test_query}")
            result = await orchestrator.process_query(test_query, user_context)
            
            if result.get("success", False):
                self.log("✅ Context passing test successful")
                
                metadata = result.get("metadata", {})
                
                # Check for context from different stages
                retrieval_context = metadata.get("retrieval_context", {})
                fact_check_context = metadata.get("fact_check_context", {})
                synthesis_context = metadata.get("synthesis_context", {})
                
                has_retrieval_context = bool(retrieval_context)
                has_fact_check_context = bool(fact_check_context)
                has_synthesis_context = bool(synthesis_context)
                
                self.log(f"  Has Retrieval Context: {has_retrieval_context}")
                self.log(f"  Has Fact-Check Context: {has_fact_check_context}")
                self.log(f"  Has Synthesis Context: {has_synthesis_context}")
                
                return {
                    "test_name": "Context Passing",
                    "success": True,
                    "has_retrieval_context": has_retrieval_context,
                    "has_fact_check_context": has_fact_check_context,
                    "has_synthesis_context": has_synthesis_context,
                    "retrieval_context": retrieval_context,
                    "fact_check_context": fact_check_context,
                    "synthesis_context": synthesis_context
                }
            else:
                self.log(f"❌ Context passing test failed: {result.get('error', 'Unknown error')}")
                return {
                    "test_name": "Context Passing",
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            self.log(f"❌ Context passing test failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "test_name": "Context Passing",
                "success": False,
                "error": str(e)
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all orchestrator tests"""
        self.log("🚀 Starting Direct Orchestrator Tests")
        
        test_results = []
        
        # Run tests
        tests = [
            self.test_orchestrator_initialization(),
            self.test_empty_retrieval_handling(),
            self.test_context_passing()
        ]
        
        for test in tests:
            result = await test
            test_results.append(result)
            await asyncio.sleep(1)  # Brief pause between tests
        
        # Compile results
        successful_tests = sum(1 for r in test_results if r.get("success", False))
        total_tests = len(test_results)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "test_results": test_results,
            "recommendations": self._generate_recommendations(test_results)
        }
        
        return summary
    
    def _generate_recommendations(self, test_results: list) -> list:
        """Generate recommendations based on test results"""
        recommendations = []
        
        success_rate = sum(1 for r in test_results if r.get("success", False)) / len(test_results) if test_results else 0
        
        if success_rate < 0.8:
            recommendations.append("Low success rate - investigate orchestrator issues")
        
        # Check for specific improvements
        empty_retrieval_tests = [r for r in test_results if "Empty Retrieval" in r.get("test_name", "")]
        if empty_retrieval_tests and not any(r.get("has_empty_warning", False) for r in empty_retrieval_tests):
            recommendations.append("Empty retrieval handling not working as expected")
        
        context_tests = [r for r in test_results if "Context Passing" in r.get("test_name", "")]
        if context_tests and not any(r.get("has_retrieval_context", False) for r in context_tests):
            recommendations.append("Context passing not working as expected")
        
        return recommendations
    
    def print_report(self, report: Dict[str, Any]):
        """Print a formatted test report"""
        print("\n" + "="*80)
        print("DIRECT ORCHESTRATOR TEST REPORT")
        print("="*80)
        
        summary = report["test_summary"]
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Successful: {summary['successful_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        
        print(f"\n🧪 Test Results:")
        for result in report["test_results"]:
            status = "✅" if result.get("success", False) else "❌"
            test_name = result.get("test_name", "Unknown")
            
            print(f"   {test_name}: {status}")
            
            if result.get("success", False):
                if "Empty Retrieval" in test_name:
                    has_warning = result.get("has_empty_warning", False)
                    print(f"     Empty retrieval warning: {'✅' if has_warning else '❌'}")
                
                if "Context Passing" in test_name:
                    has_retrieval = result.get("has_retrieval_context", False)
                    has_fact_check = result.get("has_fact_check_context", False)
                    has_synthesis = result.get("has_synthesis_context", False)
                    print(f"     Retrieval context: {'✅' if has_retrieval else '❌'}")
                    print(f"     Fact-check context: {'✅' if has_fact_check else '❌'}")
                    print(f"     Synthesis context: {'✅' if has_synthesis else '❌'}")
                
                pipeline_status = result.get("pipeline_status", "unknown")
                print(f"     Pipeline status: {pipeline_status}")
            else:
                error = result.get("error", "Unknown error")
                print(f"     Error: {error}")
        
        if report["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")
        
        print("\n" + "="*80)

async def main():
    """Main test execution"""
    tester = OrchestratorTester()
    
    try:
        report = await tester.run_all_tests()
        tester.print_report(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"orchestrator_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            import json
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 