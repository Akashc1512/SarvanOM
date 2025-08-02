# Enhanced Orchestrator LLM Selection Implementation

## Overview

This implementation provides intelligent LLM provider selection based on query classification and token limits, replacing the previous static provider selection with a dynamic, cost-optimized approach.

## Key Features

- **Modular Provider Selection**: `select_llm_provider()` method for transparent routing
- **Query Classification Integration**: Uses QueryClassifier for optimal provider selection
- **Token Limit Awareness**: Checks context + query size against provider limits
- **Intelligent Fallback Chain**: Ollama → HuggingFace → OpenAI with automatic fallback
- **Comprehensive Logging**: Tracks which model handled each query
- **Provider Health Monitoring**: Checks provider health before selection

## Provider Selection Logic

### Query Classification

The system classifies queries into three categories:

1. **Simple Factual** (`QueryType.SIMPLE_FACTUAL`)
   - Indicators: "what is", "who is", "when", "where", "how many", "define"
   - Provider Priority: Ollama → HuggingFace → OpenAI
   - Use Case: Basic factual questions, definitions, simple explanations

2. **Complex Synthesis** (`QueryType.COMPLEX_SYNTHESIS`)
   - Indicators: "analyze", "compare", "research", "study", "investigate", "synthesize"
   - Provider Priority: HuggingFace → OpenAI → Ollama
   - Use Case: Research questions, comparative analysis, complex reasoning

3. **Large Context** (`QueryType.LARGE_CONTEXT`)
   - Indicators: Long queries (>500 characters), high token requirements
   - Provider Priority: OpenAI → HuggingFace → Ollama
   - Use Case: Complex queries requiring extensive context

### Token Limits by Provider

| Provider | Max Context Tokens | Max Total Tokens | Cost | Use Case |
|----------|-------------------|------------------|------|----------|
| Ollama | 4,000 | 4,000 | Free | Simple factual queries |
| HuggingFace | 2,000 | 2,000 | Free | Research and synthesis |
| OpenAI | 16,000 | 16,000 | Paid | Large context, fallback |

## Implementation Details

### Enhanced LLM Client

The `EnhancedLLMClient` provides the core functionality:

```python
class EnhancedLLMClient:
    async def select_llm_provider(self, query: str, context_size: int = 0) -> LLMProvider:
        """Select the best LLM provider based on query classification and context size."""
        
    async def dispatch(self, query: str, context: Optional[str] = None, **kwargs) -> LLMResponse:
        """Dispatch a query to the best LLM provider with intelligent fallback."""
```

### Provider Interfaces

Each provider implements the `LLMProviderInterface`:

```python
class LLMProviderInterface(ABC):
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text with token limit awareness."""
        
    async def health_check(self) -> bool:
        """Check provider health."""
        
    def can_handle_request(self, request: LLMRequest) -> bool:
        """Check if provider can handle the request within token limits."""
```

### Orchestrator Integration

The orchestrator integrates the enhanced LLM client:

```python
class LeadOrchestrator:
    async def select_llm_provider(self, query: str, context_size: int = 0) -> LLMProvider:
        """Select the best LLM provider based on query classification and context size."""
        return await self.enhanced_llm_client.select_llm_provider(query, context_size)
```

## Usage Examples

### Basic Provider Selection

```python
# Initialize enhanced LLM client
client = EnhancedLLMClient()

# Select provider for simple factual query
provider = await client.select_llm_provider("What is Python?")
# Returns: LLMProvider.OLLAMA

# Select provider for complex synthesis
provider = await client.select_llm_provider("Analyze the impact of climate change")
# Returns: LLMProvider.HUGGINGFACE

# Select provider for large context
provider = await client.select_llm_provider("This is a very long query...", context_size=5000)
# Returns: LLMProvider.OPENAI
```

### Dispatch with Fallback

