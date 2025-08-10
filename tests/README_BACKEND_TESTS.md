# Backend Functionality Tests

This directory contains comprehensive tests to verify all backend systems are working as expected with real LLM providers.

## Overview

The test suite validates:
- **Health Endpoints** - System health and monitoring
- **Query Processing** - Real LLM integration (Ollama, OpenAI, Anthropic)
- **Vector DB Integration** - Vector database functionality
- **LLM Routing** - Model selection and fallback mechanisms
- **CORS Configuration** - Cross-origin resource sharing
- **Error Handling** - Graceful degradation and timeout handling
- **Performance** - Response time validation with real LLMs
- **Analytics** - Metrics and monitoring endpoints

## Key Features

### Real LLM Integration
- Tests use actual LLM providers instead of mocks
- Validates end-to-end functionality
- Tests fallback mechanisms between providers
- Performance testing with real API calls

### Comprehensive Coverage
- Health check endpoints (`/health`, `/health/detailed`)
- Query processing (`/search`, `/synthesize`, `/fact-check`)
- Vector database integration (`/vector/search`)
- Knowledge graph endpoints (`/graph/context`)
- Analytics endpoints (`/analytics`, `/analytics/summary`)

### Performance Validation
- Response time thresholds (30s for real LLM calls)
- Concurrent request testing
- Performance consistency checks
- CI/CD pipeline validation

## Test Structure

### Test Classes

1. **TestHealthEndpoints** - Health check validation
2. **TestRootEndpoint** - Root endpoint metadata
3. **TestQueryEndpoints** - Query processing with real LLMs
4. **TestVectorDBIntegration** - Vector database functionality
5. **TestLLMRouting** - LLM routing and fallback
6. **TestCORS** - Cross-origin resource sharing
7. **TestErrorHandling** - Error handling and resilience
8. **TestPerformance** - Performance validation
9. **TestAnalyticsEndpoints** - Analytics and monitoring
10. **TestRealLLMIntegration** - Specific LLM provider tests

### Test Markers

- `@pytest.mark.health` - Health check tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.llm` - LLM integration tests
- `@pytest.mark.cors` - CORS tests
- `@pytest.mark.vector` - Vector DB tests
- `@pytest.mark.analytics` - Analytics tests
- `@pytest.mark.slow` - Slow-running tests

## Running Tests

### Prerequisites

1. **Environment Setup**
   ```bash
   # Set up Python environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install pytest pytest-asyncio httpx
   ```

2. **LLM Provider Configuration**
   ```bash
   # For Ollama (local models)
   export OLLAMA_ENABLED=true
   
   # For OpenAI
   export OPENAI_API_KEY=your_openai_key
   
   # For Anthropic
   export ANTHROPIC_API_KEY=your_anthropic_key
   
   # Model selection policy
   export MODEL_POLICY=cheap_first  # or quality_first
   ```

3. **Backend Services**
   ```bash
   # Start the backend services
   python services/gateway/main.py
   ```

### Running Tests

#### Using the Test Runner Script

```bash
# Run all tests
python scripts/run_backend_tests.py

# Run specific test suites
python scripts/run_backend_tests.py --health-only
python scripts/run_backend_tests.py --performance-only
python scripts/run_backend_tests.py --llm-only

# Run quick tests (exclude slow tests)
python scripts/run_backend_tests.py --quick

# Run with coverage
python scripts/run_backend_tests.py --coverage

# Run specific test patterns
python scripts/run_backend_tests.py --pattern "health"
python scripts/run_backend_tests.py --markers health performance
```

#### Using Pytest Directly

```bash
# Run all tests
pytest tests/test_backend_functionality.py -v

# Run specific test classes
pytest tests/test_backend_functionality.py::TestHealthEndpoints -v
pytest tests/test_backend_functionality.py::TestQueryEndpoints -v

# Run by markers
pytest tests/test_backend_functionality.py -m health -v
pytest tests/test_backend_functionality.py -m "not slow" -v

# Run with coverage
pytest tests/test_backend_functionality.py --cov=services --cov=shared --cov-report=html
```

### Test Configuration

#### Environment Variables

```bash
# Test configuration
export TESTING=true
export LOG_LEVEL=INFO

