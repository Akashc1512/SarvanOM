#!/usr/bin/env python3
"""
Comprehensive Test Runner for SarvanOM
Tests all combinations of LLM/DB/KG components with different complexity levels
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import httpx
import requests
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComplexityLevel(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    EXPERT = "expert"

class ComponentType(Enum):
    LLM = "llm"
    DATABASE = "database"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    VECTOR_DB = "vector_db"
    SEARCH = "search"

@dataclass
class TestResult:
    test_name: str
    component_combination: str
    complexity_level: str
    success: bool
    response_time_ms: float
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class ComprehensiveTestRunner:
    """Comprehensive test runner for all SarvanOM component combinations"""
    
    def __init__(self):
        self.base_url = "http://backend-test:8000"
        self.results: List[TestResult] = []
        self.test_data = self._load_test_data()
        
    def _load_test_data(self) -> Dict[str, Any]:
        """Load test data for different complexity levels"""
        return {
            "simple": {
                "queries": [
                    "What is artificial intelligence?",
                    "Explain machine learning",
                    "What is Python programming?"
                ],
                "contexts": ["technology", "programming", "science"]
            },
            "medium": {
                "queries": [
                    "Compare supervised vs unsupervised learning with examples",
                    "Explain the transformer architecture in deep learning",
                    "How does gradient descent work in neural networks?"
                ],
                "contexts": ["machine_learning", "deep_learning", "algorithms"]
            },
            "complex": {
                "queries": [
                    "Design a multi-agent system for distributed problem solving using reinforcement learning",
                    "Implement a knowledge graph-based recommendation system with real-time updates",
                    "Create a hybrid retrieval system combining semantic search, vector similarity, and graph traversal"
                ],
                "contexts": ["advanced_ai", "distributed_systems", "knowledge_engineering"]
            },
            "expert": {
                "queries": [
                    "Develop a quantum-enhanced machine learning algorithm for drug discovery with explainable AI",
                    "Build a self-evolving knowledge graph that automatically updates based on new research papers",
                    "Create a multi-modal AI system that combines vision, language, and reasoning for scientific discovery"
                ],
                "contexts": ["quantum_computing", "scientific_ai", "autonomous_systems"]
            }
        }

    async def test_health_endpoints(self) -> List[TestResult]:
        """Test all health endpoints"""
        logger.info("Testing health endpoints...")
        results = []
        
        endpoints = [
            "/health",
            "/health/live",
            "/health/ready",
            "/metrics"
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints:
                start_time = time.time()
                try:
                    response = await client.get(f"{self.base_url}{endpoint}", timeout=30.0)
                    response_time = (time.time() - start_time) * 1000
                    
                    result = TestResult(
                        test_name=f"health_{endpoint.replace('/', '_')}",
                        component_combination="backend",
                        complexity_level="simple",
                        success=response.status_code == 200,
                        response_time_ms=response_time,
                        response_data={"status_code": response.status_code, "response": response.text[:500]}
                    )
                    results.append(result)
                    logger.info(f"✅ {endpoint}: {response.status_code} ({response_time:.2f}ms)")
                    
                except Exception as e:
                    response_time = (time.time() - start_time) * 1000
                    result = TestResult(
                        test_name=f"health_{endpoint.replace('/', '_')}",
                        component_combination="backend",
                        complexity_level="simple",
                        success=False,
                        response_time_ms=response_time,
                        error_message=str(e)
                    )
                    results.append(result)
                    logger.error(f"❌ {endpoint}: {e}")
        
        return results

    async def test_llm_providers(self) -> List[TestResult]:
        """Test all LLM providers with different complexity levels"""
        logger.info("Testing LLM providers...")
        results = []
        
        providers = ["openai", "anthropic", "huggingface", "ollama"]
        
        for provider in providers:
            for complexity in ComplexityLevel:
                for query in self.test_data[complexity.value]["queries"][:2]:  # Limit to 2 queries per complexity
                    start_time = time.time()
                    try:
                        payload = {
                            "query": query,
                            "provider": provider,
                            "context": self.test_data[complexity.value]["contexts"][0],
                            "max_results": 3
                        }
                        
                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                f"{self.base_url}/llm/generate",
                                json=payload,
                                timeout=60.0
                            )
                        
                        response_time = (time.time() - start_time) * 1000
                        
                        result = TestResult(
                            test_name=f"llm_{provider}_{complexity.value}",
                            component_combination=f"llm_{provider}",
                            complexity_level=complexity.value,
                            success=response.status_code == 200,
                            response_time_ms=response_time,
                            response_data={"status_code": response.status_code, "provider": provider}
                        )
                        results.append(result)
                        
                        if response.status_code == 200:
                            logger.info(f"✅ {provider} {complexity.value}: {response_time:.2f}ms")
                        else:
                            logger.warning(f"⚠️ {provider} {complexity.value}: {response.status_code}")
                            
                    except Exception as e:
                        response_time = (time.time() - start_time) * 1000
                        result = TestResult(
                            test_name=f"llm_{provider}_{complexity.value}",
                            component_combination=f"llm_{provider}",
                            complexity_level=complexity.value,
                            success=False,
                            response_time_ms=response_time,
                            error_message=str(e)
                        )
                        results.append(result)
                        logger.error(f"❌ {provider} {complexity.value}: {e}")
        
        return results

    async def test_database_operations(self) -> List[TestResult]:
        """Test database operations with different complexity levels"""
        logger.info("Testing database operations...")
        results = []
        
        databases = ["postgres", "redis", "arangodb", "qdrant", "meilisearch"]
        
        for db in databases:
            for complexity in ComplexityLevel:
                start_time = time.time()
                try:
                    # Test different database operations based on complexity
                    if complexity == ComplexityLevel.SIMPLE:
                        endpoint = f"/db/{db}/health"
                    elif complexity == ComplexityLevel.MEDIUM:
                        endpoint = f"/db/{db}/query"
                        payload = {"query": "SELECT 1", "limit": 10}
                    elif complexity == ComplexityLevel.COMPLEX:
                        endpoint = f"/db/{db}/complex_query"
                        payload = {"query": "complex_operation", "params": {"complexity": "high"}}
                    else:  # EXPERT
                        endpoint = f"/db/{db}/expert_operation"
                        payload = {"operation": "expert_level", "params": {"expert": True}}
                    
                    async with httpx.AsyncClient() as client:
                        if complexity == ComplexityLevel.SIMPLE:
                            response = await client.get(f"{self.base_url}{endpoint}", timeout=30.0)
                        else:
                            response = await client.post(
                                f"{self.base_url}{endpoint}",
                                json=payload,
                                timeout=60.0
                            )
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    result = TestResult(
                        test_name=f"db_{db}_{complexity.value}",
                        component_combination=f"database_{db}",
                        complexity_level=complexity.value,
                        success=response.status_code in [200, 201],
                        response_time_ms=response_time,
                        response_data={"status_code": response.status_code, "database": db}
                    )
                    results.append(result)
                    
                    if response.status_code in [200, 201]:
                        logger.info(f"✅ {db} {complexity.value}: {response_time:.2f}ms")
                    else:
                        logger.warning(f"⚠️ {db} {complexity.value}: {response.status_code}")
                        
                except Exception as e:
                    response_time = (time.time() - start_time) * 1000
                    result = TestResult(
                        test_name=f"db_{db}_{complexity.value}",
                        component_combination=f"database_{db}",
                        complexity_level=complexity.value,
                        success=False,
                        response_time_ms=response_time,
                        error_message=str(e)
                    )
                    results.append(result)
                    logger.error(f"❌ {db} {complexity.value}: {e}")
        
        return results

    async def test_knowledge_graph_operations(self) -> List[TestResult]:
        """Test knowledge graph operations with different complexity levels"""
        logger.info("Testing knowledge graph operations...")
        results = []
        
        kg_operations = [
            ("create_node", "Create a new node"),
            ("create_relationship", "Create a relationship"),
            ("query_graph", "Query the graph"),
            ("traverse_graph", "Traverse the graph"),
            ("analyze_graph", "Analyze graph structure")
        ]
        
        for operation, description in kg_operations:
            for complexity in ComplexityLevel:
                start_time = time.time()
                try:
                    payload = {
                        "operation": operation,
                        "complexity": complexity.value,
                        "data": self.test_data[complexity.value]
                    }
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{self.base_url}/kg/{operation}",
                            json=payload,
                            timeout=60.0
                        )
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    result = TestResult(
                        test_name=f"kg_{operation}_{complexity.value}",
                        component_combination="knowledge_graph",
                        complexity_level=complexity.value,
                        success=response.status_code in [200, 201],
                        response_time_ms=response_time,
                        response_data={"status_code": response.status_code, "operation": operation}
                    )
                    results.append(result)
                    
                    if response.status_code in [200, 201]:
                        logger.info(f"✅ KG {operation} {complexity.value}: {response_time:.2f}ms")
                    else:
                        logger.warning(f"⚠️ KG {operation} {complexity.value}: {response.status_code}")
                        
                except Exception as e:
                    response_time = (time.time() - start_time) * 1000
                    result = TestResult(
                        test_name=f"kg_{operation}_{complexity.value}",
                        component_combination="knowledge_graph",
                        complexity_level=complexity.value,
                        success=False,
                        response_time_ms=response_time,
                        error_message=str(e)
                    )
                    results.append(result)
                    logger.error(f"❌ KG {operation} {complexity.value}: {e}")
        
        return results

    async def test_integrated_workflows(self) -> List[TestResult]:
        """Test integrated workflows combining multiple components"""
        logger.info("Testing integrated workflows...")
        results = []
        
        workflows = [
            {
                "name": "search_and_synthesize",
                "description": "Search + LLM + Knowledge Graph",
                "endpoint": "/workflow/search_synthesize"
            },
            {
                "name": "fact_check_workflow",
                "description": "Retrieval + Fact Check + LLM",
                "endpoint": "/workflow/fact_check"
            },
            {
                "name": "knowledge_extraction",
                "description": "LLM + KG + Vector DB",
                "endpoint": "/workflow/knowledge_extraction"
            },
            {
                "name": "multi_modal_analysis",
                "description": "All components integrated",
                "endpoint": "/workflow/multi_modal"
            }
        ]
        
        for workflow in workflows:
            for complexity in ComplexityLevel:
                start_time = time.time()
                try:
                    payload = {
                        "workflow": workflow["name"],
                        "complexity": complexity.value,
                        "input": self.test_data[complexity.value]["queries"][0],
                        "context": self.test_data[complexity.value]["contexts"][0]
                    }
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{self.base_url}{workflow['endpoint']}",
                            json=payload,
                            timeout=120.0  # Longer timeout for complex workflows
                        )
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    result = TestResult(
                        test_name=f"workflow_{workflow['name']}_{complexity.value}",
                        component_combination="integrated_workflow",
                        complexity_level=complexity.value,
                        success=response.status_code in [200, 201],
                        response_time_ms=response_time,
                        response_data={"status_code": response.status_code, "workflow": workflow["name"]}
                    )
                    results.append(result)
                    
                    if response.status_code in [200, 201]:
                        logger.info(f"✅ Workflow {workflow['name']} {complexity.value}: {response_time:.2f}ms")
                    else:
                        logger.warning(f"⚠️ Workflow {workflow['name']} {complexity.value}: {response.status_code}")
                        
                except Exception as e:
                    response_time = (time.time() - start_time) * 1000
                    result = TestResult(
                        test_name=f"workflow_{workflow['name']}_{complexity.value}",
                        component_combination="integrated_workflow",
                        complexity_level=complexity.value,
                        success=False,
                        response_time_ms=response_time,
                        error_message=str(e)
                    )
                    results.append(result)
                    logger.error(f"❌ Workflow {workflow['name']} {complexity.value}: {e}")
        
        return results

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        logger.info("🚀 Starting comprehensive SarvanOM testing...")
        start_time = time.time()
        
        # Run all test suites
        test_suites = [
            ("Health Endpoints", self.test_health_endpoints()),
            ("LLM Providers", self.test_llm_providers()),
            ("Database Operations", self.test_database_operations()),
            ("Knowledge Graph Operations", self.test_knowledge_graph_operations()),
            ("Integrated Workflows", self.test_integrated_workflows())
        ]
        
        all_results = []
        for suite_name, test_coroutine in test_suites:
            logger.info(f"Running {suite_name} tests...")
            try:
                suite_results = await test_coroutine
                all_results.extend(suite_results)
                logger.info(f"✅ {suite_name} completed: {len(suite_results)} tests")
            except Exception as e:
                logger.error(f"❌ {suite_name} failed: {e}")
        
        total_time = time.time() - start_time
        
        # Generate summary
        summary = self._generate_summary(all_results, total_time)
        
        # Save results
        await self._save_results(all_results, summary)
        
        return summary

    def _generate_summary(self, results: List[TestResult], total_time: float) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - successful_tests
        
        # Group by component combination
        by_component = {}
        for result in results:
            component = result.component_combination
            if component not in by_component:
                by_component[component] = {"total": 0, "success": 0, "failed": 0}
            by_component[component]["total"] += 1
            if result.success:
                by_component[component]["success"] += 1
            else:
                by_component[component]["failed"] += 1
        
        # Group by complexity level
        by_complexity = {}
        for result in results:
            complexity = result.complexity_level
            if complexity not in by_complexity:
                by_complexity[complexity] = {"total": 0, "success": 0, "failed": 0}
            by_complexity[complexity]["total"] += 1
            if result.success:
                by_complexity[complexity]["success"] += 1
            else:
                by_complexity[complexity]["failed"] += 1
        
        # Calculate average response times
        avg_response_time = sum(r.response_time_ms for r in results) / total_tests if total_tests > 0 else 0
        
        return {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_execution_time_seconds": total_time,
                "average_response_time_ms": avg_response_time
            },
            "by_component": by_component,
            "by_complexity": by_complexity,
            "timestamp": datetime.now().isoformat()
        }

    async def _save_results(self, results: List[TestResult], summary: Dict[str, Any]):
        """Save test results to files"""
        results_dir = Path("/app/test_results")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = results_dir / f"test_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump([asdict(r) for r in results], f, indent=2)
        
        # Save summary
        summary_file = results_dir / f"test_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save human-readable report
        report_file = results_dir / f"test_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("SARVANOM COMPREHENSIVE TEST REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Test Execution Time: {datetime.now().isoformat()}\n")
            f.write(f"Total Tests: {summary['test_summary']['total_tests']}\n")
            f.write(f"Successful: {summary['test_summary']['successful_tests']}\n")
            f.write(f"Failed: {summary['test_summary']['failed_tests']}\n")
            f.write(f"Success Rate: {summary['test_summary']['success_rate']:.2f}%\n")
            f.write(f"Total Execution Time: {summary['test_summary']['total_execution_time_seconds']:.2f}s\n")
            f.write(f"Average Response Time: {summary['test_summary']['average_response_time_ms']:.2f}ms\n\n")
            
            f.write("BY COMPONENT:\n")
            f.write("-" * 40 + "\n")
            for component, stats in summary['by_component'].items():
                success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                f.write(f"{component}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)\n")
            
            f.write("\nBY COMPLEXITY:\n")
            f.write("-" * 40 + "\n")
            for complexity, stats in summary['by_complexity'].items():
                success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                f.write(f"{complexity}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)\n")
        
        logger.info(f"📊 Test results saved to {results_dir}")
        logger.info(f"📄 Detailed results: {results_file}")
        logger.info(f"📋 Summary: {summary_file}")
        logger.info(f"📝 Report: {report_file}")

async def main():
    """Main function to run comprehensive tests"""
    runner = ComprehensiveTestRunner()
    
    try:
        summary = await runner.run_comprehensive_tests()
        
        # Print summary to console
        print("\n" + "=" * 80)
        print("SARVANOM COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {summary['test_summary']['total_tests']}")
        print(f"Successful: {summary['test_summary']['successful_tests']}")
        print(f"Failed: {summary['test_summary']['failed_tests']}")
        print(f"Success Rate: {summary['test_summary']['success_rate']:.2f}%")
        print(f"Total Time: {summary['test_summary']['total_execution_time_seconds']:.2f}s")
        print(f"Avg Response Time: {summary['test_summary']['average_response_time_ms']:.2f}ms")
        
        if summary['test_summary']['success_rate'] >= 80:
            print("\n🎉 TESTS PASSED! System is working as expected.")
            return 0
        else:
            print("\n⚠️ TESTS FAILED! System needs attention.")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Test runner failed: {e}")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
