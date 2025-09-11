# Test Makefile - SarvanOM v2
# Comprehensive test execution and validation

.PHONY: help install test test-matrix test-sla test-prompts test-guided-prompt test-all test-unit test-integration test-coverage test-performance test-security clean

# Default target
help:
	@echo "SarvanOM v2 Test Suite"
	@echo "======================"
	@echo ""
	@echo "Available targets:"
	@echo "  install              Install test dependencies"
	@echo "  test                 Run all tests"
	@echo "  test-matrix          Run test matrix (LLM providers, databases, combinations)"
	@echo "  test-sla             Run SLA validation tests"
	@echo "  test-prompts         Run synthetic prompt suites"
	@echo "  test-guided-prompt   Run Guided Prompt Confirmation tests"
	@echo "  test-all             Run comprehensive test suite"
	@echo "  test-unit            Run unit tests only"
	@echo "  test-integration     Run integration tests only"
	@echo "  test-coverage        Run tests with coverage reporting"
	@echo "  test-performance     Run performance tests"
	@echo "  test-security        Run security tests"
	@echo "  clean                Clean test artifacts"
	@echo ""
	@echo "Environment variables:"
	@echo "  TEST_BASE_URL        Base URL for API testing (default: http://localhost:8004)"
	@echo "  TEST_TIMEOUT         Test timeout in seconds (default: 30)"
	@echo "  SLA_DURATION         SLA validation duration in minutes (default: 5)"
	@echo "  PARALLEL_WORKERS     Number of parallel test workers (default: 4)"

# Install test dependencies
install:
	pip install -r requirements.txt

# Run all tests
test: test-unit test-integration

# Run test matrix
test-matrix:
	@echo "Running Test Matrix..."
	python -m pytest test_matrix_runner.py -v --tb=short

# Run SLA validation tests
test-sla:
	@echo "Running SLA Validation Tests..."
	python -m pytest sla_validator.py -v --tb=short

# Run synthetic prompt suites
test-prompts:
	@echo "Running Synthetic Prompt Suites..."
	python -m pytest synthetic_prompt_suites.py -v --tb=short

# Run Guided Prompt tests
test-guided-prompt:
	@echo "Running Guided Prompt Confirmation Tests..."
	python -m pytest -m guided_prompt -v --tb=short

# Run comprehensive test suite
test-all:
	@echo "Running Comprehensive Test Suite..."
	python comprehensive_test_runner.py --all --sla-duration $(or $(SLA_DURATION),5)

# Run unit tests only
test-unit:
	@echo "Running Unit Tests..."
	python -m pytest -m unit -v --tb=short

# Run integration tests only
test-integration:
	@echo "Running Integration Tests..."
	python -m pytest -m integration -v --tb=short

# Run tests with coverage
test-coverage:
	@echo "Running Tests with Coverage..."
	python -m pytest --cov=. --cov-report=html --cov-report=term-missing -v

# Run performance tests
test-performance:
	@echo "Running Performance Tests..."
	python -m pytest -m slow -v --tb=short

# Run security tests
test-security:
	@echo "Running Security Tests..."
	bandit -r . -f json -o security_report.json
	safety check --json --output security_deps.json

# Run specific test categories
test-matrix-only:
	@echo "Running Test Matrix Only..."
	python comprehensive_test_runner.py --test-matrix

test-sla-only:
	@echo "Running SLA Validation Only..."
	python comprehensive_test_runner.py --sla-validation --sla-duration $(or $(SLA_DURATION),5)

test-prompts-only:
	@echo "Running Prompt Suites Only..."
	python comprehensive_test_runner.py --prompt-suites

test-guided-prompt-only:
	@echo "Running Guided Prompt Tests Only..."
	python comprehensive_test_runner.py --guided-prompt

# Run tests with specific markers
test-quick:
	@echo "Running Quick Tests..."
	python -m pytest -m "not slow" -v --tb=short

test-api-required:
	@echo "Running API-Required Tests..."
	python -m pytest -m requires_api -v --tb=short

# Parallel test execution
test-parallel:
	@echo "Running Tests in Parallel..."
	python -m pytest -n $(or $(PARALLEL_WORKERS),4) -v --tb=short

# Generate test reports
test-reports:
	@echo "Generating Test Reports..."
	python -m pytest --html=test_report.html --self-contained-html -v
	python -m pytest --junitxml=test_results.xml -v

# Run specific test files
test-matrix-file:
	@echo "Running Test Matrix File..."
	python test_matrix_runner.py

test-sla-file:
	@echo "Running SLA Validator File..."
	python sla_validator.py

test-prompts-file:
	@echo "Running Prompt Suites File..."
	python synthetic_prompt_suites.py