# Performance thresholds
export PERFORMANCE_THRESHOLD=30.0  # seconds
export TEST_TIMEOUT=60.0  # seconds

# LLM configuration
export MODEL_POLICY=cheap_first
export OLLAMA_ENABLED=true
export USE_VECTOR_DB=true
```

#### Test Data

The tests use predefined test queries:
- Simple queries for basic functionality
- Complex queries for LLM routing
- Technical queries for model selection
- Creative queries for response quality

## Test Results

### Expected Output

```
============================= test session starts ==============================
platform linux -- Python 3.11.0, pytest-7.4.0, pluggy-1.2.0
rootdir: /path/to/sarvanom
plugins: asyncio-0.21.1, cov-4.1.0
collected 25 items

tests/test_backend_functionality.py::TestHealthEndpoints::test_health_endpoint_returns_200_with_status PASSED [  4%]
tests/test_backend_functionality.py::TestHealthEndpoints::test_detailed_health_endpoint PASSED [  8%]
tests/test_backend_functionality.py::TestHealthEndpoints::test_health_endpoint_performance PASSED [ 12%]
...

============================== 25 passed in 45.32s ==============================
```

### Performance Metrics

- **Health Checks**: < 10 seconds
- **Query Processing**: < 30 seconds (real LLM calls)
- **Concurrent Requests**: < 60 seconds (3 concurrent)
- **Full Pipeline**: < 90 seconds (search + synthesis + fact-check)

## Troubleshooting

### Common Issues

1. **LLM Provider Not Available**
   ```
   Error: No LLM providers available
   Solution: Configure at least one LLM provider (Ollama, OpenAI, or Anthropic)
   ```

2. **Timeout Errors**
   ```
   Error: Query took 35.2s > 30.0s
   Solution: Increase PERFORMANCE_THRESHOLD or check network connectivity
   ```

3. **Backend Not Running**
   ```
   Error: Connection refused
   Solution: Start the backend services before running tests
   ```

4. **Missing Dependencies**
   ```
   Error: ModuleNotFoundError: No module named 'httpx'
   Solution: Install test dependencies: pip install pytest pytest-asyncio httpx
   ```

### Debug Mode

```bash
# Run with verbose output
pytest tests/test_backend_functionality.py -v -s

# Run single test with debug
pytest tests/test_backend_functionality.py::TestQueryEndpoints::test_query_endpoint_happy_path -v -s

# Run with logging
pytest tests/test_backend_functionality.py --log-cli-level=DEBUG
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Backend Tests
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
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx
      - name: Run tests
        run: |
          python scripts/run_backend_tests.py --quick
        env:
          OLLAMA_ENABLED: true
          MODEL_POLICY: cheap_first
```

### Local CI/CD

```bash
# Run tests for CI/CD
python scripts/run_backend_tests.py --quick --coverage

# Run full test suite
python scripts/run_backend_tests.py --coverage
```

## Contributing

### Adding New Tests

1. **Follow the existing pattern**
   ```python
   @pytest.mark.asyncio
   async def test_new_feature(self, async_client: AsyncClient):
       """Test description."""
       # Test implementation
       response = await async_client.post("/endpoint", json=data)
       assert response.status_code == 200
   ```

2. **Use appropriate markers**
   ```python
   @pytest.mark.llm  # For LLM-related tests
   @pytest.mark.performance  # For performance tests
   @pytest.mark.slow  # For slow-running tests
   ```

3. **Add to test runner**
   ```python
   # Add new test categories to run_backend_tests.py
   def run_new_feature_tests():
       return run_tests(markers=["new_feature"])
   ```

### Test Guidelines

- Use real LLM providers when possible
- Include performance assertions
- Test both success and error cases
- Use descriptive test names
- Add appropriate markers for categorization
- Keep tests independent and isolated

## Support

For issues with the tests:
1. Check the troubleshooting section
2. Review the test logs
3. Verify environment configuration
4. Ensure backend services are running
5. Check LLM provider availability
