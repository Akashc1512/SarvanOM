# Dynamic Model Selection Guide

## Overview

The Dynamic Model Selection feature intelligently routes queries to the most appropriate LLM model based on query characteristics, optimizing for both performance and cost efficiency. This system analyzes query complexity and type to choose between different models (e.g., GPT-3.5 vs GPT-4, OpenAI vs Anthropic Claude) automatically.

## Key Features

### 1. Intelligent Model Selection
- **Query Classification**: Analyzes query type (general_factual, code, analytical, etc.)
- **Complexity Assessment**: Determines query complexity (simple, moderate, complex)
- **Cost Optimization**: Balances performance with cost efficiency
- **Fallback Mechanisms**: Automatic fallback to alternative models if primary fails

### 2. Model Tiers
- **Fast Tier**: Cost-effective models for simple queries (GPT-3.5-turbo, GPT-4o-mini, Claude-3-haiku)
- **Balanced Tier**: Balanced models for moderate complexity (GPT-4, GPT-4o, Claude-3-sonnet)
- **Powerful Tier**: High-performance models for complex queries (GPT-4-turbo, Claude-3-opus)
- **Specialized Tier**: Domain-specific models (code-davinci for programming)

### 3. Query-Based Routing
- **Simple Queries**: Use fast, cost-effective models
- **Complex Queries**: Use powerful models for better reasoning
- **Code Queries**: Prefer models with code capabilities
- **Analytical Queries**: Use models with strong reasoning abilities

## Implementation

### Core Components

#### 1. DynamicModelSelector (`shared/core/model_selector.py`)
```python
from shared.core.model_selector import get_model_selector

# Initialize the model selector
model_selector = get_model_selector()

# Select optimal model for a query
result = await model_selector.select_model(
    query="How do I implement authentication in React?",
    estimated_tokens=1000
)

print(f"Selected model: {result.selected_model}")
print(f"Model tier: {result.model_tier.value}")
print(f"Estimated cost: ${result.estimated_cost:.4f}")
print(f"Reasoning: {result.reasoning}")
```

#### 2. Enhanced LLM Client (`shared/core/llm_client_v3.py`)
```python
from shared.core.llm_client_v3 import get_llm_client_v3

# Initialize LLM client
llm_client = get_llm_client_v3()

# Generate text with dynamic model selection
response = await llm_client.generate_text(
    prompt="Answer this question: What is Python?",
    max_tokens=500,
    temperature=0.2,
    query="What is Python?",  # Original query for model selection
    use_dynamic_selection=True
)
```

#### 3. Integration with Agents
```python
# Synthesis Agent uses dynamic selection
response = await llm_client._client.generate_text(
    prompt=synthesis_prompt,
    max_tokens=max_length,
    temperature=0.2,
    query=query,  # Pass original query for model selection
    use_dynamic_selection=True
)

# Citation Agent uses dynamic selection
citation_query = f"Format citations in {citation_format} style"
response = await llm_client._client.generate_text(
    prompt=citation_prompt,
    max_tokens=1500,
    temperature=0.1,
    query=citation_query,
    use_dynamic_selection=True
)
```

### Model Selection Logic

#### 1. Query Classification
The system uses the QueryClassifier to categorize queries:
- **general_factual**: Basic factual questions
- **code**: Programming and technical questions
- **analytical**: Analysis and investigation questions
- **comparative**: Comparison and evaluation questions
- **procedural**: How-to and step-by-step questions
- **creative**: Creative and innovative questions
- **opinion**: Opinion and subjective questions

#### 2. Complexity Assessment
Queries are classified by complexity:
- **Simple**: Basic queries requiring minimal processing
- **Moderate**: Medium complexity queries
- **Complex**: Advanced queries requiring comprehensive processing

#### 3. Tier Selection
Based on query characteristics:
```python
# Simple queries -> Fast tier
if complexity == QueryComplexity.SIMPLE:
    return ModelTier.FAST

# Complex queries -> Powerful tier
elif complexity == QueryComplexity.COMPLEX:
    return ModelTier.POWERFUL

# Category-specific preferences
elif category == QueryCategory.CODE:
    return ModelTier.BALANCED  # Good for code, but not always needed
elif category == QueryCategory.ANALYTICAL:
    return ModelTier.POWERFUL  # Requires strong reasoning
```

