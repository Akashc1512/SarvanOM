# QueryClassifier Guide

## Overview

The QueryClassifier is a utility that analyzes user queries and categorizes them for intelligent routing in the Universal Knowledge Platform. It uses heuristics and regex patterns to classify queries into categories that guide the orchestrator in choosing appropriate agents and data sources.

## Features

### Query Categories

The QueryClassifier supports the following query categories:

1. **`general_factual`** - Basic factual questions (default fallback)
2. **`code`** - Programming and technical questions
3. **`knowledge_graph`** - Relationship and entity-focused questions
4. **`analytical`** - Analysis and investigation questions
5. **`comparative`** - Comparison and evaluation questions
6. **`procedural`** - How-to and step-by-step questions
7. **`creative`** - Creative and innovative questions
8. **`opinion`** - Opinion and subjective questions

### Complexity Levels

- **`simple`** - Basic queries requiring minimal processing
- **`moderate`** - Medium complexity queries
- **`complex`** - Advanced queries requiring comprehensive processing

### Classification Features

- **Pattern Matching**: Uses regex patterns to identify query characteristics
- **Confidence Scoring**: Provides confidence levels for classifications
- **Agent Suggestions**: Recommends appropriate agents for each query type
- **Routing Hints**: Provides execution strategy and priority recommendations
- **Batch Processing**: Supports classifying multiple queries at once

## Usage

### Basic Usage

```python
from shared.core.query_classifier import QueryClassifier

# Initialize the classifier
classifier = QueryClassifier()

# Classify a single query
classification = await classifier.classify_query("How to implement authentication in React?")

print(f"Category: {classification.category.value}")
print(f"Confidence: {classification.confidence}")
print(f"Complexity: {classification.complexity.value}")
print(f"Suggested Agents: {classification.suggested_agents}")
```

### Integration with LeadOrchestrator

The QueryClassifier is automatically integrated into the LeadOrchestrator:

```python
from shared.core.agents.lead_orchestrator import LeadOrchestrator
from shared.core.agents.base_agent import QueryContext

# Initialize orchestrator (includes QueryClassifier)
orchestrator = LeadOrchestrator()

# Create query context
context = QueryContext(query="What is the relationship between ML and AI?")

# Analyze and plan (uses QueryClassifier internally)
plan = await orchestrator.analyze_and_plan(context)

print(f"Execution Pattern: {plan['execution_pattern']}")
print(f"Category: {plan['primary_category']}")
print(f"Priority: {plan['priority_level']}")
```

## Pattern Examples

### Knowledge Graph Patterns

Queries containing phrases like:
- "related to", "relationship between", "connection between"
- "how are", "what connects", "what links"
- "entity", "entities", "concept", "ontology"
- "influence", "impact", "effect", "cause"
- "similar", "different", "compare", "contrast"

**Example**: "What is the relationship between machine learning and artificial intelligence?"

### Code Patterns

Queries containing:
- Programming languages: "python", "javascript", "java", "c++"
- Technical terms: "code", "programming", "algorithm", "function"
- Frameworks: "react", "angular", "vue", "django"
- Development tools: "git", "docker", "kubernetes"
- Technical concepts: "api", "database", "authentication"

**Example**: "How to implement a binary search tree in Python?"

### Analytical Patterns

Queries containing:
- Analysis words: "analyze", "examine", "investigate", "study"
- Causal words: "why", "what causes", "what leads to"
- Problem-solving: "problem", "issue", "challenge", "solution"

**Example**: "Why does machine learning require large datasets?"

## Classification Results

### QueryClassification Object

```python
@dataclass
class QueryClassification:
    category: QueryCategory          # The primary category
    confidence: float               # Confidence score (0.0-1.0)
    complexity: QueryComplexity     # Complexity level
    detected_patterns: List[str]    # Patterns that matched
    suggested_agents: List[str]     # Recommended agents
    routing_hints: Dict[str, Any]  # Routing recommendations
    timestamp: datetime            # Classification timestamp
```

### Routing Hints

The classifier provides detailed routing hints:

```python
routing_hints = {
    "primary_category": "knowledge_graph",
    "complexity_level": "moderate",
    "execution_strategy": "scatter_gather",
    "priority_level": "medium",
    "estimated_tokens": 1000,
    "cache_strategy": "conservative",
    "graph_queries": True,           # Category-specific hints
    "entity_extraction": True,
    "relationship_focus": True
}
```

## Execution Strategies

Based on classification, the orchestrator chooses execution strategies:

