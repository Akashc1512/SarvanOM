"""
User Acceptance Testing (UAT) Framework

This module provides comprehensive user acceptance testing capabilities
for the SarvanOM platform, including end-to-end workflows, business
scenario testing, and user experience validation.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class UATScenario:
    """User Acceptance Test scenario"""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    expected_results: Dict[str, Any]
    priority: str = "medium"  # high, medium, low
    category: str = "functional"  # functional, performance, security, usability

@dataclass
class UATResult:
    """Result of a UAT scenario execution"""
    scenario_name: str
    passed: bool
    execution_time_seconds: float
    actual_results: Dict[str, Any]
    errors: List[str]
    timestamp: datetime

class UATFramework:
    """User Acceptance Testing framework"""
    
    def __init__(self):
        self.results: List[UATResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.scenarios: List[UATScenario] = []
        
        # Initialize test scenarios
        self._initialize_scenarios()
    
    def _initialize_scenarios(self):
        """Initialize UAT scenarios"""
        
        # Scenario 1: Health Check Validation
        self.scenarios.append(UATScenario(
            name="Health Check Validation",
            description="Verify all services are healthy and responding",
            priority="high",
            category="functional",
            steps=[
                {"action": "get", "url": "http://localhost:8000/health", "expected_status": 200},
                {"action": "get", "url": "http://localhost:8004/health", "expected_status": 200},
                {"action": "get", "url": "http://localhost:8005/health", "expected_status": 200},
                {"action": "get", "url": "http://localhost:8012/auth/health", "expected_status": 200},
                {"action": "get", "url": "http://localhost:8013/health", "expected_status": 200}
            ],
            expected_results={
                "all_services_healthy": True,
                "response_times_under_1s": True,
                "consistent_status_format": True
            }
        ))
        
        # Scenario 2: News Feed Processing
        self.scenarios.append(UATScenario(
            name="News Feed Processing",
            description="Test end-to-end news feed processing workflow",
            priority="high",
            category="functional",
            steps=[
                {"action": "post", "url": "http://localhost:8005/fetch", 
                 "payload": {
                     "query": "artificial intelligence news",
                     "feed_type": "news",
                     "user_id": "uat_user_001",
                     "session_id": "uat_session_001",
                     "trace_id": "uat_trace_001",
                     "constraints": {"limit": 5}
                 }, "expected_status": 200}
            ],
            expected_results={
                "successful_response": True,
                "contains_news_data": True,
                "response_time_under_10s": True,
                "proper_data_structure": True
            }
        ))
        
        # Scenario 3: Model Registry Operations
        self.scenarios.append(UATScenario(
            name="Model Registry Operations",
            description="Test model and provider registry functionality",
            priority="high",
            category="functional",
            steps=[
                {"action": "get", "url": "http://localhost:8000/models", "expected_status": 200},
                {"action": "get", "url": "http://localhost:8000/providers", "expected_status": 200}
            ],
            expected_results={
                "models_available": True,
                "providers_available": True,
                "valid_model_data": True,
                "valid_provider_data": True
            }
        ))
        
        # Scenario 4: Configuration Management
        self.scenarios.append(UATScenario(
            name="Configuration Management",
            description="Test service configuration endpoints",
            priority="medium",
            category="functional",
            steps=[
                {"action": "get", "url": "http://localhost:8004/config", "expected_status": 200},
                {"action": "get", "url": "http://localhost:8005/config", "expected_status": 200}
            ],
            expected_results={
                "config_endpoints_accessible": True,
                "valid_configuration_data": True,
                "consistent_config_format": True
            }
        ))
        
        # Scenario 5: Authentication Service
        self.scenarios.append(UATScenario(
            name="Authentication Service",
            description="Test authentication service endpoints",
            priority="high",
            category="functional",
            steps=[
                {"action": "get", "url": "http://localhost:8012/auth/", "expected_status": 200},
                {"action": "get", "url": "http://localhost:8012/auth/health", "expected_status": 200}
            ],
            expected_results={
                "auth_service_accessible": True,
                "health_endpoint_working": True,
                "proper_auth_structure": True
            }
        ))
        
        # Scenario 6: Multi-Service Integration
        self.scenarios.append(UATScenario(
            name="Multi-Service Integration",
            description="Test integration between multiple services",
            priority="high",
            category="functional",
            steps=[
                {"action": "get", "url": "http://localhost:8000/health", "expected_status": 200},
                {"action": "get", "url": "http://localhost:8005/health", "expected_status": 200},
                {"action": "post", "url": "http://localhost:8005/fetch", 
                 "payload": {
                     "query": "integration test",
                     "feed_type": "news",
                     "user_id": "integration_user",
                     "session_id": "integration_session",
                     "trace_id": "integration_trace",
                     "constraints": {"limit": 3}
                 }, "expected_status": 200}
            ],
            expected_results={
                "services_communicating": True,
                "end_to_end_workflow": True,
                "data_flow_functional": True
            }
        ))
        
        # Scenario 7: Performance Validation
        self.scenarios.append(UATScenario(
            name="Performance Validation",
            description="Validate system performance meets requirements",
            priority="medium",
            category="performance",
            steps=[
                {"action": "get", "url": "http://localhost:8000/health", "expected_status": 200, "max_response_time": 1.0},
                {"action": "get", "url": "http://localhost:8005/health", "expected_status": 200, "max_response_time": 1.0},
                {"action": "get", "url": "http://localhost:8004/health", "expected_status": 200, "max_response_time": 1.0}
            ],
            expected_results={
                "response_times_acceptable": True,
                "system_responsive": True,
                "no_timeouts": True
            }
        ))
        
        # Scenario 8: Error Handling
        self.scenarios.append(UATScenario(
            name="Error Handling",
            description="Test system error handling and graceful degradation",
            priority="medium",
            category="functional",
            steps=[
                {"action": "get", "url": "http://localhost:8000/nonexistent", "expected_status": 404},
                {"action": "get", "url": "http://localhost:8005/invalid", "expected_status": 404}
            ],
            expected_results={
                "proper_error_codes": True,
                "graceful_error_handling": True,
                "error_messages_helpful": True
            }
        ))
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def execute_scenario(self, scenario: UATScenario) -> UATResult:
        """Execute a UAT scenario"""
        logger.info(f"Executing UAT scenario: {scenario.name}")
        
        start_time = time.time()
        actual_results = {}
        errors = []
        
        try:
            for step in scenario.steps:
                step_result = await self._execute_step(step)
                actual_results[f"step_{scenario.steps.index(step)}"] = step_result
                
                if not step_result.get("success", False):
                    errors.append(f"Step failed: {step_result.get('error', 'Unknown error')}")
            
            # Evaluate expected results
            passed = self._evaluate_results(scenario.expected_results, actual_results, errors)
            
        except Exception as e:
            errors.append(f"Scenario execution error: {str(e)}")
            passed = False
        
        execution_time = time.time() - start_time
        
        result = UATResult(
            scenario_name=scenario.name,
            passed=passed,
            execution_time_seconds=execution_time,
            actual_results=actual_results,
            errors=errors,
            timestamp=datetime.now()
        )
        
        self.results.append(result)
        
        status = "PASSED" if passed else "FAILED"
        logger.info(f"UAT scenario '{scenario.name}' {status} in {execution_time:.2f}s")
        
        return result
    
    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single test step"""
        try:
            action = step["action"]
            url = step["url"]
            expected_status = step.get("expected_status", 200)
            max_response_time = step.get("max_response_time", 30.0)
            
            start_time = time.time()
            
            if action == "get":
                async with self.session.get(url) as response:
                    response_text = await response.text()
                    response_time = time.time() - start_time
                    
                    return {
                        "success": response.status == expected_status and response_time <= max_response_time,
                        "status_code": response.status,
                        "response_time": response_time,
                        "response_size": len(response_text),
                        "expected_status": expected_status,
                        "max_response_time": max_response_time,
                        "error": None if response.status == expected_status else f"Expected {expected_status}, got {response.status}"
                    }
            
            elif action == "post":
                payload = step.get("payload", {})
                headers = {"Content-Type": "application/json"}
                
                async with self.session.post(url, json=payload, headers=headers) as response:
                    response_text = await response.text()
                    response_time = time.time() - start_time
                    
                    return {
                        "success": response.status == expected_status and response_time <= max_response_time,
                        "status_code": response.status,
                        "response_time": response_time,
                        "response_size": len(response_text),
                        "expected_status": expected_status,
                        "max_response_time": max_response_time,
                        "error": None if response.status == expected_status else f"Expected {expected_status}, got {response.status}"
                    }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _evaluate_results(self, expected: Dict[str, Any], actual: Dict[str, Any], errors: List[str]) -> bool:
        """Evaluate if actual results meet expected results"""
        if errors:
            return False
        
        # Check if all steps were successful
        for step_key, step_result in actual.items():
            if not step_result.get("success", False):
                return False
        
        # Additional validation based on expected results
        for key, expected_value in expected.items():
            if key == "all_services_healthy":
                # Check that all health endpoints returned 200
                health_steps = [step for step in actual.values() if step.get("status_code") == 200]
                if len(health_steps) < 4:  # Expect at least 4 healthy services
                    return False
            
            elif key == "response_times_under_1s":
                # Check that all response times are under 1 second
                for step_result in actual.values():
                    if step_result.get("response_time", 0) > 1.0:
                        return False
            
            elif key == "successful_response":
                # Check that we got a successful response
                if not any(step.get("success", False) for step in actual.values()):
                    return False
            
            elif key == "contains_news_data":
                # Check that feeds response contains expected data structure
                feeds_steps = [step for step in actual.values() if step.get("response_size", 0) > 100]
                if not feeds_steps:
                    return False
        
        return True
    
    async def run_all_scenarios(self) -> List[UATResult]:
        """Run all UAT scenarios"""
        logger.info("Starting User Acceptance Testing...")
        
        async with self:
            for scenario in self.scenarios:
                await self.execute_scenario(scenario)
                await asyncio.sleep(1)  # Small delay between scenarios
        
        return self.results
    
    def generate_uat_report(self) -> str:
        """Generate comprehensive UAT report"""
        if not self.results:
            return "No UAT results available."
        
        total_scenarios = len(self.results)
        passed_scenarios = sum(1 for r in self.results if r.passed)
        failed_scenarios = total_scenarios - passed_scenarios
        pass_rate = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
        
        report = []
        report.append("=" * 80)
        report.append("SARVANOM USER ACCEPTANCE TESTING REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Scenarios: {total_scenarios}")
        report.append(f"Passed: {passed_scenarios} ({pass_rate:.1f}%)")
        report.append(f"Failed: {failed_scenarios}")
        report.append("")
        
        # Group by category
        categories = {}
        for result in self.results:
            # Find scenario by name
            scenario = next((s for s in self.scenarios if s.name == result.scenario_name), None)
            if scenario:
                category = scenario.category
                if category not in categories:
                    categories[category] = []
                categories[category].append((scenario, result))
        
        for category, scenario_results in categories.items():
            report.append(f"CATEGORY: {category.upper()}")
            report.append("-" * 40)
            
            for scenario, result in scenario_results:
                status = "✅ PASS" if result.passed else "❌ FAIL"
                report.append(f"{status} {scenario.name}")
                report.append(f"  Priority: {scenario.priority}")
                report.append(f"  Execution Time: {result.execution_time_seconds:.2f}s")
                
                if not result.passed and result.errors:
                    report.append(f"  Errors:")
                    for error in result.errors:
                        report.append(f"    - {error}")
                
                report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"Overall Pass Rate: {pass_rate:.1f}%")
        
        if failed_scenarios > 0:
            report.append(f"Failed Scenarios:")
            for result in self.results:
                if not result.passed:
                    report.append(f"  - {result.scenario_name}")
        
        return "\n".join(report)
    
    def save_results(self, filename: str = None):
        """Save UAT results to JSON file"""
        if not filename:
            filename = f"uat_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert results to serializable format
        serializable_results = []
        for result in self.results:
            serializable_results.append({
                "scenario_name": result.scenario_name,
                "passed": result.passed,
                "execution_time_seconds": result.execution_time_seconds,
                "actual_results": result.actual_results,
                "errors": result.errors,
                "timestamp": result.timestamp.isoformat()
            })
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"UAT results saved to {filename}")

async def run_user_acceptance_testing():
    """Run comprehensive user acceptance testing"""
    framework = UATFramework()
    
    logger.info("Starting User Acceptance Testing...")
    
    results = await framework.run_all_scenarios()
    
    # Generate and display report
    report = framework.generate_uat_report()
    print(report)
    
    # Save results
    framework.save_results()
    
    # Return summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    
    return {
        "total_scenarios": total,
        "passed_scenarios": passed,
        "failed_scenarios": total - passed,
        "pass_rate": (passed / total * 100) if total > 0 else 0
    }

if __name__ == "__main__":
    asyncio.run(run_user_acceptance_testing())