#### 4. Model Scoring
Models are scored based on:
- **Capability match**: Does the model support the query type?
- **Cost efficiency**: Lower cost models preferred when appropriate
- **Token capacity**: Can the model handle the estimated token count?
- **Provider reliability**: Historical reliability of the provider

### Configuration

#### Model Configuration (`config/model_selection.json`)
```json
{
  "model_selection": {
    "enabled": true,
    "default_behavior": "dynamic",
    "fallback_behavior": "fast",
    "cost_optimization": {
      "enabled": true,
      "max_cost_per_query": 0.20,
      "prefer_fast_models": true
    },
    "complexity_thresholds": {
      "simple": {
        "max_tokens": 1000,
        "preferred_tier": "fast",
        "max_cost_per_query": 0.01
      },
      "moderate": {
        "max_tokens": 3000,
        "preferred_tier": "balanced",
        "max_cost_per_query": 0.05
      },
      "complex": {
        "max_tokens": 8000,
        "preferred_tier": "powerful",
        "max_cost_per_query": 0.20
      }
    }
  }
}
```

#### Environment Variables
```bash
# Enable/disable dynamic model selection
DYNAMIC_MODEL_SELECTION=true

# Cost optimization settings
MAX_COST_PER_QUERY=0.20
PREFER_FAST_MODELS=true

# Fallback settings
MAX_RETRIES=3
RETRY_DELAY_MS=1000
```

## Usage Examples

### 1. Basic Usage
```python
from shared.core.model_selector import get_model_selector

model_selector = get_model_selector()

# Simple query - should use fast model
result = await model_selector.select_model("What is Python?", estimated_tokens=500)
# Expected: gpt-3.5-turbo or gpt-4o-mini

# Complex query - should use powerful model
result = await model_selector.select_model(
    "Analyze the impact of AI on software development", 
    estimated_tokens=2000
)
# Expected: gpt-4-turbo or claude-3-opus

# Code query - should use balanced model
result = await model_selector.select_model(
    "How do I implement authentication in React?", 
    estimated_tokens=1000
)
# Expected: gpt-4 or claude-3-sonnet
```

### 2. LLM Client Integration
```python
from shared.core.llm_client_v3 import get_llm_client_v3

llm_client = get_llm_client_v3()

# Automatic model selection
response = await llm_client.generate_text(
    prompt="Explain machine learning",
    max_tokens=500,
    query="Explain machine learning",  # For model selection
    use_dynamic_selection=True
)

# Manual model selection (fallback)
response = await llm_client.generate_text(
    prompt="Explain machine learning",
    max_tokens=500,
    use_dynamic_selection=False  # Use default model
)
```

### 3. Agent Integration
```python
# Synthesis Agent automatically uses dynamic selection
synthesis_result = await synthesis_agent.process_task({
    "verified_facts": facts,
    "query": "What are the benefits of microservices?",
    "synthesis_params": {"max_length": 1000}
})

# Citation Agent uses dynamic selection for formatting
citation_result = await citation_agent.process_task({
    "answer": answer_with_placeholders,
    "sources": sources,
    "citation_format": "APA"
})
```

## Benefits

### 1. Cost Optimization
- **Reduced costs**: Use cheaper models for simple queries
- **Efficient resource usage**: Match model capability to query needs
- **Predictable pricing**: Estimate costs before generation

### 2. Performance Improvement
- **Faster responses**: Use faster models for simple queries
- **Better quality**: Use powerful models for complex queries
- **Optimal routing**: Match query type to model capabilities

### 3. Reliability Enhancement
- **Automatic fallbacks**: Try alternative models if primary fails
- **Provider diversity**: Distribute load across multiple providers
- **Graceful degradation**: Fall back to simpler models if needed

### 4. Monitoring and Analytics
- **Selection tracking**: Monitor which models are used for which queries
- **Performance metrics**: Track response times and success rates
- **Cost analysis**: Monitor spending patterns and optimization opportunities

## Testing

### Test Script
Run the comprehensive test suite:
```bash
python test_dynamic_model_selection.py
```

