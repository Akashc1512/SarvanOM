# Backend Integration Test Suite Guide

## Overview

This guide covers the enhanced backend integration test suite that verifies the end-to-end pipeline orchestration for the Universal Knowledge Platform. The test suite ensures that the complete agent chain works correctly:

**Query → Hybrid Retrieval (Vector + Keyword + KG) → Fact-Checking → Citation → Synthesis**

## Test Suite Structure

### File: `tests/integration/test_backend_integration_enhanced.py`

This enhanced test suite focuses on the specific requirements outlined in the user's request:

1. **Basic Query Pipeline** - Tests simple factual queries with local LLM (Ollama)
2. **Complex Research Query** - Tests complex synthesis queries with cloud LLM routing
3. **LLM Failure Fallback** - Tests graceful fallback when primary LLM fails
4. **Cache Hit Verification** - Tests caching behavior and performance
5. **Agent Orchestration** - Verifies agent chain execution order
6. **Response Quality Validation** - Tests response quality metrics and citations
7. **Performance Benchmarks** - Tests SLA compliance and concurrent handling
8. **Error Handling** - Tests error handling and recovery mechanisms

## Test Cases Breakdown

### Test Case 1: Basic Query Pipeline

**Objective**: Verify simple factual queries work with local LLM (Ollama)

**Test Query**: "What is Retrieval Augmented Generation?"

**Assertions**:
- ✅ RetrievalAgent returns results from Meilisearch + Qdrant + ArangoDB
- ✅ FactCheckerAgent verifies statements
- ✅ SynthesisAgent generates a response
- ✅ CitationAgent appends at least one citation
- ✅ Orchestrator selects Ollama (Local LLM) based on query complexity
- ✅ Final response JSON includes all required fields

**Expected Response Structure**:
```json
{
  "answer": "Retrieval Augmented Generation (RAG) is...",
  "citations": [{"title": "...", "url": "..."}],
  "validation_status": "Trusted",
  "llm_provider": "Ollama",
  "cache_status": "Miss",
  "execution_time": 2.5,
  "agent_results": {
    "retrieval": {...},
    "factcheck": {...},
    "synthesis": {...},
    "citation": {...}
  }
}
```

### Test Case 2: Complex Research Query (LLM Routing Test)

**Objective**: Verify complex queries route to cloud LLM (HuggingFace/OpenAI)

**Test Query**: "Explain how knowledge graphs integrate with vector search in AI systems"

**Assertions**:
- ✅ Hybrid Retrieval returns multi-source docs
- ✅ FactChecker validates complex claims
- ✅ Orchestrator chooses HuggingFace API LLM for response generation
- ✅ Citations cover at least 2 different sources
- ✅ Validation status is "Trusted" or "Partial"

### Test Case 3: Fallback Scenario (LLM Failure)

**Objective**: Test graceful fallback when primary LLM fails

**Test Scenario**: Mock Ollama to fail, ensure fallback to HuggingFace/OpenAI

**Assertions**:
- ✅ Orchestrator gracefully falls back to cloud LLM
- ✅ Response still completes with citations
- ✅ Fallback event is logged in orchestrator logs
- ✅ Error handling is graceful

### Test Case 4: Cache Hit Verification

**Objective**: Verify caching behavior and performance

**Test Scenario**: Send same query twice

**Assertions**:
- ✅ First run: triggers full pipeline (cache miss)
- ✅ Second run: fetches cached result (cache hit)
- ✅ Cache status is "Miss" in first run, "Hit" in second
- ✅ Second run is significantly faster

## Running the Tests

### Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install pytest fastapi httpx requests
   ```

2. **Start Backend Services**:
   ```bash
   # Start API Gateway
   python -m services.api_gateway.main
   
   # Start other services (Search, Synthesis, etc.)
   # Ensure all services are running on expected ports
   ```

### Method 1: Using the Test Runner Script

```bash
python run_backend_integration_tests.py
```

This script provides:
- ✅ Dependency checking
- ✅ Service availability verification
- ✅ Comprehensive test reporting
- ✅ Specific test case execution
- ✅ Performance metrics

### Method 2: Direct pytest Execution

```bash
# Run all tests
pytest tests/integration/test_backend_integration_enhanced.py -v

# Run specific test class
pytest tests/integration/test_backend_integration_enhanced.py::TestBasicQueryPipeline -v

