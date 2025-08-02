# Route Query Function Guide

## Overview

The `route_query` function in `services/api_gateway/main.py` provides a comprehensive query processing pipeline that orchestrates multiple services to deliver accurate, verified answers.

## Function Signature

```python
async def route_query(query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]
```

## Pipeline Steps

The function implements a 4-step pipeline:

1. **Query Classification** - Classifies the query using keywords and heuristics
2. **Document Retrieval** - Calls `search_service.retrieve(query)` to find relevant documents
3. **Fact Verification** - Calls `factcheck_service.verify(results)` to verify claims
4. **Answer Synthesis** - Calls `synthesis_service.compose(answer)` to generate final answer

## Environment Configuration

The function uses the `USE_DYNAMIC_SELECTION` environment variable to decide between:
- **Local LLM (Ollama)**: When `USE_DYNAMIC_SELECTION=true`
- **API calls**: When `USE_DYNAMIC_SELECTION=false`

## Usage Example

```python
from services.api_gateway.main import route_query

# Basic usage
result = await route_query("What is Python programming language?")

# With user context
user_context = {
    "max_tokens": 3000,
    "confidence_threshold": 0.8,
    "preferences": {"style": "technical"}
}
result = await route_query("Explain quantum computing", user_context)
```

## Response Format

```python
{
    "success": True,
    "query": "What is Python programming language?",
    "classification": {
        "category": "technical",
        "confidence": 0.8,
        "complexity": "simple",
        "intent": "factual",
        "keywords_found": ["python", "programming"]
    },
    "answer": "Python is a high-level, interpreted programming language...",
    "confidence": 0.85,
    "sources": [...],  # Retrieved documents
    "verification": {
        "verification_confidence": 0.9,
        "verified_sentences": [...],
        "unsupported_sentences": [...],
        "processing_time": 2.3
    },
    "processing_time": 5.2,
    "metadata": {
        "use_dynamic_selection": True,
        "search_time": 1.1,
        "verification_time": 2.3,
        "synthesis_time": 1.8,
        "total_documents": 15,
        "verified_facts": 8,
        "unsupported_claims": 2
    }
}
```

## Query Classification

The function classifies queries into categories:

- **Technical**: Programming, algorithms, APIs, databases, etc.
- **Academic**: Research, papers, citations, scholarly content
- **Business**: Market, revenue, strategy, management
- **Medical**: Health, treatment, diagnosis, medicine
- **Legal**: Law, court cases, contracts, regulations
- **News**: Current events, recent updates
- **General**: Default category for other queries

## Error Handling

The function includes comprehensive error handling:

```python
{
    "success": False,
    "error": "Search service unavailable",
    "query": "What is Python?",
    "processing_time": 1.2
}
```

## Integration with Services

### Search Service
- Uses `RetrievalAgent` from `services/search_service/retrieval_agent.py`
- Retrieves relevant documents using hybrid search
- Supports vector search, keyword search, and knowledge graph queries

### Factcheck Service
- Uses `FactCheckAgent` from `services/factcheck_service/factcheck_agent.py`
- Verifies claims against retrieved documents
- Includes temporal validation and source authenticity checks

### Synthesis Service
- Uses `SynthesisAgent` from `services/synthesis_service/synthesis_agent.py`
- Composes final answers from verified facts
- Includes citations and disclaimers

## Performance Considerations

- **Processing Time**: Typically 3-10 seconds depending on complexity
- **Token Budget**: Distributed across services (4000 for search, 2000 for verification, 3000 for synthesis)
- **Caching**: Results can be cached for similar queries
- **Concurrency**: Supports multiple concurrent requests

## Testing

Run the test script to verify functionality:

```bash
python test_route_query.py
```

## Configuration

### Environment Variables

```bash
# Enable dynamic model selection (local LLM vs API)
USE_DYNAMIC_SELECTION=true

# Logging level
LOG_LEVEL=INFO

# Service endpoints (if using external services)
SEARCH_SERVICE_URL=http://localhost:8001
FACTCHECK_SERVICE_URL=http://localhost:8002
SYNTHESIS_SERVICE_URL=http://localhost:8003
```

### Service Dependencies

The function requires the following services to be available:
- Search Service (RetrievalAgent)
- Factcheck Service (FactCheckAgent)  
- Synthesis Service (SynthesisAgent)
- LLM Client (for dynamic model selection)

## Advanced Usage

### Custom Classification

```python
# Override classification for specific queries
user_context = {
    "force_classification": "technical",
    "classification_confidence": 0.9
}
```

### Service-Specific Parameters

```python
user_context = {
    "search_params": {
        "top_k": 30,
        "search_type": "vector_only"
    },
    "verification_params": {
        "temporal_validation": True,
        "source_authenticity": True
    },
    "synthesis_params": {
        "style": "comprehensive",
        "include_citations": True
    }
}
```

## Monitoring and Logging

The function provides detailed logging:

```python
logger.info(f"Starting query routing for: {query[:100]}...")
logger.info(f"Query classified as: {query_classification}")
logger.info(f"Retrieved {len(documents)} documents")
logger.info(f"Verification completed with confidence: {confidence}")
logger.info(f"Query routing completed in {total_time:.3f}s")
```

## Troubleshooting

### Common Issues

1. **Service Unavailable**: Check if all required services are running
2. **Import Errors**: Ensure all service modules are properly installed
3. **Timeout Errors**: Increase timeout values for complex queries
4. **Memory Issues**: Reduce token budgets for resource-constrained environments

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
LOG_LEVEL=DEBUG
```

## Future Enhancements

- **Caching Layer**: Implement Redis-based caching for frequent queries
- **Load Balancing**: Add support for multiple service instances
- **Circuit Breaker**: Implement circuit breaker pattern for service resilience
- **Metrics Collection**: Add detailed performance metrics and monitoring
- **Custom Classifiers**: Support for custom query classification models 