# SarvanOM v2 Testing Framework

Comprehensive testing framework for SarvanOM v2, including test matrix execution, SLA validation, and synthetic prompt suites.

## Overview

This testing framework provides comprehensive validation of all SarvanOM v2 components:

- **Test Matrix**: Combinatorial testing across LLM providers, databases, and query complexities
- **SLA Validation**: Real-time monitoring and validation of Service Level Agreements
- **Synthetic Prompt Suites**: Comprehensive prompt testing across all complexity levels and scenarios
- **Guided Prompt Confirmation**: Specific validation of the Guided Prompt feature

## Quick Start

### Prerequisites

- Python 3.11+
- SarvanOM v2 backend services running
- Test dependencies installed

### Installation

```bash
# Install test dependencies
make install

# Or manually
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test components
make test-matrix      # Test matrix only
make test-sla         # SLA validation only
make test-prompts     # Synthetic prompt suites only
make test-guided-prompt  # Guided Prompt tests only

# Run comprehensive test suite
make test-all
```

## Test Components

### 1. Test Matrix Runner (`test_matrix_runner.py`)

Comprehensive combinatorial testing across all system dimensions:

- **LLM Providers**: OpenAI, Anthropic, HuggingFace, Ollama
- **Databases**: Qdrant, ArangoDB, Meilisearch, PostgreSQL
- **Query Complexities**: Simple (5s), Technical (7s), Research (10s), Multimedia (10s)
- **Guided Prompt Modes**: ON, OFF, ALWAYS_BYPASS, ADAPTIVE

**Usage:**
```bash
# Run test matrix
python test_matrix_runner.py

# Or via pytest
pytest test_matrix_runner.py -v
```

**Key Features:**
- Concurrent test execution
- SLA compliance validation
- Performance metrics collection
- Comprehensive reporting

### 2. SLA Validator (`sla_validator.py`)

Real-time SLA monitoring and validation:

- **Response Time SLAs**: Per-service and per-operation thresholds
- **Availability Monitoring**: 99.9%+ uptime validation
- **Error Rate Tracking**: <0.1% system error rate
- **Alert Generation**: Real-time SLA violation alerts

**Usage:**
```bash
# Run SLA validation
python sla_validator.py

# Or via pytest
pytest sla_validator.py -v
```

**Key Features:**
- Continuous monitoring
- Real-time alerting
- Historical compliance tracking
- Performance recommendations

### 3. Synthetic Prompt Suites (`synthetic_prompt_suites.py`)

Comprehensive prompt testing across all scenarios:

- **Simple Facts**: Basic factual queries
- **Technical Explanations**: Complex technical content
- **Research Analysis**: Multi-step reasoning tasks
- **Guided Prompt Scenarios**: Ambiguous, PII, multilingual, constraint queries
- **Code Generation**: Programming tasks
- **Debugging**: Problem-solving scenarios

**Usage:**
```bash
# Run all prompt suites
python synthetic_prompt_suites.py

# Or via pytest
pytest synthetic_prompt_suites.py -v
```

**Key Features:**
- 200+ test prompts across all categories
- Quality score validation
- Guided Prompt trigger validation
- Performance benchmarking

### 4. Comprehensive Test Runner (`comprehensive_test_runner.py`)

Orchestrates all testing components:

**Usage:**
```bash
# Run all components
python comprehensive_test_runner.py --all

# Run specific components
python comprehensive_test_runner.py --test-matrix --sla-validation

# With custom parameters
python comprehensive_test_runner.py --all --sla-duration 10 --output custom_report.json
```

## Test Categories

### Unit Tests
- Individual component testing
- Mock-based testing
- Fast execution (< 1s per test)

### Integration Tests
- End-to-end API testing
- Service interaction validation
- Real backend integration

### SLA Tests
- Performance validation
- Availability monitoring
- Response time compliance

### Guided Prompt Tests
- Refinement accuracy
- Trigger rate validation
- Latency compliance (≤500ms median, p95 ≤800ms)

## Configuration

### Environment Variables

