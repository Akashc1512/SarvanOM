# KnowledgeGraphAgent Guide

## Overview

The `KnowledgeGraphAgent` is a sophisticated agent designed to interface with Neo4j knowledge graphs and provide intelligent query processing capabilities. It can handle various types of knowledge graph queries, from simple entity searches to complex relationship pathfinding.

## Features

### 🔗 **Real Neo4j Integration**
- Connects to Neo4j database using the official Python driver
- Supports both username/password and API key authentication
- Automatic connection pooling for optimal performance
- Graceful fallback to mock data when Neo4j is unavailable

### 🧠 **Intelligent Query Processing**
- **Entity Relationship Queries**: Find how entities are connected
- **Path Finding Queries**: Discover paths between entities
- **Entity Search Queries**: Search for specific entities and their properties
- **General Knowledge Queries**: Broad knowledge graph exploration

### 🛡️ **Security & Performance**
- Parameterized Cypher queries to prevent injection attacks
- Connection pooling for efficient resource usage
- Comprehensive error handling and logging
- Configurable query limits and timeouts

### 📊 **Rich Result Format**
- Structured results with entities, relationships, and paths
- Confidence scoring for result quality
- Processing time metrics
- Detailed metadata for debugging and analysis

## Installation & Setup

### 1. Install Dependencies

```bash
pip install neo4j
```

### 2. Configure Environment Variables

Add the following to your `.env` file:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
NEO4J_API_KEY=your_api_key  # Optional, for API key authentication
```

### 3. Start Neo4j Server

Using Docker:
```bash
docker run \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:latest
```

Or using the provided setup script:
```bash
./scripts/setup_neo4j.sh
```

## Usage

### Basic Usage

```python
from shared.core.agents.knowledge_graph_agent import KnowledgeGraphAgent

# Initialize the agent
agent = KnowledgeGraphAgent()

# Query the knowledge graph
result = await agent.query("How is machine learning related to artificial intelligence?")

# Access results
print(f"Found {len(result.entities)} entities")
print(f"Found {len(result.relationships)} relationships")
print(f"Confidence: {result.confidence}")
```

### Query Types

#### 1. Entity Relationship Queries

```python
# Find relationships between entities
result = await agent.query(
    "How is Python related to machine learning?",
    query_type="entity_relationship"
)
```

**Example Cypher Query:**
```cypher
MATCH (a)-[r]-(b)
WHERE (toLower(a.name) CONTAINS toLower($entity1) OR toLower(a.id) CONTAINS toLower($entity1))
AND (toLower(b.name) CONTAINS toLower($entity2) OR toLower(b.id) CONTAINS toLower($entity2))
RETURN a, r, b
LIMIT 20
```

#### 2. Path Finding Queries

```python
# Find paths between entities
result = await agent.query(
    "What is the path between Docker and Kubernetes?",
    query_type="path_finding"
)
```

**Example Cypher Query:**
```cypher
MATCH path = shortestPath((a)-[*..3]-(b))
WHERE (toLower(a.name) CONTAINS toLower($entity1) OR toLower(a.id) CONTAINS toLower($entity1))
AND (toLower(b.name) CONTAINS toLower($entity2) OR toLower(b.id) CONTAINS toLower($entity2))
RETURN path
LIMIT 5
```

#### 3. Entity Search Queries

```python
# Search for specific entities
result = await agent.query(
    "Tell me about React",
    query_type="entity_search"
)
```

**Example Cypher Query:**
```cypher
MATCH (n)
WHERE toLower(n.name) CONTAINS toLower($entity) 
   OR toLower(n.id) CONTAINS toLower($entity)
   OR any(prop in keys(n) WHERE toLower(toString(n[prop])) CONTAINS toLower($entity))
RETURN n
LIMIT 20
```

### Advanced Usage

#### Custom Query Processing

```python
# Process a task with custom context
task = {
    "query": "What are the applications of neural networks?",
    "query_type": "entity_relationship"
}

context = QueryContext(query="What are the applications of neural networks?")
result = await agent.process_task(task, context)
```

#### Health Monitoring

```python
# Check agent health status
health = agent.get_health_status()
print(f"Neo4j Connected: {health['neo4j_connected']}")
print(f"Status: {health['status']}")
```

## Data Models

### EntityNode

```python
@dataclass
class EntityNode:
    id: str                    # Unique identifier
    name: str                  # Display name
    type: str                  # Entity type (e.g., "technology", "person")
    properties: Dict[str, Any] # Additional properties
    confidence: float = 1.0    # Confidence score
```

### Relationship

```python
@dataclass
class Relationship:
    source_id: str             # Source entity ID
    target_id: str             # Target entity ID
    relationship_type: str      # Type of relationship
    properties: Dict[str, Any] # Relationship properties
    confidence: float = 1.0    # Confidence score
