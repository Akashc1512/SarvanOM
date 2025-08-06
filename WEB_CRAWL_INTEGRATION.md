# Web Crawl Integration for Retrieval Process

## Overview

This document describes the implementation of web crawling integration in the retrieval process. The system now includes web data via the CrawlerService as a fallback when local knowledge sources return insufficient or low-confidence results.

## Key Features

### ✅ **Intelligent Fallback System**
- Automatically triggers web crawling when local results are insufficient
- Configurable confidence thresholds for fallback decisions
- Respects timeouts to avoid unnecessary delays

### ✅ **Smart URL Generation**
- Uses SERP client to find relevant web pages
- Includes fallback URLs for common query types
- Validates URLs before crawling

### ✅ **Content Merging**
- Combines local and web-sourced content
- Re-ranks merged results for relevance
- Preserves source attribution

### ✅ **Pipeline Integration**
- Seamlessly integrates with the standardized multi-agent pipeline
- Passes web-sourced content to FactCheck and Synthesis agents
- Includes web sources in citations

## Architecture

### RetrievalAgent Enhancements

The RetrievalAgent now includes web crawling capabilities:

```python
class RetrievalAgent(BaseAgent):
    async def web_crawl_fallback(self, query: str, max_pages: int = 5, timeout: int = 30) -> SearchResult:
        """Perform web crawling as a fallback when local knowledge sources are insufficient."""
        
    def _should_use_web_crawl_fallback(self, local_results: List[Document], query: str, confidence_threshold: float = 0.6) -> bool:
        """Determine if web crawling fallback should be used."""
        
    async def _generate_search_urls(self, query: str) -> List[str]:
        """Generate search URLs for web crawling based on the query."""
```

### Fallback Decision Logic

The system uses multiple criteria to determine when web crawling is needed:

1. **No Local Results**: When local knowledge sources return no documents
2. **Low Confidence**: When average confidence score is below threshold (default: 0.6)
3. **Web Keywords**: When query contains web-related keywords ("latest", "recent", "news", etc.)
4. **Low Relevance**: When less than 50% of local documents are relevant to the query

### URL Generation Strategy

```python
def _get_fallback_urls(self, query: str) -> List[str]:
    """Get fallback URLs for common query types."""
    
    # Wikipedia for factual queries
    if any(word in query.lower() for word in ["what is", "definition", "meaning", "who is"]):
        fallback_urls.append(f"https://en.wikipedia.org/wiki/{topic}")
    
    # News sources for current events
    if any(word in query.lower() for word in ["latest", "recent", "news", "update", "today"]):
        fallback_urls.extend([
            "https://www.bbc.com/news",
            "https://www.reuters.com",
            "https://www.theguardian.com"
        ])
    
    # Technical documentation for technical queries
    if any(word in query.lower() for word in ["api", "documentation", "guide", "tutorial", "how to"]):
        fallback_urls.extend([
            "https://docs.python.org",
            "https://developer.mozilla.org",
            "https://stackoverflow.com"
        ])
```

## Implementation Details

### Web Crawl Fallback Process

```python
async def web_crawl_fallback(self, query: str, max_pages: int = 5, timeout: int = 30) -> SearchResult:
    """Perform web crawling as a fallback when local knowledge sources are insufficient."""
    
    # Get crawler service from service provider
    service_provider = get_service_provider()
    crawler_service = service_provider.get_crawler_service()
    
    # Generate search URLs from query
    search_urls = await self._generate_search_urls(query)
    
    documents = []
    for url in search_urls[:max_pages]:
        # Extract content from URL
        content_result = await crawler_service.extract_content(
            url=url,
            extract_images=False,  # Focus on text content
            extract_links=False
        )
        
        if content_result.get("success", False):
            content = content_result.get("data", {}).get("text_content", "")
            
            if content and len(content.strip()) > 100:  # Minimum content threshold
                # Create document from crawled content
                document = Document(
                    content=content,
                    score=0.8,  # Default confidence for web content
                    source=f"web_crawl:{url}",
                    metadata={
                        "url": url,
                        "title": title,
                        "crawl_timestamp": datetime.now().isoformat(),
                        "content_length": len(content),
                        "source_type": "web_crawl"
                    }
                )
                documents.append(document)
    
    return SearchResult(
        documents=documents,
        search_type="web_crawl",
        query_time_ms=query_time_ms,
        total_hits=len(documents),
        metadata={
            "crawl_sources": len(search_urls),
            "successful_crawls": len(documents),
            "timeout": timeout,
            "max_pages": max_pages
        }
    )
```

