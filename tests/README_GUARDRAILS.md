# 🚀 Automated Guardrails for Quality Assurance

## Overview

The Automated Guardrails system provides comprehensive quality assurance for the SarvanOM retrieval system, ensuring:

- **Groundedness**: Citation coverage ≥ 95% for factual queries
- **Latency**: Strict performance budgets (P95 ≤ 3s for simple queries)
- **Regression Prevention**: Automatic build failure on quality degradation
- **Monitoring**: Trend analysis and historical performance tracking

## 🎯 Key Features

### 1. **Golden Test Suite (100+ Prompts)**
- **Factual Queries**: High citation coverage requirements (≥95%)
- **Research Queries**: Comprehensive source requirements (≥90%)
- **Technical Queries**: Precision requirements (≥95%)
- **Creative Queries**: Flexible requirements (≥80%)
- **Performance Queries**: Speed testing (≤2s)

### 2. **Failure Scenario Testing**
- **No Paid API Keys**: Fallback to free/local models
- **Vector Database Down**: Continue with web search + KG
- **Knowledge Graph Down**: Continue with vector + web search
- **Web Search Down**: Continue with vector + KG

### 3. **Quality Thresholds**
- **Overall Success Rate**: ≥80% (build fails if below)
- **Category Success Rate**: ≥70% (build fails if below)
- **Latency Budget**: ≤5s total (build fails if above)

## 🚀 Quick Start

### Run Locally
```bash
# Run full guardrails suite
make guardrails-local

# Or directly
python tests/golden_test_suite.py
```

### Run in CI/CD
```bash
# Run with CI integration
make guardrails

# Or directly
python tests/run_guardrails_ci.py
```

### View Reports
```bash
# Generate latest report
make guardrails-report

# View results directory
ls code_garden/golden_test_results/
```

## 📊 Test Categories

### Factual Queries (20 prompts)
- **Purpose**: Test high-accuracy information retrieval
- **Requirements**: 
  - Citation coverage ≥95%
  - Uncertainty ≤10%
  - Latency ≤3s
  - Expected sources: 3

**Example Prompts:**
- "What is the capital of France?"
- "Who wrote Romeo and Juliet?"
- "What is the chemical formula for water?"

### Research Queries (20 prompts)
- **Purpose**: Test comprehensive research capabilities
- **Requirements**:
  - Citation coverage ≥90%
  - Uncertainty ≤15%
  - Latency ≤5s
  - Expected sources: 5

**Example Prompts:**
- "What are the latest developments in quantum computing?"
- "How does climate change affect biodiversity?"
- "What are the health benefits of Mediterranean diet?"

### Technical Queries (20 prompts)
- **Purpose**: Test precise technical information
- **Requirements**:
  - Citation coverage ≥95%
  - Uncertainty ≤5%
  - Latency ≤4s
  - Expected sources: 4

**Example Prompts:**
- "How does a neural network work?"
- "What is the difference between HTTP and HTTPS?"
- "How do blockchain transactions work?"

### Creative Queries (20 prompts)
- **Purpose**: Test innovative and creative responses
- **Requirements**:
  - Citation coverage ≥80%
  - Uncertainty ≤25%
  - Latency ≤3s
  - Expected sources: 2

**Example Prompts:**
- "How can I improve my creative writing skills?"
- "What are some innovative business ideas for 2024?"
- "How can I design a more sustainable home?"

### Performance Queries (20 prompts)
- **Purpose**: Test system performance and speed
- **Requirements**:
  - Citation coverage ≥85%
  - Uncertainty ≤15%
  - Latency ≤2s
  - Expected sources: 2

**Example Prompts:**
- "What is the weather like?"
- "How are you today?"
- "What time is it?"

## 🔧 Failure Scenarios

### 1. **No Paid API Keys**
- **Test**: Disable paid API keys
- **Expected**: Fallback to free/local models
- **Latency Budget**: ≤5s
- **Success Criteria**: Response generated with free models

