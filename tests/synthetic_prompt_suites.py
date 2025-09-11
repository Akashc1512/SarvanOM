"""
Synthetic Prompt Suites - SarvanOM v2
Comprehensive synthetic prompt suites for testing all system capabilities and scenarios.
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aiohttp
import random
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptCategory(Enum):
    SIMPLE_FACTS = "simple_facts"
    TECHNICAL_EXPLANATIONS = "technical_explanations"
    RESEARCH_ANALYSIS = "research_analysis"
    MULTIMEDIA_PROCESSING = "multimedia_processing"
    GUIDED_PROMPT_AMBIGUOUS = "guided_prompt_ambiguous"
    GUIDED_PROMPT_PII = "guided_prompt_pii"
    GUIDED_PROMPT_MULTILINGUAL = "guided_prompt_multilingual"
    GUIDED_PROMPT_CONSTRAINTS = "guided_prompt_constraints"
    CODE_GENERATION = "code_generation"
    DEBUGGING = "debugging"
    CREATIVE_WRITING = "creative_writing"
    DATA_ANALYSIS = "data_analysis"

class ComplexityLevel(Enum):
    SIMPLE = "simple"
    TECHNICAL = "technical"
    RESEARCH = "research"
    MULTIMEDIA = "multimedia"

@dataclass
class PromptTestCase:
    id: str
    category: str
    complexity: str
    prompt: str
    expected_refinement: Optional[str] = None
    refinement_type: Optional[str] = None
    expected_acceptance_rate: Optional[float] = None
    expected_response_time: Optional[float] = None
    expected_quality_score: Optional[float] = None
    metadata: Dict[str, Any] = None

@dataclass
class PromptSuiteResult:
    suite_id: str
    category: str
    total_tests: int
    successful_tests: int
    failed_tests: int
    avg_response_time: float
    avg_quality_score: float
    acceptance_rate: float
    sla_compliance_rate: float
    results: List[Dict[str, Any]]

class SyntheticPromptSuites:
    """Comprehensive synthetic prompt suites for testing SarvanOM v2"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.suites = self._load_prompt_suites()
        
    def _load_prompt_suites(self) -> Dict[str, List[PromptTestCase]]:
        """Load all prompt test suites"""
        suites = {}
        
        # Simple Facts Suite
        suites[PromptCategory.SIMPLE_FACTS.value] = [
            PromptTestCase(
                id="sf_001",
                category=PromptCategory.SIMPLE_FACTS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="What is the capital of France?",
                expected_response_time=2.0,
                expected_quality_score=0.95
            ),
            PromptTestCase(
                id="sf_002",
                category=PromptCategory.SIMPLE_FACTS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Define machine learning",
                expected_response_time=3.0,
                expected_quality_score=0.90
            ),
            PromptTestCase(
                id="sf_003",
                category=PromptCategory.SIMPLE_FACTS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="What is 15% of 200?",
                expected_response_time=1.0,
                expected_quality_score=0.98
            ),
            PromptTestCase(
                id="sf_004",
                category=PromptCategory.SIMPLE_FACTS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="What day is it today?",
                expected_response_time=1.5,
                expected_quality_score=0.95
            ),
            PromptTestCase(
                id="sf_005",
                category=PromptCategory.SIMPLE_FACTS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Who is the current president of the United States?",
                expected_response_time=2.5,
                expected_quality_score=0.92
            )
        ]
        
        # Technical Explanations Suite
        suites[PromptCategory.TECHNICAL_EXPLANATIONS.value] = [
            PromptTestCase(
                id="te_001",
                category=PromptCategory.TECHNICAL_EXPLANATIONS.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="How does a neural network work?",
                expected_response_time=5.0,
                expected_quality_score=0.88
            ),
            PromptTestCase(
                id="te_002",
                category=PromptCategory.TECHNICAL_EXPLANATIONS.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="Explain the difference between supervised and unsupervised learning",
                expected_response_time=6.0,
                expected_quality_score=0.85
            ),
            PromptTestCase(
                id="te_003",
                category=PromptCategory.TECHNICAL_EXPLANATIONS.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="How do I use the OpenAI API?",
                expected_response_time=4.0,
                expected_quality_score=0.90
            ),
            PromptTestCase(
                id="te_004",
                category=PromptCategory.TECHNICAL_EXPLANATIONS.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="What is the difference between REST and GraphQL APIs?",
                expected_response_time=5.5,
                expected_quality_score=0.87
            ),
            PromptTestCase(
                id="te_005",
                category=PromptCategory.TECHNICAL_EXPLANATIONS.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="Explain microservices architecture",
                expected_response_time=6.5,
                expected_quality_score=0.83
            )
        ]
        
        # Research Analysis Suite
        suites[PromptCategory.RESEARCH_ANALYSIS.value] = [
            PromptTestCase(
                id="ra_001",
                category=PromptCategory.RESEARCH_ANALYSIS.value,
                complexity=ComplexityLevel.RESEARCH.value,
                prompt="Compare the pros and cons of different AI approaches",
                expected_response_time=8.0,
                expected_quality_score=0.80
            ),
            PromptTestCase(
                id="ra_002",
                category=PromptCategory.RESEARCH_ANALYSIS.value,
                complexity=ComplexityLevel.RESEARCH.value,
                prompt="What are the latest developments in NLP?",
                expected_response_time=9.0,
                expected_quality_score=0.78
            ),
            PromptTestCase(
                id="ra_003",
                category=PromptCategory.RESEARCH_ANALYSIS.value,
                complexity=ComplexityLevel.RESEARCH.value,
                prompt="Analyze the impact of AI on healthcare",
                expected_response_time=10.0,
                expected_quality_score=0.75
            ),
            PromptTestCase(
                id="ra_004",
                category=PromptCategory.RESEARCH_ANALYSIS.value,
                complexity=ComplexityLevel.RESEARCH.value,
                prompt="Review the current state of quantum computing",
                expected_response_time=9.5,
                expected_quality_score=0.77
            ),
            PromptTestCase(
                id="ra_005",
                category=PromptCategory.RESEARCH_ANALYSIS.value,
                complexity=ComplexityLevel.RESEARCH.value,
                prompt="Evaluate the effectiveness of different machine learning algorithms",
                expected_response_time=8.5,
                expected_quality_score=0.82
            )
        ]
        
        # Guided Prompt Ambiguous Suite
        suites[PromptCategory.GUIDED_PROMPT_AMBIGUOUS.value] = [
            PromptTestCase(
                id="gp_ambiguous_001",
                category=PromptCategory.GUIDED_PROMPT_AMBIGUOUS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Show me apple",
                expected_refinement="Do you mean Apple Inc. (company) stock performance, or the fruit Apple nutritional info?",
                refinement_type="disambiguation",
                expected_acceptance_rate=0.7
            ),
            PromptTestCase(
                id="gp_ambiguous_002",
                category=PromptCategory.GUIDED_PROMPT_AMBIGUOUS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Tell me about python",
                expected_refinement="Do you mean Python programming language, or the Python snake species?",
                refinement_type="disambiguation",
                expected_acceptance_rate=0.8
            ),
            PromptTestCase(
                id="gp_ambiguous_003",
                category=PromptCategory.GUIDED_PROMPT_AMBIGUOUS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="What's the latest on tesla?",
                expected_refinement="Do you mean Tesla Inc. (electric vehicle company), or Nikola Tesla (inventor)?",
                refinement_type="disambiguation",
                expected_acceptance_rate=0.75
            ),
            PromptTestCase(
                id="gp_ambiguous_004",
                category=PromptCategory.GUIDED_PROMPT_AMBIGUOUS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Show me java",
                expected_refinement="Do you mean Java programming language, or Java island in Indonesia?",
                refinement_type="disambiguation",
                expected_acceptance_rate=0.85
            ),
            PromptTestCase(
                id="gp_ambiguous_005",
                category=PromptCategory.GUIDED_PROMPT_AMBIGUOUS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Tell me about amazon",
                expected_refinement="Do you mean Amazon.com (e-commerce company), or the Amazon rainforest?",
                refinement_type="disambiguation",
                expected_acceptance_rate=0.8
            )
        ]
        
        # Guided Prompt PII Suite
        suites[PromptCategory.GUIDED_PROMPT_PII.value] = [
            PromptTestCase(
                id="gp_pii_001",
                category=PromptCategory.GUIDED_PROMPT_PII.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="My email is john.doe@example.com and I need help with my account",
                expected_refinement="I can help with account issues. For privacy, I'll remove your email address from this query.",
                refinement_type="sanitization",
                expected_acceptance_rate=0.9
            ),
            PromptTestCase(
                id="gp_pii_002",
                category=PromptCategory.GUIDED_PROMPT_PII.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Call me at 555-123-4567 about the meeting",
                expected_refinement="I can help with meeting information. For privacy, I'll remove your phone number from this query.",
                refinement_type="sanitization",
                expected_acceptance_rate=0.9
            ),
            PromptTestCase(
                id="gp_pii_003",
                category=PromptCategory.GUIDED_PROMPT_PII.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="My SSN is 123-45-6789, help me with taxes",
                expected_refinement="I can help with tax information. For privacy, I'll remove your SSN from this query.",
                refinement_type="sanitization",
                expected_acceptance_rate=0.95
            ),
            PromptTestCase(
                id="gp_pii_004",
                category=PromptCategory.GUIDED_PROMPT_PII.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="My credit card number is 4532-1234-5678-9012, is it valid?",
                expected_refinement="I can help with credit card validation. For security, I'll remove your credit card number from this query.",
                refinement_type="sanitization",
                expected_acceptance_rate=0.95
            ),
            PromptTestCase(
                id="gp_pii_005",
                category=PromptCategory.GUIDED_PROMPT_PII.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="My address is 123 Main St, Anytown, USA 12345",
                expected_refinement="I can help with location-based queries. For privacy, I'll remove your address from this query.",
                refinement_type="sanitization",
                expected_acceptance_rate=0.9
            )
        ]
        
        # Guided Prompt Multilingual Suite
        suites[PromptCategory.GUIDED_PROMPT_MULTILINGUAL.value] = [
            PromptTestCase(
                id="gp_multilingual_001",
                category=PromptCategory.GUIDED_PROMPT_MULTILINGUAL.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="¿Cuál es la capital de España?",
                expected_refinement="I'll search for information about Spain's capital city.",
                refinement_type="intent_analysis",
                expected_acceptance_rate=0.8
            ),
            PromptTestCase(
                id="gp_multilingual_002",
                category=PromptCategory.GUIDED_PROMPT_MULTILINGUAL.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="東京の人口は何人ですか？",
                expected_refinement="I'll search for Tokyo's population information.",
                refinement_type="intent_analysis",
                expected_acceptance_rate=0.8
            ),
            PromptTestCase(
                id="gp_multilingual_003",
                category=PromptCategory.GUIDED_PROMPT_MULTILINGUAL.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Quelle est la population de Paris?",
                expected_refinement="I'll search for Paris population information.",
                refinement_type="intent_analysis",
                expected_acceptance_rate=0.8
            ),
            PromptTestCase(
                id="gp_multilingual_004",
                category=PromptCategory.GUIDED_PROMPT_MULTILINGUAL.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Wie ist das Wetter heute?",
                expected_refinement="I'll search for today's weather information.",
                refinement_type="intent_analysis",
                expected_acceptance_rate=0.8
            ),
            PromptTestCase(
                id="gp_multilingual_005",
                category=PromptCategory.GUIDED_PROMPT_MULTILINGUAL.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Qual é a moeda do Brasil?",
                expected_refinement="I'll search for Brazil's currency information.",
                refinement_type="intent_analysis",
                expected_acceptance_rate=0.8
            )
        ]
        
        # Guided Prompt Constraints Suite
        suites[PromptCategory.GUIDED_PROMPT_CONSTRAINTS.value] = [
            PromptTestCase(
                id="gp_constraints_001",
                category=PromptCategory.GUIDED_PROMPT_CONSTRAINTS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Show me recent news about AI",
                expected_refinement="I'll search for recent AI news. Would you like to specify a time range (last week, month) or particular sources?",
                refinement_type="constraint_application",
                expected_acceptance_rate=0.6
            ),
            PromptTestCase(
                id="gp_constraints_002",
                category=PromptCategory.GUIDED_PROMPT_CONSTRAINTS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Find academic papers on machine learning",
                expected_refinement="I'll search for academic papers on machine learning. Would you like to specify a publication date range or particular journals?",
                refinement_type="constraint_application",
                expected_acceptance_rate=0.7
            ),
            PromptTestCase(
                id="gp_constraints_003",
                category=PromptCategory.GUIDED_PROMPT_CONSTRAINTS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Search for free resources on Python programming",
                expected_refinement="I'll search for free Python programming resources. Would you like to specify a particular skill level (beginner, intermediate, advanced)?",
                refinement_type="constraint_application",
                expected_acceptance_rate=0.8
            ),
            PromptTestCase(
                id="gp_constraints_004",
                category=PromptCategory.GUIDED_PROMPT_CONSTRAINTS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Show me stock prices for tech companies",
                expected_refinement="I'll search for tech company stock prices. Would you like to specify particular companies or a time range?",
                refinement_type="constraint_application",
                expected_acceptance_rate=0.65
            ),
            PromptTestCase(
                id="gp_constraints_005",
                category=PromptCategory.GUIDED_PROMPT_CONSTRAINTS.value,
                complexity=ComplexityLevel.SIMPLE.value,
                prompt="Find information about climate change",
                expected_refinement="I'll search for climate change information. Would you like to focus on a particular aspect (causes, effects, solutions) or geographic region?",
                refinement_type="constraint_application",
                expected_acceptance_rate=0.7
            )
        ]
        
        # Code Generation Suite
        suites[PromptCategory.CODE_GENERATION.value] = [
            PromptTestCase(
                id="cg_001",
                category=PromptCategory.CODE_GENERATION.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="Write a Python function to sort a list",
                expected_response_time=4.0,
                expected_quality_score=0.92
            ),
            PromptTestCase(
                id="cg_002",
                category=PromptCategory.CODE_GENERATION.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="Create a REST API endpoint in Node.js",
                expected_response_time=6.0,
                expected_quality_score=0.88
            ),
            PromptTestCase(
                id="cg_003",
                category=PromptCategory.CODE_GENERATION.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="Write a SQL query to find duplicate records",
                expected_response_time=3.0,
                expected_quality_score=0.90
            ),
            PromptTestCase(
                id="cg_004",
                category=PromptCategory.CODE_GENERATION.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="Create a React component for a todo list",
                expected_response_time=5.0,
                expected_quality_score=0.85
            ),
            PromptTestCase(
                id="cg_005",
                category=PromptCategory.CODE_GENERATION.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="Write a Dockerfile for a Python web application",
                expected_response_time=4.5,
                expected_quality_score=0.87
            )
        ]
        
        # Debugging Suite
        suites[PromptCategory.DEBUGGING.value] = [
            PromptTestCase(
                id="db_001",
                category=PromptCategory.DEBUGGING.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="Why is this code not working? def add(a, b): return a + b print(add(1, 2))",
                expected_response_time=3.0,
                expected_quality_score=0.95
            ),
            PromptTestCase(
                id="db_002",
                category=PromptCategory.DEBUGGING.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="My API is returning 500 errors, how do I debug it?",
                expected_response_time=5.0,
                expected_quality_score=0.88
            ),
            PromptTestCase(
                id="db_003",
                category=PromptCategory.DEBUGGING.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="This SQL query is running slowly, how can I optimize it?",
                expected_response_time=4.0,
                expected_quality_score=0.90
            ),
            PromptTestCase(
                id="db_004",
                category=PromptCategory.DEBUGGING.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="My React component is not re-rendering, what's wrong?",
                expected_response_time=4.5,
                expected_quality_score=0.87
            ),
            PromptTestCase(
                id="db_005",
                category=PromptCategory.DEBUGGING.value,
                complexity=ComplexityLevel.TECHNICAL.value,
                prompt="I'm getting a memory leak in my Node.js application",
                expected_response_time=6.0,
                expected_quality_score=0.85
            )
        ]
        
        return suites

    async def run_single_test(self, test_case: PromptTestCase) -> Dict[str, Any]:
        """Run a single prompt test case"""
        start_time = time.time()
        success = False
        error_message = None
        response_data = None
        quality_score = None
        refinement_data = None
        
        try:
            # Prepare request payload
            payload = {
                "query": test_case.prompt,
                "complexity": test_case.complexity,
                "test_mode": True,
                "category": test_case.category
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/query/comprehensive",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        success = True
                        quality_score = response_data.get("quality_score", 0.0)
                        refinement_data = response_data.get("refinement_data")
                    else:
                        error_message = f"HTTP {response.status}: {await response.text()}"
                        
        except asyncio.TimeoutError:
            error_message = "Request timeout"
        except Exception as e:
            error_message = str(e)
        
        response_time = time.time() - start_time
        
        # Check if Guided Prompt was triggered
        guided_prompt_triggered = False
        if refinement_data and test_case.expected_refinement:
            guided_prompt_triggered = True
        
        result = {
            "test_id": test_case.id,
            "category": test_case.category,
            "complexity": test_case.complexity,
            "prompt": test_case.prompt,
            "success": success,
            "response_time": response_time,
            "error_message": error_message,
            "quality_score": quality_score,
            "guided_prompt_triggered": guided_prompt_triggered,
            "refinement_data": refinement_data,
            "expected_refinement": test_case.expected_refinement,
            "expected_acceptance_rate": test_case.expected_acceptance_rate,
            "expected_response_time": test_case.expected_response_time,
            "expected_quality_score": test_case.expected_quality_score,
            "sla_compliant": self._check_sla_compliance(test_case, response_time),
            "timestamp": time.time()
        }
        
        return result

    def _check_sla_compliance(self, test_case: PromptTestCase, response_time: float) -> bool:
        """Check if response time meets SLA requirements"""
        complexity_thresholds = {
            ComplexityLevel.SIMPLE.value: 5.0,
            ComplexityLevel.TECHNICAL.value: 7.0,
            ComplexityLevel.RESEARCH.value: 10.0,
            ComplexityLevel.MULTIMEDIA.value: 10.0
        }
        
        threshold = complexity_thresholds.get(test_case.complexity, 10.0)
        return response_time <= threshold

    async def run_suite(self, suite_name: str) -> PromptSuiteResult:
        """Run a complete prompt suite"""
        if suite_name not in self.suites:
            raise ValueError(f"Suite '{suite_name}' not found")
        
        test_cases = self.suites[suite_name]
        logger.info(f"Running suite '{suite_name}' with {len(test_cases)} test cases")
        
        # Run all tests in the suite
        tasks = [self.run_single_test(test_case) for test_case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, dict)]
        
        # Calculate suite metrics
        total_tests = len(valid_results)
        successful_tests = sum(1 for r in valid_results if r["success"])
        failed_tests = total_tests - successful_tests
        
        response_times = [r["response_time"] for r in valid_results if r["success"]]
        quality_scores = [r["quality_score"] for r in valid_results if r["success"] and r["quality_score"] is not None]
        sla_compliant_tests = sum(1 for r in valid_results if r["sla_compliant"])
        
        avg_response_time = statistics.mean(response_times) if response_times else 0.0
        avg_quality_score = statistics.mean(quality_scores) if quality_scores else 0.0
        acceptance_rate = successful_tests / total_tests if total_tests > 0 else 0.0
        sla_compliance_rate = sla_compliant_tests / total_tests if total_tests > 0 else 0.0
        
        suite_result = PromptSuiteResult(
            suite_id=suite_name,
            category=suite_name,
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            avg_response_time=avg_response_time,
            avg_quality_score=avg_quality_score,
            acceptance_rate=acceptance_rate,
            sla_compliance_rate=sla_compliance_rate,
            results=valid_results
        )
        
        logger.info(f"Suite '{suite_name}' completed: {successful_tests}/{total_tests} successful, {sla_compliance_rate:.2%} SLA compliant")
        
        return suite_result

    async def run_all_suites(self) -> Dict[str, PromptSuiteResult]:
        """Run all prompt suites"""
        logger.info("Running all synthetic prompt suites...")
        
        suite_results = {}
        for suite_name in self.suites.keys():
            try:
                result = await self.run_suite(suite_name)
                suite_results[suite_name] = result
            except Exception as e:
                logger.error(f"Failed to run suite '{suite_name}': {e}")
        
        return suite_results

    def generate_comprehensive_report(self, suite_results: Dict[str, PromptSuiteResult]) -> Dict[str, Any]:
        """Generate comprehensive report from all suite results"""
        total_tests = sum(result.total_tests for result in suite_results.values())
        total_successful = sum(result.successful_tests for result in suite_results.values())
        total_failed = sum(result.failed_tests for result in suite_results.values())
        
        all_response_times = []
        all_quality_scores = []
        all_sla_compliant = 0
        
        for result in suite_results.values():
            all_response_times.extend([r["response_time"] for r in result.results if r["success"]])
            all_quality_scores.extend([r["quality_score"] for r in result.results if r["success"] and r["quality_score"] is not None])
            all_sla_compliant += sum(1 for r in result.results if r["sla_compliant"])
        
        overall_metrics = {
            "total_tests": total_tests,
            "successful_tests": total_successful,
            "failed_tests": total_failed,
            "success_rate": total_successful / total_tests if total_tests > 0 else 0.0,
            "avg_response_time": statistics.mean(all_response_times) if all_response_times else 0.0,
            "avg_quality_score": statistics.mean(all_quality_scores) if all_quality_scores else 0.0,
            "sla_compliance_rate": all_sla_compliant / total_tests if total_tests > 0 else 0.0
        }
        
        # Category-specific metrics
        category_metrics = {}
        for suite_name, result in suite_results.items():
            category_metrics[suite_name] = {
                "total_tests": result.total_tests,
                "successful_tests": result.successful_tests,
                "failed_tests": result.failed_tests,
                "success_rate": result.acceptance_rate,
                "avg_response_time": result.avg_response_time,
                "avg_quality_score": result.avg_quality_score,
                "sla_compliance_rate": result.sla_compliance_rate
            }
        
        # Guided Prompt specific metrics
        guided_prompt_metrics = {}
        guided_prompt_suites = [name for name in suite_results.keys() if "guided_prompt" in name]
        for suite_name in guided_prompt_suites:
            result = suite_results[suite_name]
            guided_prompt_triggered = sum(1 for r in result.results if r["guided_prompt_triggered"])
            guided_prompt_metrics[suite_name] = {
                "total_tests": result.total_tests,
                "guided_prompt_triggered": guided_prompt_triggered,
                "trigger_rate": guided_prompt_triggered / result.total_tests if result.total_tests > 0 else 0.0,
                "avg_response_time": result.avg_response_time,
                "sla_compliance_rate": result.sla_compliance_rate
            }
        
        report = {
            "report_timestamp": time.time(),
            "overall_metrics": overall_metrics,
            "category_metrics": category_metrics,
            "guided_prompt_metrics": guided_prompt_metrics,
            "suite_results": {name: asdict(result) for name, result in suite_results.items()},
            "recommendations": self._generate_recommendations(overall_metrics, category_metrics)
        }
        
        return report

    def _generate_recommendations(self, overall_metrics: Dict[str, Any], category_metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if overall_metrics["success_rate"] < 0.95:
            recommendations.append("Overall success rate is below 95%. Investigate and fix failing test cases.")
        
        if overall_metrics["sla_compliance_rate"] < 0.90:
            recommendations.append("SLA compliance rate is below 90%. Optimize response times for better performance.")
        
        if overall_metrics["avg_quality_score"] < 0.85:
            recommendations.append("Average quality score is below 85%. Improve response quality and accuracy.")
        
        # Category-specific recommendations
        for category, metrics in category_metrics.items():
            if metrics["success_rate"] < 0.90:
                recommendations.append(f"Improve success rate for {category} category: {metrics['success_rate']:.2%}")
            
            if metrics["sla_compliance_rate"] < 0.85:
                recommendations.append(f"Optimize response times for {category} category: {metrics['sla_compliance_rate']:.2%} SLA compliance")
        
        return recommendations

    def save_results(self, suite_results: Dict[str, PromptSuiteResult], filename: str = None):
        """Save suite results to file"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"synthetic_prompt_results_{timestamp}.json"
        
        serializable_results = {name: asdict(result) for name, result in suite_results.items()}
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"Results saved to {filename}")

    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save comprehensive report to file"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"synthetic_prompt_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {filename}")

# Pytest integration
class TestSyntheticPromptSuites:
    """Pytest integration for synthetic prompt suites"""
    
    @pytest.fixture
    def prompt_suites(self):
        return SyntheticPromptSuites()
    
    @pytest.mark.asyncio
    async def test_simple_facts_suite(self, prompt_suites):
        """Test simple facts prompt suite"""
        result = await prompt_suites.run_suite(PromptCategory.SIMPLE_FACTS.value)
        
        assert result.total_tests > 0, "No tests executed"
        assert result.successful_tests > 0, "No successful tests"
        assert result.sla_compliance_rate >= 0.90, f"SLA compliance too low: {result.sla_compliance_rate:.2%}"
    
    @pytest.mark.asyncio
    async def test_guided_prompt_ambiguous_suite(self, prompt_suites):
        """Test Guided Prompt ambiguous suite"""
        result = await prompt_suites.run_suite(PromptCategory.GUIDED_PROMPT_AMBIGUOUS.value)
        
        assert result.total_tests > 0, "No tests executed"
        assert result.successful_tests > 0, "No successful tests"
        
        # Check that Guided Prompt was triggered for ambiguous queries
        guided_prompt_triggered = sum(1 for r in result.results if r["guided_prompt_triggered"])
        assert guided_prompt_triggered > 0, "Guided Prompt should be triggered for ambiguous queries"
    
    @pytest.mark.asyncio
    async def test_guided_prompt_pii_suite(self, prompt_suites):
        """Test Guided Prompt PII suite"""
        result = await prompt_suites.run_suite(PromptCategory.GUIDED_PROMPT_PII.value)
        
        assert result.total_tests > 0, "No tests executed"
        assert result.successful_tests > 0, "No successful tests"
        
        # Check that PII sanitization was triggered
        guided_prompt_triggered = sum(1 for r in result.results if r["guided_prompt_triggered"])
        assert guided_prompt_triggered > 0, "Guided Prompt should be triggered for PII queries"
    
    @pytest.mark.asyncio
    async def test_all_suites(self, prompt_suites):
        """Test all prompt suites"""
        suite_results = await prompt_suites.run_all_suites()
        
        assert len(suite_results) > 0, "No suites executed"
        
        # Check that all expected suites were run
        expected_suites = [category.value for category in PromptCategory]
        executed_suites = set(suite_results.keys())
        assert len(executed_suites) >= len(expected_suites) // 2, f"Not enough suites executed: {executed_suites}"
        
        # Check overall success rate
        total_tests = sum(result.total_tests for result in suite_results.values())
        total_successful = sum(result.successful_tests for result in suite_results.values())
        success_rate = total_successful / total_tests if total_tests > 0 else 0.0
        
        assert success_rate >= 0.90, f"Overall success rate too low: {success_rate:.2%}"

if __name__ == "__main__":
    async def main():
        suites = SyntheticPromptSuites()
        
        # Run all suites
        suite_results = await suites.run_all_suites()
        
        # Generate comprehensive report
        report = suites.generate_comprehensive_report(suite_results)
        
        # Save results
        suites.save_results(suite_results)
        suites.save_report(report)
        
        # Print summary
        print("\n" + "="*50)
        print("SYNTHETIC PROMPT SUITES EXECUTION SUMMARY")
        print("="*50)
        print(f"Total Tests: {report['overall_metrics']['total_tests']}")
        print(f"Successful: {report['overall_metrics']['successful_tests']}")
        print(f"Failed: {report['overall_metrics']['failed_tests']}")
        print(f"Success Rate: {report['overall_metrics']['success_rate']:.2%}")
        print(f"Average Response Time: {report['overall_metrics']['avg_response_time']:.2f}s")
        print(f"Average Quality Score: {report['overall_metrics']['avg_quality_score']:.2f}")
        print(f"SLA Compliance Rate: {report['overall_metrics']['sla_compliance_rate']:.2%}")
        print("="*50)
        
        # Print Guided Prompt metrics
        if report['guided_prompt_metrics']:
            print("\nGUIDED PROMPT METRICS:")
            for suite_name, metrics in report['guided_prompt_metrics'].items():
                print(f"  {suite_name}: {metrics['trigger_rate']:.2%} trigger rate, {metrics['sla_compliance_rate']:.2%} SLA compliance")
        
        # Print recommendations
        if report['recommendations']:
            print("\nRECOMMENDATIONS:")
            for recommendation in report['recommendations']:
                print(f"  - {recommendation}")
    
    asyncio.run(main())