```bash
# API Configuration
TEST_BASE_URL=http://localhost:8004  # Base URL for API testing
TEST_TIMEOUT=30                      # Test timeout in seconds

# SLA Configuration
SLA_DURATION=5                       # SLA validation duration in minutes

# Performance Configuration
PARALLEL_WORKERS=4                   # Number of parallel test workers
```

### Test Markers

```bash
# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest -m sla                     # SLA tests only
pytest -m guided_prompt           # Guided Prompt tests only
pytest -m "not slow"              # Exclude slow tests
pytest -m requires_api            # Tests requiring API
```

## Test Data

### Prompt Categories

1. **Simple Facts** (5s SLA)
   - Basic factual queries
   - Definitions and calculations
   - Date/time queries

2. **Technical Explanations** (7s SLA)
   - Code generation
   - Technical documentation
   - API usage examples

3. **Research Analysis** (10s SLA)
   - Multi-step reasoning
   - Literature reviews
   - Complex analysis tasks

4. **Guided Prompt Scenarios**
   - Ambiguous queries requiring disambiguation
   - PII-heavy queries requiring sanitization
   - Multilingual queries requiring intent analysis
   - Constraint application scenarios

### SLA Thresholds

| Service | Operation | Threshold |
|---------|-----------|-----------|
| Gateway | Routing | 100ms |
| Retrieval | Search | 2s |
| Synthesis | Generation | 5s |
| Fact-check | Validation | 3s |
| Guided Prompt | Refinement | 800ms |
| Qdrant | Vector Search | 50ms |
| ArangoDB | Graph Query | 100ms |
| Meilisearch | Full-text | 100ms |
| PostgreSQL | Relational | 50ms |

## Reporting

### Test Reports

All tests generate comprehensive reports:

- **JSON Reports**: Machine-readable test results
- **HTML Reports**: Human-readable test summaries
- **Coverage Reports**: Code coverage analysis
- **Performance Reports**: Response time and throughput metrics

### Report Locations

```bash
# Test results
test_results/
├── comprehensive_test_report_*.json
├── test_matrix_results_*.json
├── sla_report_*.json
└── synthetic_prompt_results_*.json

# Coverage reports
htmlcov/
├── index.html
└── coverage.xml

# Performance reports
performance/
├── response_times.json
└── throughput_metrics.json
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: make install
      - name: Run tests
        run: make test-ci
```

### Docker Testing

```bash
# Build test image
docker build -t sarvanom-tests -f Dockerfile.test .

# Run tests in container
docker run --rm sarvanom-tests

# Run with custom configuration
docker run --rm -e TEST_BASE_URL=http://api:8004 sarvanom-tests
```

## Performance Testing

### Load Testing

```bash
# Run load tests
make test-load

# Custom load test
locust -f load_tests.py --host=http://localhost:8004 --users 100 --spawn-rate 10
```

### Benchmark Testing

```bash
# Run benchmarks
make test-benchmark

# Memory profiling
make test-memory
```

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   ```bash
   # Check API health
   curl http://localhost:8004/health
   
   # Verify services are running
   docker-compose ps
   ```

2. **Test Timeouts**
   ```bash
   # Increase timeout
   export TEST_TIMEOUT=60
   make test
   ```

3. **SLA Violations**
   ```bash
   # Check service performance
   make test-sla-only
   
   # Review SLA report
   cat sla_report_*.json
   ```

### Debug Mode

```bash
# Enable debug logging
export PYTHONPATH=/app
export LOG_LEVEL=DEBUG
python -m pytest -v -s
```

## Contributing

### Adding New Tests

1. **Test Matrix**: Add new combinations to `test_matrix_runner.py`
2. **SLA Tests**: Add new thresholds to `sla_validator.py`
3. **Prompt Suites**: Add new scenarios to `synthetic_prompt_suites.py`

### Test Guidelines

- Follow pytest conventions
- Use appropriate test markers
- Include comprehensive assertions
- Add proper error handling
- Document test scenarios

### Code Quality

```bash
# Run code quality checks
make test-security
black tests/
isort tests/
flake8 tests/
mypy tests/
```

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review test logs and reports
3. Verify API service health
4. Check SLA compliance metrics

## License

This testing framework is part of SarvanOM v2 and follows the same licensing terms.
