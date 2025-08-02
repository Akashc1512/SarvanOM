# End-to-End Test Guide for Real Backend Pipeline

## Overview

This guide provides comprehensive instructions for running end-to-end tests that validate the complete backend orchestration flow using real services and data.

## Test Coverage

The E2E tests validate:

- **Full Pipeline Orchestration**: Retrieval → FactCheck → Synthesis → Citation
- **Hybrid Retrieval**: Meilisearch + Qdrant + ArangoDB integration
- **LLM Routing**: Dynamic model selection (Ollama/HuggingFace/OpenAI)
- **Cache Management**: Hit/miss behavior and performance
- **Fact-Checking**: Validation and citation management
- **Fallback Mechanisms**: Service failure handling
- **Response Structure**: Complete API response validation

## Test Cases

### 1. Basic End-to-End Query Flow (Cold Cache)
- **Objective**: Test complete pipeline execution with factual query
- **Query**: "What is Retrieval Augmented Generation?"
- **Validation**: 
  - Cache status = "Miss"
  - LLM provider selected (Ollama/HuggingFace/OpenAI)
  - Citations present
  - Validation status = "Trusted"/"Partial"
  - Execution time < 30 seconds

### 2. Cache Hit on Repeat Query
- **Objective**: Validate cache functionality
- **Query**: Same as test 1
- **Validation**:
  - Cache status = "Hit"
  - Answer content identical
  - Faster execution time
  - All fields preserved

### 3. Complex Synthesis Query (LLM Routing Check)
- **Objective**: Test LLM routing for complex queries
- **Query**: "Explain how vector databases and knowledge graphs complement each other in AI systems."
- **Validation**:
  - LLM provider = HuggingFace/OpenAI (not Ollama)
  - Multiple citations (≥2)
  - Comprehensive answer (>200 chars)
  - Technical keywords present

### 4. Fallback Scenario (Simulated Service Failure)
- **Objective**: Test fallback mechanisms
- **Query**: "Fallback test query for service failure simulation"
- **Validation**:
  - Ollama failure simulated
  - Fallback to HuggingFace/OpenAI successful
  - Answer still generated
  - Cache status = "Miss"

### 5. Fact-Check Freshness Validation
- **Objective**: Test temporal validation
- **Query**: "What is the status of AI trends from 2020?"
- **Validation**:
  - Validation status = "Outdated"/"Partial"
  - Citations contain "2020" references
  - Disclaimer added if outdated

### 6. Technical Query Routing
- **Objective**: Test technical query handling
- **Query**: "How does Python handle memory management compared to C++?"
- **Validation**:
  - Technical keywords in answer
  - Citations present
  - Confidence scores > 0

### 7. Hybrid Retrieval Validation
- **Objective**: Test all retrieval sources
- **Query**: "What are the key differences between SQL and NoSQL databases?"
- **Validation**:
  - Vector results present
  - Keyword results present
  - Knowledge graph results present
  - Total results > 0

### 8. Response Structure Validation
- **Objective**: Validate complete API response
- **Query**: "What is machine learning?"
- **Validation**:
  - All required fields present
  - Correct data types
  - Value ranges valid
  - Agent results structure complete

### 9. Error Handling and Recovery
- **Objective**: Test service failure handling
- **Query**: "Test error handling with service failures"
- **Validation**:
  - Graceful degradation
  - Error response structure
  - Service recovery

### 10. Performance Under Load
- **Objective**: Test system performance
- **Queries**: 5 concurrent technical queries
- **Validation**:
  - Success rate ≥ 60%
  - Total time < 60 seconds
  - Reasonable execution times

## Prerequisites

### 1. Environment Setup
```bash
# Ensure you're in the project root
cd /path/to/sarvanom

# Install test dependencies
pip install pytest httpx pytest-asyncio

# Optional: Install coverage
pip install pytest-cov
```

### 2. Service Requirements
- **FastAPI Gateway**: Running on default port
- **Meilisearch**: Available for vector search
- **Qdrant**: Available for vector database
- **ArangoDB**: Available for knowledge graph
- **Ollama**: Local LLM service (optional)
- **HuggingFace API**: Available for inference
- **OpenAI API**: Available for fallback

### 3. Environment Variables
Ensure these are set in your `.env` file:
```bash
# LLM Providers
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_KEY=your_hf_key
OLLAMA_BASE_URL=http://localhost:11434

# Search Services
MEILI_MASTER_KEY=your_meili_key
MEILI_URL=http://localhost:7700

# Database
ARANGODB_URL=http://localhost:8529
ARANGODB_USERNAME=root
ARANGODB_PASSWORD=your_password

# Vector Database
QDRANT_URL=http://localhost:6333
```

## Running Tests

### Method 1: Using the Test Runner Script
```bash
# Run all tests
python run_e2e_tests.py

# Run with verbose output
python run_e2e_tests.py --verbose

# Run specific test
python run_e2e_tests.py --specific-test test_basic_pipeline_flow

# Run only health checks
python run_e2e_tests.py --health-only

# Generate test report only
python run_e2e_tests.py --report-only
```

### Method 2: Using pytest directly
```bash
# Run all E2E tests
pytest tests/e2e/test_real_backend_pipeline.py -v

# Run specific test class
pytest tests/e2e/test_real_backend_pipeline.py::TestRealBackendPipeline -v

# Run specific test method
pytest tests/e2e/test_real_backend_pipeline.py::TestRealBackendPipeline::test_basic_pipeline_flow -v

# Run with coverage
pytest tests/e2e/test_real_backend_pipeline.py --cov=services --cov-report=html
```

### Method 3: Using Makefile (if available)
```bash
# Run E2E tests
make test-e2e

# Run with verbose output
make test-e2e-verbose
```