### Test Coverage
- ✅ Simple query model selection
- ✅ Complex query model selection
- ✅ Code query model selection
- ✅ Analytical query model selection
- ✅ LLM generation with dynamic selection
- ✅ Fallback mechanisms
- ✅ Cost optimization
- ✅ Performance monitoring

### Example Test Results
```
Testing simple queries...
Query: 'What is Python?' -> gpt-3.5-turbo (fast)
Query: 'How do I install pip?' -> gpt-4o-mini (fast)

Testing complex queries...
Query: 'Analyze the impact of artificial intelligence...' -> gpt-4-turbo (powerful)
Query: 'Compare and contrast different approaches...' -> claude-3-opus (powerful)

Testing code queries...
Query: 'How do I implement authentication in React?' -> gpt-4 (balanced)
Query: 'Write a Python function to sort...' -> claude-3-sonnet (balanced)
```

## Monitoring and Metrics

### Selection Metrics
```python
metrics = model_selector.get_selection_metrics()

print(f"Total selections: {metrics['total_selections']}")
print(f"Tier distribution: {metrics['tier_distribution']}")
print(f"Average selection time: {metrics['avg_selection_time_ms']:.2f}ms")
print(f"Total estimated cost: ${metrics['total_estimated_cost']:.4f}")
print(f"Average confidence: {metrics['avg_confidence']:.2f}")
```

### Performance Monitoring
- **Selection time**: How long model selection takes
- **Success rate**: Percentage of successful generations
- **Cost tracking**: Estimated vs actual costs
- **Model usage**: Distribution of model selections

## Best Practices

### 1. Query Analysis
- Provide clear, descriptive queries for better classification
- Include context when possible
- Use specific terminology for technical queries

### 2. Cost Management
- Set appropriate cost thresholds
- Monitor usage patterns
- Adjust preferences based on budget constraints

### 3. Fallback Strategy
- Always have fallback models configured
- Test fallback mechanisms regularly
- Monitor fallback usage patterns

### 4. Performance Optimization
- Cache model selections for similar queries
- Monitor selection performance
- Optimize thresholds based on usage patterns

## Troubleshooting

### Common Issues

#### 1. Model Selection Fails
```python
# Check if model selector is properly initialized
model_selector = get_model_selector()
print(f"Available models: {list(model_selector.model_configs.keys())}")
```

#### 2. High Costs
```python
# Adjust cost thresholds
model_selector.selection_thresholds["complexity_thresholds"]["complex"]["max_cost_per_query"] = 0.10
```

#### 3. Poor Performance
```python
# Check model availability and health
health_status = await llm_client.health_check()
print(f"Provider health: {health_status}")
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger("shared.core.model_selector").setLevel(logging.DEBUG)

# Test with specific tier
result = await model_selector.select_model(
    query="Test query",
    force_tier=ModelTier.POWERFUL
)
```

## Future Enhancements

### 1. Advanced Features
- **Learning-based selection**: Use historical performance data
- **Real-time optimization**: Adjust based on current performance
- **Custom model configurations**: User-defined model preferences

### 2. Integration Features
- **A/B testing**: Compare model performance
- **Performance analytics**: Detailed performance metrics
- **Automated optimization**: Self-tuning selection parameters

### 3. Provider Support
- **Additional providers**: Google, Azure, local models
- **Specialized models**: Domain-specific model selection
- **Hybrid approaches**: Combine multiple models for complex queries

## Conclusion

The Dynamic Model Selection feature provides intelligent, cost-effective routing of queries to the most appropriate LLM models. By analyzing query characteristics and automatically selecting optimal models, it significantly improves both performance and cost efficiency while maintaining high-quality responses.

The system is designed to be:
- **Intelligent**: Automatically selects the best model for each query
- **Cost-effective**: Optimizes for cost while maintaining quality
- **Reliable**: Includes comprehensive fallback mechanisms
- **Configurable**: Easily adjustable thresholds and preferences
- **Monitorable**: Comprehensive metrics and analytics

This implementation aligns with best practices for multi-model orchestration and provides a solid foundation for scalable, efficient LLM-based applications. 