### 2. **Vector Database Down**
- **Test**: Simulate vector database failure
- **Expected**: Continue with web search + knowledge graph
- **Latency Budget**: ≤4s
- **Success Criteria**: Sources from remaining lanes

### 3. **Knowledge Graph Down**
- **Test**: Simulate knowledge graph failure
- **Expected**: Continue with vector search + web search
- **Latency Budget**: ≤4s
- **Success Criteria**: Sources from remaining lanes

### 4. **Web Search Down**
- **Test**: Simulate web search failure
- **Expected**: Continue with vector search + knowledge graph
- **Latency Budget**: ≤4s
- **Success Criteria**: Sources from remaining lanes

## 📈 Quality Metrics

### Citation Coverage
- **Calculation**: `min(1.0, sources_count / expected_sources)`
- **Thresholds**: Vary by category (80%-95%)
- **Build Failure**: If any category below 70%

### Uncertainty
- **Calculation**: `max(0.0, 1.0 - citation_coverage)`
- **Thresholds**: Vary by category (5%-25%)
- **Build Failure**: If any category above 30%

### Latency
- **Measurement**: End-to-end response time
- **Thresholds**: Vary by category (2s-5s)
- **Build Failure**: If total duration >5s

### Success Rate
- **Calculation**: `passed_tests / total_tests`
- **Overall Threshold**: ≥80%
- **Category Threshold**: ≥70%
- **Build Failure**: If below thresholds

## 🚨 Build Failure Conditions

The CI pipeline will **FAIL** if any of these conditions are met:

1. **Overall Success Rate < 80%**
2. **Any Category Success Rate < 70%**
3. **Total Duration > 5 seconds**
4. **Critical Service Failures** (vector, KG, web all down)

## 📄 Output Artifacts

### 1. **JSON Results**
- **Location**: `code_garden/golden_test_results/`
- **Format**: `golden_test_results_YYYYMMDD_HHMMSS.json`
- **Content**: Complete test results with metrics

### 2. **HTML Reports**
- **Location**: `code_garden/golden_test_results/`
- **Format**: `golden_test_report_YYYYMMDD_HHMMSS.html`
- **Content**: Interactive web report with styling

### 3. **Markdown Reports**
- **Location**: `code_garden/golden_test_results/`
- **Format**: `golden_test_report_YYYYMMDD_HHMMSS.md`
- **Content**: Plain text report for documentation

### 4. **CI Logs**
- **Location**: `guardrails_ci.log`
- **Content**: Detailed execution logs for CI debugging

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Quality Guardrails
on: [push, pull_request]

jobs:
  guardrails:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run Guardrails
        run: |
          python tests/run_guardrails_ci.py
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: guardrails-results
          path: code_garden/golden_test_results/
```

### GitLab CI Example
```yaml
guardrails:
  stage: test
  script:
    - pip install -r requirements.txt
    - python tests/run_guardrails_ci.py
  artifacts:
    paths:
      - code_garden/golden_test_results/
    expire_in: 1 week
```

## 🛠️ Customization

### Adding New Test Categories
```python
# In tests/golden_test_suite.py
self.test_categories["new_category"] = {
    "description": "Description of new category",
    "min_citation_coverage": 0.85,
    "max_uncertainty": 0.20,
    "latency_budget_ms": 3500,
    "expected_sources": 3
}

self.golden_prompts["new_category"] = [
    "New prompt 1",
    "New prompt 2",
    # ... more prompts
]
```

### Modifying Quality Thresholds
```python
# In tests/golden_test_suite.py
def _should_fail_build(self, results: Dict[str, Any]) -> bool:
    overall_metrics = results["overall_metrics"]
    
    # Customize thresholds
    if overall_metrics["success_rate"] < 0.85:  # Changed from 0.8
        return True
    
    # Add custom failure conditions
    if overall_metrics["total_duration_ms"] > 3000:  # Changed from 5000
        return True
    
    return False
