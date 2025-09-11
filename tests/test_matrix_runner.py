"""
Test Matrix Runner - SarvanOM v2
Comprehensive test matrix implementation covering all system components and their interactions.
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import aiohttp
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryComplexity(Enum):
    SIMPLE = "simple"
    TECHNICAL = "technical"
    RESEARCH = "research"
    MULTIMEDIA = "multimedia"

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"

class DatabaseType(Enum):
    QDRANT = "qdrant"
    ARANGODB = "arangodb"
    MEILISEARCH = "meilisearch"
    POSTGRESQL = "postgresql"

class GuidedPromptMode(Enum):
    ON = "on"
    OFF = "off"
    ALWAYS_BYPASS = "always_bypass"
    ADAPTIVE = "adaptive"

@dataclass
class TestResult:
    test_id: str
    category: str
    provider: str
    database: str
    complexity: str
    guided_prompt_mode: str
    response_time: float
    success: bool
    error_message: Optional[str] = None
    quality_score: Optional[float] = None
    sla_compliant: bool = False
    timestamp: float = 0.0

@dataclass
class SLAMetrics:
    total_tests: int = 0
    successful_tests: int = 0
    failed_tests: int = 0
    sla_violations: int = 0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    error_rate: float = 0.0
    availability: float = 0.0

class TestMatrixRunner:
    """Comprehensive test matrix runner for SarvanOM v2"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.sla_metrics = SLAMetrics()
        
        # SLA thresholds
        self.sla_thresholds = {
            QueryComplexity.SIMPLE: 5.0,
            QueryComplexity.TECHNICAL: 7.0,
            QueryComplexity.RESEARCH: 10.0,
            QueryComplexity.MULTIMEDIA: 10.0
        }
        
        # Test prompts by complexity
        self.test_prompts = {
            QueryComplexity.SIMPLE: [
                "What is the capital of France?",
                "Define machine learning",
                "What is 15% of 200?",
                "What day is it today?"
            ],
            QueryComplexity.TECHNICAL: [
                "Write a Python function to sort a list",
                "How does a neural network work?",
                "How do I use the OpenAI API?",
                "Why is this code not working?"
            ],
            QueryComplexity.RESEARCH: [
                "Compare the pros and cons of different AI approaches",
                "What are the latest developments in NLP?",
                "Analyze the impact of AI on healthcare",
                "Describe this image and explain its relevance"
            ],
            QueryComplexity.MULTIMEDIA: [
                "Analyze this image and provide insights",
                "Transcribe this audio and summarize the key points",
                "Process this document and extract key information"
            ]
        }
        
        # Guided Prompt test scenarios
        self.guided_prompt_scenarios = {
            "ambiguous": [
                "Show me apple",
                "Tell me about python",
                "What's the latest on tesla?"
            ],
            "pii_heavy": [
                "My email is john.doe@example.com and I need help",
                "Call me at 555-123-4567 about the meeting",
                "My SSN is 123-45-6789, help me with taxes"
            ],
            "multilingual": [
                "¿Cuál es la capital de España?",
                "東京の人口は何人ですか？",
                "Quelle est la population de Paris?"
            ],
            "constraints": [
                "Show me recent news about AI",
                "Find academic papers on machine learning",
                "Search for free resources on Python programming"
            ]
        }

    async def run_single_test(self, 
                            test_id: str,
                            category: str,
                            provider: LLMProvider,
                            database: DatabaseType,
                            complexity: QueryComplexity,
                            guided_prompt_mode: GuidedPromptMode,
                            prompt: str) -> TestResult:
        """Run a single test case"""
        
        start_time = time.time()
        success = False
        error_message = None
        quality_score = None
        
        try:
            # Prepare request payload
            payload = {
                "query": prompt,
                "complexity": complexity.value,
                "provider": provider.value,
                "database": database.value,
                "guided_prompt_mode": guided_prompt_mode.value,
                "test_mode": True
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/query/comprehensive",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        success = True
                        quality_score = data.get("quality_score", 0.0)
                    else:
                        error_message = f"HTTP {response.status}: {await response.text()}"
                        
        except asyncio.TimeoutError:
            error_message = "Request timeout"
        except Exception as e:
            error_message = str(e)
        
        response_time = time.time() - start_time
        
        # Check SLA compliance
        sla_threshold = self.sla_thresholds[complexity]
        sla_compliant = response_time <= sla_threshold
        
        result = TestResult(
            test_id=test_id,
            category=category,
            provider=provider.value,
            database=database.value,
            complexity=complexity.value,
            guided_prompt_mode=guided_prompt_mode.value,
            response_time=response_time,
            success=success,
            error_message=error_message,
            quality_score=quality_score,
            sla_compliant=sla_compliant,
            timestamp=time.time()
        )
        
        return result

    async def run_llm_provider_tests(self) -> List[TestResult]:
        """Run tests across all LLM providers"""
        logger.info("Running LLM provider tests...")
        results = []
        
        tasks = []
        for provider in LLMProvider:
            for complexity in QueryComplexity:
                for prompt in self.test_prompts[complexity]:
                    test_id = f"llm_{provider.value}_{complexity.value}_{hash(prompt) % 10000}"
                    task = self.run_single_test(
                        test_id=test_id,
                        category="llm_provider",
                        provider=provider,
                        database=DatabaseType.QDRANT,  # Default database
                        complexity=complexity,
                        guided_prompt_mode=GuidedPromptMode.ON,
                        prompt=prompt
                    )
                    tasks.append(task)
        
        # Run tests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, TestResult)]
        return valid_results

    async def run_database_tests(self) -> List[TestResult]:
        """Run tests across all database types"""
        logger.info("Running database tests...")
        results = []
        
        tasks = []
        for database in DatabaseType:
            for complexity in QueryComplexity:
                for prompt in self.test_prompts[complexity]:
                    test_id = f"db_{database.value}_{complexity.value}_{hash(prompt) % 10000}"
                    task = self.run_single_test(
                        test_id=test_id,
                        category="database",
                        provider=LLMProvider.OPENAI,  # Default provider
                        database=database,
                        complexity=complexity,
                        guided_prompt_mode=GuidedPromptMode.ON,
                        prompt=prompt
                    )
                    tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results = [r for r in results if isinstance(r, TestResult)]
        return valid_results

    async def run_guided_prompt_tests(self) -> List[TestResult]:
        """Run Guided Prompt Confirmation tests"""
        logger.info("Running Guided Prompt tests...")
        results = []
        
        tasks = []
        for mode in GuidedPromptMode:
            for scenario_type, prompts in self.guided_prompt_scenarios.items():
                for prompt in prompts:
                    test_id = f"gp_{mode.value}_{scenario_type}_{hash(prompt) % 10000}"
                    task = self.run_single_test(
                        test_id=test_id,
                        category="guided_prompt",
                        provider=LLMProvider.OPENAI,
                        database=DatabaseType.QDRANT,
                        complexity=QueryComplexity.SIMPLE,
                        guided_prompt_mode=mode,
                        prompt=prompt
                    )
                    tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results = [r for r in results if isinstance(r, TestResult)]
        return valid_results

    async def run_combinatorial_tests(self) -> List[TestResult]:
        """Run combinatorial tests across all dimensions"""
        logger.info("Running combinatorial tests...")
        results = []
        
        # Sample combinatorial tests (not exhaustive due to complexity)
        test_combinations = [
            (LLMProvider.OPENAI, DatabaseType.QDRANT, QueryComplexity.SIMPLE),
            (LLMProvider.ANTHROPIC, DatabaseType.ARANGODB, QueryComplexity.TECHNICAL),
            (LLMProvider.HUGGINGFACE, DatabaseType.MEILISEARCH, QueryComplexity.RESEARCH),
            (LLMProvider.OLLAMA, DatabaseType.POSTGRESQL, QueryComplexity.MULTIMEDIA),
        ]
        
        tasks = []
        for provider, database, complexity in test_combinations:
            for prompt in self.test_prompts[complexity][:2]:  # Limit to 2 prompts per combination
                for mode in GuidedPromptMode:
                    test_id = f"combo_{provider.value}_{database.value}_{complexity.value}_{mode.value}_{hash(prompt) % 10000}"
                    task = self.run_single_test(
                        test_id=test_id,
                        category="combinatorial",
                        provider=provider,
                        database=database,
                        complexity=complexity,
                        guided_prompt_mode=mode,
                        prompt=prompt
                    )
                    tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results = [r for r in results if isinstance(r, TestResult)]
        return valid_results

    def calculate_sla_metrics(self, results: List[TestResult]) -> SLAMetrics:
        """Calculate SLA compliance metrics"""
        if not results:
            return SLAMetrics()
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - successful_tests
        sla_violations = sum(1 for r in results if not r.sla_compliant)
        
        response_times = [r.response_time for r in results if r.success]
        if response_times:
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        else:
            avg_response_time = p95_response_time = p99_response_time = 0.0
        
        error_rate = (failed_tests / total_tests) * 100 if total_tests > 0 else 0.0
        availability = (successful_tests / total_tests) * 100 if total_tests > 0 else 0.0
        
        return SLAMetrics(
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            sla_violations=sla_violations,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            error_rate=error_rate,
            availability=availability
        )

    def generate_report(self, results: List[TestResult]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        metrics = self.calculate_sla_metrics(results)
        
        # Group results by category
        by_category = {}
        for result in results:
            if result.category not in by_category:
                by_category[result.category] = []
            by_category[result.category].append(result)
        
        # Calculate category-specific metrics
        category_metrics = {}
        for category, category_results in by_category.items():
            category_metrics[category] = self.calculate_sla_metrics(category_results)
        
        # SLA compliance by complexity
        complexity_compliance = {}
        for complexity in QueryComplexity:
            complexity_results = [r for r in results if r.complexity == complexity.value]
            if complexity_results:
                compliance_rate = sum(1 for r in complexity_results if r.sla_compliant) / len(complexity_results)
                complexity_compliance[complexity.value] = {
                    "total_tests": len(complexity_results),
                    "compliant_tests": sum(1 for r in complexity_results if r.sla_compliant),
                    "compliance_rate": compliance_rate,
                    "avg_response_time": statistics.mean([r.response_time for r in complexity_results if r.success])
                }
        
        report = {
            "test_summary": {
                "total_tests": metrics.total_tests,
                "successful_tests": metrics.successful_tests,
                "failed_tests": metrics.failed_tests,
                "sla_violations": metrics.sla_violations,
                "overall_sla_compliance": (metrics.total_tests - metrics.sla_violations) / metrics.total_tests if metrics.total_tests > 0 else 0.0
            },
            "performance_metrics": {
                "avg_response_time": metrics.avg_response_time,
                "p95_response_time": metrics.p95_response_time,
                "p99_response_time": metrics.p99_response_time,
                "error_rate": metrics.error_rate,
                "availability": metrics.availability
            },
            "category_metrics": {k: asdict(v) for k, v in category_metrics.items()},
            "complexity_compliance": complexity_compliance,
            "sla_thresholds": {k.value: v for k, v in self.sla_thresholds.items()},
            "timestamp": time.time()
        }
        
        return report

    async def run_full_test_matrix(self) -> Dict[str, Any]:
        """Run the complete test matrix"""
        logger.info("Starting comprehensive test matrix execution...")
        
        all_results = []
        
        # Run all test categories
        test_categories = [
            self.run_llm_provider_tests(),
            self.run_database_tests(),
            self.run_guided_prompt_tests(),
            self.run_combinatorial_tests()
        ]
        
        for category_results in await asyncio.gather(*test_categories):
            all_results.extend(category_results)
        
        # Generate comprehensive report
        report = self.generate_report(all_results)
        
        logger.info(f"Test matrix completed. Total tests: {len(all_results)}")
        logger.info(f"Overall SLA compliance: {report['test_summary']['overall_sla_compliance']:.2%}")
        
        return report

    def save_results(self, results: List[TestResult], filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"test_matrix_results_{timestamp}.json"
        
        # Convert results to serializable format
        serializable_results = [asdict(result) for result in results]
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"Results saved to {filename}")

    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save test report to file"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"test_matrix_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {filename}")

# Pytest integration
class TestMatrixPytest:
    """Pytest integration for test matrix"""
    
    @pytest.fixture
    def test_runner(self):
        return TestMatrixRunner()
    
    @pytest.mark.asyncio
    async def test_llm_providers(self, test_runner):
        """Test all LLM providers"""
        results = await test_runner.run_llm_provider_tests()
        assert len(results) > 0, "No LLM provider tests executed"
        
        # Check that all providers were tested
        providers_tested = set(r.provider for r in results)
        assert len(providers_tested) == len(LLMProvider), f"Not all providers tested: {providers_tested}"
    
    @pytest.mark.asyncio
    async def test_databases(self, test_runner):
        """Test all database types"""
        results = await test_runner.run_database_tests()
        assert len(results) > 0, "No database tests executed"
        
        # Check that all databases were tested
        databases_tested = set(r.database for r in results)
        assert len(databases_tested) == len(DatabaseType), f"Not all databases tested: {databases_tested}"
    
    @pytest.mark.asyncio
    async def test_guided_prompt(self, test_runner):
        """Test Guided Prompt Confirmation"""
        results = await test_runner.run_guided_prompt_tests()
        assert len(results) > 0, "No Guided Prompt tests executed"
        
        # Check that all modes were tested
        modes_tested = set(r.guided_prompt_mode for r in results)
        assert len(modes_tested) == len(GuidedPromptMode), f"Not all Guided Prompt modes tested: {modes_tested}"
    
    @pytest.mark.asyncio
    async def test_sla_compliance(self, test_runner):
        """Test SLA compliance across all test categories"""
        results = await test_runner.run_full_test_matrix()
        
        # Check overall SLA compliance
        overall_compliance = results['test_summary']['overall_sla_compliance']
        assert overall_compliance >= 0.95, f"SLA compliance too low: {overall_compliance:.2%}"
        
        # Check complexity-specific compliance
        for complexity, compliance_data in results['complexity_compliance'].items():
            compliance_rate = compliance_data['compliance_rate']
            assert compliance_rate >= 0.90, f"SLA compliance for {complexity} too low: {compliance_rate:.2%}"

if __name__ == "__main__":
    async def main():
        runner = TestMatrixRunner()
        
        # Run full test matrix
        report = await runner.run_full_test_matrix()
        
        # Save results
        runner.save_report(report)
        
        # Print summary
        print("\n" + "="*50)
        print("TEST MATRIX EXECUTION SUMMARY")
        print("="*50)
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Successful: {report['test_summary']['successful_tests']}")
        print(f"Failed: {report['test_summary']['failed_tests']}")
        print(f"SLA Violations: {report['test_summary']['sla_violations']}")
        print(f"Overall SLA Compliance: {report['test_summary']['overall_sla_compliance']:.2%}")
        print(f"Average Response Time: {report['performance_metrics']['avg_response_time']:.2f}s")
        print(f"P95 Response Time: {report['performance_metrics']['p95_response_time']:.2f}s")
        print(f"Availability: {report['performance_metrics']['availability']:.2f}%")
        print("="*50)
    
    asyncio.run(main())