### Integration with Process Task

```python
async def process_task(self, task: Dict[str, Any], context: QueryContext) -> Dict[str, Any]:
    """Process a retrieval task with token optimization and web crawl fallback."""
    
    # Perform initial search based on type
    result = await self.hybrid_retrieve(query, entities)
    
    # Check if web crawl fallback is needed
    if enable_web_fallback and self._should_use_web_crawl_fallback(result.documents, query):
        logger.info("🔄 Local results insufficient, triggering web crawl fallback")
        
        # Perform web crawling with timeout
        web_result = await asyncio.wait_for(
            self.web_crawl_fallback(query, max_pages=5, timeout=web_fallback_timeout),
            timeout=web_fallback_timeout
        )
        
        # Merge web results with local results
        if web_result.documents:
            # Combine documents from both sources
            all_documents = result.documents + web_result.documents
            
            # Re-rank combined results
            reranked_documents = await self._llm_rerank(
                f"Query: {query}\n\nRank these documents by relevance:",
                all_documents
            )
            
            # Update result with merged documents
            result = SearchResult(
                documents=reranked_documents,
                search_type=f"{result.search_type}+web_crawl",
                query_time_ms=result.query_time_ms + web_result.query_time_ms,
                total_hits=len(reranked_documents),
                metadata={
                    **result.metadata,
                    "web_crawl_used": True,
                    "web_crawl_documents": len(web_result.documents),
                    "web_crawl_time_ms": web_result.query_time_ms,
                    "merged_sources": ["local", "web_crawl"]
                }
            )
```

### Pipeline Integration

The standardized orchestrator passes web crawl configuration to the retrieval agent:

```python
async def _execute_retrieval_stage(self, context: PipelineContext) -> bool:
    """Execute retrieval stage with parallel execution and web crawl fallback."""
    
    # Create QueryContext for the agent with web crawl configuration
    query_context = QueryContext(
        query=context.query,
        user_context=context.user_context,
        trace_id=context.trace_id,
        metadata={
            "enable_web_fallback": True,
            "web_fallback_timeout": 30,
            "max_web_pages": 5,
            "confidence_threshold": 0.6
        }
    )
    
    # Execute the agent using the standardized interface
    retrieval_result = await retrieval_agent.execute(query_context)
    
    # Check if web crawl was used
    metadata = retrieval_result.data.get("metadata", {})
    if metadata.get("web_crawl_used", False):
        logger.info(f"✅ Web crawl fallback was used: {metadata.get('web_crawl_documents', 0)} documents")
        context.intermediate_data["web_crawl_used"] = True
        context.intermediate_data["web_crawl_metadata"] = metadata
```

## Configuration

### Environment Variables

```bash
# Web crawl configuration
WEB_CRAWL_ENABLED=true
WEB_CRAWL_TIMEOUT=30
WEB_CRAWL_MAX_PAGES=5
WEB_CRAWL_CONFIDENCE_THRESHOLD=0.6
WEB_CRAWL_MIN_CONTENT_LENGTH=100
```

### Task Configuration

```python
task = {
    "query": "What are the latest developments in quantum computing?",
    "search_type": "hybrid",
    "enable_web_fallback": True,
    "web_fallback_timeout": 30,
    "max_web_pages": 5,
    "confidence_threshold": 0.6
}
```

## Usage Examples

### Basic Web Crawl Integration

```python
# Initialize retrieval agent
retrieval_agent = RetrievalAgent()

# Process query with web crawl fallback
task = {
    "query": "Latest news about artificial intelligence",
    "enable_web_fallback": True,
    "web_fallback_timeout": 30
}

context = QueryContext(query=task["query"])
result = await retrieval_agent.process_task(task, context)

# Check if web crawl was used
metadata = result.get("data", {}).get("metadata", {})
if metadata.get("web_crawl_used", False):
    print(f"Web crawl used: {metadata.get('web_crawl_documents', 0)} documents")
```

### Pipeline Integration

```python
# Use with standardized pipeline
from shared.core.agents.lead_orchestrator import StandardizedLeadOrchestrator

orchestrator = StandardizedLeadOrchestrator()

result = await orchestrator.process_query(
    query="What are the latest developments in quantum computing?",
    user_context={"user_id": "user123", "model": "auto"}
)

# Check for web sources in citations
citations = result.get("citations", [])
web_citations = [cite for cite in citations if "http" in str(cite)]
print(f"Web citations: {len(web_citations)}")
```

## Testing

### Test Script: `test_web_crawl_integration.py`

The test script provides comprehensive testing of:

1. **Web Crawl Fallback**: Tests queries that should trigger web crawling
2. **Timeout Handling**: Tests web crawl timeout functionality
3. **Disable Functionality**: Tests behavior when web crawl is disabled
4. **Pipeline Integration**: Tests full pipeline with web crawl integration

### Running Tests

```bash
python test_web_crawl_integration.py
```

### Test Cases

```python
test_queries = [
    {
        "query": "What are the latest developments in quantum computing?",
        "description": "Current events query - should trigger web crawl",
        "expected_web_crawl": True
    },
    {
        "query": "Latest news about artificial intelligence",
        "description": "News query with web keywords",
        "expected_web_crawl": True
    },
    {
        "query": "What is machine learning?",
        "description": "Basic factual query - may not need web crawl",
        "expected_web_crawl": False
    },
    {
        "query": "How to implement a REST API in Python",
        "description": "Technical query - should trigger web crawl",
        "expected_web_crawl": True
    }
]
```

## Performance Considerations

### Timeout Management

- **Default Timeout**: 30 seconds for web crawling operations
- **Configurable**: Can be adjusted per task or globally
- **Graceful Degradation**: Falls back to local results if web crawl times out

### Resource Optimization

- **Maximum Pages**: Default limit of 5 pages per query
- **Content Filtering**: Minimum content length threshold (100 characters)
- **URL Validation**: Ensures only valid URLs are crawled

### Caching Strategy

- **Web Content**: Not cached to ensure freshness
- **Local Results**: Still cached for performance
- **Merged Results**: Re-ranked for optimal relevance

## Error Handling

### Graceful Degradation

```python
try:
    web_result = await asyncio.wait_for(
        self.web_crawl_fallback(query, max_pages=5, timeout=web_fallback_timeout),
        timeout=web_fallback_timeout
    )
    
    if web_result.documents:
        # Merge web results with local results
        all_documents = result.documents + web_result.documents
        # ... process merged results
    else:
        logger.warning("⚠️ Web crawl returned no documents")
        
except asyncio.TimeoutError:
    logger.warning("⚠️ Web crawl fallback timed out")
except Exception as e:
    logger.error(f"❌ Web crawl fallback failed: {e}")
```

### Fallback Scenarios

1. **No Web Results**: Continue with local results only
2. **Timeout**: Use local results, log warning
3. **Crawler Service Unavailable**: Gracefully degrade to local-only
4. **Invalid URLs**: Skip invalid URLs, continue with valid ones

## Monitoring and Observability

### Metrics Tracking

```python
metadata = {
    "web_crawl_used": True,
    "web_crawl_documents": len(web_result.documents),
    "web_crawl_time_ms": web_result.query_time_ms,
    "crawl_sources": len(search_urls),
    "successful_crawls": len(documents),
    "merged_sources": ["local", "web_crawl"]
}
```

### Logging

- **Info Level**: Web crawl initiation, successful crawls
- **Warning Level**: Timeouts, insufficient content, failed crawls
- **Error Level**: Crawler service errors, URL validation failures

## Future Enhancements

### Planned Features

1. **Smart Caching**: Cache web content with TTL for frequently accessed topics
2. **Advanced URL Discovery**: Use more sophisticated URL generation strategies
3. **Content Quality Scoring**: Implement better content quality assessment
4. **Multi-Source Crawling**: Crawl multiple sources in parallel
5. **Real-time Content**: Integrate with real-time news APIs

### Extensibility

The web crawl integration is designed to be easily extensible:

```python
# Add custom URL generators
def _get_custom_fallback_urls(self, query: str) -> List[str]:
    # Custom logic for specific domains or query types
    pass

# Add custom content processors
def _process_crawled_content(self, content: str, url: str) -> Document:
    # Custom content processing logic
    pass
```

## Conclusion

The web crawl integration provides:

- **Enhanced Coverage**: Access to current web content when local sources are insufficient
- **Intelligent Fallback**: Automatic triggering based on result quality and query characteristics
- **Seamless Integration**: Works transparently within the existing pipeline
- **Performance Optimization**: Respects timeouts and resource limits
- **Quality Assurance**: Content validation and re-ranking for relevance

The implementation successfully addresses the original requirements:
- ✅ Web data integration via CrawlerService
- ✅ Intelligent fallback based on result quality
- ✅ Content merging with local knowledge sources
- ✅ Timeout and resource management
- ✅ Comprehensive testing and monitoring

The system now provides comprehensive knowledge coverage by combining local knowledge sources with current web content when needed. 🚀 