# Run specific test method
pytest tests/integration/test_backend_integration_enhanced.py::TestBasicQueryPipeline::test_basic_query_pipeline_success -v

# Run with detailed output
pytest tests/integration/test_backend_integration_enhanced.py -v --tb=long
```

### Method 3: Using the Original Test Suite

```bash
# Run the existing comprehensive test suite
pytest tests/integration/test_backend_integration.py -v
```

## API Endpoint

The tests use the `/query` endpoint that was added to the API Gateway:

```python
POST /query
{
  "query": "What is Retrieval Augmented Generation?",
  "session_id": "test-session-1",
  "user_id": "test-user-1",
  "max_tokens": 1000,
  "confidence_threshold": 0.8
}
```

**Response Format**:
```json
{
  "answer": "Generated answer text...",
  "citations": [
    {
      "title": "Source title",
      "url": "https://example.com",
      "author": "Author name",
      "year": 2024
    }
  ],
  "validation_status": "Trusted|Partial|Unverified",
  "llm_provider": "Ollama|HuggingFace|OpenAI",
  "cache_status": "Hit|Miss",
  "execution_time": 2.5,
  "agent_results": {
    "retrieval": {
      "vector_results": [...],
      "keyword_results": [...],
      "knowledge_graph_results": [...]
    },
    "factcheck": {...},
    "synthesis": {...},
    "citation": {...}
  },
  "confidence_score": 0.85,
  "coherence_score": 0.92,
  "relevance_score": 0.88
}
```

## Test Utilities

The test suite includes utility functions for common assertions:

```python
# Assert response has expected structure
assert_response_structure(data, ["answer", "citations", "validation_status"])

# Assert expected agents executed
assert_agent_execution(data, ["retrieval", "factcheck", "synthesis", "citation"])

# Assert LLM provider is one of expected providers
assert_llm_provider(data, ["Ollama", "HuggingFace", "OpenAI"])

# Assert cache status matches expected
assert_cache_status(data, "Miss")
```

## Expected Outcomes

When all tests pass, you should see:

1. **✅ All API responses are validated**
2. **✅ Orchestrator correctly routes queries**
3. **✅ Fallbacks are tested and working**
4. **✅ Cache hits are confirmed**
5. **✅ Full backend agent chain is operational**

## Troubleshooting

### Common Issues

1. **Service Not Running**:
   ```
   ❌ API Gateway is not running
   ```
   **Solution**: Start the API Gateway service

2. **Import Errors**:
   ```
   ModuleNotFoundError: No module named 'services.api_gateway.main'
   ```
   **Solution**: Ensure you're running from the project root directory

3. **Timeout Errors**:
   ```
   TimeoutError: Request timed out
   ```
   **Solution**: Check if all services are responding within expected timeouts

4. **Authentication Errors**:
   ```
   HTTPException: 401 Unauthorized
   ```
   **Solution**: Ensure proper authentication is configured for test environment

### Debug Mode

Run tests with debug output:

```bash
pytest tests/integration/test_backend_integration_enhanced.py -v -s --tb=long
```

### Service Health Check

Before running tests, verify all services are healthy:

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## Performance Benchmarks

The test suite includes performance benchmarks:

- **SLA Compliance**: 30-second response time limit
- **Concurrent Handling**: 5 simultaneous queries
- **Cache Performance**: Verify cache hits are faster than misses
- **Memory Usage**: Monitor for memory leaks during concurrent tests

## Integration with CI/CD

Add to your CI/CD pipeline:

```yaml
# .github/workflows/backend-tests.yml
- name: Run Backend Integration Tests
  run: |
    python run_backend_integration_tests.py
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Add comprehensive assertions
3. Include performance metrics
4. Document the test purpose
5. Add to the test runner script

## Summary

This enhanced test suite provides comprehensive validation of the backend integration pipeline, ensuring that:

- **Query Processing**: Works end-to-end with proper agent orchestration
- **LLM Selection**: Dynamic routing based on query complexity
- **Fallback Mechanisms**: Graceful handling of service failures
- **Caching**: Proper cache hit/miss behavior
- **Performance**: SLA compliance and concurrent handling
- **Quality**: Response quality metrics and citation verification

The test suite serves as a reliable foundation for ensuring the backend integration pipeline works correctly in all scenarios. 