- **`pipeline`** - Full sequential processing (complex queries)
- **`fork_join`** - Parallel processing (analytical/comparative queries)
- **`scatter_gather`** - Simple parallel processing (simple queries)

## Agent Recommendations

The classifier suggests appropriate agents:

- **Base agents**: `retrieval`, `synthesis` (all queries)
- **Analytical queries**: Add `fact_check`, `citation`
- **Complex queries**: Add `fact_check`, `citation`
- **Code queries**: Focus on `retrieval`, `synthesis`
- **Knowledge graph queries**: Focus on `retrieval`, `synthesis`

## Performance

### Processing Time
- Single query classification: ~0.5ms
- Batch classification: ~2-5ms per query
- Memory usage: Minimal (pattern storage only)

### Accuracy
- High confidence (>0.7): Very reliable classification
- Medium confidence (0.4-0.7): Good classification
- Low confidence (<0.4): May need manual review

## Configuration

### Customizing Patterns

You can extend the classifier with custom patterns:

```python
classifier = QueryClassifier()

# Add custom patterns (if needed)
classifier.custom_patterns = [
    r'\b(custom_pattern|specific_term)\b'
]
```

### Pattern Statistics

Get statistics about available patterns:

```python
stats = classifier.get_classification_stats()
print(f"Total patterns: {stats['total_patterns']}")
print(f"Complexity indicators: {stats['complexity_indicators']}")
```

## Testing

Run the test script to see the classifier in action:

```bash
python test_query_classifier.py
```

This will test:
- Various query types
- Classification accuracy
- Integration with LeadOrchestrator
- Batch processing
- Pattern matching

## Integration Points

### LeadOrchestrator Integration

The QueryClassifier is automatically integrated into the LeadOrchestrator's `analyze_and_plan` method:

1. **Query Analysis**: Classifies incoming queries
2. **Execution Planning**: Uses classification for routing decisions
3. **Agent Selection**: Suggests appropriate agents
4. **Strategy Selection**: Chooses execution patterns
5. **Priority Assignment**: Sets processing priorities

### API Integration

The classification results are included in API responses:

```json
{
  "answer": "...",
  "confidence": 0.85,
  "classification": {
    "category": "knowledge_graph",
    "confidence": 0.57,
    "complexity": "moderate",
    "suggested_agents": ["retrieval", "synthesis"],
    "routing_hints": {
      "execution_strategy": "scatter_gather",
      "priority_level": "medium"
    }
  }
}
```

## Best Practices

### Query Design

1. **Be Specific**: Clear, specific queries get better classification
2. **Use Keywords**: Include relevant technical terms
3. **Avoid Ambiguity**: Unclear queries may get low confidence scores

### System Integration

1. **Monitor Confidence**: Low confidence queries may need manual review
2. **Track Performance**: Monitor classification accuracy over time
3. **Update Patterns**: Regularly update patterns based on new query types

### Error Handling

```python
try:
    classification = await classifier.classify_query(query)
    if classification.confidence < 0.3:
        # Handle low confidence classification
        logger.warning(f"Low confidence classification: {classification.category}")
except Exception as e:
    # Fallback to default classification
    logger.error(f"Classification failed: {e}")
```

## Future Enhancements

### Planned Features

1. **Machine Learning**: Train on real query data for better accuracy
2. **Dynamic Patterns**: Learn new patterns from user queries
3. **Multi-language Support**: Support for non-English queries
4. **Context Awareness**: Consider user context and history
5. **Real-time Learning**: Update patterns based on feedback

### Extensibility

The QueryClassifier is designed to be easily extensible:

- Add new categories by extending `QueryCategory` enum
- Add new patterns by updating pattern lists
- Customize routing logic by modifying suggestion methods
- Integrate with external classification services

## Troubleshooting

### Common Issues

1. **Low Confidence Scores**
   - Check if query contains relevant keywords
   - Consider adding new patterns for your domain
   - Review query clarity and specificity

2. **Incorrect Classifications**
   - Verify pattern matching logic
   - Check for conflicting patterns
   - Review pattern specificity

3. **Performance Issues**
   - Monitor pattern complexity
   - Consider caching frequently used patterns
   - Optimize regex patterns for speed

### Debug Information

Enable debug logging to see classification details:

```python
import logging
logging.getLogger('shared.core.query_classifier').setLevel(logging.DEBUG)
```

This will show:
- Pattern matching results
- Confidence calculation details
- Routing decision logic
- Performance metrics 