## Expected Results

### Successful Test Run
```
🧪 Real Backend Pipeline E2E Test Runner
==================================================
Started at: 2024-12-28 15:30:00

🔧 Setting up test environment...
✅ FastAPI app imported successfully
✅ Test dependencies available

🏥 Running health checks...
✅ Health endpoint responding
✅ Simple health endpoint responding

🚀 Starting E2E tests...
Running command: python -m pytest tests/e2e/test_real_backend_pipeline.py -v --tb=short --color=yes
✅ Basic pipeline test passed - LLM Provider: Ollama, Cache: Miss, Time: 2.45s
✅ Cache hit test passed - Cache: Hit, Time: 0.12s
✅ Complex query routing test passed - LLM Provider: HuggingFace, Citations: 3
✅ Fallback test passed - LLM Provider: OpenAI, Fallback successful
✅ Freshness validation test passed - Status: Partial
✅ Technical query test passed - Confidence: 0.85
✅ Hybrid retrieval test passed - Vector: 5, Keyword: 3, KG: 2
✅ Response structure validation passed
✅ Error handling test passed - Status: 200
✅ Performance test passed - Success: 5/5, Avg Time: 1.23s, Total Time: 6.15s

✅ All tests passed in 15.67 seconds

📊 Test Report
==================================================
Test Cases Covered:
   1. Basic End-to-End Query Flow (Cold Cache)
   2. Cache Hit on Repeat Query
   3. Complex Synthesis Query (LLM Routing Check)
   4. Fallback Scenario (Simulated Service Failure)
   5. Fact-Check Freshness Validation
   6. Technical Query Routing
   7. Hybrid Retrieval Validation
   8. Response Structure Validation
   9. Error Handling and Recovery
  10. Performance Under Load

Expected Outcomes:
✅ Full pipeline orchestration (Retrieval → FactCheck → Synthesis → Citation)
✅ Hybrid retrieval (Meilisearch + Qdrant + ArangoDB)
✅ LLM routing and fallback mechanisms
✅ Cache hit/miss behavior
✅ Fact-checking and citation validation
✅ Service failure scenarios and fallbacks
✅ Response structure validation

🎉 All tests completed successfully!
```

### Failed Test Run
```
❌ Some tests failed in 25.34 seconds

📊 Test Report
==================================================
Test Cases Covered:
   1. Basic End-to-End Query Flow (Cold Cache) ❌
   2. Cache Hit on Repeat Query ❌
   3. Complex Synthesis Query (LLM Routing Check) ✅
   4. Fallback Scenario (Simulated Service Failure) ✅
   5. Fact-Check Freshness Validation ✅
   6. Technical Query Routing ✅
   7. Hybrid Retrieval Validation ✅
   8. Response Structure Validation ✅
   9. Error Handling and Recovery ✅
  10. Performance Under Load ✅

⚠️ Some tests failed. Please check:
1. Service availability and health
2. Environment configuration
3. Test logs for specific failures
4. System resources and dependencies
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```
❌ Failed to import FastAPI app: ModuleNotFoundError: No module named 'services'
```
**Solution**: Ensure you're in the project root directory and Python path is set correctly.

#### 2. Service Connection Errors
```
❌ Health checks failed: ConnectionError: Failed to connect to localhost:8000
```
**Solution**: 
- Start the FastAPI server: `uvicorn services.api_gateway.main:app --reload`
- Check service ports and configurations

#### 3. Authentication Errors
```
❌ 401 Unauthorized: Authentication required
```
**Solution**: The tests mock authentication, but ensure the auth service is properly configured.

#### 4. LLM Provider Errors
```
❌ LLM synthesis error: No LLM providers available
```
**Solution**: 
- Check API keys in `.env` file
- Ensure at least one LLM provider is configured
- Verify Ollama is running if using local models

#### 5. Database Connection Errors
```
❌ ArangoDB connection failed: Connection refused
```
**Solution**: 
- Start ArangoDB service
- Check database credentials
- Verify network connectivity

### Debug Mode

Run tests with maximum verbosity for debugging:
```bash
python run_e2e_tests.py --verbose
pytest tests/e2e/test_real_backend_pipeline.py -v -s --tb=long
```

### Individual Test Debugging

Run a specific test with detailed output:
```bash
pytest tests/e2e/test_real_backend_pipeline.py::TestRealBackendPipeline::test_basic_pipeline_flow -v -s --tb=long
```

## Performance Benchmarks

### Expected Performance Metrics
- **Single Query**: 2-5 seconds
- **Cache Hit**: < 0.5 seconds
- **Complex Query**: 5-10 seconds
- **Concurrent Queries**: 60%+ success rate
- **Total Test Suite**: < 60 seconds

### Performance Optimization
1. **Enable Caching**: Ensure Redis is running
2. **Optimize LLM Selection**: Use local models when possible
3. **Parallel Processing**: Run tests in parallel if needed
4. **Resource Monitoring**: Monitor CPU/memory usage

## Continuous Integration

### GitHub Actions Example
```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest httpx pytest-asyncio
      - name: Run E2E tests
        run: python run_e2e_tests.py --verbose
```

## Next Steps

After successful test execution:

1. **Review Results**: Check test logs and performance metrics
2. **Validate Quality**: Manually verify response quality and accuracy
3. **Monitor Performance**: Track execution times and success rates
4. **Update Documentation**: Keep test documentation current
5. **Expand Coverage**: Add more test cases as features evolve

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review service logs for detailed error messages
3. Verify environment configuration
4. Test individual components separately
5. Consult the main project documentation

---

**Note**: These tests use real services and may incur API costs. Monitor usage and set appropriate rate limits for production environments. 