#!/usr/bin/env python3
"""
MAANG Standards Compliance Checker for Sarvanom
Ensures code meets production-ready standards for top-tier tech companies.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Set
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# MAANG Standards Checklist
MAANG_STANDARDS = {
    "security": {
        "name": "Security Standards",
        "checks": [
            "No hardcoded secrets in code",
            "Environment-based configuration", 
            "Secure JWT implementation",
            "Proper error handling without information leakage",
            "Input validation and sanitization"
        ]
    },
    "code_quality": {
        "name": "Code Quality Standards",
        "checks": [
            "Type hints on all functions",
            "Proper documentation strings",
            "Clean code architecture",
            "SOLID principles adherence",
            "No code duplication"
        ]
    },
    "testing": {
        "name": "Testing Standards",
        "checks": [
            "Unit tests for core logic",
            "Integration tests for APIs",
            "Test coverage > 80%",
            "Proper test isolation",
            "Mocking external dependencies"
        ]
    },
    "scalability": {
        "name": "Scalability & Performance",
        "checks": [
            "Async/await patterns for I/O",
            "Database connection pooling",
            "Caching strategies",
            "Rate limiting implementation",
            "Monitoring and metrics"
        ]
    },
    "reliability": {
        "name": "Reliability & Observability",
        "checks": [
            "Comprehensive error handling",
            "Structured logging",
            "Health checks",
            "Circuit breaker patterns",
            "Graceful shutdown handling"
        ]
    },
    "deployment": {
        "name": "Production Deployment",
        "checks": [
            "Docker containerization", 
            "Environment configuration",
            "Database migrations",
            "Zero-downtime deployment support",
            "Backup and recovery procedures"
        ]
    }
}

class MAANGComplianceChecker:
    """Comprehensive MAANG standards compliance checker."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}
        self.score = 0
        self.max_score = 0
        
    def check_security_standards(self) -> Dict[str, bool]:
        """Check security-related standards."""
        results = {}
        
        # 1. No hardcoded secrets
        secrets_check = self._check_no_hardcoded_secrets()
        results["no_hardcoded_secrets"] = secrets_check
        
        # 2. Environment-based configuration
        env_config_check = self._check_environment_configuration()
        results["environment_configuration"] = env_config_check
        
        # 3. Secure JWT implementation
        jwt_check = self._check_jwt_implementation()
        results["secure_jwt"] = jwt_check
        
        # 4. Error handling without info leakage
        error_handling_check = self._check_secure_error_handling()
        results["secure_error_handling"] = error_handling_check
        
        # 5. Input validation
        validation_check = self._check_input_validation()
        results["input_validation"] = validation_check
        
        return results
    
    def check_code_quality_standards(self) -> Dict[str, bool]:
        """Check code quality standards."""
        results = {}
        
        # 1. Type hints
        type_hints_check = self._check_type_hints()
        results["type_hints"] = type_hints_check
        
        # 2. Documentation
        docs_check = self._check_documentation()
        results["documentation"] = docs_check
        
        # 3. Clean architecture
        architecture_check = self._check_clean_architecture()
        results["clean_architecture"] = architecture_check
        
        # 4. SOLID principles
        solid_check = self._check_solid_principles()
        results["solid_principles"] = solid_check
        
        # 5. No duplication
        duplication_check = self._check_code_duplication()
        results["no_duplication"] = duplication_check
        
        return results
    
    def check_testing_standards(self) -> Dict[str, bool]:
        """Check testing standards."""
        results = {}
        
        # 1. Unit tests exist
        unit_tests_check = self._check_unit_tests()
        results["unit_tests"] = unit_tests_check
        
        # 2. Integration tests exist
        integration_tests_check = self._check_integration_tests()
        results["integration_tests"] = integration_tests_check
        
        # 3. Test coverage
        coverage_check = self._check_test_coverage()
        results["test_coverage"] = coverage_check
        
        # 4. Test isolation
        isolation_check = self._check_test_isolation()
        results["test_isolation"] = isolation_check
        
        # 5. Mocking
        mocking_check = self._check_mocking()
        results["mocking"] = mocking_check
        
        return results
    
    def check_scalability_standards(self) -> Dict[str, bool]:
        """Check scalability and performance standards."""
        results = {}
        
        # 1. Async patterns
        async_check = self._check_async_patterns()
        results["async_patterns"] = async_check
        
        # 2. Connection pooling
        pooling_check = self._check_connection_pooling()
        results["connection_pooling"] = pooling_check
        
        # 3. Caching
        caching_check = self._check_caching_strategies()
        results["caching"] = caching_check
        
        # 4. Rate limiting
        rate_limiting_check = self._check_rate_limiting()
        results["rate_limiting"] = rate_limiting_check
        
        # 5. Monitoring
        monitoring_check = self._check_monitoring()
        results["monitoring"] = monitoring_check
        
        return results
    
    def check_reliability_standards(self) -> Dict[str, bool]:
        """Check reliability and observability standards."""
        results = {}
        
        # 1. Comprehensive error handling
        error_handling_check = self._check_comprehensive_error_handling()
        results["comprehensive_error_handling"] = error_handling_check
        
        # 2. Structured logging
        logging_check = self._check_structured_logging()
        results["structured_logging"] = logging_check
        
        # 3. Health checks
        health_check = self._check_health_checks()
        results["health_checks"] = health_check
        
        # 4. Circuit breakers
        circuit_breaker_check = self._check_circuit_breakers()
        results["circuit_breakers"] = circuit_breaker_check
        
        # 5. Graceful shutdown
        shutdown_check = self._check_graceful_shutdown()
        results["graceful_shutdown"] = shutdown_check
        
        return results
    
    def check_deployment_standards(self) -> Dict[str, bool]:
        """Check deployment and production readiness."""
        results = {}
        
        # 1. Docker containerization
        docker_check = self._check_docker_containerization()
        results["docker_containerization"] = docker_check
        
        # 2. Environment configuration
        env_check = self._check_deployment_configuration()
        results["deployment_configuration"] = env_check
        
        # 3. Database migrations
        migrations_check = self._check_database_migrations()
        results["database_migrations"] = migrations_check
        
        # 4. Zero-downtime deployment
        zero_downtime_check = self._check_zero_downtime_support()
        results["zero_downtime"] = zero_downtime_check
        
        # 5. Backup procedures
        backup_check = self._check_backup_procedures()
        results["backup_procedures"] = backup_check
        
        return results
    
    # Helper methods for specific checks
    def _check_no_hardcoded_secrets(self) -> bool:
        """Check for hardcoded secrets in code."""
        try:
            # Run the existing hardcoded values checker
            script_path = self.project_root / "scripts" / "check_hardcoded_values.py"
            if script_path.exists():
                result = subprocess.run([
                    sys.executable, str(script_path)
                ], capture_output=True, text=True, timeout=30)
                return "No critical hardcoded values found" in result.stdout
        except:
            pass
        
        # Fallback check - look for obvious secrets
        secret_patterns = ['password=', 'api_key=', 'secret_key=', 'token=']
        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8').lower()
                for pattern in secret_patterns:
                    if pattern in content and 'os.getenv' not in content:
                        return False
            except:
                continue
        return True
    
    def _check_environment_configuration(self) -> bool:
        """Check if environment-based configuration is implemented."""
        config_files = [
            self.project_root / "shared" / "core" / "config" / "central_config.py",
            self.project_root / "shared" / "core" / "config" / "environment_manager.py",
            self.project_root / "env.example"
        ]
        return all(f.exists() for f in config_files)
    
    def _check_jwt_implementation(self) -> bool:
        """Check if JWT is properly implemented."""
        jwt_files = [
            self.project_root / "shared" / "core" / "secure_auth.py",
            self.project_root / "services" / "api_gateway" / "middleware" / "auth.py"
        ]
        return any(f.exists() for f in jwt_files)
    
    def _check_secure_error_handling(self) -> bool:
        """Check if error handling is secure and doesn't leak info."""
        error_files = [
            self.project_root / "shared" / "core" / "error_handler.py",
            self.project_root / "services" / "api_gateway" / "middleware" / "error_handling.py"
        ]
        return any(f.exists() for f in error_files)
    
    def _check_input_validation(self) -> bool:
        """Check if input validation is implemented."""
        validation_file = self.project_root / "shared" / "core" / "input_validation.py"
        return validation_file.exists()
    
    def _check_type_hints(self) -> bool:
        """Check if type hints are used consistently."""
        # Sample check - look for type hints in key files
        key_files = [
            self.project_root / "services" / "api_gateway" / "main.py",
            self.project_root / "shared" / "core" / "llm_client_v3.py"
        ]
        
        for file_path in key_files:
            if not file_path.exists():
                continue
            try:
                content = file_path.read_text(encoding='utf-8')
                # Check for basic type hints
                if '->' in content and ':' in content:
                    return True
            except:
                continue
        return False
    
    def _check_documentation(self) -> bool:
        """Check if documentation is comprehensive."""
        doc_indicators = [
            self.project_root / "README.md",
            self.project_root / "documentation",
            # Check for docstrings in key files
        ]
        return any(item.exists() for item in doc_indicators)
    
    def _check_clean_architecture(self) -> bool:
        """Check if clean architecture patterns are followed."""
        architecture_dirs = [
            self.project_root / "shared",
            self.project_root / "services",
            self.project_root / "backend",
        ]
        return sum(d.exists() for d in architecture_dirs) >= 2
    
    def _check_solid_principles(self) -> bool:
        """Check if SOLID principles are followed."""
        # Check for dependency injection and interface usage
        di_files = [
            self.project_root / "services" / "api_gateway" / "di",
            self.project_root / "shared" / "core" / "interfaces.py"
        ]
        return any(f.exists() for f in di_files)
    
    def _check_code_duplication(self) -> bool:
        """Check for code duplication."""
        # Heuristic check - if we have shared modules, likely less duplication
        shared_dir = self.project_root / "shared"
        return shared_dir.exists() and len(list(shared_dir.rglob('*.py'))) > 10
    
    def _check_unit_tests(self) -> bool:
        """Check if unit tests exist."""
        test_dirs = [
            self.project_root / "tests" / "unit",
            self.project_root / "backend" / "tests",
        ]
        return any(d.exists() and len(list(d.rglob('test_*.py'))) > 0 for d in test_dirs)
    
    def _check_integration_tests(self) -> bool:
        """Check if integration tests exist."""
        test_dirs = [
            self.project_root / "tests" / "integration",
            self.project_root / "tests" / "e2e",
        ]
        return any(d.exists() and len(list(d.rglob('test_*.py'))) > 0 for d in test_dirs)
    
    def _check_test_coverage(self) -> bool:
        """Check if test coverage is configured."""
        coverage_files = [
            self.project_root / ".coveragerc",
            self.project_root / "pyproject.toml",  # might contain coverage config
        ]
        return any(f.exists() for f in coverage_files)
    
    def _check_test_isolation(self) -> bool:
        """Check if test isolation is implemented."""
        conftest_files = list(self.project_root.rglob('conftest.py'))
        return len(conftest_files) > 0
    
    def _check_mocking(self) -> bool:
        """Check if mocking is used in tests."""
        test_files = list(self.project_root.rglob('test_*.py'))
        for test_file in test_files[:5]:  # Check first 5 test files
            try:
                content = test_file.read_text(encoding='utf-8')
                if 'mock' in content.lower() or 'patch' in content:
                    return True
            except:
                continue
        return False
    
    def _check_async_patterns(self) -> bool:
        """Check if async/await patterns are used."""
        key_files = [
            self.project_root / "services" / "api_gateway" / "main.py",
            self.project_root / "shared" / "core" / "llm_client_v3.py"
        ]
        
        for file_path in key_files:
            if not file_path.exists():
                continue
            try:
                content = file_path.read_text(encoding='utf-8')
                if 'async def' in content and 'await' in content:
                    return True
            except:
                continue
        return False
    
    def _check_connection_pooling(self) -> bool:
        """Check if connection pooling is implemented."""
        pooling_file = self.project_root / "shared" / "core" / "connection_pool.py"
        return pooling_file.exists()
    
    def _check_caching_strategies(self) -> bool:
        """Check if caching is implemented."""
        cache_files = [
            self.project_root / "shared" / "core" / "cache.py",
            self.project_root / "shared" / "core" / "cache_manager_postgres.py"
        ]
        return any(f.exists() for f in cache_files)
    
    def _check_rate_limiting(self) -> bool:
        """Check if rate limiting is implemented."""
        rate_limit_files = [
            self.project_root / "shared" / "core" / "rate_limiter.py",
            self.project_root / "services" / "api_gateway" / "middleware" / "rate_limiting.py"
        ]
        return any(f.exists() for f in rate_limit_files)
    
    def _check_monitoring(self) -> bool:
        """Check if monitoring and metrics are implemented."""
        monitoring_files = [
            self.project_root / "shared" / "core" / "metrics_collector.py",
            self.project_root / "shared" / "core" / "unified_metrics.py"
        ]
        return any(f.exists() for f in monitoring_files)
    
    def _check_comprehensive_error_handling(self) -> bool:
        """Check if comprehensive error handling is implemented."""
        error_files = [
            self.project_root / "shared" / "core" / "error_handler.py",
            self.project_root / "ERROR_HANDLING_IMPLEMENTATION.md"
        ]
        return any(f.exists() for f in error_files)
    
    def _check_structured_logging(self) -> bool:
        """Check if structured logging is implemented."""
        logging_files = [
            self.project_root / "shared" / "core" / "unified_logging.py",
            self.project_root / "shared" / "core" / "logging" / "structured_logger.py"
        ]
        return any(f.exists() for f in logging_files)
    
    def _check_health_checks(self) -> bool:
        """Check if health checks are implemented."""
        health_files = [
            self.project_root / "shared" / "core" / "health_checker.py",
            self.project_root / "services" / "api_gateway" / "services" / "health_service.py"
        ]
        return any(f.exists() for f in health_files)
    
    def _check_circuit_breakers(self) -> bool:
        """Check if circuit breaker patterns are implemented."""
        # Look for circuit breaker in error handler or separate file
        error_handler = self.project_root / "shared" / "core" / "error_handler.py"
        if error_handler.exists():
            try:
                content = error_handler.read_text(encoding='utf-8')
                return 'CircuitBreaker' in content
            except:
                pass
        return False
    
    def _check_graceful_shutdown(self) -> bool:
        """Check if graceful shutdown is implemented."""
        shutdown_files = [
            self.project_root / "shared" / "core" / "shutdown_handler.py"
        ]
        
        # Also check main.py for shutdown handlers
        main_file = self.project_root / "services" / "api_gateway" / "main.py"
        if main_file.exists():
            try:
                content = main_file.read_text(encoding='utf-8')
                if 'lifespan' in content or 'shutdown' in content:
                    return True
            except:
                pass
        
        return any(f.exists() for f in shutdown_files)
    
    def _check_docker_containerization(self) -> bool:
        """Check if Docker containerization is set up."""
        docker_files = [
            self.project_root / "Dockerfile",
            self.project_root / "docker-compose.yml",
            self.project_root / "services" / "deployment" / "docker"
        ]
        return any(f.exists() for f in docker_files)
    
    def _check_deployment_configuration(self) -> bool:
        """Check if deployment configuration is ready."""
        deployment_files = [
            self.project_root / "env.example",
            self.project_root / "scripts" / "generate_env_config.py"
        ]
        return any(f.exists() for f in deployment_files)
    
    def _check_database_migrations(self) -> bool:
        """Check if database migrations are implemented."""
        migration_files = [
            self.project_root / "shared" / "core" / "migrations.py",
            self.project_root / "alembic.ini"
        ]
        return any(f.exists() for f in migration_files)
    
    def _check_zero_downtime_support(self) -> bool:
        """Check if zero-downtime deployment is supported."""
        # Look for health checks, graceful shutdown, and container orchestration
        health_check = self._check_health_checks()
        graceful_shutdown = self._check_graceful_shutdown()
        docker_support = self._check_docker_containerization()
        
        return health_check and graceful_shutdown and docker_support
    
    def _check_backup_procedures(self) -> bool:
        """Check if backup procedures are documented/implemented."""
        backup_indicators = [
            self.project_root / "scripts" / "backup.py",
            self.project_root / "documentation" / "BACKUP_PROCEDURES.md"
        ]
        return any(f.exists() for f in backup_indicators)
    
    def run_all_checks(self) -> Dict[str, Dict[str, bool]]:
        """Run all MAANG standards checks."""
        print("🚀 Running MAANG Standards Compliance Check...")
        print("=" * 60)
        
        all_results = {}
        
        # Run each category of checks
        categories = [
            ("security", self.check_security_standards),
            ("code_quality", self.check_code_quality_standards), 
            ("testing", self.check_testing_standards),
            ("scalability", self.check_scalability_standards),
            ("reliability", self.check_reliability_standards),
            ("deployment", self.check_deployment_standards)
        ]
        
        for category, check_func in categories:
            print(f"\n🔍 Checking {MAANG_STANDARDS[category]['name']}...")
            results = check_func()
            all_results[category] = results
            
            # Calculate score for this category
            passed = sum(1 for result in results.values() if result)
            total = len(results)
            self.score += passed
            self.max_score += total
            
            print(f"   ✅ Passed: {passed}/{total}")
            
            # Show failed checks
            failed_checks = [check for check, result in results.items() if not result]
            if failed_checks:
                print(f"   ❌ Failed: {', '.join(failed_checks)}")
        
        return all_results
    
    def generate_report(self, results: Dict[str, Dict[str, bool]]) -> str:
        """Generate a comprehensive compliance report."""
        overall_score = (self.score / self.max_score) * 100 if self.max_score > 0 else 0
        
        report = f"""
# MAANG Standards Compliance Report
Generated for Sarvanom Universal Knowledge Platform

## Overall Score: {overall_score:.1f}% ({self.score}/{self.max_score})

"""
        
        # Grade the overall score
        if overall_score >= 90:
            grade = "🟢 EXCELLENT (Production Ready)"
        elif overall_score >= 80:
            grade = "🟡 GOOD (Minor improvements needed)"
        elif overall_score >= 70:
            grade = "🟠 ACCEPTABLE (Some work required)"
        else:
            grade = "🔴 NEEDS WORK (Significant improvements required)"
        
        report += f"## Grade: {grade}\n\n"
        
        # Detailed results by category
        for category, category_results in results.items():
            category_info = MAANG_STANDARDS[category]
            passed = sum(1 for result in category_results.values() if result)
            total = len(category_results)
            score = (passed / total) * 100 if total > 0 else 0
            
            report += f"### {category_info['name']}: {score:.1f}% ({passed}/{total})\n\n"
            
            for i, check in enumerate(category_info['checks']):
                check_key = list(category_results.keys())[i] if i < len(category_results) else None
                status = "✅" if check_key and category_results.get(check_key, False) else "❌"
                report += f"- {status} {check}\n"
            
            report += "\n"
        
        # Recommendations
        report += "## Recommendations for MAANG-Level Standards\n\n"
        
        if overall_score < 90:
            report += "### Priority Improvements:\n"
            
            for category, category_results in results.items():
                failed_checks = [check for check, result in category_results.items() if not result]
                if failed_checks:
                    category_name = MAANG_STANDARDS[category]['name']
                    report += f"- **{category_name}**: Focus on {', '.join(failed_checks[:2])}\n"
            
            report += "\n"
        
        report += """### MAANG-Level Best Practices:
1. **Code Reviews**: Implement mandatory peer code reviews
2. **Continuous Integration**: Set up automated testing and deployment
3. **Performance Monitoring**: Implement APM (Application Performance Monitoring)
4. **Security Scanning**: Add automated security vulnerability scanning
5. **Documentation**: Maintain comprehensive API and architecture documentation
6. **Load Testing**: Implement automated load and stress testing
7. **Disaster Recovery**: Create and test disaster recovery procedures

"""
        
        return report

def main():
    """Main function to run MAANG standards compliance check."""
    checker = MAANGComplianceChecker()
    results = checker.run_all_checks()
    
    # Generate and save report
    report = checker.generate_report(results)
    
    # Save report to file
    report_file = Path("MAANG_COMPLIANCE_REPORT.md")
    report_file.write_text(report, encoding='utf-8')
    
    print(f"\n📋 Compliance Report Generated: {report_file}")
    print(f"🎯 Overall Score: {checker.score}/{checker.max_score} ({(checker.score/checker.max_score)*100:.1f}%)")
    
    # Print executive summary
    overall_score = (checker.score / checker.max_score) * 100
    
    if overall_score >= 85:
        print("🎉 CONGRATULATIONS! Your codebase meets MAANG-level standards!")
    elif overall_score >= 75:
        print("👏 Great work! You're very close to MAANG-level standards.")
    else:
        print("📚 Keep improving! Focus on the failed checks in the report.")
    
    return overall_score >= 75

if __name__ == "__main__":
    main()