# Continuous testing (watch mode)
test-watch:
	@echo "Running Tests in Watch Mode..."
	python -m pytest-watch -- -v

# Test with specific base URL
test-local:
	@echo "Running Tests against Local API..."
	TEST_BASE_URL=http://localhost:8004 python -m pytest -v

test-staging:
	@echo "Running Tests against Staging API..."
	TEST_BASE_URL=https://staging-api.sarvanom.com python -m pytest -v

test-production:
	@echo "Running Tests against Production API..."
	TEST_BASE_URL=https://api.sarvanom.com python -m pytest -v

# Load testing
test-load:
	@echo "Running Load Tests..."
	locust -f load_tests.py --host=$(or $(TEST_BASE_URL),http://localhost:8004)

# Benchmark tests
test-benchmark:
	@echo "Running Benchmark Tests..."
	python -m pytest -m benchmark -v --benchmark-only

# Memory profiling
test-memory:
	@echo "Running Memory Profiling Tests..."
	python -m pytest -m memory -v --profile

# Test data generation
generate-test-data:
	@echo "Generating Test Data..."
	python -c "from synthetic_prompt_suites import SyntheticPromptSuites; import json; suites = SyntheticPromptSuites(); print(json.dumps(suites.suites, indent=2))" > test_data.json

# Validate test configuration
validate-config:
	@echo "Validating Test Configuration..."
	python -c "import pytest; print('Pytest version:', pytest.__version__)"
	python -c "import aiohttp; print('aiohttp version:', aiohttp.__version__)"
	python -c "import asyncio; print('asyncio available')"

# Clean test artifacts
clean:
	@echo "Cleaning Test Artifacts..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf test_results/
	rm -rf *.json
	rm -rf *.xml
	rm -rf *.html
	rm -rf security_report.json
	rm -rf security_deps.json
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Setup test environment
setup:
	@echo "Setting up Test Environment..."
	python -m venv test_env
	. test_env/bin/activate && pip install -r requirements.txt

# Docker-based testing
test-docker:
	@echo "Running Tests in Docker..."
	docker build -t sarvanom-tests -f Dockerfile.test .
	docker run --rm sarvanom-tests

# CI/CD integration
test-ci:
	@echo "Running CI Tests..."
	python -m pytest --cov=. --cov-report=xml --junitxml=test_results.xml -v

# Development testing
test-dev:
	@echo "Running Development Tests..."
	python -m pytest -m "not slow" --tb=short -v

# Production readiness tests
test-prod-ready:
	@echo "Running Production Readiness Tests..."
	python -m pytest -m "integration and not slow" -v
	python comprehensive_test_runner.py --all --sla-duration 10

# Help for specific test types
help-matrix:
	@echo "Test Matrix Help:"
	@echo "  test-matrix          Run full test matrix"
	@echo "  test-matrix-only     Run test matrix via comprehensive runner"
	@echo "  test-matrix-file     Run test matrix directly"

help-sla:
	@echo "SLA Validation Help:"
	@echo "  test-sla             Run SLA validation tests"
	@echo "  test-sla-only        Run SLA validation via comprehensive runner"
	@echo "  test-sla-file        Run SLA validator directly"
	@echo "  SLA_DURATION=10      Set SLA validation duration (default: 5 minutes)"

help-prompts:
	@echo "Prompt Suites Help:"
	@echo "  test-prompts         Run synthetic prompt suites"
	@echo "  test-prompts-only    Run prompt suites via comprehensive runner"
	@echo "  test-prompts-file    Run prompt suites directly"

help-guided-prompt:
	@echo "Guided Prompt Help:"
	@echo "  test-guided-prompt   Run Guided Prompt tests"
	@echo "  test-guided-prompt-only  Run Guided Prompt via comprehensive runner"

# Environment-specific testing
test-env-dev:
	@echo "Running Development Environment Tests..."
	TEST_BASE_URL=http://localhost:8004 python -m pytest -m "not slow" -v

test-env-staging:
	@echo "Running Staging Environment Tests..."
	TEST_BASE_URL=https://staging-api.sarvanom.com python -m pytest -v

test-env-prod:
	@echo "Running Production Environment Tests..."
	TEST_BASE_URL=https://api.sarvanom.com python -m pytest -m "not slow" -v

# Test result analysis
analyze-results:
	@echo "Analyzing Test Results..."
	python -c "import json; import glob; files = glob.glob('*_report.json'); [print(f'Report: {f}') for f in files]"

# Quick health check
health-check:
	@echo "Running Health Check..."
	python -c "import aiohttp, asyncio; async def check(): async with aiohttp.ClientSession() as session: async with session.get('$(or $(TEST_BASE_URL),http://localhost:8004)/health') as r: print(f'Health: {r.status}'); asyncio.run(check())"
