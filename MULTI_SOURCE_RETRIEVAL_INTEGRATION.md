# Multi-Source Retrieval Integration

## Overview

This document describes the integration of multi-source retrieval capabilities in the `RetrievalAgent`, which now combines vector search, keyword search via Meilisearch, and graph-based search via ArangoDB to provide comprehensive information retrieval.

## Architecture

### Components

1. **Vector Search** - Semantic similarity search using embeddings
2. **Meilisearch Keyword Search** - Fast keyword-based search engine
3. **ArangoDB Graph Search** - Knowledge graph queries for entity relationships
4. **Elasticsearch** - Legacy keyword search (fallback)
5. **Web Search** - External web search via SERP APIs

### Data Flow

```
Query Input
    ↓
Query Analysis (Intent, Complexity, Entities)
    ↓
Strategy Selection
    ↓
Parallel Retrieval Execution
    ↓
Result Merging & Deduplication
    ↓
Diversity Filtering
    ↓
LLM Reranking (for complex queries)
    ↓
Unified Results
```

## Implementation Details

### 1. Multi-Source Client Initialization

The `RetrievalAgent` now initializes multiple search clients:

```python
def _initialize_multi_source_clients(self):
    """Initialize Meilisearch and ArangoDB clients."""
    # Meilisearch engine
    meilisearch_url = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
    meilisearch_master_key = os.getenv("MEILISEARCH_MASTER_KEY")
    self.meilisearch_engine = MeilisearchEngine(meilisearch_url, meilisearch_master_key)
    
    # ArangoDB knowledge graph agent
    self.arangodb_agent = ArangoDBKnowledgeGraphAgent()
```

### 2. Meilisearch Integration

**Purpose**: Fast keyword-based search with typo tolerance and ranking

**Features**:
- Lightning-fast search engine written in Rust
- Typo tolerance and fuzzy matching
- Configurable ranking rules
- Filterable attributes

**Usage**:
```python
async def meilisearch_search(self, query: str, top_k: int = 20) -> SearchResult:
    """Perform keyword search using Meilisearch."""
    results = await self.meilisearch_engine.search(query, top_k)
    # Convert to Document objects and return
```

### 3. ArangoDB Graph Search Integration

**Purpose**: Knowledge graph queries for entity relationships and semantic connections

**Features**:
- Entity extraction from queries
- Relationship discovery between entities
- Path finding in knowledge graph
- Confidence scoring for graph results

**Usage**:
```python
async def arangodb_graph_search(self, query: str, entities: List[str] = None, top_k: int = 20) -> SearchResult:
    """Perform graph-based search using ArangoDB knowledge graph agent."""
    kg_result = await self.arangodb_agent.query(query, query_type="entity_relationship")
    # Convert entities and relationships to Document objects
```

### 4. Enhanced Hybrid Retrieval

The `hybrid_retrieve` method now orchestrates multiple retrieval strategies:

```python
async def hybrid_retrieve(self, query: str, entities: List[str] = None) -> SearchResult:
    # 1. Query analysis for intelligent strategy selection
    query_analysis = await self.query_intelligence.analyze_query(query)
    
    # 2. Determine retrieval strategies
    retrieval_strategies = self._determine_retrieval_strategies(intent, complexity, entities)
    
    # 3. Execute strategies in parallel
    retrieval_tasks = []
    if "vector" in retrieval_strategies:
        retrieval_tasks.append(self.vector_search(query, top_k=20))
    if "meilisearch" in retrieval_strategies:
        retrieval_tasks.append(self.meilisearch_search(query, top_k=20))
    if "arangodb_graph" in retrieval_strategies:
        retrieval_tasks.append(self.arangodb_graph_search(query, entities, top_k=20))
    
    # 4. Merge and deduplicate results
    results = await asyncio.gather(*retrieval_tasks, return_exceptions=True)
    merged_documents = await self._merge_and_deduplicate(successful_results)
    
    # 5. Apply diversity constraints and reranking
    diverse_documents = self._apply_diversity_constraints(merged_documents)
    if complexity == "complex":
        diverse_documents = await self._llm_rerank(query, diverse_documents)
```

### 5. Strategy Selection Logic

The system intelligently selects retrieval strategies based on:

- **Query Intent**: factual, comparative, procedural, analytical, opinion
- **Query Complexity**: simple, moderate, complex
- **Available Entities**: extracted named entities from the query

```python
def _determine_retrieval_strategies(self, intent: str, complexity: str, entities: List[str]) -> List[str]:
    strategies = []
    
    # Base strategies for all queries
    strategies.append("vector")
    strategies.append("keyword")
    strategies.append("meilisearch")  # Add Meilisearch for all queries
    
    # Add ArangoDB graph search if entities are available
    if entities:
        strategies.append("arangodb_graph")
    
    # Add web search for factual and comparative queries
    if intent in ["factual", "comparative"]:
        strategies.append("web")
    
    return strategies
```

### 6. Result Merging and Deduplication

The system merges results from multiple sources while removing duplicates:

```python
async def _merge_and_deduplicate(self, results: List[SearchResult]) -> List[Document]:
    # Collect all documents
    all_documents = []
    for result in results:
        all_documents.extend(result.documents)
    
    # Deduplicate by content similarity
    unique_documents = []
    seen_contents = set()
    
    for doc in all_documents:
        content_hash = hashlib.md5(doc.content.lower().encode()).hexdigest()
        if content_hash not in seen_contents:
            seen_contents.add(content_hash)
            unique_documents.append(doc)
        else:
            # Keep higher scoring document if content is similar
            existing_doc = next((d for d in unique_documents 
                               if hashlib.md5(d.content.lower().encode()).hexdigest() == content_hash), None)
            if existing_doc and doc.score > existing_doc.score:
                unique_documents.remove(existing_doc)
                unique_documents.append(doc)
    
    # Sort by score
    unique_documents.sort(key=lambda x: x.score, reverse=True)
    return unique_documents
```

## Configuration

### Environment Variables

```bash
# Meilisearch Configuration
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_MASTER_KEY=your_master_key_here

# ArangoDB Configuration
ARANGO_URL=http://localhost:8529
ARANGO_USERNAME=root
ARANGO_PASSWORD=your_password
ARANGO_DATABASE=knowledge_graph

# Vector Database Configuration
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=knowledge-base

# Elasticsearch Configuration (fallback)
ELASTICSEARCH_HOST=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your_password
```

### Agent Configuration

```python
config = {
    "vector_db": {
        "url": "http://localhost:6333",
        "collection_name": "knowledge_base",
    },
    "elasticsearch": {
        "hosts": ["http://localhost:9200"],
        "index_name": "knowledge_base",
    },
    "knowledge_graph": {
        "endpoint_url": "http://localhost:7200/repositories/knowledge"
    },
    "cache_similarity_threshold": 0.92,
    "max_results_per_search": 20,
    "diversity_threshold": 0.3,
}
```

## Usage Examples

### Basic Usage

```python
from services.search_service.retrieval_agent import RetrievalAgent

# Initialize agent
agent = RetrievalAgent()

# Perform hybrid retrieval
result = await agent.hybrid_retrieve("What is machine learning?")

# Access results
for doc in result.documents:
    print(f"Source: {doc.source}, Score: {doc.score}")
    print(f"Content: {doc.content}")
```

### Individual Source Queries

```python
# Meilisearch keyword search
meili_result = await agent.meilisearch_search("artificial intelligence", top_k=10)

# ArangoDB graph search
arango_result = await agent.arangodb_graph_search("machine learning", entities=["ML", "AI"])

# Vector search
vector_result = await agent.vector_search("deep learning", top_k=10)
```

## Testing

Run the test script to verify the integration:

```bash
python test_multi_source_retrieval.py
```

The test script validates:
- Entity extraction functionality
- Individual source retrieval
- Hybrid retrieval with result merging
- Error handling and fallbacks

## Performance Considerations

### Parallel Execution
- All retrieval strategies execute in parallel using `asyncio.gather()`
- Failed strategies don't block successful ones
- Timeout handling prevents hanging queries

### Caching
- Semantic cache for similar queries
- Result caching to avoid redundant searches
- Embedding cache for vector operations

### Resource Management
- Connection pooling for database clients
- Graceful degradation when services are unavailable
- Circuit breaker pattern for external APIs

## Error Handling

The system includes comprehensive error handling:

1. **Service Unavailability**: Graceful fallback to available sources
2. **Timeout Handling**: Configurable timeouts for each retrieval strategy
3. **Partial Failures**: Continue with successful results even if some strategies fail
4. **Mock Data**: Fallback to mock data when external services are unavailable

## Monitoring and Metrics

The system provides detailed metadata for monitoring:

```python
result.metadata = {
    "intent": "factual",
    "complexity": "moderate", 
    "entities": ["machine learning", "AI"],
    "strategies_used": ["vector", "meilisearch", "arangodb_graph"],
    "query_analysis": {...},
    "processing_time_ms": 150,
    "total_hits": 25
}
```

## Future Enhancements

1. **Dynamic Weighting**: Adjust strategy weights based on query type and historical performance
2. **Learning-based Selection**: Use ML to predict optimal strategy combinations
3. **Real-time Adaptation**: Adjust strategies based on current system load
4. **Advanced Fusion**: Implement more sophisticated result fusion algorithms
5. **Cross-source Validation**: Validate results across multiple sources for confidence scoring

## Troubleshooting

### Common Issues

1. **Meilisearch Connection Failed**
   - Check if Meilisearch is running on the configured port
   - Verify master key configuration
   - Check network connectivity

2. **ArangoDB Connection Failed**
   - Ensure ArangoDB is running and accessible
   - Verify database credentials
   - Check if knowledge graph collections exist

3. **No Results Returned**
   - Verify that search indexes are populated with data
   - Check query analysis and entity extraction
   - Review strategy selection logic

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Conclusion

The multi-source retrieval integration provides a robust, scalable solution for comprehensive information retrieval. By combining vector search, keyword search, and graph-based search, the system can handle diverse query types and provide high-quality, relevant results across multiple domains. 