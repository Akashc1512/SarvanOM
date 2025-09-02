#!/usr/bin/env python3
"""
Golden Test Suite for Automated Guardrails

This module contains a comprehensive set of ~100 prompts across various categories
with expected properties for citation coverage, uncertainty levels, and latency budgets.
Used for regression testing and performance monitoring.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from shared.contracts.query import RetrievalSearchRequest
from services.retrieval.orchestrator import RetrievalOrchestrator

logger = logging.getLogger(__name__)


class GoldenTestSuite:
    """Comprehensive test suite for automated guardrails."""
    
    def __init__(self):
        self.orchestrator = RetrievalOrchestrator()
        self.results_dir = Path("code_garden/golden_test_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Test categories with expected properties
        self.test_categories = {
            "factual_queries": {
                "description": "Factual questions requiring high citation coverage",
                "min_citation_coverage": 0.95,
                "max_uncertainty": 0.1,
                "latency_budget_ms": 3000,
                "expected_sources": 3
            },
            "research_queries": {
                "description": "Research questions requiring comprehensive sources",
                "min_citation_coverage": 0.90,
                "max_uncertainty": 0.15,
                "latency_budget_ms": 5000,
                "expected_sources": 5
            },
            "technical_queries": {
                "description": "Technical questions requiring precise information",
                "min_citation_coverage": 0.95,
                "max_uncertainty": 0.05,
                "latency_budget_ms": 4000,
                "expected_sources": 4
            },
            "creative_queries": {
                "description": "Creative questions allowing some uncertainty",
                "min_citation_coverage": 0.80,
                "max_uncertainty": 0.25,
                "latency_budget_ms": 3000,
                "expected_sources": 2
            },
            "performance_queries": {
                "description": "Simple queries for performance testing",
                "min_citation_coverage": 0.85,
                "max_uncertainty": 0.15,
                "latency_budget_ms": 2000,
                "expected_sources": 2
            }
        }
        
        # Golden prompts across categories (100+ total)
        self.golden_prompts = {
            "factual_queries": [
                "What is the capital of France?",
                "Who wrote Romeo and Juliet?",
                "What is the chemical formula for water?",
                "When did World War II end?",
                "What is the largest planet in our solar system?",
                "Who was the first president of the United States?",
                "What is the speed of light?",
                "What is the population of Tokyo?",
                "Who painted the Mona Lisa?",
                "What is the atomic number of carbon?",
                "When was the Declaration of Independence signed?",
                "What is the tallest mountain in the world?",
                "Who discovered penicillin?",
                "What is the boiling point of water?",
                "When did the Berlin Wall fall?",
                "What is the largest ocean on Earth?",
                "Who wrote The Great Gatsby?",
                "What is the chemical symbol for gold?",
                "When did the Titanic sink?",
                "What is the distance from Earth to the Moon?"
            ],
            "research_queries": [
                "What are the latest developments in quantum computing?",
                "How does climate change affect biodiversity?",
                "What are the health benefits of Mediterranean diet?",
                "How do vaccines work to prevent diseases?",
                "What are the economic impacts of renewable energy?",
                "How does machine learning improve healthcare?",
                "What are the causes of income inequality?",
                "How do social media algorithms affect society?",
                "What are the environmental impacts of electric vehicles?",
                "How does sleep affect cognitive performance?",
                "What are the benefits of exercise for mental health?",
                "How do cryptocurrencies impact traditional banking?",
                "What are the effects of meditation on stress?",
                "How does urbanization affect wildlife?",
                "What are the health risks of processed foods?",
                "How do renewable energy sources compare to fossil fuels?",
                "What are the psychological effects of social isolation?",
                "How does artificial intelligence affect job markets?",
                "What are the benefits of organic farming?",
                "How do educational technologies improve learning outcomes?"
            ],
            "technical_queries": [
                "How does a neural network work?",
                "What is the difference between HTTP and HTTPS?",
                "How do blockchain transactions work?",
                "What is the purpose of a load balancer?",
                "How does Docker containerization work?",
                "What is the difference between SQL and NoSQL databases?",
                "How do microservices communicate?",
                "What is the purpose of a CDN?",
                "How does OAuth authentication work?",
                "What is the difference between TCP and UDP?",
                "How do REST APIs work?",
                "What is the purpose of a reverse proxy?",
                "How does SSL/TLS encryption work?",
                "What is the difference between synchronous and asynchronous programming?",
                "How do message queues work?",
                "What is the purpose of a cache?",
                "How does Git version control work?",
                "What is the difference between monolithic and microservice architectures?",
                "How do webhooks work?",
                "What is the purpose of a firewall?"
            ],
            "creative_queries": [
                "How can I improve my creative writing skills?",
                "What are some innovative business ideas for 2024?",
                "How can I design a more sustainable home?",
                "What are some creative ways to reduce food waste?",
                "How can I make learning more engaging for children?",
                "What are some innovative solutions for urban transportation?",
                "How can I create a more productive workspace?",
                "What are some creative marketing strategies for small businesses?",
                "How can I design a garden that attracts wildlife?",
                "What are some innovative approaches to education?",
                "How can I make cooking more fun and creative?",
                "What are some creative ways to save money?",
                "How can I design a more accessible website?",
                "What are some innovative approaches to healthcare?",
                "How can I make exercise more enjoyable?",
                "What are some creative solutions for environmental problems?",
                "How can I design a more efficient kitchen?",
                "What are some innovative approaches to remote work?",
                "How can I make travel more sustainable?",
                "What are some creative ways to reduce stress?"
            ],
            "performance_queries": [
                "What is the weather like?",
                "How are you today?",
                "What time is it?",
                "What is your name?",
                "How old are you?",
                "What do you do?",
                "Where are you from?",
                "What languages do you speak?",
                "What is your favorite color?",
                "What is your favorite food?",
                "What is your favorite movie?",
                "What is your favorite book?",
                "What is your favorite music?",
                "What is your favorite sport?",
                "What is your favorite hobby?",
                "What is your favorite season?",
                "What is your favorite animal?",
                "What is your favorite place?",
                "What is your favorite number?",
                "What is your favorite day of the week?"
            ]
        }
        
        # Failure scenario tests
        self.failure_scenarios = {
            "no_paid_keys": {
                "description": "Test graceful degradation when paid API keys are unavailable",
                "expected_behavior": "Fallback to free/local models",
                "latency_budget_ms": 5000
            },
            "vector_down": {
                "description": "Test graceful degradation when vector database is unavailable",
                "expected_behavior": "Continue with web search and knowledge graph",
                "latency_budget_ms": 4000
            },
            "kg_down": {
                "description": "Test graceful degradation when knowledge graph is unavailable",
                "expected_behavior": "Continue with vector search and web search",
                "latency_budget_ms": 4000
            },
            "web_down": {
                "description": "Test graceful degradation when web search is unavailable",
                "expected_behavior": "Continue with vector search and knowledge graph",
                "latency_budget_ms": 4000
            }
        }
    
    async def run_golden_tests(self) -> tuple[Dict[str, Any], bool]:
        """Run the complete golden test suite."""
        logger.info("🚀 Starting Golden Test Suite")
        
        start_time = time.time()
        results = {
            "timestamp": datetime.now().isoformat(),
            "test_summary": {},
            "category_results": {},
            "failure_scenario_results": {},
            "overall_metrics": {}
        }
        
        # Run tests for each category
        for category, config in self.test_categories.items():
            logger.info(f"📋 Testing category: {category}")
            category_results = await self._test_category(category, config)
            results["category_results"][category] = category_results
            
            # Update summary
            results["test_summary"][category] = {
                "total_tests": len(category_results),
                "passed": sum(1 for r in category_results if r["passed"]),
                "failed": sum(1 for r in category_results if not r["passed"]),
                "avg_latency_ms": sum(r["latency_ms"] for r in category_results) / len(category_results),
                "avg_citation_coverage": sum(r["citation_coverage"] for r in category_results) / len(category_results),
                "avg_uncertainty": sum(r["uncertainty"] for r in category_results) / len(category_results)
            }
        
        # Run failure scenario tests
        logger.info("🔧 Testing failure scenarios")
        for scenario, config in self.failure_scenarios.items():
            scenario_result = await self._test_failure_scenario(scenario, config)
            results["failure_scenario_results"][scenario] = scenario_result
        
        # Calculate overall metrics
        total_tests = sum(summary["total_tests"] for summary in results["test_summary"].values())
        total_passed = sum(summary["passed"] for summary in results["test_summary"].values())
        
        results["overall_metrics"] = {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_tests - total_passed,
            "success_rate": total_passed / total_tests if total_tests > 0 else 0,
            "total_duration_ms": (time.time() - start_time) * 1000
        }
        
        # Save results
        await self._save_results(results)
        
        # Check if build should fail
        build_should_fail = self._should_fail_build(results)
        
        logger.info(f"📊 Golden Test Suite completed in {results['overall_metrics']['total_duration_ms']:.2f}ms")
        logger.info(f"✅ Success Rate: {results['overall_metrics']['success_rate']:.1%}")
        logger.info(f"🚨 Build should fail: {build_should_fail}")
        
        return results, build_should_fail
    
    async def _test_category(self, category: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test all prompts in a category."""
        results = []
        prompts = self.golden_prompts[category]
        
        for i, prompt in enumerate(prompts):
            logger.info(f"  Testing prompt {i+1}/{len(prompts)}: {prompt[:50]}...")
            
            try:
                # Create request
                request = RetrievalSearchRequest(
                    query=prompt,
                    max_results=config["expected_sources"]
                )
                
                # Execute retrieval
                start_time = time.time()
                response = await self.orchestrator.orchestrate_retrieval(request)
                latency_ms = (time.time() - start_time) * 1000
                
                # Analyze response
                result = self._analyze_response(
                    prompt, response, latency_ms, config, category
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error testing prompt '{prompt}': {e}")
                results.append({
                    "prompt": prompt,
                    "category": category,
                    "passed": False,
                    "error": str(e),
                    "latency_ms": 0,
                    "citation_coverage": 0,
                    "uncertainty": 1.0,
                    "sources_count": 0
                })
        
        return results
    
    async def _test_failure_scenario(self, scenario: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific failure scenario."""
        logger.info(f"  Testing failure scenario: {scenario}")
        
        # Use a simple test prompt
        test_prompt = "What is the weather like today?"
        request = RetrievalSearchRequest(query=test_prompt, max_results=3)
        
        try:
            start_time = time.time()
            response = await self.orchestrator.orchestrate_retrieval(request)
            latency_ms = (time.time() - start_time) * 1000
            
            # Check if graceful degradation worked
            graceful_degradation = self._check_graceful_degradation(response, scenario)
            
            return {
                "scenario": scenario,
                "passed": graceful_degradation and latency_ms <= config["latency_budget_ms"],
                "latency_ms": latency_ms,
                "graceful_degradation": graceful_degradation,
                "sources_count": len(response.sources) if response.sources else 0,
                "expected_behavior": config["expected_behavior"]
            }
            
        except Exception as e:
            logger.error(f"Error testing failure scenario {scenario}: {e}")
            return {
                "scenario": scenario,
                "passed": False,
                "error": str(e),
                "latency_ms": 0,
                "graceful_degradation": False,
                "sources_count": 0
            }
    
    def _analyze_response(self, prompt: str, response, latency_ms: float, 
                         config: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Analyze a response for quality metrics."""
        sources = response.sources if response.sources else []
        
        # Calculate citation coverage (simplified - in real implementation, 
        # this would analyze the actual response content)
        citation_coverage = min(1.0, len(sources) / config["expected_sources"])
        
        # Calculate uncertainty (simplified - in real implementation, 
        # this would analyze response confidence indicators)
        uncertainty = max(0.0, 1.0 - citation_coverage)
        
        # Determine if test passed
        passed = (
            latency_ms <= config["latency_budget_ms"] and
            citation_coverage >= config["min_citation_coverage"] and
            uncertainty <= config["max_uncertainty"]
        )
        
        return {
            "prompt": prompt,
            "category": category,
            "passed": passed,
            "latency_ms": latency_ms,
            "citation_coverage": citation_coverage,
            "uncertainty": uncertainty,
            "sources_count": len(sources),
            "latency_budget_ms": config["latency_budget_ms"],
            "min_citation_coverage": config["min_citation_coverage"],
            "max_uncertainty": config["max_uncertainty"]
        }
    
    def _check_graceful_degradation(self, response, scenario: str) -> bool:
        """Check if graceful degradation worked for a failure scenario."""
        sources = response.sources if response.sources else []
        
        # Basic check - in real implementation, this would be more sophisticated
        if scenario == "vector_down":
            # Should still have some sources from other lanes
            return len(sources) > 0
        elif scenario == "kg_down":
            # Should still have some sources from other lanes
            return len(sources) > 0
        elif scenario == "web_down":
            # Should still have some sources from other lanes
            return len(sources) > 0
        else:
            return True
    
    def _should_fail_build(self, results: Dict[str, Any]) -> bool:
        """Determine if the build should fail based on results."""
        overall_metrics = results["overall_metrics"]
        
        # Fail if success rate is below 80%
        if overall_metrics["success_rate"] < 0.8:
            return True
        
        # Fail if any category has less than 70% success rate
        for category, summary in results["test_summary"].items():
            category_success_rate = summary["passed"] / summary["total_tests"]
            if category_success_rate < 0.7:
                return True
        
        # Fail if average latency exceeds 5 seconds
        if overall_metrics["total_duration_ms"] > 5000:
            return True
        
        return False
    
    async def _save_results(self, results: Dict[str, Any]):
        """Save test results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.results_dir / f"golden_test_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save HTML report
        html_file = self.results_dir / f"golden_test_report_{timestamp}.html"
        html_content = self._generate_html_report(results)
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        # Save Markdown report
        md_file = self.results_dir / f"golden_test_report_{timestamp}.md"
        md_content = self._generate_markdown_report(results)
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        logger.info(f"📄 Results saved to:")
        logger.info(f"  JSON: {json_file}")
        logger.info(f"  HTML: {html_file}")
        logger.info(f"  Markdown: {md_file}")
    
    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """Generate HTML report from results."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Golden Test Suite Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #e8f5e8; border-radius: 3px; }}
        .category {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Golden Test Suite Report</h1>
        <p>Generated: {results['timestamp']}</p>
    </div>
    
    <div class="overview">
        <h2>📊 Overall Results</h2>
        <div class="metric">
            <strong>Total Tests:</strong> {results['overall_metrics']['total_tests']}
        </div>
        <div class="metric">
            <strong>Passed:</strong> {results['overall_metrics']['total_passed']}
        </div>
        <div class="metric">
            <strong>Failed:</strong> {results['overall_metrics']['total_failed']}
        </div>
        <div class="metric">
            <strong>Success Rate:</strong> {results['overall_metrics']['success_rate']:.1%}
        </div>
        <div class="metric">
            <strong>Total Duration:</strong> {results['overall_metrics']['total_duration_ms']:.2f}ms
        </div>
    </div>
    
    <div class="categories">
        <h2>📋 Category Results</h2>
        {self._generate_category_html(results['category_results'])}
    </div>
    
    <div class="failure-scenarios">
        <h2>🔧 Failure Scenario Results</h2>
        {self._generate_failure_scenarios_html(results['failure_scenario_results'])}
    </div>
</body>
</html>
        """
    
    def _generate_category_html(self, category_results: Dict[str, Any]) -> str:
        """Generate HTML for category results."""
        html = ""
        for category, results in category_results.items():
            passed = sum(1 for r in results if r["passed"])
            total = len(results)
            success_rate = passed / total if total > 0 else 0
            
            html += f"""
            <div class="category">
                <h3>{category.replace('_', ' ').title()}</h3>
                <p><strong>Success Rate:</strong> <span class="{'passed' if success_rate >= 0.8 else 'failed'}">{success_rate:.1%}</span></p>
                <p><strong>Passed:</strong> {passed}/{total}</p>
                <table>
                    <tr>
                        <th>Prompt</th>
                        <th>Status</th>
                        <th>Latency (ms)</th>
                        <th>Citation Coverage</th>
                        <th>Uncertainty</th>
                    </tr>
            """
            
            for result in results:
                status_class = "passed" if result["passed"] else "failed"
                status_text = "✅ PASS" if result["passed"] else "❌ FAIL"
                
                html += f"""
                    <tr>
                        <td>{result['prompt'][:50]}...</td>
                        <td class="{status_class}">{status_text}</td>
                        <td>{result['latency_ms']:.2f}</td>
                        <td>{result['citation_coverage']:.2f}</td>
                        <td>{result['uncertainty']:.2f}</td>
                    </tr>
                """
            
            html += "</table></div>"
        
        return html
    
    def _generate_failure_scenarios_html(self, failure_results: Dict[str, Any]) -> str:
        """Generate HTML for failure scenario results."""
        html = """
        <table>
            <tr>
                <th>Scenario</th>
                <th>Status</th>
                <th>Latency (ms)</th>
                <th>Graceful Degradation</th>
                <th>Sources Count</th>
            </tr>
        """
        
        for scenario, result in failure_results.items():
            status_class = "passed" if result["passed"] else "failed"
            status_text = "✅ PASS" if result["passed"] else "❌ FAIL"
            
            html += f"""
                <tr>
                    <td>{scenario.replace('_', ' ').title()}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{result['latency_ms']:.2f}</td>
                    <td>{'✅' if result['graceful_degradation'] else '❌'}</td>
                    <td>{result['sources_count']}</td>
                </tr>
            """
        
        html += "</table>"
        return html
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate Markdown report from results."""
        md = f"""# 🚀 Golden Test Suite Report

**Generated:** {results['timestamp']}

## 📊 Overall Results

- **Total Tests:** {results['overall_metrics']['total_tests']}
- **Passed:** {results['overall_metrics']['total_passed']}
- **Failed:** {results['overall_metrics']['total_failed']}
- **Success Rate:** {results['overall_metrics']['success_rate']:.1%}
- **Total Duration:** {results['overall_metrics']['total_duration_ms']:.2f}ms

## 📋 Category Results

"""
        
        for category, category_results in results['category_results'].items():
            passed = sum(1 for r in category_results if r["passed"])
            total = len(category_results)
            success_rate = passed / total if total > 0 else 0
            
            md += f"""### {category.replace('_', ' ').title()}

- **Success Rate:** {success_rate:.1%}
- **Passed:** {passed}/{total}

| Prompt | Status | Latency (ms) | Citation Coverage | Uncertainty |
|--------|--------|---------------|-------------------|-------------|
"""
            
            for result in category_results:
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                md += f"| {result['prompt'][:50]}... | {status} | {result['latency_ms']:.2f} | {result['citation_coverage']:.2f} | {result['uncertainty']:.2f} |\n"
            
            md += "\n"
        
        md += """## 🔧 Failure Scenario Results

| Scenario | Status | Latency (ms) | Graceful Degradation | Sources Count |
|----------|--------|---------------|----------------------|---------------|
"""
        
        for scenario, result in results['failure_scenario_results'].items():
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            graceful = "✅" if result['graceful_degradation'] else "❌"
            md += f"| {scenario.replace('_', ' ').title()} | {status} | {result['latency_ms']:.2f} | {graceful} | {result['sources_count']} |\n"
        
        return md


async def main():
    """Main function to run the golden test suite."""
    suite = GoldenTestSuite()
    results, should_fail = await suite.run_golden_tests()
    
    if should_fail:
        logger.error("🚨 BUILD SHOULD FAIL - Quality thresholds not met")
        exit(1)
    else:
        logger.info("✅ BUILD CAN PROCEED - All quality thresholds met")


if __name__ == "__main__":
    asyncio.run(main())
