# SarvanOM Comprehensive Testing Guide

## Overview

This guide provides comprehensive testing for all combinations of SarvanOM's backend LLM, database, and knowledge graph components with different levels and complexity of tasks using Docker.

## Test Architecture

### Components Tested

#### LLM Providers
- **OpenAI**: GPT models for text generation and analysis
- **Anthropic**: Claude models for reasoning and analysis
- **HuggingFace**: Open-source models for various NLP tasks
- **Ollama**: Local models for zero-budget operations

#### Databases
- **PostgreSQL**: Primary relational database
- **Redis**: Caching and session storage
- **ArangoDB**: Knowledge graph storage
- **Qdrant**: Vector database for embeddings
- **Meilisearch**: Full-text search engine

#### Knowledge Graph
- **ArangoDB**: Graph database for relationships
- **Vector Storage**: Qdrant for semantic search
- **Graph Traversal**: Complex relationship queries

### Complexity Levels

#### Simple Tasks
- Basic queries and responses
- Simple database operations
- Basic knowledge graph queries
- Health checks and monitoring

#### Medium Tasks
- Multi-step reasoning
- Complex database queries
- Graph traversal operations
- Multi-modal data processing

#### Complex Tasks
- Advanced AI reasoning
- Distributed system operations
- Knowledge graph analysis
- Multi-component workflows

#### Expert Tasks
- Quantum-enhanced algorithms
- Self-evolving systems
- Multi-modal AI systems
- Autonomous system operations

## Test Matrix

### LLM + Database Combinations
| LLM Provider | PostgreSQL | Redis | ArangoDB | Qdrant | Meilisearch |
|--------------|------------|-------|----------|--------|-------------|
| OpenAI       | ✅         | ✅     | ✅       | ✅     | ✅          |
| Anthropic    | ✅         | ✅     | ✅       | ✅     | ✅          |
| HuggingFace  | ✅         | ✅     | ✅       | ✅     | ✅          |
| Ollama       | ✅         | ✅     | ✅       | ✅     | ✅          |

### Knowledge Graph + Vector DB Combinations
| Knowledge Graph | Vector DB | Search Engine | Complexity |
|-----------------|-----------|---------------|------------|
| ArangoDB        | Qdrant    | Meilisearch   | Simple     |
| ArangoDB        | Qdrant    | Meilisearch   | Medium     |
| ArangoDB        | Qdrant    | Meilisearch   | Complex    |
| ArangoDB        | Qdrant    | Meilisearch   | Expert     |

### Integrated Workflows
1. **Search and Synthesize**: Search + LLM + Knowledge Graph
2. **Fact Check Workflow**: Retrieval + Fact Check + LLM
3. **Knowledge Extraction**: LLM + KG + Vector DB
4. **Multi-modal Analysis**: All components integrated

## Running Tests

### Prerequisites

1. **Docker and Docker Compose** installed and running
2. **Python 3.13+** with virtual environment
3. **Required dependencies** installed

### Quick Start

```bash
# Run comprehensive test suite
make test-comprehensive

# Or use the Python script directly
python test_docker_comprehensive.py
```

### Individual Component Tests

```bash
# Test all LLM combinations
make test-llm-combinations

# Test all database combinations
make test-db-combinations

# Test knowledge graph combinations
make test-kg-combinations
```

### Complexity Level Tests

```bash
# Test simple tasks only
make test-simple

# Test medium complexity
make test-medium

# Test complex tasks
make test-complex

# Test expert level (all complexity levels)
make test-expert
```

### Quick Health Check

```bash
# Quick test for development
make test-quick

# Check all service health
make health-check
```

## Test Configuration

### Environment Variables

The test environment uses `.env.docker` with the following key configurations:

```bash
# Database Configuration
POSTGRES_DB=sarvanom_test
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sarvanom_test_password_2025

# Redis Configuration
REDIS_PASSWORD=sarvanom_redis_test_2025

# ArangoDB Configuration
ARANGODB_PASSWORD=sarvanom_arangodb_test_2025

# Meilisearch Configuration
MEILI_MASTER_KEY=sarvanom_meili_test_master_key_2025_very_secure

# Environment
ENVIRONMENT=testing
LOG_LEVEL=DEBUG
```

### Docker Services

The test environment includes:

- **Infrastructure Services**: PostgreSQL, Redis, ArangoDB, Qdrant, Meilisearch, Ollama, MinIO
- **Backend Service**: SarvanOM API Gateway
- **Test Runner**: Comprehensive test execution
- **Monitoring**: Prometheus and Grafana

## Test Results

### Output Files

Test results are saved in the `test_results/` directory:

- `test_results_YYYYMMDD_HHMMSS.json`: Detailed test results
- `test_summary_YYYYMMDD_HHMMSS.json`: Test summary and statistics
- `test_report_YYYYMMDD_HHMMSS.txt`: Human-readable report

### Metrics Collected

- **Success Rate**: Percentage of successful tests
- **Response Time**: Average response time per test
- **Component Performance**: Performance by component type
- **Complexity Analysis**: Performance by complexity level
- **Error Analysis**: Detailed error messages and patterns

### Sample Output

```
SARVANOM COMPREHENSIVE TEST SUMMARY
====================================
Total Tests: 156
Successful: 142
Failed: 14
Success Rate: 91.03%
Total Time: 1247.32s
Avg Response Time: 234.56ms

BY COMPONENT:
  llm_openai: 38/40 (95.0%)
  llm_anthropic: 36/40 (90.0%)
  llm_huggingface: 32/40 (80.0%)
  llm_ollama: 28/40 (70.0%)
  database_postgres: 8/8 (100.0%)
  database_redis: 8/8 (100.0%)
  knowledge_graph: 20/24 (83.3%)
  integrated_workflow: 12/16 (75.0%)

BY COMPLEXITY:
  simple: 45/48 (93.8%)
  medium: 38/42 (90.5%)
  complex: 35/40 (87.5%)
  expert: 24/26 (92.3%)
```

## Troubleshooting

### Common Issues

1. **Docker Not Running**
   ```bash
   # Check Docker status
   docker --version
   docker ps
   ```

2. **Port Conflicts**
   ```bash
   # Check for port usage
   netstat -tulpn | grep :8000
   ```

3. **Service Health Issues**
   ```bash
   # Check service logs
   docker compose -f docker-compose.test.yml logs [service-name]
   ```

4. **Test Timeout**
   ```bash
   # Increase timeout in test configuration
   # Or run individual component tests
   make test-simple
   ```

### Debug Mode

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python test_docker_comprehensive.py

# Check individual service health
curl http://localhost:8000/health
curl http://localhost:5432  # PostgreSQL
curl http://localhost:6379  # Redis
curl http://localhost:8529/_api/version  # ArangoDB
curl http://localhost:6333/  # Qdrant
curl http://localhost:7700/health  # Meilisearch
curl http://localhost:11434/api/tags  # Ollama
```

## Performance Benchmarks

### Expected Performance

| Component | Simple | Medium | Complex | Expert |
|-----------|--------|--------|---------|--------|
| OpenAI    | <100ms | <500ms | <2s     | <5s    |
| Anthropic | <150ms | <600ms | <2.5s   | <6s    |
| HuggingFace| <200ms| <800ms | <3s     | <8s    |
| Ollama    | <300ms | <1s    | <4s     | <10s   |
| PostgreSQL| <50ms  | <100ms | <200ms  | <500ms |
| Redis     | <10ms  | <20ms  | <50ms   | <100ms |
| ArangoDB  | <100ms | <300ms | <1s     | <2s    |
| Qdrant    | <150ms | <400ms | <1.5s   | <3s    |
| Meilisearch| <80ms | <200ms | <500ms  | <1s    |

### Success Rate Targets

- **Simple Tasks**: >95%
- **Medium Tasks**: >90%
- **Complex Tasks**: >85%
- **Expert Tasks**: >80%
- **Overall**: >90%

## Continuous Integration

### GitHub Actions Integration

```yaml
name: Comprehensive Testing
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Comprehensive Tests
        run: make test-comprehensive
```

### Local Development

```bash
# Run tests before committing
make test-quick

# Run full test suite before major changes
make test-comprehensive
```

## Advanced Testing

### Load Testing

```bash
# Run load tests with multiple concurrent requests
docker compose -f docker-compose.test.yml run --rm test-runner python -c "
import asyncio
from scripts.comprehensive_test_runner import ComprehensiveTestRunner
runner = ComprehensiveTestRunner()
# Configure for load testing
asyncio.run(runner.run_load_tests())
"
```

### Stress Testing

```bash
# Run stress tests with high complexity tasks
make test-expert
```

### Integration Testing

```bash
# Test all integrated workflows
docker compose -f docker-compose.test.yml run --rm test-runner python -c "
import asyncio
from scripts.comprehensive_test_runner import ComprehensiveTestRunner
runner = ComprehensiveTestRunner()
asyncio.run(runner.test_integrated_workflows())
"
```

## Conclusion

This comprehensive testing framework ensures that all combinations of SarvanOM's components work correctly across different complexity levels. The Docker-based approach provides consistent, reproducible testing environments that can be easily integrated into CI/CD pipelines.

For questions or issues, refer to the test logs in the `test_results/` directory or check the individual service logs using Docker commands.