```

### KnowledgeGraphResult

```python
@dataclass
class KnowledgeGraphResult:
    entities: List[EntityNode]           # Found entities
    relationships: List[Relationship]     # Found relationships
    paths: List[List[EntityNode]]        # Found paths
    query_entities: List[str]            # Original query entities
    confidence: float                    # Overall confidence
    processing_time_ms: float            # Processing time
    metadata: Dict[str, Any]            # Additional metadata
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI |
| `NEO4J_USERNAME` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `password` | Neo4j password |
| `NEO4J_DATABASE` | `neo4j` | Neo4j database name |
| `NEO4J_API_KEY` | `None` | Neo4j API key (alternative to username/password) |

### Connection Settings

```python
# Connection pooling settings
max_connection_lifetime = 3600      # 1 hour
max_connection_pool_size = 50       # Maximum connections in pool
```

## Error Handling

The agent includes comprehensive error handling:

1. **Connection Errors**: Graceful fallback to mock data
2. **Query Errors**: Detailed error messages in metadata
3. **Entity Extraction Errors**: Fallback to keyword-based extraction
4. **Neo4j Driver Errors**: Automatic retry and connection testing

### Example Error Handling

```python
try:
    result = await agent.query("How is X related to Y?")
    if result.confidence > 0.5:
        print("High confidence results found")
    else:
        print("Low confidence - consider refining query")
except Exception as e:
    print(f"Query failed: {e}")
```

## Testing

### Run the Test Script

```bash
python test_knowledge_graph_agent.py
```

This will test:
- Neo4j connection status
- Various query types
- Mock data fallback
- Health monitoring

### Test Output Example

```
🔌 Testing Neo4j Connection
==============================
Environment Variables:
  NEO4J_URI: bolt://localhost:7687
  NEO4J_USERNAME: neo4j
  NEO4J_PASSWORD: ********
  NEO4J_DATABASE: neo4j
  NEO4J_API_KEY: Not set

Neo4j Connection Status: ✅ Connected
Using Mock Data: False

🧪 Testing KnowledgeGraphAgent
==================================================
🔍 Test 1: Entity relationship query
Query: How is machine learning related to artificial intelligence?
Type: entity_relationship
------------------------------
✅ Query completed successfully
Confidence: 0.90
Processing time: 45.23ms
Entities found: 2
Relationships found: 1
Paths found: 0

📋 Entities:
  - Machine Learning (technology)
    Description: A subset of artificial intelligence that enables systems to learn from data...
  - Artificial Intelligence (technology)
    Description: The simulation of human intelligence by machines...

🔗 Relationships:
  - ml --[is_subset_of]--> ai
    Description: Machine Learning is a subset of Artificial Intelligence
```

## Integration with Other Agents

The KnowledgeGraphAgent can be integrated with other agents in the system:

```python
from shared.core.agent_orchestrator import LeadOrchestrator

# Initialize orchestrator with knowledge graph agent
orchestrator = LeadOrchestrator()
orchestrator.add_agent(KnowledgeGraphAgent())

# Use in multi-agent workflows
result = await orchestrator.process_query(
    "How does machine learning relate to deep learning and neural networks?"
)
```

## Performance Optimization

### Query Optimization Tips

1. **Use Specific Query Types**: Choose the most appropriate query type for your use case
2. **Limit Results**: Use LIMIT clauses in Cypher queries
3. **Index Properties**: Create indexes on frequently queried properties
4. **Connection Pooling**: The agent automatically manages connection pooling

### Monitoring

```python
# Monitor performance metrics
health = agent.get_health_status()
print(f"Entities in graph: {health['entities_count']}")
print(f"Relationships in graph: {health['relationships_count']}")
print(f"Last updated: {health['last_updated']}")
```

## Troubleshooting

### Common Issues

1. **Neo4j Connection Failed**
   - Check if Neo4j server is running
   - Verify connection credentials
   - Ensure firewall allows connection to port 7687

2. **No Results Found**
   - Check if entities exist in the knowledge graph
   - Verify entity names match exactly
   - Try broader search terms

3. **Low Confidence Scores**
   - Refine query to be more specific
   - Check if relevant data exists in the graph
   - Consider adding more data to the knowledge graph

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('shared.core.agents.knowledge_graph_agent').setLevel(logging.DEBUG)
```

## Future Enhancements

- **Graph Analytics**: Advanced graph algorithms and analytics
- **Semantic Search**: Natural language understanding for queries
- **Real-time Updates**: Live knowledge graph updates
- **Multi-modal Queries**: Support for images, documents, and other data types
- **Federated Queries**: Query across multiple knowledge graphs

## Contributing

When contributing to the KnowledgeGraphAgent:

1. Follow the existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Ensure backward compatibility
5. Add proper error handling and logging

## License

This KnowledgeGraphAgent is part of the Universal Knowledge Hub project and follows the same licensing terms. 