```

### Adding New Failure Scenarios
```python
# In tests/golden_test_suite.py
self.failure_scenarios["new_scenario"] = {
    "description": "Test new failure scenario",
    "expected_behavior": "Expected behavior description",
    "latency_budget_ms": 4000
}
```

## 📊 Monitoring and Trends

### Weekly Reports
The system automatically saves results with timestamps, enabling:

1. **Performance Trends**: Track latency improvements/regressions
2. **Quality Metrics**: Monitor citation coverage over time
3. **Failure Analysis**: Identify recurring issues
4. **Capacity Planning**: Understand system performance under load

### Metrics Dashboard
Consider integrating with:
- **Prometheus**: For real-time metrics
- **Grafana**: For visualization
- **ELK Stack**: For log analysis
- **Custom Dashboard**: For business metrics

## 🚀 Performance Optimization

### Current Performance Targets
- **Vector Search**: ≤2.0s (currently ~25s - needs optimization)
- **Knowledge Graph**: ≤1.5s (currently ~1.0s - ✅ compliant)
- **Web Search**: ≤1.0s (currently compliant)
- **End-to-End**: ≤3.0s (currently ~1.0s - ✅ compliant)

### Optimization Strategies
1. **Embedding Model**: Use faster models (L3 vs L6)
2. **Vector Database**: Optimize Qdrant queries
3. **Caching**: Implement result caching
4. **Parallelization**: Optimize async execution
5. **Resource Limits**: Enforce strict timeouts

## 🔍 Troubleshooting

### Common Issues

#### 1. **Vector Search Too Slow**
```bash
# Check Qdrant health
docker ps | grep qdrant

# Check embedding model
python -c "from shared.embeddings.local_embedder import get_embedder; print('Model loaded')"
```

#### 2. **Knowledge Graph Failures**
```bash
# Check ArangoDB health
docker ps | grep arangodb

# Test connection
python -c "from shared.core.agents.knowledge_graph_service import KnowledgeGraphService; print('KG service ready')"
```

#### 3. **Web Search Issues**
```bash
# Check API keys
echo $SERPAPI_API_KEY
echo $BRAVE_API_KEY

# Test endpoints
curl -s "https://api.serpapi.com/search?q=test&api_key=$SERPAPI_API_KEY" | head -20
```

### Debug Mode
```bash
# Run with verbose logging
LOG_LEVEL=DEBUG python tests/golden_test_suite.py

# Check specific category
python -c "
from tests.golden_test_suite import GoldenTestSuite
import asyncio

async def test_category():
    suite = GoldenTestSuite()
    results = await suite._test_category('factual_queries', suite.test_categories['factual_queries'])
    print(f'Results: {len(results)} tests')
    for r in results[:3]:
        print(f'- {r[\"prompt\"]}: {r[\"passed\"]}')

asyncio.run(test_category())
"
```

## 📚 Additional Resources

### Documentation
- [SarvanOM Architecture](docs/architecture.md)
- [Performance Guidelines](docs/performance.md)
- [Testing Strategy](docs/testing.md)

### Code Examples
- [Golden Test Suite](tests/golden_test_suite.py)
- [CI Integration](tests/run_guardrails_ci.py)
- [Performance Tests](tests/test_always_on_performance.py)

### Monitoring
- [Prometheus Metrics](docs/metrics.md)
- [Logging Configuration](docs/logging.md)
- [Alerting Rules](docs/alerting.md)

---

## 🎯 Next Steps

1. **Run Initial Guardrails**: `make guardrails-local`
2. **Review Results**: Check `code_garden/golden_test_results/`
3. **Optimize Performance**: Address vector search latency
4. **Integrate CI/CD**: Add to build pipeline
5. **Monitor Trends**: Track weekly performance metrics

For questions or issues, check the troubleshooting section or create an issue in the project repository.