```python
# Dispatch query with automatic fallback
response = await client.dispatch(
    query="What is machine learning?",
    context="Additional context...",
    max_tokens=1000,
    temperature=0.2,
    query_id="user_query_123"
)

print(f"Provider used: {response.provider}")
print(f"Response: {response.content}")
print(f"Response time: {response.response_time_ms}ms")
```

### Orchestrator Integration

```python
# In the orchestrator
orchestrator = LeadOrchestrator()

# Select provider for synthesis
provider = await orchestrator.select_llm_provider(query, context_size=estimated_tokens)

# Log the selection
logger.info(f"Selected LLM Provider: {provider.value} for query: {query_id}")
```

## Fallback Chain

The system implements a robust fallback chain:

1. **Primary Selection**: Based on query classification
2. **Health Check**: Verify provider is available
3. **Token Limit Check**: Ensure provider can handle request
4. **Fallback Chain**: Try alternative providers if primary fails
5. **Error Handling**: Graceful degradation with comprehensive logging

### Fallback Logic

```python
# Primary provider fails
try:
    response = await primary_provider.generate_text(request)
except Exception as e:
    logger.warning(f"Primary provider failed: {e}")
    
    # Try fallback providers
    for fallback_provider in fallback_providers:
        try:
            response = await fallback_provider.generate_text(request)
            logger.info(f"Fallback successful using {fallback_provider.value}")
            return response
        except Exception as fallback_error:
            logger.error(f"Fallback provider also failed: {fallback_error}")
    
    # All providers failed
    raise Exception("All LLM providers failed")
```

## Logging and Transparency

The system provides comprehensive logging:

```
🔍 Query classified as: simple_factual
📊 Estimated tokens needed: 1500
🎯 Selected LLM Provider: Ollama for simple factual query
✅ Generated response using ollama in 125.5ms
Selected LLM Provider: ollama for query: abc123
```

### Log Format

- **Query Classification**: Shows how the query was classified
- **Token Estimation**: Estimated tokens needed for the request
- **Provider Selection**: Which provider was selected and why
- **Response Time**: How long the response took
- **Query ID**: Unique identifier for tracking

## Testing

### Test Coverage

The implementation includes comprehensive tests:

- ✅ **Query Classification**: Tests correct provider selection based on query type
- ✅ **Token Limit Awareness**: Tests token overflow detection and fallback
- ✅ **Provider Health Monitoring**: Tests health check functionality
- ✅ **Fallback Chain**: Tests provider failure and automatic fallback
- ✅ **Concurrent Requests**: Tests handling of multiple simultaneous requests
- ✅ **Edge Cases**: Tests empty queries, special characters, etc.

### Running Tests

```bash
# Run all LLM selection tests
pytest test_orchestrator_llm_selection.py -v --asyncio-mode=auto

# Run specific test
pytest test_orchestrator_llm_selection.py::TestOrchestratorLLMSelection::test_query_classification_simple_factual -v
```

## Configuration

### Environment Variables

```bash
# Ollama Configuration
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# HuggingFace Configuration
HUGGINGFACE_API_KEY=your_api_key
HUGGINGFACE_MODEL=microsoft/DialoGPT-medium

# OpenAI Configuration (fallback)
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-3.5-turbo
```

### Provider Configuration

```python
# Example provider configuration
ollama_config = ProviderConfig(
    name=LLMProvider.OLLAMA,
    base_url="http://localhost:11434",
    api_key=None,
    models=["llama3.2:3b", "mistral:7b"],
    timeout=60,
    token_limits=ProviderTokenLimits(
        max_context_tokens=4000,
        max_total_tokens=4000,
        cost_per_1k_tokens=0.0,
        is_free=True
    )
)
```

## Performance Considerations

### Token Estimation

The system uses rough token estimation:

```python
def estimate_tokens(self, text: str) -> int:
    """Estimate token count (rough approximation)."""
    return len(text) // 4  # 1 token ≈ 4 characters
```

### Health Monitoring

Providers are checked before use:

```python
async def health_check(self) -> bool:
    """Check if provider is healthy and available."""
    try:
        # Provider-specific health check
        return await self._check_provider_health()
    except Exception:
        return False
```

### Statistics Tracking

The system tracks provider usage:

```python
def get_provider_stats(self) -> Dict[str, Any]:
    """Get comprehensive provider statistics."""
    return {
        "ollama": {
            "calls": 150,
            "success": 145,
            "failures": 5,
            "success_rate": 0.967,
            "avg_time_ms": 125.5
        },
        "huggingface": {
            "calls": 75,
            "success": 72,
            "failures": 3,
            "success_rate": 0.960,
            "avg_time_ms": 200.0
        }
    }
```

## Error Handling

### Graceful Degradation

The system handles various failure scenarios:

1. **Provider Unavailable**: Automatic fallback to next provider
2. **Token Limit Exceeded**: Skip to provider with higher limits
3. **Network Issues**: Retry with exponential backoff
4. **All Providers Failed**: Return meaningful error message

### Error Recovery

```python
try:
    response = await client.dispatch(query)
except Exception as e:
    logger.error(f"All providers failed: {e}")
    # Return fallback response or error message
    return create_error_response("Unable to process query at this time")
```

## Monitoring and Observability

### Health Checks

```python
# Check all providers
health_status = await client.health_check()
print(health_status)
# Output:
# {
#     "ollama": {"status": "healthy", "info": {...}},
#     "huggingface": {"status": "healthy", "info": {...}},
#     "openai": {"status": "healthy", "info": {...}}
# }
```

### Provider Statistics

```python
# Get usage statistics
stats = client.get_provider_stats()
print(f"Ollama success rate: {stats['ollama']['success_rate']:.2%}")
print(f"Average response time: {stats['ollama']['avg_time_ms']:.1f}ms")
```

## Integration with Existing Systems

### Synthesis Agent Integration

The synthesis agent now uses the enhanced LLM client:

```python
# In synthesis_agent.py
from shared.core.llm_client_enhanced import EnhancedLLMClient

async def _synthesize_answer(self, verified_facts, query, params):
    llm_client = EnhancedLLMClient()
    
    response = await llm_client.dispatch(
        query=synthesis_prompt,
        context=None,
        max_tokens=max_length,
        temperature=0.2,
        system_message=system_message,
        query_id=f"synthesis_{hash(query) % 10000}"
    )
    
    return response.content
```

### Orchestrator Integration

The orchestrator provides a unified interface:

```python
# In lead_orchestrator.py
async def select_llm_provider(self, query: str, context_size: int = 0) -> LLMProvider:
    """Select the best LLM provider based on query classification and context size."""
    return await self.enhanced_llm_client.select_llm_provider(query, context_size)
```

## Future Enhancements

### Planned Features

1. **Dynamic Token Estimation**: More accurate token counting
2. **Provider Performance Learning**: Adapt selection based on historical performance
3. **Cost Optimization**: Track and optimize for cost efficiency
4. **Custom Provider Support**: Easy addition of new providers
5. **Advanced Fallback Strategies**: More sophisticated fallback logic

### Performance Optimizations

1. **Connection Pooling**: Reuse connections for better performance
2. **Caching**: Cache provider health status and selection decisions
3. **Parallel Health Checks**: Check multiple providers simultaneously
4. **Predictive Selection**: Use ML to predict optimal provider

## Conclusion

The Enhanced Orchestrator LLM Selection implementation provides a robust, intelligent system for selecting the best LLM provider based on query characteristics and system constraints. It offers:

- **Intelligent Routing**: Automatic selection based on query type
- **Cost Optimization**: Prioritizes free providers when appropriate
- **Robust Fallback**: Graceful handling of provider failures
- **Comprehensive Monitoring**: Full visibility into provider usage
- **Easy Integration**: Seamless integration with existing orchestrator

The system is production-ready with comprehensive testing, error handling, and monitoring capabilities, making it suitable for high-volume, cost-sensitive applications. 